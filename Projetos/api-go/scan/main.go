package main

import (
    "net/http"
    "github.com/fribeiro/learned/projetos/api-go/scanner"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    r.POST("/scan/full", func(c *gin.Context) {
        var req struct {
            Target string `json:"target" binding:"required"`
        }

        if err := c.ShouldBindJSON(&req); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": "Target inválido"})
            return
        }

        result, err := scanner.RunScan(req.Target)
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
            return
        }

        c.JSON(http.StatusOK, result)
    })

    r.Run(":8080")
}
