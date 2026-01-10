import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Configuração da Página ---
st.set_page_config(page_title="AntibioDialysis Pro", page_icon="🧬", layout="wide")

# --- CSS Personalizado ---
st.markdown("""
<style>
    .metric-container { background-color: #f0f2f6; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .stAlert { padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 1. Carregamento de Dados ---
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("antibioticos.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame()

df_meds = carregar_dados()

# --- 2. Barra Lateral: Dados Completos ---
with st.sidebar:
    st.header("👤 Dados Antropométricos")
    
    sexo = st.radio("Sexo:", ["Masculino", "Feminino"], horizontal=True)
    idade = st.number_input("Idade (anos):", min_value=18, max_value=120, value=65)
    peso = st.number_input("Peso (kg):", min_value=30.0, value=70.0, step=0.5)
    altura = st.number_input("Altura (cm):", min_value=100, value=170, step=1, help="Necessário para cálculo de BSA.")
    
    st.markdown("---")
    st.header("🧪 Função Renal")
    creatinina = st.number_input("Creatinina Sérica (mg/dL):", min_value=0.1, value=4.0, step=0.1)
    
    st.markdown("---")
    st.header("⚙️ Diálise")
    hora_hd = st.time_input("Início da Sessão:", value=datetime.strptime("08:00", "%H:%M").time())
    duracao = st.slider("Duração (h):", 2.0, 5.0, 4.0, step=0.5)

# --- 3. Fórmulas Matemáticas ---

def calcular_ckd_epi(creatinina, idade, sexo):
    """Retorna eTFG normalizada (mL/min/1.73m²)"""
    if sexo == "Feminino":
        kappa = 0.7
        alpha = -0.241
        fator_sexo = 1.012
    else:
        kappa = 0.9
        alpha = -0.302
        fator_sexo = 1.0

    scr_div_kappa = creatinina / kappa
    termo_min = min(scr_div_kappa, 1) ** alpha
    termo_max = max(scr_div_kappa, 1) ** -1.200

    egfr = 142 * termo_min * termo_max * (0.9938 ** idade) * fator_sexo
    return egfr

def calcular_bsa_dubois(peso, altura_cm):
    """Retorna Superfície Corporal (m²) usando fórmula de Du Bois"""
    # BSA = 0.007184 * W^0.425 * H^0.725
    return 0.007184 * (peso ** 0.425) * (altura_cm ** 0.725)

# Cálculos em tempo real
egfr_norm = calcular_ckd_epi(creatinina, idade, sexo)
bsa = calcular_bsa_dubois(peso, altura)
egfr_absoluto = egfr_norm * (bsa / 1.73) # Desnormalização

# --- 4. Interface Principal ---
st.title("🏥 AntibioDialysis: Ajuste de Precisão")

# Painel de Métricas Renais
col_metrics1, col_metrics2, col_metrics3 = st.columns(3)

with col_metrics1:
    st.metric(label="Superfície Corporal (BSA)", value=f"{bsa:.2f} m²", help="Fórmula de Du Bois & Du Bois")

with col_metrics2:
    st.metric(
        label="eTFG (Padronizada)", 
        value=f"{egfr_norm:.1f}", 
        delta="mL/min/1.73m²", 
        delta_color="off",
        help="CKD-EPI 2021. Usada para estadiamento renal."
    )

with col_metrics3:
    # Destaque visual para o valor que deve guiar a dose
    st.markdown(f"""
    <div style="background-color: #d1e7dd; padding: 10px; border-radius: 5px; border: 1px solid #a3cfbb;">
        <span style="font-size: 0.9em; color: #0f5132;">eTFG Absoluta (Para Dose)</span><br>
        <span style="font-size: 1.8em; font-weight: bold; color: #0f5132;">{egfr_absoluto:.1f}</span> <span style="font-size: 0.8em;">mL/min</span>
    </div>
    """, unsafe_allow_html=True)

# Alerta de Discrepância
discrepancia = abs(egfr_norm - egfr_absoluto)
if discrepancia > 10:
    st.info(f"💡 **Nota:** Devido à constituição física do paciente (BSA {bsa:.2f}m²), a capacidade real de filtração ({egfr_absoluto:.1f} mL/min) difere significativamente do valor padronizado.")

st.markdown("---")

# --- 5. Seleção e Análise de Medicamento ---
col_selection, col_result = st.columns([1, 2])

with col_selection:
    if not df_meds.empty:
        lista_meds = df_meds['Medicamento'].unique().tolist()
        lista_meds.sort()
        med_selecionado = st.selectbox("🔎 Antibiótico:", lista_meds)
        
        # Exibir classe e risco básico aqui
        if med_selecionado:
            info_med = df_meds[df_meds['Medicamento'] == med_selecionado].iloc[0]
            st.caption(f"Classe: {info_med['Classe']}")
            if "Sim" in info_med['Dialisavel']:
                st.warning("⚠️ Droga Dialisável")
            else:
                st.success("✅ Seguro na HD")
    else:
        st.error("CSV não carregado.")
        med_selecionado = None

with col_result:
    if med_selecionado:
        dados = info_med # Já carregado no bloco anterior
        
        st.subheader(f"Guia: {dados['Medicamento']}")
        
        # Lógica de Horário
        inicio_dt = datetime.combine(datetime.today(), hora_hd)
        termino_dt = inicio_dt + timedelta(hours=duracao)
        
        # Container de recomendação
        with st.container():
            col_res_1, col_res_2 = st.columns(2)
            
            with col_res_1:
                st.markdown("**1. Ajuste de Dose (Diálise):**")
                st.info(f"{dados['Ajuste_Hemodialise']}")
                
                # Alerta se função residual for alta
                if egfr_absoluto > 20:
                    st.warning(f"⚠️ Atenção: Função renal residual de {egfr_absoluto:.0f} mL/min. A dose padrão de diálise pode ser insuficiente. Considere aumentar a dose ou monitorar nível sérico.")
            
            with col_res_2:
                st.markdown("**2. Timing Ideal:**")
                is_dialisavel = "Não" not in dados['Dialisavel'] and "Minimamente" not in dados['Dialisavel']
                
                if is_dialisavel:
                    st.write(f"🚫 Não administrar entre {hora_hd.strftime('%H:%M')} e {termino_dt.strftime('%H:%M')}.")
                    st.success(f"💉 Administrar **após as {termino_dt.strftime('%H:%M')}**.")
                    if isinstance(dados['Suplementacao_Pos_HD'], str) and len(dados['Suplementacao_Pos_HD']) > 5:
                         st.markdown(f"**Reposição:** {dados['Suplementacao_Pos_HD']}")
                else:
                    st.success("✅ Horário Livre (Independente da HD).")

# --- Footer ---
st.markdown("---")
st.caption("Fórmulas: CKD-EPI 2021 (Filtração) | Du Bois & Du Bois (BSA). A desnormalização segue a recomendação da FDA/EMA para ajuste de dose em extremos de peso.")
