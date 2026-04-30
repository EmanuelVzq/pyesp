import string

TIPOS_ERROR = {
    "SIMBOLO_NO_RECONOCIDO": 1,
    "CADENA_SIN_CIERRE": 2,
    "COMILLA_DESAPAREADA": 3,
    "NUMERO_INVALIDO": 4,
    "OPERADOR_INVALIDO": 5,
    "DELIMITADOR_MAL_FORMADO": 6,
    "CARACTER_CONTROL_INVALIDO": 7,
    "SECUENCIA_ESCAPE_INVALIDA": 8
}

errores=[]

def agregar_error(categoria, caracter, posicion, descripcion, linea=None):
    errores.append({
        "tipo": "LEXICO",
        "categoria": categoria,
        "codigo_categoria": TIPOS_ERROR.get(categoria, 0),
        "caracter": caracter,
        "posicion": posicion,
        "linea": linea,
        "descripcion": descripcion
    })

def mostrar_errores():
    if errores:
        print("\n")
        print("PILA DE ERRORES LEXICOS")
        for idx, error in enumerate(errores, 1):
            print(f"\nError #{idx}:")
            print(f"  Tipo:       {error['tipo']}")
            print(f"  Categoría:  {error['categoria']} (código: {error['codigo_categoria']})")
            print(f"  Carácter:   '{error['caracter']}'")
            print(f"  Posición:   {error['posicion']}")
            if error['linea']:
                print(f"  Línea:      {error['linea']}")
            print(f"  Descripción: {error['descripcion']}")
        print("\n")

def limpiar_errores():
    global errores
    errores = []

def tipo_char(c):
    if c == '"':
        return "comilla_doble"
    elif c == "'":
        return "comilla_simple"
    elif c.isalpha() or c == "_":
        return "letra"
    elif c.isdigit():
        return "digito"
    elif c == "+":
        return "op_suma"
    elif c == "-":
        return "op_resta"
    elif c == "*":
        return "op_mul"
    elif c == "/":
        return "op_div"
    elif c == "%":
        return "op_mod"
    elif c in "=<>":
        return "op_comp"
    elif c in "(){}[],:.;":
        return "delim"
    elif c == " ":
        return "espacio"
    elif c == "\t":
        return "tab"
    elif c == "\n":
        return "salto_linea"
    elif c.isspace():
        return "otro_espacio"
    else:
        return "error"

palabras_reservadas = {
    "si", "sino", "sino_si", "mientras", "para", "en",
    "repetir_hasta", "romper", "continuar", "pasar",
    "funcion", "retorna", "clase", "hereda", "esto",
    "super", "anonima", "intentar", "excepto", "finalmente",
    "lanzar", "afirmar", "asincrono", "esperar",
    "importar", "desde", "como",
    "y", "o", "no", "es", "no_es",
    "verdadero", "falso", "nulo",
    "global", "local", "coincidir", "caso",
    "producir", "eliminar", "con"
}


class AFD:
    def __init__(self, nombre, estados, estado_inicial, estados_finales, transiciones):
        self.nombre = nombre
        self.estados = estados
        self.estado_inicial = estado_inicial
        self.estados_finales = estados_finales
        self.transiciones = transiciones
        self.estado_actual = estado_inicial

    def reiniciar(self):
        self.estado_actual = self.estado_inicial

    def procesar(self, simbolo, c, i):
        nuevo_estado = self.transiciones.get(
            (self.estado_actual, simbolo),
            "dead"
        )

        if nuevo_estado == "dead" and simbolo == "error":
            agregar_error(
                "SIMBOLO_NO_RECONOCIDO",
                c,
                i,
                "símbolo no reconocido en el lenguaje"
            )

        self.estado_actual = nuevo_estado
        return self.estado_actual

    def es_aceptado(self):
        return self.estado_actual in self.estados_finales


def afd_4_espacios():
    estados = {"q0", "q1", "q2", "q3", "q4", "dead"}
    estado_inicial = "q0"
    estados_finales = {"q4"}

    transiciones = {
        ("q0", "espacio"): "q1",
        ("q0", "otro"): "q0",

        ("q1", "espacio"): "q2",
        ("q1", "otro"): "q0",

        ("q2", "espacio"): "q3",
        ("q2", "otro"): "q0",

        ("q3", "espacio"): "q4",
        ("q3", "otro"): "q0",

        ("q4", "espacio"): "dead",
        ("q4", "otro"): "q0",

        ("dead", "espacio"): "dead",
        ("dead", "otro"): "dead",
    }

    return AFD("4_ESPACIOS", estados, estado_inicial, estados_finales, transiciones)


def tipo_simbolo_string(c):
    if c == '"':
        return "comilla_doble"
    elif c== "'":
        return "comilla_simple"
    else:
        return "contenido"


def afd_cadenas():
    estados = {"q0", "q1", "q2", "q3", "q4", "dead"}
    estado_inicial = "q0"
    estados_finales = {"q2", "q4"}

    transiciones = {
        ("q0", "comilla_doble"): "q1",
        ("q1", "contenido"): "q1",
        ("q1", "comilla_doble"): "q2",

        ("q0", "comilla_simple"): "q3",
        ("q3", "contenido"): "q3",
        ("q3", "comilla_simple"): "q4",
    }

    return AFD("CADENAS", estados, estado_inicial, estados_finales, transiciones)


def afd_operadores():
    estados = {"q0","q1","q2","q3","q4","q5"}
    estado_inicial = "q0"
    estados_finales = {"q1","q2","q3","q4","q5"}

    transiciones = {
        ("q0","op_suma"):"q1",
        ("q0","op_resta"):"q2",
        ("q0","op_mul"):"q3",
        ("q0","op_div"):"q4",
        ("q0","op_mod"):"q5",
    }

    return AFD("OPERADORES", estados, estado_inicial, estados_finales, transiciones)

def ejecutar_cadenas(texto):
    limpiar_errores()
    afd = afd_cadenas()

    for i, c in enumerate(texto):
        simbolo = tipo_simbolo_string(c)
        afd.procesar(simbolo, c, i)

    if afd.es_aceptado():
        print(f"'{texto}' → Cadena valida")
    else:
        print(f"'{texto}' → Cadena invalida")
        if not errores:
            if texto and texto[0] not in ('"', "'"):
                agregar_error(
                    "CADENA_SIN_CIERRE",
                    texto[0],
                    0,
                    "la cadena no comienza con comilla"
                )
            else:
                agregar_error(
                    "CADENA_SIN_CIERRE",
                    texto[-1] if texto else "",
                    len(texto)-1 if texto else 0,
                    "la cadena no cierra correctamente"
                )
    
    mostrar_errores()

if __name__ == "__main__":
    ejecutar_cadenas('"hola mundo"')
    ejecutar_cadenas("'hola@'")
    ejecutar_cadenas("'hola")

def ejecutar_operadores(texto):
    limpiar_errores()
    afd = afd_operadores()

    for i, c in enumerate(texto):
        simbolo = tipo_char(c)    
        afd.procesar(simbolo, c, i)

    if afd.es_aceptado():
        print(f"'{texto}' → Operador valido")
    else:
        print(f"'{texto}' → Operador invalido")
        if not errores:
            agregar_error(
                "OPERADOR_INVALIDO",
                texto,
                0,
                f"'{texto}' no es un operador valido (+, -, *, /, %)"
            )
    
    mostrar_errores()

if __name__ == "__main__":
    ejecutar_operadores("+")
    ejecutar_operadores("-")
    ejecutar_operadores("*")
    ejecutar_operadores("/")
    ejecutar_operadores("%")
    ejecutar_operadores("a")          

def ejecutar_4_espacios(texto):
    limpiar_errores()
    afd = afd_4_espacios()

    for i, c in enumerate(texto):
        simbolo = "espacio" if c == " " else "otro"
        afd.procesar(simbolo, c, i)

    if afd.es_aceptado():
        print(f"'{texto}' → Indentación de 4 espacios valida")
    else:
        print(f"'{texto}' → Indentación invalida")
        if not errores:
            espacios = len(texto)
            agregar_error(
                "DELIMITADOR_MAL_FORMADO",
                texto if texto else "(vacio)",
                0,
                f"se esperaban 4 espacios, se encontraron {espacios}"
            )
    
    mostrar_errores()

if __name__ == "__main__":
    ejecutar_4_espacios("    ")  
    ejecutar_4_espacios("   ")        
    ejecutar_4_espacios("     ")      
    ejecutar_4_espacios("\t")           