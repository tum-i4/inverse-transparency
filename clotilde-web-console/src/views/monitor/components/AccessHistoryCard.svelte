<script>
  import Chart from "chart.js";
  import moment from "moment";
  import { onMount } from "svelte";
  import InvCard from "../../../shared/components/InvCard.svelte";

  export let accessesPerDay;
  export let label;

  let ctx;
  let lineChart;

  $: {
    if (ctx) {
      // convert to 2d list, because object entries don't have a reliable order
      // & turn timestamps back into moments
      let accessesPerDayMapped = Object.entries(accessesPerDay).map((entry) => [moment(entry[0]), entry[1]]);

      if (accessesPerDayMapped.length > 0) {
        // fill in missing days
        const lastDay = moment().startOf("day");
        let currentDay = moment(lastDay).subtract(1, "week");

        while (currentDay.isBefore(lastDay)) {
          currentDay.add(1, "days");

          // Add if day is not already included
          if (!accessesPerDayMapped.map((entry) => entry[0]).some((element) => element.isSame(currentDay, "day"))) {
            accessesPerDayMapped.push([moment(currentDay), 0]);
          }
        }
      }

      let accessesPerDaySorted = accessesPerDayMapped.sort((a, b) => a[0].diff(b[0]));

      // construct updated chart
      lineChart = new Chart(ctx, {
        type: "line",
        data: {
          labels: accessesPerDaySorted.map((entry) => entry[0].format("DD.MM.")),
          datasets: [
            {
              data: accessesPerDaySorted.map((entry) => entry[1]),
              borderColor: "#62e097",
              borderWidth: 3,
              fill: "false",
            },
          ],
        },
        options: {
          scales: {
            xAxes: [
              {
                gridLines: {
                  drawOnChartArea: false,
                },
                ticks: {
                  fontColor: "black",
                  fontFamily: "IBMPlexMono, monospace",
                },
              },
            ],
            yAxes: [
              {
                gridLines: {
                  drawOnChartArea: false,
                },
                ticks: {
                  beginAtZero: true,
                  fontColor: "black",
                  fontFamily: "IBMPlexMono, monospace",
                  stepSize: 1,
                },
              },
            ],
          },
          legend: {
            display: false,
          },
        },
      });
    }
  }

  onMount(() => {
    ctx = document.getElementById("chart").getContext("2d");
  });
</script>

<InvCard>
  <div class="card-body">
    <h5 class="card-title">{label}</h5>
    <canvas id="chart" />
  </div>
</InvCard>
