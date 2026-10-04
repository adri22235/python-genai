import os
import sys
import time
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: Falta GEMINI_API_KEY")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# 1. Instrucción de sistema experta con auto-verificación obligatoria
system_instruction = (
    "Eres un examinador jefe y profesor titular de autoescuela experto en la normativa de la DGT (Dirección General de Tráfico de España).\n"
    "REGLA DE AUTO-VERIFICACIÓN OBLIGATORIA:\n"
    "1. Analiza cuidadosamente las preguntas trampa clásicas de la DGT (semáforos especiales de túneles/carril/peaje que carecen de fase verde y se apagan para permitir el paso, maniobras en calles cortadas, prioridades en tramos estrechos, etc.).\n"
    "2. En tu proceso de pensamiento, comprueba si la pregunta se refiere a una señalización especial de túnel antes de asumir la regla general de semáforos circulares.\n"
    "3. Formatea la respuesta siempre con la plantilla oficial:\n"
    "• Respuesta correcta: [Letra]) [Texto de la opción]\n"
    "• Explicación: [Fundamentación normativa detallada]"
)

# 2. Configuración con Thinking + Top P 0.95 + System Instruction
config = types.GenerateContentConfig(
    temperature=1.0,
    top_p=0.95,
    system_instruction=system_instruction,
    thinking_config=types.ThinkingConfig(
        thinking_budget=8192
    )
)

prompt = (
    "Pregunta de examen DGT / TodoTest:\n"
    "¿Qué haremos al encontrar un semáforo rojo en la entrada de un túnel?\n"
    "a) Pasar con precaución.\n"
    "b) Esperar hasta que cambie a verde.\n"
    "c) Esperar hasta que se apague la luz roja.\n\n"
    "Aplica la auto-verificación sobre la señalización específica de túneles y da la respuesta correcta."
)

models_to_try = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"]

print("=" * 65)
print("🧠 PROBANDO AUTO-VERIFICACIÓN DGT + TOP P 0.95 + SYSTEM INSTRUCTION:")
print("=" * 65)

for model_name in models_to_try:
    print(f"\n⚡ Ejecutando en [{model_name}] con auto-verificación activa...")
    for attempt in range(1, 4):
        try:
            start_time = time.time()
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            elapsed = time.time() - start_time
            print(f"\n--- 📄 RESPUESTA OFICIAL EN {elapsed:.2f}s [{model_name}] ---")
            print(response.text)
            print("---------------------------------------------------------------")
            print("✅ ¡CONSULTA CON AUTO-VERIFICACIÓN DGT COMPLETADA!")
            sys.exit(0)
        except Exception as e:
            if "503" in str(e) or "high demand" in str(e).lower():
                print(f"⚠️ Servidor ocupado (503). Reintentando en 3s (Intento {attempt}/3)...")
                time.sleep(3)
            else:
                print(f"❌ Error con {model_name}: {e}")
                break

print("\n❌ Servidores saturados. Prueba en un momento.")
