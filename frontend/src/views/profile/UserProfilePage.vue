<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/utils/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const profile = ref(null)
const following = ref(false)
const stats = ref(null)
const loading = ref(true)
const error = ref('')

const marketLabels = { a_share: 'A股', hk_stock: '港股', us_stock: '美股', fund: '基金', bond: '债券', future: '期货' }
const riskLabels = { C1: '保守型', C2: '稳健型', C3: '平衡型', C4: '进取型', C5: '激进型' }
const badgeLabels = { sharp_analyst: '睿智分析师', value_hunter: '价值猎手', hot_author: '热门作者', community_mentor: '社区导师' }

async function fetchProfile() {
  loading.value = true
  error.value = ''
  try {
    profile.value = await api.get(`/profile/${route.params.userId}`)
    try {
      const s = await api.get(`/social/stats/me`)
      if (s) {
        // /social/stats/me returns stats for the current user; we get target user stats differently
        // Skip for now; we'll compute from following list
      }
    } catch (e) { /* ignore */ }
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function toggleFollow() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const result = following.value
      ? await api.delete(`/social/follows/${route.params.userId}`)
      : await api.post(`/social/follows/${route.params.userId}`)
    following.value = result.is_following
  } catch (e) { /* ignore */ }
}

onMounted(fetchProfile)
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchProfile" /></div>
    <template v-else-if="profile">
      <button @click="router.back()" class="text-muted-foreground hover:text-primary transition-colors bg-transparent border-0 cursor-pointer text-sm mb-4">← 返回</button>

      <div class="bg-card rounded-lg border border-border p-6 mb-6">
        <div class="flex items-start gap-4">
          <div class="w-16 h-16 rounded-full bg-primary-light flex items-center justify-center text-white text-2xl font-bold shrink-0">
            {{ profile.nickname?.charAt(0) || '?' }}
          </div>
          <div class="flex-1">
            <h1 class="text-xl font-bold text-foreground mb-1">{{ profile.nickname || '用户' }}</h1>
            <p v-if="profile.bio" class="text-sm text-muted-foreground mb-2">{{ profile.bio }}</p>
            <div v-if="profile.achievements" class="flex items-center gap-3 text-sm text-muted-foreground flex-wrap">
              <span>发帖 {{ profile.achievements.posts_count || 0 }}</span>
              <span>影响力 {{ profile.achievements.influence_score || 0 }}</span>
            </div>
            <div v-if="profile.achievements?.badges?.length" class="flex gap-1 mt-2">
              <span v-for="badge in profile.achievements.badges" :key="badge" class="text-xs px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 font-medium">
                {{ badgeLabels[badge] || badge }}
              </span>
            </div>
          </div>
          <button
            v-if="auth.isLoggedIn && auth.userId !== route.params.userId"
            @click="toggleFollow"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer border-0 shrink-0"
            :class="following ? 'bg-muted text-foreground hover:bg-border' : 'bg-primary text-white hover:bg-primary-dark'"
          >{{ following ? '已关注' : '+ 关注' }}</button>
        </div>
      </div>

      <div v-if="profile.investment_preferences" class="bg-card rounded-lg border border-border p-6">
        <h3 class="font-semibold text-foreground mb-3">投资偏好</h3>
        <div class="flex flex-wrap gap-2 mb-3">
          <span v-for="m in profile.investment_preferences.focus_markets || []" :key="m" class="text-xs bg-blue-50 text-primary px-2 py-0.5 rounded">
            {{ marketLabels[m] || m }}
          </span>
          <span v-if="!profile.investment_preferences.focus_markets?.length" class="text-sm text-muted-foreground">未设置</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-muted-foreground">风险偏好:</span>
          <span class="text-sm font-medium text-foreground">{{ riskLabels[profile.investment_preferences.risk_preference] || profile.investment_preferences.risk_preference }}</span>
        </div>
      </div>
    </template>
  </div>
</template>
