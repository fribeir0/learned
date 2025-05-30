package main

import (
	"net/http"
	"github.com/gin-gonic/gin"
)

type album struct {
	ID string  `json:"id"`
	Title string  `json:"title"`
	Artist string  `json:"artist"`
	Price float64  `json:"price"`

}

var albums = []album{
	{ID: "1", Title: "Blue Train", Artist: "John Coltrane", Price: 56.90},
	{ID: "2", Title: "Red Train", Artist: "John Coltrane", Price: 96.90},
	{ID: "3", Title: "Yellow Train", Artist: "John Coltrane", Price: 126.90},
}

func main () {
	router := gin.Default()
	router.GET("/albums", getAlbums)
	router.POST("/albums, postAlbums")
	router.Run("localhost:1042")

}

func getAlbums (c *gin.Context) {
	c.IndentedJSON(http.StatusOK, albums)
}

func postAlbums (c *gin.Context) {
	var newAlbum album
	if err := c.BindJSON(&newAlbum); err != nil {
		return
	}
	albums = append(albums,newAlbum)
	c.IndentedJSON(http.StatusCreated, newAlbum) 
}

