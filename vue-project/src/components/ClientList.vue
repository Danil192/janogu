<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useUserStore } from '@/stores/user';
import { Modal } from 'bootstrap';

const userStore = useUserStore();
const clients = ref([]);
const services = ref([]);
const loading = ref(false);
const clientPictureRef = ref();
const editPictureRef = ref();
const editModal = ref(null);
const editingClient = ref({});

const clientToAdd = ref({
  name: '',
  phone: '',
  email: '',
  service: null,
  picture: null
});

const filters = ref({
  name: '',
  phone: '',
  email: '',
  service: ''
});

async function addClient() {
  try {
    const formData = new FormData();
    
    formData.append('name', clientToAdd.value.name);
    formData.append('phone', clientToAdd.value.phone);
    formData.append('email', clientToAdd.value.email);
    formData.append('service', clientToAdd.value.service);

    if (clientPictureRef.value?.files[0]) {
      formData.append('picture', clientPictureRef.value.files[0]);
    }

    await axios.post('/api/clients/', formData, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`,
        'Content-Type': 'multipart/form-data'
      }
    });

    await fetchData();
    clientToAdd.value = { name: '', phone: '', email: '', service: null, picture: null };
    if (clientPictureRef.value) {
      clientPictureRef.value.value = '';
    }
  } catch (error) {
    console.error('Ошибка добавления:', error.response?.data || error);
    alert('Ошибка при добавлении клиента');
  }
}

async function fetchData() {
  loading.value = true;
  try {
    console.log('Fetching data with token:', userStore.getToken);
    const [clientsRes, servicesRes] = await Promise.all([
      axios.get('/api/clients/', {
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
    console.log('Received clients:', clientsRes.data);
    console.log('Received services:', servicesRes.data);
    clients.value = clientsRes.data;
    services.value = servicesRes.data;
  } catch (error) {
    console.error('Ошибка загрузки данных:', error.response?.data || error);
  }
  loading.value = false;
}

onMounted(async () => {
  console.log('Component mounted, userStore:', userStore);
  if (userStore.isLoggedIn) {
    await fetchData();
  }
  const modalElement = document.getElementById('editModal');
  if (modalElement) {
    editModal.value = new Modal(modalElement);
  }
});

function editClient(client) {
  editingClient.value = { ...client };
  if (editModal.value) {
    editModal.value.show();
  }
}

async function saveEdit() {
  try {
    const formData = new FormData();
    formData.append('name', editingClient.value.name);
    formData.append('phone', editingClient.value.phone);
    formData.append('email', editingClient.value.email);
    formData.append('service', editingClient.value.service);

    if (editPictureRef.value?.files[0]) {
      formData.append('picture', editPictureRef.value.files[0]);
    }

    await axios.put(`/api/clients/${editingClient.value.id}/`, formData, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`,
        'Content-Type': 'multipart/form-data'
      }
    });

    await fetchData();
    if (editModal.value) {
      editModal.value.hide();
    }
  } catch (error) {
    console.error('Ошибка при редактировании:', error.response?.data || error);
    alert('Ошибка при редактировании клиента');
  }
}

async function deleteClient(id) {
  if (!confirm('Вы уверены, что хотите удалить этого клиента?')) {
    return;
  }

  try {
    await axios.delete(`/api/clients/${id}/`, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`
      }
    });
    await fetchData();
  } catch (error) {
    console.error('Ошибка при удалении:', error.response?.data || error);
    alert('Ошибка при удалении клиента');
  }
}

const filteredClients = computed(() => {
  if (!clients.value) return [];
  
  return clients.value.filter(client => {
    const nameMatch = client.name.toLowerCase().includes(filters.value.name.toLowerCase());
    const phoneMatch = client.phone.includes(filters.value.phone);
    const emailMatch = client.email.toLowerCase().includes(filters.value.email.toLowerCase());
    const serviceMatch = !filters.value.service || client.service === parseInt(filters.value.service);
    
    return nameMatch && phoneMatch && emailMatch && serviceMatch;
  });
});
</script>

<template>
  <div class="container">
    <div v-if="!userStore.isLoggedIn">
      <p class="alert alert-warning">Необходима авторизация</p>
    </div>
    <div v-else>
      <h2>Клиенты</h2>

      <!-- Добавляем панель фильтров -->
      <div class="card mb-4">
        <div class="card-body">
          <h5 class="card-title">Фильтры</h5>
          <div class="row g-3">
            <div class="col-md-3">
              <input 
                v-model="filters.name"
                type="text"
                class="form-control"
                placeholder="Поиск по ФИО"
              >
            </div>
            <div class="col-md-3">
              <input 
                v-model="filters.phone"
                type="text"
                class="form-control"
                placeholder="Поиск по телефону"
              >
            </div>
            <div class="col-md-3">
              <input 
                v-model="filters.email"
                type="text"
                class="form-control"
                placeholder="Поиск по email"
              >
            </div>
            <div class="col-md-3">
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
          </div>
        </div>
      </div>

      <!-- Форма добавления -->
      <form @submit.prevent="addClient" class="mb-4">
        <div class="row g-3">
          <div class="col">
            <input v-model="clientToAdd.name" placeholder="ФИО" class="form-control" required>
          </div>
          <div class="col">
            <input v-model="clientToAdd.phone" placeholder="Телефон" class="form-control" required>
          </div>
          <div class="col">
            <input v-model="clientToAdd.email" type="email" placeholder="Email" class="form-control" required>
          </div>
          <div class="col">
            <select v-model="clientToAdd.service" class="form-select" required>
              <option value="">Выберите услугу</option>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }}
              </option>
            </select>
          </div>
          <div class="col">
            <input type="file" ref="clientPictureRef" class="form-control" accept="image/*">
          </div>
          <div class="col-auto">
            <button type="submit" class="btn btn-primary">Добавить</button>
          </div>
        </div>
      </form>

      <!-- Список клиентов -->
      <div v-if="loading">Загрузка...</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Фото</th>
            <th>ФИО</th>
            <th>Телефон</th>
            <th>Email</th>
            <th>Услуга</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="client in filteredClients" :key="client.id">
            <td>
              <img 
                v-if="client.picture" 
                :src="client.picture" 
                alt="Фото клиента"
                style="height: 50px; width: 50px; object-fit: cover;"
              >
            </td>
            <td>{{ client.name }}</td>
            <td>{{ client.phone }}</td>
            <td>{{ client.email }}</td>
            <td>{{ services.find(s => s.id === client.service)?.name }}</td>
            <td>
              <button class="btn btn-warning btn-sm me-2" @click="editClient(client)">
                Редактировать
              </button>
              <button class="btn btn-danger btn-sm" @click="deleteClient(client.id)">
                Удалить
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Информация о количестве -->
      <div class="mt-3">
        <p class="text-muted">
          Найдено клиентов: {{ filteredClients.length }}
          <span v-if="filteredClients.length !== clients.length">
            (всего: {{ clients.length }})
          </span>
        </p>
      </div>

      <!-- Модальное окно редактирования -->
      <div class="modal fade" id="editModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Редактировать клиента</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">ФИО</label>
                <input type="text" class="form-control" v-model="editingClient.name">
              </div>
              <div class="mb-3">
                <label class="form-label">Телефон</label>
                <input type="text" class="form-control" v-model="editingClient.phone">
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" v-model="editingClient.email">
              </div>
              <div class="mb-3">
                <label class="form-label">Услуга</label>
                <select class="form-select" v-model="editingClient.service">
                  <option v-for="service in services" :key="service.id" :value="service.id">
                    {{ service.name }}
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Фото</label>
                <input type="file" class="form-control" ref="editPictureRef" accept="image/*">
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
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
}
.form-floating {
  margin: 0 5px;
}
.hover-zoom {
  transition: transform 0.2s;
}
.hover-zoom:hover {
  transform: scale(1.1);
  box-shadow: 0 0 10px rgba(0,0,0,0.2);
}

.card {
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

.card-title {
  margin-bottom: 1rem;
}

.form-control:focus,
.form-select:focus {
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}
</style>