<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import axios from 'axios';
import Cookies from 'js-cookie';

const router = useRouter();
const userStore = useUserStore();

const credentials = ref({
  username: '',
  password: ''
});

const error = ref('');
const loading = ref(false);

// Настраиваем axios
axios.defaults.baseURL = 'http://localhost:8000';
axios.defaults.withCredentials = true;

// Получаем CSRF токен при монтировании компонента
onMounted(async () => {
  try {
    // Делаем GET запрос для получения CSRF токена
    await axios.get('/api/auth/csrf/');
    const csrfToken = Cookies.get('csrftoken');
    if (csrfToken) {
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    }
  } catch (err) {
    console.error('Error fetching CSRF token:', err);
  }
});

async function login() {
  loading.value = true;
  error.value = '';
  
  try {
    console.log('Login credentials:', {
      username: credentials.value.username,
      password: credentials.value.password
    });

    const response = await axios.post('/api/auth/login/', credentials.value);
    
    console.log('Server response:', response.data);
    
    userStore.setUser({
      id: response.data.user_id,
      username: response.data.username,
      token: response.data.token
    });

    router.push('/profile');
  } catch (err) {
    console.error('Login error details:', {
      status: err.response?.status,
      data: err.response?.data,
      error: err.message
    });
    error.value = err.response?.data?.error || 'Неверное имя пользователя или пароль';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card mt-5">
          <div class="card-body">
            <h3 class="card-title text-center mb-4">Вход в систему</h3>
            
            <div v-if="error" class="alert alert-danger">
              {{ error }}
            </div>

            <form @submit.prevent="login">
              <div class="mb-3">
                <label class="form-label">Имя пользователя</label>
                <input 
                  v-model="credentials.username"
                  type="text"
                  class="form-control"
                  required
                  autocomplete="username"
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Пароль</label>
                <input 
                  v-model="credentials.password"
                  type="password"
                  class="form-control"
                  required
                  autocomplete="current-password"
                >
              </div>

              <button 
                type="submit" 
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Войти
              </button>
            </form>

            <div class="mt-3 text-muted">
              <small>
                Для входа используйте:<br>
                Admin: danil/admin123<br>
                User: user/user123
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template> 