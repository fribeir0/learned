package scan

import (
	"encoding/json"
	"net/http"
	"os/exec"

)

type Result struct {
	Output string `json:"output"`
	
}