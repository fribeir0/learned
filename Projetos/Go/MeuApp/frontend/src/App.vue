<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
    <div class="bg-white p-8 rounded-lg shadow-xl text-center">
      <h1 class="text-3xl font-bold mb-4">Meu Primeiro App!</h1>
      
      <input 
        v-model="nome" 
        placeholder="Digite seu nome" 
        class="border p-2 rounded mb-4"
      />
      
      <button 
        @click="cumprimentar" 
        class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Enviar
      </button>
      
      <p v-if="mensagem" class="mt-4 text-lg">{{ mensagem }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const nome = ref('')
const mensagem = ref('')

// Chama a função do backend Go
const cumprimentar = async () => {
  mensagem.value = await window.go.main.App.Cumprimentar(nome.value)
}
</script>