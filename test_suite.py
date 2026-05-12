# test_suite.py - Suite de Pruebas para PyEsp

PRUEBAS_ERRORES = {
    "Test 1: Variable mal declarada": """
funcion calcular():
    variabl numero = 10
    imprimi(numero)
    resultado = numero + 5
    imprimir(resultado)

calcular()
""",

    "Test 2: Palabras reservadas mal escritas": """
funcion prueba():
    sí numero > 5:
        imprimir("Mayor")

    sino_:
        imprimir("Menor")

    mientras_que verdadero:
        romper

prueba()
""",

    "Test 3: Caracteres especiales no permitidos": """
funcion test():
    @variable = 10
    $valor = 20
    #nombre = "Juan"

    numero = 30
    resultado = numero + 5
    imprimir(numero)

test()
""",

    "Test 4: Cadenas sin cerrar": """
funcion test_cadenas():
    texto1 = "Hola mundo
    texto2 = 'Sin cierre
    texto3 = "Bien cerrada"
    imprimir(texto3)

test_cadenas()
""",

    "Test 5: Delimitadores mal formados": """
funcion test_delim():
    lista = [1, 2, 3
    diccionario = {a: 1, b: 2}
    tupla = (1, 2, 3

    para elemento en lista:
        imprimir(elemento)

test_delim()
""",

    "Test 6: Numeros invalidos": """
funcion test_numeros():
    numero1 = 123a45
    numero2 = 12..34
    numero3 = -45
    numero4 = 3.14
    numero5 = 100

    imprimir(numero5)

test_numeros()
""",

    "Test 7: Indentacion incorrecta": """
funcion test_indent():
si verdadero:
    imprimir("Sin indentacion correcta")
  imprimir("Mal indentado")
    imprimir("Bien indentado")

test_indent()
""",

    "Test 8: Comentarios mal formados": """
# Comentario simple correcto
imprimir("Codigo")

'''Comentario sin cerrar

funcion test():
    pasar

test()
""",

    "Test 9: Operadores invalidos": """
funcion test_operadores():
    a = 10
    b = 5

    resultado1 = a +++ b
    resultado2 = a --- b
    resultado3 = a ** b
    resultado4 = a %% b

    imprimir(resultado4)

test_operadores()
""",

    "Test 10: Codigo correcto sin errores": """
funcion calcular_suma(a, b):
    suma = a + b
    retorna suma

funcion principal():
    numero1 = 5
    numero2 = 10

    resultado = calcular_suma(numero1, numero2)
    imprimir(resultado)

    si resultado > 10:
        imprimir("Mayor que 10")
    sino:
        imprimir("Menor o igual")

    para i en [1, 2, 3, 4, 5]:
        imprimir(i)

principal()
"""
}

DESCRIPCIONES = {
    "Test 1: Variable mal declarada": [
        "ERROR: 'variabl' no es palabra reservada valida (deberia ser 'variable')",
        "ERROR: 'imprimi' no es palabra reservada valida (deberia ser 'imprimir')",
        "CORRECTO: Identificadores 'numero' y 'resultado' son validos"
    ],

    "Test 2: Palabras reservadas mal escritas": [
        "ERROR: 'sí' no reconocido (deberia ser 'si')",
        "ERROR: 'sino_' no reconocido (deberia ser 'sino')",
        "ERROR: 'mientras_que' no reconocido (deberia ser 'mientras')",
        "CORRECTO: 'para', 'verdadero', 'romper' detectados correctamente"
    ],

    "Test 3: Caracteres especiales": [
        "ERROR: '@' simbolo no reconocido",
        "ERROR: '$' simbolo no reconocido",
        "ERROR: '#' al inicio de identificador (no permitido)",
        "CORRECTO: Variables validas 'variable', 'valor', 'numero'"
    ],

    "Test 4: Cadenas sin cerrar": [
        "ERROR: Cadena sin cierre en linea 3 (comilla doble)",
        "ERROR: Cadena sin cierre en linea 4 (comilla simple)",
        "CORRECTO: Cadena bien cerrada en linea 5",
        "Se espera error lexico por cadenas no cerradas"
    ],

    "Test 5: Delimitadores": [
        "ERROR: '[' sin cerrarse correctamente",
        "ERROR: '(' sin cerrarse correctamente",
        "CORRECTO: Delimitadores bien formados en estructura valida"
    ],

    "Test 6: Numeros invalidos": [
        "ERROR: '123a45' - numero con letras en medio",
        "ERROR: '12..34' - punto decimal duplicado",
        "CORRECTO: '-45', '3.14', '100' son numeros validos"
    ],

    "Test 7: Indentacion": [
        "ERROR: Indentacion sin multiplos correctos de espacios",
        "ERROR: Mezcla de indentacion (4 espacios, 2 espacios, 4 espacios)",
        "Se espera deteccion de error de indentacion"
    ],

    "Test 8: Comentarios": [
        "ERROR: Comentario de bloque sin cierre (triple comilla)",
        "CORRECTO: Comentario simple correcto (#)",
        "Codigo sin procesar despues del comentario sin cerrar"
    ],

    "Test 9: Operadores invalidos": [
        "ERROR: '+++' operador no valido (triple suma)",
        "ERROR: '---' operador no valido (triple resta)",
        "ERROR: '**' operador no reconocido",
        "ERROR: '%%' operador no valido (modulo duplicado)",
        "CORRECTO: Operadores validos: + - * / = > <"
    ],

    "Test 10: Codigo correcto sin errores": [
        "CORRECTO: Todo el codigo es valido",
        "CORRECTO: Palabras reservadas: funcion, retorna, si, sino, para, imprimir",
        "CORRECTO: Identificadores: calcular_suma, principal, numero1, numero2",
        "CORRECTO: Numeros validos: 5, 10",
        "CORRECTO: Lista valida: [1, 2, 3, 4, 5]",
        "CORRECTO: Estructura y logica correcta"
    ]
}