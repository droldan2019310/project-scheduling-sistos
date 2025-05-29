import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Simulación de Sincronización", layout="wide")
st.title("🔒 Simulación de Mecanismos de Sincronización")

# Sidebar
st.sidebar.header("Configuración")
modo = st.sidebar.selectbox("Modo de sincronización", ["Mutex", "Semáforo"])

# Carga de archivos
procesos_file = st.file_uploader("📂 Cargar archivo de procesos", type="txt", key="procesos")
recursos_file = st.file_uploader("📂 Cargar archivo de recursos", type="txt", key="recursos")
acciones_file = st.file_uploader("📂 Cargar archivo de acciones", type="txt", key="acciones")

def cargar_procesos(file):
    procesos = []
    errores = []
    lines = file.read().decode("utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        partes = [p.strip() for p in line.split(",")]
        if len(partes) != 4:
            errores.append(f"Línea {i} procesos: formato inválido (4 valores esperados)")
            continue
        pid, bt, at, pr = partes
        try:
            bt = int(bt)
            at = int(at)
            pr = int(pr)
        except ValueError:
            errores.append(f"Línea {i} procesos: burst_time, arrival_time y priority deben ser enteros")
            continue
        procesos.append({
            "pid": pid,
            "burst_time": bt,
            "arrival_time": at,
            "priority": pr
        })
    return procesos, errores

def cargar_recursos(file):
    recursos = {}
    errores = []
    lines = file.read().decode("utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        partes = [p.strip() for p in line.split(",")]
        if len(partes) != 2:
            errores.append(f"Línea {i} recursos: formato inválido (2 valores esperados)")
            continue
        nombre, contador = partes
        try:
            contador = int(contador)
        except ValueError:
            errores.append(f"Línea {i} recursos: contador debe ser entero")
            continue
        recursos[nombre] = contador
    return recursos, errores

def cargar_acciones(file):
    acciones = []
    errores = []
    lines = file.read().decode("utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        partes = [p.strip() for p in line.split(",")]
        if len(partes) != 4:
            errores.append(f"Línea {i} acciones: formato inválido (4 valores esperados)")
            continue
        pid, accion, recurso, ciclo = partes
        try:
            ciclo = int(ciclo)
        except ValueError:
            errores.append(f"Línea {i} acciones: ciclo debe ser entero")
            continue
        acciones.append({
            "pid": pid,
            "accion": accion.upper(),
            "recurso": recurso,
            "ciclo": ciclo
        })
    return acciones, errores

# Solo continuar si los 3 archivos están cargados
if procesos_file and recursos_file and acciones_file:
    procesos, err_procesos = cargar_procesos(procesos_file)
    recursos, err_recursos = cargar_recursos(recursos_file)
    acciones, err_acciones = cargar_acciones(acciones_file)

    errores_totales = err_procesos + err_recursos + err_acciones
    if errores_totales:
        st.error("Se encontraron errores en los archivos:")
        for err in errores_totales:
            st.write(f"- {err}")

    if procesos and recursos and acciones:
        st.success("✅ Archivos validados correctamente y listos para simular.")

        # Mostrar tablas resumen
        st.markdown("## 📊 Datos cargados")

        st.markdown("### 📋 Procesos")
        df_procesos = pd.DataFrame(procesos)
        st.dataframe(df_procesos, use_container_width=True)

        st.markdown("### 🧩 Recursos")
        df_recursos = pd.DataFrame([{"Recurso": r, "Contador Inicial": c} for r, c in recursos.items()])
        st.dataframe(df_recursos, use_container_width=True)

        st.markdown("### 🎬 Acciones")
        df_acciones = pd.DataFrame(acciones)
        st.dataframe(df_acciones, use_container_width=True)

        # Botón para iniciar simulación
        if st.button("🚀 Empezar simulación"):

            if modo == "Mutex":
                st.subheader("🔄 Simulación paso a paso (Mutex)")

                estado_recursos = recursos.copy()
                ciclo_max = max(a['ciclo'] for a in acciones)
                acciones_ordenadas = sorted(acciones, key=lambda a: a['ciclo'])

                gantt_placeholder = st.empty()
                df_gantt = pd.DataFrame(columns=["Proceso", "Recurso", "Inicio", "Fin", "Estado"])

                recursos_ocupados = {}

                for ciclo in range(ciclo_max + 1):
                    acciones_en_ciclo = [a for a in acciones_ordenadas if a['ciclo'] == ciclo]

                    recursos_usados_este_ciclo = []

                    for accion in acciones_en_ciclo:
                        pid = accion["pid"]
                        recurso = accion["recurso"]
                        estado = ""

                        if estado_recursos[recurso] > 0:
                            estado = "ACCESSED"
                            estado_recursos[recurso] -= 1
                            recursos_usados_este_ciclo.append(recurso)
                        else:
                            estado = "WAITING"

                        df_gantt = pd.concat([
                            df_gantt,
                            pd.DataFrame([{
                                "Proceso": pid,
                                "Recurso": recurso,
                                "Inicio": ciclo,
                                "Fin": ciclo + 1,
                                "Estado": estado
                            }])
                        ])

                    if ciclo in recursos_ocupados:
                        for recurso in recursos_ocupados[ciclo]:
                            if estado_recursos[recurso] < recursos[recurso]:
                                estado_recursos[recurso] += 1
                        del recursos_ocupados[ciclo]

                    if recursos_usados_este_ciclo:
                        recursos_ocupados[ciclo + 1] = recursos_ocupados.get(ciclo + 1, []) + recursos_usados_este_ciclo

                    color_map = {"ACCESSED": "green", "WAITING": "red"}
                    fig = px.bar(
                        df_gantt,
                        x="Inicio",
                        y="Proceso",
                        color="Estado",
                        color_discrete_map=color_map,
                        orientation="h",
                        text="Recurso",
                        base="Inicio",
                        hover_data=["Inicio", "Fin", "Estado", "Recurso"]
                    )
                    fig.update_layout(
                        xaxis_title="Ciclo",
                        yaxis_title="Proceso",
                        title=f"Simulación Mutex - Ciclo {ciclo}",
                        barmode="stack"
                    )
                    gantt_placeholder.plotly_chart(fig, use_container_width=True)
                    time.sleep(0.5)

            elif modo == "Semáforo":
                st.subheader("🔄 Simulación paso a paso (Semáforo)")

                estado_recursos = recursos.copy()
                ciclo_max = max(a['ciclo'] for a in acciones)
                pendientes = []
                df_gantt = pd.DataFrame(columns=["Proceso", "Recurso", "Inicio", "Fin", "Estado"])
                procesos_activos = {}  # {(pid, recurso): ciclo_fin}
                gantt_placeholder = st.empty()

                for ciclo in range(ciclo_max + 10):
                    st.write(f"**Ciclo {ciclo}** - Estado recursos: {estado_recursos}")

                    # Liberar recursos
                    procesos_a_liberar = []
                    for (pid, recurso), ciclo_fin in procesos_activos.items():
                        if ciclo >= ciclo_fin:
                            estado_recursos[recurso] += 1
                            procesos_a_liberar.append((pid, recurso))
                            st.write(f"   ✅ {pid} libera {recurso}")

                    for key in procesos_a_liberar:
                        del procesos_activos[key]

                    # Nuevas solicitudes
                    nuevas_solicitudes = [a for a in acciones if a['ciclo'] == ciclo]
                    for solicitud in nuevas_solicitudes:
                        pendientes.append(solicitud)
                        st.write(f"   📥 {solicitud['pid']} solicita {solicitud['recurso']}")

                    pendientes_siguiente_ciclo = []

                    # Procesar solicitudes pendientes
                    for solicitud in pendientes:
                        pid = solicitud["pid"]
                        recurso = solicitud["recurso"]
                        intentos = solicitud.get("intentos", 0)

                        if estado_recursos[recurso] > 0:
                            estado_recursos[recurso] -= 1
                            procesos_activos[(pid, recurso)] = ciclo + 1

                            nuevo_registro = pd.DataFrame([{
                                "Proceso": pid,
                                "Recurso": recurso,
                                "Inicio": ciclo,
                                "Fin": ciclo + 1,
                                "Estado": "ACCESSED",
                                "ID": f"{pid}-{recurso}-{ciclo}-ACCESSED"
                            }])
                            df_gantt = pd.concat([df_gantt, nuevo_registro], ignore_index=True)

                            st.write(f"   ✅ {pid} accede a {recurso}")

                        elif intentos >= 5:
                            nuevo_registro = pd.DataFrame([{
                                "Proceso": pid,
                                "Recurso": recurso,
                                "Inicio": ciclo,
                                "Fin": ciclo + 1,
                                "Estado": "FAILED",
                                "ID": f"{pid}-{recurso}-{ciclo}-FAILED"
                            }])
                            df_gantt = pd.concat([df_gantt, nuevo_registro], ignore_index=True)

                            st.write(f"   ❌ {pid} falla al acceder a {recurso} (muchos intentos)")

                        else:
                            nueva_solicitud = solicitud.copy()
                            nueva_solicitud["intentos"] = intentos + 1
                            pendientes_siguiente_ciclo.append(nueva_solicitud)

                            nuevo_registro = pd.DataFrame([{
                                "Proceso": pid,
                                "Recurso": recurso,
                                "Inicio": ciclo,
                                "Fin": ciclo + 1,
                                "Estado": "WAITING",
                                "ID": f"{pid}-{recurso}-{ciclo}-WAITING"
                            }])
                            df_gantt = pd.concat([df_gantt, nuevo_registro], ignore_index=True)

                            st.write(f"   ⏳ {pid} espera por {recurso} (intento {intentos + 1})")

                    pendientes = pendientes_siguiente_ciclo

                    # Graficar Gantt
                    color_map = {
                        "ACCESSED": "blue",
                        "WAITING": "orange",
                        "FAILED": "red"
                    }

                    if not df_gantt.empty:
                        fig = go.Figure()

                        for _, row in df_gantt.iterrows():
                            color = color_map.get(row['Estado'], 'gray')
                            fig.add_trace(go.Bar(
                                name=row['Estado'],
                                x=[row['Fin'] - row['Inicio']],
                                y=[row['Proceso']],
                                base=[row['Inicio']],
                                orientation='h',
                                marker=dict(color=color),
                                text=row['Recurso'],
                                textposition='inside',
                                showlegend=False,
                                hovertemplate=f"<b>{row['Proceso']}</b><br>" +
                                              f"Recurso: {row['Recurso']}<br>" +
                                              f"Estado: {row['Estado']}<br>" +
                                              f"Ciclo: {row['Inicio']}-{row['Fin']}<extra></extra>"
                            ))

                        for estado, color in color_map.items():
                            if estado in df_gantt['Estado'].values:
                                fig.add_trace(go.Bar(
                                    name=estado,
                                    x=[None],
                                    y=[None],
                                    marker=dict(color=color),
                                    showlegend=True
                                ))

                        fig.update_layout(
                            title=f"Simulación Semáforo - Ciclo {ciclo}",
                            xaxis_title="Ciclo",
                            yaxis_title="Proceso",
                            barmode="overlay",
                            showlegend=True,
                            legend=dict(title="Estado")
                        )

                        gantt_placeholder.plotly_chart(fig, use_container_width=True)

                    time.sleep(1)

                    if not pendientes and not procesos_activos and ciclo > ciclo_max:
                        break

                # Resumen final
                st.subheader("📊 Resumen por proceso")

                if not df_gantt.empty:
                    resumen_data = []

                    for proceso in df_gantt['Proceso'].unique():
                        df_proceso = df_gantt[df_gantt['Proceso'] == proceso]

                        accesos = len(df_proceso[df_proceso['Estado'] == 'ACCESSED'])
                        esperas = len(df_proceso[df_proceso['Estado'] == 'WAITING'])
                        fallidas = len(df_proceso[df_proceso['Estado'] == 'FAILED'])
                        total = accesos + esperas + fallidas

                        porcentaje_exito = (accesos / total * 100) if total > 0 else 0

                        resumen_data.append({
                            'Proceso': proceso,
                            'Accesos': accesos,
                            'Esperas': esperas,
                            'Fallidas': fallidas,
                            '% Éxito': round(porcentaje_exito, 4)
                        })

                    df_resumen = pd.DataFrame(resumen_data)
                    st.dataframe(df_resumen, use_container_width=True, height=300)
                else:
                    st.write("No hay datos para mostrar en el resumen.")

    else:
        st.warning("⚠️ Por favor, corrige los errores antes de continuar.")

else:
    st.warning("⚠️ Por favor, carga los tres archivos para comenzar.")
