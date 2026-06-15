<template>
  <div class="user-mgmt">
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
      <el-button type="primary" @click="openDialog(null)"><el-icon><Plus /></el-icon>新增用户</el-button>
    </div>
    <el-card>
      <el-table :data="users" stripe v-loading="loading">
        <el-table-column prop="username" label="账号" width="140" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'operator' ? 'primary' : 'info'" size="small">
              {{ roleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? "启用" : "禁用" }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm :title="`确定${row.is_active ? '禁用' : '启用'}该用户？`" @confirm="toggleUser(row)">
              <template #reference>
                <el-button link :type="row.is_active ? 'warning' : 'success'" size="small">{{ row.is_active ? "禁用" : "启用" }}</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px">
      <el-form :model="dialogForm" :rules="dialogRules" ref="dialogRef" label-width="100px">
        <el-form-item label="账号" prop="username">
          <el-input v-model="dialogForm.username" :disabled="!!editingUser" />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="dialogForm.real_name" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="dialogForm.role" style="width:100%">
            <el-option label="管理员" value="admin" />
            <el-option label="操作员" value="operator" />
            <el-option label="只读" value="readonly" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="dialogForm.password" type="password" show-password :placeholder="editingUser ? '留空则不修改' : '请输入密码'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import api from "../../api";
import { ElMessage } from "element-plus";

const users = ref([]);
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const dialogRef = ref(null);
const editingUser = ref(null);

const dialogForm = reactive({ username: "", real_name: "", role: "operator", password: "" });

const dialogTitle = computed(() => editingUser.value ? "编辑用户" : "新增用户");

const dialogRules = {
  username: [{ required: true, message: "请输入账号", trigger: "blur" }],
  real_name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
};

const roleText = (r) => ({ admin: "管理员", operator: "操作员", readonly: "只读" })[r] || r;

async function fetchUsers() {
  loading.value = true;
  try {
    const res = await api.get("/auth/users");
    users.value = res.data.items;
  } finally {
    loading.value = false;
  }
}

function openDialog(user) {
  editingUser.value = user;
  if (user) {
    dialogForm.username = user.username;
    dialogForm.real_name = user.real_name;
    dialogForm.role = user.role;
    dialogForm.password = "";
  } else {
    dialogForm.username = "";
    dialogForm.real_name = "";
    dialogForm.role = "operator";
    dialogForm.password = "";
  }
  dialogVisible.value = true;
}

async function saveUser() {
  const valid = await dialogRef.value?.validate().catch(() => false);
  if (!valid) return;
  saving.value = true;
  try {
    if (editingUser.value) {
      const data = { real_name: dialogForm.real_name, role: dialogForm.role };
      if (dialogForm.password) data.password = dialogForm.password;
      await api.put(`/auth/users/${editingUser.value.id}`, data);
      ElMessage.success("更新成功");
    } else {
      await api.post("/auth/users", { ...dialogForm });
      ElMessage.success("新增成功");
    }
    dialogVisible.value = false;
    fetchUsers();
  } finally {
    saving.value = false;
  }
}

async function toggleUser(user) {
  await api.put(`/auth/users/${user.id}`, { is_active: !user.is_active });
  ElMessage.success(user.is_active ? "已禁用" : "已启用");
  fetchUsers();
}

onMounted(fetchUsers);
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 18px; font-weight: 600; color: #111827; }
</style>
