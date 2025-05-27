import streamlit as st
import pandas as pd
import plotly.express as px
import time
import plotly.graph_objects as go

st.set_page_config(page_title="Simulación de Sincronización", layout="wide")
st.title("🔒 Simulación de Mecanismos de Sincronización")

# Sidebar
st.sidebar.header("Configuración")
modo = st.sidebar.selectbox("Modo de sincronización", ["Mutex", "Semáforo"])

# Carga de archivos
procesos_file = st.file_uploader("📂 Cargar archivo de procesos", type="txt", key="procesos")
recursos_file = st.file_uploader("📂 Cargar archivo de recursos", type="txt", key="recursos")
acciones_file = st.file_uploader("📂 Cargar archivo de acciones", type="txt", key="acciones")

if procesos_file and recursos_file and acciones_file:
    # Cargar procesos
    procesos = []
    for line in procesos_file.read().decode("utf-8").splitlines():
        pid, bt, at, pr = line.strip().split(",")
        procesos.append({
            "pid": pid.strip(),
            "burst_time": int(bt.strip()),
            "arrival_time": int(at.strip()),
            "priority": int(pr.strip())
        })

    # Cargar recursos
    recursos = {}
    for line in recursos_file.read().decode("utf-8").splitlines():
        nombre, contador = line.strip().split(",")
        recursos[nombre.strip()] = int(contador.strip())

    # Cargar acciones
    acciones = []
    for line in acciones_file.read().decode("utf-8").splitlines():
        pid, accion, recurso, ciclo = line.strip().split(",")
        acciones.append({
            "pid": pid.strip(),
            "accion": accion.strip().upper(),
            "recurso": recurso.strip(),
            "ciclo": int(ciclo.strip())
        })

    st.success("✅ Archivos cargados correctamente")

    st.markdown("## 📊 Datos cargados")

    # Tabla 1: Procesos
    st.markdown("### 📋 Procesos")
    df_procesos = pd.DataFrame(procesos)
    st.dataframe(df_procesos, use_container_width=True)

    # Tabla 2: Recursos
    st.markdown("### 🧩 Recursos")
    df_recursos = pd.DataFrame([{"Recurso": r, "Contador Inicial": c} for r, c in recursos.items()])
    st.dataframe(df_recursos, use_container_width=True)

    # Tabla 3: Acciones
    st.markdown("### 🎬 Acciones")
    df_acciones = pd.DataFrame(acciones)
    st.dataframe(df_acciones, use_container_width=True)


    # Solo implementamos Mutex por ahora
    if modo == "Mutex":
        st.subheader("🔄 Simulación paso a paso (Mutex)")

        estado_recursos = recursos.copy()
        ciclo_max = max(a['ciclo'] for a in acciones)
        acciones_ordenadas = sorted(acciones, key=lambda a: a['ciclo'])

        gantt_placeholder = st.empty()
        df_gantt = pd.DataFrame(columns=["Proceso", "Recurso", "Inicio", "Fin", "Estado"])

        # Recursos ocupados previamente (a liberar DESPUÉS de evaluar el ciclo)
        recursos_ocupados = {}

        for ciclo in range(ciclo_max + 1):
            acciones_en_ciclo = [a for a in acciones_ordenadas if a['ciclo'] == ciclo]

            recursos_usados_este_ciclo = []

            # ✅ Primero: procesar acciones
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

            # ✅ Segundo: liberar recursos ocupados previamente
            if ciclo in recursos_ocupados:
                for recurso in recursos_ocupados[ciclo]:
                    if estado_recursos[recurso] < recursos[recurso]:
                        estado_recursos[recurso] += 1
                del recursos_ocupados[ciclo]

            # ✅ Registrar los recursos usados este ciclo para liberar después
            if recursos_usados_este_ciclo:
                recursos_ocupados[ciclo + 1] = recursos_ocupados.get(ciclo + 1, []) + recursos_usados_este_ciclo

            # Dibujar gráfico
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

        # Estado inicial de recursos (semáforos)
        estado_recursos = recursos.copy()
        ciclo_max = max(a['ciclo'] for a in acciones)
        
        # Cola de procesos pendientes por recurso
        pendientes = []
        
        # DataFrame para el gráfico Gantt
        df_gantt = pd.DataFrame(columns=["Proceso", "Recurso", "Inicio", "Fin", "Estado"])
        
        # Procesos actualmente usando recursos (para liberarlos después)
        procesos_activos = {}  # {(proceso, recurso): ciclo_fin}
        
        gantt_placeholder = st.empty()
        
        for ciclo in range(ciclo_max + 10):  # Ciclos adicionales para procesos pendientes
            st.write(f"**Ciclo {ciclo}** - Estado recursos: {estado_recursos}")
            
            # 1. LIBERAR RECURSOS de procesos que terminaron
            procesos_a_liberar = []
            for (pid, recurso), ciclo_fin in procesos_activos.items():
                if ciclo >= ciclo_fin:
                    estado_recursos[recurso] += 1
                    procesos_a_liberar.append((pid, recurso))
                    st.write(f"   ✅ {pid} libera {recurso}")
            
            for key in procesos_a_liberar:
                del procesos_activos[key]
            
            # 2. NUEVAS SOLICITUDES en este ciclo
            nuevas_solicitudes = [a for a in acciones if a['ciclo'] == ciclo]
            for solicitud in nuevas_solicitudes:
                pendientes.append(solicitud)
                st.write(f"   📥 {solicitud['pid']} solicita {solicitud['recurso']}")
            
            # 3. PROCESAR SOLICITUDES PENDIENTES
            pendientes_siguiente_ciclo = []
            
            for solicitud in pendientes:
                pid = solicitud["pid"]
                recurso = solicitud["recurso"]
                intentos = solicitud.get("intentos", 0)
                
                # Verificar si el recurso está disponible
                if estado_recursos[recurso] > 0:
                    # ACCESO CONCEDIDO
                    estado_recursos[recurso] -= 1
                    procesos_activos[(pid, recurso)] = ciclo + 1  # Se libera en el siguiente ciclo
                    
                    # Registrar en Gantt
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
                    # FALLO DESPUÉS DE MUCHOS INTENTOS
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
                    # ESPERA - recurso no disponible
                    nueva_solicitud = solicitud.copy()
                    nueva_solicitud["intentos"] = intentos + 1
                    pendientes_siguiente_ciclo.append(nueva_solicitud)
                    
                    # Registrar estado de espera en Gantt
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
            
            # Actualizar pendientes para el siguiente ciclo
            pendientes = pendientes_siguiente_ciclo
            
            # 4. ACTUALIZAR GRÁFICO GANTT
            color_map = {
                "ACCESSED": "blue",
                "WAITING": "orange", 
                "FAILED": "red"
            }
            
            if not df_gantt.empty:
                # Versión simplificada del gráfico de Gantt
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
                
                # Agregar leyenda manual
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
            
            # Pausa para animación
            time.sleep(1)
            
            # Condición de parada: no hay más pendientes y no hay procesos activos
            if not pendientes and not procesos_activos and ciclo > ciclo_max:
                break
        
        # 5. TABLA RESUMEN FINAL
        st.subheader("📊 Resumen por proceso")
        
        if not df_gantt.empty:
            # Agrupar por proceso y estado
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
    st.warning("⚠️ Por favor, carga los tres archivos para comenzar.")
