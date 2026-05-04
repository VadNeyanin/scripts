package xml_parser

import (
	"currency/application/pkg/services"
	"encoding/xml"
	"fmt"
	"io"
	"net/http"
	"reflect"
	"strings"

	"golang.org/x/text/encoding/charmap"
)

type ValInfo struct {
	XMLName xml.Name `xml:"Valuta"`
	Name    string   `xml:"name,attr"`
	Items   []Item   `xml:"Item"`
}

type Item struct {
	XMLName     xml.Name `xml:"Item"`
	ID          string   `xml:"ID,attr"`
	Name        string   `xml:"Name"`
	EngName     string   `xml:"EngName"`
	Nominal     string   `xml:"Nominal"`
	ParentCode  string   `xml:"ParentCode"`
	ISONumCode  string   `xml:"ISO_Num_Code"`
	ISOCharCode string   `xml:"ISO_Char_Code"`
}

type ValCurs struct {
	XMLName xml.Name `xml:"ValCurs"`
	Date    string   `xml:"Date,attr"`
	Name    string   `xml:"name,attr"`
	Valutes []Valute `xml:"Valute"`
}

type Valute struct {
	XMLName   xml.Name `xml:"Valute"`
	ID        string   `xml:"ID,attr"`
	NumCode   string   `xml:"NumCode"`
	CharCode  string   `xml:"CharCode"`
	Nominal   string   `xml:"Nominal"`
	Name      string   `xml:"Name"`
	Value     string   `xml:"Value"`
	VunitRate string   `xml:"VunitRate"`
}

func Parser[structure any](date string, ISO string) structure {
	var xml_f structure
	if date != "" {
		formatted_date := services.DateFormatting(date)
		xml_url := "https://www.cbr.ru/scripts/XML_daily.asp?date_req=" + formatted_date
		xml_f = XMLPreparation[structure](xml_url)
	} else {
		xml_url := "https://www.cbr.ru/scripts/XML_daily.asp"
		xml_f = XMLPreparation[structure](xml_url)
	}

	return xml_f
}

func XMLPreparation[structure any](URL string) structure {
	var valuta structure
	var remove_xml_tag string

	client := &http.Client{}
	req, err := http.NewRequest("GET", URL, nil)
	if err != nil {
		fmt.Printf("Error creating request: %v\n", err)
		return valuta
	}

	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
	req.Header.Set("Accept", "application/xml, text/xml, */*")
	req.Header.Set("Accept-Language", "ru-RU,ru;q=0.9,en;q=0.8")

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("Error making request: %v\n", err)
		return valuta
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("Server returned status: %s\n", resp.Status)
		return valuta
	}

	xmlData, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("Error reading response: %v\n", err)
		return valuta
	}

	decoder := charmap.Windows1251.NewDecoder()
	utf8Data, err := decoder.Bytes(xmlData)
	if err != nil {
		fmt.Printf("Encoding conversion error: %v\n", err)
		return valuta
	}

	xmlStr := string(utf8Data)
	if reflect.TypeOf(valuta).Name() == "ValInfo" {
		remove_xml_tag = "<Valuta"
	} else {
		remove_xml_tag = "<ValCurs"
	}
	if idx := strings.Index(xmlStr, remove_xml_tag); idx != -1 {
		xmlStr = xmlStr[idx:]
	}

	err = xml.Unmarshal([]byte(xmlStr), &valuta)
	if err != nil {
		fmt.Printf("Parsing error: %v\n", err)
	}

	return valuta
}
