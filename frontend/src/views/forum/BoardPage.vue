<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import PostCard from '@/components/PostCard.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const board = ref(null)
const posts = ref([])
const loading = ref(true)
const error = ref('')

async function fetchBoard() {
  loading.value = true
  error.value = ''
  try {
    board.value = await api.get(`/forum/boards/${route.params.boardId}`)
    posts.value = await api.get('/content/posts', { params: { board_id: route.params.boardId, limit: 50 } })
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(fetchBoard)
watch(() => route.params.boardId, fetchBoard)
</script>

<template>
  <div>
    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchBoard" /></div>
    <template v-else-if="board">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
          <button @click="router.back()" class="text-muted-foreground hover:text-primary transition-colors bg-transparent border-0 cursor-pointer text-sm">← 返回</button>
          <div>
            <h2 class="text-lg font-bold text-foreground">{{ board.name }}</h2>
            <p class="text-xs text-muted-foreground">{{ board.description }}</p>
          </div>
        </div>
        <router-link to="/posts/new" class="px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium no-underline hover:bg-primary-dark transition-colors">发帖</router-link>
      </div>
      <div v-if="!posts.length"><EmptyState message="该板块暂无帖子，快来发第一个帖吧" /></div>
      <div v-else class="space-y-3">
        <PostCard v-for="post in posts" :key="post.id" :post="post" />
      </div>
    </template>
  </div>
</template>
