<template>
  <div v-if="Object.keys(schema).length > 0">
    <el-form-item v-for="(config, key) in schema" :key="key" :label="config.label || key">
      <el-input
        v-if="config.type === 'string'"
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
})

const emit = defineEmits(['update:modelValue'])

function update(key, value) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}
</script>
