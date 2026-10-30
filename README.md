# Práctica: Sistema de Procesamiento de Documentos Concurrentes

## Trabajadores concurrentes
- Medina
- Candia
- Ricardo
- Arturo

---

## Preguntas y Respuestas Teóricas

### 1. ¿Por qué `queue.Queue` es apropiada para compartir trabajos?
`queue.Queue` es una estructura de datos diseñada específicamente para entornos multi-hilo (*thread-safe*). Maneja internamente las primitivas de sincronización necesarias para que operaciones como `put()` y `get_nowait()` sean atómicas. Esto asegura que dos trabajadores no puedan extraer el mismo documento simultáneamente y evita condiciones de carrera sobre la cola sin necesidad de implementar locks externos adicionales.

### 2. ¿Qué protege `Lock` y qué pasaría si se actualizara el resumen sin él?
El `Lock` (`threading.Lock()`) protege el acceso y la modificación concurrente de los diccionarios compartidos `resultados` y `tamanos`. 
En Python, operaciones como `resultados[nombre] += 1` o `tamanos[nombre] += tamano` no son atómicas a nivel de máquina/bytecode (involucran lectura, incremento y reasignación). Si dos hilos intentan actualizar los diccionarios al mismo tiempo sin un lock, ocurre una **condición de carrera (race condition)** donde una actualización sobreescribe a la otra, perdiéndose conteos y dando un total menor a 24.

### 3. ¿Qué cambiarías si cada documento tuviera que guardarse en un archivo real?
Depende de cómo se organice la persistencia:
- **Archivo único compartido** (ej. `salida.txt`): Se debe utilizar un `Lock` para sincronizar las operaciones de escritura (`file.write(...)`), evitando que las líneas se intercalen o se corrompa el contenido del archivo.
- **Archivo individual por trabajador** (ej. `Medina.txt`, `Candia.txt`): No se requiere lock para la escritura en disco, ya que cada hilo maneja su propio descriptor de archivo de forma independiente.
- **Archivo individual por documento** (ej. `doc_1.txt`, `doc_2.txt`): Dado que cada documento se extrae de forma única de la cola, cada hilo escribe en un archivo con nombre distinto, por lo que tampoco se requiere lock entre hilos.

---

## Reto Adicional: Comparación Secuencial vs Concurrente

### Comparación de Tiempos
- **Versión secuencial**: Un solo hilo procesaría los 24 documentos uno tras otro. Si la suma de los tamaños simulados promedia entre 65 y 75 unidades a razón de `tamano * 0.1` s cada una, el tiempo total secuencial es de **~7 a 8 segundos**.
- **Versión con 4 hilos concurrentes**: Al distribuirse el trabajo entre Medina, Candia, Ricardo y Arturo en paralelo, el tiempo total se reduce a **~1.9 a 2.1 segundos**.

### ¿Por qué la diferencia puede ser pequeña en este ejemplo artificial?
1. **Sobrecarga de gestión de hilos (Overhead)**: El sistema operativo incurre en tiempo para crear los hilos, cambiar de contexto y coordinar la sincronización del `Lock`.
2. **Duración muy corta de las tareas**: Al multiplicar el tamaño por `0.1`, las pausas duran apenas décimas de segundo (0.1 a 0.5 s), haciendo que el tiempo de gestión del sistema represente una porción más visible en proporción al tiempo de cálculo real.
3. **GIL (Global Interpreter Lock)**: Aunque `time.sleep()` libera el GIL permitiendo verdadera concurrencia durante la espera, en operaciones CPU-intensivas puras en Python el GIL limitaría la paralelización a un solo núcleo.

---

## Verificaciones del Sistema
- **Verificación 1**: La suma de los documentos completados por los 4 trabajadores es exactamente 24.
- **Verificación 2**: Cada documento de la cola compartida es extraído y procesado exactamente una vez.
- **Verificación 3**: Los cuatro hilos finalizan su ejecución de forma controlada mediante `get_nowait()` y la captura de `queue.Empty`, sin quedarse bloqueados en el `join()`.
