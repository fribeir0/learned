package scanner

import (
    "os"
    "strconv"
    "strings"
    "github.com/fribeiro/learned/projetos/api-go/utils"
)

type Naabu struct {
    PortMap map[string][]int
}

func (n *Naabu) RunFromList(subs []string) error {
    n.PortMap = make(map[string][]int)

    if len(subs) == 0 {
        return nil
    }

    tmpFile := "scans/naabu_input.txt"
    content := []byte(strings.Join(subs, "\n"))
    if err := os.WriteFile(tmpFile, content, 0644); err != nil {
        return err
    }

    output, err := utils.ExecuteCommand("naabu", "-list", tmpFile, "-silent")
    if err != nil {
        return err
    }

    lines := strings.Split(string(output), "\n")
    for _, line := range lines {
        parts := strings.Split(line, ":")
        if len(parts) == 2 {
            port, _ := strconv.Atoi(parts[1])
            n.PortMap[parts[0]] = append(n.PortMap[parts[0]], port)
        }
    }

    return nil
}
