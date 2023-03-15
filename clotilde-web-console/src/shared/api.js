import { navigateTo } from "svelte-router-spa";
import { getToken } from "./auth.js";

const BASE_URL = process.env.OVERSEER_URL;

/**
 * Send a GET request to given Overseer endpoint.
 * @param {string} path Path of endpoint.
 * @param {boolean} auth Optionally include authentication header for request.
 */
export function get(path, auth = true) {
  return send({ method: "GET", path }, auth);
}

/**
 * Send a DELETE request to given Overseer endpoint.
 * @param {string} path Path of endpoint.
 * @param {boolean} auth Optionally include authentication header for request.
 */
export function del(path, auth = true) {
  return send({ method: "DELETE", path }, auth);
}

/**
 * Send a POST request to given Overseer endpoint.
 * @param {string} path Path of endpoint.
 * @param {object} data JSON data to include as body.
 * @param {boolean} auth Optionally include authentication header for request.
 */
export function post(path, data, auth = true) {
  return send({ method: "POST", path, data }, auth);
}

/**
 * Send a PUT request to given Overseer endpoint.
 * @param {string} path Path of endpoint.
 * @param {object} data JSON data to include as body.
 * @param {boolean} auth Optionally include authentication header for request.
 */
export function put(path, data, auth = true) {
  return send({ method: "PUT", path, data }, auth);
}

async function send({ method, path, data = undefined }, auth) {
  const options = { method, headers: {} };

  if (data) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(data);
  }

  if (auth) {
    const token = await getToken(); // get token, refreshing when necessary
    if (!token) {
      navigateTo("/");
      return undefined;
    }
    options.headers["authorization"] = `Bearer ${token}`;
  }

  let response;
  response = await fetch(`${BASE_URL}/${path}`, options);
  if (response.ok) {
    if (checkContentType(response, "application/json")) {
      return response.json();
    }
  } else {
    throw new Error(`${response.status}: ${response.statusText}. Caused by a request to ${response.url}.`);
  }
}

function checkContentType(response, contentType) {
  const responseContentType = response.headers.get("content-type");
  return !!responseContentType && responseContentType.indexOf(contentType) !== -1;
}
