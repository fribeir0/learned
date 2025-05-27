package scanner

import "github.com/fribeiro/learned/projetos/api-go/model"

type ScanContext struct {
    Target     string
    Subdomains []string
    PortMap    map[string][]int
    Services   map[string]model.HostInfo
}
