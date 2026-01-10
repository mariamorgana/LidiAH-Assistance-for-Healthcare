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

# --- SEGURANÇA (Senha simples) ---
# Tenta pegar dos segredos do Streamlit, se não existir, usa padrão
SENHA_ADMIN = st.secrets.get("SENHA_PAINEL", "nefro123") 

# --- SIDEBAR: Login de Admin ---
with st.sidebar:
    st.header("🔐 Área Restrita")
    senha_input = st.text_input("Senha de Admin (Edição):", type="password")
    
    if senha_input == SENHA_ADMIN:
        st.success("Modo Edição ATIVO")
        modo_edicao = True
    else:
        st.info("Modo Visualização")
        modo_edicao = False
        
    st.markdown("---")
    st.caption("Acesso para ajuste de fluxo.")

# --- CRIAÇÃO DAS ABAS (Ordem Invertida Aqui) ---
# Agora "Mapa de Fluxo" vem primeiro na lista
tab_painel, tab_calc = st.tabs(["✈️ Mapa de Fluxo (Aeroporto)", "🧮 Calc. Antibiótico"])

# ==============================================================================
# ABA 1: PAINEL DE AEROPORTO (Agora é a primeira)
# ==============================================================================
with tab_painel:
    col_title, col_status = st.columns([3, 1])
    with col_title:
        st.title("✈️ Mapeamento de Fluxo")
    with col_status:
        if modo_edicao:
            st.success("🔓 Edição Liberada")
        else:
            st.info("🔒 Apenas Leitura")
    
    # --- 1. Inicialização do Banco de Dados Local ---
    if 'dados_aeroporto' not in st.session_state:
        st.session_state.dados_aeroporto = pd.DataFrame([
            {"Prontuário": "10234", "Paciente": "Maria Silva", "Setor": "UTI Geral", "Leito": "05", "Hora Prevista": "08:00", "Status": "Em Diálise"},
            {"Prontuário": "98421", "Paciente": "João Santos", "Setor": "Ambulatório", "Leito": "M01", "Hora Prevista": "09:30", "Status": "Aguardando"},
            {"Prontuário": "45123", "Paciente": "Ana Costa", "Setor": "Enfermaria", "Leito": "302A", "Hora Prevista": "10:00", "Status": "Previsto"},
        ])

    # --- 2. Lógica de Exibição Condicional ---
    
    configuracao_colunas = {
        "Prontuário": st.column_config.TextColumn("Prontuário", width="small"),
        "Paciente": st.column_config.TextColumn("Nome do Paciente", width="medium"),
        "Setor": st.column_config.SelectboxColumn("Setor de Origem", width="medium", options=["Ambulatório", "UTI Geral", "UTI Cardio", "Enfermaria", "Emergência", "Externo"], required=True),
        "Leito": st.column_config.TextColumn("Leito/Poltrona", width="small"),
        "Hora Prevista": st.column_config.TimeColumn("Horário Previsto", format="HH:mm", step=60),
        "Status": st.column_config.SelectboxColumn("Status Atual", width="medium", options=["Previsto", "Aguardando", "Em Diálise", "Finalizado"], required=True),
    }

    if modo_edicao:
        # MODO EDITOR (COM SENHA)
        st.caption("🛠️ Você está no modo administrador. Pode editar células e adicionar pacientes.")
        df_editado = st.data_editor(
            st.session_state.dados_aeroporto,
            column_config=configuracao_colunas,
            hide_index=True,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_aeroporto_admin"
        )
        st.session_state.dados_aeroporto = df_editado
        
        if st.button("Salvar/Atualizar"):
            st.rerun()
            
    else:
        # MODO LEITURA (SEM SENHA)
        st.caption("👁️ Modo de visualização pública. Insira a senha na barra lateral para fazer alterações.")
        st.dataframe(
            st.session_state.dados_aeroporto,
            column_config=configuracao_colunas,
            hide_index=True,
            use_container_width=True
        )

    st.markdown("---")

    # --- 3. Visão Geral (Métricas) ---
    dados_atuais = st.session_state.dados_aeroporto
    
    total_previsto = len(dados_atuais[dados_atuais['Status'] == 'Previsto'])
    total_aguardando = len(dados_atuais[dados_atuais['Status'] == 'Aguardando'])
    total_em_dialise = len(dados_atuais[dados_atuais['Status'] == 'Em Diálise'])
    total_finalizado = len(dados_atuais[dados_atuais['Status'] == 'Finalizado'])
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📅 Previstos", total_previsto)
    k2.metric("⚠️ Aguardando", total_aguardando)
    k3.metric("🟢 Em Diálise", total_em_dialise)
    k4.metric("🏁 Finalizados", total_finalizado)


# ==============================================================================
# ABA 2: CALCULADORA DE ANTIBIÓTICOS (Agora é a segunda)
# ==============================================================================
with tab_calc:
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
