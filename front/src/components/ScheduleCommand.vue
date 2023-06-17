<template>
  <form @submit.prevent="addEvent()" class="box">
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
</template>

<script>
import http from "@/http";
import notifications from '@/notifications';
import { format } from "date-fns";
import Datepicker from "vue3-datepicker";

// TODO: when adding cartfolders, pick the timezone from Intl.DateTimeFormat().resolvedOptions().timeZone

export default {
  props: ['parameters'],
  components: { Datepicker, ScheduleCommand },
  data() {
    return {
      template: "",
      day: new Date(),
      time: format(new Date(), "HH:mm:ss"),
      command: "",
    };
  },
  watch: {
    template(selectedTemplate) {
      this.command = selectedTemplate;
    }
  },
  methods: {
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
          .then(this.getSchedule) // TODO trigger reloadSchedule event
          .catch(notifications.error_handler(error));
    }
  },
};
</script>

<style>

</style>
