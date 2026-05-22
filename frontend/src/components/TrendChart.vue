<template>
  <v-chart :option="chartOption" style="height: 400px; width: 100%" autoresize />
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent])

const props = defineProps({
  data: { type: Array, default: () => [] },
})

const chartOption = computed(() => ({
  title: { text: '通过率趋势', left: 'center' },
  tooltip: { trigger: 'axis', formatter: '{b}<br/>通过率: {c}%' },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: props.data.map(d => d.date),
    axisLabel: { rotate: 30 },
  },
  yAxis: {
    type: 'value',
    name: '通过率 (%)',
    min: 0,
    max: 100,
  },
  series: [
    {
      name: '通过率',
      type: 'line',
      data: props.data.map(d => d.pass_rate),
      smooth: true,
      itemStyle: { color: '#409eff' },
      areaStyle: { color: 'rgba(64, 158, 255, 0.1)' },
    },
  ],
}))
</script>
