<template>
  <div id="playout_history" class="content">
    <h1>Users</h1>
    <p>
      From here you can edit usernames and passwords that will be allowed
      to stream, if <code>harbor</code> authentication
      <a href="https://showergel.readthedocs.io/en/latest/liquidsoap.html#authenticating-users-on-harbor" target="_blank">
        is set up
      </a>.
    </p>
    <button class="button block is-primary is-rounded" @click="showUserAdd = true">Add</button>
    <div class="modal" :class="{ 'is-active': showUserAdd }">
      <div class="modal-background"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">Create user account</p>
          <button class="delete" aria-label="close" @click="resetAdd()"></button>
        </header>
        <section class="modal-card-body">
          <form @submit.prevent="addUser()" class="box" id="addUser">
          <p>
            Avoid special characters (even spaces) in usernames.
          </p>
          <div class="field">
              <label class="label" for="username">Username</label>
              <div class="control">
                <input class="input" id="username" v-model="addUsername" />
              </div>
          </div>
          <div class="field">
              <label class="label" for="password">Pass phrase</label>
              <div class="control">
                <input class="input" type="password" id="password" v-model="addPassword"/>
              </div>
          </div>
          <div class="field">
              <label class="label" for="password_confirmation">Confirm pass phrase</label>
              <div class="control">
                <input class="input" type="password" id="password_confirmation" v-model="addPasswordConfirmation" />
              </div>
              <p class="help is-danger" v-show="addPasswordsMismatch">
                Pass phrases don't match
              </p>
          </div>
          </form>
        </section>
        <footer class="modal-card-foot">
          <button class="button is-success" type="submit" form="addUser">Create account</button>
          <button class="button" @click="resetAdd()">Cancel</button>
        </footer>
      </div>
    </div>

    <div class="table-container">
      <table class="table is-striped">
        <thead>
          <tr>
            <th>Username</th>
            <th>Created</th>
            <th>Modified</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.username">
            <td>{{ user.username }}</td>
            <td>{{ new Date(user.created_at).toLocaleString() }}</td>
            <td>{{ new Date(user.modified_at).toLocaleString() }}</td>
            <td>
              <button
                class="button is-warning icon"
                @click="changePassword(user.username)"
                title="Change pass phrase"
                >
                  <i class="mdi mdi-lock-reset"></i>
              </button>
              <button
                class="button is-danger icon"
                @click="deleteUser(user.username)"
                title="Remove user account"
                >
                  <i class="mdi mdi-account-off"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import http from '@/http';
import notifications from '@/notifications';

export default {
  data () {
    return {
      addUsername: '',
      addPassword: '',
      addPasswordConfirmation: '',
      showUserAdd: false,
      users: []
    }
  },

  computed: {
    addPasswordsMismatch() {
      return this.addPassword != this.addPasswordConfirmation;
    }
  },

  methods: {
    getUsers () {
      http.get('/users')
        .then(this.onResults)
        .catch(notifications.error_handler);
    },
    onResults (response) {
      this.users = response.data.users;
    },
    resetAdd () {
      this.showUserAdd = false;
      this.addUsername = '';
      this.addPassword = '';
      this.addPasswordConfirmation = '';
    },
    addUser () {
      if (! this.addPasswordsMismatch) {
        http.put('/users', {
          username: this.addUsername,
          password: this.addPassword,
        })
          .then(this.resetAdd)
          .then(this.getUsers)
          .catch(notifications.error_handler);
      }
    },
    changePassword(username) {
      let pass = prompt(`Please enter a new pass phrase for ${username}`);
      if (pass) {
        let confirm = prompt(`Please confirm ${username}'s new pass phrase`);
        if (confirm) {
          if (confirm == pass) {
            http.post(`/users/${username}`, {
              password: pass,
            })
            .then(notifications.success_handler("Pass phrase updated"))
            .catch(notifications.error_handler);
          } else {
            notifications.error("Pass phrases don't match !");
          }
        }
      }
    },
    deleteUser(username) {
      if(confirm(`Really remove ${username}'s account ? All related data will be removed too.`)) {
        http.delete('/users/'+username)
          .then(this.getUsers)
          .catch(notifications.error_handler);
      }
    }
  },
  mounted () {
    this.getUsers();
  }
}
</script>

<style scoped>
#showUserAdd {
    cursor: pointer;
}
</style>
