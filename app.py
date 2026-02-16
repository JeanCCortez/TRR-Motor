import streamlit as st
import math
from fpdf import FPDF

# ==========================================
# CONSTANTES DA TEORIA TRR
# ==========================================
BETA = 0.028006
A0 = 1.2001e-10
G = 6.67430e-11
C = 299792458.0

def calcular_D_A(z1, z2):
    if z1 >= z2: return 0.0
    passos = 500
    dz = (z2 - z1) / passos
    integral = sum(1.0 / math.sqrt(0.3 * (1 + z1 + i*dz)**3 + 0.7) * dz for i in range(passos))
    return ((299792.458 / 70.0) * integral / (1 + z2)) * 3.086e22

# ==========================================
# FUNÇÃO PARA LIMPAR OS DADOS E ZERAR CAIXAS
# ==========================================
def limpar_dados():
    # 1. Apaga os relatórios da tela
    if 'res_dyn' in st.session_state:
        del st.session_state['res_dyn']
    if 'res_opt' in st.session_state:
        del st.session_state['res_opt']
        
    # 2. Força "Zeros" em todas as caixas de Dinâmica
    st.session_state.d_rad = 0.0
    st.session_state.d_vobs = 0.0
    st.session_state.d_vgas = 0.0
    st.session_state.d_vdisk = 0.0
    st.session_state.d_vbulge = 0.0
    
    # 3. Força "Zeros" em todas as caixas de Óptica
    st.session_state.o_zl = 0.0
    st.session_state.o_zs = 0.0
    st.session_state.o_mest = 0.0
    st.session_state.o_theta = 0.0
    st.session_state.o_cluster = False

# ==========================================
# GERADORES DE PDF (TEXTO LIMPO SEM ACENTOS)
# ==========================================
def gerar_pdf_dinamica(rad, vobs, vgas, vdisk, vbulge, vtrr, prec, ml_disk, ml_bulge):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="RELATORIO DE UNIFICACAO TRR - DINAMICA GALACTICA", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    
    texto = f"""
--------------------------------------------------------------------------------
1. CONSTANTES UNIVERSAIS UTILIZADAS:
- Limite de Fase (a0) = 1.2001e-10 m/s^2
- Indice de Viscosidade do Vacuo (Beta) = 0.028006

2. DADOS OBSERVADOS (TELESCOPIO):
- Raio Observado: {rad} kpc
- Velocidade Observada: {vobs} km/s
- Velocidade do Gas: {vgas} km/s
- Velocidade do Disco: {vdisk} km/s
- Velocidade do Bojo/Haste: {vbulge} km/s

3. RESULTADOS DA CALIBRACAO TRR:
- Previsao de Velocidade TRR: {vtrr:.2f} km/s
- Precisao de Acerto (Acuracia): {prec:.2f}%
- Razao Massa/Luz Calibrada (Disco): {ml_disk:.2f}
- Razao Massa/Luz Calibrada (Bojo): {ml_bulge:.2f}

4. METODOLOGIA FISICA (TRANSPARENCIA):
A equacao extraiu a aceleracao a partir da morfologia real da galaxia. 
A proporcao fisica entre o Bojo e o Disco cria um escudo geometrico 
contra o vacuo viscoso. Esta interacao hidrodinamica gera o arrasto 
topologico que sustenta a coesao galactica sem materia escura.
--------------------------------------------------------------------------------
    """
    for linha in texto.split('\n'):
        pdf.multi_cell(0, 8, txt=linha)
    return pdf.output(dest='S').encode('latin-1', 'replace')

def gerar_pdf_optica(zl, zs, mest, theta, is_cluster, theta_trr, prec, fator, eta_c):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="RELATORIO DE UNIFICACAO TRR - OPTICA COSMOLOGICA", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    gas_txt = "Sim (Multiplicador de plasma)" if is_cluster else "Nao"
    
    texto = f"""
--------------------------------------------------------------------------------
1. CONSTANTES UNIVERSAIS UTILIZADAS:
- Indice de Viscosidade do Vacuo (Beta) = 0.028006
- Constante Gravitacional (G) = 6.67430e-11
- Velocidade da Luz (c) = 299792458 m/s

2. DADOS OBSERVADOS (TELESCOPIO):
- Redshift Lente (z_L): {zl:.4f}
- Redshift Fonte (z_S): {zs:.4f}
- Massa Estelar Estimada: {mest} x 10^11 M_sol
- Anel de Einstein Observado: {theta} arcsec
- Aglomerado Gigante com Gas?: {gas_txt}

3. RESULTADOS DA CALIBRACAO TRR:
- Desvio Previsto TRR: {theta_trr:.2f} arcsec
- Precisao de Acerto (Acuracia): {prec:.2f}%
- Massa Estelar Otimizada: {mest * fator:.2f} x 10^11 M_sol
- Indice de Refracao de Cortez (eta_C): {eta_c:.5f}

4. METODOLOGIA FISICA (TRANSPARENCIA):
A luz sofre um atraso de fase fisico ao atravessar o tecido viscoso 
do vacuo. O Indice de Refracao amplifica geometricamente a curvatura. 
A mesma constante Beta que propulsiona galaxias refratou a luz aqui, 
confirmando matematicamente a unificacao cosmica da teoria.
--------------------------------------------------------------------------------
    """
    for linha in texto.split('\n'):
        pdf.multi_cell(0, 8, txt=linha)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ==========================================
# DICIONÁRIO DE IDIOMAS (GLOBAL)
# ==========================================
LANG = {
    "PT": {
        "title": "🌌 Motor Cosmológico TRR", "rad": "Raio observado (kpc)", "vobs": "Velocidade Obs (km/s)", "vgas": "Velocidade Gás (km/s)", "vdisk": "Veloc. Disco (km/s)", "vbulge": "Veloc. Haste/Bojo (km/s)", 
        "calc": "🚀 Processar TRR", "clear": "🧹 Limpar Tudo", "zl": "Redshift Lente (z_L)", "zs": "Redshift Fonte (z_S)", "mest": "Massa Estelar (10^11 M_sol)", "theta": "Anel Einstein (arcsec)", 
        "cluster": "Aglomerado Gigante com Gás?", "tab1": "📊 Dinâmica Galáctica", "tab2": "👁️ Óptica Cosmológica", "pdf_btn": "📄 Baixar / Compartilhar PDF", "details": "📚 Ver Relatório Detalhado (Métodos e Constantes)",
        "ml_disk": "M/L Disco", "ml_bulge": "M/L Bojo", "v_trr": "Previsão TRR", "v_obs": "Veloc. Telescópio", "precision": "Precisão de Acerto",
        "mest_opt": "Massa Otimizada", "eta_c": "Índice de Cortez (η_C)", "theta_trr": "Desvio TRR", "theta_obs": "Desvio Telescópio",
        "exp_dyn": "A constante β (0.028006) interagiu com a geometria da galáxia gerando o escudo topológico. A curva de velocidade foi sustentada respeitando a matéria bariônica pura, sem matéria escura.",
        "exp_opt": "A luz sofreu o atraso de fase ao atravessar o vácuo viscoso. O Índice de Cortez amplificou o desvio da luz eliminando a necessidade matemática de Halos Escuros."
    },
    "EN": {
        "title": "🌌 TRR Cosmological Engine", "rad": "Observed Radius (kpc)", "vobs": "Obs Velocity (km/s)", "vgas": "Gas Velocity (km/s)", "vdisk": "Disk Velocity (km/s)", "vbulge": "Bar/Bulge Vel. (km/s)", 
        "calc": "🚀 Process TRR", "clear": "🧹 Clear All", "zl": "Lens Redshift (z_L)", "zs": "Source Redshift (z_S)", "mest": "Stellar Mass (10^11 M_sol)", "theta": "Einstein Ring (arcsec)", 
        "cluster": "Giant Gas Cluster?", "tab1": "📊 Galactic Dynamics", "tab2": "👁️ Cosmological Optics", "pdf_btn": "📄 Download / Share PDF", "details": "📚 View Detailed Report (Methods & Constants)",
        "ml_disk": "M/L Disk", "ml_bulge": "M/L Bulge", "v_trr": "TRR Prediction", "v_obs": "Telescope Vel.", "precision": "Accuracy",
        "mest_opt": "Optimized Mass", "eta_c": "Cortez Index (η_C)", "theta_trr": "TRR Deflection", "theta_obs": "Telescope Deflection",
        "exp_dyn": "The β constant (0.028006) interacted with the galaxy's geometry creating a topological shield. The velocity curve was sustained respecting pure baryonic matter, without dark matter.",
        "exp_opt": "Light suffered a phase delay crossing the viscous vacuum. The Cortez Index amplified the light deflection, eliminating the mathematical need for Dark Halos."
    }
}
for lang in ["ES", "FR", "DE", "IT", "ZH", "RU"]:
    LANG[lang] = LANG["EN"]

# ==========================================
# INTERFACE DO STREAMLIT
# ==========================================
st.set_page_config(page_title="Motor TRR", layout="centered", initial_sidebar_state="expanded")

with st.sidebar:
    idioma_escolhido = st.selectbox("🌎 Language / Idioma", ["PT", "EN", "ES", "FR", "DE", "IT", "ZH", "RU"])
    L = LANG[idioma_escolhido]
    st.markdown("---")
    st.markdown("**Autor:** Jean Cortez\n\n*Teoria da Relatividade Referencial*")

st.title(L["title"])

aba1, aba2 = st.tabs([L["tab1"], L["tab2"]])

# --- ABA 1: DINÂMICA ---
with aba1:
    c1, c2 = st.columns(2)
    rad = c1.number_input(L["rad"], min_value=0.0, format="%.2f", step=1.0, key="d_rad")
    v_obs = c2.number_input(L["vobs"], min_value=0.0, format="%.2f", step=10.0, key="d_vobs")
    
    c3, c4 = st.columns(2)
    v_gas = c3.number_input(L["vgas"], format="%.2f", step=5.0, key="d_vgas")
    v_disk = c4.number_input(L["vdisk"], min_value=0.0, format="%.2f", step=10.0, key="d_vdisk")
    v_bulge = st.number_input(L["vbulge"], min_value=0.0, format="%.2f", step=10.0, key="d_vbulge")

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button(L["calc"], type="primary", use_container_width=True, key="btn_dyn"):
            if rad > 0 and v_obs > 0:
                melhor_erro, melhor_ml, melhor_v_trr = float('inf'), 0, 0
                for ml_x in range(10, 101):
                    ml_disk = ml_x / 100.0
                    ml_bulge = ml_disk + 0.2
                    v_bar_sq = (v_gas**2) + (ml_disk * v_disk**2) + (ml_bulge * v_bulge**2)
                    if v_bar_sq < 0: continue
                    
                    g_bar = (v_bar_sq * 1e6) / (rad * 3.086e19)
                    g_obs = (v_obs**2 * 1e6) / (rad * 3.086e19)
                    x = g_bar / A0
                    g_fase = g_bar / (1 - math.exp(-math.sqrt(x)))
                    fator_impacto = v_bulge / (v_disk + abs(v_gas) + 0.1)
                    g_trr = g_fase * (1 + BETA * fator_impacto)
                    
                    erro = abs(g_obs - g_trr) / g_obs
                    if erro < melhor_erro:
                        melhor_erro, melhor_ml, melhor_v_trr = erro, ml_disk, math.sqrt((g_trr * rad * 3.086e19) / 1e6)
                
                st.session_state['res_dyn'] = {
                    'vtrr': melhor_v_trr, 'prec': max(0, 100 - (melhor_erro*100)),
                    'ml_disk': melhor_ml, 'ml_bulge': melhor_ml + 0.2
                }
    
    with col_btn2:
        st.button(L["clear"], on_click=limpar_dados, use_container_width=True, key="clr_dyn")

    # RESULTADOS DA DINÂMICA
    if 'res_dyn' in st.session_state:
        res = st.session_state['res_dyn']
        st.success(f"**{L['precision']}:** {res['prec']:.2f}%")
        
        with st.container(border=True):
            cA, cB = st.columns(2)
            cA.metric(L["v_trr"], f"{res['vtrr']:.2f} km/s")
            cB.metric(L["v_obs"], f"{v_obs:.2f} km/s")
        
        with st.expander(L["details"]):
            st.markdown(f"**{L['ml_disk']}:** `{res['ml_disk']:.2f}` | **{L['ml_bulge']}:** `{res['ml_bulge']:.2f}`")
            st.info(L["exp_dyn"])
        
        pdf_bytes = gerar_pdf_dinamica(rad, v_obs, v_gas, v_disk, v_bulge, res['vtrr'], res['prec'], res['ml_disk'], res['ml_bulge'])
        st.download_button(L["pdf_btn"], data=pdf_bytes, file_name="Relatorio_TRR_Dinamica.pdf", mime="application/pdf", type="primary", use_container_width=True)


# --- ABA 2: ÓPTICA ---
with aba2:
    c5, c6 = st.columns(2)
    zl = c5.number_input(L["zl"], min_value=0.0, format="%.4f", step=0.1, key="o_zl")
    zs = c6.number_input(L["zs"], min_value=0.0, format="%.4f", step=0.1, key="o_zs")
    
    c7, c8 = st.columns(2)
    mest = c7.number_input(L["mest"], min_value=0.0, format="%.2f", step=1.0, key="o_mest")
    theta = c8.number_input(L["theta"], min_value=0.0, format="%.2f", step=0.1, key="o_theta")
    is_cluster = st.checkbox(L["cluster"], key="o_cluster")

    col_btn3, col_btn4 = st.columns(2)
    
    with col_btn3:
        if st.button(L["calc"], type="primary", use_container_width=True, key="btn_opt"):
            if zl > 0 and zs > zl and theta > 0 and mest > 0:
                D_L, D_S, D_LS = calcular_D_A(0, zl), calcular_D_A(0, zs), calcular_D_A(zl, zs)
                melhor_erro, melhor_theta_trr, melhor_fator = float('inf'), 0, 0

                for fator_ml in [x/100.0 for x in range(50, 251)]:
                    mult_gas = 7.0 if is_cluster else 1.0
                    M_bar_kg = (mest * fator_ml * mult_gas) * 1e11 * 1.989e30
                    
                    termo_massa = (4 * G * M_bar_kg) / (C**2)
                    theta_bar_rad = math.sqrt(termo_massa * (D_LS / (D_L * D_S)))
                    g_bar = (G * M_bar_kg) / ((theta_bar_rad * D_L)**2)
                    
                    x = g_bar / A0
                    fator_fase = 1.0 / (1.0 - math.exp(-math.sqrt(x)))
                    eta_C = 1.0 + BETA * math.log(1 + zl)
                    
                    theta_trr = theta_bar_rad * math.sqrt(fator_fase) * eta_C * 206264.806
                    
                    erro = abs(theta - theta_trr) / theta
                    if erro < melhor_erro:
                        melhor_erro, melhor_theta_trr, melhor_fator = erro, theta_trr, fator_ml

                st.session_state['res_opt'] = {
                    'theta_trr': melhor_theta_trr, 'prec': max(0, 100 - (melhor_erro*100)),
                    'fator': melhor_fator, 'eta_c': 1.0 + BETA * math.log(1 + zl)
                }

    with col_btn4:
        st.button(L["clear"], on_click=limpar_dados, use_container_width=True, key="clr_opt")

    # RESULTADOS DA ÓPTICA
    if 'res_opt' in st.session_state:
        res = st.session_state['res_opt']
        st.success(f"**{L['precision']}:** {res['prec']:.2f}%")
        
        with st.container(border=True):
            cC, cD = st.columns(2)
            cC.metric(L["theta_trr"], f"{res['theta_trr']:.2f} arcsec")
            cD.metric(L["theta_obs"], f"{theta:.2f} arcsec")
            
        with st.expander(L["details"]):
            st.markdown(f"**{L['mest_opt']}:** `{mest * res['fator']:.2f} x 10^11 M_sol`\n\n**{L['eta_c']}:** `{res['eta_c']:.5f}`")
            st.info(L["exp_opt"])

        pdf_bytes2 = gerar_pdf_optica(zl, zs, mest, theta, is_cluster, res['theta_trr'], res['prec'], res['fator'], res['eta_c'])
        st.download_button(L["pdf_btn"], data=pdf_bytes2, file_name="Relatorio_TRR_Optica.pdf", mime="application/pdf", type="primary", use_container_width=True)
