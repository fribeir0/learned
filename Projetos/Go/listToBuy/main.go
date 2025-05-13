package main

import "github.com/wailsapp/wails/v2/pkg/application"

func main() {
	// Cria uma instância do App
	app := application.New(&App{})

	// Executa o app
	app.Run()
}