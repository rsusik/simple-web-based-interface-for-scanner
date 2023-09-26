const routes = [
  {
    path: "/",
    component: () => import("layouts/MainLayout.vue"),
    children: [{ path: "", component: () => import("pages/Index.vue") }],
  },
  {
    path: "/scan",
    component: () => import("layouts/MainLayout.vue"),
    children: [{ path: "", component: () => import("pages/Scan.vue") }],
  },
  {
    path: "/scans",
    component: () => import("layouts/MainLayout.vue"),
    children: [{ path: "", component: () => import("pages/ScanList.vue") }],
  },

  {
    path: "/upload",
    component: () => import("layouts/MainLayout.vue"),
    children: [{ path: "", component: () => import("pages/Upload.vue") }],
  },

  {
    path: "/print",
    component: () => import("layouts/MainLayout.vue"),
    children: [{ path: "", component: () => import("pages/Print.vue") }],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: "/:catchAll(.*)*",
    component: () => import("pages/Error404.vue"),
  },
];

export default routes;
