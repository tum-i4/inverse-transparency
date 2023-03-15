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

<h1 class="brand">Inverse Transparency: Console</h1>
{#if !$authStore}
  <Login />
{:else}
  <p>
    You're already logged in. Redirecting to
    <!-- prettier-ignore -->
    <Navigate to="/monitor">Monitor</Navigate>.
  </p>
{/if}
