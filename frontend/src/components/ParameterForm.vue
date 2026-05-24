<template>
  <div v-if="Object.keys(schema).length > 0">
    <el-form-item v-for="(config, key) in schema" :key="key" :label="config.label || key">
      <el-select
        v-if="isColumnParam(key)"
        :model-value="modelValue[key]"
        @update:model-value="update(key, $event)"
        filterable
        clearable
        style="width: 100%"
      >
        <el-option
          v-for="c in columns"
          :key="c.column_name"
          :label="formatColumnLabel(c)"
          :value="c.column_name"
        />
      </el-select>
      <el-input
        v-else-if="config.type === 'string'"
        :model-value="modelValue[key]"
        @update:model-value="update(key, $event)"
      />
      <el-input-number
        v-else-if="config.type === 'integer'"
        :model-value="modelValue[key]"
        @update:model-value="update(key, $event)"
      />
      <el-input-number
        v-else-if="config.type === 'number' || config.type === 'float'"
        :model-value="modelValue[key]"
        @update:model-value="update(key, $event)"
        :step="0.01"
      />
      <el-input
        v-else-if="config.type === 'array'"
        :model-value="Array.isArray(modelValue[key]) ? modelValue[key].join(',') : ''"
        @update:model-value="update(key, $event ? $event.split(',') : [])"
        placeholder="逗号分隔多个值"
      />
      <el-input
        v-else
        :model-value="modelValue[key]"
        @update:model-value="update(key, $event)"
      />
    </el-form-item>
  </div>
</template>

<script setup>
const props = defineProps({
  schema: { type: Object, default: () => ({}) },
  modelValue: { type: Object, default: () => ({}) },
  columns: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

function isColumnParam(key) {
  const k = key.toLowerCase()
  return (k.includes('column_a') || k.includes('column_b')) && props.columns.length > 0
}

function formatColumnLabel(col) {
  const parts = [col.column_name, `(${col.data_type})`]
  if (col.comment) parts.push(col.comment)
  return parts.join(' ')
}

function update(key, value) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}
</script>
