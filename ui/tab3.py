import streamlit as st
from utils.contador import get_contador, set_contador

def render_tab3():
    st.subheader("Panel de Administración")
    st.info(f"El valor actual del contador de liquidaciones es: **{get_contador()}**")
    password = st.text_input("Ingrese contraseña de administrador", type="password", key="admin_password")
    if password == "sunafil2025":
        st.success("Acceso concedido")
        nuevo_valor = st.number_input("Establecer nuevo valor para el contador", min_value=1, step=1, value=get_contador(), key="new_counter_val")
        if st.button("Actualizar Contador"):
            if set_contador(nuevo_valor):
                st.success(f"Contador actualizado a: {nuevo_valor}")
            else:
                st.error("El valor debe ser un número entero positivo.")
    elif password:
        st.error("Contraseña incorrecta.")
