import jwtDecode from "jwt-decode";
import moment from "moment";
import { writable } from "svelte/store";

function createNotificationStore() {
  const { subscribe, update } = writable([]);

  return {
    subscribe,
    update,
    add: (notification) => update((notifications) => [...notifications, notification]),
  };
}
export const notificationStore = createNotificationStore();

/**
 * Defines a custom store to handle data related to authentication
 */
function createAuthStore() {
  const { subscribe, set } = writable(null);

  return {
    subscribe,
    /**
     * Decodes token and saves part of the contents in store.
     * @param {string} token JWT token as received from Revolori.
     */
    set: (token) => {
      const tokenContent = jwtDecode(token);
      set({
        token: token,
        email: tokenContent.sub,
        expires: moment.unix(tokenContent.exp),
      });
    },
    clear: () => set(null),
  };
}
export const authStore = createAuthStore();
