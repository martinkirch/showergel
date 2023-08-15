<script setup>
import { useParametersStore } from "@/stores/ParametersStore.js";
const parameters = useParametersStore();
</script>

<template>
  <div class="content">
    <h1>This is Showergel</h1>
    <h2>A companion app for your Liquidsoap radio</h2>
    <p>Version {{ parameters.version }}, connected to {{parameters.liquidsoap_version}}.</p>
    <p>Showergel is still in early development.</p>
    <ul>
      <li>
        <a href="https://showergel.readthedocs.io/en/latest/" target="_blank">
          Documentation
        </a>
      </li>
      <li>
        <a href="https://www.liquidsoap.info/doc-dev/" target="_blank">
          Liquidsoap documentation
        </a>
      </li>
      <li>
        <a href="https://github.com/martinkirch/showergel" target="_blank">
          Sources and issue tracker
        </a>
      </li>
    </ul>
  </div>
</template>
