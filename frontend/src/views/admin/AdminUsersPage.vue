<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import EmptyState from '@/components/EmptyState.vue'

const users = ref([])
const loading = ref(true)
const error = ref('')
const statusFilter = ref('all')
const keyword = ref('')
const actionLoading = ref({})

async function fetchUsers() {
  loading.value = true
  error.value = ''
  try {
    const params = { limit: 50 }
    if (statusFilter.value !== 'all') params.status = statusFilter.value
    if (keyword.value.trim()) params.keyword = keyword.value.trim()
    users.value = await api.get('/admin/users', { params })
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function doManage(userId, action) {
  actionLoading.value[userId] = true
  try {
    await api.patch(`/admin/users/${userId}`, { action, reason: `管理员操作: ${action}` })
    await fetchUsers()
  } catch (e) {
    error.value = e.message || '操作失败'
  } finally {
    actionLoading.value[userId] = false
  }
}

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('zh-CN')
}

const statusColors = {
  active: 'bg-green-50 text-green-600',
  warned: 'bg-amber-50 text-amber-600',
  muted: 'bg-orange-50 text-orange-600',
  banned: 'bg-red-50 text-red-500',
}
const statusLabels = { active: '正常', warned: '已警告', muted: '已禁言', banned: '已封禁' }

onMounted(fetchUsers)
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-bold text-foreground">用户管理</h2>
      <router-link to="/admin" class="text-sm text-primary no-underline hover:underline">← 返回后台</router-link>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-2 mb-4">
      <button v-for="opt in ['all', 'active', 'warned', 'muted', 'banned']" :key="opt"
        @click="statusFilter = opt; fetchUsers()"
        class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors cursor-pointer border-0"
        :class="statusFilter === opt ? 'bg-primary text-white' : 'bg-surface text-muted-foreground hover:bg-muted'">
        {{ { all: '全部', active: '正常', warned: '已警告', muted: '已禁言', banned: '已封禁' }[opt] || opt }}
      </button>
      <div class="flex-1" />
      <input v-model="keyword" @keyup.enter="fetchUsers" type="text" placeholder="搜索昵称..."
        class="h-9 px-3 rounded-lg border border-border bg-surface text-sm w-40 outline-none focus:ring-2 focus:ring-primary transition" />
      <button @click="fetchUsers"
        class="h-9 px-3 rounded-lg bg-primary text-white text-sm hover:bg-primary-dark transition-colors cursor-pointer border-0">搜索</button>
    </div>

    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchUsers" /></div>
    <div v-else-if="!users.length"><EmptyState message="暂无用户" /></div>
    <div v-else class="space-y-2">
      <div v-for="user in users" :key="user.user_id"
        class="bg-card rounded-lg border border-border p-4">
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-primary-light flex items-center justify-center text-white text-sm font-bold shrink-0">
              {{ user.nickname?.charAt(0) || '?' }}
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-sm font-semibold text-foreground">{{ user.nickname }}</span>
                <span class="text-xs px-1.5 py-0.5 rounded font-medium" :class="statusColors[user.user_status] || 'bg-gray-100'">
                  {{ statusLabels[user.user_status] || user.user_status }}
                </span>
              </div>
              <div class="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                <span>{{ user.phone || user.email || '-' }}</span>
                <span>{{ user.register_method }}</span>
                <span>发帖 {{ user.posts_count }}</span>
                <span v-if="user.created_at">注册 {{ formatTime(user.created_at) }}</span>
              </div>
              <p v-if="user.status_reason" class="text-xs text-muted-foreground mt-0.5">原因: {{ user.status_reason }}</p>
            </div>
          </div>
          <div class="flex gap-1 shrink-0">
            <button v-if="user.user_status !== 'warned' && user.user_status !== 'banned'"
              @click="doManage(user.user_id, 'warn')" :disabled="actionLoading[user.user_id]"
              class="px-2 py-1 rounded text-xs font-medium bg-amber-50 text-amber-600 hover:bg-amber-100 transition-colors cursor-pointer border-0">警告</button>
            <button v-if="user.user_status !== 'muted' && user.user_status !== 'banned'"
              @click="doManage(user.user_id, 'mute')" :disabled="actionLoading[user.user_id]"
              class="px-2 py-1 rounded text-xs font-medium bg-orange-50 text-orange-600 hover:bg-orange-100 transition-colors cursor-pointer border-0">禁言</button>
            <button v-if="user.user_status !== 'banned'"
              @click="doManage(user.user_id, 'ban')" :disabled="actionLoading[user.user_id]"
              class="px-2 py-1 rounded text-xs font-medium bg-red-50 text-red-500 hover:bg-red-100 transition-colors cursor-pointer border-0">封禁</button>
            <button v-if="user.user_status === 'banned' || user.user_status === 'muted'"
              @click="doManage(user.user_id, 'unban')" :disabled="actionLoading[user.user_id]"
              class="px-2 py-1 rounded text-xs font-medium bg-green-50 text-green-600 hover:bg-green-100 transition-colors cursor-pointer border-0">解封</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
