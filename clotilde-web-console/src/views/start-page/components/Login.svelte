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
  <h4>Zum Fortfahren einloggen</h4>
</div>

<div class="row">
  <div class="col-md-6 col-xs">
    <form on:submit|preventDefault={handleSubmit}>
      <div class="form-group">
        <label for="inputUsername">E-Mail</label>
        <input
          type="text"
          class="form-control rounded-0 border-dark"
          id="inputUsername"
          bind:value={username}
          required
          pattern=".+@.+\..+"
          title="Bitte verwenden sie eine gültige E-Mail-Adresse." />
      </div>

      <div class="form-group">
        <label for="inputPassword">Passwort</label>
        <input
          type="password"
          class="form-control rounded-0 border-dark"
          id="inputPassword"
          bind:value={password}
          required />
      </div>

      <button type="submit" class="btn btn-dark rounded-0 border-dark">Einloggen</button>
    </form>
  </div>
</div>
