def table (number) :
    for i in range (10):
        i += 1
        result = int(number * i)
        print (f"{number} * {i} = {result}") 

if __name__ == "__main__" :
    table(8)