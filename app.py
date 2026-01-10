import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Configuração da Página ---
st.set_page_config(page_title="HemoFlow Manager", page_icon="🏥", layout="wide")

# --- CSS Personalizado ---
st.markdown("""
<style>
    .metric-container { background-color: #f0f2f6; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .stAlert { padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS (CACHE) ---
@st.cache_data
def carregar_dados_antibioticos():
    try:
        return pd.read_csv("antibioticos.csv")
    except FileNotFoundError:
        return pd.DataFrame()

# --- SEGURANÇA ---
SENHA_ADMIN = st.secrets.get("SENHA_PAINEL", "nefro123") 

# --- SIDEBAR (Controle Específico do Painel) ---
with st.sidebar:
    st.header("🔐 Admin (Apenas Mapa)")
    st.caption("Insira a senha para editar o fluxo. A calculadora permanece liberada.")
    
    senha_input = st.text_input("Senha de Acesso:", type="password")
    
    if senha_input == SENHA_ADMIN:
        modo_edicao = True
        st.success("Edição do Mapa: ATIVA")
    else:
        modo_edicao = False
        # Não mostramos mensagem de erro/aviso aqui para não poluir quando usar a calculadora
        
    st.markdown("---")

# --- CRIAÇÃO DAS ABAS ---
tab_painel, tab_calc = st.tabs(["✈️ Mapa de Fluxo (Aeroporto)", "🧮 Calc. Antibiótico"])

# ==============================================================================
# ABA 1: PAINEL DE FLUXO (Onde o modo leitura se aplica)
# ==============================================================================
with tab_painel:
    
    # Cabeçalho com Status de Segurança Específico desta aba
    col_title, col_status = st.columns([3, 1])
    with col_title:
        st.title("✈️ Mapeamento de Fluxo")
    with col_status:
        # O aviso de bloqueio aparece SÓ AQUI
        if modo_edicao:
            st.success("🔓 Modo Edição")
        else:
            st.info("🔒 Modo Leitura (Visualização)")
    
    # --- 1. Dados (Estrutura) ---
    if 'dados_aeroporto' not in st.session_state:
        st.session_state.dados_aeroporto = pd.DataFrame([
            {"Prontuário": "10234", "Setor": "UTI Geral", "Leito": "05", "Hora Prevista": "08:00", "Status": "Em Diálise"},
            {"Prontuário": "98421", "Setor": "Ambulatório", "Leito": "M01", "Hora Prevista": "09:30", "Status": "Aguardando"},
            {"Prontuário": "45123", "Setor": "Enfermaria", "Leito": "302A", "Hora Prevista": "10:00", "Status": "Previsto"},
        ])

    # --- 2. Cores do Status (Apenas Visualização) ---
    def colorir_status(val):
        color, font_color = 'white', 'black'
        if val == 'Em Diálise':
            color, font_color = '#d1e7dd', '#0f5132' # Verde
        elif val == 'Aguardando':
            color, font_color = '#fff3cd', '#856404' # Amarelo
        elif val == 'Previsto':
            color, font_color = '#cff4fc', '#055160' # Azul
        elif val == 'Finalizado':
            color, font_color = '#e2e3e5', '#6c757d' # Cinza
        return f'background-color: {color}; color: {font_color}; font-weight: bold;'

    # --- 3. Configuração de Colunas ---
    config_colunas = {
        "Prontuário": st.column_config.TextColumn("Prontuário", width="medium"),
        "Setor": st.column_config.SelectboxColumn("Setor", width="medium", options=["Ambulatório", "UTI Geral", "UTI Cardio", "Enfermaria", "Emergência"], required=True),
        "Leito": st.column_config.TextColumn("Leito", width="small"),
        "Hora Prevista": st.column_config.TimeColumn("Horário", format="HH:mm", step=60),
        "Status": st.column_config.SelectboxColumn("Status", width="medium", options=["Previsto", "Aguardando", "Em Diálise", "Finalizado"], required=True),
    }

    # --- 4. Lógica de Exibição (Editável vs Leitura) ---
    if modo_edicao:
        st.caption("🛠️ Edite os dados diretamente na tabela.")
        df_editado = st.data_editor(
            st.session_state.dados_aeroporto,
            column_config=config_colunas,
            hide_index=True,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_aeroporto_admin"
        )
        st.session_state.dados_aeroporto = df_editado
        
        if st.button("Salvar Alterações"):
            st.rerun()
            
    else:
        # Modo Leitura: Tabela Colorida
        st.caption("👁️ Exibição pública. Insira senha na lateral para alterar.")
        df_colorido = st.session_state.dados_aeroporto.style.map(colorir_status, subset=['Status'])
        st.dataframe(
            df_colorido,
            column_config=config_colunas,
            hide_index=True,
            use_container_width=True,
            height=400
        )

    st.markdown("---")
    
    # Métricas
    da = st.session_state.dados_aeroporto
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📅 Previstos", len(da[da['Status'] == 'Previsto']))
    k2.metric("⚠️ Aguardando", len(da[da['Status'] == 'Aguardando']))
    k3.metric("🟢 Em Diálise", len(da[da['Status'] == 'Em Diálise']))
    k4.metric("🏁 Finalizados", len(da[da['Status'] == 'Finalizado']))


# ==============================================================================
# ABA 2: CALCULADORA (SEMPRE LIBERADA)
# ==============================================================================
with tab_calc:
    # Note que aqui NÃO HÁ verificação de senha.
    
    df_meds = carregar_dados_antibioticos()
    
    with st.container():
        st.header("1. Dados Clínicos e Medicamento")
        col_input_1, col_input_2, col_input_3 = st.columns(3)
        
        with col_input_1:
            sexo = st.radio("Sexo:", ["Masculino", "Feminino"], horizontal=True)
            idade = st.number_input("Idade:", 18, 120, 65)
            peso = st.number_input("Peso (kg):", 30.0, 150.0, 70.0)
            altura = st.number_input("Altura (cm):", 100, 250, 170)
        
        with col_input_2:
            creatinina = st.number_input("Creatinina (mg/dL):", 0.1, 20.0, 4.0, 0.1)
            hora_hd = st.time_input("Início da Sessão:", value=datetime.strptime("08:00", "%H:%M").time())
            duracao = st.slider("Duração (h):", 2.0, 5.0, 4.0, step=0.5)
            
        with col_input_3:
             if not df_meds.empty:
                lista_meds = df_meds['Medicamento'].unique().tolist()
                lista_meds.sort()
                med_selecionado = st.selectbox("🔎 Escolha o Antibiótico:", lista_meds)
             else:
                st.error("CSV não carregado.")
                med_selecionado = None

    st.markdown("---")

    # Fórmulas
    def calcular_ckd_epi(creatinina, idade, sexo):
        if sexo == "Feminino":
            kappa, alpha, fator = 0.7, -0.241, 1.012
        else:
            kappa, alpha, fator = 0.9, -0.302, 1.0
        scr_div_kappa = creatinina / kappa
        return 142 * (min(scr_div_kappa, 1) ** alpha) * (max(scr_div_kappa, 1) ** -1.200) * (0.9938 ** idade) * fator

    def calcular_bsa(peso, altura):
        return 0.007184 * (peso ** 0.425) * (altura ** 0.725)

    egfr_norm = calcular_ckd_epi(creatinina, idade, sexo)
    bsa = calcular_bsa(peso, altura)
    egfr_absoluto = egfr_norm * (bsa / 1.73)

    col_res1, col_res2 = st.columns([1, 2])
    
    with col_res1:
        st.markdown("### 📊 Função Renal")
        st.metric("eTFG Absoluta", f"{egfr_absoluto:.1f} mL/min", help="Desnormalizada pelo BSA")
        st.caption(f"BSA: {bsa:.2f} m² | eTFG Padronizada: {egfr_norm:.1f}")

    with col_res2:
        if med_selecionado and not df_meds.empty:
            dados = df_meds[df_meds['Medicamento'] == med_selecionado].iloc[0]
            st.subheader(f"💊 {dados['Medicamento']}")
            
            inicio_dt = datetime.combine(datetime.today(), hora_hd)
            termino_dt = inicio_dt + timedelta(hours=duracao)
            is_dialisavel = "Não" not in dados['Dialisavel'] and "Minimamente" not in dados['Dialisavel']
            
            c_a, c_b = st.columns(2)
            with c_a:
                st.info(f"**Ajuste:** {dados['Ajuste_Hemodialise']}")
            with c_b:
                if is_dialisavel:
                    st.warning(f"⚠️ Dialisável. Administrar após **{termino_dt.strftime('%H:%M')}**")
                else:
                    st.success("✅ Seguro durante a diálise.")
