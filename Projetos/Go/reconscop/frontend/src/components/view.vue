<template>
  <div>
    <input v-model="target" placeholder="Digite o IP">
    <button @click="scan">Scan</button>
    <pre>{{ result }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const target = ref('')
const result = ref('')

async function scan() {
  result.value = await window.backend.Scanner.RunScan(target.value)
}
</script>
