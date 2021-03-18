<script>
  import { notificationStore } from "../shared/stores.js";

  function handleDismissal(index) {
    notificationStore.update((notifications) => {
      notifications.splice(index, 1);
      return notifications;
    });
  }
</script>

<style>
  .notification-container {
    position: fixed;
    top: 96px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1;
  }
</style>

<div class="notification-container">
  {#each $notificationStore as notification, i}
    <div class="alert alert-danger alert-dismissible fade show rounded-0" role="alert">
      {notification}
      <button type="button" class="close" aria-label="Close" on:click={() => handleDismissal(i)}>
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  {/each}
</div>
