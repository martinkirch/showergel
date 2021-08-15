<template>
  <div id="schedule" class="content my-4">
    <form @submit.prevent="addEvent()" class="box">
      <h2>Add an event</h2>
      <div class="field">
        <label class="label" for="template">Command template</label>
        <div class="select">
          <select v-model="template" id="template">
            <option selected disabled value="">Pick a command... </option>
            <option v-for="command in parameters.commands" :key="command" :value="command">
              {{ command }}
            </option>
          </select>
        </div>
      </div>
      <div class="field">
        <label class="label" for="command">Command</label>
          <div class="control">
            <input
              type="text"
              class="input"
              v-model="command"
            />
          </div>
      </div>
      <label class="label" for="day">When</label>
      <div class="field has-addons">
        <div class="control">
          <Datepicker
            class="input"
            placeholder="2021-01-01"
            v-model="day"
          />
        </div>
        <div class="control">
          <input
            type="text"
            class="input"
            size="8"
            v-model="time"
          />
        </div>
      </div>
      <div class="field">
        <button :class="`button is-link ${isLoading ? 'is-loading' : ''}`" type="submit">
          Add event
        </button>
      </div>
    </form>
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
import Datepicker from "vue3-datepicker";

export default {
  props: ['parameters'],
  components: { Datepicker },
  data() {
    return {
      template: "",
      day: new Date(),
      time: format(new Date(), "HH:mm:ss"),
      command: "",
      results: null,
      isLoading: true,
      isError: false,
    };
  },
  watch: {
    template(selectedTemplate) {
      this.command = selectedTemplate;
    }
  },
  methods: {
    onError(error) {
      this.isError = true;
      notifications.error_handler(error);
    },
    addEvent() {
      let when = new Date(this.day);
      let splitted = this.time.split(':');
      let hour = parseInt(splitted[0]);
      if (hour || hour === 0) {
        when.setHours(hour);
      }
      let minute = parseInt(splitted[1]);
      if (minute || minute === 0) {
        when.setMinutes(minute);
      }
      let second = parseInt(splitted[2]);
      if (second || second === 0) {
        when.setSeconds(second);
      }
      http.put('/schedule', {
          command: this.command,
          when: when.toISOString(),
        })
          .then(this.getSchedule)
          .catch(this.onError);
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
