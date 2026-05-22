import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/datasources',
  },
  {
    path: '/datasources',
    name: 'Datasources',
    component: () => import('../views/DatasourceView.vue'),
  },
  {
    path: '/rules',
    name: 'Rules',
    component: () => import('../views/RuleConfigView.vue'),
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('../views/TaskView.vue'),
  },
  {
    path: '/results',
    name: 'Results',
    component: () => import('../views/ResultView.vue'),
  },
  {
    path: '/trend',
    name: 'Trend',
    component: () => import('../views/TrendView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
