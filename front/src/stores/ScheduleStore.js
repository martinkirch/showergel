import { defineStore } from "pinia";
import http from "@/http";
import notifications from '@/notifications';

export const useScheduleStore = defineStore('schedule', {
    state: () => ({
        events: {},
        loading: false
    }),
    getters: {
        count() {
            return this.events.length;
        },
        eventById: (state) => {
            return (eventId) => state.events[eventId];
        }
    },
    actions: {
        async getSchedule() {
            try {
                this.loading = true;
                const response = await http.get("/schedule");
                this.$patch({
                    events: response.data,
                    loading: false
                });
            } catch(err) {
                notifications.error_handler(err);
            }
        },
        async addCartfolder(cartfolder, day_of_week, hour, minute) {
            if (cartfolder) {
                try {
                    const response = await http.put('/schedule/cartfolder', {
                        name: cartfolder,
                        day_of_week: day_of_week,
                        hour: hour,
                        minute: minute,
                        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                    })
                    const added = response.data;
                    this.$patch((state) => {
                        state.events[added['when']] = added;
                        state.hasChanged = true;
                    })
                } catch(err) {
                    notifications.error_handler(err);
                }
            }
        },
        async addCommand(command, when) {
            if (command) {
                try {
                    const response = await http.put('/schedule/command', {
                        command: command,
                        when: when,
                    })
                    const added = response.data;
                    this.$patch((state) => {
                        state.events[added['when']] = added;
                        state.hasChanged = true;
                    })
                } catch(err) {
                    notifications.error_handler(err);
                }
            }
        },
        async deleteByOccurrence(when) {
            if (when in this.events){
                try {
                    http.delete('/schedule/'+this.events[when].event_id)
                    this.$patch((state) => {
                        delete state.events[when];
                        state.hasChanged = true;
                    })
                } catch(err) {
                    notifications.error_handler(err);
                }

            }
        }
    }
})
