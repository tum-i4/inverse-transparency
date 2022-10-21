<script>
  import { createEventDispatcher } from "svelte";

  export let users;
  export let tools;
  export let filters = undefined;

  const dispatch = createEventDispatcher();

  function resetFilters() {
    filters = { search: "", userRid: "", tool: "", minTimestamp: "", maxTimestamp: "" };
  }

  // Set filters to default value
  resetFilters();
</script>

<div class="form-row">
  <div class="col form-group">
    <p class="font-weight-bold">Filter:</p>
  </div>
  <div class="col-auto mt-auto mb-3">
    <button class="btn btn-outline-dark rounded-0 border-dark" type="button" on:click={resetFilters}>
      Filter zurücksetzen</button
    >
  </div>
  <div class="col-auto mt-auto mb-3">
    <button class="btn btn-outline-dark rounded-0 border-dark" type="button" on:click={() => dispatch("exportPdf")}>
      Als PDF exportieren</button
    >
  </div>
</div>
<div class="form-row">
  <div class="col form-group">
    <label for="searchFilter">Freitextsuche</label>
    <input type="text" class="form-control rounded-0 border-dark" id="searchFilter" bind:value={filters.search} />
  </div>
  <div class="col form-group">
    <label for="userRid">Verantwortlich</label>
    <select class="form-control rounded-0 border-dark" id="userRid" bind:value={filters.userRid}>
      <option />
      {#each users as user}
        <option>{user}</option>
      {/each}
    </select>
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
    <label for="minTimestamp">Zeitraum von</label>
    <input
      type="date"
      class="form-control rounded-0 border-dark"
      id="minTimestamp"
      bind:value={filters.minTimestamp}
      max={filters.maxTimestamp}
    />
  </div>
  <div class="col form-group">
    <label for="maxTimestamp">Zeitraum bis</label>
    <input
      type="date"
      class="form-control rounded-0 border-dark"
      id="maxTimestamp"
      bind:value={filters.maxTimestamp}
      min={filters.minTimestamp}
    />
  </div>
</div>
