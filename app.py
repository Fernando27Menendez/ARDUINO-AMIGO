import json
from flask import Flask, render_template, request
from Lexer import get_tokens
from Parser import Parser
from Generador import Generador

app = Flask(__name__)

EJEMPLOS = {
    "1. Básico: Semáforo Inteligente": """configuracion:
  numpin led_rojo = 13;
  numpin led_amarillo = 12;
  numpin led_verde = 11;
  configurar (led_rojo, salida);
  configurar (led_amarillo, salida);
  configurar (led_verde, salida);
fin
circuito:
  encender (led_rojo);
  esperar (5000);
  apagar (led_rojo);
  encender (led_amarillo);
  esperar (2000);
  apagar (led_amarillo);
  encender (led_verde);
  esperar (5000);
  apagar (led_verde);
fin""",

    "2. Intermedio: Control Temperatura": """configuracion:
  numpin sensor_temperatura = A0;
  numpin motor_ventilador = 9;
  decimal temperatura_maxima = 30.0;
  configurar (motor_ventilador, salida);
fin
circuito:
  numero lectura = leer_sensor(sensor_temperatura);
  decimal temperatura = lectura * 0.48;
  si (temperatura > temperatura_maxima):
    encender (motor_ventilador);
  sino:
    apagar (motor_ventilador);
  fin
  esperar (1000);
fin""",

    "3. Avanzado: Puerta Garage Servo": """incluir libreria "servo.h";
configuracion:
  numpin trigger = 9;
  numpin echo = 10;
  numpin servo_pin = 6;
  decimal distancia_maxima = 20.0;
  configurar (trigger, salida);
  configurar (echo, entrada);
  servo puerta;
  conectar.puerta (servo_pin);
  estado.puerta (0);
fin
circuito:
  apagar (trigger);
  esperar (2);
  encender (trigger);
  esperar (10);
  apagar (trigger);
  numero duracion = pulso.echo;
  numero distancia = duracion * 0.034/2;
  si (distancia < distancia_maxima):
    estado.puerta (90);
  sino:
    estado.puerta (0);
  fin
fin""",

    "4. Básico: Interruptor Simple": """configuracion:
  numpin boton_pulsador = 2;
  numpin foco = 13;
  configurar (boton_pulsador, entrada);
  configurar (foco, salida);
fin
circuito:
  numero estado_boton = leer_sensor(boton_pulsador);
  si (estado_boton == 1):
    encender (foco);
  sino:
    apagar (foco);
  fin
  esperar (100);
fin""",

    "5. Intermedio: Alarma Silenciosa": """configuracion:
  numpin sensor_puerta = 4;
  numpin led_alarma = 8;
  configurar (sensor_puerta, entrada);
  configurar (led_alarma, salida);
fin
circuito:
  numero puerta_cerrada = leer_sensor(sensor_puerta);
  si (puerta_cerrada == 0):
    encender (led_alarma);
    esperar (200);
    apagar (led_alarma);
    esperar (200);
  sino:
    apagar (led_alarma);
  fin
fin""",

    "6. Básico: Luces de Policía": """configuracion:
  numpin luz_azul = 6;
  numpin luz_roja = 7;
  numero tiempo_corto = 100;
  configurar (luz_azul, salida);
  configurar (luz_roja, salida);
fin
circuito:
  encender (luz_azul);
  apagar (luz_roja);
  esperar (tiempo_corto);
  apagar (luz_azul);
  encender (luz_roja);
  esperar (tiempo_corto);
fin""",

    "7. Intermedio: Detector Crepuscular": """configuracion:
  numpin sensor_luz = A1;
  numpin farola = 10;
  numero umbral_oscuridad = 300;
  configurar (farola, salida);
fin
circuito:
  numero luz_actual = leer_sensor(sensor_luz);
  si (luz_actual < umbral_oscuridad):
    encender (farola);
  sino:
    apagar (farola);
  fin
  esperar (1000);
fin""",

    "8. Matemáticas: Mezcladora": """configuracion:
  numpin led_prueba = 13;
  numero contador = 0;
  numero limite = 5;
  configurar (led_prueba, salida);
fin
circuito:
  contador = contador + 1;
  si (contador > limite):
    encender (led_prueba);
    esperar (500);
    apagar (led_prueba);
    esperar (200);
    contador = 0;
  fin
fin""",

    "9. Avanzado: Barrera Estacionamiento": """incluir libreria "servo.h";
configuracion:
  numpin sensor_coche = 3;
  numpin pin_motor = 9;
  configurar(sensor_coche, entrada);
  servo barrera;
  conectar.barrera (pin_motor);
  estado.barrera (0);
fin
circuito:
  numero hay_coche = leer_sensor(sensor_coche);
  si (hay_coche == 1):
    estado.barrera (90);
    esperar (5000);
  sino:
    estado.barrera (0);
  fin
  esperar (500);
fin""",

    "10. Salud: Termómetro Fiebre": """configuracion:
  numpin sensor_temp = A2;
  numpin buzzer = 5;
  decimal fiebre_alta = 38.5;
  configurar (buzzer, salida);
fin
circuito:
  numero datos = leer_sensor(sensor_temp);
  decimal grados = datos * 0.48;
  si (grados > fiebre_alta):
    encender (buzzer);
    esperar (1000);
    apagar (buzzer);
    esperar (2000);
  fin
fin"""
}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', 
                           ejemplos=EJEMPLOS)

@app.route('/compilar', methods=['POST'])
def compilar():
    data = request.get_json()
    codigo = data.get('codigo', '')
    
    if not codigo:
        return json.dumps({'cpp': '', 'tac': [], 'errores': ['No hay código para compilar']}), 400, {'ContentType':'application/json'}

    # FASE 1: LÉXICO
    tokens, errores_lex = get_tokens(codigo)
    
    if errores_lex:
        return json.dumps({'cpp': '', 'tac': [], 'tokens': [], 'errores': errores_lex}), 200, {'ContentType':'application/json'}

    # FASE 2: SINTÁCTICO Y GENERACIÓN TAC
    parser = Parser(tokens)
    
    try:
        parser.parse_programa()
        tac_quads = parser.tac.setup_instructions + parser.tac.loop_instructions
        
        # FASE 3: GENERACIÓN C++
        gen = Generador(parser.tac)
        codigo_ino = gen.obtener_codigo_arduino()
        
        return json.dumps({
            'cpp': codigo_ino,
            'tac': tac_quads,
            'tokens': tokens,
            'errores': []
        }), 200, {'ContentType':'application/json'}
        
    except Exception as e:
        return json.dumps({
            'cpp': '',
            'tac': [],
            'tokens': tokens,
            'errores': [str(e)]
        }), 200, {'ContentType':'application/json'}

if __name__ == '__main__':
    app.run(debug=True)
