<template>
  <div id="toast-container">
    <div
      v-for="t in toasts"
      :key="t.id"
      :class="['toast-message', t.type, { show: t.show }]"
    >{{ t.message }}</div>
  </div>
</template>

<script setup>
import { useToast } from '../composables/useToast.js'
const { toasts } = useToast()
</script>
