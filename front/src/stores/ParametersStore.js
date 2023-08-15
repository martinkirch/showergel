import { defineStore } from "pinia";
import http from "@/http";

export const useParametersStore = defineStore('parameters', {
    state: () => ({
        name: 'Showergel',
        version: '',
        liquidsoap_version: '',
        commands: Array(),
        cartfolders: Array(),
    }),
    actions: {
        async getParameters() {
            try {
                const response = await http.get("/parameters");
                this.$patch(response.data);

            } catch(err) {
                console.log(err);
            }
        }
    }
});
