<script setup>
import { ref, watchEffect } from 'vue';
import { format } from "date-fns";
import Datepicker from "vue3-datepicker";
import { useScheduleStore } from "@/stores/ScheduleStore.js";

const props = defineProps({
  commands: Array
})

const store = useScheduleStore();
const day = ref(new Date());
const time = ref(format(new Date(), "HH:mm:ss"));
const command = ref('');
const template = ref('');
watchEffect(() => command.value = template.value);

function addEvent() {
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
  store.addCommand(this.command, when);
}
</script>

<template>
  <form @submit.prevent="addEvent()" class="box">
    <h3>Schedule a custom command</h3>
    <div class="field">
      <label class="label" for="template">Command template</label>
      <div class="select">
        <select v-model="template" id="template">
          <option selected disabled value="">Pick a command... </option>
          <option v-for="command in commands" :key="command" :value="command">
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
      <button class="button is-link" type="submit">
        Add event
      </button>
    </div>
  </form>
</template>
