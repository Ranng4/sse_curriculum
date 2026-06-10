<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'

const stats = ref(null)
const loading = ref(true)
const error = ref('')

async function fetchStats() {
  loading.value = true
  error.value = ''
  try {
    stats.value = await api.get('/admin/stats')
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(fetchStats)
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-bold text-foreground">管理后台</h2>
      <div class="flex gap-2">
        <router-link to="/admin/posts" class="px-3 py-1.5 rounded-lg bg-surface text-foreground text-sm border border-border no-underline hover:bg-muted transition-colors">内容审核</router-link>
        <router-link to="/admin/users" class="px-3 py-1.5 rounded-lg bg-surface text-foreground text-sm border border-border no-underline hover:bg-muted transition-colors">用户管理</router-link>
      </div>
    </div>

    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchStats" /></div>
    <template v-else-if="stats">
      <!-- Summary Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-card rounded-lg border border-border p-4">
          <p class="text-xs text-muted-foreground mb-1">总用户数</p>
          <p class="text-2xl font-bold text-primary">{{ stats.total_users }}</p>
        </div>
        <div class="bg-card rounded-lg border border-border p-4">
          <p class="text-xs text-muted-foreground mb-1">总帖子数</p>
          <p class="text-2xl font-bold text-primary">{{ stats.total_posts }}</p>
        </div>
        <div class="bg-card rounded-lg border border-border p-4">
          <p class="text-xs text-muted-foreground mb-1">总评论数</p>
          <p class="text-2xl font-bold text-primary">{{ stats.total_comments }}</p>
        </div>
        <div class="bg-card rounded-lg border border-border p-4">
          <p class="text-xs text-muted-foreground mb-1">总点赞数</p>
          <p class="text-2xl font-bold text-primary">{{ stats.total_likes }}</p>
        </div>
      </div>

      <!-- Activity -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div class="bg-card rounded-lg border border-border p-4">
          <p class="text-sm font-semibold text-foreground mb-3">今日活跃</p>
          <div class="flex gap-4">
            <div><span class="text-xs text-muted-foreground">今日帖子</span><p class="text-lg font-bold text-foreground">{{ stats.posts_today }}</p></div>
            <div><span class="text-xs text-muted-foreground">活跃用户</span><p class="text-lg font-bold text-foreground">{{ stats.active_users_today }}</p></div>
          </div>
        </div>
        <div class="bg-card rounded-lg border border-border p-4">
          <p class="text-sm font-semibold text-foreground mb-3">待处理</p>
          <div class="flex gap-4">
            <router-link to="/admin/posts?status=pending" class="no-underline">
              <span class="text-xs text-muted-foreground">待审核</span>
              <p class="text-lg font-bold text-amber-500">{{ stats.pending_reviews }}</p>
            </router-link>
            <router-link to="/admin/posts?status=flagged" class="no-underline">
              <span class="text-xs text-muted-foreground">被举报</span>
              <p class="text-lg font-bold text-destructive">{{ stats.flagged_content }}</p>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Top Boards -->
      <div class="bg-card rounded-lg border border-border p-4" v-if="stats.top_boards?.length">
        <p class="text-sm font-semibold text-foreground mb-3">活跃板块 TOP10</p>
        <div class="space-y-2">
          <div v-for="(b, idx) in stats.top_boards" :key="b.board_name"
            class="flex items-center justify-between text-sm">
            <div class="flex items-center gap-2">
              <span class="w-5 text-center font-bold" :class="idx < 3 ? 'text-primary' : 'text-muted-foreground'">{{ idx + 1 }}</span>
              <span class="text-foreground">{{ b.board_name }}</span>
            </div>
            <span class="text-muted-foreground">{{ b.post_count }} 帖</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
