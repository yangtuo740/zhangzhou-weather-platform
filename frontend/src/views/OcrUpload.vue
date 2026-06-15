<template>
  <div class="ocr-page">
    <h2 class="page-title">证书OCR识别</h2>
    <el-card>
      <el-steps :active="step" align-center style="margin-bottom:24px">
        <el-step title="上传图片" />
        <el-step title="OCR识别" />
        <el-step title="校对确认" />
        <el-step title="保存完成" />
      </el-steps>

      <div v-if="step === 0">
        <el-upload drag :auto-upload="false" :on-change="handleFileChange" :limit="1" accept=".png,.jpg,.jpeg,.bmp,.webp" list-type="picture">
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">拖拽校准证书图片到此处，或<em>点击上传</em></div>
          <template #tip><div class="el-upload__tip">支持 PNG / JPG / BMP / WEBP 格式</div></template>
        </el-upload>
        <div v-if="previewUrl" style="text-align:center;margin-top:16px">
          <img :src="previewUrl" style="max-width:600px;max-height:400px;border:1px solid #E5E7EB;border-radius:8px" />
        </div>
        <div style="text-align:center;margin-top:20px">
          <el-button type="primary" size="large" @click="startOcr" :loading="ocrLoading" :disabled="!uploadFile">开始识别</el-button>
        </div>
      </div>

      <div v-if="step === 1">
        <el-alert title="OCR识别完成，请核对并修正以下字段，确认无误后保存。" type="success" show-icon :closable="false" style="margin-bottom:16px" />
        <el-form :model="ocrResult" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="证书编号"><el-input v-model="ocrResult.cert_no" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="送检单位"><el-input v-model="ocrResult.send_unit" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="计量器具名称"><el-input v-model="ocrResult.device_name" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="型号/规格"><el-input v-model="ocrResult.model_spec" /></el-form-item></el-col>
            <el-col :span="24"><el-form-item label="装备编码"><el-input v-model="ocrResult.equip_code" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="制造单位"><el-input v-model="ocrResult.manufacturer" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="校准日期"><el-input v-model="ocrResult.calib_date" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="批准人"><el-input v-model="ocrResult.approver" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="核验员"><el-input v-model="ocrResult.reviewer" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="校准员"><el-input v-model="ocrResult.calibrator" /></el-form-item></el-col>
            <el-col :span="24"><el-form-item label="印章"><el-input v-model="ocrResult.seal" /></el-form-item></el-col>
          </el-row>
        </el-form>
        <div style="text-align:center;margin-top:20px">
          <el-button @click="step = 0">重新上传</el-button>
          <el-button type="primary" @click="saveOcr" :loading="saving">确认并保存</el-button>
        </div>
      </div>

      <div v-if="step === 2">
        <el-result icon="success" title="设备信息已保存成功！">
          <template #extra>
            <el-button type="primary" @click="resetOcr">继续上传</el-button>
            <el-button @click="$router.push('/devices')">查看设备列表</el-button>
          </template>
        </el-result>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import api from "../api";
import { ElMessage } from "element-plus";

const step = ref(0);
const uploadFile = ref(null);
const previewUrl = ref("");
const ocrLoading = ref(false);
const saving = ref(false);

const ocrResult = reactive({
  cert_no: "", send_unit: "", device_name: "", model_spec: "", equip_code: "",
  manufacturer: "", approver: "", reviewer: "", calibrator: "", calib_date: "", seal: ""
});

function handleFileChange(file) {
  uploadFile.value = file.raw;
  previewUrl.value = URL.createObjectURL(file.raw);
}

async function startOcr() {
  if (!uploadFile.value) return;
  ocrLoading.value = true;
  try {
    const formData = new FormData();
    formData.append("file", uploadFile.value);
    const res = await api.post("/ocr/recognize", formData, { headers: { "Content-Type": "multipart/form-data" } });
    Object.assign(ocrResult, res.data);
    step.value = 1;
  } catch {
    ElMessage.error("OCR识别失败，请重试");
  } finally {
    ocrLoading.value = false;
  }
}

async function saveOcr() {
  saving.value = true;
  try {
    await api.post("/devices", ocrResult);
    step.value = 2;
  } catch {
    ElMessage.error("保存失败");
  } finally {
    saving.value = false;
  }
}

function resetOcr() {
  uploadFile.value = null;
  previewUrl.value = "";
  Object.keys(ocrResult).forEach(k => ocrResult[k] = "");
  step.value = 0;
}
</script>

<style scoped>
.page-title { font-size: 18px; font-weight: 600; color: #111827; margin-bottom: 16px; }
</style>
