<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>趋势分析</span>
          <div style="display: flex; gap: 12px">
            <el-select v-model="filterTaskId" clearable placeholder="按任务筛选" style="width: 200px" @change="loadData">
              <el-option v-for="t in tasks" :key="t.id" :label="t.name" :value="t.id" />
            </el-select>
            <el-select v-model="days" style="width: 120px" @change="loadData">
              <el-option :value="7" label="近7天" />
              <el-option :value="30" label="近30天" />
              <el-option :value="90" label="近90天" />
            </el-select>
          </div>
        </div>
      </template>
      <TrendChart :data="trendData" v-loading="loading" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { resultApi, taskApi } from '../api'
import TrendChart from '../components/TrendChart.vue'

const trendData = ref([])
const tasks = ref([])
const loading = ref(false)
const filterTaskId = ref('')
const days = ref(30)

async function loadData() {
  loading.value = true
  try {
    const params = { days: days.value }
    if (filterTaskId.value) params.task_id = filterTaskId.value
    const { data } = await resultApi.trend(params)
    trendData.value = data
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
