<script>
  import * as api from "../../../shared/api.js";
  import InvErrorAlert from "../../../shared/components/InvErrorAlert.svelte";
  import InvSpinner from "../../../shared/components/InvSpinner.svelte";
  import { notificationStore } from "../../../shared/stores.js";
  import ClearanceTable from "../componets/ClearanceTable.svelte";

  let dataAccessPoliciesPromise = getAccessPolicies();

  async function getAccessPolicies() {
    return api.get("data-access-policies");
  }

  async function handleDeletion(id) {
    try {
      await api.del(`data-access-policies/${id}`);
      let policies = await dataAccessPoliciesPromise;
      dataAccessPoliciesPromise = Promise.resolve(policies.filter((policy) => policy.id != id));
    } catch (error) {
      notificationStore.add(error.message);
    }
  }

  async function handleAddition(policy) {
    try {
      policy.user_rid = policy.user_rid === "*" || policy.user_rid === "" ? null : policy.user_rid;

      policy = await api.post("data-access-policies", policy);
      let policies = await dataAccessPoliciesPromise;
      dataAccessPoliciesPromise = Promise.resolve([...policies, policy]);
    } catch (error) {
      notificationStore.add(error.message);
    }
  }
</script>

<h1 class="brand">Datenfreigabe</h1>

{#await dataAccessPoliciesPromise}
  <InvSpinner />
{:then dataAccessPolicies}
  <ClearanceTable
    {dataAccessPolicies}
    on:deletion={(event) => handleDeletion(event.detail.id)}
    on:addition={(event) => handleAddition(event.detail.newPolicy)} />
{:catch error}
  <InvErrorAlert messagePrefix="Beim Laden der Datenfreigaberegeln ist ein Fehler aufgetreten" {error} />
{/await}
