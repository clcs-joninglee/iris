<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded shadow w-80">
      <h1 class="text-2xl font-bold mb-6 text-center">Register</h1>
      <input v-model="username" placeholder="Username" class="w-full border p-2 rounded mb-3" />
      <input v-model="email" placeholder="Email" class="w-full border p-2 rounded mb-3" />
      <input v-model="password" type="password" placeholder="Password" class="w-full border p-2 rounded mb-4" />
      <button @click="handleRegister" class="w-full bg-green-500 text-white p-2 rounded hover:bg-green-600">
        Register
      </button>
      <p class="text-center mt-3 text-sm">
        已有帳號？<a href="/login" class="text-blue-500 hover:underline">登入</a>
      </p>
      <p v-if="error" class="text-red-500 mt-3 text-sm text-center">{{ error }}</p>
      <p v-if="success" class="text-green-500 mt-3 text-sm text-center">註冊成功，請登入</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/axios'

const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const success = ref(false)

async function handleRegister() {
  try {
    await api.post('/auth/register', {
      username: username.value,
      email: email.value,
      password: password.value,
    })
    success.value = true
    error.value = ''
  } catch (e) {
    error.value = e.response?.data?.detail || '註冊失敗'
  }
}
</script>