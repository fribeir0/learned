package utils

import (
	"os"
	"path/filepath"
)

func SaveOutput (path string, data[]byte) error {
	dir := filepath.Dir(path)

	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}

	return os.WriteFile(path, data, 0644)
}