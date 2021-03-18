<script>
  import InvCard from "../../../shared/components/InvCard.svelte";

  export let topUsers;
  export let label;
</script>

<InvCard>
  <div class="card-body">
    <h5 class="card-title">{label}</h5>
    <ul class="list-group list-group-flash">
      {#each topUsers.slice(0, 5) as user}
        <li class="list-group-item bg-transparent">{user}</li>
      {/each}
    </ul>
  </div>
</InvCard>
