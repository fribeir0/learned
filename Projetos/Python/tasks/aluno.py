def check (aluno,nota):
    aprovados = {}
    reprovados = {}
    if nota >= 6:
        print ("Aluno Aprovado")
        aprovados[aluno] = nota 
        print (aprovados)
    else:
        print ("Aluno reprovado")
        reprovados[aluno] = nota
        print (reprovados)
if __name__ == "__main__" :
    aluno = input("Digite o nome do aluno")
    nota = int(input("Digite a nota do aluno"))
    check (aluno,nota)