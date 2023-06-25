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
    name: 'Users',
    component: () => import('@/views/Users.vue')
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('@/views/Schedule.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
