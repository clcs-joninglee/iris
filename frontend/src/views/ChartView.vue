<template>
  <div class="p-8">
    <div class="flex items-center gap-4 mb-6">
      <button @click="$router.push('/iris')" class="bg-gray-200 px-4 py-2 rounded hover:bg-gray-300">
        ← Back
      </button>
      <h1 class="text-2xl font-bold">Iris Scatter Plot</h1>
    </div>

    <div class="max-w-2xl">
      <Scatter :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Scatter } from 'vue-chartjs'
import { Chart as ChartJS, LinearScale, PointElement, Tooltip, Legend } from 'chart.js'
import api from '../api/axios'

ChartJS.register(LinearScale, PointElement, Tooltip, Legend)

const data = ref([])

onMounted(async () => {
  const res = await api.get('/iris/?limit=200')
    data.value = res.data.data
})

const colors = {
  setosa: 'rgba(255, 99, 132, 0.7)',
  versicolor: 'rgba(54, 162, 235, 0.7)',
  virginica: 'rgba(75, 192, 192, 0.7)',
}

const chartData = computed(() => {
  const species = ['setosa', 'versicolor', 'virginica']
  return {
    datasets: species.map(s => ({
      label: s,
      data: data.value
        .filter(i => i.Species === s)
        .map(i => ({ x: i.SepalLengthCm, y: i.SepalWidthCm })),
      backgroundColor: colors[s],
    })),
  }
})

const chartOptions = {
  responsive: true,
  plugins: { legend: { position: 'top' } },
  scales: {
    x: { title: { display: true, text: 'Sepal Length' } },
    y: { title: { display: true, text: 'Sepal Width' } },
  },
}
</script>