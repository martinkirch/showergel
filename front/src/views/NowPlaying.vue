<template>
  <div class="content is-large">
    <p id="servertime">{{ formattedServerTime }}</p>
    <h1 id="currentTrack">{{ currentTrack }}</h1>
    <h2 v-if="remaining">
      Remaining time (estimated): {{remaining}}s.
    </h2>
    <h2>
      <span v-if="currentOnAirTime">
        Since {{ currentOnAirTime }}
      </span>
      from {{ currentSource }}[{{ currentStatus }}]
    </h2>
    <span id="serveruptime">Stream uptime: {{ serverUptime }}</span>
    <button class="button" @click="confirmSkip()">Skip</button>
  </div>
</template>

<script>
import http from '@/http.js';
import _ from 'lodash';
import axios from 'axios';

export default {
  data () {
    return {
      serverUptime: 'unkown',
      serverTime: new Date(),
      currentArtist: '',
      currentTitle: '',
      currentSource: '',
      currentStatus: 'connecting to Liquidsoap',
      currentOnAir: new Date(),
      remaining: null,
      cancelSource: axios.CancelToken.source(),
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
      if (this.currentOnAir && isFinite(this.currentOnAir)) {
        return this.currentOnAir.toLocaleTimeString();
      } else {
        return null;
      }
    }
  },

  methods: {
    _getLive () { // always use the throttled this.getLive()
      http.get('/live', { cancelToken: this.cancelSource.token })
        .then(this.onLiveResponse)
        .catch(error => {
          console.log(error);
        })
    },
    onLiveResponse (response) {
      this.getLive();
      this.currentArtist = response.data.artist || '';
      this.currentTitle = response.data.title || '';
      this.currentSource = response.data.source || '';
      this.currentStatus = response.data.status || '';
      this.serverTime = new Date(response.data.server_time);
      this.serverUptime = response.data.uptime || 'unkown';
      this.currentOnAir = new Date(response.data.on_air);
      if ( response.data.remaining ) {
        this.remaining = Math.round(response.data.remaining);
      } else {
        this.remaining = null;
      }
    },
    skip() {
      http.delete('/live')
        .then(this.getLive.flush)
        .catch(error => { console.log(error) })
    },
    confirmSkip () {
      if ( confirm("Skip current track ?") ) {
        this.skip();
      }
    }
  },
  mounted () {
    this.getLive = _.throttle(this._getLive, 1000, { leading:false, trailing:true });
    this._getLive();
  },
  unmounted () {
    this.getLive.cancel();
    this.cancelSource.cancel();
  }
}
</script>

<style scoped>
#servertime {
  float: right;
  font-weight: bold;
  font-family:monospace;
}

#currentTrack {
  color: black;
  font-size: 3em;
}

#currentTrack {
  margin-top: 0;
}

#serveruptime {
  float: right;
  color: rgb(175, 175, 175);
  font-family:monospace;
  font-size: small;
}
</style>
