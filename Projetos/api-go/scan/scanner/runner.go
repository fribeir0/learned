package scanner

import (
    "github.com/fribeiro/learned/projetos/api-go/model"
)

func RunScan(target string) (model.ReconResult, error) {
    ctx := &ScanContext{
        Target:   target,
        PortMap:  make(map[string][]int),
        Services: make(map[string]model.HostInfo),
    }

    // Subfinder
    subfinder := Subfinder{}
    subs, err := subfinder.Run(target)
    if err != nil {
        return model.ReconResult{}, err
    }
    ctx.Subdomains = subs

    // Naabu
    naabu := &Naabu{}
    err = naabu.RunFromList(ctx.Subdomains)
    if err != nil {
        return model.ReconResult{}, err
    }
    ctx.PortMap = naabu.PortMap

    // Nmap
    nmap := &Nmap{}
    err = nmap.Run(ctx.PortMap)
    if err != nil {
        return model.ReconResult{}, err
    }
    ctx.Services = nmap.Services

    return model.ReconResult{
        Target:     ctx.Target,
        Subdomains: ctx.Subdomains,
        Hosts:      ctx.Services,
    }, nil
}
