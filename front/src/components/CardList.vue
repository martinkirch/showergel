<template>
  <div class="card-list">
    <div
      v-if="loading"
      class="is-flex is-justify-content-center is-align-items-center my-6"
    >
      <div class="loader"></div>
    </div>
    <div
      v-if="!loading && error"
      class="is-flex is-justify-content-center is-align-items-center my-6"
    >
      <p class="is-error">
        Sorry there was an error. You may find more details in your Javascript
        console, or in Showergel's logs
      </p>
    </div>
    <div v-if="!loading && !error" class="list-container">
      <div class="field">
        <label class="label" for="filter">Filter by artist or song name</label>
        <div class="control">
          <input id="filter" class="input" type="text" v-model="filter" />
        </div>
      </div>
      <div v-for="(titles, day) in filteredResults" :key="day">
        <p
          class="subtitle is-3 day has-background-link has-text-light p-2 has-text-centered"
        >
          {{ day }}
        </p>
        <div class="titles">
          <div
            v-for="(title, index) in titles"
            :key="title.on_air"
            :class="`media mt-0 px-4 ${
              index % 2 === 0 ? 'has-background-light' : ''
            }`"
          >
            <div class="media-left">
              <div class="block pt-1">
                {{ formatDate(new Date(title.on_air), "HH:mm:ss") }}
              </div>
            </div>
            <div class="media-content columns">
              <div class="content column">
                <p class="mb-0">
                  <strong class="small-caps subtitle is-4 is-capitalized">
                    {{ title.artist }}
                  </strong>
                </p>
                <p class="is-size-5 has-text-grey is-italic mb-0">
                  {{ title.title }}
                </p>
                <p class="has-text-grey mb-0">
                  {{ title.album }} - {{ title.year }}
                </p>
              </div>
              <div class="content column">
                <div class="tag is-warning">
                  {{ title.source }}
                </div>
                <p class="pt-2 is-size-6 has-text-grey">
                  {{ title.initial_uri }}
                </p>
              </div>
            </div>
            <div class="media-right">
              <!-- <button class="delete"></button> -->
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { format } from "date-fns";

export default {
  data() {
    return {
      filter: "",
    };
  },
  props: {
    results: Object,
    loading: { type: Boolean, default: true },
    error: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    filteredResults() {
      const filteredResults = {};
      if (this.results && typeof this.results === "object") {
        Object.keys(this.results).forEach((day) => {
          const filteredDay = this.results[day].filter((result) => {
            if (this.filter) {
              return (
                result.artist.includes(this.filter) ||
                result.title.includes(this.filter)
              );
            }
            return true;
          });
          filteredResults[day] = filteredDay;
        });
      }
      return filteredResults;
    },
  },
  methods: {
    formatDate: format,
  },
};
</script>

<style>
.small-caps {
  font-variant: small-caps;
  font-weight: 500;
}
.card-list .loader {
  width: 4rem;
  height: 4rem;
}
</style>
