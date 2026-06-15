<template>
  <div class="device-form">
    <div class="page-header">
      <h2 class="page-title">{{ isEdit ? "编辑设备" : "新增设备" }}</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>
    <el-card>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" v-loading="loading">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="证书编号" prop="cert_no"><el-input v-model="form.cert_no" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="送检单位" prop="send_unit"><el-input v-model="form.send_unit" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计量器具名称" prop="device_name"><el-input v-model="form.device_name" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="型号/规格" prop="model_spec"><el-input v-model="form.model_spec" /></el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="装备编码" prop="equip_code"><el-input v-model="form.equip_code" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="制造单位" prop="manufacturer"><el-input v-model="form.manufacturer" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="校准日期" prop="calib_date"><el-input v-model="form.calib_date" placeholder="YYYY-MM-DD" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="批准人" prop="approver"><el-input v-model="form.approver" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="核验员" prop="reviewer"><el-input v-model="form.reviewer" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="校准员" prop="calibrator"><el-input v-model="form.calibrator" /></el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="印章" prop="seal"><el-input v-model="form.seal" /></el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注" prop="remarks"><el-input v-model="form.remarks" type="textarea" :rows="3" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="saving">{{ isEdit ? "保存修改" : "确认新增" }}</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";
import { ElMessage } from "element-plus";

const route = useRoute();
const router = useRouter();
const formRef = ref(null);
const loading = ref(false);
const saving = ref(false);
const isEdit = computed(() => !!route.params.id);

const form = reactive({
  cert_no: "", send_unit: "", device_name: "", model_spec: "", equip_code: "",
  manufacturer: "", approver: "", reviewer: "", calibrator: "", calib_date: "", seal: "", remarks: ""
});

const rules = {
  device_name: [{ required: true, message: "请输入计量器具名称", trigger: "blur" }],
  send_unit: [{ required: true, message: "请输入送检单位", trigger: "blur" }],
};

onMounted(async () => {
  if (isEdit.value) {
    loading.value = true;
    try {
      const res = await api.get(`/devices/${route.params.id}`);
      Object.assign(form, res.data);
    } finally {
      loading.value = false;
    }
  }
});

async function submitForm() {
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) return;
  saving.value = true;
  try {
    if (isEdit.value) {
      await api.put(`/devices/${route.params.id}`, form);
      ElMessage.success("更新成功");
    } else {
      await api.post("/devices", form);
      ElMessage.success("新增成功");
    }
    router.push("/devices");
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 18px; font-weight: 600; color: #111827; }
</style>
