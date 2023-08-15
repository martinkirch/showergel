<script setup>
import { onMounted, ref } from 'vue';
import http from "@/http";
import { format } from "date-fns";
import CardList from "../components/CardList.vue";
import Datepicker from "vue3-datepicker";

const start = ref("");
const end = ref("");
const limit = ref("10");
const chronological = ref("");
const results = ref({});
const isLoading = ref(true);
const isError = ref(false);

function getHistory() {
  isLoading.value = true;
  isError.value = false;
  let params = new URLSearchParams();
  if (limit.value) {
    params.append("limit", limit.value);
  }
  if (start.value) {
    params.append("start", format(new Date(start.value), "yyyy-MM-dd"));
  }
  if (end.value) {
    params.append("end", format(new Date(end.value), "yyyy-MM-dd"));
  }
  if (chronological.value) {
    params.append("chronological", chronological.value);
  }

  http
    .get("/metadata_log", { params })
    .then((response) => {
      const rawResults = response.data.metadata_log;
      const resultsByDay = rawResults.reduce((acc, curr) => {
        const currDay = format(new Date(curr.on_air), "dd/MM/yyyy");
        if (!acc[currDay]) {
          acc[currDay] = [curr];
        } else {
          acc[currDay].push(curr);
        }
        return acc;
      }, {});
      results.value = resultsByDay;
      isLoading.value = false;
    })
    .catch((error) => {
      isError.value = true;
      console.log(error);
    });
}
onMounted(getHistory);
</script>

<template>
  <div id="playout_history" class="content my-4">
    <h1>Playout History</h1>
    <form @submit.prevent="getHistory()" class="box">
      <div class="columns">
        <div class="field column">
          <label class="label" for="start">From</label>
          <div class="control">
            <Datepicker
              class="input"
              placeholder="2021-01-01"
              v-model="start"
            />
          </div>
        </div>
        <div class="field column">
          <label class="label" for="end">To</label>
          <div class="control">
            <Datepicker class="input" placeholder="2021-01-01" v-model="end" />
          </div>
        </div>
      </div>
      <div class="is-flex is-justify-content-space-between">
        <div class="field">
          <label class="label" for="limit">Max. results:</label>
          <div class="control">
            <div class="select">
              <select v-model="limit" id="limit">
                <option>10</option>
                <option>100</option>
                <option>1000</option>
              </select>
            </div>
          </div>
        </div>
        <div class="field is-flex is-align-self-flex-end">
          <label class="checkbox" for="chronological">
            <input
              class="checkbox"
              type="checkbox"
              id="chronological"
              v-model="chronological"
              true-value="yes"
              false-value=""
            />
            Chronologically
          </label>
        </div>
        <div class="field is-align-self-flex-end">
          <button :class="`button is-link ${isLoading ? 'is-loading' : ''}`">
            Search
          </button>
        </div>
      </div>
    </form>
    <CardList :results="results" :loading="isLoading" :error="isError" />
  </div>
</template>

<style>
#playout_history {
  --vdp-hover-bg-color: hsl(217, 71%, 53%);
  --vdp-selected-color: #ffffff;
  --vdp-selected-bg-color: hsl(217, 71%, 53%);
}

.titles .columns {
  margin-bottom: 0;
}
</style>
