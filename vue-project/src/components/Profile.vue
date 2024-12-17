<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import axios from 'axios';

const userStore = useUserStore();
const loading = ref(false);
const userDetails = ref(null);
const appointments = ref([]);
const reviews = ref([]);

async function fetchUserData() {
  loading.value = true;
  try {
    const [userRes, appointmentsRes, reviewsRes] = await Promise.all([
      axios.get('/api/users/profile/', {
        headers: {
          'Authorization': `Token ${userStore.getToken}`
        }
      }),
      axios.get('/api/appointments/', {
        headers: {
          'Authorization': `Token ${userStore.getToken}`
        }
      }),
      axios.get('/api/reviews/', {
        headers: {
          'Authorization': `Token ${userStore.getToken}`
        }
      })
    ]);

    userDetails.value = userRes.data;
    appointments.value = appointmentsRes.data;
    reviews.value = reviewsRes.data;
  } catch (error) {
    console.error('Ошибка загрузки данных:', error);
  }
  loading.value = false;
}

onMounted(() => {
  if (userStore.isLoggedIn) {
    fetchUserData();
  }
});
</script>

<template>
  <div class="container" v-if="userStore.isLoggedIn">
    <div class="row">
      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Профиль</h5>
            <div v-if="loading">Загрузка...</div>
            <div v-else-if="userDetails">
              <p><strong>Имя пользователя:</strong> {{ userStore.username }}</p>
              <p><strong>Email:</strong> {{ userDetails.email }}</p>
              <p><strong>Дата регистрации:</strong> {{ new Date(userDetails.date_joined).toLocaleDateString() }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-8">
        <div class="card mb-4">
          <div class="card-body">
            <h5 class="card-title">Мои записи</h5>
            <div v-if="loading">Загрузка...</div>
            <div v-else>
              <table class="table">
                <thead>
                  <tr>
                    <th>Услуга</th>
                    <th>Мастер</th>
                    <th>Дата</th>
                    <th>Статус</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="appointment in appointments" :key="appointment.id">
                    <td>{{ appointment.service_name }}</td>
                    <td>{{ appointment.master_name }}</td>
                    <td>{{ new Date(appointment.datetime).toLocaleString() }}</td>
                    <td>
                      <span class="badge bg-success">Подтверждено</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Мои отзывы</h5>
            <div v-if="loading">Загрузка...</div>
            <div v-else>
              <div v-for="review in reviews" :key="review.id" class="mb-3">
                <div class="d-flex justify-content-between">
                  <h6>{{ review.service_name }}</h6>
                  <div>{{ '⭐'.repeat(review.rating) }}</div>
                </div>
                <p class="text-muted mb-1">{{ new Date(review.date).toLocaleDateString() }}</p>
                <p>{{ review.text }}</p>
                <hr>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="container">
    <div class="alert alert-warning">
      Необходима авторизация для просмотра профиля
    </div>
  </div>
</template>

<style scoped>
.container {
  margin-top: 2rem;
}
.card {
  margin-bottom: 1rem;
}
</style> 