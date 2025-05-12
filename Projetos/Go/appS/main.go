package main

import (
	"context"
	"os/exec"
)

type App struct{}

func NewApp() *App {
	return &App{}
}

// Função chamada pelo Vue para rodar o Nmap
func (a *App) RunScan(ctx context.Context, target string) (string, error) {
	cmd := exec.Command("nmap", "-sV", target)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return "", err
	}
	return string(output), nil
}
