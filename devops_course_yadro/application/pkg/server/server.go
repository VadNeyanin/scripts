package server

import (
	"currency/application/pkg/config"
	"currency/application/pkg/xml_parser"
	"encoding/json"
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/go-chi/chi/v5"
)

type Response struct {
	Data    CurrencyData `json:"data"`
	Service string       `json:"service"`
}

type CurrencyData map[string]float64

type InfoResponse struct {
	Version string `json:"version"`
	Service string `json:"service"`
	Author  string `json:"author"`
}

func Start(cfg *config.Config) {
	r := chi.NewRouter()

	r.Get("/info", func(w http.ResponseWriter, r *http.Request) {
		handleInfo(w, cfg)
	})
	r.Get("/info/currency", handleCurrency)
	
	port := ":" + config.GetPort()
	
	server := &http.Server{
		Addr:         port,
		Handler:      r,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}
	
	log.Printf("Starting server on port %s", port)
	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

func handleInfo(w http.ResponseWriter, cfg *config.Config) {
	response := InfoResponse{
		Version: cfg.Version,
		Service: cfg.Service,
		Author:  cfg.Author,
	}
	w.Header().Set("Content-Type", "application/json")
	
	if err := json.NewEncoder(w).Encode(response); err != nil {
		log.Printf("Error encoding info response: %v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
}

func handleCurrency(w http.ResponseWriter, r *http.Request) {
	date := r.URL.Query().Get("date")
	ISO := r.URL.Query().Get("currency")
	
	if date == "" {
		http.Error(w, "Missing required parameter: date", http.StatusBadRequest)
		return
	}
	
	vc := xml_parser.Parser[*xml_parser.ValCurs](date, ISO)
	
	if vc == nil {
		http.Error(w, "Failed to parse currency data", http.StatusInternalServerError)
		return
	}
	
	response := ConvertToResponse(vc, ISO)
	w.Header().Set("Content-Type", "application/json")
	
	if err := json.NewEncoder(w).Encode(response); err != nil {
		log.Printf("Error encoding currency response: %v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
}

func ConvertToResponse(vc *xml_parser.ValCurs, targetCurrency string) Response {
	response := Response{
		Data:    make(CurrencyData),
		Service: "currency",
	}

	if vc == nil {
		return response
	}

	for _, valute := range vc.Valutes {
		if targetCurrency != "" && valute.CharCode != targetCurrency {
			continue
		}

		valueStr := strings.Replace(valute.Value, ",", ".", -1)
		
		value, err := strconv.ParseFloat(valueStr, 64)
		if err != nil {
			log.Printf("Error parsing currency value %s for %s: %v", valueStr, valute.CharCode, err)
			continue
		}
		
		response.Data[valute.CharCode] = value

		if targetCurrency != "" {
			break
		}
	}

	return response
}