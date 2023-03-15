<script>
  import moment from "moment";
  import AccessHistoryCard from "./AccessHistoryCard.svelte";
  import SummaryCountCard from "./SummaryCountCard.svelte";
  import TopUsersCard from "./TopUsersCard.svelte";

  export let accesses;

  const numDaysHistory = 7; // sets for how many days looking back the access summary metrics are calculated

  $: accessesToday = accesses.filter(
    ({ timestamp }) => timestamp.isSame(moment(), "day") && timestamp.isSameOrBefore(moment())
  );

  $: accessesThisWeek = accesses.filter(
    ({ timestamp }) => timestamp.isAfter(moment().subtract(numDaysHistory, "day")) && timestamp.isSameOrBefore(moment())
  );

  $: dataUsersThisWeek = accessesThisWeek.reduce((userAccessCounts, { user_rid }) => {
    userAccessCounts[user_rid] = (userAccessCounts[user_rid] || 0) + 1;
    return userAccessCounts;
  }, {});

  $: topUsersThisWeek = Object.entries(dataUsersThisWeek)
    .sort((a, b) => b[1] - a[1])
    .map((userCount) => userCount[0]);

  $: accessesPerDay = accessesThisWeek.reduce((accessCountPerDay, { timestamp }) => {
    const date = moment(timestamp).startOf("day").toISOString();
    accessCountPerDay[date] = (accessCountPerDay[date] || 0) + 1;
    return accessCountPerDay;
  }, {});
</script>

<div class="py-3 row">
  <div class="col-xs-12 col-lg-4 mb-4 mb-lg-0">
    <SummaryCountCard count={accessesToday.length} label="accesses today" />
  </div>
  <div class="col-xs-12 col-lg-4 mb-4 mb-lg-0">
    <SummaryCountCard count={accessesThisWeek.length} label="accesses in the last {numDaysHistory} days" />
  </div>
  <div class="col-xs-12 col-lg-4 mb-4 mb-lg-0">
    <SummaryCountCard
      count={Object.keys(dataUsersThisWeek).length}
      label="distinct data consumers in the last {numDaysHistory} days"
    />
  </div>
</div>
<div class="py-3 row">
  <div class="col-xs-12 col-lg-8 mb-4 mb-lg-0">
    <AccessHistoryCard {accessesPerDay} label="Access history of the last {numDaysHistory} days" />
  </div>
  <div class="col-xs-12 col-lg-4">
    <TopUsersCard topUsers={topUsersThisWeek} label="Top consumers of the last {numDaysHistory} days" />
  </div>
</div>
