<script setup>
defineProps({
  comment: { type: Object, required: true },
})

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="py-3" :class="{ 'ml-10 pl-4 border-l-2 border-muted': comment.parent_comment_id }">
    <div class="flex items-center gap-2 mb-1">
      <span class="text-sm font-semibold text-foreground">{{ comment.author?.nickname || '匿名' }}</span>
      <span class="text-xs text-muted-foreground">{{ formatTime(comment.created_at) }}</span>
    </div>
    <p class="text-sm text-foreground leading-relaxed whitespace-pre-wrap">{{ comment.content }}</p>
  </div>
</template>
