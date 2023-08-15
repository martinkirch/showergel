<script setup>
import ScheduleCartfolder from "@/components/ScheduleCartfolder.vue";
import ScheduleCommand from "@/components/ScheduleCommand.vue";
import Schedule from "@/components/Schedule.vue";
import { useParametersStore } from "@/stores/ParametersStore.js";
const parameters = useParametersStore();
</script>

<template>
  <div id="schedule" class="content my-4">
    <h2>Upcoming programs</h2>
    <Schedule />
    TODO: those forms as modals
    <ScheduleCartfolder :cartfolders="parameters.cartfolders"/>
    <ScheduleCommand :commands="parameters.commands"/>
  </div>
</template>
