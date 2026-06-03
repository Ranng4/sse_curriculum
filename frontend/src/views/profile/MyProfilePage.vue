<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/utils/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'

const auth = useAuthStore()
const router = useRouter()
const profile = ref(null)
const socialStats = ref(null)
const loading = ref(true)
const error = ref('')
const tab = ref('info')

const marketLabels = { a_share: 'A股', hk_stock: '港股', us_stock: '美股', fund: '基金', bond: '债券', future: '期货' }
const riskLabels = { C1: '保守型', C2: '稳健型', C3: '平衡型', C4: '进取型', C5: '激进型' }
const badgeLabels = { sharp_analyst: '睿智分析师', value_hunter: '价值猎手', hot_author: '热门作者', community_mentor: '社区导师' }

async function fetchProfile() {
  loading.value = true
  error.value = ''
  try {
    const [profileData, statsData] = await Promise.all([
      api.get('/profile/me'),
      api.get('/social/stats/me'),
    ])
    profile.value = profileData
    socialStats.value = statsData
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function onLogout() {
  auth.logout()
  router.push('/auth/login')
}

onMounted(fetchProfile)
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchProfile" /></div>
    <template v-else-if="profile">
      <!-- Profile Header -->
      <div class="bg-card rounded-lg border border-border p-6 mb-6">
        <div class="flex items-start gap-4">
          <div class="w-16 h-16 rounded-full bg-primary flex items-center justify-center text-white text-2xl font-bold shrink-0">
            {{ profile.nickname?.charAt(0) || '?' }}
          </div>
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <h1 class="text-xl font-bold text-foreground">{{ profile.nickname }}</h1>
            </div>
            <p v-if="profile.bio" class="text-sm text-muted-foreground mb-2">{{ profile.bio }}</p>
            <div class="flex items-center gap-3 text-sm text-muted-foreground flex-wrap">
              <span>关注 {{ socialStats?.following_count || 0 }}</span>
              <span>粉丝 {{ socialStats?.follower_count || 0 }}</span>
              <span>发帖 {{ profile.achievements?.posts_count || 0 }}</span>
              <span>影响力 {{ profile.achievements?.influence_score || 0 }}</span>
            </div>
            <!-- Badges -->
            <div v-if="profile.achievements?.badges?.length" class="flex gap-1 mt-2">
              <span v-for="badge in profile.achievements.badges" :key="badge" class="text-xs px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 font-medium">
                {{ badgeLabels[badge] || badge }}
              </span>
            </div>
          </div>
          <router-link to="/profile/me/edit" class="px-3 py-1.5 rounded-lg border border-border text-sm text-foreground no-underline hover:bg-muted transition-colors shrink-0">编辑资料</router-link>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-0 border-b border-border mb-4">
        <button @click="tab = 'info'" class="px-4 py-2 text-sm font-medium border-b-2 transition-colors cursor-pointer bg-transparent"
          :class="tab === 'info' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'">基本信息</button>
        <button @click="tab = 'preferences'" class="px-4 py-2 text-sm font-medium border-b-2 transition-colors cursor-pointer bg-transparent"
          :class="tab === 'preferences' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'">投资偏好</button>
        <button @click="tab = 'privacy'" class="px-4 py-2 text-sm font-medium border-b-2 transition-colors cursor-pointer bg-transparent"
          :class="tab === 'privacy' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'">隐私设置</button>
        <button @click="tab = 'verification'" class="px-4 py-2 text-sm font-medium border-b-2 transition-colors cursor-pointer bg-transparent"
          :class="tab === 'verification' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'">认证状态</button>
      </div>

      <!-- Info Tab -->
      <div v-if="tab === 'info'" class="bg-card rounded-lg border border-border p-6 space-y-3">
        <div class="flex justify-between"><span class="text-sm text-muted-foreground">昵称</span><span class="text-sm font-medium text-foreground">{{ profile.nickname }}</span></div>
        <div class="flex justify-between"><span class="text-sm text-muted-foreground">简介</span><span class="text-sm text-foreground">{{ profile.bio || '未设置' }}</span></div>
        <div class="flex justify-between"><span class="text-sm text-muted-foreground">经验标签</span><span class="text-sm text-foreground">{{ profile.experience_tags?.join(', ') || '无' }}</span></div>
        <div class="flex justify-between"><span class="text-sm text-muted-foreground">注册时间</span><span class="text-sm text-foreground">{{ new Date(profile.created_at).toLocaleDateString('zh-CN') }}</span></div>
      </div>

      <!-- Preferences Tab -->
      <div v-if="tab === 'preferences'" class="bg-card rounded-lg border border-border p-6 space-y-3">
        <div class="flex justify-between">
          <span class="text-sm text-muted-foreground">关注市场</span>
          <div class="flex gap-1 flex-wrap">
            <span v-for="m in profile.investment_preferences?.focus_markets" :key="m" class="text-xs bg-blue-50 text-primary px-2 py-0.5 rounded">{{ marketLabels[m] || m }}</span>
            <span v-if="!profile.investment_preferences?.focus_markets?.length" class="text-sm text-muted-foreground">未设置</span>
          </div>
        </div>
        <div class="flex justify-between">
          <span class="text-sm text-muted-foreground">风险偏好</span>
          <span class="text-sm font-medium text-foreground">{{ riskLabels[profile.investment_preferences?.risk_preference] || profile.investment_preferences?.risk_preference }}</span>
        </div>
        <router-link to="/suitability" class="inline-block mt-2 text-sm text-primary font-medium no-underline hover:underline">投资者适当性评估 →</router-link>
      </div>

      <!-- Privacy Tab -->
      <div v-if="tab === 'privacy'" class="bg-card rounded-lg border border-border p-6 space-y-3">
        <div class="flex justify-between"><span class="text-sm text-muted-foreground">昵称可见性</span><span class="text-sm text-foreground">{{ profile.privacy_settings?.nickname_visibility }}</span></div>
        <div class="flex justify-between"><span class="text-sm text-muted-foreground">头像可见性</span><span class="text-sm text-foreground">{{ profile.privacy_settings?.avatar_visibility }}</span></div>
        <div class="flex justify-between"><span class="text-sm text-muted-foreground">简介可见性</span><span class="text-sm text-foreground">{{ profile.privacy_settings?.bio_visibility }}</span></div>
        <div class="flex justify-between"><span class="text-sm text-muted-foreground">投资偏好可见性</span><span class="text-sm text-foreground">{{ profile.privacy_settings?.investment_preferences_visibility }}</span></div>
        <div class="flex justify-between"><span class="text-sm text-muted-foreground">成就可见性</span><span class="text-sm text-foreground">{{ profile.privacy_settings?.achievements_visibility }}</span></div>
      </div>

      <!-- Verification Tab -->
      <div v-if="tab === 'verification'" class="bg-card rounded-lg border border-border p-6">
        <div class="flex justify-between mb-3">
          <span class="text-sm text-muted-foreground">基础认证</span>
          <span class="text-xs px-2 py-0.5 rounded font-medium"
            :class="profile.auth?.basic_verified ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-500'">{{ profile.auth?.basic_verified ? '已认证' : '未认证' }}</span>
        </div>
        <router-link to="/auth/register" class="text-sm text-primary font-medium no-underline hover:underline">前往认证 →</router-link>
      </div>

      <!-- Logout -->
      <div class="mt-6 text-center">
        <button @click="onLogout" class="px-6 py-2 rounded-lg bg-destructive text-white text-sm font-medium hover:bg-red-700 transition-colors cursor-pointer border-0">退出登录</button>
      </div>
    </template>
  </div>
</template>
