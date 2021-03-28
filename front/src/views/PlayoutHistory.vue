<template>
  <div id="playout_history" class="content">
    <h1>Playout History</h1>
    <form @submit.prevent="getHistory()" class="box">
      <div class="field">
        <label class="label" for="start">From</label>
        <div class="control">
          <input class="input" v-model="start" id="start" placeholder="2021-01-01" />
        </div>
      </div>
      <div class="field">
        <label class="label" for="end">To</label>
        <div class="control">
          <input class="input" v-model="end" id="end" placeholder="2021-01-01" />
        </div>
      </div>
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
      <div class="field">
        <label class="checkbox" for="chronological">
          <input class="checkbox" type="checkbox" id="chronological" v-model="chronological" true-value="yes" false-value=""/>
          Chronologically
        </label>
      </div>
      <div class="field">
        <button class="button is-primary">Search</button>
      </div>
    </form>
    <div class="table-container">
      <table class="table is-striped">
        <thead>
          <tr>
            <th>Day</th>
            <th>When</th>
            <th>Artist</th>
            <th>Title</th>
            <th>Source</th>
            <th>Source URI</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="result in results" :key="result.on_air">
            <td>{{ new Date(result.on_air).toLocaleDateString() }}</td>
            <td>{{ new Date(result.on_air).toLocaleTimeString() }}</td>
            <td>{{ result.artist }}</td>
            <td>{{ result.title }}</td>
            <td class="is-size-7">{{ result.source }}</td>
            <td class="is-size-7">{{ result.initial_uri }}</td>
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
      start: '',
      end: '',
      limit: "10",
      chronological: '',
      results: []
    }
  },

  computed: {

  },

  methods: {
    getHistory () {
      let params = new URLSearchParams();
      if (this.limit) {
        params.append("limit", this.limit);
      }
      if (this.start) {
        params.append("start", this.start);
      }
      if (this.end) {
        params.append("end", this.end);
      }
      if (this.chronological) {
        params.append("chronological", this.chronological);
      }
      http.get('/metadata_log', { params: params })
        .then(this.onResults)
        .catch(error => { console.log(error) })
    },
    onResults (response) {
      this.results = response.data.metadata_log
    }
  },
  mounted () {
    this.getHistory()
  }
}
</script>

<style scoped>

</style>
