import threading
import time
import random
from queue import Queue, Empty

trabajos = Queue()
lock = threading.Lock()
resultados = {}
tamanos = {}

for doc_id in range(1, 25):
    trabajos.put((doc_id, random.randint(1, 5)))

def trabajador(nombre, lock):
    while True:
        try:
            doc_id, tamano = trabajos.get_nowait()
        except Empty:
            break

        print(f"[{nombre}] Procesando documento {doc_id} (Tamaño: {tamano})...")
        time.sleep(tamano * 0.1)

        with lock:
            resultados[nombre] = resultados.get(nombre, 0) + 1
            tamanos[nombre] = tamanos.get(nombre, 0) + tamano
            print(f"[{nombre}] -> Completó documento {doc_id}")

nombres = ["Medina", "Candia", "Ricardo", "Arturo"]
hilos = []

inicio = time.time()

for nombre in nombres:
    hilo = threading.Thread(target=trabajador, args=(nombre, lock))
    hilos.append(hilo)
    hilo.start()

for hilo in hilos:
    hilo.join()

tiempo_total = time.time() - inicio

print("\nTotal procesado:", sum(resultados.values()))
print("Tiempo total:", round(tiempo_total, 2), "segundos")
print("Resumen por trabajador:")
for nombre in nombres:
    print(f"- {nombre}: {resultados.get(nombre, 0)} documentos | tamaño total: {tamanos.get(nombre, 0)}")
