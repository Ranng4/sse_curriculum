<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const router = useRouter()

const account = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function onLogin() {
  error.value = ''
  if (!account.value.trim() || !password.value) {
    error.value = '请填写账号和密码'
    return
  }
  loading.value = true
  try {
    await auth.login({ account: account.value.trim(), password: password.value })
    router.push('/')
  } catch (e) {
    error.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-xl font-bold text-foreground mb-6">登录</h2>
    <form @submit.prevent="onLogin" class="space-y-4">
      <div v-if="error" class="bg-red-50 text-destructive text-sm p-3 rounded-lg border border-red-200">{{ error }}</div>
      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">手机号/邮箱/第三方账号</label>
        <input v-model="account" type="text" placeholder="请输入账号"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>
      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">密码</label>
        <input v-model="password" type="password" placeholder="请输入密码"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>
      <button type="submit" :disabled="loading"
        class="w-full h-10 rounded-lg bg-primary text-white font-medium text-sm hover:bg-primary-dark transition-colors cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed border-0">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>
    <p class="text-center text-sm text-muted-foreground mt-4">
      还没有账号？<router-link to="/auth/register" class="text-primary font-medium no-underline hover:underline">立即注册</router-link>
    </p>
  </div>
</template>
