package utils

import (
	"encoding/json"
	"os"

	"github.com/fribeiro/learned/projetos/api-go/model"
)

func SaveReconResult(result model.ReconResult, filename string) error {
	data, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(filename, data, 0644)
}
