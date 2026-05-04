package services

import (
	"strings"
)

func DateFormatting(date string) string {
	parts := strings.Split(date, "-")
	formatted_date := strings.Join([]string{parts[2], parts[1], parts[0]}, "/")
	return formatted_date
}
