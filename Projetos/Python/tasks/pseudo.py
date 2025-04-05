estoque = {}
option = 0

while option != 3:
    print (f"option 1 -  Adicionar produto")
    print (f"option 2 -  Consultar produto")
    print (f"option 3 -  Sair")
    option = int(input())
    if option == 1:
        print (f"Digite o nome do produto")
        nomeProduto = input("")
        print (f"Digite a quantidade")
        quantidade = input("")
        if (nomeProduto in estoque.keys()):
            print ("Adicionando estoque")
            estoque.update({nomeProduto:quantidade})
        else :
            print ("Criando o produto e adicionando no estoque")
            estoque[nomeProduto] = quantidade
            print (estoque[nomeProduto])

    if option == 2:
        print (f"Digite o produto a ser consultado")
        nomeProduto = input("")
        if (nomeProduto in estoque.keys()):
            print (f"O produto:",nomeProduto)
            print ("Tem de estoque:")
            print (estoque[nomeProduto])
        else:
            print ("produto nao encontrado")
    elif option == 3:
        print("saindo do sistemas")
    else:
        print ("opcao invalida")