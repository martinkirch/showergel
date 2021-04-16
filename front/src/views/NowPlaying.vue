<template>
  <div class="content is-large">
    <p id="servertime">{{ formattedServerTime }}</p>
    <h1 id="currentTrack">{{ currentTrack }}</h1>
    <h2 v-if="remaining">
      Remaining time (estimated): {{remaining}}s.
    </h2>
    <h2>Since {{ currentOnAirTime }} from {{ currentSource }}[{{ currentStatus }}]</h2>
    <button class="button" @click="confirmSkip()">Skip</button>
  </div>
</template>

<script>
import http from '@/http';

export default {
  data () {
    return {
      serverTime: new Date(),
      currentArtist: '',
      currentTitle: '',
      currentSource: '',
      currentStatus: 'connecting to Liquidsoap',
      currentOnAir: new Date(),
      remaining: null,
      timeoutID: null,
    }
  },

  computed: {
    formattedServerTime () {
      return this.serverTime.toLocaleTimeString();
    },
    currentTrack () {
      return this.currentArtist + ' - ' + this.currentTitle;
    },
    currentOnAirTime() {
      return this.currentOnAir.toLocaleTimeString();
    }
  },

  methods: {
    getLive () {
      http.get('/live')
        .then(this.onLiveResponse)
        .catch(error => { console.log(error) })
    },
    onLiveResponse (response) {
      self.timeoutID = setTimeout(this.getLive, 1000);
      this.currentArtist = response.data.artist || '';
      this.currentTitle = response.data.title || '';
      this.currentSource = response.data.source || '';
      this.currentStatus = response.data.status || '';
      this.serverTime = new Date(response.data.server_time);
      this.currentOnAir = new Date(response.data.on_air);
      if ( response.data.remaining ) {
        this.remaining = Math.round(response.data.remaining);
      } else {
        this.remaining = null;
      }
    },
    skip() {
      http.delete('/live')
        .then(this.getLive)
        .catch(error => { console.log(error) })
    },
    confirmSkip () {
      if ( confirm("Skip current track ?") ) {
        this.skip();
      }
    }
  },
  mounted () {
    this.getLive();
  },
  unmounted () {
    if (self.timeoutID) {
      clearTimeout(self.timeoutID);
    }
  }
}
</script>

<style scoped>
#servertime {
  float: right;
  font-weight: bold;
}

#currentTrack {
  color: black;
  font-size: 3em;
}
</style>
