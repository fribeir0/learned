<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Scanner Nmap</h1>

    <input
      v-model="target"
      placeholder="Digite o IP ou domínio"
      class="border p-2 rounded w-full mb-4"
    />

    <button
      @click="scan"
      class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
    >
      Escanear
    </button>

    <pre class="mt-4 p-2 bg-gray-100 rounded whitespace-pre-wrap">
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
  result.value = '⏳ Escaneando...'
  try {
    const output = await RunScan(target.value)
    result.value = output
  } catch (err) {
    result.value = '❌ Erro: ' + err.message
  }
}
</script>
