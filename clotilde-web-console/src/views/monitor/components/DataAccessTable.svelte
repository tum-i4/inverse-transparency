<script>
  import moment from "moment";
  import { createEventDispatcher } from "svelte";
  import InvCard from "../../../shared/components/InvCard.svelte";
  import PdfGenerator from "../../../shared/pdf";
  import { authStore } from "../../../shared/stores.js";
  import DataAccessTableFilter from "./DataAccessTableFilter.svelte";

  export let accesses;
  export let overview;
  export let ACCESS_ROW_LIMIT;
  export let pageIndex = 0;
  export let sections = 0;

  const dispatch = createEventDispatcher();

  let filters;
  let users = Object.keys(overview.user_rid);
  let tools = Object.keys(overview.tool);
  let paginationList = [];

  function definedAndIncludesSearchTermCasefolded(inp) {
    return inp && inp.toLowerCase().includes(filters.search.toLowerCase());
  }

  function searchTermMatches(access) {
    return (
      definedAndIncludesSearchTermCasefolded(access.justification) ||
      (access.data_types && access.data_types.some(definedAndIncludesSearchTermCasefolded)) ||
      definedAndIncludesSearchTermCasefolded(access.owner_rid) ||
      definedAndIncludesSearchTermCasefolded(access.user_rid) ||
      definedAndIncludesSearchTermCasefolded(access.tool)
    );
  }

  function onExportPDF() {
    if (filters.userRid == "") {
      alert("Um ein PDF zu exportieren, wählen Sie bitte mittels der Filter eine*n Datennutzer*in aus.");
      return;
    }

    const exportStartDate =
      filters.minTimestamp ||
      accesses
        .reduce((prev, curr) => (prev.timestamp.isBefore(curr.timestamp) ? prev : curr))
        .timestamp.format("YYYY-MM-DD");
    const exportEndDate = filters.maxTimestamp || moment().format("YYYY-MM-DD");
    new PdfGenerator().loadAndGenerate($authStore.email, filters.userRid, exportStartDate, exportEndDate);
  }

  $: sliceOffset = pageIndex * ACCESS_ROW_LIMIT;
  $: filteredAccesses = accesses
    .filter((access) =>
      filters
        ? access.user_rid.includes(filters.userRid) &&
          (filters.tool === "" || access.tool === filters.tool) &&
          (filters.minTimestamp === "" || access.timestamp.isSameOrAfter(moment(filters.minTimestamp), "day")) &&
          (filters.maxTimestamp === "" || access.timestamp.isSameOrBefore(moment(filters.maxTimestamp), "day")) &&
          (filters.search === "" || searchTermMatches(access))
        : true
    )
    .slice(sliceOffset, sliceOffset + ACCESS_ROW_LIMIT);

  // Build the list of pages for pagination
  $: {
    let firstPageShown = Math.max(0, pageIndex - 5); // start 5 pages to the left, but not below 0
    paginationList = Array(10) // show at most 10 pages
      .fill()
      .map((_, i) => firstPageShown + i)
      .filter((x) => x < sections); // cut off indices beyond the section limit
  }
</script>

<style>
  table {
    table-layout: fixed;
    width: 100%;
  }

  td {
    text-overflow: ellipsis;
  }
  th.tool {
    width: 110px;
  }
  th.kind {
    width: 113px;
  }
  th.timestamp {
    width: 180px;
  }
</style>

<h2 class="brand">Zugriffe auf Ihre Daten</h2>

<div class="pt-3">
  <InvCard>
    <div class="card-body">
      <DataAccessTableFilter {users} {tools} on:exportPdf={onExportPDF} bind:filters />
      <!-- Helper class `d-md-table` due to layout issue: https://stackoverflow.com/a/46093659/ -->
      <table class="table table-responsive-md d-md-table">
        <thead>
          <tr>
            <th scope="col">Verantwortlich</th>
            <th scope="col" class="tool">Tool</th>
            <th scope="col" class="kind">Art</th>
            <th scope="col">Begründung</th>
            <th scope="col">Datentypen</th>
            <th scope="col" class="timestamp">Zeitstempel</th>
          </tr>
        </thead>

        {#each filteredAccesses as row}
          <tr>
            <td>{row.user_rid}</td>
            <td>{row.tool}</td>
            <td>{row.access_kind}</td>
            <td>{row.justification}</td>
            <td>{row.data_types.join(", ")}</td>
            <td>{row.timestamp.local().format("L LTS")}</td>
          </tr>
        {/each}
      </table>
      <ul class="pagination justify-content-center flex-wrap">
        <li class="page-item">
          <button
            class="page-link btn btn-dark rounded-0 border-dark"
            class:disabled={pageIndex <= 0}
            on:click={() => dispatch("previous")}>Zurück</button
          >
        </li>
        {#each paginationList as i}
          <li class="page-item">
            <button
              class="page-link btn rounded-0 border-dark {pageIndex === i ? 'active btn-dark' : ''}"
              on:click={() => dispatch("update", { position: i })}
            >
              {i + 1}
            </button>
          </li>
        {/each}
        <li class="page-item">
          <button
            class="page-link btn btn-dark rounded-0 border-dark"
            class:disabled={pageIndex >= sections - 1}
            on:click={() => dispatch("next")}>Weiter</button
          >
        </li>
      </ul>
      <div style="text-align: center;">Seite {pageIndex + 1} von {sections}</div>
    </div>
  </InvCard>
</div>
