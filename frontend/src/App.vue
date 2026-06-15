<template>
  <div id="app-container">
    <el-container v-if="authStore.isLoggedIn" class="main-layout">
      <el-aside width="220px" class="sidebar">
        <div class="logo">
          <h2>气象装备保障平台</h2>
        </div>
        <el-menu :default-active="activeMenu" router background-color="#1A56DB" text-color="#fff" active-text-color="#FFD700">
          <el-menu-item index="/dashboard"><el-icon><Odometer /></el-icon><span>仪表盘</span></el-menu-item>
          <el-menu-item index="/devices"><el-icon><Monitor /></el-icon><span>设备管理</span></el-menu-item>
          <el-menu-item index="/ocr"><el-icon><Camera /></el-icon><span>证书OCR识别</span></el-menu-item>
          <el-menu-item index="/export"><el-icon><Download /></el-icon><span>数据导出</span></el-menu-item>
          <el-sub-menu index="admin" v-if="authStore.user?.role === 'admin'">
            <template #title><el-icon><Setting /></el-icon><span>系统管理</span></template>
            <el-menu-item index="/admin/users"><el-icon><User /></el-icon><span>用户管理</span></el-menu-item>
            <el-menu-item index="/admin/logs"><el-icon><Document /></el-icon><span>操作日志</span></el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="topbar">
          <div class="topbar-right">
            <span class="user-info">{{ authStore.user?.real_name || authStore.user?.username }}</span>
            <el-button type="danger" size="small" @click="logout">退出登录</el-button>
          </div>
        </el-header>
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
    <router-view v-else />
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "./stores/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const activeMenu = computed(() => route.path);

function logout() {
  authStore.logout();
  router.push("/login");
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: #F9FAFB; }
#app-container { min-height: 100vh; }
.main-layout { min-height: 100vh; }
.sidebar { background: #1A56DB; overflow: hidden; }
.sidebar .logo { padding: 20px 16px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.15); }
.sidebar .logo h2 { color: #fff; font-size: 16px; font-weight: 600; }
.el-menu { border-right: none !important; }
.topbar { background: #fff; border-bottom: 1px solid #E5E7EB; display: flex; align-items: center; justify-content: flex-end; padding: 0 24px; }
.topbar-right { display: flex; align-items: center; gap: 12px; }
.user-info { color: #4B5563; font-size: 14px; }
.main-content { background: #F9FAFB; padding: 24px; }
</style>
