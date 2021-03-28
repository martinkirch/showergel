<template>
  <div id="sidebar" class="column is-narrow">
    <div class="header">
      <p class="logo">🧴</p>
      <h1 class="title">{{ title }}</h1>
    </div>
    <aside class="menu">
      <ul class="menu-list">
        <li>
          <router-link to="/" active-class="is-active">
              <span class="icon is-medium">
                <i class="mdi mdi-home"></i>
              </span>
              <span>Home</span>
          </router-link>
        </li>
        <li>
          <router-link to="/users" active-class="is-active">
              <span class="icon is-medium">
                <i class="mdi mdi-account-group"></i>
              </span>
              <span>Users</span>
          </router-link>
        </li>
        <li>
          <router-link to="/playout_history" active-class="is-active">
              <span class="icon is-medium">
                <i class="mdi mdi-history"></i>
              </span>
              <span>Playout History</span>
          </router-link>
        </li>
        <li>
          <router-link to="/about" active-class="is-active">
              <span class="icon is-medium">
                <i class="mdi mdi-information"></i>
              </span>
              <span>About</span>
          </router-link>
        </li>
      </ul>
    </aside>
  </div>
</template>

<script>
export default {
  props: ['title']
}
</script>


<style scoped>
#sidebar {
  background: white;
}
.header {
  text-align: center;
  padding: 1rem;
}
.logo {
  font-size: 8rem;
}
.router-link-exact-active > button {
  background-color: #44b783 !important;
  color: white !important;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2) !important;
  margin-bottom: 15px;
}
.button {
  justify-content: left !important;
}
.margin-top {
  margin-top: 2rem;
}
.margin-btn {
  margin-bottom: 10px;
}
</style>
