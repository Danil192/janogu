<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';
import { Modal } from 'bootstrap';
import { useUserStore } from '@/stores/user'

// Установите базовый URL
axios.defaults.baseURL = 'http://localhost:8000';

const services = ref([]);
const loading = ref(false);
const servicesPictureRef = ref();
const serviceEditPictureRef = ref();
const selectedImage = ref(null);
const stats = ref(null);
const showOTPModal = ref(false);
const otpCode = ref('');
const otpVerified = ref(false);
const pendingDeleteId = ref(null);

const serviceToAdd = ref({
  name: '',
  price: 0,
  duration: 0
});

const serviceToEdit = ref({
  name: '',
  price: 0,
  duration: 0
});

// Добавляем фильтры
const filters = ref({
  name: '',
  price: '',
  duration: ''
});

const userStore = useUserStore()

async function fetchData() {
  loading.value = true;
  try {
    const response = await axios.get('/api/services/', {
      headers: {
        'Authorization': `Token ${userStore.getToken}`
      }
    });
    services.value = response.data;
  } catch (error) {
    console.error('Ошибка загрузки данных:', error);
  }
  loading.value = false;
}

async function addService() {
  try {
    const formData = new FormData();

    if (servicesPictureRef.value.files[0]) {
      formData.append('picture', servicesPictureRef.value.files[0]);
    }

    formData.set('name', serviceToAdd.value.name);
    formData.set('price', serviceToAdd.value.price);
    formData.set('duration', serviceToAdd.value.duration);

    const response = await axios.post("/api/services/", formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': Cookies.get('csrftoken')
      },
      withCredentials: true
    });
    
    await fetchData();
    serviceToAdd.value = { name: '', price: 0, duration: 0 };
    if (servicesPictureRef.value) {
      servicesPictureRef.value.value = '';
    }
  } catch (error) {
    console.error('Ошибка добавления:', error.response?.data || error);
  }
}

async function updateService() {
  if (!otpVerified.value) {
    showOTPModal.value = true;
    return;
  }
  
  try {
    const formData = new FormData();

    if (serviceEditPictureRef.value.files[0]) {
      formData.append('picture', serviceEditPictureRef.value.files[0]);
    }

    formData.set('name', serviceToEdit.value.name);
    formData.set('price', serviceToEdit.value.price);
    formData.set('duration', serviceToEdit.value.duration);

    await axios.put(`/api/services/${serviceToEdit.value.id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': Cookies.get('csrftoken')
      },
      withCredentials: true
    });
    await fetchData();
    if (serviceEditPictureRef.value) {
      serviceEditPictureRef.value.value = '';
    }
  } catch (error) {
    console.error('Ошибка обновления:', error);
  }
}

async function deleteService(id) {
  try {
    await axios.delete(`/api/services/${id}/`, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`
      }
    });
    await fetchData();
  } catch (error) {
    console.error('Ошибка удаления:', error);
    alert('Ошибка при удалении услуги');
  }
}

function showImage(imageUrl) {
  selectedImage.value = imageUrl;
  const imageModal = new Modal(document.getElementById('imageModal'));
  imageModal.show();
}

async function fetchStats() {
  try {
    const response = await axios.get('/api/services/stats/');
    stats.value = response.data;
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error);
  }
}

async function checkOTPStatus() {
  if (!userStore.isLoggedIn) {
    return;
  }
  
  try {
    const response = await axios.get('/api/services/otp-status/', {
      headers: {
        'Authorization': `Token ${userStore.getToken}`
      }
    });
    userStore.setOTPVerified(response.data.otp_verified);
  } catch (error) {
    console.error('Ошибка проверки OTP:', error);
  }
}

async function verifyOTP() {
  try {
    const response = await axios.post('/api/services/verify-otp/', {
      code: otpCode.value
    });
    if (response.data.success) {
      userStore.setOTPVerified(true);
      showOTPModal.value = false;
      
      // Если было ожидающее удаление, выполняем его
      if (pendingDeleteId.value) {
        await deleteService(pendingDeleteId.value);
        pendingDeleteId.value = null;
      } else {
        await updateService();
      }
    } else {
      alert('Неверный код');
    }
  } catch (error) {
    console.error('Ошибка верификации OTP:', error);
    alert('Ошибка при проверке кода');
  }
}

// Упрощаем функцию handleDelete
async function handleDelete(id) {
  try {
    await deleteService(id);
  } catch (err) {
    console.error('Ошибка при удалении:', err);
    alert('Не удалось удалить услугу');
  }
}

async function handleEdit() {
  if (!otpVerified.value) {
    showOTPModal.value = true;
    return;
  }
  await updateService();
}

// Функция фильтрации
function filteredServices() {
  return services.value.filter(service => {
    return (!filters.value.name || service.name.toLowerCase().includes(filters.value.name.toLowerCase())) &&
           (!filters.value.price || service.price.toString().includes(filters.value.price)) &&
           (!filters.value.duration || service.duration.toString().includes(filters.value.duration));
  });
}

async function exportToExcel() {
  try {
    const response = await axios.get('/api/services/export-excel/', {
      headers: {
        'Authorization': `Token ${userStore.getToken}`
      },
      responseType: 'blob'
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `services_${new Date().toISOString().split('T')[0]}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (err) {
    console.error('Ошибка при экспорте:', err);
    alert('Ошибка при экспорте данных');
  }
}

onMounted(() => {
  if (userStore.isLoggedIn) {
    axios.defaults.headers.common['Authorization'] = `Token ${userStore.getToken}`;
    fetchData();
    fetchStats();
    checkOTPStatus();
  }
});

watch(() => userStore.isLoggedIn, (newValue) => {
  if (newValue) {
    axios.defaults.headers.common['Authorization'] = `Token ${userStore.getToken}`;
    fetchData();
    fetchStats();
    checkOTPStatus();
  }
});
</script>

<template>
  <div v-if="userStore.isLoggedIn">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Услуги</h2>
        <button 
          @click="exportToExcel" 
          class="btn btn-success"
        >
          <i class="bi bi-file-earmark-excel me-2"></i>
          Экспорт в Excel
        </button>
      </div>
      
      <!-- Блок статистики -->
      <div v-if="stats" class="card mb-4">
        <div class="card-body">
          <h5 class="card-title">Статистика</h5>
          <div class="row">
            <div class="col">
              <p>Всего услуг: {{ stats.total_services }}</p>
              <p>Средняя цена: {{ stats.avg_price?.toFixed(0) }} ₽</p>
            </div>
            <div class="col">
              <p>Максимальная цена: {{ stats.max_price }} ₽</p>
              <p>Минимальная цена: {{ stats.min_price }} ₽</p>
            </div>
            <div class="col">
              <p>Средняя длительность: {{ stats.avg_duration?.toFixed(0) }} мин</p>
              <p>Общая выручка: {{ stats.total_revenue }} ₽</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Форма добавления -->
      <form @submit.prevent="addService" class="mb-4">
        <div class="row">
          <div class="col">
            <input v-model="serviceToAdd.name" placeholder="Название услуги" required class="form-control">
          </div>
          <div class="col">
            <input v-model.number="serviceToAdd.price" type="number" placeholder="Цена" required class="form-control">
          </div>
          <div class="col">
            <input v-model.number="serviceToAdd.duration" type="number" placeholder="Длительность (мин)" required class="form-control">
          </div>
          <div class="col-auto">
              <input class="form-control" type="file" ref="servicesPictureRef" />
          </div>
          <div class="col-auto">
            <button type="submit" class="btn btn-primary">Добавить</button>
          </div>
        </div>
      </form>

      <!-- Добавляем фильтры перед таблицей -->
      <div class="row mb-3">
        <div class="col">
          <div class="input-group">
            <span class="input-group-text">
              <i class="bi bi-search"></i>
            </span>
            <input 
              v-model="filters.name" 
              class="form-control" 
              placeholder="Поиск по названию..."
            >
          </div>
        </div>
        <div class="col">
          <div class="input-group">
            <span class="input-group-text">₽</span>
            <input 
              v-model="filters.price" 
              class="form-control" 
              placeholder="Поиск по цене..."
              type="number"
            >
          </div>
        </div>
        <div class="col">
          <div class="input-group">
            <span class="input-group-text">
              <i class="bi bi-clock"></i>
            </span>
            <input 
              v-model="filters.duration" 
              class="form-control" 
              placeholder="Поиск по длительности..."
              type="number"
            >
          </div>
        </div>
        <div class="col-auto">
          <button 
            class="btn btn-outline-secondary" 
            @click="filters = {name: '', price: '', duration: ''}"
          >
            Сбросить фильтры
          </button>
        </div>
      </div>

      <!-- Список услуг -->
      <div v-if="loading">Загрузка...</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Изображение</th>
            <th>Название</th>
            <th>Цена</th>
            <th>Длительность</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="service in filteredServices()" :key="service.id">
            <td>
              <img 
                v-if="service.picture" 
                :src="service.picture"
                alt="Изображение услуги"
                style="height: 50px; width: 50px; object-fit: cover; cursor: pointer;"
                @click="showImage(service.picture)"
                class="hover-zoom"
              >
            </td>
            <td>{{ service.name }}</td>
            <td>{{ service.price }} ₽</td>
            <td>{{ service.duration }} мин</td>
            <td>
              <button @click="serviceToEdit = {...service}" class="btn btn-sm btn-primary me-2" data-bs-toggle="modal" data-bs-target="#editModal">
                <i class="bi bi-pencil"></i>
              </button>
              <button @click="handleDelete(service.id)" class="btn btn-sm btn-danger">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Модальное окно редактирования -->
      <div class="modal fade" id="editModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Редактировать услугу</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3 text-center" v-if="serviceToEdit.picture">
                <img 
                  :src="serviceToEdit.picture"
                  alt="Текущее изображение"
                  style="height: 100px; width: 100px; object-fit: cover;"
                >
              </div>
              <div class="mb-3">
                <label class="form-label">Изображение</label>
                <input 
                  type="file" 
                  ref="serviceEditPictureRef" 
                  class="form-control"
                  accept="image/*"
                >
              </div>
              <div class="mb-3">
                <input v-model="serviceToEdit.name" placeholder="Название услуги" class="form-control">
              </div>
              <div class="mb-3">
                <input v-model.number="serviceToEdit.price" type="number" placeholder="Цена" class="form-control">
              </div>
              <div class="mb-3">
                <input v-model.number="serviceToEdit.duration" type="number" placeholder="Длительность (мин)" class="form-control">
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
              <button @click="handleEdit" class="btn btn-primary" data-bs-dismiss="modal">Сохранить</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Добавим модальное окно для просмотра изображения -->
      <div class="modal fade" id="imageModal" tabindex="-1">
        <div class="modal-dialog modal-lg modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body text-center p-0">
              <img 
                v-if="selectedImage" 
                :src="selectedImage" 
                alt="Увеличенное изображение"
                style="max-width: 100%; max-height: 80vh; object-fit: contain;"
              >
            </div>
          </div>
        </div>
      </div>

      <!-- Модальное окно OTP -->
      <div class="modal fade" id="otpModal" tabindex="-1" v-if="showOTPModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Подтверждение действия</h5>
              <button type="button" class="btn-close" @click="showOTPModal = false"></button>
            </div>
            <div class="modal-body">
              <p>Для редактирования требуется подтверждение.</p>
              <div class="mb-3">
                <label class="form-label">Введите код подтверждения (123456)</label>
                <input v-model="otpCode" type="text" class="form-control" placeholder="123456">
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showOTPModal = false">Отмена</button>
              <button type="button" class="btn btn-primary" @click="verifyOTP">Подтвердить</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else>
    Необходима авторизация
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
}

.hover-zoom {
  transition: transform 0.2s;
}

.hover-zoom:hover {
  transform: scale(1.1);
  box-shadow: 0 0 10px rgba(0,0,0,0.2);
}
</style>