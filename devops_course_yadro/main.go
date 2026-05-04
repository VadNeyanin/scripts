package main

import (
	"currency/application/pkg/config"
	"currency/application/pkg/server"
	"fmt"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		fmt.Printf("Error load config: %v\n", err)
		return
	}
	server.Start(cfg)
}
