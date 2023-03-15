import moment from "moment";
import { get } from "svelte/store";
import { authStore } from "../shared/stores.js";

const REVOLORI_URL = process.env.REVOLORI_URL;

/**
 * Makes a call to Revolori, if successful this sets a refresh token cookie and stores the JWT token.
 * @param {string} email The user's email address used for authentication.
 * @param {string} password The user's password.
 */
export async function login(email, password) {
  const options = {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  };

  const response = await fetch(`${REVOLORI_URL}/login`, options);
  if (response.ok) {
    const data = await response.json();
    authStore.set(data.token);
  } else {
    throw new Error(`${response.status}: ${response.statusText}. Caused by a request to ${response.url}.`);
  }
}

/**
 * Makes a call to Revolori, which invalidates the refresh token, and deletes the JWT token in the store.
 */
export async function logout() {
  const options = {
    method: "DELETE",
    credentials: "include",
  };

  const response = await fetch(`${REVOLORI_URL}/login`, options);
  if (response.ok) {
    authStore.clear();
    return true;
  } else {
    throw new Error(`${response.status}: ${response.statusText}. Caused by a request to ${response.url}.`);
  }
}

/**
 * Tries to acquire a new JWT token from Revolori using the refresh token stored in a cookie.
 */
export async function refreshToken() {
  const options = {
    method: "GET",
    credentials: "include",
  };
  const response = await fetch(`${REVOLORI_URL}/refresh`, options); // if there is no token-cookie, this results in an error in the browser console, which is expected and doesn't impact functionality
  if (response.ok) {
    const data = await response.json();
    if (data) {
      authStore.set(data.token);
    } else {
      throw new Error("Token refresh failed.");
    }
  }
}

/**
 * Return token from store. If there is no stored token or the token has expired, an attempt is made to refresh the token.
 */
export async function getToken() {
  if (get(authStore) && !checkTokenExpired()) {
    return get(authStore).token;
  } else {
    try {
      await refreshToken();
      return get(authStore).token;
    } catch {
      return null;
    }
  }
}

function checkTokenExpired() {
  return get(authStore).expires <= moment();
}
