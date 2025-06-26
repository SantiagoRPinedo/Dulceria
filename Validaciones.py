
def validar_int(dato):
    try:
        entero = int(dato)
        return (1)
    except ValueError:
        print("nope")
        return ("Este dato no es un entero") 

def validar_float(dato):
    try:
        dec = float(dato)
        return (1)
    except ValueError:
        print("nope")
        return ("Este dato no es un decimal") 