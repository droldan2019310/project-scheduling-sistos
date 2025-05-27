import streamlit as st
import pandas as pd
import time
from algorithms import fifo, sjf, srtf, round_robin, priority

st.set_page_config(page_title="Simulador de Planificación de Procesos", layout="wide")

# ===== Estilo general =====
st.title("🎯 Simulador de Algoritmos de Calendarización")
st.markdown("Carga tus procesos y selecciona uno o más algoritmos para simular visualmente su comportamiento.")

# ===== Carga del archivo .txt =====
uploaded_file = st.file_uploader("📂 Cargar archivo de procesos (.txt)", type="txt")

if uploaded_file:
    # Leer datos
    content = uploaded_file.read().decode("utf-8").splitlines()
    procesos = []
    for line in content:
        pid, bt, at, pr = line.strip().split(",")
        procesos.append({
            "pid": pid.strip(),
            "burst_time": int(bt.strip()),
            "arrival_time": int(at.strip()),
            "priority": int(pr.strip())
        })

    df = pd.DataFrame(procesos)
    st.subheader("📋 Procesos cargados")
    st.dataframe(df)

    # ===== Selección de algoritmos =====
    st.subheader("⚙️ Seleccionar algoritmos a simular")
    algos = st.multiselect(
        "Selecciona uno o más algoritmos:",
        ["FIFO", "SJF", "SRTF", "Round Robin", "Priority"]
    )

    quantum = None
    if "Round Robin" in algos:
        quantum = st.number_input("⏱ Quantum para Round Robin:", min_value=1, step=1, value=2)

    # ===== Ejecutar simulación =====
    if st.button("🚀 Ejecutar simulación"):
        st.subheader("📊 Resultados de simulación")

        tabs = st.tabs(algos)
        for i, algo in enumerate(algos):
            with tabs[i]:
                st.markdown(f"### Algoritmo: `{algo}`")
                if algo == "FIFO":
                    resultado = fifo.fifo_scheduler(procesos)
                elif algo == "SJF":
                    resultado = sjf.sjf_scheduler(procesos)
                elif algo == "SRTF":
                    resultado = srtf.srtf_scheduler(procesos)
                elif algo == "Round Robin":
                    resultado = round_robin.round_robin_scheduler(procesos, quantum)
                elif algo == "Priority":
                    resultado = priority.priority_scheduler(procesos)
                else:
                    st.error("Algoritmo no implementado.")
                    continue

                # ===== Mostrar Gantt =====
                st.markdown("#### 🕒 Diagrama de Gantt (simulación dinámica)")
                gantt = resultado["timeline"]
                gantt_container = st.empty()

                chart_data = []
                for i, bloque in enumerate(gantt):
                    chart_data.append({
                        "Proceso": bloque["pid"],
                        "Inicio": bloque["start"],
                        "Fin": bloque["end"]
                    })
                    gantt_df = pd.DataFrame(chart_data)
                    gantt_container.bar_chart(
                        gantt_df.set_index("Proceso")[["Inicio", "Fin"]].T
                    )
                    time.sleep(0.4)

                # ===== Mostrar métricas =====
                st.markdown("#### 📈 Métricas de eficiencia")
                st.metric("Tiempo promedio de espera", f"{resultado['avg_waiting_time']:.2f} ciclos")
                total_time = max(b['end'] for b in gantt)
                st.metric("Tiempo total de ejecución", f"{total_time} ciclos")

else:
    st.warning("Por favor, carga un archivo de procesos válido para comenzar.")