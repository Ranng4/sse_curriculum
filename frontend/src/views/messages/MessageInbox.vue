<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import EmptyState from '@/components/EmptyState.vue'

const router = useRouter()
const conversations = ref([])
const loading = ref(true)
const error = ref('')

async function fetchConversations() {
  loading.value = true
  error.value = ''
  try {
    conversations.value = await api.get('/messages/conversations')
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function openChat(partnerId) {
  router.push({ name: 'message-conversation', params: { partnerId } })
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

onMounted(fetchConversations)
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <h2 class="text-lg font-bold text-foreground mb-4">私信</h2>

    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchConversations" /></div>
    <div v-else-if="!conversations.length"><EmptyState message="暂无私信对话" /></div>
    <div v-else class="space-y-1">
      <div
        v-for="conv in conversations" :key="conv.partner_id"
        @click="openChat(conv.partner_id)"
        class="flex items-center gap-3 bg-card rounded-lg border border-border p-4 hover:shadow-sm transition-shadow cursor-pointer"
      >
        <div class="w-10 h-10 rounded-full bg-primary-light flex items-center justify-center text-white text-sm font-bold shrink-0"
          :class="{ 'ring-2 ring-primary': conv.unread_count > 0 }">
          {{ conv.partner_nickname?.charAt(0) || '?' }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between">
            <span class="text-sm font-semibold text-foreground">{{ conv.partner_nickname }}</span>
            <span class="text-xs text-muted-foreground">{{ formatTime(conv.last_time) }}</span>
          </div>
          <p class="text-sm text-muted-foreground truncate">
            <span v-if="conv.last_from_me" class="text-muted-foreground">我: </span>
            {{ conv.last_message }}
          </p>
        </div>
        <span v-if="conv.unread_count > 0"
          class="bg-primary text-white text-xs font-bold px-2 py-0.5 rounded-full shrink-0">
          {{ conv.unread_count }}
        </span>
      </div>
    </div>
  </div>
</template>
