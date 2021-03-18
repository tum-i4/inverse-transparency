<script>
  import moment from "moment";
  import localization from "moment/locale/de";
  import { Router } from "svelte-router-spa";
  import Footer from "./common/Footer.svelte";
  import Header from "./common/Header.svelte";
  import Notifications from "./common/Notifications.svelte";
  import "./global.scss";
  import { routes } from "./routes";

  moment.updateLocale("de", localization);
</script>

<main>
  <Header />

  <Notifications />

  <div class="container-xl">
    <Router {routes} />

    <Footer />
  </div>
</main>
