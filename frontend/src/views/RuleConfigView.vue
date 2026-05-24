<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>校验规则配置</span>
          <el-button type="primary" @click="showDialog = true">新建规则</el-button>
        </div>
      </template>
      <el-table :data="rulesWithComments" v-loading="loading" stripe>
        <el-table-column prop="table_name" label="表名" />
        <el-table-column prop="column_name" label="列名" />
        <el-table-column prop="column_comment" label="列名注释" width="150">
          <template #default="{ row }">
            <span v-if="row.column_comment">{{ row.column_comment }}</span>
            <span v-else style="color: #999">-</span>
          </template>
        </el-table-column>
        <el-table-column label="规则类型">
          <template #default="{ row }">
            {{ getRuleName(row.builtin_rule_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重等级" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" title="新建校验规则" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="数据源">
          <el-select v-model="form.datasource_id" @change="onDatasourceChange" style="width: 100%">
            <el-option v-for="ds in datasources" :key="ds.id" :label="ds.name" :value="ds.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="表名">
          <el-select v-model="form.table_name" @change="onTableChange" style="width: 100%">
            <el-option v-for="t in tables" :key="t.table_name" :label="t.table_name" :value="t.table_name" />
          </el-select>
        </el-form-item>
        <el-form-item label="列名">
          <el-select v-model="form.column_name" clearable style="width: 100%">
            <el-option
              v-for="c in columns"
              :key="c.column_name"
              :label="formatColumnLabel(c)"
              :value="c.column_name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="校验规则">
          <RuleSelector v-model="form.builtin_rule_id" :rules="builtinRules" @change="onRuleChange" />
        </el-form-item>
        <el-form-item label="容忍度">
          <el-input-number v-model="form.mostly" :min="0" :max="1" :step="0.05" :precision="2" />
        </el-form-item>
        <el-form-item label="严重等级">
          <el-select v-model="form.severity" style="width: 100%">
            <el-option label="critical" value="critical" />
            <el-option label="warning" value="warning" />
            <el-option label="info" value="info" />
          </el-select>
        </el-form-item>
        <ParameterForm v-if="selectedRule" :schema="selectedRule.parameters_schema" v-model="form.parameters" :columns="columns" />
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑规则对话框 -->
    <el-dialog v-model="editDialog" title="编辑校验规则" width="600px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="数据源">
          <el-select v-model="editForm.datasource_id" @change="onEditDatasourceChange" style="width: 100%">
            <el-option v-for="ds in datasources" :key="ds.id" :label="ds.name" :value="ds.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="表名">
          <el-select v-model="editForm.table_name" @change="onEditTableChange" style="width: 100%">
            <el-option v-for="t in editTables" :key="t.table_name" :label="t.table_name" :value="t.table_name" />
          </el-select>
        </el-form-item>
        <el-form-item label="列名">
          <el-select v-model="editForm.column_name" clearable style="width: 100%">
            <el-option
              v-for="c in editColumns"
              :key="c.column_name"
              :label="formatColumnLabel(c)"
              :value="c.column_name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="校验规则">
          <RuleSelector v-model="editForm.builtin_rule_id" :rules="builtinRules" @change="onEditRuleChange" />
        </el-form-item>
        <el-form-item label="容忍度">
          <el-input-number v-model="editForm.mostly" :min="0" :max="1" :step="0.05" :precision="2" />
        </el-form-item>
        <el-form-item label="严重等级">
          <el-select v-model="editForm.severity" style="width: 100%">
            <el-option label="critical" value="critical" />
            <el-option label="warning" value="warning" />
            <el-option label="info" value="info" />
          </el-select>
        </el-form-item>
        <ParameterForm v-if="editSelectedRule" :schema="editSelectedRule.parameters_schema" v-model="editForm.parameters" :columns="editColumns" />
      </el-form>
      <template #footer>
        <el-button @click="editDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { datasourceApi, builtinRuleApi, validationRuleApi } from '../api'
import RuleSelector from '../components/RuleSelector.vue'
import ParameterForm from '../components/ParameterForm.vue'

const rules = ref([])
const rulesWithComments = ref([])
const builtinRules = ref([])
const datasources = ref([])
const columnCommentMap = ref({}) // 缓存列注释
const tables = ref([])
const columns = ref([])
const editTables = ref([])
const editColumns = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editDialog = ref(false)
const saving = ref(false)

const form = ref({
  datasource_id: '',
  table_name: '',
  column_name: '',
  builtin_rule_id: '',
  parameters: {},
  mostly: null,
  severity: 'warning',
})

const editForm = ref({
  id: '',
  datasource_id: '',
  table_name: '',
  column_name: '',
  builtin_rule_id: '',
  parameters: {},
  mostly: null,
  severity: 'warning',
  enabled: true,
})

const selectedRule = computed(() =>
  builtinRules.value.find(r => r.id === form.value.builtin_rule_id)
)

const editSelectedRule = computed(() =>
  builtinRules.value.find(r => r.id === editForm.value.builtin_rule_id)
)

function getRuleName(builtinRuleId) {
  const r = builtinRules.value.find(b => b.id === builtinRuleId)
  return r ? r.display_name : builtinRuleId
}

function severityType(severity) {
  if (severity === 'critical') return 'danger'
  if (severity === 'warning') return 'warning'
  return 'info'
}

function formatColumnLabel(col) {
  // 格式：英文字段 (类型) 中文注释
  const parts = [col.column_name, `(${col.data_type})`]
  if (col.comment) {
    parts.push(col.comment)
  }
  return parts.join(' ')
}

async function loadData() {
  loading.value = true
  try {
    const [rulesRes, builtinRes, dsRes] = await Promise.all([
      validationRuleApi.list(),
      builtinRuleApi.list(),
      datasourceApi.list(),
    ])
    rules.value = rulesRes.data
    builtinRules.value = builtinRes.data
    datasources.value = dsRes.data
    // 加载列注释
    await loadColumnComments()
  } finally {
    loading.value = false
  }
}

async function loadColumnComments() {
  // 按数据源和表名分组
  const dsTableMap = new Map()
  for (const rule of rules.value) {
    const ds = datasources.value.find(d => d.id === rule.datasource_id)
    if (!ds || !rule.table_name) continue
    const key = `${ds.id}:${rule.table_name}`
    if (!dsTableMap.has(key)) {
      dsTableMap.set(key, { dsId: ds.id, tableName: rule.table_name })
    }
  }

  // 批量获取列注释
  for (const { dsId, tableName } of dsTableMap.values()) {
    const cacheKey = `${dsId}:${tableName}`
    if (columnCommentMap.value[cacheKey]) continue
    try {
      const { data: columns } = await datasourceApi.getColumns(dsId, tableName)
      const commentMap = {}
      for (const col of columns) {
        if (col.comment) {
          commentMap[col.column_name] = col.comment
        }
      }
      columnCommentMap.value[cacheKey] = commentMap
    } catch {
      columnCommentMap.value[cacheKey] = {}
    }
  }

  // 合并规则和列注释
  rulesWithComments.value = rules.value.map(rule => {
    const ds = datasources.value.find(d => d.id === rule.datasource_id)
    const cacheKey = ds ? `${ds.id}:${rule.table_name}` : null
    const commentMap = cacheKey ? columnCommentMap.value[cacheKey] || {} : {}
    return {
      ...rule,
      column_comment: rule.column_name ? commentMap[rule.column_name] || '' : ''
    }
  })
}

async function onDatasourceChange(dsId) {
  tables.value = []
  columns.value = []
  form.value.table_name = ''
  form.value.column_name = ''
  if (dsId) {
    const { data } = await datasourceApi.getTables(dsId)
    tables.value = data
  }
}

async function onTableChange(table) {
  columns.value = []
  form.value.column_name = ''
  if (table && form.value.datasource_id) {
    const { data } = await datasourceApi.getColumns(form.value.datasource_id, table)
    columns.value = data
  }
}

function onRuleChange() {
  form.value.parameters = {}
}

async function handleCreate() {
  saving.value = true
  try {
    await validationRuleApi.create(form.value)
    ElMessage.success('规则创建成功')
    showDialog.value = false
    loadData()
  } catch {
    ElMessage.error('创建失败')
  } finally {
    saving.value = false
  }
}

async function handleEdit(rule) {
  // 查找规则对应的数据源
  const ds = datasources.value.find(d => d.name === rule.datasource_name || d.id === rule.datasource_id)
  if (!ds) {
    ElMessage.warning('未找到对应的数据源')
    return
  }

  editForm.value = {
    id: rule.id,
    datasource_id: ds.id,
    table_name: rule.table_name,
    column_name: rule.column_name,
    builtin_rule_id: rule.builtin_rule_id,
    parameters: rule.parameters || {},
    mostly: rule.mostly,
    severity: rule.severity,
    enabled: rule.enabled,
  }

  // 加载表和列
  try {
    const { data: tableData } = await datasourceApi.getTables(ds.id)
    editTables.value = tableData

    if (rule.table_name) {
      const { data: colData } = await datasourceApi.getColumns(ds.id, rule.table_name)
      editColumns.value = colData
    }
  } catch {
    ElMessage.error('加载数据失败')
  }

  editDialog.value = true
}

async function onEditDatasourceChange(dsId) {
  editTables.value = []
  editColumns.value = []
  editForm.value.table_name = ''
  editForm.value.column_name = ''
  if (dsId) {
    const { data } = await datasourceApi.getTables(dsId)
    editTables.value = data
  }
}

async function onEditTableChange(table) {
  editColumns.value = []
  editForm.value.column_name = ''
  if (table && editForm.value.datasource_id) {
    const { data } = await datasourceApi.getColumns(editForm.value.datasource_id, table)
    editColumns.value = data
  }
}

function onEditRuleChange() {
  editForm.value.parameters = {}
}

async function handleUpdate() {
  saving.value = true
  try {
    await validationRuleApi.update(editForm.value.id, editForm.value)
    ElMessage.success('规则更新成功')
    editDialog.value = false
    loadData()
  } catch {
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(rule) {
  await ElMessageBox.confirm('确定删除该规则？', '提示')
  await validationRuleApi.delete(rule.id)
  ElMessage.success('已删除')
  loadData()
}

onMounted(loadData)
</script>
