import re

# ============================================================
# ESPECIFICACIÓN LÉXICA 
# ============================================================
TOKEN_PATTERNS = [
    ('COMENTARIO',         r'#.*'),
    ('RES_CONFIGURACION',  r'configuracion:'),
    ('RES_CIRCUITO',       r'circuito:'),
    ('RES_FIN',            r'\bfin\b'),
    ('RES_INCLUIR',        r'incluir libreria'),
    ('TIPO_SERVO',         r'\bservo\b'),
    ('TIPO_DECIMAL',       r'\bdecimal\b'),
    ('TIPO_ENTERO',        r'\b(numpin|numero)\b'),
    ('RES_SI',             r'\bsi\b'),
    ('RES_SINO',           r'\bsino:?'),
    ('ACCION_CONFIGURAR',  r'\bconfigurar\b'),
    ('ACCION_ENCENDER',    r'\bencender\b'),
    ('ACCION_APAGAR',      r'\bapagar\b'),
    ('ACCION_LEER',        r'\bleer_sensor\b'),
    ('ACCION_ESPERAR',     r'\besperar\b'),
    ('MODO_PIN',           r'\b(salida|entrada)\b'),
    ('OBJ_CONECTAR',       r'\bconectar\b'),
    ('OBJ_ESTADO',         r'\bestado\b'),
    ('OBJ_PULSO',          r'\bpulso\b'),
    ('NUM_DECIMAL',        r'\d+\.\d+'),
    ('NUM_ENTERO',         r'\d+'),
    ('VAL_PIN_ANALOG',     r'A\d+'),
    ('VAL_TEXTO',          r'\".*?\"'),
    ('ID_VARIABLE',        r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('OP_RELACIONAL',      r'(==|<=|>=|<|>)'),
    ('OP_ASIGNACION',      r'='),
    ('OP_ARITMETICO',      r'[\+\-\*\/]'),
    ('SYM_PUNTO_COMA',     r';'),
    ('SYM_COMA',           r','),
    ('SYM_PUNTO',          r'\.'),
    ('SYM_PAR_IZQ',        r'\('),
    ('SYM_PAR_DER',        r'\)'),
    ('SYM_DOS_PUNTOS',     r':'),
    ('SKIP',               r'\s+'), # Usamos \s+ para atrapar cualquier espacio, tab o salto de línea
    ('ERROR',              r'.'),
]

def get_tokens(codigo):
    tokens = []
    errores_lexicos = []
    linea_actual = 1
    pos = 0
    
    # Pre-compilamos los patrones para mayor eficiencia
    compiled_patterns = [(tipo, re.compile(patron)) for tipo, patron in TOKEN_PATTERNS]
    
    while pos < len(codigo):
        match = None
        for tipo, regex in compiled_patterns:
            match = regex.match(codigo, pos)
            if match:
                valor = match.group(0)
                if tipo == 'SKIP':
                    linea_actual += valor.count('\n')
                elif tipo == 'COMENTARIO':
                    pass
                elif tipo == 'ERROR':
                    # Si caemos aquí, es que ningún patrón anterior coincidió.
                    # El espacio debería haber coincidido con SKIP.
                    # Si no lo hizo, lo reportamos.
                    errores_lexicos.append(f"Error Léxico: Carácter '{valor}' inesperado en línea {linea_actual}")
                else:
                    tokens.append({'tipo': tipo, 'valor': valor, 'linea': linea_actual})
                pos = match.end()
                break
        
        if not match:
            # Esto técnicamente no debería pasar con el patrón ERROR (.), pero por seguridad:
            pos += 1 
            
    return tokens, errores_lexicos
