import { createRouter, createWebHistory } from 'vue-router'
import NowPlaying from '@/views/NowPlaying.vue'

const routes = [
  {
    path: '/',
    alias: '/index.html',
    name: 'NowPlaying',
    component: NowPlaying
  },
  {
    path: '/playout_history',
    name: 'Playout History',
    component: () => import('@/views/PlayoutHistory.vue')
  },
  {
    path: '/users',
    name: 'UsersPanel',
    component: () => import('@/views/UsersPanel.vue')
  },
  {
    path: '/schedule',
    name: 'SchedulePanel',
    component: () => import('@/views/SchedulePanel.vue')
  },
  {
    path: '/about',
    name: 'AboutPanel',
    component: () => import('@/views/AboutPanel.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
