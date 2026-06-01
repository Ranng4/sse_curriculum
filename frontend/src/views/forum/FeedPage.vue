<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/utils/api'
import PostCard from '@/components/PostCard.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const posts = ref([])
const loading = ref(true)
const error = ref('')

async function fetchFeed() {
  loading.value = true
  error.value = ''
  try {
    const followingOnly = route.query.following_only === '1'
    posts.value = await api.get('/content/feed', { params: { following_only: followingOnly, limit: 30 } })
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(fetchFeed)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-bold text-foreground">动态流</h2>
      <router-link to="/posts/new" class="px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium no-underline hover:bg-primary-dark transition-colors">发帖</router-link>
    </div>

    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchFeed" /></div>
    <div v-else-if="!posts.length"><EmptyState message="还没有动态，快去关注一些用户吧" /></div>
    <div v-else class="space-y-3">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>
  </div>
</template>
