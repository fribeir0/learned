package main

import (
	"reconscope/backend"
	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/options"
)

func main() {
	app := backend.NewScanner()

	err := wails.Run(&options.App{
		Title:  "ReconScope",
		Width:  1024,
		Height: 768,
		Bind: []interface{}{
			app,
		},
	})
	if err != nil {
		panic(err)
	}
}
