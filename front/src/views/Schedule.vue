<template>
  <div id="schedule" class="content my-4">
    <h2>Add an event</h2>
    <ScheduleCommand :parameters="parameters"/>
    <h2>Upcoming events</h2>
    <Schedule />
  </div>
</template>

<script>
import ScheduleCommand from "../components/ScheduleCommand.vue";
import Schedule from "../components/Schedule.vue";

// TODO: when adding cartfolders, pick the timezone from Intl.DateTimeFormat().resolvedOptions().timeZone

export default {
  props: ['parameters'],
  components: { ScheduleCommand, Schedule },
};
</script>

<style>
</style>
