<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'

const route = useRoute()
const router = useRouter()
const section = ref(null)
const loading = ref(true)
const error = ref('')
const categoryLabel = { market: '市场讨论区', topic: '主题专区', company_research: '公司研究专区', qa: '问答求助区' }

async function fetchSection() {
  const category = route.params.category
  loading.value = true
  error.value = ''
  try {
    section.value = await api.get(`/forum/sections/${category}`)
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(fetchSection)
watch(() => route.params.category, fetchSection)
</script>

<template>
  <div>
    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchSection" /></div>
    <template v-else-if="section">
      <div class="flex items-center gap-3 mb-4">
        <button @click="router.push('/')" class="text-muted-foreground hover:text-primary transition-colors bg-transparent border-0 cursor-pointer text-sm">← 返回</button>
        <h2 class="text-lg font-bold text-foreground">{{ section.title }}</h2>
      </div>
      <p class="text-sm text-muted-foreground mb-4">{{ section.description }}</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <div
          v-for="board in section.boards" :key="board.id"
          @click="router.push({ name: 'board', params: { boardId: board.id } })"
          class="bg-card rounded-lg border border-border p-4 hover:shadow-md hover:border-primary/30 transition-all cursor-pointer"
        >
          <h3 class="font-semibold text-foreground mb-1">{{ board.name }}</h3>
          <p class="text-xs text-muted-foreground leading-relaxed line-clamp-2">{{ board.description }}</p>
          <div v-if="board.market" class="mt-2">
            <span class="text-xs bg-muted text-primary px-2 py-0.5 rounded font-medium">{{ board.market }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
