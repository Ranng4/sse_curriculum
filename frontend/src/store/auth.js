import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const userId = ref(localStorage.getItem('user_id') || null)

  const isLoggedIn = computed(() => !!token.value)

  function setSession(accessToken, id) {
    token.value = accessToken
    userId.value = id
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('user_id', id)
  }

  function clearSession() {
    token.value = null
    userId.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_id')
  }

  async function register(payload) {
    const data = await api.post('/auth/register', payload)
    setSession(data.token.access_token, data.user_id)
    return data
  }

  async function login(payload) {
    const data = await api.post('/auth/login', payload)
    setSession(data.access_token, data.user_id)
    return data
  }

  function logout() {
    clearSession()
  }

  return { token, userId, isLoggedIn, setSession, clearSession, register, login, logout }
})
