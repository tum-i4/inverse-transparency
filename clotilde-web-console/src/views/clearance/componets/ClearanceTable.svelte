<script>
  import moment from "moment";
  import { createEventDispatcher } from "svelte";
  import InvCard from "../../../shared/components/InvCard.svelte";
  import ClearanceForm from "./ClearanceForm.svelte";

  export let dataAccessPolicies;
  const dispatch = createEventDispatcher();
</script>

<style>
  table {
    line-height: 1.5;
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
    width: 140px;
  }
  th.period {
    width: 325px;
  }
  th.controls {
    width: 116px;
  }

  td.tool {
    text-transform: capitalize;
  }
</style>

<div class="pt-3">
  <InvCard>
    <div class="card-body">
      <table class="table">
        <thead>
          <tr>
            <th scope="col" class="user">User</th>
            <th scope="col" class="tool">Tool</th>
            <th scope="col" class="kind">Kind</th>
            <th scope="col" class="period">Period</th>
            <th scope="col" class="controls"></th>
          </tr>
        </thead>
        {#each dataAccessPolicies as policy (policy.id)}
          <tr>
            <td>{policy.user_rid ? policy.user_rid : '*'}</td>
            <td class="tool">{policy.tool ? policy.tool : '*'}</td>
            <td>{policy.access_kind ? policy.access_kind : '*'}</td>
            <td>
              {policy.validity_period_start_date ? moment
                    .utc(policy.validity_period_start_date)
                    .local()
                    .format('L') : '∞'} - {policy.validity_period_end_date ? moment
                    .utc(policy.validity_period_end_date)
                    .local()
                    .format('L') : '∞'}
            </td>
            <td>
              <button
                type="button"
                class="btn btn-outline-danger btn-sm rounded-0 w-100"
                on:click={() => dispatch('deletion', { id: policy.id })}>
                Delete
              </button>
            </td>
          </tr>
        {/each}
        <ClearanceForm on:addition />
      </table>
    </div>
  </InvCard>
</div>
