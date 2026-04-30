# keywords.py

PALABRAS_RESERVADAS = {
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

TIPOS_DATOS = {
    "numero", "texto", "booleano", "lista", "diccionario", "nulo"
}

OPERADORES = {
    "+", "-", "*", "/", "%", "=", "==", "!=", "<", ">", "<=", ">=",
    "&&", "||", "!", "&", "|", "^", "~", "<<", ">>"
}

# Función auxiliar para validar si una palabra es reservada
def es_palabra_reservada(palabra):
    return palabra.lower() in PALABRAS_RESERVADAS

def es_tipo_dato(palabra):
    return palabra.lower() in TIPOS_DATOS

def es_operador(op):
    return op in OPERADORES