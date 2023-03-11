import App from '../App.vue'

export default [
  {
    path: '/',
    redirect: '/index',
    component: App,
  },
  {
    path: '/index',
    name: 'index',
    component: () => import('../views/index.vue'),
    meta: {},
  },
  {
    path: '/:pathMatch(.*)',
    component: () => import('../components/commom/404.vue'),
  },
]
