<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="datasource ? '编辑数据源' : '新建数据源'"
    width="500px"
  >
    <el-form :model="form" label-width="80px">
      <el-form-item label="名称">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="类型">
        <el-select v-model="form.db_type" style="width: 100%">
          <el-option label="MySQL" value="mysql" />
          <el-option label="PostgreSQL" value="postgresql" />
          <el-option label="SQL Server" value="sqlserver" />
        </el-select>
      </el-form-item>
      <el-form-item label="主机">
        <el-input v-model="form.host" />
      </el-form-item>
      <el-form-item label="端口">
        <el-input-number v-model="form.port" :min="1" :max="65535" />
      </el-form-item>
      <el-form-item label="数据库">
        <el-input v-model="form.database" />
      </el-form-item>
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { datasourceApi } from '../api'

const props = defineProps({
  visible: Boolean,
  datasource: Object,
})

const emit = defineEmits(['update:visible', 'saved'])

const saving = ref(false)
const form = ref(getDefaultForm())

function getDefaultForm() {
  return { name: '', db_type: 'mysql', host: '', port: 3306, database: '', username: '', password: '' }
}

watch(() => props.visible, (val) => {
  if (val) {
    form.value = props.datasource
      ? { ...props.datasource, password: '' }
      : getDefaultForm()
  }
})

async function handleSave() {
  saving.value = true
  try {
    if (props.datasource) {
      await datasourceApi.update(props.datasource.id, form.value)
    } else {
      await datasourceApi.create(form.value)
    }
    ElMessage.success('保存成功')
    emit('update:visible', false)
    emit('saved')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>
