<script>
  import { onMount } from "svelte";
  import { Navigate, navigateTo } from "svelte-router-spa";
  import { getToken } from "../../../shared/auth.js";
  import { authStore } from "../../../shared/stores.js";
  import Login from "../components/Login.svelte";

  onMount(async () => {
    if ($authStore) {
      navigateTo("/monitor");
    } else if ((await getToken()) && $authStore) {
      navigateTo("/monitor");
    }
  });
</script>

<h1 class="brand">Inverse Transparenz: Konsole</h1>
{#if !$authStore}
  <Login />
{:else}
  <p>
    Sie sind schon eingeloggt. Weiter zum
    <!-- prettier-ignore -->
    <Navigate to="/monitor">Monitor</Navigate>.
  </p>
{/if}
