<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

const router = useRouter()

const boards = ref([])
const boardId = ref('')
const title = ref('')
const content = ref('')
const postType = ref('normal')
const stockCodes = ref('')
const error = ref('')
const submitting = ref(false)

async function fetchBoards() {
  try {
    const sections = await api.get('/forum/sections')
    boards.value = sections.flatMap(s => s.boards || [])
  } catch (e) {
    /* ignore */
  }
}

async function onSubmit() {
  error.value = ''
  if (!boardId.value) { error.value = '请选择板块'; return }
  if (!title.value.trim()) { error.value = '请输入标题'; return }
  if (!content.value.trim()) { error.value = '请输入内容'; return }

  submitting.value = true
  try {
    const codes = stockCodes.value.split(/[,;\s]+/).map(s => s.trim()).filter(Boolean)
    const post = await api.post('/content/posts', {
      board_id: boardId.value,
      title: title.value.trim(),
      content: content.value.trim(),
      post_type: postType.value,
      stock_codes: codes,
    })
    router.push({ name: 'post-detail', params: { postId: post.id } })
  } catch (e) {
    error.value = e.message || '发帖失败'
  } finally {
    submitting.value = false
  }
}

onMounted(fetchBoards)
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <h2 class="text-lg font-bold text-foreground mb-4">发布新帖</h2>
    <form @submit.prevent="onSubmit" class="bg-card rounded-lg border border-border p-6 space-y-4">
      <div v-if="error" class="bg-red-50 text-destructive text-sm p-3 rounded-lg border border-red-200">{{ error }}</div>

      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">选择板块 *</label>
        <select v-model="boardId" class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary transition cursor-pointer">
          <option value="">-- 请选择 --</option>
          <option v-for="b in boards" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">帖子类型</label>
        <div class="flex gap-2">
          <button type="button" @click="postType = 'normal'"
            class="flex-1 h-9 rounded-lg text-sm font-medium transition-colors cursor-pointer border"
            :class="postType === 'normal' ? 'bg-primary text-white border-primary' : 'bg-surface text-foreground border-border hover:bg-muted'">普通帖</button>
          <button type="button" @click="postType = 'longform'"
            class="flex-1 h-9 rounded-lg text-sm font-medium transition-colors cursor-pointer border"
            :class="postType === 'longform' ? 'bg-primary text-white border-primary' : 'bg-surface text-foreground border-border hover:bg-muted'">长文分析</button>
          <button type="button" @click="postType = 'realtime'"
            class="flex-1 h-9 rounded-lg text-sm font-medium transition-colors cursor-pointer border"
            :class="postType === 'realtime' ? 'bg-primary text-white border-primary' : 'bg-surface text-foreground border-border hover:bg-muted'">实时讨论</button>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">标题 *</label>
        <input v-model="title" type="text" placeholder="请输入标题" maxlength="120"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>

      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">内容 *</label>
        <textarea v-model="content" placeholder="请输入内容..." maxlength="5000" rows="6"
          class="w-full px-3 py-2 rounded-lg border border-border bg-surface text-foreground text-sm outline-none resize-none focus:ring-2 focus:ring-primary focus:border-primary transition"
        ></textarea>
        <p class="text-xs text-muted-foreground mt-1">{{ content.length }}/5000</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">相关股票代码（逗号分隔）</label>
        <input v-model="stockCodes" type="text" placeholder="如: 600519, 000001"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>

      <div class="flex gap-3 pt-2">
        <button type="button" @click="router.back()" class="flex-1 h-10 rounded-lg bg-surface text-foreground text-sm font-medium border border-border hover:bg-muted transition-colors cursor-pointer">取消</button>
        <button type="submit" :disabled="submitting" class="flex-1 h-10 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed border-0">发布</button>
      </div>
    </form>
  </div>
</template>
