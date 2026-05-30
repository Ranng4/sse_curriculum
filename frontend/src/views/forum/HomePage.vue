<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'

const router = useRouter()
const sections = ref([])
const hotPosts = ref([])
const loading = ref(true)
const error = ref('')

const categoryIcons = { market: '📈', topic: '💡', company_research: '🔬', qa: '❓' }

async function fetchData() {
  loading.value = true
  error.value = ''
  try {
    const [sectionsData, hotData] = await Promise.all([
      api.get('/forum/sections'),
      api.get('/content/hot-rank', { params: { limit: 10 } }),
    ])
    sections.value = sectionsData
    hotPosts.value = hotData
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function goToSection(category) {
  router.push({ name: 'section', params: { category } })
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

onMounted(fetchData)
</script>

<template>
  <div v-if="loading"><LoadingSpinner /></div>
  <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchData" /></div>
  <template v-else>
    <!-- Forum Sections -->
    <h2 class="text-lg font-bold text-foreground mb-4">论坛板块</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div
        v-for="section in sections" :key="section.category"
        @click="goToSection(section.category)"
        class="bg-card rounded-lg border border-border p-4 hover:shadow-md hover:border-primary/30 transition-all cursor-pointer"
      >
        <div class="flex items-center gap-2 mb-2">
          <span class="text-2xl">{{ categoryIcons[section.category] || '📋' }}</span>
          <h3 class="font-semibold text-foreground">{{ section.title }}</h3>
        </div>
        <p class="text-xs text-muted-foreground leading-relaxed">{{ section.description }}</p>
        <div class="mt-2 flex flex-wrap gap-1">
          <span
            v-for="board in section.boards.slice(0, 4)" :key="board.id"
            class="text-xs bg-muted text-muted-foreground px-1.5 py-0.5 rounded"
          >{{ board.name }}</span>
          <span v-if="section.boards.length > 4" class="text-xs text-muted-foreground">+{{ section.boards.length - 4 }}</span>
        </div>
      </div>
    </div>

    <!-- Hot Posts -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-bold text-foreground">热榜</h2>
      <router-link to="/hot" class="text-sm text-primary font-medium no-underline hover:underline">查看更多 →</router-link>
    </div>
    <div class="space-y-3">
      <div
        v-for="(post, idx) in hotPosts.slice(0, 8)" :key="post.id"
        @click="router.push({ name: 'post-detail', params: { postId: post.id } })"
        class="flex items-center gap-3 bg-card rounded-lg border border-border p-3 hover:shadow-sm transition-shadow cursor-pointer"
      >
        <span class="text-lg font-bold w-7 h-7 flex items-center justify-center rounded-full shrink-0"
          :class="idx < 3 ? 'bg-red-50 text-red-500' : 'bg-muted text-muted-foreground'"
        >{{ idx + 1 }}</span>
        <div class="flex-1 min-w-0">
          <h4 class="text-sm font-medium text-foreground truncate">{{ post.title }}</h4>
          <div class="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
            <span>{{ post.author?.nickname }}</span>
            <span>{{ formatTime(post.created_at) }}</span>
            <span>{{ post.metrics?.engagement_score || 0 }} 热度</span>
          </div>
        </div>
      </div>
    </div>
  </template>
</template>
