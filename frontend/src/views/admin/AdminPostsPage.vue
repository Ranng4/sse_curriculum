<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/utils/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const auth = useAuthStore()
const posts = ref([])
const loading = ref(true)
const error = ref('')
const statusFilter = ref(route.query.status || 'all')
const actionLoading = ref({})

async function fetchPosts() {
  loading.value = true
  error.value = ''
  try {
    const params = { limit: 50 }
    if (statusFilter.value !== 'all') params.status = statusFilter.value
    posts.value = await api.get('/admin/posts', { params })
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function doReview(postId, action) {
  actionLoading.value[postId] = true
  try {
    await api.patch(`/admin/posts/${postId}`, { action, reason: `管理员${action === 'approve' ? '批准' : action === 'reject' ? '驳回' : '标记'}` })
    await fetchPosts()
  } catch (e) {
    error.value = e.message || '操作失败'
  } finally {
    actionLoading.value[postId] = false
  }
}

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const statusColors = {
  approved: 'bg-green-50 text-green-600',
  rejected: 'bg-red-50 text-red-500',
  flagged: 'bg-amber-50 text-amber-600',
  pending: 'bg-blue-50 text-blue-600',
}
const statusLabels = { approved: '已批准', rejected: '已驳回', flagged: '已标记', pending: '待审核' }

watch(statusFilter, fetchPosts)
onMounted(fetchPosts)
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-bold text-foreground">内容审核</h2>
      <router-link to="/admin" class="text-sm text-primary no-underline hover:underline">← 返回后台</router-link>
    </div>

    <!-- Filter Tabs -->
    <div class="flex gap-2 mb-4">
      <button v-for="opt in ['all', 'pending', 'flagged', 'approved', 'rejected']" :key="opt"
        @click="statusFilter = opt"
        class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors cursor-pointer border-0"
        :class="statusFilter === opt ? 'bg-primary text-white' : 'bg-surface text-muted-foreground hover:bg-muted'">
        {{ { all: '全部', pending: '待审核', flagged: '已标记', approved: '已批准', rejected: '已驳回' }[opt] || opt }}
      </button>
    </div>

    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchPosts" /></div>
    <div v-else-if="!posts.length"><EmptyState message="暂无需要审核的内容" /></div>
    <div v-else class="space-y-2">
      <div v-for="post in posts" :key="post.id"
        class="bg-card rounded-lg border border-border p-4">
        <div class="flex items-start justify-between gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-xs px-1.5 py-0.5 rounded font-medium" :class="statusColors[post.review_status] || 'bg-gray-100'">
                {{ statusLabels[post.review_status] || post.review_status }}
              </span>
              <span class="text-xs text-muted-foreground">{{ post.board_name }}</span>
              <span class="text-xs text-muted-foreground">by {{ post.author_nickname }}</span>
              <span class="text-xs text-muted-foreground">{{ formatTime(post.created_at) }}</span>
            </div>
            <h4 class="text-sm font-medium text-foreground mb-1">{{ post.title }}</h4>
            <p v-if="post.review_reason" class="text-xs text-muted-foreground">原因: {{ post.review_reason }}</p>
          </div>
          <div class="flex gap-1 shrink-0">
            <button v-if="post.review_status !== 'approved'"
              @click="doReview(post.id, 'approve')" :disabled="actionLoading[post.id]"
              class="px-2 py-1 rounded text-xs font-medium bg-green-50 text-green-600 hover:bg-green-100 transition-colors cursor-pointer border-0">
              批准</button>
            <button v-if="post.review_status !== 'rejected'"
              @click="doReview(post.id, 'reject')" :disabled="actionLoading[post.id]"
              class="px-2 py-1 rounded text-xs font-medium bg-red-50 text-red-500 hover:bg-red-100 transition-colors cursor-pointer border-0">
              驳回</button>
            <button v-if="post.review_status !== 'flagged'"
              @click="doReview(post.id, 'flag')" :disabled="actionLoading[post.id]"
              class="px-2 py-1 rounded text-xs font-medium bg-amber-50 text-amber-600 hover:bg-amber-100 transition-colors cursor-pointer border-0">
              标记</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
