class Generador:
    def __init__(self, tac):
        self.tac = tac
        self.codigo = ""
        self.vars_declaradas = set()

    def obtener_codigo_arduino(self):
        self.codigo += "// Código generado por Arduino Amigo\n"
        
        if any(lib.lower() == "servo.h" for lib in self.tac.librerias_usadas):
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
        indent = "  "
        stack = [] # Pila para reconstruir estructuras (tipo, etiqueta_objetivo)

        for inst in self.tac.loop_instructions:
            op = inst['op']
            res = inst['res']
            arg1 = inst['arg1']
            arg2 = inst['arg2']

            # Verificar si alcanzamos una etiqueta que cierra un bloque
            if op == 'label' and stack and stack[-1][1] == res:
                tipo_bloque, etiqueta = stack.pop()
                indent = indent[0:-2]
                self.codigo += f"{indent}}}\n"
                if tipo_bloque == 'if' and any(i['op'] == 'label' and i['res'] == etiqueta for i in self.tac.loop_instructions[self.tac.loop_instructions.index(inst)+1:]):
                    # Podría haber un else a continuación si hay un goto previo, 
                    # pero nuestra lógica de 'goto' ya lo maneja.
                    pass
                continue

            if op == 'declare':
                tipo_arduino = "float" if arg1 == 'decimal' else "int"
                if res not in self.vars_declaradas:
                    self.codigo += f"{indent}{tipo_arduino} {res} = {arg2};\n"
                    self.vars_declaradas.add(res)
                else:
                    self.codigo += f"{indent}{res} = {arg2};\n"

            elif op == '=':
                prefijo = ""
                if res not in self.vars_declaradas:
                    prefijo = "float "
                    self.vars_declaradas.add(res)
                self.codigo += f"{indent}{prefijo}{res} = {arg1};\n"

            elif op in ['+', '-', '*', '/', '>', '<', '==', '>=', '<=']:
                tipo = "bool" if op in ['>', '<', '==', '>=', '<='] else "float"
                prefijo = ""
                if res not in self.vars_declaradas:
                    prefijo = f"{tipo} "
                    self.vars_declaradas.add(res)
                self.codigo += f"{indent}{prefijo}{res} = {arg1} {op} {arg2};\n"

            elif op == 'if_false':
                # Reconstrucción: if_false tX L1 -> if (tX) {
                self.codigo += f"{indent}if ({arg1}) {{\n"
                indent += "  "
                stack.append(('if', res))

            elif op == 'goto':
                # Si estamos en un 'if' y viene un goto, es probablemente un 'else'
                if stack and stack[-1][0] == 'if':
                    tipo, label_dest = stack.pop()
                    indent = indent[0:-2]
                    self.codigo += f"{indent}}} else {{\n"
                    indent += "  "
                    stack.append(('else', res))
                else:
                    # Salto explícito (raro en este lenguaje actual, pero por si acaso)
                    self.codigo += f"{indent}goto {res};\n"

            elif op == 'label':
                # Ignoramos etiquetas que no cierran bloques según nuestra pila
                # (como la etiqueta del else que ya procesamos en el goto)
                pass

            elif op == 'call':
                fn = arg1
                a1 = arg2
                r = res
                if fn == 'digitalWrite':
                    self.codigo += f"{indent}digitalWrite({a1}, {r});\n"
                elif fn == 'delay':
                    self.codigo += f"{indent}delay({a1});\n"
                elif fn == 'write':
                    self.codigo += f"{indent}{r}.write({a1});\n"
                elif fn == 'analogRead':
                    prefijo = ""
                    if r not in self.vars_declaradas:
                        prefijo = "int "
                        self.vars_declaradas.add(r)
                    self.codigo += f"{indent}{prefijo}{r} = analogRead({a1});\n"
                elif fn == 'pulseIn':
                    prefijo = ""
                    if r not in self.vars_declaradas:
                        prefijo = "long "
                        self.vars_declaradas.add(r)
                    self.codigo += f"{indent}{prefijo}{r} = pulseIn({a1}, HIGH);\n"

        self.codigo += "}\n"
        return self.codigo