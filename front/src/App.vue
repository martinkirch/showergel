<template>
  <div id="app" class="columns">
    <Sidebar :title="parameters.name"></Sidebar>
    <div class="column container is-fluid">
      <router-view :parameters="parameters"/>
    </div>
  </div>
</template>

<script>
import http from '@/http'
import Sidebar from '@/components/Sidebar.vue'
import { reactive } from 'vue'

const parameters_wrapper = reactive({
  parameters: {
    name: 'Showergel',
    version: '',
    commands: Array(),
  }
})

export default {
  name: 'Showergel',
  components: {
    Sidebar
  },
  data() {
    return parameters_wrapper;
  },
  methods: {
    onParametersResponse (response) {
      this.parameters = response.data;
    }
  },
  mounted () {
    http.get('/parameters')
      .then(this.onParametersResponse)
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
