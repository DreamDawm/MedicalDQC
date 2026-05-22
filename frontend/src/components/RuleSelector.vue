<template>
  <el-select
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event); $emit('change', $event)"
    style="width: 100%"
    filterable
  >
    <el-option-group v-for="group in groupedRules" :key="group.label" :label="group.label">
      <el-option
        v-for="rule in group.options"
        :key="rule.id"
        :label="rule.display_name"
        :value="rule.id"
      />
    </el-option-group>
  </el-select>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: String,
  rules: { type: Array, default: () => [] },
})

defineEmits(['update:modelValue', 'change'])

const groupedRules = computed(() => {
  const groups = {}
  for (const rule of props.rules) {
    if (!groups[rule.category]) {
      groups[rule.category] = []
    }
    groups[rule.category].push(rule)
  }
  return Object.entries(groups).map(([label, options]) => ({ label, options }))
})
</script>
