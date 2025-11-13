import streamlit as st

st.title('Meu primeiro app😍')

st.header('Vamos fazer algo vom interatividade')

n = st.number_input('Entre com seu número')

st.write(f'O número que você escolheu ao quadrado é {n**2}.')