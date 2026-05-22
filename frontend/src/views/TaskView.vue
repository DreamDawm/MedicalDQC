<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>校验任务</span>
          <el-button type="primary" @click="showDialog = true">新建任务</el-button>
        </div>
      </template>
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="name" label="任务名称" />
        <el-table-column label="数据源">
          <template #default="{ row }">
            {{ getDsName(row.datasource_id) }}
          </template>
        </el-table-column>
        <el-table-column label="规则数" width="80">
          <template #default="{ row }">{{ row.rule_ids.length }}</template>
        </el-table-column>
        <el-table-column prop="schedule_cron" label="定时计划" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '激活' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="handleRun(row)">执行</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" title="新建校验任务" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="数据源">
          <el-select v-model="form.datasource_id" @change="onDsChange" style="width: 100%">
            <el-option v-for="ds in datasources" :key="ds.id" :label="ds.name" :value="ds.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="校验规则">
          <el-select v-model="form.rule_ids" multiple style="width: 100%">
            <el-option v-for="r in availableRules" :key="r.id" :label="r.table_name + ' - ' + (r.column_name || '*')" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="定时计划">
          <el-input v-model="form.schedule_cron" placeholder="cron 表达式（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi, datasourceApi, validationRuleApi } from '../api'

const tasks = ref([])
const datasources = ref([])
const availableRules = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)

const form = ref({
  name: '',
  datasource_id: '',
  rule_ids: [],
  schedule_cron: '',
})

function getDsName(dsId) {
  const ds = datasources.value.find(d => d.id === dsId)
  return ds ? ds.name : dsId
}

async function loadData() {
  loading.value = true
  try {
    const [tasksRes, dsRes] = await Promise.all([
      taskApi.list(),
      datasourceApi.list(),
    ])
    tasks.value = tasksRes.data
    datasources.value = dsRes.data
  } finally {
    loading.value = false
  }
}

async function onDsChange(dsId) {
  form.value.rule_ids = []
  if (dsId) {
    const { data } = await validationRuleApi.list({ datasource_id: dsId })
    availableRules.value = data
  } else {
    availableRules.value = []
  }
}

async function handleCreate() {
  saving.value = true
  try {
    await taskApi.create(form.value)
    ElMessage.success('任务创建成功')
    showDialog.value = false
    loadData()
  } catch {
    ElMessage.error('创建失败')
  } finally {
    saving.value = false
  }
}

async function handleRun(task) {
  try {
    await taskApi.run(task.id)
    ElMessage.success('任务已提交执行')
  } catch {
    ElMessage.error('执行失败')
  }
}

async function handleDelete(task) {
  await ElMessageBox.confirm('确定删除该任务？', '提示')
  await taskApi.delete(task.id)
  ElMessage.success('已删除')
  loadData()
}

onMounted(loadData)
</script>
