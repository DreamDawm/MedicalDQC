<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>校验报告</span>
          <el-select v-model="filterTaskId" clearable placeholder="按任务筛选" style="width: 200px" @change="loadData">
            <el-option v-for="t in tasks" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </div>
      </template>
      <el-table :data="results" v-loading="loading" stripe>
        <el-table-column label="任务">
          <template #default="{ row }">{{ getTaskName(row.task_id) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="通过/总计" width="120">
          <template #default="{ row }">
            {{ row.passed_count }} / {{ row.total_expectations }}
          </template>
        </el-table-column>
        <el-table-column label="通过率" width="100">
          <template #default="{ row }">
            {{ row.total_expectations ? Math.round(row.passed_count / row.total_expectations * 100) : 0 }}%
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button v-if="row.report_path" size="small" type="primary" @click="downloadReport(row)">
              下载报告
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 16px; text-align: right">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { resultApi, taskApi } from '../api'

const results = ref([])
const tasks = ref([])
const loading = ref(false)
const filterTaskId = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)

function getTaskName(taskId) {
  const t = tasks.value.find(task => task.id === taskId)
  return t ? t.name : taskId
}

function statusType(status) {
  if (status === 'success') return 'success'
  if (status === 'failed') return 'danger'
  if (status === 'running') return 'warning'
  return 'info'
}

function downloadReport(row) {
  window.open(resultApi.reportUrl(row.id), '_blank')
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (filterTaskId.value) params.task_id = filterTaskId.value
    const { data } = await resultApi.list(params)
    results.value = data
    total.value = data.length < pageSize ? (page.value - 1) * pageSize + data.length : page.value * pageSize + 1
  } finally {
    loading.value = false
  }
}

async function loadTasks() {
  const { data } = await taskApi.list()
  tasks.value = data
}

onMounted(() => {
  loadTasks()
  loadData()
})
</script>
