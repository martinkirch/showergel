<template>
  <div id="schedule" class="content my-4">
    <event-add-generic :parameters="parameters"></event-add-generic>
    <h2>Upcoming events</h2>
    <div v-for="event in results" :key="event.id">
      <p>
        <span class="when">
          {{ new Date(event.when).toLocaleString() }}
        </span>
        {{ event.command }}
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
import { format } from "date-fns";
import EventAddGeneric from '../components/EventAddGeneric.vue';

export default {
  props: ['parameters'],
  components: { EventAddGeneric },
  data() {
    return {
      results: null,
      isLoading: true,
    };
  },
  methods: {
    onError(error) {
      notifications.error_handler(error);
    },
    getSchedule() {
      this.isLoading = true;
      http
        .get("/schedule")
        .then(this.onResults)
        .catch(this.onError);
    },
    onResults(response) {
      this.results = response.data.schedule;
      this.isLoading = false;
    },
    deleteEvent(evendId, when) {
      const when_hint = new Date(when).toLocaleString();
      if(confirm(`Really remove event of ${when_hint}?`)) {
        http.delete('/schedule/'+evendId)
          .then(this.getSchedule)
          .catch(notifications.error_handler);
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
