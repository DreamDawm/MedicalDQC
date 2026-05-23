<template>
  <div class="progress-ring" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <!-- 背景圆环 -->
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        :stroke="bgColor"
        :stroke-width="strokeWidth"
      />
      <!-- 进度圆环 -->
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        :stroke="progressColor"
        :stroke-width="strokeWidth"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="offset"
        stroke-linecap="round"
        transform="rotate(-90)"
        :style="{ transformOrigin: '50% 50%' }"
      />
    </svg>
    <div class="progress-text" :style="{ fontSize: textSize + 'px' }">
      <span v-if="status === 'running'" class="percentage">{{ progress }}%</span>
      <span v-else-if="status === 'success'" class="status-icon success">✓</span>
      <span v-else-if="status === 'failed'" class="status-icon failed">✗</span>
      <span v-else-if="status === 'error'" class="status-icon error">!</span>
      <span v-else class="percentage">-</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  progress: {
    type: Number,
    default: 0,
  },
  status: {
    type: String,
    default: 'idle',
  },
  size: {
    type: Number,
    default: 50,
  },
  strokeWidth: {
    type: Number,
    default: 4,
  },
})

const radius = computed(() => (props.size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const offset = computed(() => {
  const progress = Math.min(100, Math.max(0, props.progress))
  return circumference.value * (1 - progress / 100)
})

const bgColor = '#e5e7eb'
const progressColor = computed(() => {
  if (props.status === 'success') return '#67c23a'
  if (props.status === 'failed') return '#f56c6c'
  if (props.status === 'error') return '#f56c6c'
  return '#409eff'
})

const textSize = computed(() => Math.max(10, props.size / 4))
</script>

<style scoped>
.progress-ring {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.progress-text {
  position: absolute;
  font-weight: 600;
  color: #606266;
}

.percentage {
  color: #409eff;
}

.status-icon {
  font-weight: bold;
  font-size: 1.2em;
}

.status-icon.success {
  color: #67c23a;
}

.status-icon.failed {
  color: #f56c6c;
}

.status-icon.error {
  color: #f56c6c;
}
</style>
