<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import axios from 'axios';
import { useUserStore } from '@/stores/user';
import { Modal } from 'bootstrap';
import Chart from 'chart.js/auto';

const userStore = useUserStore();
const reviews = ref([]);
const clients = ref([]);
const services = ref([]);
const loading = ref(false);
const editModal = ref(null);
const editingReview = ref({});

// Добавляем фильтры
const filters = ref({
  client: '',
  service: '',
  rating: '',
  dateFrom: '',
  dateTo: '',
  comment: ''
});

// Вычисляемое свойство для фильтрации отзывов
const filteredReviews = computed(() => {
  if (!reviews.value) return [];
  
  return reviews.value.filter(review => {
    // Фильтр по клиенту
    const clientMatch = !filters.value.client || 
      review.client === parseInt(filters.value.client);
    
    // Фильтр по услуге
    const serviceMatch = !filters.value.service || 
      review.service === parseInt(filters.value.service);
    
    // Фильтр по оценке
    const ratingMatch = !filters.value.rating || 
      review.rating === parseInt(filters.value.rating);
    
    // Фильтр по дате
    const reviewDate = new Date(review.date);
    const dateFromMatch = !filters.value.dateFrom || 
      reviewDate >= new Date(filters.value.dateFrom);
    const dateToMatch = !filters.value.dateTo || 
      reviewDate <= new Date(filters.value.dateTo);
    
    // Фильтр по комментарию
    const commentMatch = !filters.value.comment || 
      review.comment.toLowerCase().includes(filters.value.comment.toLowerCase());
    
    return clientMatch && serviceMatch && ratingMatch && 
           dateFromMatch && dateToMatch && commentMatch;
  });
});

const reviewToAdd = ref({
  service: null,
  rating: 5,
  comment: ''
});

async function addReview() {
  try {
    const formData = {
      service: reviewToAdd.value.service,
      rating: reviewToAdd.value.rating,
      comment: reviewToAdd.value.comment
    };

    await axios.post('/api/reviews/', formData, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`,
        'Content-Type': 'application/json'
      }
    });

    await fetchData();
    reviewToAdd.value = { service: null, rating: 5, comment: '' };
  } catch (error) {
    console.error('Ошибка добавления:', error.response?.data || error);
    let errorMessage = 'Ошибка при добавлении отзыва';
    if (error.response?.data) {
      if (typeof error.response.data === 'object') {
        errorMessage += ': ' + Object.values(error.response.data).join(', ');
      } else {
        errorMessage += ': ' + error.response.data;
      }
    }
    alert(errorMessage);
  }
}

async function fetchData() {
  loading.value = true;
  try {
    const [reviewsRes, servicesRes] = await Promise.all([
      axios.get('/api/reviews/', {
        headers: {
          'Authorization': `Token ${userStore.getToken}`
        }
      }),
      axios.get('/api/services/', {
        headers: {
          'Authorization': `Token ${userStore.getToken}`
        }
      })
    ]);
    reviews.value = reviewsRes.data;
    services.value = servicesRes.data;
  } catch (error) {
    console.error('Ошибка загрузки данных:', error);
  }
  loading.value = false;
}

onMounted(() => {
  fetchData();
  editModal.value = new Modal(document.getElementById('editModal'));
});

function editReview(review) {
  editingReview.value = { ...review };
  editModal.value.show();
}

async function saveEdit() {
  try {
    const formData = {
      service: editingReview.value.service,
      rating: editingReview.value.rating,
      comment: editingReview.value.comment
    };

    await axios.put(`/api/reviews/${editingReview.value.id}/`, formData, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`,
        'Content-Type': 'application/json'
      }
    });

    await fetchData();
    editModal.value.hide();
  } catch (error) {
    console.error('Ошибка при редактировании:', error.response?.data || error);
    alert('Ошибка при редактировании отзыва');
  }
}

async function deleteReview(id) {
  if (!confirm('Вы уверены, что хотите удалить этот отзыв?')) {
    return;
  }

  try {
    await axios.delete(`/api/reviews/${id}/`, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`
      }
    });
    await fetchData();
  } catch (error) {
    console.error('Ошибка при удалении:', error.response?.data || error);
    alert('Ошибка при удалении отзыва');
  }
}

// Добавляем состояние для статистики
const showStats = ref(false);
let chart = null;

// Вычисляем статистику
const statistics = computed(() => {
  if (!reviews.value) return null;
  
  const stats = {
    totalReviews: reviews.value.length,
    averageRating: 0,
    ratingDistribution: Array(5).fill(0),
    serviceRatings: {},
    recentTrend: []
  };
  
  reviews.value.forEach(review => {
    // Считаем распределение оценок
    stats.ratingDistribution[review.rating - 1]++;
    
    // Считаем средний рейтинг
    stats.averageRating += review.rating;
    
    // Группируем по услугам
    if (!stats.serviceRatings[review.service]) {
      stats.serviceRatings[review.service] = {
        count: 0,
        sum: 0,
        name: services.value.find(s => s.id === review.service)?.name
      };
    }
    stats.serviceRatings[review.service].count++;
    stats.serviceRatings[review.service].sum += review.rating;
  });
  
  stats.averageRating = stats.averageRating / stats.totalReviews;
  
  return stats;
});

// Функция для отображения графика
function showStatistics() {
  showStats.value = !showStats.value;
  
  if (showStats.value) {
    nextTick(() => {
      const ctx = document.getElementById('statsChart').getContext('2d');
      
      if (chart) {
        chart.destroy();
      }
      
      chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['1★', '2★', '3★', '4★', '5★'],
          datasets: [{
            label: 'Распределение оценок',
            data: statistics.value.ratingDistribution,
            backgroundColor: [
              'rgba(255, 99, 132, 0.5)',
              'rgba(255, 159, 64, 0.5)',
              'rgba(255, 205, 86, 0.5)',
              'rgba(75, 192, 192, 0.5)',
              'rgba(54, 162, 235, 0.5)'
            ],
            borderColor: [
              'rgb(255, 99, 132)',
              'rgb(255, 159, 64)',
              'rgb(255, 205, 86)',
              'rgb(75, 192, 192)',
              'rgb(54, 162, 235)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          animation: {
            duration: 1000,
            easing: 'easeInOutQuart'
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          }
        }
      });
    });
  }
}
</script>

<template>
  <div class="container mt-4">
    <h2>Отзывы</h2>

    <!-- Панель фильтров -->
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Фильтры</h5>
        <div class="row g-3">
          <!-- Фильтр по клиенту -->
          <div class="col-md-4">
            <select 
              v-model="filters.client"
              class="form-select"
            >
              <option value="">Все клиенты</option>
              <option v-for="client in clients" :key="client.id" :value="client.id">
                {{ client.name }}
              </option>
            </select>
          </div>

          <!-- Фильтр по услуге -->
          <div class="col-md-4">
            <select 
              v-model="filters.service"
              class="form-select"
            >
              <option value="">Все услуги</option>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }}
              </option>
            </select>
          </div>

          <!-- Фильтр по оценке -->
          <div class="col-md-4">
            <select 
              v-model="filters.rating"
              class="form-select"
            >
              <option value="">Все оценки</option>
              <option v-for="rating in 5" :key="rating" :value="rating">
                {{ rating }} {{ rating === 1 ? 'звезда' : rating < 5 ? 'звезды' : 'звёзд' }}
              </option>
            </select>
          </div>

          <!-- Фильтр по дате -->
          <div class="col-md-3">
            <input 
              type="date"
              v-model="filters.dateFrom"
              class="form-control"
              placeholder="Дата с"
            >
          </div>
          <div class="col-md-3">
            <input 
              type="date"
              v-model="filters.dateTo"
              class="form-control"
              placeholder="Дата по"
            >
          </div>

          <!-- Фильтр по комментарию -->
          <div class="col-md-6">
            <input 
              type="text"
              v-model="filters.comment"
              class="form-control"
              placeholder="Поиск по комментарию"
            >
          </div>
        </div>
      </div>
    </div>

    <!-- Добавляем кнопку статистики после фильтров -->
    <div class="text-end mb-3">
      <button 
        class="btn btn-info"
        @click="showStatistics"
      >
        <i class="bi" :class="showStats ? 'bi-graph-down' : 'bi-graph-up'"></i>
        {{ showStats ? 'Скрыть статистику' : 'Показать статистику' }}
      </button>
    </div>
    
    <!-- Панель статистики -->
    <div v-if="showStats" class="statistics-panel">
      <div class="card mb-4">
        <div class="card-body">
          <div class="row">
            <div class="col-md-4">
              <div class="stat-card">
                <h3>{{ statistics.totalReviews }}</h3>
                <p>Всего отзывов</p>
              </div>
            </div>
            <div class="col-md-4">
              <div class="stat-card">
                <h3>{{ statistics.averageRating.toFixed(1) }}★</h3>
                <p>Средняя оценка</p>
              </div>
            </div>
            <div class="col-md-4">
              <div class="stat-card">
                <h3>{{ statistics.ratingDistribution[4] }}</h3>
                <p>Отличных отзывов</p>
              </div>
            </div>
          </div>
          
          <!-- График -->
          <div class="chart-container">
            <canvas id="statsChart"></canvas>
          </div>
          
          <!-- Рейтинг по услугам -->
          <div class="service-ratings mt-4">
            <h5>Рейтинг услуг</h5>
            <div class="row">
              <div 
                v-for="(stat, serviceId) in statistics.serviceRatings" 
                :key="serviceId"
                class="col-md-6 mb-2"
              >
                <div class="service-rating-card">
                  <span class="service-name">{{ stat.name }}</span>
                  <div class="rating-bar">
                    <div 
                      class="rating-fill"
                      :style="{
                        width: `${(stat.sum / stat.count / 5) * 100}%`,
                        backgroundColor: `hsl(${(stat.sum / stat.count / 5) * 120}, 70%, 50%)`
                      }"
                    ></div>
                  </div>
                  <span class="rating-value">{{ (stat.sum / stat.count).toFixed(1) }}★</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Форма добавления -->
    <form @submit.prevent="addReview" class="mb-4">
      <div class="row g-3 align-items-center">
        <div class="col">
          <select v-model="reviewToAdd.service" class="form-select" required>
            <option value="">Выберите услугу</option>
            <option v-for="service in services" :key="service.id" :value="service.id">
              {{ service.name }}
            </option>
          </select>
        </div>
        <div class="col">
          <select v-model="reviewToAdd.rating" class="form-select" required>
            <option value="5">★★★★★</option>
            <option value="4">★★★★☆</option>
            <option value="3">★★★☆☆</option>
            <option value="2">★★☆☆☆</option>
            <option value="1">★☆☆☆☆</option>
          </select>
        </div>
        <div class="col">
          <input 
            type="text" 
            v-model="reviewToAdd.comment" 
            class="form-control"
            placeholder="Ваш отзыв"
            required
          >
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">
            <i class="bi bi-plus-lg"></i> Добавить отзыв
          </button>
        </div>
      </div>
    </form>

    <!-- Список отзывов -->
    <div v-if="loading">Загрузка...</div>
    <table v-else class="table">
      <thead>
        <tr>
          <th>Клиент</th>
          <th>Услуга</th>
          <th>Оценка</th>
          <th>Комментарий</th>
          <th>Дата</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="review in filteredReviews" :key="review.id">
          <td>{{ clients.find(c => c.id === review.client)?.name }}</td>
          <td>{{ services.find(s => s.id === review.service)?.name }}</td>
          <td>
            <div class="stars">
              <i v-for="star in 5" :key="star"
                 class="bi"
                 :class="star <= review.rating ? 'bi-star-fill text-warning' : 'bi-star'">
              </i>
            </div>
          </td>
          <td>{{ review.comment }}</td>
          <td>{{ new Date(review.date).toLocaleString() }}</td>
          <td>
            <button class="btn btn-warning btn-sm me-2" @click="editReview(review)">
              Редактировать
            </button>
            <button class="btn btn-danger btn-sm" @click="deleteReview(review.id)">
              Удалить
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Информация о количестве -->
    <div class="mt-3">
      <p class="text-muted">
        Найдено отзывов: {{ filteredReviews.length }}
        <span v-if="filteredReviews.length !== reviews.length">
          (всего: {{ reviews.length }})
        </span>
      </p>
    </div>

    <!-- Модальное окно редактирования -->
    <div class="modal fade" id="editModal" ref="editModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать отзыв</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Услуга</label>
              <select class="form-select" v-model="editingReview.service">
                <option v-for="service in services" :key="service.id" :value="service.id">
                  {{ service.name }}
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Оценка</label>
              <select class="form-select" v-model="editingReview.rating">
                <option value="5">★★★★★</option>
                <option value="4">★★★★☆</option>
                <option value="3">★★★☆☆</option>
                <option value="2">★★☆☆☆</option>
                <option value="1">★☆☆☆☆</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Отзыв</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="editingReview.comment"
              >
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button type="button" class="btn btn-primary" @click="saveEdit">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
}

.card {
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
  margin-bottom: 1rem;
}

.form-control:focus,
.form-select:focus {
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}

.stars {
  white-space: nowrap;
}

.table th {
  background-color: #f8f9fa;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
}

.bi-star-fill,
.bi-star {
  font-size: 1rem;
  margin-right: 2px;
}

.statistics-panel {
  animation: slideDown 0.3s ease-out;
}

.stat-card {
  text-align: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-card h3 {
  font-size: 2rem;
  margin: 0;
  color: #0d6efd;
}

.chart-container {
  margin-top: 2rem;
  height: 300px;
}

.service-rating-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
}

.service-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rating-bar {
  flex: 2;
  height: 20px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
}

.rating-fill {
  height: 100%;
  transition: width 1s ease-out;
}

.rating-value {
  min-width: 50px;
  text-align: right;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 