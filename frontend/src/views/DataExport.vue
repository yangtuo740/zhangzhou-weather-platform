<template>
  <div class="export-page">
    <h2 class="page-title">数据导出</h2>
    <el-card>
      <el-form label-width="120px">
        <el-form-item label="导出范围">
          <el-radio-group v-model="exportScope">
            <el-radio value="all">导出全部设备</el-radio>
            <el-radio value="filtered">按筛选条件导出</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="筛选条件" v-if="exportScope === 'filtered'">
          <el-input v-model="filterKeyword" placeholder="设备名称/装备编码" style="width:300px" />
          <el-select v-model="filterStatus" placeholder="校准状态" clearable style="width:180px;margin-left:12px">
            <el-option label="在校准期内" value="active" />
            <el-option label="即将到期" value="expiring" />
            <el-option label="已过期" value="expired" />
          </el-select>
        </el-form-item>
        <el-form-item label="导出字段">
          <el-checkbox-group v-model="selectedFields">
            <el-checkbox v-for="f in fieldOptions" :key="f.value" :label="f.value">{{ f.label }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="doExport" :loading="exporting"><el-icon><Download /></el-icon>导出 Excel</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api";
import { ElMessage } from "element-plus";

const exportScope = ref("all");
const filterKeyword = ref("");
const filterStatus = ref("");
const exporting = ref(false);

const fieldOptions = [
  { value: "cert_no", label: "证书编号" },
  { value: "send_unit", label: "送检单位" },
  { value: "device_name", label: "计量器具名称" },
  { value: "model_spec", label: "型号/规格" },
  { value: "equip_code", label: "装备编码" },
  { value: "manufacturer", label: "制造单位" },
  { value: "approver", label: "批准人" },
  { value: "reviewer", label: "核验员" },
  { value: "calibrator", label: "校准员" },
  { value: "calib_date", label: "校准日期" },
  { value: "seal", label: "印章" },
  { value: "status", label: "状态" },
  { value: "remarks", label: "备注" },
];

const defaultFields = ["cert_no", "send_unit", "device_name", "model_spec", "equip_code", "manufacturer", "calib_date", "seal", "status"];
const selectedFields = ref([...defaultFields]);

async function doExport() {
  exporting.value = true;
  try {
    const params = {};
    if (exportScope.value === "filtered") {
      params.keyword = filterKeyword.value;
      params.status = filterStatus.value;
    }
    const res = await api.post("/devices/export", {
      fields: selectedFields.value,
      file_format: "xlsx",
    }, { responseType: "blob" });

    const url = URL.createObjectURL(new Blob([res.data]));
    const a = document.createElement("a");
    a.href = url;
    a.download = `设备导出_${new Date().toISOString().slice(0, 10)}.xlsx`;
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch {
    ElMessage.error("导出失败");
  } finally {
    exporting.value = false;
  }
}
</script>

<style scoped>
.page-title { font-size: 18px; font-weight: 600; color: #111827; margin-bottom: 16px; }
</style>
