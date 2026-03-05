import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta

# Configuración profesional
st.set_page_config(page_title="Segurtec Master Nube - Web", layout="wide")

db_config = {
    'user': 'JkhUY2VNZh3vSyL.root',
    'password': 'cbt8iGFrXdcgTCWz', 
    'host': 'gateway01.us-east-1.prod.aws.tidbcloud.com',
    'database': 'test',
    'port': 4000
}

def conectar():
    try:
        return mysql.connector.connect(**db_config)
    except:
        return None

st.title("📊 Panel de Control Segurtec - Seguridad Física RDC")
st.info("Visualización en tiempo real de matrices de entrenamiento")

conn = conectar()
if conn:
    # Cargar datos
    query = "SELECT * FROM entrenamientos"
    df = pd.read_sql(query, conn)
    conn.close()

    if not df.empty:
        # --- BLINDAJE DE DATOS ---
        hoy = datetime.now()
        # Convertir a mayúsculas para que coincidan siempre
        df['tipo_matriz'] = df['tipo_matriz'].str.upper().str.strip()
        # Limpiar fechas
        df['f_realizado'] = pd.to_datetime(df['f_realizado'], format='%d/%m/%Y', errors='coerce')
        # Calcular si está al día (menos de 365 días)
        df['al_dia'] = df['f_realizado'].apply(lambda x: (x + timedelta(days=365)) > hoy if pd.notnull(x) else False)

        # Totales
        total_p = df['persona_num'].nunique()
        
        # Filtrar por tipo exacto
        hsq_rows = df[df['tipo_matriz'] == 'HSQ']
        fis_rows = df[df['tipo_matriz'] == 'FISICA']

        # Sumar solo los que están "Al Día"
        hsq_val = hsq_rows['al_dia'].sum()
        fis_val = fis_rows['al_dia'].sum()
        
        # Porcentajes (Base 30 cursos como en el .EXE)
        p_hsq = (hsq_val / (total_p * 30)) * 100 if total_p > 0 else 0
        p_fis = (fis_val / (total_p * 30)) * 100 if total_p > 0 else 0

        # Mostrar KPIs
        c1, c2, c3 = st.columns(3)
        c1.metric("Personal Activo", f"{total_p}")
        c2.metric("Matriz HSQ Global", f"{p_hsq:.2f}%")
        c3.metric("Seguridad Física Global", f"{p_fis:.2f}%")

        # Barras visuales
        st.subheader("📈 Avance por Categoría")
        st.write("**Entrenamientos Legales e Inducción (HSQ)**")
        st.progress(min(p_hsq/100, 1.0))
        
        st.write("**Procedimientos Seguros (Seguridad Física)**")
        st.progress(min(p_fis/100, 1.0))

        # Tabla detallada
        st.markdown("---")
        df['Colaborador'] = df['nombre'].fillna('') + " " + df['apellidos'].fillna('')
        lista = sorted(df['Colaborador'].unique())
        sel = st.selectbox("Buscar historial detallado:", lista)
        
        filtro = df[df['Colaborador'] == sel][['curso', 'f_realizado', 'tipo_matriz']]
        filtro['f_realizado'] = filtro['f_realizado'].dt.strftime('%d/%m/%Y')
        st.table(filtro)

    else:
        st.warning("La base de datos está vacía.")
else:
    st.error("No hay conexión con la base de datos en la nube.")