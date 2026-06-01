<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/utils/api'
import PostCard from '@/components/PostCard.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const keyword = ref(route.query.q || '')
const posts = ref([])
const suggestions = ref([])
const loading = ref(false)
const error = ref('')
const sort = ref('latest')

async function doSearch() {
  const q = keyword.value.trim()
  if (!q) { posts.value = []; return }
  loading.value = true
  error.value = ''
  try {
    const [postsData, suggestData] = await Promise.all([
      api.get('/content/posts', { params: { keyword: q, sort: sort.value, limit: 50 } }),
      api.get('/content/search/suggest', { params: { q, limit: 10 } }),
    ])
    posts.value = postsData
    suggestions.value = suggestData.suggestions || []
  } catch (e) {
    error.value = e.message || '搜索失败'
  } finally {
    loading.value = false
  }
}

function onSuggestionClick(suggestion) {
  keyword.value = suggestion
  doSearch()
}

onMounted(() => {
  if (route.query.q) doSearch()
})
watch(() => route.query.q, (val) => {
  keyword.value = val || ''
  if (val) doSearch()
})
</script>

<template>
  <div>
    <h2 class="text-lg font-bold text-foreground mb-4">搜索</h2>
    <form @submit.prevent="doSearch" class="flex gap-2 mb-4">
      <input
        v-model="keyword" type="text" placeholder="搜索关键词、股票代码..."
        class="flex-1 h-10 px-3 rounded-lg border border-border bg-card text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition"
      />
      <select v-model="sort" class="h-10 px-3 rounded-lg border border-border bg-card text-sm outline-none cursor-pointer">
        <option value="latest">最新</option>
        <option value="hot">最热</option>
      </select>
      <button type="submit" class="h-10 px-5 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors cursor-pointer border-0">搜索</button>
    </form>

    <!-- Suggestions -->
    <div v-if="suggestions.length" class="flex flex-wrap gap-2 mb-4">
      <button
        v-for="s in suggestions" :key="s"
        @click="onSuggestionClick(s)"
        class="px-3 py-1 rounded-full bg-muted text-sm text-foreground hover:bg-primary hover:text-white transition-colors cursor-pointer border-0"
      >{{ s }}</button>
    </div>

    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="doSearch" /></div>
    <div v-else-if="keyword && !posts.length"><EmptyState :message="`未找到与「${keyword}」相关的内容`" /></div>
    <div v-else-if="posts.length" class="space-y-3">
      <p class="text-sm text-muted-foreground mb-2">找到 {{ posts.length }} 条结果</p>
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>
  </div>
</template>
