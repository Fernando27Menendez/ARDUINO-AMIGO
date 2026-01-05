from TAC import TACGenerator

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_actual = self.tokens[self.pos] if self.tokens else None
        self.tac = TACGenerator()

    def avanzar(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_actual = self.tokens[self.pos]
        else:
            self.token_actual = None

    def consumir(self, tipo_esperado):
        if self.token_actual and self.token_actual['tipo'] == tipo_esperado:
            val = self.token_actual['valor']
            self.avanzar()
            return val
        else:
            encontrado = self.token_actual['tipo'] if self.token_actual else "FIN DE ARCHIVO"
            linea = self.token_actual['linea'] if self.token_actual else "desconocida"
            raise Exception(f"Línea {linea}: Error Sintáctico. Se esperaba '{tipo_esperado}', pero se encontró '{encontrado}'")

    def parse_programa(self):
        # 1. Librerías (Opcional)
        while self.token_actual and self.token_actual['tipo'] == 'RES_INCLUIR':
            self.consumir('RES_INCLUIR')
            lib = self.consumir('VAL_TEXTO')
            self.tac.agregar_libreria(lib)
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')

        # 2. Bloque Configuración: configuracion: ... fin
        self.consumir('RES_CONFIGURACION')
        while self.token_actual and self.token_actual['tipo'] != 'RES_FIN':
            self.parse_declaracion_setup()
        self.consumir('RES_FIN') # Cierre de configuracion:
        
        # 3. Bloque Circuito: circuito: ... fin
        self.consumir('RES_CIRCUITO')
        while self.token_actual and self.token_actual['tipo'] != 'RES_FIN':
            self.parse_sentencia_loop()
        self.consumir('RES_FIN') # Cierre de circuito:
        
        # Verificar fin de archivo
        if self.token_actual:
            raise Exception(f"Línea {self.token_actual['linea']}: Error. Se encontró código extra fuera de los bloques principales.")

    def parse_declaracion_setup(self):
        t = self.token_actual
        if not t: return

        if t['tipo'] in ['TIPO_ENTERO', 'TIPO_DECIMAL', 'TIPO_SERVO']:
            tipo = self.consumir(t['tipo'])
            nombre = self.consumir('ID_VARIABLE')
            
            if tipo == 'servo':
                if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                    self.consumir('SYM_PUNTO_COMA')
                self.tac.emit('declare', 'servo', None, nombre, 'setup')
                return

            self.consumir('OP_ASIGNACION')
            if self.token_actual['tipo'] in ['NUM_ENTERO', 'NUM_DECIMAL', 'VAL_PIN_ANALOG', 'ID_VARIABLE']:
                valor = self.consumir(self.token_actual['tipo'])
            else:
                raise Exception(f"Línea {self.token_actual['linea']}: Valor '{self.token_actual['valor']}' no válido en la declaración de '{nombre}'")
                
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('declare', tipo, valor, nombre, 'setup')

        elif t['tipo'] == 'ACCION_CONFIGURAR':
            self.consumir('ACCION_CONFIGURAR')
            self.consumir('SYM_PAR_IZQ')
            pin = self.consumir('ID_VARIABLE')
            self.consumir('SYM_COMA')
            modo = self.consumir('MODO_PIN')
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'pinMode', pin, modo, 'setup')

        elif t['tipo'] == 'OBJ_CONECTAR':
            self.consumir('OBJ_CONECTAR')
            self.consumir('SYM_PUNTO')
            obj = self.consumir('ID_VARIABLE')
            self.consumir('SYM_PAR_IZQ')
            pin = self.token_actual['valor']
            if self.token_actual['tipo'] in ['ID_VARIABLE', 'NUM_ENTERO']:
                self.avanzar()
            else:
                 raise Exception(f"Línea {self.token_actual['linea']}: Pin '{self.token_actual['valor']}' no válido en conectar.{obj}()")
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'attach', pin, obj, 'setup')

        elif t['tipo'] == 'OBJ_ESTADO':
            self.consumir('OBJ_ESTADO')
            self.consumir('SYM_PUNTO')
            obj = self.consumir('ID_VARIABLE')
            self.consumir('SYM_PAR_IZQ')
            val = self.token_actual['valor']
            if self.token_actual['tipo'] in ['ID_VARIABLE', 'NUM_ENTERO']:
                 self.avanzar()
            else:
                 raise Exception(f"Línea {self.token_actual['linea']}: Valor '{self.token_actual['valor']}' no válido en estado.{obj}()")
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'write', val, obj, 'setup')
        else:
             raise Exception(f"Línea {t['linea']}: Error Sintáctico. Sentencia inesperada en configuracion: '{t['valor']}'")

    def parse_sentencia_loop(self):
        t = self.token_actual
        if not t: return

        if t['tipo'] == 'ACCION_ENCENDER':
            self.consumir('ACCION_ENCENDER')
            self.consumir('SYM_PAR_IZQ')
            pin = self.consumir('ID_VARIABLE')
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'digitalWrite', pin, 'HIGH', 'loop')

        elif t['tipo'] == 'ACCION_APAGAR':
            self.consumir('ACCION_APAGAR')
            self.consumir('SYM_PAR_IZQ')
            pin = self.consumir('ID_VARIABLE')
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'digitalWrite', pin, 'LOW', 'loop')

        elif t['tipo'] == 'ACCION_ESPERAR':
            self.consumir('ACCION_ESPERAR')
            self.consumir('SYM_PAR_IZQ')
            val = self.token_actual['valor']
            if self.token_actual['tipo'] in ['NUM_ENTERO', 'ID_VARIABLE']:
                 self.avanzar()
            else:
                 raise Exception(f"Línea {self.token_actual['linea']}: El tiempo de espera debe ser número o variable.")
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'delay', val, None, 'loop')

        elif t['tipo'] == 'OBJ_ESTADO':
            self.consumir('OBJ_ESTADO')
            self.consumir('SYM_PUNTO')
            obj = self.consumir('ID_VARIABLE')
            self.consumir('SYM_PAR_IZQ')
            val = self.token_actual['valor']
            self.avanzar() 
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'write', val, obj, 'loop')

        elif t['tipo'] in ['TIPO_ENTERO', 'TIPO_DECIMAL', 'ID_VARIABLE']:
            tipo = None
            if t['tipo'] in ['TIPO_ENTERO', 'TIPO_DECIMAL']:
                tipo = self.consumir(t['tipo'])
            
            nombre_var = self.consumir('ID_VARIABLE')
            self.consumir('OP_ASIGNACION')

            if self.token_actual and self.token_actual['tipo'] == 'ACCION_LEER':
                self.consumir('ACCION_LEER')
                self.consumir('SYM_PAR_IZQ')
                pin = self.consumir('ID_VARIABLE')
                self.consumir('SYM_PAR_DER')
                if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                    self.consumir('SYM_PUNTO_COMA')
                if tipo: self.tac.emit('declare', tipo, '0', nombre_var, 'loop')
                self.tac.emit('call', 'analogRead', pin, nombre_var, 'loop')
            
            elif self.token_actual and self.token_actual['tipo'] == 'OBJ_PULSO':
                self.consumir('OBJ_PULSO')
                self.consumir('SYM_PUNTO')
                attr = self.consumir('ID_VARIABLE')
                if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                    self.consumir('SYM_PUNTO_COMA')
                if tipo: self.tac.emit('declare', tipo, '0', nombre_var, 'loop')
                self.tac.emit('call', 'pulseIn', attr, nombre_var, 'loop')

            else:
                arg1 = self.token_actual['valor']
                if self.token_actual['tipo'] in ['NUM_ENTERO', 'NUM_DECIMAL', 'ID_VARIABLE']:
                    self.avanzar()
                else:
                    raise Exception(f"Línea {self.token_actual['linea']}: Se esperaba un valor o variable en la asignación de '{nombre_var}'")
                
                if self.token_actual and self.token_actual['tipo'] == 'OP_ARITMETICO':
                    op = self.consumir('OP_ARITMETICO')
                    arg2 = self.token_actual['valor']
                    if self.token_actual['tipo'] in ['NUM_ENTERO', 'NUM_DECIMAL', 'ID_VARIABLE']:
                        self.avanzar()
                    else:
                        raise Exception(f"Línea {self.token_actual['linea']}: Se esperaba un valor tras '{op}'")
                    if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                        self.consumir('SYM_PUNTO_COMA')
                    if tipo: self.tac.emit('declare', tipo, '0', nombre_var, 'loop')
                    self.tac.emit(op, arg1, arg2, nombre_var, 'loop')
                else:
                    if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                        self.consumir('SYM_PUNTO_COMA')
                    if tipo: self.tac.emit('declare', tipo, arg1, nombre_var, 'loop')
                    else: self.tac.emit('=', arg1, None, nombre_var, 'loop')

        elif t['tipo'] == 'RES_SI':
            self.parse_condicional()
        else:
            raise Exception(f"Línea {t['linea']}: Sentencia '{t['valor']}' no válida en el bloque circuito.")

    def parse_condicional(self):
        self.consumir('RES_SI')
        self.consumir('SYM_PAR_IZQ')
        op1 = self.token_actual['valor']
        if self.token_actual['tipo'] in ['ID_VARIABLE', 'NUM_ENTERO', 'NUM_DECIMAL']:
            self.avanzar()
        else:
            raise Exception(f"Línea {self.token_actual['linea']}: Primer operando de condición no válido.")
            
        op = self.consumir('OP_RELACIONAL')
        
        op2 = self.token_actual['valor']
        if self.token_actual['tipo'] in ['ID_VARIABLE', 'NUM_ENTERO', 'NUM_DECIMAL']:
            self.avanzar()
        else:
            raise Exception(f"Línea {self.token_actual['linea']}: Segundo operando de condición no válido.")
            
        self.consumir('SYM_PAR_DER')
        if self.token_actual and self.token_actual['tipo'] == 'SYM_DOS_PUNTOS':
            self.consumir('SYM_DOS_PUNTOS') 

        t_res = self.tac.new_temp()
        L_false = self.tac.new_label()
        L_end = self.tac.new_label()

        self.tac.emit(op, op1, op2, t_res, 'loop') 
        self.tac.emit('if_false', t_res, None, L_false, 'loop')

        while self.token_actual and self.token_actual['tipo'] not in ['RES_FIN', 'RES_SINO']:
            self.parse_sentencia_loop()
        
        if self.token_actual and self.token_actual['tipo'] == 'RES_SINO':
            self.tac.emit('goto', None, None, L_end, 'loop')
            self.tac.emit('label', None, None, L_false, 'loop')
            self.consumir('RES_SINO')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_DOS_PUNTOS':
                self.consumir('SYM_DOS_PUNTOS')
            while self.token_actual and self.token_actual['tipo'] != 'RES_FIN':
                self.parse_sentencia_loop()
            self.consumir('RES_FIN')
            self.tac.emit('label', None, None, L_end, 'loop')
        else:
            self.consumir('RES_FIN')
            self.tac.emit('label', None, None, L_false, 'loop')
