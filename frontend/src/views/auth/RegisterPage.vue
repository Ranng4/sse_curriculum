<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const router = useRouter()

const method = ref('phone')
const phone = ref('')
const email = ref('')
const password = ref('')
const nickname = ref('')
const verificationCode = ref('')
const error = ref('')
const loading = ref(false)

async function onRegister() {
  error.value = ''
  const payload = { method: method.value, password: password.value, nickname: nickname.value.trim(), verification_code: verificationCode.value }
  if (method.value === 'phone') {
    payload.phone = phone.value.trim()
    if (!payload.phone) { error.value = '请输入手机号'; return }
  } else if (method.value === 'email') {
    payload.email = email.value.trim()
    if (!payload.email) { error.value = '请输入邮箱'; return }
  }
  if (!nickname.value.trim()) { error.value = '请输入昵称'; return }
  if (password.value.length < 6) { error.value = '密码至少6位'; return }
  if (verificationCode.value.length < 4) { error.value = '验证码至少4位'; return }

  loading.value = true
  try {
    await auth.register(payload)
    router.push('/')
  } catch (e) {
    error.value = e.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-xl font-bold text-foreground mb-6">注册</h2>
    <form @submit.prevent="onRegister" class="space-y-4">
      <div v-if="error" class="bg-red-50 text-destructive text-sm p-3 rounded-lg border border-red-200">{{ error }}</div>

      <!-- Method selector -->
      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">注册方式</label>
        <div class="flex gap-2">
          <button type="button" @click="method = 'phone'"
            class="flex-1 h-9 rounded-lg text-sm font-medium transition-colors cursor-pointer border"
            :class="method === 'phone' ? 'bg-primary text-white border-primary' : 'bg-surface text-foreground border-border hover:bg-muted'">手机号</button>
          <button type="button" @click="method = 'email'"
            class="flex-1 h-9 rounded-lg text-sm font-medium transition-colors cursor-pointer border"
            :class="method === 'email' ? 'bg-primary text-white border-primary' : 'bg-surface text-foreground border-border hover:bg-muted'">邮箱</button>
        </div>
      </div>

      <div v-if="method === 'phone'">
        <label class="block text-sm font-medium text-foreground mb-1.5">手机号</label>
        <input v-model="phone" type="tel" placeholder="请输入手机号"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>
      <div v-if="method === 'email'">
        <label class="block text-sm font-medium text-foreground mb-1.5">邮箱</label>
        <input v-model="email" type="email" placeholder="请输入邮箱"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>
      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">昵称</label>
        <input v-model="nickname" type="text" placeholder="请输入昵称" maxlength="32"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>
      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">密码</label>
        <input v-model="password" type="password" placeholder="至少6位密码" maxlength="128"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>
      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">验证码（测试用："1234"）</label>
        <input v-model="verificationCode" type="text" placeholder="请输入验证码" maxlength="8"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>
      <button type="submit" :disabled="loading"
        class="w-full h-10 rounded-lg bg-primary text-white font-medium text-sm hover:bg-primary-dark transition-colors cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed border-0">
        {{ loading ? '注册中...' : '注册' }}
      </button>
    </form>
    <p class="text-center text-sm text-muted-foreground mt-4">
      已有账号？<router-link to="/auth/login" class="text-primary font-medium no-underline hover:underline">去登录</router-link>
    </p>
  </div>
</template>
