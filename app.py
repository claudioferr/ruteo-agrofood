import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium import Popup
from io import BytesIO

st.set_page_config(page_title="Optimización de Rutas", layout="wide")

LAT_ORIGEN = -33.28436
LON_ORIGEN = -70.84775

archivo = st.file_uploader("📤 Sube el archivo Excel con los pedidos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip().str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    df["direccion"] = df["direccion"].fillna("").astype(str)
    df["cliente"] = df["cliente"].astype(str)
    df["latitud"] = df["latitud"].astype(float)
    df["longitud"] = df["longitud"].astype(float)
    df["furgon"] = df["furgon"].astype(str)

    # Agrupar por ubicación
    df_grouped = df.groupby(["latitud", "longitud", "furgon"]).agg({
        "cliente": "count",
        "direccion": "first"
    }).reset_index().rename(columns={"cliente": "pedidos"})

    mapa = folium.Map(location=[LAT_ORIGEN, LON_ORIGEN], zoom_start=12)
    colores = {"1": "red", "2": "blue", "3": "green"}

    folium.Marker(
        [LAT_ORIGEN, LON_ORIGEN],
        tooltip="Centro de distribución",
        icon=folium.Icon(color="orange", icon="truck", prefix="fa")
    ).add_to(mapa)

    for _, row in df_grouped.iterrows():
        popup_text = f"Dirección: {row['direccion']}<br>Pedidos: {row['pedidos']}<br>Furgón: {row['furgon']}"
        popup = Popup(popup_text, max_width=300)
        folium.Marker(
            location=[row["latitud"], row["longitud"]],
            popup=popup,
            tooltip=popup_text,
            icon=folium.Icon(color=colores.get(row["furgon"], "gray"))
        ).add_to(mapa)

    st.markdown("### 🗺️ Mapa de Rutas")
    folium_static(mapa)

    st.markdown("### ✏️ Editar asignación de clientes a furgones")
    df_editable = st.data_editor(df.copy(), num_rows="dynamic")
    df_editable["furgon"] = df_editable["furgon"].astype(str)

    st.download_button(
        label="📥 Descargar asignación editada (Excel)",
        data=df_editable.to_excel(index=False),
        file_name="asignacion_editada.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )