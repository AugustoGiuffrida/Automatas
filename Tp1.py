#Dado el alfabeto Σ={a,b,c,d,0,1,2,3,4}, obtenga dos cadenas, x e  y, del alfabeto dado, 
#indique la longitud de cada cadena y aplique las siguientes operaciones:
#concatenación de x e y, las potencias x0, x1, y2, y3, xx,yx.

def ejercicio1(x:list,y:list):
    x_len = len(x)
    y_len = len(y)

    #operaciones
    #x0
    x0 = []
    #x1
    x1 = x
    #y2
    y2 = y + y
    #y3
    y3 = y2 + y
    #xx
    xx = x + x
    #xy
    xy = x + y
    print (f'|x|={x_len}, \n|y|={y_len}, \nx0={x0}, \nx1={x1}, \ny2={y2}, \ny3={y3}, \nxx={xx}, \nxy={xy}')


#Dados los siguientes lenguajes, A, el conjunto de letras y B, el conjunto de dígitos, realice
#las siguientes operaciones B ∪ A, A ∩ B, A.B, A3, B 2, B 0, A *, B (A ∩ B)*.
def ejercicio2(A,B):

    BuA = B + A

    AnB = []
    for i in A:
        if i in B:
            AnB.append(i)
    print(AnB)
    

if __name__ == '__main__':
    #ejercicio1(['a','b','c',1,2,3],['b',4])
    ejercicio2([1,2,3],[3,4,5,1])
