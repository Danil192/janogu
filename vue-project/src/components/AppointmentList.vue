<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useUserStore } from '@/stores/user';
import { Modal } from 'bootstrap';

const userStore = useUserStore();
const appointments = ref([]);
const clients = ref([]);
const services = ref([]);
const masters = ref([]);
const loading = ref(false);
const editModal = ref(null);
const editingAppointment = ref({});

// Добавляем фильтры
const filters = ref({
  client: '',
  service: '',
  master: '',
  dateFrom: '',
  dateTo: '',
  status: 'all' // можно добавить фильтр по статусу (все, предстоящие, прошедшие)
});

// Вычисляемое свойство для фильтрации записей
const filteredAppointments = computed(() => {
  if (!appointments.value) return [];
  
  return appointments.value.filter(appointment => {
    // Фильтр по клиенту
    const clientMatch = !filters.value.client || 
      appointment.client === parseInt(filters.value.client);
    
    // Фильтр по услуге
    const serviceMatch = !filters.value.service || 
      appointment.service === parseInt(filters.value.service);
    
    // Фильтр по мастеру
    const masterMatch = !filters.value.master || 
      appointment.master === parseInt(filters.value.master);
    
    // Фильтр по дате
    const appointmentDate = new Date(appointment.date);
    const dateFromMatch = !filters.value.dateFrom || 
      appointmentDate >= new Date(filters.value.dateFrom);
    const dateToMatch = !filters.value.dateTo || 
      appointmentDate <= new Date(filters.value.dateTo);
    
    // Фильтр по статусу
    const now = new Date();
    const isPast = appointmentDate < now;
    const statusMatch = filters.value.status === 'all' || 
      (filters.value.status === 'upcoming' && !isPast) ||
      (filters.value.status === 'past' && isPast);
    
    return clientMatch && serviceMatch && masterMatch && 
           dateFromMatch && dateToMatch && statusMatch;
  });
});

const appointmentToAdd = ref({
  service: null,
  master: null,
  date: '',
  time: ''
});

async function addAppointment() {
  try {
    // Объединяем дату и время
    const dateTime = new Date(appointmentToAdd.value.date + 'T' + appointmentToAdd.value.time);
    
    const formData = {
      service: appointmentToAdd.value.service,
      master: appointmentToAdd.value.master,
      date: dateTime.toISOString()
    };

    await axios.post('/api/appointments/', formData, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`,
        'Content-Type': 'application/json'
      }
    });

    await fetchData();
    appointmentToAdd.value = { service: null, master: null, date: '', time: '' };
  } catch (error) {
    console.error('Ошибка добавления:', error.response?.data || error);
    let errorMessage = 'Ошибка при добавлении записи';
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
    const [appointmentsRes, servicesRes, mastersRes] = await Promise.all([
      axios.get('/api/appointments/', {
        headers: {
          'Authorization': `Token ${userStore.getToken}`
        }
      }),
      axios.get('/api/services/', {
        headers: {
          'Authorization': `Token ${userStore.getToken}`
        }
      }),
      axios.get('/api/masters/', {
        headers: {
          'Authorization': `Token ${userStore.getToken}`
        }
      })
    ]);
    appointments.value = appointmentsRes.data;
    services.value = servicesRes.data;
    masters.value = mastersRes.data;
  } catch (error) {
    console.error('Ошибка загрузки данных:', error);
  }
  loading.value = false;
}

onMounted(() => {
  fetchData();
  editModal.value = new Modal(document.getElementById('editModal'));
});

function editAppointment(appointment) {
  editingAppointment.value = { 
    ...appointment,
    date: new Date(appointment.date).toISOString().split('T')[0],
    time: new Date(appointment.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };
  editModal.value.show();
}

async function saveEdit() {
  try {
    const dateTime = new Date(editingAppointment.value.date + 'T' + editingAppointment.value.time);
    
    const formData = {
      service: editingAppointment.value.service,
      master: editingAppointment.value.master,
      date: dateTime.toISOString()
    };

    await axios.put(`/api/appointments/${editingAppointment.value.id}/`, formData, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`,
        'Content-Type': 'application/json'
      }
    });

    await fetchData();
    editModal.value.hide();
  } catch (error) {
    console.error('Ошибка при редактировании:', error.response?.data || error);
    alert('Ошибка при редактировании записи');
  }
}

async function deleteAppointment(id) {
  if (!confirm('Вы уверены, что хотите удалить эту запись?')) {
    return;
  }

  try {
    await axios.delete(`/api/appointments/${id}/`, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`
      }
    });
    await fetchData();
  } catch (error) {
    console.error('Ошибка при удалении:', error.response?.data || error);
    alert('Ошибка при удалении записи');
  }
}
</script>

<template>
  <div class="container mt-4">
    <h2>Записи</h2>

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

          <!-- Фильтр по мастеру -->
          <div class="col-md-4">
            <select 
              v-model="filters.master"
              class="form-select"
            >
              <option value="">Все мастера</option>
              <option v-for="master in masters" :key="master.id" :value="master.id">
                {{ master.name }}
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

          <!-- Фильтр по статусу -->
          <div class="col-md-3">
            <select 
              v-model="filters.status"
              class="form-select"
            >
              <option value="all">Все записи</option>
              <option value="upcoming">Предстоящие</option>
              <option value="past">Прошедшие</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Форма добавления -->
    <form @submit.prevent="addAppointment" class="mb-4">
      <div class="row g-3 align-items-center">
        <div class="col">
          <select v-model="appointmentToAdd.service" class="form-select" required>
            <option value="">Выберите услугу</option>
            <option v-for="service in services" :key="service.id" :value="service.id">
              {{ service.name }}
            </option>
          </select>
        </div>
        <div class="col">
          <select v-model="appointmentToAdd.master" class="form-select" required>
            <option value="">Выберите мастера</option>
            <option v-for="master in masters" :key="master.id" :value="master.id">
              {{ master.name }}
            </option>
          </select>
        </div>
        <div class="col">
          <input 
            type="date" 
            v-model="appointmentToAdd.date" 
            class="form-control"
            :min="new Date().toISOString().split('T')[0]"
            required
          >
        </div>
        <div class="col">
          <input 
            type="time" 
            v-model="appointmentToAdd.time" 
            class="form-control"
            required
          >
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">
            <i class="bi bi-plus-lg"></i> Записаться
          </button>
        </div>
      </div>
    </form>

    <!-- Список записей -->
    <div v-if="loading">Загрузка...</div>
    <table v-else class="table">
      <thead>
        <tr>
          <th>Клиент</th>
          <th>Услуга</th>
          <th>Мастер</th>
          <th>Дата и время</th>
          <th>Статус</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="appointment in filteredAppointments" :key="appointment.id">
          <td>{{ clients.find(c => c.id === appointment.client)?.name }}</td>
          <td>{{ services.find(s => s.id === appointment.service)?.name }}</td>
          <td>{{ masters.find(m => m.id === appointment.master)?.name }}</td>
          <td>{{ new Date(appointment.date).toLocaleString() }}</td>
          <td>
            <span 
              :class="[
                'badge',
                new Date(appointment.date) > new Date() ? 'bg-success' : 'bg-secondary'
              ]"
            >
              {{ new Date(appointment.date) > new Date() ? 'Предстоит' : 'Прошла' }}
            </span>
          </td>
          <td>
            <button class="btn btn-warning btn-sm me-2" @click="editAppointment(appointment)">
              Редактировать
            </button>
            <button class="btn btn-danger btn-sm" @click="deleteAppointment(appointment.id)">
              Удалить
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Информация о количестве -->
    <div class="mt-3">
      <p class="text-muted">
        Найдено записей: {{ filteredAppointments.length }}
        <span v-if="filteredAppointments.length !== appointments.length">
          (всего: {{ appointments.length }})
        </span>
      </p>
    </div>

    <!-- Модальное окно редактирования -->
    <div class="modal fade" id="editModal" ref="editModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать запись</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Услуга</label>
              <select class="form-select" v-model="editingAppointment.service">
                <option v-for="service in services" :key="service.id" :value="service.id">
                  {{ service.name }}
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Мастер</label>
              <select class="form-select" v-model="editingAppointment.master">
                <option v-for="master in masters" :key="master.id" :value="master.id">
                  {{ master.name }}
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Дата</label>
              <input 
                type="date" 
                class="form-control" 
                v-model="editingAppointment.date"
                :min="new Date().toISOString().split('T')[0]"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">Время</label>
              <input 
                type="time" 
                class="form-control" 
                v-model="editingAppointment.time"
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

.badge {
  font-size: 0.9em;
}

.table th {
  background-color: #f8f9fa;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
}
</style> 