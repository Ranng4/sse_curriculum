<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/utils/api'
import CommentItem from '@/components/CommentItem.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const post = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref('')
const commentContent = ref('')
const submitting = ref(false)

async function fetchPost() {
  loading.value = true
  error.value = ''
  try {
    const [postData, commentsData] = await Promise.all([
      api.get(`/content/posts/${route.params.postId}`),
      api.get(`/content/posts/${route.params.postId}/comments`),
    ])
    post.value = postData
    comments.value = commentsData
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function toggleLike() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const metrics = post.value.liked_by_me
      ? await api.delete(`/content/posts/${post.value.id}/like`)
      : await api.post(`/content/posts/${post.value.id}/like`)
    post.value.liked_by_me = !post.value.liked_by_me
    post.value.metrics = metrics
  } catch (e) { /* ignore */ }
}

async function toggleFavorite() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const metrics = post.value.favorited_by_me
      ? await api.delete(`/content/posts/${post.value.id}/favorite`)
      : await api.post(`/content/posts/${post.value.id}/favorite`)
    post.value.favorited_by_me = !post.value.favorited_by_me
    post.value.metrics = metrics
  } catch (e) { /* ignore */ }
}

async function submitComment() {
  const content = commentContent.value.trim()
  if (!content) return
  submitting.value = true
  try {
    const newComment = await api.post(`/content/posts/${post.value.id}/comments`, { content })
    comments.value.push(newComment)
    commentContent.value = ''
    post.value.metrics.comment_count++
  } catch (e) {
    /* ignore */
  } finally {
    submitting.value = false
  }
}

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const typeLabel = { normal: '普通帖', longform: '长文分析', realtime: '实时讨论' }

onMounted(fetchPost)
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchPost" /></div>
    <template v-else-if="post">
      <!-- Post Header -->
      <div class="mb-4">
        <button @click="router.back()" class="text-muted-foreground hover:text-primary transition-colors bg-transparent border-0 cursor-pointer text-sm mb-3">← 返回</button>
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-medium px-2 py-0.5 rounded bg-blue-50 text-primary">{{ post.board_name }}</span>
          <span class="text-xs text-muted-foreground">{{ typeLabel[post.post_type] || post.post_type }}</span>
        </div>
        <h1 class="text-2xl font-bold text-foreground leading-tight mb-3">{{ post.title }}</h1>
        <div class="flex items-center gap-3 text-sm text-muted-foreground flex-wrap">
          <router-link :to="{ name: 'user-profile', params: { userId: post.author?.user_id } }" class="font-semibold text-foreground no-underline hover:text-primary transition-colors">{{ post.author?.nickname }}</router-link>
          <span>{{ formatTime(post.created_at) }}</span>
          <span v-if="post.stock_codes?.length" class="flex gap-1">
            <span v-for="code in post.stock_codes" :key="code" class="text-xs font-mono bg-muted text-primary px-1.5 py-0.5 rounded">{{ code }}</span>
          </span>
        </div>
      </div>

      <!-- Post Content -->
      <div class="bg-card rounded-lg border border-border p-6 mb-6">
        <div class="text-foreground leading-relaxed whitespace-pre-wrap text-sm">{{ post.content }}</div>
      </div>

      <!-- Post Actions -->
      <div class="flex items-center gap-4 mb-8 bg-card rounded-lg border border-border p-3">
        <button
          @click="toggleLike"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors cursor-pointer border-0"
          :class="post.liked_by_me ? 'bg-red-50 text-red-500' : 'bg-surface text-muted-foreground hover:bg-muted'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" :fill="post.liked_by_me ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>
          {{ post.metrics?.like_count || 0 }}
        </button>
        <button
          @click="toggleFavorite"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors cursor-pointer border-0"
          :class="post.favorited_by_me ? 'bg-amber-50 text-accent' : 'bg-surface text-muted-foreground hover:bg-muted'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" :fill="post.favorited_by_me ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>
          {{ post.metrics?.favorite_count || 0 }}
        </button>
        <span class="flex items-center gap-1.5 text-sm text-muted-foreground">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
          {{ post.metrics?.comment_count || 0 }}
        </span>
      </div>

      <!-- Comments Section -->
      <h3 class="text-base font-bold text-foreground mb-4">评论 ({{ comments.length }})</h3>

      <!-- Comment Form -->
      <div v-if="auth.isLoggedIn" class="bg-card rounded-lg border border-border p-4 mb-4">
        <textarea
          v-model="commentContent" placeholder="写下你的看法..." maxlength="2000" rows="3"
          class="w-full px-3 py-2 rounded-lg border border-border bg-surface text-foreground text-sm outline-none resize-none focus:ring-2 focus:ring-primary focus:border-primary transition"
        ></textarea>
        <div class="flex justify-end mt-2">
          <button
            @click="submitComment" :disabled="submitting || !commentContent.trim()"
            class="px-4 py-1.5 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed border-0"
          >{{ submitting ? '提交中...' : '发表评论' }}</button>
        </div>
      </div>
      <div v-else class="bg-muted rounded-lg p-4 text-center text-sm text-muted-foreground mb-4">
        <router-link to="/auth/login" class="text-primary font-medium no-underline hover:underline">登录</router-link> 后参与评论
      </div>

      <div v-if="!comments.length" class="bg-card rounded-lg border border-border p-8">
        <EmptyState message="暂无评论，快来抢沙发" />
      </div>
      <div v-else class="bg-card rounded-lg border border-border divide-y divide-border px-4">
        <CommentItem v-for="c in comments" :key="c.id" :comment="c" />
      </div>
    </template>
  </div>
</template>
