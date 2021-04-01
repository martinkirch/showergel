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

<script>
import http from "@/http";
import { format } from "date-fns";
import CardList from "../components/CardList.vue";
import Datepicker from "vue3-datepicker";

export default {
  components: { CardList, Datepicker },
  data() {
    return {
      start: "",
      end: "",
      limit: "10",
      chronological: "",
      results: null,
      isLoading: true,
      isError: false,
    };
  },
  methods: {
    getHistory() {
      this.isLoading = true;
      this.isError = false;
      let params = new URLSearchParams();
      if (this.limit) {
        params.append("limit", this.limit);
      }
      if (this.start) {
        params.append("start", format(new Date(this.start), "yyyy-MM-dd"));
      }
      if (this.end) {
        params.append("end", format(new Date(this.end), "yyyy-MM-dd"));
      }
      if (this.chronological) {
        params.append("chronological", this.chronological);
      }

      http
        .get("/metadata_log", { params })
        .then(this.onResults)
        .catch((error) => {
          this.isError = true;
          console.log(error);
        });
    },
    onResults(response) {
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
      this.results = resultsByDay;
      this.isLoading = false;
    },

    formatDate: format,
  },
  mounted() {
    this.getHistory();
  },
};
</script>

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