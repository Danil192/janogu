<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const username = ref('');
const router = useRouter();

onMounted(() => {
  username.value = localStorage.getItem('username');
});

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  router.push('/login');
}
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
    <div class="container">
      <router-link class="navbar-brand" to="/">Beauty Salon</router-link>
      
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarContent">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/services">Услуги</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/clients">Клиенты</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/masters">Мастера</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/appointments">Записи</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/reviews">Отзывы</router-link>
          </li>
        </ul>
        
        <div class="d-flex align-items-center">
          <a href="/admin" class="nav-link me-3" target="_blank">
            <i class="bi bi-gear-fill"></i> Админка
          </a>
          
          <div v-if="username" class="d-flex align-items-center">
            <span class="navbar-text me-3">
              {{ username }}
            </span>
            <button class="btn btn-outline-danger" @click="logout">
              Выйти
            </button>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template> 