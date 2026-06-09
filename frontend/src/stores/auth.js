//負責登入狀態管理

import { ref } from 'vue'
import api from '../api/axios'

const user = ref(null)
const accessToken = ref(localStorage.getItem('access_token'))

async function login(username, password) {
  const res = await api.post('/auth/login', { username, password })
  accessToken.value = res.data.access_token
  localStorage.setItem('access_token', res.data.access_token)
  localStorage.setItem('refresh_token', res.data.refresh_token)
}

async function logout() {
  try {
    await api.post('/auth/logout')
  } finally {
    accessToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }
}

function isLoggedIn() {
  return !!accessToken.value
}

export { user, accessToken, login, logout, isLoggedIn }