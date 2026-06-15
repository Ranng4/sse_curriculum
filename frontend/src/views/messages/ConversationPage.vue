<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const messages = ref([])
const partnerNickname = ref('')
const loading = ref(true)
const error = ref('')
const newContent = ref('')
const sending = ref(false)
const chatContainer = ref(null)

async function fetchMessages() {
  loading.value = true
  error.value = ''
  try {
    const partnerId = route.params.partnerId
    messages.value = await api.get(`/messages/conversations/${partnerId}`)
    if (messages.value.length > 0) {
      // Find partner nickname from the first message
      const first = messages.value[0]
      partnerNickname.value = first.from_id === partnerId ? first.from_nickname : '对方'
      if (first.from_id !== partnerId && first.from_id !== localStorage.getItem('user_id')) {
        // Get from the conversation list instead
      }
    }
    // Get partner info
    try {
      const convos = await api.get('/messages/conversations')
      const conv = convos.find(c => c.partner_id === partnerId)
      if (conv) partnerNickname.value = conv.partner_nickname
    } catch (_) {}
    await nextTick()
    scrollToBottom()
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function sendMessage() {
  const content = newContent.value.trim()
  if (!content) return
  sending.value = true
  try {
    const msg = await api.post('/messages', { to_user_id: route.params.partnerId, content })
    messages.value.push(msg)
    newContent.value = ''
    await nextTick()
    scrollToBottom()
  } catch (e) {
    error.value = e.message || '发送失败'
  } finally {
    sending.value = false
  }
}

function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(fetchMessages)
</script>

<template>
  <div class="max-w-3xl mx-auto flex flex-col h-[calc(100vh-120px)]">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-4">
      <button @click="router.push({ name: 'message-inbox' })"
        class="text-muted-foreground hover:text-primary transition-colors bg-transparent border-0 cursor-pointer text-sm">← 返回</button>
      <div class="w-8 h-8 rounded-full bg-primary-light flex items-center justify-center text-white text-sm font-bold shrink-0">
        {{ partnerNickname?.charAt(0) || '?' }}
      </div>
      <h2 class="text-base font-bold text-foreground">{{ partnerNickname || '私信' }}</h2>
    </div>

    <!-- Messages -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto bg-card rounded-lg border border-border p-4 mb-4">
      <div v-if="loading"><LoadingSpinner /></div>
      <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchMessages" /></div>
      <div v-else-if="!messages.length"><EmptyState message="发送第一条消息开始对话" /></div>
      <div v-else class="space-y-3">
        <div v-for="msg in messages" :key="msg.id"
          class="flex" :class="msg.from_id === route.params.partnerId ? 'justify-start' : 'justify-end'">
          <div class="max-w-[75%] rounded-lg px-3 py-2 text-sm"
            :class="msg.from_id === route.params.partnerId
              ? 'bg-muted text-foreground rounded-tl-none'
              : 'bg-primary text-white rounded-tr-none'">
            <p class="whitespace-pre-wrap break-words">{{ msg.content }}</p>
            <p class="text-xs mt-1 opacity-70">{{ formatTime(msg.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Input -->
    <form @submit.prevent="sendMessage" class="flex gap-2">
      <input v-model="newContent" type="text" placeholder="输入消息..."
        class="flex-1 h-10 px-3 rounded-lg border border-border bg-card text-foreground text-sm outline-none focus:ring-2 focus:ring-primary transition"
        maxlength="2000" />
      <button type="submit" :disabled="sending || !newContent.trim()"
        class="h-10 px-4 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed border-0">
        {{ sending ? '发送中' : '发送' }}
      </button>
    </form>
  </div>
</template>
