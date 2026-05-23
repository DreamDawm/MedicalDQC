<template>
  <el-select v-model="selectedOption" @change="handleChange" style="width: 100%" clearable placeholder="选择定时计划">
    <el-option label="手动执行（无定时）" value="" />
    <el-option-group label="每小时">
      <el-option label="每小时整点执行" value="0 * * * *" />
      <el-option label="每2小时执行" value="0 */2 * * *" />
      <el-option label="每4小时执行" value="0 */4 * * *" />
      <el-option label="每6小时执行" value="0 */6 * * *" />
      <el-option label="每12小时执行" value="0 */12 * * *" />
    </el-option-group>
    <el-option-group label="每天">
      <el-option label="每天 00:00 执行" value="0 0 * * *" />
      <el-option label="每天 06:00 执行" value="0 6 * * *" />
      <el-option label="每天 08:00 执行" value="0 8 * * *" />
      <el-option label="每天 12:00 执行" value="0 12 * * *" />
      <el-option label="每天 18:00 执行" value="0 18 * * *" />
      <el-option label="每天 22:00 执行" value="0 22 * * *" />
    </el-option-group>
    <el-option-group label="每周">
      <el-option label="每周一 00:00 执行" value="0 0 * * 1" />
      <el-option label="每周一 08:00 执行" value="0 8 * * 1" />
      <el-option label="每周二 00:00 执行" value="0 0 * * 2" />
      <el-option label="每周三 00:00 执行" value="0 0 * * 3" />
      <el-option label="每周四 00:00 执行" value="0 0 * * 4" />
      <el-option label="每周五 00:00 执行" value="0 0 * * 5" />
      <el-option label="每周六 00:00 执行" value="0 0 * * 6" />
      <el-option label="每周日 00:00 执行" value="0 0 * * 0" />
    </el-option-group>
    <el-option-group label="每月">
      <el-option label="每月1日 00:00 执行" value="0 0 1 * *" />
      <el-option label="每月1日 08:00 执行" value="0 8 1 * *" />
      <el-option label="每月15日 00:00 执行" value="0 0 15 * *" />
      <el-option label="每月最后一天 00:00 执行" value="0 0 L * *" />
    </el-option-group>
    <el-option-group label="自定义">
      <el-option label="自定义表达式..." value="__custom__" />
    </el-option-group>
  </el-select>

  <el-dialog v-model="showCustomDialog" title="自定义 Cron 表达式" width="400px">
    <el-form label-width="100px">
      <el-form-item label="分钟">
        <el-input-number v-model="custom.minute" :min="0" :max="59" />
      </el-form-item>
      <el-form-item label="小时">
        <el-input-number v-model="custom.hour" :min="0" :max="23" />
      </el-form-item>
      <el-form-item label="日期">
        <el-input v-model="custom.day" placeholder="* 或 1-31 或 1,15" />
      </el-form-item>
      <el-form-item label="月份">
        <el-input v-model="custom.month" placeholder="* 或 1-12 或 1,6,12" />
      </el-form-item>
      <el-form-item label="星期">
        <el-input v-model="custom.weekday" placeholder="* 或 0-7 (0和7都是周日)" />
      </el-form-item>
      <el-form-item label="生成的表达式">
        <el-input :model-value="customCron" readonly />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showCustomDialog = false">取消</el-button>
      <el-button type="primary" @click="applyCustom">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const selectedOption = ref('')
const showCustomDialog = ref(false)
const custom = ref({
  minute: 0,
  hour: 0,
  day: '*',
  month: '*',
  weekday: '*'
})

const customCron = computed(() => {
  return `${custom.value.minute} ${custom.value.hour} ${custom.value.day} ${custom.value.month} ${custom.value.weekday}`
})

watch(() => props.modelValue, (newVal) => {
  selectedOption.value = newVal
}, { immediate: true })

function handleChange(val) {
  if (val === '__custom__') {
    showCustomDialog.value = true
    return
  }
  emit('update:modelValue', val || '')
}

function applyCustom() {
  emit('update:modelValue', customCron.value)
  showCustomDialog.value = false
  selectedOption.value = customCron.value
}
</script>
