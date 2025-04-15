package backend

import (
	"os/exec"
)

type Scanner struct{}

func NewScanner() *Scanner {
	return &Scanner{}
}

func (s *Scanner) RunScan(ip string) string {
	cmd := exec.Command("nmap", "-sV", ip)
	out, err := cmd.CombinedOutput()
	if err != nil {
		return "Erro ao rodar Nmap: " + err.Error()
	}
	return string(out)
}
