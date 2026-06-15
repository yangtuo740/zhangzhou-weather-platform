<template>
  <div class="audit-log">
    <h2 class="page-title">操作日志</h2>
    <el-card>
      <div class="filter-bar">
        <el-input v-model="keyword" placeholder="搜索用户名/操作类型" clearable style="width:300px" @keyup.enter="search" />
        <el-button type="primary" @click="search" style="margin-left:12px">搜索</el-button>
      </div>
      <el-table :data="logs" stripe v-loading="loading" style="margin-top:16px">
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="action" label="操作类型" width="140">
          <template #default="{ row }">
            <el-tag size="small">{{ actionText(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="操作对象" min-width="200" show-overflow-tooltip />
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
      </el-table>
      <div class="pagination">
        <el-pagination background layout="total, prev, pager, next" :total="total" :page-size="20" v-model:current-page="page" @current-change="fetchLogs" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../../api";

const logs = ref([]);
const total = ref(0);
const page = ref(1);
const loading = ref(false);
const keyword = ref("");

const actionMap = {
  create: "新增设备", update: "更新设备", delete: "删除设备",
  ocr_create: "OCR录入", export: "导出数据",
  create_user: "创建用户", update_user: "更新用户", login: "登录"
};

function actionText(a) { return actionMap[a] || a; }

async function fetchLogs() {
  loading.value = true;
  try {
    const res = await api.get("/devices/logs/list", { params: { page: page.value, page_size: 20, keyword: keyword.value } });
    logs.value = res.data.items;
    total.value = res.data.total;
  } finally {
    loading.value = false;
  }
}

function search() { page.value = 1; fetchLogs(); }

onMounted(fetchLogs);
</script>

<style scoped>
.page-title { font-size: 18px; font-weight: 600; color: #111827; margin-bottom: 16px; }
.filter-bar { display: flex; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
