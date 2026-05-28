<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  post: { type: Object, required: true },
})

const router = useRouter()

function goToPost() {
  router.push({ name: 'post-detail', params: { postId: props.post.id } })
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const typeLabel = { normal: '普通', longform: '长文', realtime: '快讯' }
</script>

<template>
  <article
    class="bg-card rounded-lg border border-border p-4 hover:shadow-md transition-shadow cursor-pointer"
    @click="goToPost"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-1 flex-wrap">
          <span class="text-xs font-medium px-1.5 py-0.5 rounded bg-blue-50 text-primary">
            {{ post.board_name }}
          </span>
          <span v-if="post.post_type !== 'normal'" class="text-xs text-muted-foreground">
            {{ typeLabel[post.post_type] || post.post_type }}
          </span>
        </div>
        <h3 class="text-base font-semibold text-foreground mb-1 line-clamp-2 leading-snug">
          {{ post.title }}
        </h3>
        <p class="text-sm text-muted-foreground line-clamp-2 mb-2 leading-relaxed">
          {{ post.content }}
        </p>
        <div class="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
          <span class="font-medium text-foreground">{{ post.author?.nickname || '匿名' }}</span>
          <span>{{ formatTime(post.created_at) }}</span>
          <span class="flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>
            {{ post.metrics?.like_count || 0 }}
          </span>
          <span class="flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
            {{ post.metrics?.comment_count || 0 }}
          </span>
        </div>
      </div>
      <!-- Stock codes -->
      <div v-if="post.stock_codes?.length" class="hidden sm:flex flex-col gap-1 shrink-0">
        <span
          v-for="code in post.stock_codes.slice(0, 3)" :key="code"
          class="text-xs font-mono bg-muted text-primary px-2 py-0.5 rounded font-medium"
        >{{ code }}</span>
        <span v-if="post.stock_codes.length > 3" class="text-xs text-muted-foreground">
          +{{ post.stock_codes.length - 3 }}
        </span>
      </div>
    </div>
  </article>
</template>
