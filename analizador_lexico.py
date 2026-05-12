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

errores = []


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
    elif c in "<>":
        return "op_comp"
    elif c in "=":
        return "igual"
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
    "importar", "desde", "como", "imprimir",
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
        ("q0", "espacio"): "q1",  ("q0", "otro"): "q0",
        ("q1", "espacio"): "q2",  ("q1", "otro"): "q0",
        ("q2", "espacio"): "q3",  ("q2", "otro"): "q0",
        ("q3", "espacio"): "q4",  ("q3", "otro"): "q0",
        ("q4", "espacio"): "dead",("q4", "otro"): "q0",
        ("dead", "espacio"): "dead", ("dead", "otro"): "dead",
    }
    return AFD("4_ESPACIOS", estados, estado_inicial, estados_finales, transiciones)


def tipo_simbolo_string(c):
    if c == '"':
        return "comilla_doble"
    elif c == "'":
        return "comilla_simple"
    elif c == "\n":
        return "salto"
    else:
        return "contenido"


def tipo_simbolo_string_variable(texto, pos):
    if pos >= len(texto):
        return "error", 0 
    c = texto[pos]
    if c == '"':
        return "comilla_doble", 1
    elif c == "'":
        return "comilla_simple", 1
    elif c == '\n':
        return "salto", 1
    elif c == '\r':
        return "contenido", 1
    elif c == '\t':
        return "contenido", 1
    else:
        return "contenido", 1


def afd_cadenas():
    estados = {"q0", "q1", "q2", "q3", "q4", "dead"}
    estado_inicial = "q0"
    estados_finales = {"q2", "q4"}
    transiciones = {
        ("q0", "comilla_doble"): "q1",
        ("q1", "contenido"):     "q1",
        ("q1", "salto"):         "q1",
        ("q1", "comilla_doble"): "q2",
        ("q0", "comilla_simple"): "q3",
        ("q3", "contenido"):      "q3",
        ("q3", "salto"):          "q3",
        ("q3", "comilla_simple"): "q4",
    }
    return AFD("CADENAS", estados, estado_inicial, estados_finales, transiciones)


def afd_operadores():
    estados = {"q0", "q1", "q2", "q3", "q4", "q5", "q6"}
    estado_inicial = "q0"
    estados_finales = {"q1", "q2", "q3", "q4", "q5", "q6"}
    transiciones = {
        ("q0", "op_suma"):  "q1",
        ("q0", "op_resta"): "q2",
        ("q0", "op_mul"):   "q3",
        ("q0", "op_div"):   "q4",
        ("q0", "op_mod"):   "q5",
        ("q0", "igual"):    "q6",
    }
    return AFD("OPERADORES", estados, estado_inicial, estados_finales, transiciones)


def afd_palabras_reservadas():
    estados = {"q0", "q1", "q2", "dead"}
    estado_inicial = "q0"
    estados_finales = {"q1", "q2"}
    transiciones = {
        ("q0", "palabra_reservada"): "q1",
        ("q1", "espacio"):           "q2",
    }
    return AFD("PALABRAS_RESERVADAS", estados, estado_inicial, estados_finales, transiciones)


def tipo_simbolo_pr(token):
    if token in palabras_reservadas:
        return "palabra_reservada"
    return "otro"


def ejecutar_palabras_reservadas(texto):
    limpiar_errores()
    afd = afd_palabras_reservadas()

    texto_strip = texto.rstrip(" ")
    tiene_espacio = len(texto) > len(texto_strip)

    simbolo = tipo_simbolo_pr(texto_strip)
    afd.procesar(simbolo, texto_strip, 0)

    if tiene_espacio and afd.estado_actual == "q1":
        afd.procesar("espacio", " ", len(texto_strip))

    if afd.es_aceptado():
        print(f"'{texto}' → Palabra reservada válida")
    else:
        print(f"'{texto}' → NO es una palabra reservada válida")
        if not errores:
            agregar_error(
                "SIMBOLO_NO_RECONOCIDO",
                texto_strip,
                0,
                f"'{texto_strip}' no pertenece al conjunto de palabras reservadas"
            )
    mostrar_errores()


def afd_variables():

    estados = {"q0", "q1", "q2", "dead"}
    estado_inicial = "q0"
    estados_finales = {"q1", "q2"}
    transiciones = {
        ("q0", "letra"):        "q1",
        ("q1", "letra"):        "q1",
        ("q1", "digito"):       "q1",
        ("q1", "espacio"):      "q2",
    }
    return AFD("VARIABLES", estados, estado_inicial, estados_finales, transiciones)


def tipo_simbolo_var(c):
    if c.isalpha() or c == "_":
        return "letra"
    elif c.isdigit():
        return "digito"
    elif c == " ":
        return "espacio"
    return "otro"


def ejecutar_variables(texto):
    limpiar_errores()
    afd = afd_variables()

    for i, c in enumerate(texto):
        simbolo = tipo_simbolo_var(c)
        afd.procesar(simbolo, c, i)

    texto_strip = texto.strip()
    es_reservada = texto_strip in palabras_reservadas

    if afd.es_aceptado() and not es_reservada:
        print(f"'{texto}' → Identificador/Variable valido")
    else:
        if es_reservada:
            print(f"'{texto}' → INVÁLIDO: es una palabra reservada, no un identificador")
            agregar_error(
                "SIMBOLO_NO_RECONOCIDO",
                texto_strip,
                0,
                f"'{texto_strip}' es palabra reservada y no puede usarse como identificador"
            )
        else:
            print(f"'{texto}' → Identificador/Variable inválido")
            if not errores:
                agregar_error(
                    "SIMBOLO_NO_RECONOCIDO",
                    texto[0] if texto else "",
                    0,
                    "el identificador contiene caracteres inválidos o inicia con dígito"
                )
    mostrar_errores()


def afd_numeros():
    estados = {"q0", "q1", "q2", "q3", "q_error", "dead"}
    estado_inicial = "q0"
    estados_finales = {"q1", "q3"}
    transiciones = {
        ("q0", "digito"):      "q1",
        ("q1", "digito"):      "q1",
        ("q1", "punto"):       "q2",
        ("q1", "letra"):       "q_error",
        ("q2", "digito"):      "q3",
        ("q3", "digito"):      "q3",
        ("q3", "letra"):       "q_error",
        ("q_error", "digito"): "q_error",
        ("q_error", "letra"):  "q_error",
    }
    return AFD("NUMEROS", estados, estado_inicial, estados_finales, transiciones)


def tipo_simbolo_num(c):
    if c.isdigit():
        return "digito"
    elif c == ".":
        return "punto"
    elif c.isalpha() or c == "_":
        return "letra"
    return "otro"


def ejecutar_numeros(texto):
    limpiar_errores()
    afd = afd_numeros()

    for i, c in enumerate(texto):
        simbolo = tipo_simbolo_num(c)
        afd.procesar(simbolo, c, i)

    if afd.es_aceptado():
        tipo = "Número real" if "." in texto else "Número entero"
        print(f"'{texto}' → {tipo} válido")
    else:
        print(f"'{texto}' → Número inválido")
        if not errores:
            agregar_error(
                "NUMERO_INVALIDO",
                texto,
                0,
                f"'{texto}' no es un número entero ni real válido"
            )
    mostrar_errores()


def afd_comentarios():
    estados = {"q0", "q1", "q2", "q3", "q4", "q5", "q6", "dead"}
    estado_inicial = "q0"
    estados_finales = {"q2", "q4", "q6"}
    transiciones = {
        # comillas dobles triples  """""
        ("q0", "comilla_doble_triple"):  "q1",
        ("q1", "contenido"):             "q1",
        ("q1", "comilla_doble_triple"):  "q2",

        # comillas simples triples  '''
        ("q0", "comilla_simple_triple"): "q3",
        ("q3", "contenido"):             "q3",
        ("q3", "comilla_simple_triple"): "q4",

        # comentario de línea  # 
        ("q0", "hash"):        "q5",
        ("q5", "contenido"):   "q5",
        ("q5", "salto_linea"): "q6",
    }
    return AFD("COMENTARIOS", estados, estado_inicial, estados_finales, transiciones)


def tipo_simbolo_com(texto, pos):
    if texto[pos:pos+3] == '"""':
        return "comilla_doble_triple", 3
    if texto[pos:pos+3] == "'''":
        return "comilla_simple_triple", 3
    c = texto[pos]
    if c == "#":
        return "hash", 1
    if c == "\n":
        return "salto_linea", 1
    return "contenido", 1


def ejecutar_comentarios(texto):
    limpiar_errores()
    afd = afd_comentarios()

    i = 0
    while i < len(texto):
        simbolo, avance = tipo_simbolo_com(texto, i)
        afd.procesar(simbolo, texto[i:i+avance], i)
        i += avance

    if afd.es_aceptado():
        if afd.estado_actual == "q2":
            print(f"'{texto}' → Comentario de bloque (triple comilla doble) válido")
        elif afd.estado_actual == "q4":
            print(f"'{texto}' → Comentario de bloque (triple comilla simple) válido")
        else:
            print(f"'{texto}' → Comentario de línea (#) válido")
    else:
        print(f"'{texto}' → Comentario inválido")
        if not errores:
            if texto.startswith('"""'):
                agregar_error(
                    "CADENA_SIN_CIERRE",
                    texto[-1],
                    len(texto) - 1,
                    'comentario de bloque con """ no fue cerrado correctamente'
                )
            elif texto.startswith("'''"):
                agregar_error(
                    "CADENA_SIN_CIERRE",
                    texto[-1],
                    len(texto) - 1,
                    "comentario de bloque con ''' no fue cerrado correctamente"
                )
            elif texto.startswith("#"):
                agregar_error(
                    "CADENA_SIN_CIERRE",
                    texto[-1],
                    len(texto) - 1,
                    "comentario de línea (#) sin salto de línea al final"
                )
            else:
                agregar_error(
                    "SIMBOLO_NO_RECONOCIDO",
                    texto[0] if texto else "",
                    0,
                    'no es un comentario válido (use """, \'\'\', o #)'
                )
    mostrar_errores()


def afd_delimitadores():
    estados = {
        "q0", "q1", "q2", "q3", "q4", "q5", "q6",
        "q7", "q8", "q9", "q10", "q11", "q_error_dos_puntos", "dead"
    }
    estado_inicial = "q0"
    estados_finales = {
        "q1", "q2", "q3", "q4", "q5", "q6",
        "q7", "q8", "q9", "q10", "q11"
    }
    transiciones = {
        # {} delimitadores con contenido y simple
        ("q0", "llave_a"):    "q1",
        ("q1", "contenido"):  "q1",
        ("q1", "llave_c"):    "q2",
        ("q0", "llave_c"):    "q2",
        # [] delimitadores con contenido y simple
        ("q0", "corch_a"):    "q3",
        ("q3", "contenido"):  "q3",
        ("q3", "corch_c"):    "q4",
        ("q0", "corch_c"):    "q4",
        # () delimitadores con contenido y simple
        ("q0", "paren_a"):    "q5",
        ("q5", "contenido"):  "q5",
        ("q5", "paren_c"):    "q6",
        ("q0", "paren_c"):    "q6",
        # , o ,\n
        ("q0", "coma"):       "q7",
        ("q7", "salto"):      "q8",
        # . o .atributo
        ("q0", "punto"):      "q9",
        ("q9", "contenido"):  "q10",
        ("q10", "contenido"): "q10",
        # ; simple
        ("q0", "punto_coma"): "q4",

        ("q0", "dos_puntos"):"q11",
        ("q11", "salto"): "q2",
        ("q11", "espacio"): "q11",
        ("q11", "contenido"): "q_error_dos_puntos",
        ("q11", "llave_a"): "q_error_dos_puntos",
        ("q11", "llave_c"): "q_error_dos_puntos",
        ("q11", "corch_a"): "q_error_dos_puntos",
        ("q11", "corch_c"): "q_error_dos_puntos",
        ("q11", "paren_a"): "q_error_dos_puntos",
        ("q11", "paren_c"): "q_error_dos_puntos",
        ("q11", "coma"): "q_error_dos_puntos",
        ("q11", "punto"): "q_error_dos_puntos",
        ("q11", "dos_puntos"): "q_error_dos_puntos",
        ("q11", "punto_coma"): "q_error_dos_puntos",

        ("q_error_dos_puntos", "contenido"): "q_error_dos_puntos",
        ("q_error_dos_puntos", "espacio"): "q_error_dos_puntos",
    }
    return AFD("DELIMITADORES", estados, estado_inicial, estados_finales, transiciones)


def tipo_simbolo_del(c):
    if c == "{":  return "llave_a"
    if c == "}":  return "llave_c"
    if c == "[":  return "corch_a"
    if c == "]":  return "corch_c"
    if c == "(":  return "paren_a"
    if c == ")":  return "paren_c"
    if c == ",":  return "coma"
    if c == ".":  return "punto"
    if c == ":":  return "dos_puntos"
    if c == ";":  return "punto_coma"
    if c == "\n": return "salto"
    if c == " ":  return "espacio"
    if c in ['"', "'"]: return "error"
    return "contenido"

def tipo_simbolo_comp(texto, pos):
    par = texto[pos:pos+2]
    if par == ">=":
        return "mayor_igual", 2
    if par == "<=":
        return "menor_igual", 2
    if par == "==":
        return "igualdad", 2
    if par == "!=":
        return "desigualdad", 2

    c = texto[pos]
    if c == ">":
        return "mayor_que", 1
    if c == "<":
        return "menor_que", 1
    return "error", 1

def afd_comparadores():
    estados = {"q0", "q1", "dead"}
    estado_inicial = "q0"
    estados_finales = {"q1"}
    transiciones = {
        ("q0", "mayor_que"):   "q1",
        ("q0", "menor_que"):   "q1",
        ("q0", "mayor_igual"): "q1",
        ("q0", "menor_igual"): "q1",
        ("q0", "igualdad"):    "q1",
        ("q0", "desigualdad"): "q1",
    }
    return AFD("COMPARADORES", estados, estado_inicial, estados_finales, transiciones)

def ejecutar_comparadores(texto):
    limpiar_errores()
    afd = afd_comparadores()

    simbolo, avance = tipo_simbolo_comp(texto, 0)
    afd.procesar(simbolo, texto[:avance], 0)

    if afd.es_aceptado():
        print(f"'{texto}' → Comparador válido")
    else:
        print(f"'{texto}' → Comparador inválido")
        if not errores:
            agregar_error(
                "OPERADOR_INVALIDO",
                texto,
                0,
                f"'{texto}' no es un comparador válido (>, <, >=, <=, ==, !=)"
            )
    mostrar_errores()

def ejecutar_delimitadores(texto):
    limpiar_errores()
    afd = afd_delimitadores()

    for i, c in enumerate(texto):
        simbolo = tipo_simbolo_del(c)
        afd.procesar(simbolo, c, i)

    if afd.es_aceptado():
        print(f"'{texto}' → Delimitador válido")
    else:
        print(f"'{texto}' → Delimitador inválido")
        if not errores:
            agregar_error(
                "DELIMITADOR_MAL_FORMADO",
                texto,
                0,
                f"'{texto}' no es un delimitador válido o está mal formado"
            )
    mostrar_errores()


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
                agregar_error("CADENA_SIN_CIERRE", texto[0], 0, "la cadena no comienza con comilla")
            else:
                agregar_error("CADENA_SIN_CIERRE", texto[-1] if texto else "", len(texto)-1 if texto else 0, "la cadena no cierra correctamente")
    mostrar_errores()


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
            agregar_error("OPERADOR_INVALIDO", texto, 0, f"'{texto}' no es un operador valido (+, -, *, /, %)")
    mostrar_errores()


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
            agregar_error("DELIMITADOR_MAL_FORMADO", texto if texto else "(vacio)", 0, f"se esperaban 4 espacios, se encontraron {espacios}")
    mostrar_errores()

def afd_inicio_linea():
    estados = {"q0", "q1", "q2", "q_error", "dead"}
    estado_inicial = "q0"
    estados_finales = {"q2"}
    transiciones = {
        ("q0", "espacio"):         "q0",    # indentación opcional
        ("q0", "letra"):           "q1",    # inicia con letra → válido
        ("q1", "letra"):           "q1",
        ("q1", "digito"):          "q1",
        ("q1", "espacio"):         "q2",    # terminó el token
        ("q1", "operador"):        "q2",
        ("q1", "dos_puntos"):      "q2",
        ("q1", "paren_a"):         "q2",
        ("q1", "salto"):           "q2",
        ("q0", "digito"):          "q_error",  # inicia con dígito → error
        ("q0", "simbolo"):         "q_error",  # inicia con símbolo → error
        ("q_error", "letra"):      "q_error",
        ("q_error", "digito"):     "q_error",
        ("q_error", "espacio"):    "q_error",
        ("q_error", "simbolo"):    "q_error",
        ("q_error", "operador"):   "q_error",
        ("q_error", "dos_puntos"): "q_error",
        ("q_error", "paren_a"):    "q_error",
    }
    return AFD("INICIO_LINEA", estados, estado_inicial, estados_finales, transiciones)


def tipo_simbolo_inicio_linea(c):
    if c.isalpha() or c == "_": 
        return "letra"
    if c.isdigit():              
        return "digito"
    if c == " ":                 
        return "espacio"
    if c == "\n":                
        return "salto"
    if c == ":":                 
        return "dos_puntos"
    if c == "(":                 
        return "paren_a"
    if c in "=+-*/%":           
        return "operador"
    return "simbolo"

def validar_inicio_lineas(codigo_fuente):
    lineas = codigo_fuente.split("\n")

    for num_linea, linea in enumerate(lineas, 1):
        # Ignorar líneas vacías o solo espacios
        if not linea.strip():
            continue

        afd = afd_inicio_linea()
        linea_con_salto = linea + "\n"
        token_inicio = ""
        error_en_linea = False

        for i, c in enumerate(linea_con_salto):
            simbolo = tipo_simbolo_inicio_linea(c)
            afd.procesar(simbolo, c, i)

            # Acumular el token de inicio para validarlo
            if afd.estado_actual == "q1":
                token_inicio += c

            # Si llega a q_error, marcar error
            if afd.estado_actual == "q_error" and not error_en_linea:
                error_en_linea = True

            # Si termina el token (q2), validar si es PR o identificador válido
            if afd.estado_actual == "q2" and token_inicio:
                token_limpio = token_inicio.strip()

                if token_limpio in palabras_reservadas:
                    print(f"  Línea {num_linea}: '{token_limpio}' → Palabra reservada ✓")
                elif token_limpio and (token_limpio[0].isalpha() or token_limpio[0] == "_"):
                    print(f"  Línea {num_linea}: '{token_limpio}' → Identificador válido ✓")
                else:
                    error_en_linea = True
                    agregar_error(
                        "SIMBOLO_NO_RECONOCIDO",
                        token_limpio,
                        0,
                        f"'{token_limpio}' no es una palabra reservada ni un identificador válido",
                        num_linea
                    )
                break

        if error_en_linea and token_inicio:
            token_limpio = token_inicio.strip()
            agregar_error(
                "SIMBOLO_NO_RECONOCIDO",
                token_limpio,
                0,
                f"'{token_limpio}' no es una palabra reservada ni un identificador válido",
                num_linea
            )
            print(f"  Línea {num_linea}: '{token_limpio}' → ERROR: no es PR ni identificador ✗")

TIPO_TOKEN = {
    "PALABRA_RESERVADA": "Palabra Reservada",
    "IDENTIFICADOR":     "Identificador / Variable",
    "ENTERO":            "Número Entero",
    "REAL":              "Número Real",
    "CADENA":            "Cadena de Texto",
    "COMENTARIO":        "Comentario",
    "OPERADOR":          "Operador",
    "COMPARADOR":        "Comparador",
    "DELIMITADOR":       "Delimitador",
    "INDENTACION":       "Indentación (4 espacios)",
    "ESPACIO":           "Espacio / Blanco",
    "SALTO":             "Salto de Línea",
    "DESCONOCIDO":       "Token Desconocido",
}


# TABLA DE SIMBOLOS
tabla_simbolos = []
_id_simbolo = 1

def registrar_simbolo(token, lexema, categoria):
    global _id_simbolo

    for s in tabla_simbolos:
        if s["lexema"] == lexema:
            return s["id"]

    simbolo = {
        "token": token,
        "lexema": lexema,
        "categoria": categoria,
        "id": _id_simbolo
    }
    tabla_simbolos.append(simbolo)
    _id_simbolo += 1
    return simbolo["id"]

AFDS_CONFIG = [
    {"tipo": "CADENA",        "afd": afd_cadenas,        "simbolo": tipo_simbolo_string_variable, "avance_variable": True},
    {"tipo": "COMENTARIO",    "afd": afd_comentarios,    "simbolo": tipo_simbolo_com,              "avance_variable": True},
    {"tipo": "NUMERO",        "afd": afd_numeros,        "simbolo": tipo_simbolo_num,              "avance_variable": False},
    {"tipo": "COMPARADOR",    "afd": afd_comparadores,   "simbolo": tipo_simbolo_comp,             "avance_variable": True},
    {"tipo": "IDENTIFICADOR", "afd": afd_variables,      "simbolo": tipo_simbolo_var,              "avance_variable": False},
    {"tipo": "OPERADOR",      "afd": afd_operadores,     "simbolo": tipo_char,                     "avance_variable": False},
    {"tipo": "DELIMITADOR",   "afd": afd_delimitadores,  "simbolo": tipo_simbolo_del,              "avance_variable": False},
]

def consumir_con_afd(codigo, i, config):
    afd = config["afd"]()
    simbolo_fn = config["simbolo"]
    avance_variable = config["avance_variable"]

    j = i
    ultimo_aceptado = -1

    while j < len(codigo):
        if avance_variable:
            simbolo, avance = simbolo_fn(codigo, j)
        else:
            simbolo = simbolo_fn(codigo[j])
            avance = 1

        if simbolo == "error":
            break

        nuevo_estado = afd.transiciones.get((afd.estado_actual, simbolo), "dead")
        if nuevo_estado == "dead":
            break

        afd.estado_actual = nuevo_estado
        j += avance

        if afd.es_aceptado():
            ultimo_aceptado = j

    if afd.estado_actual == "q_error":
        lexema_invalido = codigo[i:j]
        agregar_error(
            "NUMERO_INVALIDO",
            lexema_invalido,
            i,
            f"'{lexema_invalido}' no es un número válido (contiene letras)"
        )
        return lexema_invalido, j

    if afd.estado_actual == "q_error_dos_puntos":
        lexema_invalido = codigo[i:j]
        agregar_error(
            "DELIMITADOR_MAL_FORMADO",
            lexema_invalido,
            i,
            f"'{lexema_invalido}' → después de ':' solo se permite un salto de línea '\\n'"
        )
        return lexema_invalido, j

    if ultimo_aceptado != -1:
        return codigo[i:ultimo_aceptado], ultimo_aceptado
    else:
        return None, i


def analizar_codigo(codigo_fuente):
    global errores, tabla_simbolos, _id_simbolo
    limpiar_errores()
    tabla_simbolos.clear()
    _id_simbolo = 1

    tokens = []
    i = 0
    linea = 1
    col = 1

    # ── VALIDACIÓN DE INICIO DE LÍNEA E INDENTACIÓN ────────────────
    lineas = codigo_fuente.split("\n")
    for num_linea, texto_linea in enumerate(lineas, 1):
        if not texto_linea.strip():
            continue

        # Validar indentación: solo múltiplos de 4 espacios
        espacios_indentacion = len(texto_linea) - len(texto_linea.lstrip(" "))
        if espacios_indentacion % 4 != 0:
            agregar_error(
                "DELIMITADOR_MAL_FORMADO",
                texto_linea.strip()[:10],
                1,
                f"indentación inválida: {espacios_indentacion} espacios, se esperan múltiplos de 4 (4, 8, 12...)",
                num_linea
            )

        # Validar token de inicio con AFD
        afd_il = afd_inicio_linea()
        token_inicio = ""
        linea_sin_indent = texto_linea.lstrip(" ")

        for c in linea_sin_indent + "\n":
            estado_antes = afd_il.estado_actual
            simbolo = tipo_simbolo_inicio_linea(c)
            afd_il.procesar(simbolo, c, 0)

            if afd_il.estado_actual == "q1":
                token_inicio += c

            if estado_antes == "q1" and afd_il.estado_actual == "q2":
                token_limpio = token_inicio.strip()
                es_pr = token_limpio in palabras_reservadas

                # Buscar el primer carácter no-espacio después del token
                pos_token = len(token_limpio)
                resto_linea = linea_sin_indent[pos_token:]
                primer_char_sig = resto_linea.lstrip(" ")[:1]

                if es_pr:
                    pass
                elif primer_char_sig in ("=", "(", "["):
                    # Con o sin espacios antes del = ( [ → identificador válido
                    pass
                else:
                    agregar_error(
                        "SIMBOLO_NO_RECONOCIDO",
                        token_limpio,
                        1,
                        f"'{token_limpio}' no es una palabra reservada reconocida del lenguaje",
                        num_linea
                    )
                break

            if afd_il.estado_actual == "q_error":
                token_invalido = linea_sin_indent.split()[0] if linea_sin_indent.strip() else ""
                agregar_error(
                    "SIMBOLO_NO_RECONOCIDO",
                    token_invalido,
                    1,
                    f"'{token_invalido}' no es una palabra reservada ni un identificador válido",
                    num_linea
                )
                break
    # ── FIN VALIDACIÓN ─────────────────────────────────────────────

    while i < len(codigo_fuente):
        mejor_lexema = None
        mejor_tipo = None
        mejor_j = i

        # Si el carácter actual es una comilla, probar CADENA primero
        if codigo_fuente[i] in ['"', "'"]:
            config_cadena = AFDS_CONFIG[0]
            lexema, j = consumir_con_afd(codigo_fuente, i, config_cadena)
            if lexema:
                mejor_lexema = lexema
                mejor_tipo = "CADENA"
                mejor_j = j

        # Si no es comilla o CADENA falló, probar todos los AFDs
        if not mejor_lexema:
            for config in AFDS_CONFIG:
                if codigo_fuente[i] in ['"', "'"] and config["tipo"] == "CADENA":
                    continue
                lexema, j = consumir_con_afd(codigo_fuente, i, config)
                if lexema and (mejor_lexema is None or len(lexema) > len(mejor_lexema)):
                    mejor_lexema = lexema
                    mejor_tipo = config["tipo"]
                    mejor_j = j

        # TOKEN RECONOCIDO
        if mejor_lexema:
            tipo = mejor_tipo

            # Si el AFD de números reportó error, registrar como token inválido
            if tipo == "NUMERO" and any(
                e["categoria"] == "NUMERO_INVALIDO" and e["caracter"] == mejor_lexema
                for e in errores
            ):
                tokens.append({
                    "token": "ERROR",
                    "lexema": mejor_lexema,
                    "tipo": "DESCONOCIDO",
                    "descripcion": "Token no reconocido",
                    "linea": linea,
                    "columna": col,
                    "id": -1,
                    "error": True
                })
                col += len(mejor_lexema)
                i = mejor_j
                continue

            if tipo == "IDENTIFICADOR":
                if mejor_lexema in palabras_reservadas:
                    tipo = "PALABRA_RESERVADA"

            if tipo == "NUMERO":
                tipo = "REAL" if "." in mejor_lexema else "ENTERO"

            descripcion = TIPO_TOKEN.get(tipo, tipo)
            token_name = f"TK_{tipo}"
            simbolo_id = registrar_simbolo(token_name, mejor_lexema, descripcion)

            tokens.append({
                "token": token_name,
                "lexema": mejor_lexema,
                "tipo": tipo,
                "descripcion": descripcion,
                "linea": linea,
                "columna": col,
                "id": simbolo_id,
                "error": False
            })

            for c in mejor_lexema:
                if c == "\n":
                    linea += 1
                    col = 1
                else:
                    col += 1

            i = mejor_j
            continue

        # Espacios en blanco
        if codigo_fuente[i].isspace():
            if codigo_fuente[i] == "\n":
                linea += 1
                col = 1
            else:
                col += 1
            i += 1
            continue

        # ERROR LÉXICO
        c = codigo_fuente[i]
        agregar_error(
            "SIMBOLO_NO_RECONOCIDO",
            c,
            col,
            f"carácter '{c}' (U+{ord(c):04X}) no pertenece al lenguaje",
            linea
        )
        tokens.append({
            "token": "ERROR",
            "lexema": c,
            "tipo": "DESCONOCIDO",
            "descripcion": "Token no reconocido",
            "linea": linea,
            "columna": col,
            "id": -1,
            "error": True
        })
        col += 1
        i += 1

    conteo = {}
    for t in tokens:
        conteo[t["tipo"]] = conteo.get(t["tipo"], 0) + 1

    return {
        "tokens": tokens,
        "errores": errores,
        "resumen": {
            "total_tokens": len(tokens),
            "por_tipo": conteo,
            "total_errores": len(errores)
        }
    }

def imprimir_tabla_simbolos():
    print("\nTABLA DE SIMBOLOS (CUADRUPLOS)\n")
    print(f"{'Token':<15}{'Lexema':<20}{'Categoria':<25}{'ID'}")
    print("-" * 70)

    for s in tabla_simbolos:
        print(f"{s['token']:<15}{s['lexema']:<20}{s['categoria']:<25}{s['id']}")


if __name__ == "__main__":

    sep = "=" * 55


    print("PRUEBAS AFD: CADENAS")

    ejecutar_cadenas('"hola mundo"')
    ejecutar_cadenas("'hola@'")
    ejecutar_cadenas("'hola")
    ejecutar_cadenas('"Hola: esto es una prueba"')
    ejecutar_cadenas('"Caracteres: @#$%^&*()_+-=[]{}|;:,.<>?/"')
    ejecutar_cadenas("'Con comillas simples: también funciona'")
    ejecutar_cadenas('"Cadena con dos puntos : y punto y coma ;"')


    print("PRUEBAS AFD: OPERADORES")

    ejecutar_operadores("+")
    ejecutar_operadores("-")
    ejecutar_operadores("*")
    ejecutar_operadores("/")
    ejecutar_operadores("%")
    ejecutar_operadores("a")


    print("PRUEBAS AFD: 4 ESPACIOS (INDENTACION)")

    ejecutar_4_espacios("    ")   
    ejecutar_4_espacios("   ") 
    ejecutar_4_espacios("     ")
    ejecutar_4_espacios("\t")


    print("PRUEBAS AFD 1: PALABRAS RESERVADAS")

    ejecutar_palabras_reservadas("si")
    ejecutar_palabras_reservadas("mientras ")
    ejecutar_palabras_reservadas("funcion")
    ejecutar_palabras_reservadas("verdadero")
    ejecutar_palabras_reservadas("hola")
    ejecutar_palabras_reservadas("Si")


    print("PRUEBAS AFD 2: VARIABLES / IDENTIFICADORES")

    ejecutar_variables("miVariable")
    ejecutar_variables("_contador")
    ejecutar_variables("var1")
    ejecutar_variables("nombreLargo123")
    ejecutar_variables("1invalido")
    ejecutar_variables("mi-var")
    ejecutar_variables("si")


    print("PRUEBAS AFD 3: NÚMEROS ENTEROS Y REALES")

    ejecutar_numeros("42")
    ejecutar_numeros("0")
    ejecutar_numeros("3.14")
    ejecutar_numeros("100.001")
    ejecutar_numeros("3.")
    ejecutar_numeros(".5")
    ejecutar_numeros("12a3")


    print("PRUEBAS AFD 4: COMENTARIOS")

    ejecutar_comentarios('"""esto es un comentario de bloque"""') 
    ejecutar_comentarios('""""""')
    ejecutar_comentarios("'''comentario en comillas simples'''")
    ejecutar_comentarios("''''''")
    ejecutar_comentarios("# esto es un comentario de línea\n")
    ejecutar_comentarios("# comentario sin salto")
    ejecutar_comentarios('"""sin cierre')
    ejecutar_comentarios("'''sin cierre")

    print("PRUEBAS AFD 5: COMPARADORES")

    ejecutar_comparadores(">")
    ejecutar_comparadores("<")
    ejecutar_comparadores(">=")
    ejecutar_comparadores("<=")
    ejecutar_comparadores("==")
    ejecutar_comparadores("!=")
    ejecutar_comparadores("!!=")
    ejecutar_comparadores("===")
    ejecutar_comparadores("!=@")



    print("PRUEBAS AFD 5: DELIMITADORES")

    ejecutar_delimitadores("{contenido}")
    ejecutar_delimitadores("[elementos]")
    ejecutar_delimitadores("(parametros)")
    ejecutar_delimitadores(",\n")
    ejecutar_delimitadores(".atributo")
    ejecutar_delimitadores(":")
    ejecutar_delimitadores(";")
    ejecutar_delimitadores("{sin_cierre")
    ejecutar_delimitadores("@")

    print("ANALISIS LEXICO COMPLETO")
    print("-"*60)

    codigo = """
a = 1+2
imprimir("El resultado es: ", a)
    """

    resultado = analizar_codigo(codigo)

    print("\nTOKENS\n")
    print(f"{'Token':<15}{'Lexema':<15}{'Tipo':<15}{'ID'}")
    print("-"*60)

    for t in resultado["tokens"]:
        print(f"{t['token']:<15}{t['lexema']:<15}{t['tipo']:<15}{t['id']}")

    imprimir_tabla_simbolos()
    mostrar_errores()