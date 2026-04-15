package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
)

func readArrayFromFile(filename string) ([]string, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var array []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		array = append(array, scanner.Text())
	}
	return array, scanner.Err()
}

func createPackagesList() {
	cmd := exec.Command("bash", "-c", "dpkg-query -f '${binary:Package}\n' -W > /tmp/pkgs.txt")
	if err := cmd.Run(); err != nil {
		log.Fatal(err)
	}
}

func lostPackages(base_pkgs []string, host_pkgs []string) bool {
	present := make(map[string]bool)
	for _, item := range host_pkgs {
		present[item] = true
	}

	missing := []string{}
	for _, item := range base_pkgs {
		if !present[item] {
			missing = append(missing, item)
		}
	}

	if len(missing) == 0 {
		fmt.Println("Все элементы базового массива присутствуют")
		return false
	}

	content := strings.Join(missing, "\n")
	err := os.WriteFile("/tmp/missing_packages.txt", []byte(content), 0644)
	if err != nil {
		fmt.Printf("Ошибка записи файла: %v\n", err)
		return true
	}
	
	fmt.Println("Отсутствующие элементы:")
	for _, item := range missing {
		fmt.Println("-", item)
	}
	
	return true
}

func main() {
	lines, err := readArrayFromFile("/tmp/base.txt")
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Количество базовых пакетов:", len(lines))
	
	createPackagesList()
	packages, err := readArrayFromFile("/tmp/pkgs.txt")
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Количество пакетов на машине:", len(packages))
	
	hasMissing := lostPackages(lines, packages)
	if hasMissing {
		os.Exit(1)
	}
}
