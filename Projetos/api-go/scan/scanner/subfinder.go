package scanner

import (
	"encoding/json"
	"strings"
	"github.com/fribeiro/learned/projetos/api-go/utils"
)

type Subfinder struct{}

func (s Subfinder) Run(target string) ([]string, error) {
	output, err := utils.ExecuteCommand("subfinder", "-d", target, "-silent", "-json")
	if err != nil {
		return nil, err
	}

	lines := strings.Split(string(output), "\n")
	var subs []string

	for _, line := range lines {
		if strings.TrimSpace(line) == "" {
			continue
		}

		var r struct {
			Host string `json:"host"`
		}
		if err := json.Unmarshal([]byte(line), &r); err == nil {
			subs = append(subs, r.Host)
		}
	}

	return subs, nil
}
