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
        <el-table-column label="定时计划">
          <template #default="{ row }">
            <span v-if="row.schedule_cron">{{ formatCron(row.schedule_cron) }}</span>
            <span v-else style="color: #999">手动执行</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '激活' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
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
          <CronSelector v-model="form.schedule_cron" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑任务对话框 -->
    <el-dialog v-model="editDialog" title="编辑校验任务" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="数据源">
          <el-select v-model="editForm.datasource_id" @change="onEditDsChange" style="width: 100%">
            <el-option v-for="ds in datasources" :key="ds.id" :label="ds.name" :value="ds.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="校验规则">
          <el-select v-model="editForm.rule_ids" multiple style="width: 100%">
            <el-option v-for="r in editAvailableRules" :key="r.id" :label="r.table_name + ' - ' + (r.column_name || '*')" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="定时计划">
          <CronSelector v-model="editForm.schedule_cron" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="editForm.is_active" active-text="激活" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi, datasourceApi, validationRuleApi } from '../api'
import CronSelector from '../components/CronSelector.vue'

const tasks = ref([])
const datasources = ref([])
const availableRules = ref([])
const editAvailableRules = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editDialog = ref(false)
const saving = ref(false)

const form = ref({
  name: '',
  datasource_id: '',
  rule_ids: [],
  schedule_cron: '',
})

const editForm = ref({
  id: '',
  name: '',
  datasource_id: '',
  rule_ids: [],
  schedule_cron: '',
  is_active: true,
})

function getDsName(dsId) {
  const ds = datasources.value.find(d => d.id === dsId)
  return ds ? ds.name : dsId
}

function formatCron(cron) {
  const cronMap = {
    '0 * * * *': '每小时整点',
    '0 */2 * * *': '每2小时',
    '0 */4 * * *': '每4小时',
    '0 */6 * * *': '每6小时',
    '0 */12 * * *': '每12小时',
    '0 0 * * *': '每天 00:00',
    '0 6 * * *': '每天 06:00',
    '0 8 * * *': '每天 08:00',
    '0 12 * * *': '每天 12:00',
    '0 18 * * *': '每天 18:00',
    '0 22 * * *': '每天 22:00',
    '0 0 * * 1': '每周一 00:00',
    '0 8 * * 1': '每周一 08:00',
    '0 0 * * 2': '每周二 00:00',
    '0 0 * * 3': '每周三 00:00',
    '0 0 * * 4': '每周四 00:00',
    '0 0 * * 5': '每周五 00:00',
    '0 0 * * 6': '每周六 00:00',
    '0 0 * * 0': '每周日 00:00',
    '0 0 1 * *': '每月1日 00:00',
    '0 8 1 * *': '每月1日 08:00',
    '0 0 15 * *': '每月15日 00:00',
    '0 0 L * *': '每月最后一天 00:00',
  }
  return cronMap[cron] || cron
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

async function handleEdit(task) {
  const ds = datasources.value.find(d => d.id === task.datasource_id)
  if (!ds) {
    ElMessage.warning('未找到对应的数据源')
    return
  }

  editForm.value = {
    id: task.id,
    name: task.name,
    datasource_id: task.datasource_id,
    rule_ids: task.rule_ids,
    schedule_cron: task.schedule_cron || '',
    is_active: task.is_active,
  }

  // 加载该数据源下的规则
  try {
    const { data } = await validationRuleApi.list({ datasource_id: task.datasource_id })
    editAvailableRules.value = data
  } catch {
    ElMessage.error('加载规则失败')
  }

  editDialog.value = true
}

async function onEditDsChange(dsId) {
  editForm.value.rule_ids = []
  if (dsId) {
    const { data } = await validationRuleApi.list({ datasource_id: dsId })
    editAvailableRules.value = data
  } else {
    editAvailableRules.value = []
  }
}

async function handleUpdate() {
  saving.value = true
  try {
    await taskApi.update(editForm.value.id, editForm.value)
    ElMessage.success('任务更新成功')
    editDialog.value = false
    loadData()
  } catch {
    ElMessage.error('更新失败')
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
