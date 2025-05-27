# 🧠 Simulador de Algoritmos de Planificación y Sincronización

Este proyecto es una aplicación educativa desarrollada en **Python** con **Streamlit**, que permite visualizar de forma interactiva y animada cómo funcionan los **algoritmos de planificación** de procesos y los **mecanismos de sincronización** como **mutex** y **semáforos**.

## 🚀 Características principales

- Visualización animada de algoritmos de planificación:
  - FIFO
  - SJF
  - SRTF
  - Round Robin (con configuración de Quantum)
  - Priority Scheduling
- Simulación paso a paso de sincronización con:
  - Mutex (exclusión mutua)
  - Semáforo (con reintentos automáticos)
- Visualización con **Diagramas de Gantt interactivos**
- Tablas resumen con métricas clave (% de éxito, accesos, esperas)

---

## 📂 Estructura del proyecto

```
project/
│
├── algorithms/              # Lógica de planificación (FIFO, SJF, etc.)
│   ├── fifo.py
│   ├── sjf.py
│   ├── srtf.py
│   ├── round_robin.py
│   ├── priority.py
│
├── pages/                   # Páginas de Streamlit
│   └── 2_sync.py            # Simulación de sincronización (Mutex y Semáforo)
│
├── app.py                   # Página principal (planificación)
├── requirements.txt         # Requisitos del proyecto
└── README.md                # Este archivo
```

---

## ⚙️ Requisitos

- Python 3.10+
- pip

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

> Si no tienes Streamlit:
```bash
pip install streamlit
```

---

## 🧭 ¿Cómo levantar el proyecto?

Desde la raíz del proyecto, ejecuta:

```bash
streamlit run app.py
```

Y luego puedes cambiar entre páginas desde el **sidebar** (por ejemplo, para ir a `2_sync.py`).

---

## 📄 Estructura de archivos de entrada

### 📌 Archivo de procesos (`process.txt`)
```
P1,5,0,1
P2,4,1,2
P3,3,2,3
```
Formato: `pid,burst_time,arrival_time,priority`

---

### 📌 Archivo de recursos (`resources.txt`)
```
R1,1
R2,2
```
Formato: `nombre_recurso,cantidad`

---

### 📌 Archivo de acciones (`actions.txt`)
```
P1,READ,R1,0
P2,WRITE,R2,1
```
Formato: `pid,acción,recurso,ciclo`

---

## 🧩 Funciones clave

### 📍 Algoritmos de planificación (`algorithms/`)
Cada archivo implementa una función principal como:

```python
def fifo_scheduler(procesos): -> dict
    return {
        'timeline': [...],
        'avg_waiting_time': ...
    }
```

---

### 📍 Mutex (en `2_sync.py`)

```python
if estado_recursos[recurso] > 0:
    estado = "ACCESSED"
else:
    estado = "WAITING"
```

Los recursos son liberados al final del ciclo y se usa Plotly para animación Gantt.

---

### 📍 Semáforo (en `2_sync.py`)

```python
if estado_recursos[recurso] > 0:
    estado = "ACCESSED"
elif intentos >= 5:
    estado = "FAILED"
else:
    estado = "WAITING"
    # Se reintenta en el siguiente ciclo
```

---

## 📊 Resultados

- **Gantt dinámico:** muestra en tiempo real los accesos y bloqueos.
- **Resumen por proceso:** incluye accesos, bloqueos y porcentaje de éxito.

---

## 🧑‍💻 Autor

Desarrollado por Davis Roldan – Universidad del Valle de Guatemala.

---

