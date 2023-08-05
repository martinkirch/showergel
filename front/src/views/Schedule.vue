<template>
  <div id="schedule" class="content my-4">
    <h2>Add an event</h2>
    <ScheduleCommand :commands="parameters.commands"/>
    <ScheduleCartfolder :cartfolders="parameters.cartfolders"/>
    <h2>Upcoming events</h2>
    <Schedule />
  </div>
</template>

<script>
import ScheduleCartfolder from "../components/ScheduleCartfolder.vue";
import ScheduleCommand from "../components/ScheduleCommand.vue";
import Schedule from "../components/Schedule.vue";

export default {
  props: ['parameters'],
  components: { ScheduleCommand, Schedule, ScheduleCartfolder },
};
</script>

<style>
</style>
