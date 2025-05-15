package main

import (
	"github.com/gin-gonic/gin"
	"github.com/fribeiro/learned/projetos/api-go/controller"
)

func main () {
	router := gin.Default()
	router.POST ("/scan/subfinder" , controller.RunSubFinder)
	router.POST ("/scan/naabu", controller.RunNaabu)
	router.Run("localhost:1421")
}



