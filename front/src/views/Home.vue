<template>
  <div id="home">
    <p id="servertime">{{ formattedServerTime }}</p>
    <p>Now playing</p>
    <h1 id="currentTrack">{{ currentTrack }}</h1>
    <h2>Since {{ currentOnAirTime }} from {{ currentSource }}[{{ currentStatus }}]</h2>
  </div>
</template>

<script>
import http from '@/http'

export default {
  data () {
    return {
      serverTime: new Date(),
      currentArtist: '',
      currentTitle: '',
      currentSource: '',
      currentStatus: 'connecting to Liquidsoap',
      currentOnAir: new Date(),
    }
  },

  computed: {
    formattedServerTime () {
      return this.serverTime.toLocaleTimeString()
    },
    currentTrack () {
      return this.currentArtist + ' - ' + this.currentTitle
    },
    currentOnAirTime() {
      return this.currentOnAir.toLocaleTimeString()
    }
  },

  methods: {
    getLive () {
      http.get('/live')
        .then(this.onLiveResponse)
        .catch(error => { console.log(error) })
    },
    onLiveResponse (response) {
      this.serverTime = new Date(response.data.server_time)
      this.currentArtist = response.data.artist
      this.currentTitle = response.data.title
      this.currentSource = response.data.source
      this.currentStatus = response.data.status
      this.currentOnAir = new Date(response.data.on_air)
      setTimeout(this.getLive, 1000)
    }
  },
  mounted () {
    this.getLive()
  }
}
</script>

<style scoped>
#home {
  font-size: 2em;
}

#servertime {
  float: right;
  font-weight: bold;
}

#currentTrack {
  color: black;
  font-size: 3em;
}
</style>
