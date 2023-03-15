<script>
  import { navigateTo } from "svelte-router-spa";
  import * as auth from "../../../shared/auth.js";
  import { notificationStore } from "../../../shared/stores.js";

  let username = "";
  let password = "";

  let loginResult;

  async function handleSubmit() {
    try {
      await auth.login(username, password);

      username = "";
      password = "";
      navigateTo("/monitor");
    } catch (error) {
      notificationStore.add(error.message);
    }
  }
</script>

<div class="py-3">
  <h4>Please login to continue</h4>
</div>

<div class="row">
  <div class="col-md-6 col-xs">
    <form on:submit|preventDefault={handleSubmit}>
      <div class="form-group">
        <label for="inputUsername">Email</label>
        <input
          type="text"
          class="form-control rounded-0 border-dark"
          id="inputUsername"
          bind:value={username}
          required
          pattern=".+@.+\..+"
          title="Please enter a valid email address." />
      </div>

      <div class="form-group">
        <label for="inputPassword">Password</label>
        <input
          type="password"
          class="form-control rounded-0 border-dark"
          id="inputPassword"
          bind:value={password}
          required />
      </div>

      <button type="submit" class="btn btn-dark rounded-0 border-dark">Log in</button>
    </form>
  </div>
</div>
