<script>
  import moment from "moment";
  import * as api from "../../../shared/api.js";
  import InvErrorAlert from "../../../shared/components/InvErrorAlert.svelte";
  import InvSpinner from "../../../shared/components/InvSpinner.svelte";
  import DataAccessSummary from "../components/DataAccessSummary.svelte";
  import DataAccessTable from "../components/DataAccessTable.svelte";

  let accessesPromise = getAccesses();

  async function getAccesses() {
    try {
      const data = await api.get(`data-accesses`);

      const accesses = data.accesses.map((access) => {
        return { ...access, timestamp: moment.utc(access.timestamp) }; // convert timestamp string to moment as utc
      });

      return Promise.resolve(accesses);
    } catch (error) {
      return Promise.reject(error);
    }
  }
</script>

<h1 class="brand">Monitor</h1>

{#await accessesPromise}
  <InvSpinner />
{:then accesses}
  <DataAccessSummary {accesses} />
  <div class="pt-5" />
  <DataAccessTable {accesses} />

{:catch error}
  <InvErrorAlert messagePrefix="Beim Laden des Monitors ist ein Fehler aufgetreten" {error} />
{/await}
