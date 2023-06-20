<template>
  <div>
    <div v-for="event in events" :key="event.id">
      <p>
        <span class="when">
          {{ new Date(event.when).toLocaleString() }}
        </span>
        {{ event.what }}
        <button
          class="button is-danger icon"
          @click="deleteEvent(event.event_id, event.when)"
          title="Remove event"
          >
            <i class="mdi mdi-calendar-remove"></i>
        </button>
      </p>
    </div>
  </div>
</template>

<script>
import http from "@/http";
import notifications from '@/notifications';

// TODO: when adding cartfolders, pick the timezone from Intl.DateTimeFormat().resolvedOptions().timeZone

export default {
  data() {
    return {
      events: null,
      isLoading: true,
      isError: false,
    };
  },
  methods: {
    onError(error) {
      this.isError = true;
      notifications.error_handler(error);
    },
    getSchedule() {
      this.isLoading = true;
      this.isError = false;
      http
        .get("/schedule")
        .then(this.onResults)
        .catch(this.onError);
    },
    onResults(response) {
      this.events = response.data.schedule;
      this.isLoading = false;
    },
    deleteEvent(evendId, when) {
      const when_hint = new Date(when).toLocaleString();
      if(confirm(`Really remove event of ${when_hint}?`)) {
        http.delete('/schedule/'+evendId)
          .then(this.getSchedule)
          .catch(this.onError);
      }
    }
  },
  mounted() {
    this.getSchedule();
  },
};
</script>

<style>
.when {
  font-weight: bold;
}
</style>
