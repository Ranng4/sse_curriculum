<script setup>
defineProps({
  message: { type: String, default: '暂无数据' },
  icon: { type: String, default: '📭' },
})
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16 text-muted-foreground">
    <span class="text-4xl mb-3">{{ icon }}</span>
    <p class="text-sm">{{ message }}</p>
  </div>
</template>
