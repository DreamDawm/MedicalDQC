<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>数据源管理</span>
          <el-button type="primary" @click="showForm()">新建数据源</el-button>
        </div>
      </template>
      <el-table :data="datasources" v-loading="loading" stripe>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="db_type" label="类型" width="120" />
        <el-table-column prop="host" label="主机" />
        <el-table-column prop="port" label="端口" width="80" />
        <el-table-column prop="database" label="数据库" />
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button size="small" @click="testConnection(row)">测试</el-button>
            <el-button size="small" @click="showForm(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <DatasourceForm
      v-model:visible="formVisible"
      :datasource="currentDs"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { datasourceApi } from '../api'
import DatasourceForm from '../components/DatasourceForm.vue'

const datasources = ref([])
const loading = ref(false)
const formVisible = ref(false)
const currentDs = ref(null)

async function loadData() {
  loading.value = true
  try {
    const { data } = await datasourceApi.list()
    datasources.value = data
  } finally {
    loading.value = false
  }
}

function showForm(ds = null) {
  currentDs.value = ds
  formVisible.value = true
}

async function testConnection(ds) {
  try {
    const { data } = await datasourceApi.test(ds.id)
    if (data.success) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error(data.message)
    }
  } catch {
    ElMessage.error('连接测试失败')
  }
}

async function handleDelete(ds) {
  await ElMessageBox.confirm('确定删除该数据源？', '提示')
  await datasourceApi.delete(ds.id)
  ElMessage.success('已删除')
  loadData()
}

onMounted(loadData)
</script>
