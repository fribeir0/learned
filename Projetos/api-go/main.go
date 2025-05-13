package main

import (
	"net/http"
	"api-go/scan"
)

func main() {
	subfinder.HandleFunc("/run, subfinder.HttpxHandler")
	http.ListenAndServe(":8080",nil)
}