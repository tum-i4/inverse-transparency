<script>
  export let tools;
  export let accessKinds;

  export let filters = { userRid: "", tool: "", accessKind: "", timestamp: "" };

  function resetFilters() {
    filters = { userRid: "", tool: "", accessKind: "", timestamp: "" };
  }
</script>

<p class="font-weight-bold">Filter:</p>
<div class="form-row">
  <div class="col form-group">
    <label for="userRid">Verantwortlich</label>
    <input type="text" class="form-control rounded-0 border-dark" id="userRid" bind:value={filters.userRid} />
  </div>
  <div class="col form-group">
    <label for="tool">Tool</label>
    <select class="form-control rounded-0 border-dark" id="tool" bind:value={filters.tool}>
      <option />
      {#each tools as tool}
        <option>{tool}</option>
      {/each}
    </select>
  </div>
  <div class="col form-group">
    <label for="accessKind">Art</label>
    <select class="form-control rounded-0 border-dark" id="accessKind" bind:value={filters.accessKind}>
      <option />
      {#each accessKinds as accessKind}
        <option>{accessKind}</option>
      {/each}
    </select>
  </div>
  <div class="col form-group">
    <label for="timestamp">Zeitstempel</label>
    <input type="date" class="form-control rounded-0 border-dark" id="timestamp" bind:value={filters.timestamp} />
  </div>
  <div class="col-auto mt-auto mb-3">
    <button type="button" class="btn btn-outline-dark rounded-0 border-dark" on:click={resetFilters}>Reset</button>
  </div>
</div>
