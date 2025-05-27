package model

type HostInfo struct {
    OpenPorts []int
    Services  map[int]ServiceInfo
}

type ServiceInfo struct {
    Service string
    Version string
}

type ReconResult struct {
    Target     string
    Subdomains []string
    Hosts      map[string]HostInfo
}
