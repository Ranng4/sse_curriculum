<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'

const router = useRouter()
const posts = ref([])
const loading = ref(true)
const error = ref('')

async function fetchHot() {
  loading.value = true
  error.value = ''
  try {
    posts.value = await api.get('/content/hot-rank', { params: { limit: 50 } })
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

onMounted(fetchHot)
</script>

<template>
  <div>
    <h2 class="text-lg font-bold text-foreground mb-4">🔥 热门排行</h2>
    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchHot" /></div>
    <div v-else class="space-y-2">
      <div
        v-for="(post, idx) in posts" :key="post.id"
        @click="router.push({ name: 'post-detail', params: { postId: post.id } })"
        class="flex items-center gap-3 bg-card rounded-lg border border-border p-3 hover:shadow-sm transition-shadow cursor-pointer"
      >
        <span class="text-lg font-bold w-8 h-8 flex items-center justify-center rounded-full shrink-0"
          :class="idx < 3 ? 'bg-red-50 text-red-500' : 'bg-muted text-muted-foreground'"
        >{{ idx + 1 }}</span>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-0.5">
            <span class="text-xs px-1.5 py-0.5 rounded bg-blue-50 text-primary font-medium">{{ post.board_name }}</span>
          </div>
          <h4 class="text-sm font-medium text-foreground truncate">{{ post.title }}</h4>
          <div class="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
            <span>{{ post.author?.nickname }}</span>
            <span>{{ formatTime(post.created_at) }}</span>
            <span class="font-medium">{{ post.metrics?.engagement_score || 0 }} 热度</span>
            <span>{{ post.metrics?.like_count || 0 }} 👍</span>
            <span>{{ post.metrics?.comment_count || 0 }} 💬</span>
          </div>
        </div>
        <div v-if="post.stock_codes?.length" class="hidden sm:flex gap-1 shrink-0">
          <span v-for="code in post.stock_codes.slice(0, 3)" :key="code" class="text-xs font-mono bg-muted text-primary px-1.5 py-0.5 rounded">{{ code }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
