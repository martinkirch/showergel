<template>
  <div class="home">
    <p>Server time : {{ formattedServerTime }} - {{ rawServerTime }}</p>
  </div>
</template>

<script>
import http from '@/http'

export default {
  data () {
    return {
      rawServerTime: ''
    }
  },

  computed: {
    parsedServerTime () {
      return new Date(this.rawServerTime)
    },
    formattedServerTime () {
      return this.parsedServerTime.toLocaleTimeString()
    }
  },

  methods: {
    getLive () {
      http.get('/live')
        .then(this.onLiveResponse)
        .catch(error => { console.log(error) })
    },
    onLiveResponse (response) {
      this.rawServerTime = response.data.server_time
      setTimeout(this.getLive, 1000)
    }
  },
  mounted () {
    this.getLive()
  }
}
</script>
