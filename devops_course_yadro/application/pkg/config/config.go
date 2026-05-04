package config

import (
	"os"
	"strconv"
	"strings"

	"github.com/joho/godotenv"
)

type Config struct {
	Version string
	Service string
	Author  string
}

func Load() (*Config, error) {
	envMap, err := godotenv.Read()
	if err != nil {
		envMap["version"] = "0.1.0"
		envMap["service"] = "currency"
		envMap["author"] = "v.neyanin"
	}
	return &Config{
		Version: envMap["version"],
		Service: envMap["service"],
		Author:  envMap["author"],
	}, nil
}
func GetPort() string {
	portStr := os.Getenv("PORT")

	if portStr == "" {
		println("PORT пустая, используем по умолчанию: 8000")
		return "8000"
	}

	portStr = strings.TrimSpace(portStr)
	if portStr == "" {
		println("PORT пустой после удаления пробелов, используем 8000")
		return "8000"
	}

	port, err := strconv.Atoi(portStr)
	if err != nil {
		println("PORT содержит не только цифры (\"", portStr, "\"), используем 8000")
		return "8000"
	}

	if port < 1 || port > 65535 {
		println("PORT=", port, " вне допустимого диапазона (1-65535), используем 8000")
		return "8000"
	}

	return portStr
}
