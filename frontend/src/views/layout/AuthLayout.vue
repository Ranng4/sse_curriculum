<template>
  <div class="min-h-screen bg-surface flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <router-link to="/" class="inline-flex items-center gap-2 text-primary no-underline">
          <span class="text-3xl font-bold tracking-tight">融智论坛</span>
        </router-link>
        <p class="text-muted-foreground mt-2">股票基金投资交流平台</p>
      </div>
      <div class="bg-card rounded-xl shadow-sm border border-border p-6">
        <router-view />
      </div>
    </div>
  </div>
</template>
