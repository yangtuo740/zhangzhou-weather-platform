<template>
  <div class="dashboard">
    <h2 class="page-title">仪表盘</h2>
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.total_devices }}</div>
        <div class="stat-label">在管设备</div>
      </el-card>
      <el-card class="stat-card stat-green">
        <div class="stat-value">{{ stats.active_devices }}</div>
        <div class="stat-label">在校准期内</div>
      </el-card>
      <el-card class="stat-card stat-yellow">
        <div class="stat-value">{{ stats.expiring_devices }}</div>
        <div class="stat-label">30天内到期</div>
      </el-card>
      <el-card class="stat-card stat-red">
        <div class="stat-value">{{ stats.expired_devices }}</div>
        <div class="stat-label">已过期</div>
      </el-card>
    </div>
    <div class="quick-actions">
      <el-button type="primary" @click="$router.push('/ocr')"><el-icon><Camera /></el-icon>上传证书识别</el-button>
      <el-button @click="$router.push('/devices/new')"><el-icon><Plus /></el-icon>手动录入设备</el-button>
      <el-button @click="$router.push('/export')"><el-icon><Download /></el-icon>导出数据</el-button>
    </div>
    <el-card class="recent-logs">
      <template #header><span>最近操作记录</span></template>
      <el-table :data="stats.recent_logs || []" size="small" stripe>
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="action" label="操作" width="120" />
        <el-table-column prop="target" label="对象" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";

const stats = ref({ total_devices: 0, active_devices: 0, expiring_devices: 0, expired_devices: 0, recent_logs: [] });

onMounted(async () => {
  try {
    const res = await api.get("/dashboard");
    stats.value = res.data;
  } catch {}
});
</script>

<style scoped>
.dashboard { max-width: 100%; }
.page-title { font-size: 18px; font-weight: 600; color: #111827; margin-bottom: 24px; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { text-align: center; padding: 8px; }
.stat-value { font-size: 32px; font-weight: 700; color: #1A56DB; }
.stat-label { font-size: 13px; color: #6B7280; margin-top: 4px; }
.stat-green .stat-value { color: #059669; }
.stat-yellow .stat-value { color: #D97706; }
.stat-red .stat-value { color: #DC2626; }
.quick-actions { display: flex; gap: 12px; margin-bottom: 24px; }
.recent-logs { margin-top: 8px; }
</style>
