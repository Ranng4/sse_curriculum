<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const searchQuery = ref('')
const mobileMenuOpen = ref(false)

function onSearch() {
  const q = searchQuery.value.trim()
  if (q) {
    router.push({ name: 'search', query: { q } })
  }
}

function onLogout() {
  auth.logout()
  router.push({ name: 'login' })
}

const navLinks = [
  { to: '/', label: '首页' },
  { to: '/feed', label: '动态' },
  { to: '/hot', label: '热榜' },
]
</script>

<template>
  <header class="bg-primary shadow-md sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 h-14 flex items-center gap-4">
      <!-- Logo -->
      <router-link to="/" class="text-white font-bold text-lg no-underline shrink-0">
        融智论坛
      </router-link>

      <!-- Desktop Nav -->
      <nav class="hidden md:flex items-center gap-1">
        <router-link
          v-for="link in navLinks" :key="link.to" :to="link.to"
          class="px-3 py-1.5 rounded-md text-sm text-blue-100 hover:text-white hover:bg-primary-dark transition-colors no-underline"
          :class="{ 'bg-primary-dark text-white': route.path === link.to }"
        >
          {{ link.label }}
        </router-link>
      </nav>

      <!-- Search -->
      <form @submit.prevent="onSearch" class="hidden sm:flex flex-1 max-w-md">
        <input
          v-model="searchQuery" type="text" placeholder="搜索帖子、股票代码..."
          class="w-full h-9 px-3 rounded-l-md border-0 bg-primary-dark text-white placeholder-blue-200 text-sm outline-none"
        />
        <button type="submit" class="h-9 px-3 rounded-r-md bg-accent text-white text-sm font-medium hover:bg-amber-600 transition-colors cursor-pointer">
          搜索
        </button>
      </form>

      <div class="flex-1 sm:hidden" />
      <div class="hidden sm:block w-px h-5 bg-primary-light/30" />

      <!-- Auth -->
      <div class="hidden md:flex items-center gap-2">
        <template v-if="auth.isLoggedIn">
          <router-link to="/admin" class="text-blue-100 hover:text-white text-sm no-underline transition-colors">
            管理
          </router-link>
          <router-link to="/profile/me" class="text-blue-100 hover:text-white text-sm no-underline transition-colors">
            个人中心
          </router-link>
          <button @click="onLogout" class="text-blue-100 hover:text-white text-sm bg-transparent border-0 cursor-pointer transition-colors">
            退出
          </button>
        </template>
        <template v-else>
          <router-link to="/auth/login" class="text-blue-100 hover:text-white text-sm no-underline transition-colors">登录</router-link>
          <router-link to="/auth/register" class="bg-white text-primary px-3 py-1 rounded-md text-sm font-medium no-underline hover:bg-blue-50 transition-colors">注册</router-link>
        </template>
      </div>

      <!-- Mobile Menu Toggle -->
      <button
        class="md:hidden text-white bg-transparent border-0 cursor-pointer p-1"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Mobile Menu -->
    <div v-if="mobileMenuOpen" class="md:hidden bg-primary-dark px-4 py-3 space-y-2">
      <form @submit.prevent="onSearch(); mobileMenuOpen = false" class="flex mb-3">
        <input v-model="searchQuery" type="text" placeholder="搜索帖子、股票代码..."
          class="flex-1 h-9 px-3 rounded-l-md border-0 bg-primary text-white placeholder-blue-200 text-sm outline-none" />
        <button type="submit" class="h-9 px-3 rounded-r-md bg-accent text-white text-sm font-medium cursor-pointer">搜索</button>
      </form>
      <router-link v-for="link in navLinks" :key="link.to" :to="link.to" @click="mobileMenuOpen = false"
        class="block px-3 py-2 rounded-md text-blue-100 hover:text-white hover:bg-primary no-underline text-sm">
        {{ link.label }}
      </router-link>
      <template v-if="auth.isLoggedIn">
        <router-link to="/admin" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-md text-blue-100 hover:text-white hover:bg-primary no-underline text-sm">管理后台</router-link>
        <router-link to="/profile/me" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-md text-blue-100 hover:text-white hover:bg-primary no-underline text-sm">个人中心</router-link>
        <button @click="onLogout(); mobileMenuOpen = false" class="w-full text-left px-3 py-2 rounded-md text-blue-100 hover:text-white hover:bg-primary bg-transparent border-0 text-sm cursor-pointer">退出</button>
      </template>
      <template v-else>
        <router-link to="/auth/login" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-md text-blue-100 hover:text-white hover:bg-primary no-underline text-sm">登录</router-link>
      </template>
    </div>
  </header>
</template>
