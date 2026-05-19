/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<object, object, unknown>;
  export default component;
}

export {};

declare module "vue-router" {
  interface RouteMeta {
    guest?: boolean;
    requiresAuth?: boolean;
    permission?: string;
  }
}
