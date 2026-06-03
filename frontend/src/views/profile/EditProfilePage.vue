<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

const router = useRouter()

const nickname = ref('')
const bio = ref('')
const avatarUrl = ref('')
const experienceTags = ref('')
const focusMarkets = ref([])
const riskPreference = ref('C3')
const error = ref('')
const saving = ref(false)

const marketOptions = [
  { value: 'a_share', label: 'A股' },
  { value: 'hk_stock', label: '港股' },
  { value: 'us_stock', label: '美股' },
  { value: 'fund', label: '基金' },
  { value: 'bond', label: '债券' },
  { value: 'future', label: '期货' },
]
const riskOptions = [
  { value: 'C1', label: 'C1 保守型' },
  { value: 'C2', label: 'C2 稳健型' },
  { value: 'C3', label: 'C3 平衡型' },
  { value: 'C4', label: 'C4 进取型' },
  { value: 'C5', label: 'C5 激进型' },
]

function toggleMarket(val) {
  const idx = focusMarkets.value.indexOf(val)
  if (idx >= 0) focusMarkets.value.splice(idx, 1)
  else focusMarkets.value.push(val)
}

async function loadProfile() {
  try {
    const profile = await api.get('/profile/me')
    nickname.value = profile.nickname || ''
    bio.value = profile.bio || ''
    avatarUrl.value = profile.avatar_url || ''
    experienceTags.value = (profile.experience_tags || []).join(', ')
    focusMarkets.value = profile.investment_preferences?.focus_markets || []
    riskPreference.value = profile.investment_preferences?.risk_preference || 'C3'
  } catch (e) {
    error.value = e.message || '加载失败'
  }
}

async function onSaveBasic() {
  error.value = ''
  saving.value = true
  try {
    const tags = experienceTags.value.split(/[,;，；\s]+/).map(s => s.trim()).filter(Boolean)
    await api.patch('/profile/basic', {
      nickname: nickname.value.trim() || undefined,
      bio: bio.value.trim() || undefined,
      avatar_url: avatarUrl.value.trim() || undefined,
      experience_tags: tags.length ? tags : undefined,
    })
    router.push('/profile/me')
  } catch (e) {
    error.value = e.message || '保存失败'
  } finally {
    saving.value = false
  }
}

async function onSavePreferences() {
  error.value = ''
  saving.value = true
  try {
    await api.patch('/profile/investment-preferences', {
      focus_markets: focusMarkets.value,
      risk_preference: riskPreference.value,
    })
    router.push('/profile/me')
  } catch (e) {
    error.value = e.message || '保存失败'
  } finally {
    saving.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h2 class="text-lg font-bold text-foreground mb-4">编辑资料</h2>

    <div v-if="error" class="bg-red-50 text-destructive text-sm p-3 rounded-lg border border-red-200 mb-4">{{ error }}</div>

    <!-- Basic Info -->
    <div class="bg-card rounded-lg border border-border p-6 mb-6 space-y-4">
      <h3 class="font-semibold text-foreground">基本信息</h3>
      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">昵称</label>
        <input v-model="nickname" type="text" placeholder="昵称" maxlength="32"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>
      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">头像URL</label>
        <input v-model="avatarUrl" type="url" placeholder="https://..." maxlength="512"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>
      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">简介</label>
        <textarea v-model="bio" placeholder="介绍一下你的投资风格..." maxlength="500" rows="3"
          class="w-full px-3 py-2 rounded-lg border border-border bg-surface text-foreground text-sm outline-none resize-none focus:ring-2 focus:ring-primary focus:border-primary transition"
        ></textarea>
      </div>
      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">投资经验标签（逗号分隔）</label>
        <input v-model="experienceTags" type="text" placeholder="如: 价值投资, 量化交易, 技术分析"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary focus:border-primary transition" />
      </div>
      <button @click="onSaveBasic" :disabled="saving"
        class="px-6 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors cursor-pointer disabled:opacity-60 border-0">保存基本信息</button>
    </div>

    <!-- Investment Preferences -->
    <div class="bg-card rounded-lg border border-border p-6 space-y-4">
      <h3 class="font-semibold text-foreground">投资偏好</h3>
      <div>
        <label class="block text-sm font-medium text-foreground mb-2">关注市场</label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="m in marketOptions" :key="m.value" type="button"
            @click="toggleMarket(m.value)"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors cursor-pointer border"
            :class="focusMarkets.includes(m.value) ? 'bg-primary text-white border-primary' : 'bg-surface text-foreground border-border hover:bg-muted'"
          >{{ m.label }}</button>
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium text-foreground mb-1.5">风险偏好</label>
        <select v-model="riskPreference"
          class="w-full h-10 px-3 rounded-lg border border-border bg-surface text-foreground text-sm outline-none focus:ring-2 focus:ring-primary transition cursor-pointer">
          <option v-for="r in riskOptions" :key="r.value" :value="r.value">{{ r.label }}</option>
        </select>
      </div>
      <button @click="onSavePreferences" :disabled="saving"
        class="px-6 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors cursor-pointer disabled:opacity-60 border-0">保存投资偏好</button>
    </div>
  </div>
</template>
