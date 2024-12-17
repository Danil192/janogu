import { createRouter, createWebHistory } from 'vue-router'
import ClientList from '@/components/ClientList.vue'
import ServiceList from '@/components/ServiceList.vue'
import MasterList from '@/components/MasterList.vue'
import AppointmentList from '@/components/AppointmentList.vue'
import ReviewList from '@/components/ReviewList.vue'
import Profile from '@/components/Profile.vue'
import Login from '@/components/Login.vue'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/clients'
    },
    {
      path: '/clients',
      name: 'clients',
      component: ClientList
    },
    {
      path: '/services',
      name: 'services',
      component: ServiceList
    },
    {
      path: '/masters',
      name: 'masters',
      component: MasterList
    },
    {
      path: '/appointments',
      name: 'appointments',
      component: AppointmentList
    },
    {
      path: '/reviews',
      name: 'reviews',
      component: ReviewList
    },
    {
      path: '/profile',
      name: 'profile',
      component: Profile
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    }
  ]
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  const publicPages = ['/login'];
  const authRequired = !publicPages.includes(to.path);

  if (authRequired && !userStore.isLoggedIn) {
    return next('/login');
  }

  next();
});

export default router
