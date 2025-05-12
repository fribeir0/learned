<template>
  <div class="p-4">
    <h1 class="text-2xl mb-4">Scanner de Rede</h1>

    <input v-model="target" placeholder="Ex: 192.168.0.1" class="border p-2 w-full mb-4" />

    <button @click="scan" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
      Escanear
    </button>

    <pre class="bg-gray-100 p-4 mt-4 overflow-auto max-h-[400px] whitespace-pre-wrap">
      {{ result }}
    </pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RunScan } from '../../wailsjs/go/main/App'

const target = ref('')
const result = ref('')

const scan = async () => {
  result.value = '🔍 Escaneando...'
  try {
    const res = await RunScan(target.value)
    result.value = res
  } catch (err) {
    result.value = '❌ Erro: ' + err.message
  }
}
</script>
