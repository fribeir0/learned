package calc

import "errors"

func Dividir(x, y int) (int, error) {
	if y == 0 {
		return 0, errors.New("Este valor esta incorreto,nenhum numero da pra ser divido por ZERO")
	}
	return (x / y) , nil
}

func Soma (x,y int) (int, error) {
	
	if y <= 0 {
		return 0, errors.New("valores negativos nao pode")
	}
	return (x + y) , nil
}

func Subtrair (x,y int) (int,error) {

	if x == y {
		return 0, errors.New("Os valores sao iguais")
	}
	return (x - y),nil
}

func Multiplic (x,y int) (int,error) {
	if y <= 0 {
		return 0, errors.New("Valores multiplicados por zero e 0")
	}
	return (x*y) , nil
}