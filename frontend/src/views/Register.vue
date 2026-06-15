<template>
  <div class="login-page">
    <div class="login-card">
      <h1>账号注册</h1>
      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleRegister">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="账号" size="large" />
        </el-form-item>
        <el-form-item prop="real_name">
          <el-input v-model="form.real_name" placeholder="真实姓名" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" native-type="submit" :loading="loading" style="width:100%">注 册</el-button>
        </el-form-item>
      </el-form>
      <p class="register-link">已有账号？<router-link to="/login">返回登录</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { ElMessage } from "element-plus";

const router = useRouter();
const authStore = useAuthStore();
const formRef = ref(null);
const loading = ref(false);

const form = reactive({ username: "", real_name: "", password: "", confirmPassword: "" });

const validateConfirm = (rule, value, callback) => {
  if (value !== form.password) callback(new Error("两次密码不一致"));
  else callback();
};

const rules = {
  username: [{ required: true, message: "请输入账号", trigger: "blur" }],
  real_name: [{ required: true, message: "请输入真实姓名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur", min: 6 }],
  confirmPassword: [{ required: true, message: "请确认密码", trigger: "blur" }, { validator: validateConfirm, trigger: "blur" }],
};

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) return;
  loading.value = true;
  try {
    await authStore.register(form.username, form.password, form.real_name);
    ElMessage.success("注册成功，请登录");
    router.push("/login");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1A56DB 0%, #3B82F6 100%); }
.login-card { background: #fff; border-radius: 12px; padding: 48px 40px; width: 400px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
.login-card h1 { text-align: center; color: #111827; font-size: 22px; margin-bottom: 32px; }
.register-link { text-align: center; color: #6B7280; font-size: 13px; margin-top: 16px; }
.register-link a { color: #1A56DB; text-decoration: none; }
</style>
