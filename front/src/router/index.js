import { createRouter, createWebHistory } from 'vue-router'
import NowPlaying from '../views/NowPlaying.vue'

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
    component: () => import(/* webpackChunkName: "playout_history" */ '../views/PlayoutHistory.vue')
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import(/* webpackChunkName: "users" */ '../views/Users.vue')
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  }
]

const router = createRouter({
  history: createWebHistory("/#/"),
  routes
})

export default router
