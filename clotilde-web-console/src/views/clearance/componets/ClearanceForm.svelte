<script>
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  let newPolicy = {};
</script>

<tr>
  <form id="clearance-form" on:submit|preventDefault={() => dispatch('addition', { newPolicy })} />
  <td>
    <input type="text" class="form-control form-control-sm rounded-0 border-dark" bind:value={newPolicy.user_rid} />
  </td>
  <td>
    <select class="form-control form-control-sm rounded-0 border-dark" bind:value={newPolicy.tool}>
      <option value={null}>*</option>
      <option value={'slack'}>Slack</option>
      <option value={'git'}>Git</option>
      <option value={'jira'}>Jira</option>
    </select>
  </td>
  <td>
    <select class="form-control form-control-sm rounded-0 border-dark" bind:value={newPolicy.access_kind}>
      <option value={null}>*</option>
      <option>Direkt</option>
      <option>Query</option>
      <option>Aggregation</option>
    </select>
  </td>
  <td>
    <div class="form-row">
      <input
        type="date"
        class="col form-control form-control-sm rounded-0 border-dark"
        on:input={(e) => {
          if (e.target.value) newPolicy.validity_period_start_date = e.target.value;
          else newPolicy.validity_period_start_date = null;
        }} />
      <span class="mx-1">-</span>
      <input
        type="date"
        class="col form-control form-control-sm rounded-0 border-dark"
        on:input={(e) => {
          if (e.target.value) newPolicy.validity_period_end_date = e.target.value;
          else newPolicy.validity_period_end_date = null;
        }} />
    </div>
  </td>
  <td>
    <button type="submit" class="btn btn-dark btn-sm rounded-0 border-dark" form="clearance-form">Neue Regel</button>
  </td>
</tr>
