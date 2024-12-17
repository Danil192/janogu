<template>
  <div class="container mt-4">
    <h2>Мастера</h2>

    <!-- Добавляем панель фильтров -->
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Фильтры</h5>
        <div class="row g-3">
          <div class="col-md-4">
            <input 
              v-model="filters.name"
              type="text"
              class="form-control"
              placeholder="Поиск по ФИО"
            >
          </div>
          <div class="col-md-4">
            <input 
              v-model="filters.specialization"
              type="text"
              class="form-control"
              placeholder="Поиск по специализации"
            >
          </div>
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
        </div>
      </div>
    </div>

    <!-- Форма добавления -->
    <form @submit.prevent="addMaster" class="mb-4">
      <div class="row g-3 align-items-center">
        <div class="col">
          <input 
            type="text" 
            v-model="masterToAdd.name" 
            class="form-control"
            placeholder="ФИО мастера"
            required
          >
        </div>
        <div class="col">
          <input 
            type="text" 
            v-model="masterToAdd.specialization" 
            class="form-control"
            placeholder="Специализация"
            required
          >
        </div>
        <div class="col">
          <select 
            v-model="masterToAdd.services" 
            class="form-select" 
            multiple 
            required
          >
            <option v-for="service in services" :key="service.id" :value="service.id">
              {{ service.name }}
            </option>
          </select>
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">
            <i class="bi bi-plus-lg"></i> Добавить мастера
          </button>
        </div>
      </div>
    </form>

    <!-- Список мастеров -->
    <div v-if="loading">Загрузка...</div>
    <table v-else class="table">
      <thead>
        <tr>
          <th>ФИО</th>
          <th>Специализация</th>
          <th>Услуги</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="master in filteredMasters" :key="master.id">
          <td>{{ master.name }}</td>
          <td>{{ master.specialization }}</td>
          <td>
            <span v-for="serviceId in master.services" :key="serviceId" class="badge bg-primary me-1">
              {{ services.find(s => s.id === serviceId)?.name }}
            </span>
          </td>
          <td>
            <button class="btn btn-warning btn-sm me-2" @click="editMaster(master)">
              Редактировать
            </button>
            <button class="btn btn-danger btn-sm" @click="deleteMaster(master.id)">
              Удалить
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Информация о количестве -->
    <div class="mt-3">
      <p class="text-muted">
        Найдено мастеров: {{ filteredMasters.length }}
        <span v-if="filteredMasters.length !== masters.length">
          (всего: {{ masters.length }})
        </span>
      </p>
    </div>

    <!-- Модальное окно редактирования -->
    <div class="modal fade" id="editModal" ref="editModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать мастера</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">ФИО</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="editingMaster.name"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">Специализация</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="editingMaster.specialization"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">Услуги</label>
              <select 
                class="form-select" 
                v-model="editingMaster.services" 
                multiple
              >
                <option v-for="service in services" :key="service.id" :value="service.id">
                  {{ service.name }}
                </option>
              </select>
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

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useUserStore } from '@/stores/user';
import { Modal } from 'bootstrap';

const userStore = useUserStore();
const masters = ref([]);
const services = ref([]);
const loading = ref(false);
const editModal = ref(null);
const editingMaster = ref({});

// Добавляем фильтры
const filters = ref({
  name: '',
  specialization: '',
  service: ''
});

// Вычисляемое свойство для фильтрации мастеров
const filteredMasters = computed(() => {
  if (!masters.value) return [];
  
  return masters.value.filter(master => {
    const nameMatch = master.name.toLowerCase().includes(filters.value.name.toLowerCase());
    const specializationMatch = master.specialization.toLowerCase().includes(filters.value.specialization.toLowerCase());
    const serviceMatch = !filters.value.service || master.services.includes(parseInt(filters.value.service));
    
    return nameMatch && specializationMatch && serviceMatch;
  });
});

const masterToAdd = ref({
  name: '',
  specialization: '',
  services: []
});

async function fetchData() {
  loading.value = true;
  try {
    const [mastersRes, servicesRes] = await Promise.all([
      axios.get('/api/masters/', {
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
    masters.value = mastersRes.data;
    services.value = servicesRes.data;
  } catch (error) {
    console.error('Ошибка загрузки данных:', error);
  }
  loading.value = false;
}

async function addMaster() {
  try {
    const formData = {
      name: masterToAdd.value.name,
      specialization: masterToAdd.value.specialization,
      services: masterToAdd.value.services
    };

    await axios.post('/api/masters/', formData, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`,
        'Content-Type': 'application/json'
      }
    });

    await fetchData();
    masterToAdd.value = { name: '', specialization: '', services: [] };
  } catch (error) {
    console.error('Ошибка добавления:', error.response?.data || error);
    alert('Ошибка при добавлении мастера');
  }
}

function editMaster(master) {
  editingMaster.value = { ...master };
  editModal.value.show();
}

async function saveEdit() {
  try {
    await axios.put(`/api/masters/${editingMaster.value.id}/`, editingMaster.value, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`,
        'Content-Type': 'application/json'
      }
    });

    await fetchData();
    editModal.value.hide();
  } catch (error) {
    console.error('Ошибка при редактировании:', error.response?.data || error);
    alert('Ошибка при редактировании мастера');
  }
}

async function deleteMaster(id) {
  if (!confirm('Вы уверены, что хотите удалить этого мастера?')) {
    return;
  }

  try {
    await axios.delete(`/api/masters/${id}/`, {
      headers: {
        'Authorization': `Token ${userStore.getToken}`
      }
    });
    await fetchData();
  } catch (error) {
    console.error('Ошибка при удалении:', error.response?.data || error);
    alert('Ошибка при удалении мастера');
  }
}

onMounted(() => {
  fetchData();
  editModal.value = new Modal(document.getElementById('editModal'));
});
</script>

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

.btn-group {
  display: flex;
  gap: 5px;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
}
</style>


