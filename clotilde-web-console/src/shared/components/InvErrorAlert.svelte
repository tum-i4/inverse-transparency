<script>
  export let messagePrefix;
  export let error;
</script>

<div class="pt-3">
  <div class="alert alert-danger rounded-0">{messagePrefix}: {error.message}</div>
</div>
