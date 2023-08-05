<script setup>
import { ref } from 'vue';
import { useScheduleStore } from "@/stores/ScheduleStore.js";

const props = defineProps({
  cartfolders: Array
})

const store = useScheduleStore();
const day = ref(0);
const hour = ref(0);
const minute = ref(0);
const cartfolder = ref('');

const weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
</script>

<template>
  <form @submit.prevent="store.addCartfolder(cartfolder, day, hour, minute)" class="box">
    <h3>Schedule a cartfolder</h3>
    <div class="field">
      <label class="label" for="cartfolder">Cartfolder</label>
      <div class="select">
        <select v-model="cartfolder" id="cartfolder">
          <option v-for="cartname in cartfolders" :value="cartname">
            {{ cartname }}
          </option>
        </select>
      </div>
    </div>
    <div class="field">
      <label class="label" for="day">When</label>
      <div class="field has-addons choosewhen">
        Every
        <div class="select">
          <select v-model="day" id="day">
            <option v-for="(dayName, dayNumber) in weekdays" :value="dayNumber" :key="dayNumber">
              {{ dayName }}
            </option>
          </select>
        </div>
        at
        <div class="select">
          <select v-model="hour" id="hour">
            <option v-for="n in 24" :value="n-1" :key="n-1">{{ (n-1).toString().padStart(2, "0") }}</option>
          </select>
        </div>
        :
        <div class="select">
          <select v-model="minute" id="minute">
            <option v-for="n in 60" :value="n-1" :key="n-1">{{ (n-1).toString().padStart(2, "0") }}</option>
          </select>
        </div>
      </div>
    </div>
    <div class="field">
      <button class="button is-link" type="submit">
        Add program
      </button>
    </div>
  </form>
</template>

<style>
.choosewhen .select {
  margin-right: 0.3em;
  margin-left: 0.3em;
}
</style>
