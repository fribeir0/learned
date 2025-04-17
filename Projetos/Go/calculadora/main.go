package main

import (
	"fmt"
	"project/calc"
)

func main() {
	num1 := 26
	num2 := 26

	result,err := calc.Dividir(num1, num2)

	if err != nil {
		fmt.Println("Erro Divisão:", err)
	}
	fmt.Println(result)

	resultSoma,err := calc.Soma (num1,num2)
	if err != nil {
		fmt.Println("Error Soma:", err)
	}
	fmt.Println(resultSoma)

	resultSub,err := calc.Subtrair(num1,num2)
	if err != nil {
		fmt.Println("Error subtraçao", err)
	}
	fmt.Println(resultSub)

	resultMultiplic,err := calc.Multiplic(num1,num2)

	if err != nil {
		fmt.Println("Error Multiplicacao", err)
	}
	fmt.Println(resultMultiplic)

}
