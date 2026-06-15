import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

const routes = [
  { path: "/login", name: "Login", component: () => import("../views/Login.vue"), meta: { guest: true } },
  { path: "/register", name: "Register", component: () => import("../views/Register.vue"), meta: { guest: true } },
  { path: "/dashboard", name: "Dashboard", component: () => import("../views/Dashboard.vue"), meta: { requiresAuth: true } },
  { path: "/devices", name: "DeviceList", component: () => import("../views/DeviceList.vue"), meta: { requiresAuth: true } },
  { path: "/devices/new", name: "DeviceForm", component: () => import("../views/DeviceForm.vue"), meta: { requiresAuth: true } },
  { path: "/devices/:id", name: "DeviceDetail", component: () => import("../views/DeviceDetail.vue"), meta: { requiresAuth: true } },
  { path: "/devices/:id/edit", name: "DeviceEdit", component: () => import("../views/DeviceForm.vue"), meta: { requiresAuth: true } },
  { path: "/ocr", name: "OcrUpload", component: () => import("../views/OcrUpload.vue"), meta: { requiresAuth: true } },
  { path: "/export", name: "DataExport", component: () => import("../views/DataExport.vue"), meta: { requiresAuth: true } },
  { path: "/admin/users", name: "UserManagement", component: () => import("../views/admin/UserManagement.vue"), meta: { requiresAuth: true, admin: true } },
  { path: "/admin/logs", name: "AuditLog", component: () => import("../views/admin/AuditLog.vue"), meta: { requiresAuth: true, admin: true } },
  { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach((to, from, next) => {
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return next("/login");
  }
  if (to.meta.guest && auth.isLoggedIn) {
    return next("/dashboard");
  }
  if (to.meta.admin && auth.user?.role !== "admin") {
    return next("/dashboard");
  }
  next();
});

export default router;
