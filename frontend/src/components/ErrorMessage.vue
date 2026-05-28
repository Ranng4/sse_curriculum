<script setup>
defineProps({
  message: { type: String, default: '加载失败' },
})

const emit = defineEmits(['retry'])
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 text-muted-foreground">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mb-3 text-destructive/70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L2.992 16.5c-.77.833.192 2.5 1.732 2.5z" />
    </svg>
    <p class="text-sm mb-3">{{ message }}</p>
    <button
      v-if="emit" @click="$emit('retry')"
      class="px-4 py-1.5 rounded-md bg-primary text-white text-sm hover:bg-primary-dark transition-colors cursor-pointer border-0"
    >
      重试
    </button>
  </div>
</template>
