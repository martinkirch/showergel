<script setup>
import { onMounted } from 'vue';
import { useParametersStore } from "@/stores/ParametersStore.js";
import SideBar from '@/components/SideBar.vue';

const parameters = useParametersStore();
onMounted(parameters.getParameters);
</script>

<template>
  <div id="app" class="columns">
    <SideBar :title="parameters.name"></SideBar>
    <div class="column container is-fluid">
      <router-view />
    </div>
  </div>
</template>

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
