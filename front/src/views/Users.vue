<template>
  <div id="playout_history" class="content">
    <h1>Users</h1>
    <form @submit.prevent="addUser()" class="box">
      <h3 @click="showUserAdd = true" id="showUserAdd">Add</h3>
      <div v-if="showUserAdd">
        <div class="field">
            <label class="label" for="username">Username</label>
            <div class="control">
            <input class="input" id="username" />
            </div>
        </div>
        <div class="field">
            <label class="label" for="password">Password</label>
            <div class="control">
            <input class="input" type="password" id="password" />
            </div>
        </div>
        <div class="field">
            <label class="label" for="password_confirmation">Confirm password</label>
            <div class="control">
            <input class="input" type="password" id="password_confirmation" />
            </div>
        </div>
        <div class="field">
            <button class="button is-primary">Create account</button>
        </div>
      </div>
    </form>
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
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import http from '@/http'

export default {
  data () {
    return {
      showUserAdd: false,
      users: []
    }
  },

  computed: {

  },

  methods: {
    getUsers () {
      http.get('/users')
        .then(this.onResults)
        .catch(error => { console.log(error) })
    },
    onResults (response) {
      this.users = response.data.users
    },
    addUser () {
        // TODO
        // then showUserAdd = false;
    }
  },
  mounted () {
    this.getUsers()
  }
}
</script>

<style scoped>
#showUserAdd {
    cursor: pointer;
}
</style>
