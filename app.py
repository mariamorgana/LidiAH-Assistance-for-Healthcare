import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from datetime import datetime, timedelta

# --- IDENTIDADE VISUAL LIDIAH ---
LOGO_PATH = Path(__file__).parent / "assets" / "logo_lidiah.png"

def carregar_logo_base64():
    if LOGO_PATH.exists():
        return base64.b64encode(LOGO_PATH.read_bytes()).decode()
    return None

LOGO_B64 = carregar_logo_base64()

# --- Configuração da Página ---
try:
    from PIL import Image
    icone_pagina = Image.open(LOGO_PATH) if LOGO_PATH.exists() else "🏥"
except Exception:
    icone_pagina = "🏥"

st.set_page_config(page_title="LidiAH - Assistance for Healthcare", page_icon=icone_pagina, layout="wide")

# --- CSS Personalizado (Identidade Visual LidiAH) ---
st.markdown("""
<style>
    :root {
        --lidiah-teal: #01ABB2;
        --lidiah-teal-dark: #017A80;
        --lidiah-navy: #454B5A;
        --lidiah-coral: #F0665A;
        --lidiah-bg: #F2F6F7;
    }

    .metric-container { background-color: var(--lidiah-bg); padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .stAlert { padding: 10px; border-radius: 5px; }

    /* Cabeçalho com logo */
    .lidiah-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 12px 0 20px 0;
        border-bottom: 2px solid var(--lidiah-bg);
        margin-bottom: 20px;
    }
    .lidiah-header img { height: 110px; }

    /* Logo na sidebar */
    .lidiah-sidebar-logo { text-align: center; padding: 4px 0 16px 0; }
    .lidiah-sidebar-logo img { width: 100%; max-width: 220px; }

    /* Cartões de navegação na sidebar */
    .lidiah-nav-titulo { color: var(--lidiah-navy); font-weight: 700; font-size: 0.95rem; margin: 4px 0 10px 0; }
    .lidiah-nav-card {
        display: flex;
        align-items: center;
        gap: 10px;
        background-color: var(--lidiah-bg);
        border-left: 4px solid var(--lidiah-teal);
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }
    .lidiah-nav-card .nav-icon { font-size: 1.3rem; }
    .lidiah-nav-card .nav-label { font-weight: 600; color: var(--lidiah-navy); font-size: 0.92rem; }
    .lidiah-header .lidiah-titulo { font-size: 1.05rem; color: var(--lidiah-navy); font-weight: 500; }

    /* Realce nas abas ativas com a cor da marca */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--lidiah-teal-dark) !important;
        border-bottom-color: var(--lidiah-teal) !important;
    }
    button[data-baseweb="tab"] p { font-weight: 600; }

    /* Sidebar com toque de marca */
    section[data-testid="stSidebar"] h2 { color: var(--lidiah-navy); }

    /* Botões primários */
    button[kind="primary"] {
        background-color: var(--lidiah-teal) !important;
        border-color: var(--lidiah-teal) !important;
    }
    button[kind="primary"]:hover {
        background-color: var(--lidiah-teal-dark) !important;
        border-color: var(--lidiah-teal-dark) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Cabeçalho com Logo ---
if LOGO_B64:
    st.markdown(f"""
    <div class="lidiah-header">
        <img src="data:image/png;base64,{LOGO_B64}" alt="LidiAH">
        <div class="lidiah-titulo">Ferramentas de apoio clínico para nefrologia e diálise</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("## 🏥 LidiAH — Assistance for Healthcare")
    st.caption("Ferramentas de apoio clínico para nefrologia e diálise")

# --- CARREGAMENTO DE DADOS (CACHE) ---
@st.cache_data
def carregar_dados_antibioticos():
    try:
        return pd.read_csv("antibioticos.csv")
    except FileNotFoundError:
        return pd.DataFrame()

# --- SEGURANÇA ---
SENHA_ADMIN = st.secrets.get("SENHA_PAINEL", "nefro123") 

# --- SIDEBAR ---
with st.sidebar:
    if LOGO_B64:
        st.markdown(f"""
        <div class="lidiah-sidebar-logo">
            <img src="data:image/png;base64,{LOGO_B64}" alt="LidiAH">
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="lidiah-nav-titulo">🗂️ Ferramentas</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="lidiah-nav-card"><span class="nav-icon">🧮</span><span class="nav-label">Calc. Antibiótico</span></div>
    <div class="lidiah-nav-card"><span class="nav-icon">💧</span><span class="nav-label">Hiponatremia</span></div>
    """, unsafe_allow_html=True)
    st.caption("Selecione a ferramenta nas abas no topo da página.")

    st.markdown("---")
    st.header("🔐 Admin (Apenas Mapa)")
    st.caption("Insira a senha para editar o fluxo.")
    
    senha_input = st.text_input("Senha de Acesso:", type="password")
    
    if senha_input == SENHA_ADMIN:
        modo_edicao = True
        st.success("Edição do Mapa: ATIVA")
    else:
        modo_edicao = False
        
    st.markdown("---")
    
    # BOTÃO DE EMERGÊNCIA (Para limpar o cache antigo)
    if st.button("🗑️ Resetar Painel (Limpar Memória)", type="primary"):
        st.session_state.clear()
        st.rerun()

# --- CONTROLE DE ABAS ---
MOSTRAR_MAPA_FLUXO = False  # Mude para True para reexibir a aba "Mapa de Fluxo"

# --- CRIAÇÃO DAS ABAS ---
if MOSTRAR_MAPA_FLUXO:
    tab_painel, tab_calc, tab_hipo = st.tabs(["✈️ Mapa de Fluxo (Aeroporto)", "🧮 Calc. Antibiótico", "💧 Hiponatremia"])
else:
    tab_calc, tab_hipo = st.tabs(["🧮 Calc. Antibiótico", "💧 Hiponatremia"])

# ==============================================================================
# ABA 1: PAINEL DE FLUXO (NOVA VARIÁVEL)
# ==============================================================================
if MOSTRAR_MAPA_FLUXO:
    with tab_painel:
        col_title, col_status = st.columns([3, 1])
        with col_title:
            st.title("✈️ Mapeamento de Fluxo")
        with col_status:
            if modo_edicao:
                st.success("🔓 Modo Edição")
            else:
                st.info("🔒 Modo Leitura")

        # 1. Dados (USANDO NOME NOVO PARA FORÇAR ATUALIZAÇÃO)
        if 'dados_fluxo_final' not in st.session_state: 
            st.session_state.dados_fluxo_final = pd.DataFrame([
                {"Prontuário": "10234", "Setor": "UTI Geral", "Leito": "05", "Hora Prevista": "08:00", "Status": "Em Diálise"},
                {"Prontuário": "98421", "Setor": "Ambulatório", "Leito": "M01", "Hora Prevista": "09:30", "Status": "Aguardando"},
                {"Prontuário": "45123", "Setor": "Enfermaria", "Leito": "302A", "Hora Prevista": "10:00", "Status": "Previsto"},
            ])

        # 2. Cores do Status (Apenas Visualização)
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

        # 3. Configuração de Colunas (SEM PACIENTE)
        config_colunas = {
            "Prontuário": st.column_config.TextColumn("Prontuário", width="medium"),
            "Setor": st.column_config.SelectboxColumn("Setor", width="medium", options=["Ambulatório", "UTI Geral", "UTI Cardio", "Enfermaria", "Emergência"], required=True),
            "Leito": st.column_config.TextColumn("Leito", width="small"),
            "Hora Prevista": st.column_config.TimeColumn("Horário", format="HH:mm", step=60),
            "Status": st.column_config.SelectboxColumn("Status", width="medium", options=["Previsto", "Aguardando", "Em Diálise", "Finalizado"], required=True),
        }

        # 4. Exibição
        if modo_edicao:
            st.caption("🛠️ Edite os dados diretamente na tabela.")
            df_editado = st.data_editor(
                st.session_state.dados_fluxo_final,
                column_config=config_colunas,
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                key="editor_aeroporto_final"
            )
            st.session_state.dados_fluxo_final = df_editado

            if st.button("Salvar Alterações"):
                st.rerun() 
        else:
            st.caption("👁️ Exibição pública.")
            # Verifica se existe coluna antiga por segurança
            df_safe = st.session_state.dados_fluxo_final.copy()
            if "Paciente" in df_safe.columns:
                 df_safe = df_safe.drop(columns=["Paciente"])

            df_colorido = df_safe.style.map(colorir_status, subset=['Status'])
            st.dataframe(
                df_colorido,
                column_config=config_colunas,
                hide_index=True,
                use_container_width=True,
                height=400
            )

        st.markdown("---")

        # Métricas
        da = st.session_state.dados_fluxo_final
        k1, k2, k3, k4 = st.columns(4)
        # Proteção contra erro se a coluna Status não existir
        if 'Status' in da.columns:
            k1.metric("📅 Previstos", len(da[da['Status'] == 'Previsto']))
            k2.metric("⚠️ Aguardando", len(da[da['Status'] == 'Aguardando']))
            k3.metric("🟢 Em Diálise", len(da[da['Status'] == 'Em Diálise']))
            k4.metric("🏁 Finalizados", len(da[da['Status'] == 'Finalizado']))


# ==============================================================================
# ABA 2: CALCULADORA COMPLETA
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
            
            # BLOCO 1
            st.markdown("##### 1. Ajuste de Dose")
            st.info(f"{dados['Ajuste_Hemodialise']}")
            if pd.notna(dados.get('Suplementacao_Pos_HD')) and str(dados.get('Suplementacao_Pos_HD')) != "nan":
                st.write(f"**Suplementação:** {dados['Suplementacao_Pos_HD']}")

            st.markdown("---")

            # BLOCO 2
            st.markdown("##### 2. Recomendação de Horário")
            if pd.notna(dados.get('Recomendacao_Horario')):
                st.write(f"📝 **Diretriz:** {dados['Recomendacao_Horario']}")
            
            if is_dialisavel:
                st.warning(f"⚠️ **Atenção: Medicamento Dialisável**")
                st.write(f"A sessão está prevista para terminar às **{termino_dt.strftime('%H:%M')}**.")
                st.error(f"Administrar **APÓS** o término ({termino_dt.strftime('%H:%M')}) para evitar remoção.")
            else:
                st.success(f"✅ **Seguro na Diálise**")
                st.info("Pode ser administrado antes ou durante a sessão sem perda de eficácia.")

# ==============================================================================
# ABA 3: MANEJO AGUDO DA HIPONATREMIA GRAVE
# ==============================================================================
with tab_hipo:
    st.title("💧 Manejo Agudo da Hiponatremia")
    st.caption(
        "Baseado em: Adrogué HJ et al. JAMA. 2022;328(3):280-291 (doi:10.1001/jama.2022.11176) "
        "e Sterns RH et al. CJASN. 2024;19:129-135 — 'Stay the Course' (doi:10.2215/CJN.0000000000000244)."
    )
    st.warning(
        "⚕️ Ferramenta de **apoio à decisão clínica**. Não substitui o julgamento médico. "
        "Sempre correlacionar com o quadro clínico completo, volemia, etiologia e protocolos institucionais."
    )

    if 'hipo_caso' not in st.session_state:
        st.session_state.hipo_caso = None

    # ==========================================================================
    # INICIAR NOVO CASO
    # ==========================================================================
    if st.session_state.hipo_caso is None:
        st.subheader("1️⃣ Novo Caso — Avaliação Inicial")

        sodio_inicial = st.number_input(
            "Sódio sérico inicial (mEq/L):", 90.0, 134.0, 118.0, 0.5, key="hipo_sodio_ini"
        )

        st.write("**Sintomas neurológicos / clínicos:**")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            s_graves = st.multiselect(
                "🔴 Sintomas graves (risco iminente):",
                ["Sonolência / rebaixamento do nível de consciência", "Convulsões",
                 "Coma", "Desconforto cardiorrespiratório"],
                key="hipo_sint_graves"
            )
        with col_s2:
            s_moderados = st.multiselect(
                "🟡 Sintomas moderadamente graves:",
                ["Vômitos", "Confusão mental"],
                key="hipo_sint_moderados"
            )

        alto_risco_complicacao = False
        if s_moderados and not s_graves:
            alto_risco_complicacao = st.checkbox(
                "Paciente em alto risco de progressão para complicações com risco de morte?",
                key="hipo_alto_risco_compl"
            )

        st.write("**Fatores de risco para síndrome de desmielinização osmótica (mielinólise):**")
        fatores = st.multiselect(
            "Selecione os fatores presentes:",
            ["Transtorno por uso de álcool", "Hipopotassemia grave", "Desnutrição", "Hepatopatia avançada"],
            key="hipo_fatores_risco"
        )
        if sodio_inicial <= 105:
            st.caption("🔺 Sódio ≤105 mEq/L: fator de risco adicionado automaticamente.")

        if st.button("▶️ Iniciar Caso", type="primary", key="hipo_iniciar"):
            risco_alto = (sodio_inicial <= 105) or (len(fatores) > 0)
            st.session_state.hipo_caso = {
                'sodio_inicial': sodio_inicial,
                'sintomas_graves': s_graves,
                'sintomas_moderados': s_moderados,
                'alto_risco_complicacao': alto_risco_complicacao,
                'fatores_risco': fatores,
                'risco_alto_mielinolise': risco_alto,
                'medidas': [{'horas': 0.0, 'sodio': sodio_inicial}],
            }
            st.rerun()

    # ==========================================================================
    # CASO ATIVO
    # ==========================================================================
    else:
        caso = st.session_state.hipo_caso
        risco_txt = "🔴 ALTO RISCO de mielinólise" if caso['risco_alto_mielinolise'] else "🟢 Risco padrão de mielinólise"
        st.subheader(f"2️⃣ Caso Ativo — Sódio inicial: {caso['sodio_inicial']} mEq/L | {risco_txt}")

        fatores_show = list(caso['fatores_risco'])
        if caso['sodio_inicial'] <= 105:
            fatores_show.append("Sódio ≤105 mEq/L")
        if fatores_show:
            st.caption("Fatores de risco para mielinólise: " + ", ".join(fatores_show))
        if caso['sintomas_graves'] or caso['sintomas_moderados']:
            st.caption("Sintomas: " + ", ".join(caso['sintomas_graves'] + caso['sintomas_moderados']))

        emergencia = bool(caso['sintomas_graves']) or (bool(caso['sintomas_moderados']) and caso['alto_risco_complicacao'])

        # ----- Conduta inicial -----
        st.markdown("### 🩺 Conduta Recomendada")
        if emergencia:
            st.error("**TRATAMENTO DE EMERGÊNCIA — sintomas graves ou risco de complicação fatal**")
            st.markdown("""
- Salina hipertônica **3%** em **bolus**: 100–150 mL IV em 10–20 minutos.
- Pode repetir até **2–3 vezes**, conforme necessário.
- **Meta:** elevar o sódio sérico em **4–6 mEq/L dentro de 1–2 horas** (suficiente para reverter encefalopatia hiponatrêmica / hipertensão intracraniana).
- Dosar o sódio sérico **após cada bolus**.
- Considerar suporte de via aérea / UTI se rebaixamento do nível de consciência.
- Suspender fluidos hipotônicos e fármacos que favoreçam hiponatremia (opioides, antidepressivos, etc.).
""")
        else:
            st.info(
                "Sem critérios de emergência no momento. Avaliar a causa de base (hipovolêmica, euvolêmica ou "
                "hipervolêmica) e tratar conforme a etiologia. Monitorar sódio sérico periodicamente."
            )

        st.markdown("---")

        # ----- Registrar nova medida -----
        st.markdown("### 📈 Registrar Nova Dosagem de Sódio")
        col1, col2 = st.columns(2)
        ultima_hora_registrada = max(m['horas'] for m in caso['medidas'])
        with col1:
            nova_hora = st.number_input(
                "Horas desde o início do tratamento:", 0.0, 240.0,
                value=float(ultima_hora_registrada + 2), step=0.5, key="hipo_nova_hora"
            )
        with col2:
            novo_sodio = st.number_input(
                "Sódio sérico medido (mEq/L):", 90.0, 160.0, float(caso['sodio_inicial']), 0.5, key="hipo_novo_sodio"
            )

        if st.button("➕ Adicionar Medida", key="hipo_add_medida"):
            caso['medidas'].append({'horas': nova_hora, 'sodio': novo_sodio})
            caso['medidas'].sort(key=lambda m: m['horas'])
            st.rerun()

        # ----- Avaliação da taxa de correção -----
        medidas = caso['medidas']
        if len(medidas) > 1:
            st.markdown("### 📊 Avaliação da Taxa de Correção")

            def sodio_em(t_alvo, pontos):
                """Interpola linearmente o sódio no tempo t_alvo (h) a partir das medidas registradas."""
                pontos = sorted(pontos, key=lambda m: m['horas'])
                if t_alvo <= pontos[0]['horas']:
                    return pontos[0]['sodio']
                if t_alvo >= pontos[-1]['horas']:
                    return pontos[-1]['sodio']
                for i in range(len(pontos) - 1):
                    h0, h1 = pontos[i]['horas'], pontos[i + 1]['horas']
                    if h0 <= t_alvo <= h1:
                        s0, s1 = pontos[i]['sodio'], pontos[i + 1]['sodio']
                        if h1 == h0:
                            return s1
                        frac = (t_alvo - h0) / (h1 - h0)
                        return s0 + frac * (s1 - s0)
                return pontos[-1]['sodio']

            ultima = medidas[-1]
            t_atual = ultima['horas']
            sodio_atual = ultima['sodio']

            delta_24h = sodio_atual - sodio_em(max(0.0, t_atual - 24), medidas)
            delta_48h = sodio_atual - sodio_em(max(0.0, t_atual - 48), medidas)
            delta_total = sodio_atual - caso['sodio_inicial']

            limite_24h = 8 if caso['risco_alto_mielinolise'] else 10
            limite_48h = 18

            c1, c2, c3 = st.columns(3)
            c1.metric("Δ Total", f"{delta_total:+.1f} mEq/L")
            c2.metric("Δ Últimas 24h", f"{delta_24h:+.1f} mEq/L", help=f"Limite: {limite_24h} mEq/L")
            c3.metric("Δ Últimas 48h", f"{delta_48h:+.1f} mEq/L", help=f"Limite: {limite_48h} mEq/L")

            # ----- Lógica de decisão -----
            if delta_24h > limite_24h or delta_48h > limite_48h:
                st.error(f"""
🚨 **LIMITE DE CORREÇÃO EXCEDIDO** (>{limite_24h} mEq/L em 24h ou >{limite_48h} mEq/L em 48h)

**Considerar religamento terapêutico (relowering):**
- Interromper a solução salina hipertônica.
- Considerar **desmopressina (DDAVP)** 2–4 mcg IV/SC a cada 6–8h.
- Infundir **soro glicosado 5% (D5W)** para reduzir o sódio de volta à faixa de segurança.
- Monitorar o sódio sérico a cada 2–4h até estabilização.
{"- **Paciente de ALTO RISCO para mielinólise — atenção redobrada.**" if caso['risco_alto_mielinolise'] else ""}
""")
            elif delta_24h > limite_24h - 2 or delta_48h > limite_48h - 3:
                st.warning(f"""
⚠️ **Aproximando-se do limite de correção** (meta: ≤{limite_24h} mEq/L/24h; ≤{limite_48h} mEq/L/48h)

- Considerar reduzir ou suspender a infusão de salina hipertônica.
- Trocar para fluidos isotônicos ou hipotônicos conforme a causa de base, se aplicável.
- Aumentar a frequência de monitorização do sódio sérico (a cada 2–4h).
- Atenção à diurese aquosa espontânea (poliúria hipotônica) — causa mais comum de supercorreção.
""")
            elif emergencia and delta_total < 4 and t_atual <= 2:
                st.warning("""
⏳ **Meta inicial ainda não atingida** (objetivo: +4 a 6 mEq/L nas primeiras 1–2h em pacientes com sintomas graves).

- Considerar repetir bolus de NaCl 3% (100–150 mL em 10–20 min), respeitando o máximo de 2–3 bolus.
""")
            else:
                st.success(f"""
✅ **Correção dentro da meta de segurança** (limite: {limite_24h} mEq/L/24h; {limite_48h} mEq/L/48h)

- Manter monitorização do sódio sérico a cada 4–6h nas primeiras 24h.
- Reavaliar sintomas clínicos e a causa de base da hiponatremia.
""")

            st.markdown("#### 🗂️ Histórico de Medidas")
            df_medidas = pd.DataFrame(medidas).rename(
                columns={'horas': 'Horas desde início', 'sodio': 'Sódio (mEq/L)'}
            )
            st.dataframe(df_medidas, hide_index=True, use_container_width=True)

        st.markdown("---")
        if st.button("🔚 Encerrar Caso e Iniciar Novo Paciente", type="secondary", key="hipo_encerrar"):
            st.session_state.hipo_caso = None
            st.rerun()
