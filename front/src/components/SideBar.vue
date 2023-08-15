<script setup>
defineProps({
  title: String,
});
</script>

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
                <i class="mdi mdi-play-box-outline"></i>
              </span>
              <span>Now playing</span>
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
          <router-link to="/users" active-class="is-active">
              <span class="icon is-medium">
                <i class="mdi mdi-account-group"></i>
              </span>
              <span>Users</span>
          </router-link>
        </li>
        <li>
          <router-link to="/schedule" active-class="is-active">
              <span class="icon is-medium">
                <i class="mdi mdi-calendar-clock"></i>
              </span>
              <span>Schedule</span>
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


<style scoped>
#sidebar {
  background: white;
}
.header {
  text-align: center;
  padding: 1rem;
}
h1.title {
  max-width: 6em;
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
</style>
