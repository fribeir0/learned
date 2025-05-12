package main  // Mesmo pacote que main.go

import (
	"context"
)

// App é a struct principal com suas funções e dados
type App struct {
	ctx   context.Context
	Items []string  // Exemplo: lista para armazenar itens
}

// Função executada ao iniciar o app
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
	a.Items = []string{}  // Inicializa a lista vazia
}

// Adiciona um item à lista (chamada pelo frontend)
func (a *App) AddItem(item string) {
	a.Items = append(a.Items, item)
}

// Retorna todos os itens (chamada pelo frontend)
func (a *App) GetItems() []string {
	return a.Items
}