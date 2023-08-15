<script setup>
import { onMounted, onUnmounted, ref, computed } from 'vue';
import http from '@/http.js';
import _ from 'lodash';
import axios from 'axios';

const serverUptime = ref('unkown');
const serverTime = ref(new Date());
const currentArtist = ref('');
const currentTitle = ref('');
const currentSource = ref('');
const currentStatus = ref('connecting to Liquidsoap');
const currentOnAir = ref(new Date());
const remaining = ref(null);

const cancelSource = axios.CancelToken.source();

const formattedServerTime = computed(() => serverTime.value.toLocaleTimeString());
const currentTrack = computed (() => currentArtist.value + ' - ' + currentTitle.value);
const currentOnAirTime = computed(() => {
  if (currentOnAir.value && isFinite(currentOnAir.value)) {
    return currentOnAir.value.toLocaleTimeString();
  } else {
    return null;
  }
});

var getLive;
function _getLive() { // always use the throttled getLive()
  http.get('/live', { cancelToken: cancelSource.token })
    .then((response) => {
      getLive();
      currentArtist.value = response.data.artist || '';
      currentTitle.value = response.data.title || '';
      currentSource.value = response.data.source || '';
      currentStatus.value = response.data.status || '';
      serverTime.value = new Date(response.data.server_time);
      serverUptime.value = response.data.uptime || 'unkown';
      currentOnAir.value = new Date(response.data.on_air);
      if ( response.data.remaining ) {
        remaining.value = Math.round(response.data.remaining);
      } else {
        remaining.value = null;
      }
    })
    .catch(error => {
      console.log(error);
    })
};
getLive = _.throttle(_getLive, 1000, { leading:false, trailing:true });
onMounted(() => getLive());
onUnmounted(() => {
  getLive.cancel();
  cancelSource.cancel();
});

function confirmSkip () {
  if ( confirm("Skip current track ?") ) {
    http.delete('/live')
      .then(getLive.flush)
      .catch(error => { console.log(error) })
  }
}
</script>

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
