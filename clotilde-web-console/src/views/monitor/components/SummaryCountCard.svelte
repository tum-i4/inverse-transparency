<script>
  import InvCard from "../../../shared/components/InvCard.svelte";

  export let count;
  export let label;
</script>

<InvCard>
  <div class="card-body">
    <span class="display-1">{count}</span>
    <br />
    <span>{label}</span>
  </div>
</InvCard>
