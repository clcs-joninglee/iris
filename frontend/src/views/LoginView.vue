<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded shadow w-80">
      <h1 class="text-2xl font-bold mb-6 text-center">Iris Login</h1>
      <input
        v-model="username"
        placeholder="Username"
        class="w-full border p-2 rounded mb-3"
      />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        class="w-full border p-2 rounded mb-4"
      />
      <button
        @click="handleLogin"
        class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
      >
        Login
      </button>
      <p v-if="error" class="text-red-500 mt-3 text-sm text-center">{{ error }}</p>
      <p class="text-center mt-3 text-sm">
        沒有帳號？<a href="/register" class="text-blue-500 hover:underline">註冊</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../stores/auth'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

async function handleLogin() {
  try {
    await login(username.value, password.value)
    router.push('/iris')
  } catch {
    error.value = '帳號或密碼錯誤'
  }
}
</script>