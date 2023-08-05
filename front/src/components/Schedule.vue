
<script setup>
import { onMounted } from 'vue'
import { useScheduleStore } from "@/stores/ScheduleStore.js";

const store = useScheduleStore();

function deleteEvent(what, when) {
  const when_hint = new Date(when).toLocaleString();
  if(confirm(`Really remove "${what}" at ${when_hint}?`)) {
    store.deleteByOccurrence(when);
  }
}

onMounted(() => {
  store.getSchedule();
})
</script>

<template>
  <div>
    <div v-for="event in store.events" :key="event.event_id" :class="`${store.loading ? 'is-loading' : ''}`">
      <p>
        <span class="when">
          {{ new Date(event.when).toLocaleString() }}
        </span>
        {{ event.type }} - {{ event.what }}
        <button
          class="button is-danger icon"
          @click="deleteEvent(event.what, event.when)"
          title="Remove event"
          >
            <i class="mdi mdi-calendar-remove"></i>
        </button>
      </p>
    </div>
  </div>
</template>

<style>
.when {
  font-weight: bold;
}
</style>
