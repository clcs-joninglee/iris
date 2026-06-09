<template>
  <div class="p-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Iris Data</h1>
      <button @click="handleLogout" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
        Logout
      </button>
    </div>

    <div class="flex gap-2 mb-4">
      <button @click="currentPage = 'all'; page = 1; fetchData()" :class="tabClass('all')">All</button>
      <button @click="currentPage = 'setosa'; page = 1; fetchData()" :class="tabClass('setosa')">Setosa</button>
      <button @click="currentPage = 'versicolor'; page = 1; fetchData()" :class="tabClass('versicolor')">Versicolor</button>
      <button @click="currentPage = 'virginica'; page = 1; fetchData()" :class="tabClass('virginica')">Virginica</button>
      <button @click="$router.push('/chart')" class="ml-auto bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        Chart
      </button>
    </div>

    <table class="w-full border-collapse border border-gray-300">
      <thead class="bg-gray-100">
        <tr>
          <th class="border p-2">ID</th>
          <th class="border p-2">Sepal Length</th>
          <th class="border p-2">Sepal Width</th>
          <th class="border p-2">Petal Length</th>
          <th class="border p-2">Petal Width</th>
          <th class="border p-2">Species</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in data" :key="item.Id">
            <td class="border p-2 text-center">{{ item.Id }}</td>
            <td class="border p-2 text-center">{{ item.SepalLengthCm }}</td>
            <td class="border p-2 text-center">{{ item.SepalWidthCm }}</td>
            <td class="border p-2 text-center">{{ item.PetalLengthCm }}</td>
            <td class="border p-2 text-center">{{ item.PetalWidthCm }}</td>
            <td class="border p-2 text-center">{{ item.Species }}</td>
        </tr>
      </tbody>
    </table>
        <div class="flex items-center gap-4 mt-4">
            <button @click="prevPage" :disabled="page === 1" class="bg-gray-200 px-4 py-2 rounded hover:bg-gray-300 disabled:opacity-50">
                上一頁
            </button>
            <span>第 {{ page }} 頁 / 共 {{ totalPages }} 頁</span>
            <button @click="nextPage" :disabled="page === totalPages" class="bg-gray-200 px-4 py-2 rounded hover:bg-gray-300 disabled:opacity-50">
                下一頁
            </button>
        </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { logout } from '../stores/auth'
import api from '../api/axios'

const router = useRouter()
const data = ref([])
const currentPage = ref('all')
const page = ref(1)
const pageSize = 10
const total = ref(0)

async function fetchData() {
  const offset = (page.value - 1) * pageSize
  if (currentPage.value === 'all') {
    const res = await api.get(`/iris/?limit=${pageSize}&offset=${offset}`)
    data.value = res.data.data
    total.value = res.data.total
  } else {
    const res = await api.get(`/iris/search?species=${currentPage.value}&limit=${pageSize}&offset=${offset}`)
    data.value = res.data.data
    total.value = res.data.total
  }
}
onMounted(fetchData)

const totalPages = computed(() => Math.ceil(total.value / pageSize))

function prevPage() {
  if (page.value > 1) { page.value--; fetchData() }
}

function nextPage() {
  if (page.value < totalPages.value) { page.value++; fetchData() }
}

function tabClass(tab) {
  return currentPage.value === tab
    ? 'bg-blue-500 text-white px-4 py-2 rounded'
    : 'bg-gray-200 px-4 py-2 rounded hover:bg-gray-300'
}

async function handleLogout() {
  try {
    await logout()
  } finally {
    router.push('/login')
  }
}
</script>