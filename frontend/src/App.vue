<template>
  <el-container style="height: 100vh">
    <el-header>
      <el-menu mode="horizontal" :default-active="activeRoute" router>
        <el-menu-item index="/datasources">数据源管理</el-menu-item>
        <el-menu-item index="/rules">校验规则</el-menu-item>
        <el-menu-item index="/tasks">校验任务</el-menu-item>
        <el-menu-item index="/results">校验报告</el-menu-item>
        <el-menu-item index="/trend">趋势分析</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeRoute = computed(() => route.path)
</script>

<style>
body {
  margin: 0;
  padding: 0;
}
</style>
