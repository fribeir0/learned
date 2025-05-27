package scanner

import (
    "fmt"
    "os/exec"
    "github.com/fribeiro/learned/projetos/api-go/model"
)

type Nmap struct {
    Services map[string]model.HostInfo
}

func (n *Nmap) Run(portMap map[string][]int) error {
    n.Services = make(map[string]model.HostInfo)

    for host, ports := range portMap {
        if len(ports) == 0 {
            continue
        }

        portStr := ""
        for i, port := range ports {
            if i > 0 {
                portStr += ","
            }
            portStr += fmt.Sprintf("%d", port)
        }

        cmd := exec.Command("nmap", "-sV", "-p", portStr, host)
        output, err := cmd.CombinedOutput()
		fmt.Println("Nmap output:", string(output))

        if err != nil {
            return err
        }
        // Aqui você pode adicionar o parsing da saída do Nmap para preencher n.Services
        // Por simplicidade, vamos apenas armazenar os ports abertos
        n.Services[host] = model.HostInfo{
            OpenPorts: ports,
            Services:  make(map[int]model.ServiceInfo),
        }

    }

    return nil
}
