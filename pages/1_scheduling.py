import streamlit as st
import pandas as pd
import plotly.express as px
import time
from algorithms import fifo, sjf, srtf, round_robin, priority


st.set_page_config(page_title="Simulador de Calendarización", layout="wide")
st.title("📅 Simulación de Algoritmos de Calendarización")

uploaded_file = st.file_uploader("📂 Cargar archivo de procesos (.txt)", type="txt")

if uploaded_file:
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

    st.subheader("⚙️ Seleccionar algoritmos a simular")
    algos = st.multiselect(
        "Selecciona uno o más algoritmos:",
        ["FIFO", "SJF", "SRTF", "Round Robin", "Priority"]
    )

    quantum = None
    if "Round Robin" in algos:
        quantum = st.number_input("⏱ Quantum para Round Robin:", min_value=1, step=1, value=2)

    simulate_step_by_step = st.checkbox("🌀 Simulación paso a paso", value=True)

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

                st.markdown("#### 🕒 Diagrama de Gantt (simulación animada)")
                gantt = resultado["timeline"]
                gantt_placeholder = st.empty()

                df_gantt = pd.DataFrame(columns=["Proceso", "Inicio", "Fin", "Duración", "Base"])

                for bloque in gantt:
                    new_row = {
                        "Proceso": bloque["pid"],
                        "Inicio": bloque["start"],
                        "Fin": bloque["end"],
                        "Duración": bloque["end"] - bloque["start"],
                        "Base": bloque["start"]
                    }
                    df_gantt = pd.concat([df_gantt, pd.DataFrame([new_row])], ignore_index=True)

                    fig = px.bar(
                        df_gantt,
                        y="Proceso",
                        x="Duración",
                        color="Proceso",
                        orientation="h",
                        text="Duración",
                        base="Base",
                        hover_data=["Inicio", "Fin"]
                    )
                    fig.update_layout(
                        title="Diagrama de Gantt (basado en ciclos)",
                        xaxis_title="Ciclo",
                        yaxis_title="Proceso",
                        barmode="stack"
                    )
                    gantt_placeholder.plotly_chart(fig, use_container_width=True)

                    if simulate_step_by_step:
                        time.sleep(0.3 * new_row["Duración"])

                st.markdown("#### 📈 Métricas de eficiencia")
                st.metric("Tiempo promedio de espera", f"{resultado['avg_waiting_time']:.2f} ciclos")
                total_time = max(b['end'] for b in gantt)
                st.metric("Tiempo total de ejecución", f"{total_time} ciclos")

else:
    st.warning("Por favor, carga un archivo de procesos válido para comenzar.")