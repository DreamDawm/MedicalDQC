<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>校验规则配置</span>
          <el-button type="primary" @click="showDialog = true">新建规则</el-button>
        </div>
      </template>
      <el-table :data="rules" v-loading="loading" stripe>
        <el-table-column prop="table_name" label="表名" />
        <el-table-column prop="column_name" label="列名" />
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
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
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
            <el-option v-for="c in columns" :key="c.column_name" :label="`${c.column_name} (${c.data_type})`" :value="c.column_name" />
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
        <ParameterForm v-if="selectedRule" :schema="selectedRule.parameters_schema" v-model="form.parameters" />
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="saving">保存</el-button>
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
const builtinRules = ref([])
const datasources = ref([])
const tables = ref([])
const columns = ref([])
const loading = ref(false)
const showDialog = ref(false)
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

const selectedRule = computed(() =>
  builtinRules.value.find(r => r.id === form.value.builtin_rule_id)
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
  } finally {
    loading.value = false
  }
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

async function handleDelete(rule) {
  await ElMessageBox.confirm('确定删除该规则？', '提示')
  await validationRuleApi.delete(rule.id)
  ElMessage.success('已删除')
  loadData()
}

onMounted(loadData)
</script>
