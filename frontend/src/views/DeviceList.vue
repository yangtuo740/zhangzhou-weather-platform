<template>
  <div class="device-list">
    <div class="page-header">
      <h2 class="page-title">设备管理</h2>
      <el-button type="primary" @click="$router.push('/devices/new')"><el-icon><Plus /></el-icon>新增设备</el-button>
    </div>
    <el-card class="filter-card">
      <el-row :gutter="12">
        <el-col :span="8">
          <el-input v-model="keyword" placeholder="搜索设备名称/装备编码/送检单位/证书编号" clearable @clear="search" @keyup.enter="search" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="statusFilter" placeholder="校准状态" clearable @change="search">
            <el-option label="在校准期内" value="active" />
            <el-option label="即将到期" value="expiring" />
            <el-option label="已过期" value="expired" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="search">搜索</el-button>
          <el-button @click="reset">重置</el-button>
        </el-col>
      </el-row>
    </el-card>
    <el-card>
      <el-table :data="devices" stripe v-loading="loading" @row-click="goDetail" style="cursor:pointer">
        <el-table-column prop="device_name" label="计量器具名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="model_spec" label="型号/规格" width="120" />
        <el-table-column prop="equip_code" label="装备编码" min-width="200" show-overflow-tooltip />
        <el-table-column prop="send_unit" label="送检单位" min-width="160" show-overflow-tooltip />
        <el-table-column prop="manufacturer" label="制造单位" min-width="140" show-overflow-tooltip />
        <el-table-column prop="calib_date" label="校准日期" width="120" />
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="$router.push(`/devices/${row.id}/edit`)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button link type="danger" size="small" @click.stop>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination background layout="total, prev, pager, next" :total="total" :page-size="pageSize" v-model:current-page="page" @current-change="fetchDevices" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { ElMessage } from "element-plus";

const router = useRouter();
const devices = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = 20;
const loading = ref(false);
const keyword = ref("");
const statusFilter = ref("");

const statusMap = { active: "在校准期内", expiring: "即将到期", expired: "已过期" };
const statusTypeMap = { active: "success", expiring: "warning", expired: "danger" };

function statusText(s) { return statusMap[s] || s; }
function statusType(s) { return statusTypeMap[s] || "info"; }

async function fetchDevices() {
  loading.value = true;
  try {
    const res = await api.get("/devices", { params: { page: page.value, page_size: pageSize, keyword: keyword.value, status: statusFilter.value } });
    devices.value = res.data.items;
    total.value = res.data.total;
  } finally {
    loading.value = false;
  }
}

function search() { page.value = 1; fetchDevices(); }
function reset() { keyword.value = ""; statusFilter.value = ""; search(); }
function goDetail(row) { router.push(`/devices/${row.id}`); }

async function handleDelete(id) {
  await api.delete(`/devices/${id}`);
  ElMessage.success("已删除");
  fetchDevices();
}

onMounted(fetchDevices);
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 18px; font-weight: 600; color: #111827; }
.filter-card { margin-bottom: 16px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
