<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'

const router = useRouter()
const questionnaire = ref(null)
const result = ref(null)
const answers = ref({})
const submitting = ref(false)
const loading = ref(true)
const error = ref('')

const riskLabels = { C1: '保守型（C1）', C2: '稳健型（C2）', C3: '平衡型（C3）', C4: '进取型（C4）', C5: '激进型（C5）' }

async function fetchData() {
  loading.value = true
  error.value = ''
  try {
    const [qData, rData] = await Promise.allSettled([
      api.get('/suitability/questionnaire'),
      api.get('/suitability/result'),
    ])
    questionnaire.value = qData.status === 'fulfilled' ? qData.value : null
    result.value = rData.status === 'fulfilled' ? rData.value : null
    if (result.value?.answers) {
      answers.value = { ...result.value.answers }
    }
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function onSubmit() {
  submitting.value = true
  error.value = ''
  try {
    result.value = await api.post('/suitability/submit', { answers: answers.value })
  } catch (e) {
    error.value = e.message || '提交失败'
  } finally {
    submitting.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h2 class="text-lg font-bold text-foreground mb-4">投资者适当性评估</h2>

    <div v-if="loading"><LoadingSpinner /></div>
    <div v-else-if="error"><ErrorMessage :message="error" @retry="fetchData" /></div>
    <template v-else-if="questionnaire">
      <!-- Current Result -->
      <div v-if="result?.completed" class="bg-card rounded-lg border border-border p-6 mb-6">
        <h3 class="font-semibold text-foreground mb-3">评估结果</h3>
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-full flex items-center justify-center text-lg font-bold text-white"
            :class="result.risk_level === 'C1' || result.risk_level === 'C2' ? 'bg-green-500' : result.risk_level === 'C3' ? 'bg-amber-500' : 'bg-red-500'"
          >{{ result.risk_level }}</div>
          <div>
            <p class="text-lg font-bold text-foreground">{{ riskLabels[result.risk_level] || result.risk_level }}</p>
            <p class="text-sm text-muted-foreground">得分: {{ result.score }} | 提交时间: {{ new Date(result.submitted_at).toLocaleDateString('zh-CN') }}</p>
          </div>
        </div>
      </div>

      <!-- Questionnaire -->
      <div class="bg-card rounded-lg border border-border p-6 space-y-6">
        <h3 class="font-semibold text-foreground">{{ questionnaire.title }}</h3>
        <div v-for="q in questionnaire.questions" :key="q.question_id" class="space-y-2">
          <p class="text-sm font-medium text-foreground">{{ q.title }}</p>
          <div class="flex gap-2 flex-wrap">
            <button
              v-for="opt in q.options" :key="opt.option_key" type="button"
              @click="answers[q.question_id] = opt.score"
              class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors cursor-pointer border"
              :class="answers[q.question_id] === opt.score ? 'bg-primary text-white border-primary' : 'bg-surface text-foreground border-border hover:bg-muted'"
            >{{ opt.option_key }}. {{ opt.title }}</button>
          </div>
        </div>
        <button @click="onSubmit" :disabled="submitting"
          class="px-6 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors cursor-pointer disabled:opacity-60 border-0">提交评估</button>
      </div>
    </template>
  </div>
</template>
