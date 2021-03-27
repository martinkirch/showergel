<template>
  <div id="app" class="columns">
    <Sidebar :title="apptitle"></Sidebar>
    <div class="column container is-fluid">
      <router-view />
    </div>
  </div>
</template>

<script>
import http from '@/http'
import Sidebar from '@/components/Sidebar.vue'

export default {
  name: 'Showergel',
  components: {
    Sidebar
  },
  data() {
    return {
      apptitle: "Showergel"
    }
  },
  methods: {
    onParamsResponse (response) {
      this.apptitle = response.data.name
    }
  },
  mounted () {
    http.get('/params')
      .then(this.onParamsResponse)
      .catch(error => { console.log(error) })
  }
}
</script>

<style>
body {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  background: #f8f8f8;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
</style>
