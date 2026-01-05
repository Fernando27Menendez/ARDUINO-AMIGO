from TAC import TACGenerator

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_actual = self.tokens[self.pos] if self.tokens else None
        self.tac = TACGenerator()
        self.tabla_simbolos = set() # Semantic analysis: tracks declared variables

    def avanzar(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_actual = self.tokens[self.pos]
        else:
            self.token_actual = None

    def verificar_variable(self, nombre, linea):
        if nombre not in self.tabla_simbolos:
            raise Exception(f"Línea {linea}: Error Semántico. La variable '{nombre}' no ha sido declarada.")

    def registrar_variable(self, nombre, linea):
        if nombre in self.tabla_simbolos:
            # En Arduino se permite redeclarar en diferentes alcances, pero para este lenguaje
            # académico, vamos a ser estrictos con la duplicidad en el mismo programa.
            pass
        self.tabla_simbolos.add(nombre)

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
        
        if self.token_actual:
            raise Exception(f"Línea {self.token_actual['linea']}: Error. Código extra fuera de los bloques principales.")

    def parse_declaracion_setup(self):
        t = self.token_actual
        if not t: return
        linea = t['linea']

        if t['tipo'] in ['TIPO_ENTERO', 'TIPO_DECIMAL', 'TIPO_SERVO']:
            tipo = self.consumir(t['tipo'])
            nombre = self.consumir('ID_VARIABLE')
            self.registrar_variable(nombre, linea)
            
            if tipo == 'servo':
                if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                    self.consumir('SYM_PUNTO_COMA')
                self.tac.emit('declare', 'servo', None, nombre, 'setup')
                return

            self.consumir('OP_ASIGNACION')
            if self.token_actual['tipo'] in ['NUM_ENTERO', 'NUM_DECIMAL', 'VAL_PIN_ANALOG', 'ID_VARIABLE']:
                if self.token_actual['tipo'] == 'ID_VARIABLE':
                    self.verificar_variable(self.token_actual['valor'], self.token_actual['linea'])
                valor = self.consumir(self.token_actual['tipo'])
            else:
                raise Exception(f"Línea {self.token_actual['linea']}: Valor '{self.token_actual['valor']}' no válido.")
                
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('declare', tipo, valor, nombre, 'setup')

        elif t['tipo'] == 'ACCION_CONFIGURAR':
            self.consumir('ACCION_CONFIGURAR')
            self.consumir('SYM_PAR_IZQ')
            pin = self.consumir('ID_VARIABLE')
            self.verificar_variable(pin, linea)
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
            self.verificar_variable(obj, linea)
            self.consumir('SYM_PAR_IZQ')
            pin_token = self.token_actual
            if pin_token['tipo'] == 'ID_VARIABLE':
                self.verificar_variable(pin_token['valor'], pin_token['linea'])
                self.avanzar()
                pin = pin_token['valor']
            elif pin_token['tipo'] == 'NUM_ENTERO':
                self.avanzar()
                pin = pin_token['valor']
            else:
                 raise Exception(f"Línea {pin_token['linea']}: Pin no válido.")
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'attach', pin, obj, 'setup')

        elif t['tipo'] == 'OBJ_ESTADO':
            self.consumir('OBJ_ESTADO')
            self.consumir('SYM_PUNTO')
            obj = self.consumir('ID_VARIABLE')
            self.verificar_variable(obj, linea)
            self.consumir('SYM_PAR_IZQ')
            val_token = self.token_actual
            if val_token['tipo'] in ['ID_VARIABLE', 'NUM_ENTERO']:
                 if val_token['tipo'] == 'ID_VARIABLE':
                     self.verificar_variable(val_token['valor'], val_token['linea'])
                 self.avanzar()
                 val = val_token['valor']
            else:
                 raise Exception(f"Línea {val_token['linea']}: Valor no válido.")
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'write', val, obj, 'setup')
        else:
             raise Exception(f"Línea {linea}: Sentencia inesperada en configuracion: '{t['valor']}'")

    def parse_sentencia_loop(self):
        t = self.token_actual
        if not t: return
        linea = t['linea']

        if t['tipo'] == 'ACCION_ENCENDER':
            self.consumir('ACCION_ENCENDER')
            self.consumir('SYM_PAR_IZQ')
            pin = self.consumir('ID_VARIABLE')
            self.verificar_variable(pin, linea)
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'digitalWrite', pin, 'HIGH', 'loop')

        elif t['tipo'] == 'ACCION_APAGAR':
            self.consumir('ACCION_APAGAR')
            self.consumir('SYM_PAR_IZQ')
            pin = self.consumir('ID_VARIABLE')
            self.verificar_variable(pin, linea)
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'digitalWrite', pin, 'LOW', 'loop')

        elif t['tipo'] == 'ACCION_ESPERAR':
            self.consumir('ACCION_ESPERAR')
            self.consumir('SYM_PAR_IZQ')
            val_token = self.token_actual
            if val_token['tipo'] == 'ID_VARIABLE':
                 self.verificar_variable(val_token['valor'], val_token['linea'])
                 self.avanzar()
            elif val_token['tipo'] == 'NUM_ENTERO':
                 self.avanzar()
            else:
                 raise Exception(f"Línea {linea}: El tiempo debe ser número o variable.")
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'delay', val_token['valor'], None, 'loop')

        elif t['tipo'] == 'OBJ_ESTADO':
            self.consumir('OBJ_ESTADO')
            self.consumir('SYM_PUNTO')
            obj = self.consumir('ID_VARIABLE')
            self.verificar_variable(obj, linea)
            self.consumir('SYM_PAR_IZQ')
            val_token = self.token_actual
            if val_token['tipo'] == 'ID_VARIABLE':
                 self.verificar_variable(val_token['valor'], val_token['linea'])
            self.avanzar() 
            self.consumir('SYM_PAR_DER')
            if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                self.consumir('SYM_PUNTO_COMA')
            self.tac.emit('call', 'write', val_token['valor'], obj, 'loop')

        elif t['tipo'] in ['TIPO_ENTERO', 'TIPO_DECIMAL', 'ID_VARIABLE']:
            tipo = None
            if t['tipo'] in ['TIPO_ENTERO', 'TIPO_DECIMAL']:
                tipo = self.consumir(t['tipo'])
            
            nombre_var = self.consumir('ID_VARIABLE')
            if tipo:
                self.registrar_variable(nombre_var, linea)
            else:
                self.verificar_variable(nombre_var, linea)

            self.consumir('OP_ASIGNACION')

            if self.token_actual['tipo'] == 'ACCION_LEER':
                self.consumir('ACCION_LEER')
                self.consumir('SYM_PAR_IZQ')
                pin = self.consumir('ID_VARIABLE')
                self.verificar_variable(pin, self.token_actual['linea'] if self.token_actual else linea)
                self.consumir('SYM_PAR_DER')
                if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                    self.consumir('SYM_PUNTO_COMA')
                if tipo: self.tac.emit('declare', tipo, '0', nombre_var, 'loop')
                self.tac.emit('call', 'analogRead', pin, nombre_var, 'loop')
            
            elif self.token_actual['tipo'] == 'OBJ_PULSO':
                self.consumir('OBJ_PULSO')
                self.consumir('SYM_PUNTO')
                attr = self.consumir('ID_VARIABLE')
                self.verificar_variable(attr, linea)
                if self.token_actual and self.token_actual['tipo'] == 'SYM_PUNTO_COMA':
                    self.consumir('SYM_PUNTO_COMA')
                if tipo: self.tac.emit('declare', tipo, '0', nombre_var, 'loop')
                self.tac.emit('call', 'pulseIn', attr, nombre_var, 'loop')

            else:
                arg1_token = self.token_actual
                if arg1_token['tipo'] == 'ID_VARIABLE':
                    self.verificar_variable(arg1_token['valor'], arg1_token['linea'])
                
                if arg1_token['tipo'] in ['NUM_ENTERO', 'NUM_DECIMAL', 'ID_VARIABLE']:
                    self.avanzar()
                    arg1 = arg1_token['valor']
                else:
                    raise Exception(f"Línea {arg1_token['linea']}: Valor no válido.")
                
                if self.token_actual and self.token_actual['tipo'] == 'OP_ARITMETICO':
                    op = self.consumir('OP_ARITMETICO')
                    arg2_token = self.token_actual
                    if arg2_token['tipo'] == 'ID_VARIABLE':
                        self.verificar_variable(arg2_token['valor'], arg2_token['linea'])
                    
                    if arg2_token['tipo'] in ['NUM_ENTERO', 'NUM_DECIMAL', 'ID_VARIABLE']:
                        self.avanzar()
                        arg2 = arg2_token['valor']
                    else:
                        raise Exception(f"Línea {arg2_token['linea']}: Valor tras '{op}' no válido.")
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
            raise Exception(f"Línea {linea}: Sentencia '{t['valor']}' no válida.")

    def parse_condicional(self):
        self.consumir('RES_SI')
        self.consumir('SYM_PAR_IZQ')
        
        op1_token = self.token_actual
        if op1_token['tipo'] == 'ID_VARIABLE':
            self.verificar_variable(op1_token['valor'], op1_token['linea'])
        self.avanzar()
        
        op = self.consumir('OP_RELACIONAL')
        
        op2_token = self.token_actual
        if op2_token['tipo'] == 'ID_VARIABLE':
            self.verificar_variable(op2_token['valor'], op2_token['linea'])
        self.avanzar()
            
        self.consumir('SYM_PAR_DER')
        if self.token_actual and self.token_actual['tipo'] == 'SYM_DOS_PUNTOS':
            self.consumir('SYM_DOS_PUNTOS') 

        t_res = self.tac.new_temp()
        L_false = self.tac.new_label()
        L_end = self.tac.new_label()

        self.tac.emit(op, op1_token['valor'], op2_token['valor'], t_res, 'loop') 
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
