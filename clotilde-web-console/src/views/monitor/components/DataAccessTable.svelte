<script>
  import moment from "moment";
  import InvCard from "../../../shared/components/InvCard.svelte";
  import DataAccessTableFilter from "./DataAccessTableFilter.svelte";

  export let accesses;

  let filters;

  $: filteredAccesses = accesses.filter((access) =>
    filters
      ? access.user_rid.includes(filters.userRid) &&
        (filters.tool === "" || access.tool === filters.tool) &&
        (filters.accessKind === "" || access.access_kind === filters.accessKind) &&
        (filters.timestamp === "" || access.timestamp.isSame(moment(filters.timestamp), "day"))
      : true
  );
</script>

<style>
  table {
    table-layout: fixed;
    width: 100%;
  }

  td {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
  th.tool {
    width: 100px;
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
      <DataAccessTableFilter
        tools={[...new Set(accesses.map((access) => (access ? access.tool : [])))]}
        accessKinds={[...new Set(accesses.map((access) => (access ? access.access_kind : [])))]}
        bind:filters />
      <table class="table">
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
            <td>{row.data_types.join(', ')}</td>
            <td>{row.timestamp.local().format('L LTS')}</td>
          </tr>
        {/each}
      </table>
    </div>
  </InvCard>
</div>
