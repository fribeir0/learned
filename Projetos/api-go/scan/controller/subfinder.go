package controller

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"time"
	"fmt"
	"path/filepath"
	"github.com/fribeiro/learned/projetos/api-go/utils"
)

func RunSubFinder (c * gin.Context) {
	type ScanRequest struct {
		Target string `json:"target" binding:"required"`
	}

	var req ScanRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error":"JSON Invalido ou target ausente"})
		return
	}

	target := req.Target
	
	output, err := utils.ExecuteCommand("subfinder", "-d", target, "-silent", "-json")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
	timestamp := time.Now().Format("2006-01-02-15-04-05")
	filePath := filepath.Join("scans", target, fmt.Sprintf("%s-subfinder.json",timestamp))

	if err := utils.SaveOutput(filePath, output); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":"subfinder scan completo",
		"target":target,
		"filepath":filePath,

	})
}