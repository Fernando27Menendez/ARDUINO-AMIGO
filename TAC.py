# TAC.py
class TACGenerator:
    def __init__(self):
        self.setup_instructions = [] # Para el bloque 'configuracion:'
        self.loop_instructions = []  # Para el bloque 'circuito:'
        self.temp_count = 0
        self.label_count = 0
        self.librerias_usadas = set() # Ej: set(['Servo.h'])

    def new_temp(self):
        """Genera t1, t2, t3..."""
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        """Genera L1, L2, L3..."""
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, op, arg1, arg2, res, context='loop'):
        """
        Crea un cuarteto (instrucción de 3 direcciones).
        context: puede ser 'setup' o 'loop'
        """
        cuarteto = {'op': op, 'arg1': arg1, 'arg2': arg2, 'res': res}
        
        if context == 'setup':
            self.setup_instructions.append(cuarteto)
        else:
            self.loop_instructions.append(cuarteto)
            
    def agregar_libreria(self, lib):
        self.librerias_usadas.add(lib)