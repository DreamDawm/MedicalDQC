<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="执行日志"
    width="700px"
    top="10vh"
    destroy-on-close
  >
    <div class="log-container" ref="logContainer">
      <div v-if="loading" class="log-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>连接中...</span>
      </div>
      <div v-else-if="logs.length === 0" class="log-empty">
        暂无日志
      </div>
      <div v-else>
        <div
          v-for="(log, index) in logs"
          :key="index"
          class="log-entry"
          :class="{ 'log-error': isLogError(log) }"
        >
          {{ log }}
        </div>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <span class="status-text" :class="statusClass">
          {{ statusText }}
        </span>
        <el-button @click="$emit('update:visible', false)">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  taskId: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:visible', 'complete'])

const logs = ref([])
const loading = ref(false)
const status = ref('idle')
const logContainer = ref(null)
let eventSource = null

const statusText = computed(() => {
  if (status.value === 'running') return '执行中...'
  if (status.value === 'success') return '执行成功'
  if (status.value === 'failed') return '执行失败'
  if (status.value === 'error') return '执行出错'
  return '等待执行'
})

const statusClass = computed(() => {
  if (status.value === 'success') return 'status-success'
  if (status.value === 'failed' || status.value === 'error') return 'status-error'
  if (status.value === 'running') return 'status-running'
  return ''
})

function isLogError(log) {
  return log.toLowerCase().includes('error') || log.toLowerCase().includes('出错')
}

function scrollToBottom() {
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

function connectSSE() {
  if (!props.taskId) return

  loading.value = true
  logs.value = []
  status.value = 'running'

  eventSource = new EventSource(`/api/tasks/${props.taskId}/stream`)

  eventSource.onmessage = (event) => {
    loading.value = false
    const data = JSON.parse(event.data)

    if (data.type === 'log') {
      logs.value.push(data.message)
      setTimeout(scrollToBottom, 50)
    } else if (data.type === 'progress') {
      status.value = data.status
    } else if (data.type === 'complete') {
      status.value = data.status
      eventSource.close()
      emit('complete', data.status)
    } else if (data.type === 'timeout') {
      logs.value.push('[系统] 连接超时，请刷新页面')
      eventSource.close()
    }
  }

  eventSource.onerror = () => {
    loading.value = false
    logs.value.push('[系统] 连接断开')
    eventSource.close()
  }
}

function disconnectSSE() {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
}

watch(() => props.visible, (newVal) => {
  if (newVal) {
    connectSSE()
  } else {
    disconnectSSE()
  }
})

onUnmounted(() => {
  disconnectSSE()
})
</script>

<style scoped>
.log-container {
  height: 400px;
  overflow-y: auto;
  background: #1e1e1e;
  border-radius: 6px;
  padding: 12px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.log-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  gap: 8px;
}

.log-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.log-entry {
  color: #d4d4d4;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-error {
  color: #f56c6c;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-text {
  font-weight: 500;
}

.status-success {
  color: #67c23a;
}

.status-error {
  color: #f56c6c;
}

.status-running {
  color: #409eff;
}
</style>
