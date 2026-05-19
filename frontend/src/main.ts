import { createApp } from "vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import { createPinia } from "pinia";
import router from "./router";
import App from "./App.vue";
import { vPermission } from "./directives/permission";

const app = createApp(App);

app.use(ElementPlus);
app.use(createPinia());
app.use(router);

app.directive("permission", vPermission);

app.mount("#app");
