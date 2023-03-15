import PageNotFound from "./common/PageNotFound.svelte";
import Clearance from "./views/clearance/layouts/Clearance.svelte";
import Monitor from "./views/monitor/layouts/Monitor.svelte";
import StartPage from "./views/start-page/layouts/StartPage.svelte";

const routes = [
  { name: "/", component: StartPage },
  { name: "monitor", component: Monitor },
  { name: "clearance", component: Clearance },
  {
    name: "404",
    path: "404",
    component: PageNotFound,
  },
];

export { routes };
