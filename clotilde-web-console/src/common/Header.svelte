<script>
  import { navigateTo } from "svelte-router-spa";
  import { getToken, logout } from "../shared/auth.js";
  import { authStore, notificationStore } from "../shared/stores.js";

  getToken();

  function navigateHome() {
    navigateTo("/");
  }

  async function handleLogout() {
    try {
      await logout();
      navigateHome(); // if successful navigate to start page
    } catch (error) {
      notificationStore.add(error.message);
    }
  }
</script>

<nav class="navbar navbar-expand-md navbar-dark bg-dark mb-4">
  <div class="navbar-collapse ">
    <img
      class="navbar-brand pb-0"
      role="button"
      on:click={navigateHome}
      src="../inv_transparenz-wortbildmarke-n.svg"
      width="300"
      height="60"
      loading="lazy"
      alt="Inverse Transparency"
    />
    {#if $authStore}
      <div class="navbar-nav mt-auto brand">
        <a class="nav-item nav-link pb-0" href="/monitor">Monitor</a>
        <a class="nav-item nav-link pb-0" href="/clearance">Clearance</a>
      </div>
    {/if}
  </div>
  {#if $authStore}
    <span class="navbar-text mt-auto pb-0 brand">Logged in: {$authStore.email}</span>
    <button class="btn btn-link text-light mt-auto pb-0 border-0 brand" on:click={handleLogout}>Log out</button>
  {/if}
</nav>
