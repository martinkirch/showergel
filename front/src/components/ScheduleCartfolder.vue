<template>
  <form @submit.prevent="addEvent()" class="box">
    <h3>Schedule a cartfolder</h3><!-- TODO this should be collapsible -->
    <div class="field">
      <label class="label" for="cartfolder">Cartfolder</label>
      <div class="select">
        <select v-model="cartfolder" id="cartfolder">
          <option v-for="cartfolder in cartfolders" :key="cartfolder" :value="cartfolder">
            {{ cartfolder }}
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
            <option value="0">Monday</option>
            <option value="1">Tueday</option>
            <option value="2">Wednesday</option>
            <option value="3">Thursday</option>
            <option value="4">Friday</option>
            <option value="5">Saturday</option>
            <option value="6">Sunday</option>
          </select>
        </div>
        at
        <div class="select">
          <select v-model="hour" id="hour">
            <option v-for="n in 24" :value="n">{{ n.toString().padStart(2, "0") }}</option>
          </select>
        </div>
        :
        <div class="select">
          <select v-model="minute" id="minute">
            <option v-for="n in 60" :value="n">{{ n.toString().padStart(2, "0") }}</option>
          </select>
        </div>
      </div>
    </div>
    <div class="field">
      <button class="button is-link" type="submit">
        Add event
      </button>
    </div>
  </form>
</template>

<script>
import http from "@/http";
import notifications from '@/notifications';

export default {
  props: ['cartfolders'],
  data() {
    return {
      day: "",
      hour: "",
      minute: "",
      cartfolder: "",
    };
  },
  methods: {
    addEvent() {
      http.put('/schedule/cartfolder', {
          name: this.cartfolder,
          day_of_week: this.day,
          hour: this.hour,
          minute: this.minute,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        })
          .catch(notifications.error_handler(error)); // TODO trigger model update here
    }
  },
};
</script>

<style>
.choosewhen .select {
  margin-right: 0.3em;
  margin-left: 0.3em;
}
</style>
