#creando una lista ( se pueden modificar)
lista=["Gonzalo martin","soy gonzalo autor de MANITO AI",True,1.70] 
print(lista)
#creando una tupla ( no se pueden modificar)
tupla=("Gonzalo martin","soy gonzalo autor de MANITO AI",True,1.70)
print(tupla)
#esto es valido 
lista[3]="maquinola"
#esto no es valido
#tupla[3]="maquinola"
print(lista[3])
#creando un conjunto set ( no se accede a datos por indice, no almacena datos duplicados)
conjunto={"Gonzalo martin","soy gonzalo autor de MANITO AI",True,1.70}
print(conjunto)
conjunto
#creando un diccionari (dict)
diccionario ={'nombre':"MANITO AI",
              'estoy emocionado':True,
              'propisito':"automatizar_respuestas",
              'dato_duplicado':"MANITO AI",
              'altura':1.70,}
print(diccionario['altura'] + 2)