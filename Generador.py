class Generador:
    def __init__(self, tac):
        self.tac = tac
        self.codigo = ""
        self.vars_declaradas = set()

    def obtener_codigo_arduino(self):
        self.codigo += "// Código generado por Arduino Amigo\n"
        
        if "servo.h" in self.tac.librerias_usadas:
            self.codigo += "#include <Servo.h>\n"
        
        self.codigo += "\n"

        # 1. VARIABLES GLOBALES (PROCEDENTES DEL SETUP)
        for inst in self.tac.setup_instructions:
            if inst['op'] == 'declare':
                tipo_arduino = "int"
                if inst['arg1'] == 'decimal': 
                    tipo_arduino = "float"
                elif inst['arg1'] == 'servo':
                    tipo_arduino = "Servo"
                
                if inst['arg1'] == 'servo':
                    self.codigo += f"{tipo_arduino} {inst['res']};\n"
                else:
                    self.codigo += f"{tipo_arduino} {inst['res']} = {inst['arg2']};\n"
                self.vars_declaradas.add(inst['res'])

        self.codigo += "\n"

        # 2. VOID SETUP
        self.codigo += "void setup() {\n"
        for inst in self.tac.setup_instructions:
            if inst['op'] == 'call':
                fn = inst['arg1']
                a1 = inst['arg2']
                res = inst['res']
                if fn == 'pinMode':
                    modo = "OUTPUT" if res == 'salida' else "INPUT"
                    self.codigo += f"  pinMode({a1}, {modo});\n"
                elif fn == 'attach':
                    self.codigo += f"  {res}.attach({a1});\n"
                elif fn == 'write':
                    self.codigo += f"  {res}.write({a1});\n"
        self.codigo += "}\n\n"

        # 3. VOID LOOP
        self.codigo += "void loop() {\n"
        for inst in self.tac.loop_instructions:
            op = inst['op']
            res = inst['res']
            arg1 = inst['arg1']
            arg2 = inst['arg2']

            if op == 'declare':
                tipo_arduino = "float" if arg1 == 'decimal' else "int"
                if res not in self.vars_declaradas:
                    self.codigo += f"  {tipo_arduino} {res} = {arg2};\n"
                    self.vars_declaradas.add(res)
                else:
                    self.codigo += f"  {res} = {arg2};\n"

            elif op == '=':
                prefijo = ""
                if res not in self.vars_declaradas:
                    prefijo = "float "
                    self.vars_declaradas.add(res)
                self.codigo += f"  {prefijo}{res} = {arg1};\n"

            elif op in ['+', '-', '*', '/', '>', '<', '==', '>=', '<=']:
                tipo = "bool" if op in ['>', '<', '==', '>=', '<='] else "float"
                prefijo = ""
                if res not in self.vars_declaradas:
                    prefijo = f"{tipo} "
                    self.vars_declaradas.add(res)
                self.codigo += f"  {prefijo}{res} = {arg1} {op} {arg2};\n"

            elif op == 'if_false':
                self.codigo += f"  if (!{arg1}) goto {res};\n"
            elif op == 'goto':
                self.codigo += f"  goto {res};\n"
            elif op == 'label':
                self.codigo += f"  {res}:\n"

            elif op == 'call':
                fn = arg1
                a1 = arg2
                r = res
                if fn == 'digitalWrite':
                    self.codigo += f"  digitalWrite({a1}, {r});\n"
                elif fn == 'delay':
                    self.codigo += f"  delay({a1});\n"
                elif fn == 'write':
                    self.codigo += f"  {r}.write({a1});\n"
                elif fn == 'analogRead':
                    prefijo = ""
                    if r not in self.vars_declaradas:
                        prefijo = "int "
                        self.vars_declaradas.add(r)
                    self.codigo += f"  {prefijo}{r} = analogRead({a1});\n"
                elif fn == 'pulseIn':
                    prefijo = ""
                    if r not in self.vars_declaradas:
                        prefijo = "long "
                        self.vars_declaradas.add(r)
                    self.codigo += f"  {prefijo}{r} = pulseIn({a1}, HIGH);\n"

        self.codigo += "}\n"
        return self.codigo