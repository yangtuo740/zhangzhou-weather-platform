<template>
  <div class="device-detail">
    <div class="page-header">
      <h2 class="page-title">设备详情</h2>
      <div>
        <el-button @click="$router.push(`/devices/${device.id}/edit`)">编辑</el-button>
        <el-button @click="$router.back()">返回</el-button>
      </div>
    </div>
    <el-card v-loading="loading">
      <el-descriptions :column="2" border size="large">
        <el-descriptions-item label="证书编号">{{ device.cert_no || "-" }}</el-descriptions-item>
        <el-descriptions-item label="送检单位">{{ device.send_unit || "-" }}</el-descriptions-item>
        <el-descriptions-item label="计量器具名称">{{ device.device_name || "-" }}</el-descriptions-item>
        <el-descriptions-item label="型号/规格">{{ device.model_spec || "-" }}</el-descriptions-item>
        <el-descriptions-item label="装备编码" :span="2">{{ device.equip_code || "-" }}</el-descriptions-item>
        <el-descriptions-item label="制造单位">{{ device.manufacturer || "-" }}</el-descriptions-item>
        <el-descriptions-item label="校准日期">{{ device.calib_date || "-" }}</el-descriptions-item>
        <el-descriptions-item label="批准人">{{ device.approver || "-" }}</el-descriptions-item>
        <el-descriptions-item label="核验员">{{ device.reviewer || "-" }}</el-descriptions-item>
        <el-descriptions-item label="校准员">{{ device.calibrator || "-" }}</el-descriptions-item>
        <el-descriptions-item label="印章" :span="2">{{ device.seal || "-" }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(device.status)">{{ statusText(device.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注">{{ device.remarks || "-" }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    <el-card v-if="device.cert_image_path" class="cert-image-card" style="margin-top:16px">
      <template #header><span>证书图片</span></template>
      <img :src="`/uploads/${device.cert_image_path.split('/').pop()}`" style="max-width:100%;max-height:600px" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "../api";

const route = useRoute();
const device = ref({});
const loading = ref(false);

const statusText = (s) => ({ active: "在校准期内", expiring: "即将到期", expired: "已过期" })[s] || s;
const statusType = (s) => ({ active: "success", expiring: "warning", expired: "danger" })[s] || "info";

onMounted(async () => {
  loading.value = true;
  try {
    const res = await api.get(`/devices/${route.params.id}`);
    device.value = res.data;
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 18px; font-weight: 600; color: #111827; }
</style>
