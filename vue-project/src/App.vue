<script setup>
import { onMounted } from 'vue';
import axios from 'axios';
import "bootstrap/dist/css/bootstrap.min.css"
import Cookies from 'js-cookie';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();

// Устанавливаем базовый URL для axios
axios.defaults.baseURL = 'http://localhost:8000';

onMounted(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
  axios.defaults.withCredentials = true;
  userStore.initializeFromStorage();
})

async function logout() {
  try {
    const token = userStore.getToken;
    console.log('Logging out with token:', token); // Для отладки

    await axios.post('/api/auth/logout/', null, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    });

    userStore.clearUser();
    router.push('/login');
  } catch (err) {
    console.error('Ошибка при выходе:', err.response?.data || err);
    // Даже если запрос не удался, все равно очищаем данные пользователя
    userStore.clearUser();
    router.push('/login');
  }
}
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
    <div class="container">
      <router-link class="navbar-brand" to="/">Салон красоты</router-link>
      <div class="navbar-nav me-auto">
        <router-link class="nav-link" to="/clients">Клиенты</router-link>
        <router-link class="nav-link" to="/services">Услуги</router-link>
        <router-link class="nav-link" to="/masters">Мастера</router-link>
        <router-link class="nav-link" to="/appointments">Записи</router-link>
        <router-link class="nav-link" to="/reviews">Отзывы</router-link>
      </div>
      <div class="navbar-nav">
        <template v-if="userStore.isLoggedIn">
          <router-link class="nav-link" to="/profile">
            <i class="bi bi-person-circle"></i> {{ userStore.username }}
          </router-link>
          <a 
            @click.prevent="logout" 
            href="#" 
            class="nav-link" 
            style="cursor: pointer;"
            @mouseover="console.log('Current token:', userStore.getToken)"
          >
            <i class="bi bi-box-arrow-right"></i> Выход
          </a>
        </template>
        <template v-else>
          <router-link class="nav-link" to="/login">
            <i class="bi bi-box-arrow-in-right"></i> Вход
          </router-link>
        </template>
        <a v-if="userStore.isAdmin" href="/admin" class="nav-link" target="_blank">
          <i class="bi bi-gear-fill"></i> Админка
        </a>
      </div>
    </div>
  </nav>

  <router-view></router-view>
</template>

<style scoped>
.router-link-active {
  font-weight: bold;
  color: #0d6efd !important;
}
</style>
