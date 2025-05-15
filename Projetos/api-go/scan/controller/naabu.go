package controller

import (
	"fmt"
	"net/http"
	"path/filepath"
	"time"

	"github.com/fribeiro/learned/projetos/api-go/utils"
	"github.com/gin-gonic/gin"
)

func RunNaabu(c *gin.Context) {
	type ScanRequest struct {
		Target string `json:"target" binding:"required"`
	}

	var req ScanRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Json invalido ou target ausente"})
		return
	}

	target := req.Target

	output, err := utils.ExecuteCommand("naabu", "-host", target, "-json", "-silent")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	timestamp := time.Now().Format("2006-01-02-15-04-05")
	filePath := filepath.Join("scans", target, fmt.Sprintf("%s-subfinder.json", timestamp))

	if err := utils.SaveOutput(filePath, output); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":  "naabu feito com sucesso",
		"target":   target,
		"filepath": filePath,
	})
}
