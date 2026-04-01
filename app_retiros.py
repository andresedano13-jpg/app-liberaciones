import streamlit as st
import pandas as pd
from datetime import datetime
import os

ARCHIVO_EXCEL = "Messi.xlsx"

COLUMNAS = [
    "Fecha", "Detalle Glosa", "Trimestre", "Monto liberado", 
    "Área solicitante", "División", "Aprobador", 
    "Estado de Solicitud", "Comentarios de Costos", "ID Unico", "Mail Solicitante"
]

# Diccionario para que el Área cambie según la División
AREAS_POR_DIVISION = {
    "1101-La Zanja": [
        "1101006 -SUPERVISION Y SERV. AUX. MINA", "1101007 -PLANEAMIENTO MINA", 
        "1101008 -GEOLOGIA MINA", "1101101 -PLANTA OPERACIONES", 
        "1101102 -TRATAMIENTO AGUAS", "1101103 -MANTENIMIENTO PLANTA", 
        "1101104 -SUPERVISION Y SERV. AUX. PLANT", "1101114 -MANTTO PLANTA AGUAS", 
        "1101201 -GENERACION Y TRANSM. ENERGIA", "1101202 -GESTION DE PROYECTOS", 
        "1101203 -GESTION AMBIENTAL", "1101204 -SEGURIDAD MINERA", 
        "1101205 -GESTION MANTENIMIENTO", "1101206 -GERENCIA DE UNIDAD", 
        "1101207 -LABORATORIO QUIMICO", "1101208 -ADMINISTRACION UNIDAD", 
        "1101210 -RECURSOS HUMANOS", "1101211 -GESTION SOCIAL"
    ],
    "1201-Tantahuatay": [
        "1201001 -EXPLORACION INFILL", "1201004 -EXPLOTACION TAJO ABIERTO", 
        "1201006 -SUPERVISION Y SERV. AUX. MINA", "1201007 -PLANEAMIENTO MINA", 
        "1201008 -GEOLOGIA MINA", "1201010 -AMORTIZACION", 
        "1201101 -PLANTA OPERACIONES", "1201102 -TRATAMIENTO AGUAS", 
        "1201103 -MANTENIMIENTO PLANTA", "1201104 -SUPERVISION Y SERV. AUX. PLANT", 
        "1201114 -MANTTO PLANTA AGUAS", "1201201 -GENERACION Y TRANSM. ENERGIA", 
        "1201202 -GESTION DE PROYECTOS", "1201203 -GESTION AMBIENTAL", 
        "1201204 -SEGURIDAD MINERA", "1201205 -GESTION MANTENIMIENTO", 
        "1201206 -GERENCIA DE UNIDAD", "1201207 -LABORATORIO QUIMICO", 
        "1201208 -ADMINISTRACION UNIDAD", "1201210 -RECURSOS HUMANOS", 
        "1201211 -GESTION SOCIAL"
    ]
}

# 2. MOTOR DE BASE DE DATOS (Conectando con Excel en la nube)
def cargar_datos():
    if os.path.exists(ARCHIVO_EXCEL):
        try:
            return pd.read_excel(ARCHIVO_EXCEL)
        except:
            return pd.DataFrame(columns=COLUMNAS)
    return pd.DataFrame(columns=COLUMNAS)

def guardar_datos(df):
    try:
        df.to_excel(ARCHIVO_EXCEL, index=False)
        return True
    except PermissionError:
        return False

if 'df' not in st.session_state:
    st.session_state.df = cargar_datos()


# 3. INTERFAZ Y NAVEGACIÓN
st.set_page_config(page_title="App Liberaciones", layout="wide")

# Barra lateral de seguridad
st.sidebar.title("🔐 Acceso")
menu_opciones = ["👤 Solicitante (Crear/Rastrear)"] 

st.sidebar.markdown("---")
# Clave
clave = st.sidebar.text_input("Código Área de Costos:", type="password")
if clave == "costos2026": 
    st.sidebar.success("Acceso de administrador concedido")
    menu_opciones.extend(["💼 Área de Costos (Aprobar)", "📊 Ver Historial Completo"])

rol = st.sidebar.radio("Navegación:", menu_opciones)


# --- PANTALLA 1
if rol == "👤 Solicitante (Crear/Rastrear)":
    st.title("💸 Solicitar Liberación de Fondo")
    
    tab1, tab2 = st.tabs(["📝 Nueva Solicitud", "🔍 Rastrear mis Solicitudes"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            correo = st.text_input("Tu Correo (Mail Solicitante)")
            division = st.selectbox("Selecciona División", list(AREAS_POR_DIVISION.keys()))
            area = st.selectbox("Selecciona Área (Centro Gestor)", AREAS_POR_DIVISION[division])
            
        with col2:
            trimestre = st.selectbox("Trimestre", ["Q1", "Q2", "Q3", "Q4", "Anual"])
            monto = st.number_input("Monto a liberar ($)", min_value=0.0, step=100.0)
            
        glosa = st.text_area("Detalle Glosa (Motivo del retiro)")
        
        if st.button("🚀 Enviar Solicitud a Costos"):
            if correo == "" or monto == 0:
                st.error("⚠️ Por favor llena tu correo y asegúrate de que el monto sea mayor a 0.")
            else:
                nuevo_id = "REQ-" + datetime.now().strftime("%Y%m%d%H%M%S")
                fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                nuevo_registro = pd.DataFrame([{
                    "Fecha": fecha_actual, "Detalle Glosa": glosa, "Trimestre": trimestre,
                    "Monto liberado": monto, "Área solicitante": area, "División": division,
                    "Aprobador": "Pendiente", "Estado de Solicitud": "Enviado",
                    "Comentarios de Costos": "", "ID Unico": nuevo_id, "Mail Solicitante": correo
                }])
                
                st.session_state.df = pd.concat([st.session_state.df, nuevo_registro], ignore_index=True)
                
                if guardar_datos(st.session_state.df):
                    st.success(f"✅ ¡Solicitud enviada! Guárdalo: {nuevo_id}")
                else:
                    st.error("❌ ERROR: No se pudo guardar. Intenta de nuevo.")
                    st.session_state.df = st.session_state.df.iloc[:-1]
                    
    with tab2:
        st.subheader("Rastreo de Solicitudes en Tiempo Real")
        st.info("Ingresa tu correo para verificar si tu solicitud fue aprobada por Costos.")
        
        mi_correo = st.text_input("Buscar por correo:")
        
        if mi_correo:
            mis_datos = st.session_state.df[st.session_state.df["Mail Solicitante"] == mi_correo]
            
            if mis_datos.empty:
                st.warning("No encontramos ninguna solicitud registrada con este correo.")
            else:
                st.dataframe(
                    mis_datos[["ID Unico", "Fecha", "Monto liberado", "Estado de Solicitud", "Comentarios de Costos"]],
                    use_container_width=True,
                    hide_index=True 
                )


# --- PANTALLA 2
elif rol == "💼 Área de Costos (Aprobar)":
    st.title("💼 Panel de Aprobación")
    df = st.session_state.df
    pendientes = df[df["Estado de Solicitud"].isin(["Enviado", "En Revisión"])]
    
    if pendientes.empty:
        st.info("🎉 No hay solicitudes pendientes por revisar. ¡A descansar!")
    else:
        st.dataframe(pendientes, use_container_width=True)
        st.markdown("---")
        
        col_a, col_b = st.columns(2)
        with col_a:
            id_selec = st.selectbox("ID a procesar:", pendientes["ID Unico"].tolist())
            nuevo_estado = st.radio("Acción a tomar:", ["Aprobada", "Rechazada", "En Revisión"])
        with col_b:
            aprobador = st.text_input("Tu Nombre (Aprobador):")
            comentario = st.text_area("Comentarios para el solicitante:")
            
        if st.button("💾 Actualizar Estado en Base de Datos"):
            if aprobador == "":
                st.error("⚠️ Debes ingresar tu nombre.")
            else:
                idx = df.index[df['ID Unico'] == id_selec].tolist()[0]
                st.session_state.df.at[idx, 'Estado de Solicitud'] = nuevo_estado
                st.session_state.df.at[idx, 'Comentarios de Costos'] = comentario
                st.session_state.df.at[idx, 'Aprobador'] = aprobador
                
                if guardar_datos(st.session_state.df):
                    st.success(f"✅ Solicitud {id_selec} actualizada correctamente.")
                    st.rerun()
                else:
                    st.error("❌ ERROR: Hubo un problema al guardar.")


# --- PANTALLA 3: EL MAPEADOR DE BI 
elif rol == "📊 Ver Historial Completo":
    st.title("📊 Base de Datos Maestra (Histórico)")
    
    col_1, col_2, col_3 = st.columns(3)
    with col_1:
        st.metric("Total de Solicitudes", len(st.session_state.df))
    with col_2:
        monto_aprobado = st.session_state.df[st.session_state.df["Estado de Solicitud"] == "Aprobada"]["Monto liberado"].sum()
        st.metric("Total Aprobado ($)", f"{monto_aprobado:,.2f}")
    with col_3:
        pendientes_count = len(st.session_state.df[st.session_state.df["Estado de Solicitud"] == "Enviado"])
        st.metric("Pendientes por revisar", pendientes_count)
        
    st.dataframe(st.session_state.df, use_container_width=True)
