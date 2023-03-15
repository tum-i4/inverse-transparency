<script>
  import moment from "moment";
  import * as api from "../../../shared/api.js";
  import InvErrorAlert from "../../../shared/components/InvErrorAlert.svelte";
  import InvSpinner from "../../../shared/components/InvSpinner.svelte";
  import DataAccessSummary from "../components/DataAccessSummary.svelte";
  import DataAccessTable from "../components/DataAccessTable.svelte";

  const ACCESS_ROW_LIMIT = 25;
  let pageIndex = 0;
  let sections = 0;
  $: accesses = [];
  $: overview = {};

  // Fill the page on first load
  let accessesPromise = getAccesses(0, ACCESS_ROW_LIMIT * 10);
  accessesPromise.then((response) => {
    accesses = response.accesses;
    overview = response.overview;
    sections = response.sections;
  });

  async function getAccesses(offset, limit) {
    try {
      let data = await api.get(`data-accesses?offset=${offset}&limit=${limit}`);
      let _accesses = data.accesses.map((access) => {
        return { ...access, timestamp: moment.utc(access.timestamp) }; // convert timestamp string to moment as utc
      });
      let _sections = Math.ceil(data.total / ACCESS_ROW_LIMIT);
      return Promise.resolve({ accesses: _accesses, overview: data.overview, sections: _sections });
    } catch (error) {
      return Promise.reject(error);
    }
  }

  async function switchPage(newPageIndex) {
    // Discard in case of invalid page indices
    if (newPageIndex < 0 || newPageIndex >= sections) {
      return;
    }
    pageIndex = newPageIndex;

    // Theoretical limit when counting from index 0.
    const absoluteLimit = pageIndex * ACCESS_ROW_LIMIT + ACCESS_ROW_LIMIT;
    // We have preloaded enough entries
    if (accesses.length >= absoluteLimit) {
      return;
    }
    let response = await getAccesses(accesses.length, absoluteLimit - accesses.length);
    accesses = accesses.concat(response.accesses);
  }
</script>

<h1 class="brand">Monitor</h1>

{#await accessesPromise}
  <InvSpinner />
{:then}
  <DataAccessSummary {accesses} />
  <div class="pt-5" />
  <DataAccessTable
    on:previous={() => switchPage(pageIndex - 1)}
    on:next={() => switchPage(pageIndex + 1)}
    on:update={(event) => switchPage(event.detail.position)}
    {ACCESS_ROW_LIMIT}
    {pageIndex}
    {accesses}
    {overview}
    {sections}
  />
{:catch error}
  <InvErrorAlert messagePrefix="An error occurred while attempting to load the monitor" {error} />
{/await}
