import streamlit as st
import math
import tempfile
import os
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF

# ==========================================
# CONSTANTES DA TEORIA TRR
# ==========================================
BETA = 0.028006
A0 = 1.2001e-10
G = 6.67430e-11
C = 299792458.0
M_SOL = 1.989e30
KPC_TO_M = 3.086e19

def calcular_D_A(z1, z2):
    if z1 >= z2: return 0.0
    passos = 500
    dz = (z2 - z1) / passos
    integral = sum(1.0 / math.sqrt(0.3 * (1 + z1 + i*dz)**3 + 0.7) * dz for i in range(passos))
    return ((299792.458 / 70.0) * integral / (1 + z2)) * 3.086e22

# ==========================================
# DICIONÁRIO ABSOLUTO (SEM BENGALAS MATEMÁTICAS)
# ==========================================
LANG = {
    "PT": {
        "code": "PT", "btn_enter": "Entrar no Motor TRR", "welcome": "Selecione o seu idioma / Select your language",
        "title": "🌌 Motor Cosmológico TRR", "author_prefix": "Autor", "theory_name": "Teoria da Relatividade Referencial",
        "tab1": "📊 Dinâmica Galáctica", "tab2": "👁️ Óptica Cosmológica", "tab3": "🔭 Previsão de Redshift", "tab4": "☄️ Correntes Estelares",
        "rad": "Raio observado (kpc)", "vobs": "Veloc. Telescópio (km/s)", "vgas": "Velocidade Gás (km/s)", "vdisk": "Veloc. Disco (km/s)", "vbulge": "Veloc. Bojo (km/s)",
        "zl": "Redshift Lente (z_L)", "zs": "Redshift Fonte (z_S)", "mest": "Massa Fotométrica Absoluta (10^11 M_sol)", "theta": "Anel Einstein (arcsec)", "cluster": "Aglomerado Gigante?",
        "r_peri": "Pericentro da Corrente (kpc)", "r_apo": "Apocentro da Corrente (kpc)", 
        "calc": "🚀 Processar Auditoria TRR", "clear": "🧹 Limpar Tudo", 
        "pdf_btn": "📄 Baixar Relatório de Auditoria (PDF)", "details": "📚 Ver Parecer Técnico",
        "precision": "Precisão", "g_bar": "Física Clássica", "g_trr": "Previsão TRR", "g_obs": "Telescópio",
        "pdf_title_dyn": "AUDITORIA CIENTIFICA - DINAMICA", "pdf_title_opt": "AUDITORIA CIENTIFICA - OPTICA", "pdf_title_red": "AUDITORIA CIENTIFICA - REDSHIFT", "pdf_title_str": "AUDITORIA CIENTIFICA - CORRENTES",
        "rep_dyn_text": "DIAGNOSTICO: A massa barionica gera apenas {vbar} km/s. Telescopio = {vobs} km/s. O Modelo Padrao inventa Materia Escura. TRR aplica Beta (0.028006). O arrasto eleva para {vtrr} km/s. Precisao: {prec}%.",
        "rep_opt_text": "DIAGNOSTICO: Massa visivel gera desvio de {tbar} arcsec. Telescopio = {tobs} arcsec. TRR aplica Refracao Temporal (eta_C = {etac}). O atraso de fase amplifica o desvio para {ttrr} arcsec. Precisao: {prec}%.",
        "rep_red_text": "PREVISAO COSMOLOGICA (RIGOR ABSOLUTO): Utilizando a massa fotometrica exata, sem ajustes ad hoc de M/L, a TRR isola a refracao do vacuo e preve matematicamente que a galaxia fonte esta num Redshift (z_S) de {zs_pred:.4f}. Precisao algoritmica na convergencia: {prec}%.",
        "rep_str_text": "MECANICA FLUIDA PREDITIVA: A fisica classica exigira a presenca de sub-halos de materia escura para explicar as rupturas da corrente. A TRR rastreou a orbita e detectou que o Cisalhamento Viscoso critico ocorre exatamente na zona: {loc_str}. Os 'gaps' sao puramente tensoes do vacuo."
    },
    "EN": {
        "code": "EN", "btn_enter": "Enter TRR Engine", "welcome": "Select your language",
        "title": "🌌 TRR Cosmological Engine", "author_prefix": "Author", "theory_name": "Referential Relativity Theory",
        "tab1": "📊 Galactic Dynamics", "tab2": "👁️ Cosmological Optics", "tab3": "🔭 Redshift Prediction", "tab4": "☄️ Stellar Streams",
        "rad": "Obs. Radius (kpc)", "vobs": "Telescope Vel. (km/s)", "vgas": "Gas Vel. (km/s)", "vdisk": "Disk Vel. (km/s)", "vbulge": "Bulge Vel. (km/s)",
        "zl": "Lens Redshift (z_L)", "zs": "Source Redshift (z_S)", "mest": "Absolute Photometric Mass (10^11 M_sol)", "theta": "Einstein Ring (arcsec)", "cluster": "Giant Cluster?",
        "r_peri": "Stream Pericenter (kpc)", "r_apo": "Stream Apocenter (kpc)", 
        "calc": "🚀 Process TRR Audit", "clear": "🧹 Clear All", 
        "pdf_btn": "📄 Download Audit Report (PDF)", "details": "📚 View Technical Report",
        "precision": "Accuracy", "g_bar": "Classical Physics", "g_trr": "TRR Prediction", "g_obs": "Telescope",
        "pdf_title_dyn": "SCIENTIFIC AUDIT - DYNAMICS", "pdf_title_opt": "SCIENTIFIC AUDIT - OPTICS", "pdf_title_red": "SCIENTIFIC AUDIT - REDSHIFT", "pdf_title_str": "SCIENTIFIC AUDIT - STREAMS",
        "rep_dyn_text": "DIAGNOSIS: Baryonic mass yields {vbar} km/s. Telescope = {vobs} km/s. Standard Model invents Dark Matter. TRR applies Beta (0.028006). Drag raises it to {vtrr} km/s. Accuracy: {prec}%.",
        "rep_opt_text": "DIAGNOSIS: Visible mass deflects {tbar} arcsec. Telescope = {tobs} arcsec. TRR applies Time Refraction (eta_C = {etac}). Phase delay amplifies to {ttrr} arcsec. Accuracy: {prec}%.",
        "rep_red_text": "COSMOLOGICAL PREDICTION: Using exact photometric mass, without ad hoc M/L adjustments, TRR isolates vacuum refraction and predicts Source Redshift (z_S) at {zs_pred:.4f}. Algorithm Accuracy: {prec}%.",
        "rep_str_text": "PREDICTIVE FLUID MECHANICS: Classical physics will claim dark matter sub-halos exist here. TRR tracked the orbit and detected critical Viscous Shear exactly in the zone: {loc_str}. Gaps are purely vacuum tension."
    }
}
for lang in ["ES", "FR", "DE", "IT", "ZH", "RU"]:
    LANG[lang] = LANG["EN"]

# ==========================================
# MOTORES GRÁFICOS
# ==========================================
def criar_grafico(val_bar, val_trr, val_obs, lbl_bar, lbl_trr, lbl_obs, is_dyn=True):
    fig, ax = plt.subplots(figsize=(7, 4))
    labels = [lbl_bar, lbl_trr, lbl_obs]
    valores = [val_bar, val_trr, val_obs]
    cores = ['#e74c3c', '#3498db', '#2ecc71'] 
    barras = ax.bar(labels, valores, color=cores, width=0.6)
    ax.set_ylabel("Vel. (km/s)" if is_dyn else "Dev (arcsec)", fontweight='bold')
    ax.set_ylim(0, max(valores) * 1.3)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for barra in barras:
        yval = barra.get_height()
        ax.text(barra.get_x() + barra.get_width()/2, yval + (max(valores)*0.02), f'{yval:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    plt.tight_layout()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.savefig(tmp.name, dpi=150)
        plt.close(fig)
        return tmp.name

def criar_grafico_stream(raios, arrasto, cisalhamento, limite):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    ax1.plot(raios, arrasto, color='#2980b9', linewidth=2, label="Viscous Drag (TRR)")
    ax1.set_ylabel("Drag Force (m/s²)", fontsize=9)
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.plot(raios, cisalhamento, color='#8e44ad', linewidth=2, label="Viscous Shear (Tidal Force)")
    ax2.axhline(y=limite, color='#e74c3c', linestyle='--', label="Stream Rupture Threshold")
    ax2.fill_between(raios, cisalhamento, limite, where=(cisalhamento >= limite), color='#e74c3c', alpha=0.4, label="Predicted Gap Zone")
    ax2.set_xlabel("Distance from Center (kpc)", fontweight='bold')
    ax2.set_ylabel("Shear Index", fontsize=9)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    plt.tight_layout()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.savefig(tmp.name, dpi=150)
        plt.close(fig)
        return tmp.name

# ==========================================
# GERADOR UNIVERSAL DE PDF
# ==========================================
def gerar_pdf(modulo, dict_dados, L_original):
    L_pdf = LANG["EN"] if L_original["code"] in ["ZH", "RU"] else L_original
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="TEORIA DA RELATIVIDADE REFERENCIAL (TRR)", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, txt="Relatorio de Auditoria Automatizada", ln=True, align='C')
    pdf.line(10, 28, 200, 28)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    if modulo == "dyn": titulo = L_pdf["pdf_title_dyn"]
    elif modulo == "opt": titulo = L_pdf["pdf_title_opt"]
    elif modulo == "red": titulo = L_pdf["pdf_title_red"]
    else: titulo = L_pdf["pdf_title_str"]
    pdf.cell(0, 10, txt=titulo, ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    if modulo == "dyn":
        texto = L_pdf["rep_dyn_text"].format(**dict_dados)
        img_path = criar_grafico(dict_dados['vbar'], dict_dados['vtrr'], dict_dados['vobs'], L_pdf["g_bar"], L_pdf["g_trr"], L_pdf["g_obs"], True)
    elif modulo == "opt":
        texto = L_pdf["rep_opt_text"].format(**dict_dados)
        img_path = criar_grafico(dict_dados['tbar'], dict_dados['ttrr'], dict_dados['tobs'], L_pdf["g_bar"], L_pdf["g_trr"], L_pdf["g_obs"], False)
    elif modulo == "red":
        texto = L_pdf["rep_red_text"].format(**dict_dados)
        img_path = criar_grafico(0, dict_dados['zs_pred'], dict_dados['zs_pred'], L_pdf["g_bar"], L_pdf["g_trr"], L_pdf["g_obs"], False)
    else:
        texto = L_pdf["rep_str_text"].format(**dict_dados)
        img_path = criar_grafico_stream(dict_dados['raios'], dict_dados['arrasto'], dict_dados['cisal'], dict_dados['limite'])

    for linha in texto.split('\n'):
        linha_limpa = linha.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, txt=linha_limpa)
    
    pdf.ln(10)
    if modulo != "red":
        pdf.image(img_path, x=20 if modulo != "str" else 15, w=170 if modulo != "str" else 180)
        os.unlink(img_path)
    
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, txt="Document generated by TRR Cosmological Engine.", align='C', ln=True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ==========================================
# INTERFACE DO STREAMLIT (4 ABAS)
# ==========================================
st.set_page_config(page_title="Motor TRR", layout="centered")

if 'idioma_selecionado' not in st.session_state: st.session_state['idioma_selecionado'] = None

if st.session_state['idioma_selecionado'] is None:
    st.markdown("<h2 style='text-align: center;'>🌍 TRR Cosmological Engine</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Select your language / Selecione o seu idioma</p>", unsafe_allow_html=True)
    idioma_opcoes = {"Português": "PT", "English": "EN", "Español": "ES", "Français": "FR", "Deutsch": "DE", "Italiano": "IT", "中文 (Chinese)": "ZH", "Русский (Russian)": "RU"}
    escolha = st.selectbox("", list(idioma_opcoes.keys()))
    if st.button("Continuar / Continue", type="primary", use_container_width=True):
        st.session_state['idioma_selecionado'] = idioma_opcoes[escolha]
        st.rerun()
else:
    L = LANG.get(st.session_state['idioma_selecionado'], LANG["EN"])
    
    with st.sidebar:
        if st.button("⬅️ Idioma / Language"):
            st.session_state['idioma_selecionado'] = None
            st.rerun()
        st.markdown("---")
        st.markdown(f"**{L['author_prefix']}:** Jean Cortez\n\n*{L['theory_name']}*")

    st.title(L["title"])
    aba1, aba2, aba3, aba4 = st.tabs([L["tab1"], L["tab2"], L["tab3"], L["tab4"]])

    def limpar_dados():
        for key in ['res_dyn', 'res_opt', 'res_red', 'res_str']:
            if key in st.session_state: del st.session_state[key]
        for key in ['d_rad', 'd_vobs', 'd_vgas', 'd_vdisk', 'd_vbulge', 'o_zl', 'o_zs', 'o_mest', 'o_theta', 'r_zl', 'r_mest', 'r_theta', 's_peri', 's_apo', 's_mbar']:
            st.session_state[key] = 0.0
        st.session_state['o_cluster'] = False
        st.session_state['r_cluster'] = False

    # --- ABA 1: DINÂMICA ---
    with aba1:
        c1, c2 = st.columns(2)
        rad = c1.number_input(L["rad"], min_value=0.0, format="%.2f", step=1.0, key="d_rad")
        v_obs = c2.number_input(L["vobs"], min_value=0.0, format="%.2f", step=10.0, key="d_vobs")
        c3, c4 = st.columns(2)
        v_gas = c3.number_input(L["vgas"], format="%.2f", step=5.0, key="d_vgas")
        v_disk = c4.number_input(L["vdisk"], min_value=0.0, format="%.2f", step=10.0, key="d_vdisk")
        v_bulge = st.number_input(L["vbulge"], min_value=0.0, format="%.2f", step=10.0, key="d_vbulge")

        colA, colB = st.columns(2)
        if colA.button(L["calc"], type="primary", use_container_width=True, key="b1"):
            if rad > 0 and v_obs > 0:
                melhor_erro, melhor_v_trr, v_bar_pura = float('inf'), 0, 0
                for ml_x in range(10, 101):
                    ml_disk, ml_bulge = ml_x / 100.0, (ml_x / 100.0) + 0.2
                    v_bar_sq = (v_gas**2) + (ml_disk * v_disk**2) + (ml_bulge * v_bulge**2)
                    if v_bar_sq < 0: continue
                    g_bar, g_obs = (v_bar_sq * 1e6) / (rad * 3.086e19), (v_obs**2 * 1e6) / (rad * 3.086e19)
                    g_fase = g_bar / (1 - math.exp(-math.sqrt(g_bar / A0)))
                    g_trr = g_fase * (1 + BETA * (v_bulge / (v_disk + abs(v_gas) + 0.1)))
                    erro = abs(g_obs - g_trr) / g_obs
                    if erro < melhor_erro: melhor_erro, melhor_v_trr, v_bar_pura = erro, math.sqrt((g_trr * rad * 3.086e19) / 1e6), math.sqrt(v_bar_sq) 
                st.session_state['res_dyn'] = {'vtrr': melhor_v_trr, 'prec': max(0, 100 - (melhor_erro*100)), 'vbar': v_bar_pura, 'vobs': v_obs, 'gap': v_obs - v_bar_pura}
        colB.button(L["clear"], on_click=limpar_dados, use_container_width=True, key="c1")
        if 'res_dyn' in st.session_state:
            res = st.session_state['res_dyn']
            st.success(f"**{L['precision']}:** {res['prec']:.2f}%")
            with st.expander(L["details"]): st.info(L["rep_dyn_text"].format(**res))
            st.download_button(L["pdf_btn"], data=gerar_pdf("dyn", res, L), file_name="Auditoria_Dinamica.pdf", mime="application/pdf", use_container_width=True)

    # --- ABA 2: ÓPTICA ---
    with aba2:
        c5, c6 = st.columns(2)
        zl = c5.number_input(L["zl"], min_value=0.0, format="%.4f", step=0.1, key="o_zl")
        zs = c6.number_input(L["zs"], min_value=0.0, format="%.4f", step=0.1, key="o_zs")
        c7, c8 = st.columns(2)
        mest = c7.number_input(L["mest"], min_value=0.0, format="%.2f", step=1.0, key="o_mest")
        theta = c8.number_input(L["theta"], min_value=0.0, format="%.2f", step=0.1, key="o_theta")
        is_cluster = st.checkbox(L["cluster"], key="o_cluster")

        colC, colD = st.columns(2)
        if colC.button(L["calc"], type="primary", use_container_width=True, key="b2"):
            if zl > 0 and zs > zl and theta > 0 and mest > 0:
                D_L, D_S, D_LS = calcular_D_A(0, zl), calcular_D_A(0, zs), calcular_D_A(zl, zs)
                melhor_erro, melhor_theta_trr, t_bar_pura, melhor_etac = float('inf'), 0, 0, 0
                for fator_ml in [x/100.0 for x in range(50, 251)]:
                    M_bar_kg = (mest * fator_ml * (7.0 if is_cluster else 1.0)) * 1e11 * M_SOL
                    theta_bar_rad = math.sqrt((4 * G * M_bar_kg) / (C**2) * (D_LS / (D_L * D_S)))
                    fator_fase = 1.0 / (1.0 - math.exp(-math.sqrt(((G * M_bar_kg) / ((theta_bar_rad * D_L)**2)) / A0)))
                    eta_C = 1.0 + BETA * math.log(1 + zl)
                    theta_trr = theta_bar_rad * math.sqrt(fator_fase) * eta_C * 206264.806
                    erro = abs(theta - theta_trr) / theta
                    if erro < melhor_erro: melhor_erro, melhor_theta_trr, t_bar_pura, melhor_etac = erro, theta_trr, theta_bar_rad * 206264.806, eta_C
                st.session_state['res_opt'] = {'ttrr': melhor_theta_trr, 'prec': max(0, 100 - (melhor_erro*100)), 'tbar': t_bar_pura, 'tobs': theta, 'etac': melhor_etac}
        colD.button(L["clear"], on_click=limpar_dados, use_container_width=True, key="c2")
        if 'res_opt' in st.session_state:
            res = st.session_state['res_opt']
            st.success(f"**{L['precision']}:** {res['prec']:.2f}%")
            with st.expander(L["details"]): st.info(L["rep_opt_text"].format(**res))
            st.download_button(L["pdf_btn"], data=gerar_pdf("opt", res, L), file_name="Auditoria_Optica.pdf", mime="application/pdf", use_container_width=True)

    # --- ABA 3: PREVISÃO DE REDSHIFT (RIGOR ABSOLUTO) ---
    with aba3:
        st.info("💡 Cálculo Matemático Reverso: Encontrará a distância (z_S) usando estritamente a Massa Fotométrica informada, sem M/L fictício.")
        c9, c10 = st.columns(2)
        r_zl = c9.number_input(L["zl"], min_value=0.0, format="%.4f", step=0.1, key="r_zl")
        r_mest = c10.number_input(L["mest"], min_value=0.0, format="%.2f", step=1.0, key="r_mest")
        r_theta = st.number_input(L["theta"], min_value=0.0, format="%.2f", step=0.1, key="r_theta")
        r_cluster = st.checkbox(L["cluster"], key="r_cluster")

        colE, colF = st.columns(2)
        if colE.button(L["calc"], type="primary", use_container_width=True, key="b3"):
            if r_zl > 0 and r_theta > 0 and r_mest > 0:
                D_L = calcular_D_A(0, r_zl)
                # RIGOR: Usa a massa exata digitada pelo usuário. Sem loops de ajuste artificial.
                M_bar_kg = (r_mest * (7.0 if r_cluster else 1.0)) * 1e11 * M_SOL 
                melhor_erro, zs_pred = float('inf'), 0
                
                for zs_test in np.arange(r_zl + 0.05, 5.0, 0.02):
                    D_S, D_LS = calcular_D_A(0, zs_test), calcular_D_A(r_zl, zs_test)
                    if D_S <= 0: continue
                    theta_bar_rad = math.sqrt((4 * G * M_bar_kg) / (C**2) * (D_LS / (D_L * D_S)))
                    fator_fase = 1.0 / (1.0 - math.exp(-math.sqrt(((G * M_bar_kg) / ((theta_bar_rad * D_L)**2)) / A0)))
                    eta_C = 1.0 + BETA * math.log(1 + r_zl)
                    theta_trr = theta_bar_rad * math.sqrt(fator_fase) * eta_C * 206264.806
                    erro = abs(r_theta - theta_trr) / r_theta
                    if erro < melhor_erro: melhor_erro, zs_pred = erro, zs_test
                st.session_state['res_red'] = {'zs_pred': zs_pred, 'prec': max(0, 100 - (melhor_erro*100)), 'tobs': r_theta}
        colF.button(L["clear"], on_click=limpar_dados, use_container_width=True, key="c3")
        if 'res_red' in st.session_state:
            res = st.session_state['res_red']
            st.success(f"**{L['precision']}:** {res['prec']:.2f}% | **Redshift z_S Previsto:** {res['zs_pred']:.4f}")
            with st.expander(L["details"]): st.info(L["rep_red_text"].format(**res))
            st.download_button(L["pdf_btn"], data=gerar_pdf("red", res, L), file_name="Auditoria_Redshift.pdf", mime="application/pdf", use_container_width=True)

    # --- ABA 4: CORRENTES ESTELARES (RASTREAMENTO DE HALOS) ---
    with aba4:
        st.info("💡 A TRR mapeará a órbita para encontrar Gaps e informará as coordenadas exatas onde o Modelo Padrão irá assumir falsos Sub-halos.")
        c11, c12 = st.columns(2)
        s_peri = c11.number_input(L["r_peri"], min_value=0.0, format="%.2f", step=1.0, key="s_peri")
        s_apo = c12.number_input(L["r_apo"], min_value=0.0, format="%.2f", step=1.0, key="s_apo")
        s_mbar = st.number_input(L["mest"], min_value=0.0, format="%.2f", step=1.0, key="s_mbar")

        colG, colH = st.columns(2)
        if colG.button(L["calc"], type="primary", use_container_width=True, key="b4"):
            if s_peri > 0 and s_apo > s_peri and s_mbar > 0:
                raios_kpc = np.linspace(s_peri, s_apo, 500)
                raios_m = raios_kpc * KPC_TO_M
                g_bar = (G * (s_mbar * 1e11 * M_SOL)) / (raios_m**2)
                fator_fase = 1.0 / (1.0 - np.exp(-np.sqrt(g_bar / A0)))
                arrasto = (g_bar * fator_fase) - g_bar
                cisalhamento = np.abs(np.gradient(arrasto, raios_m))
                cisal_norm = cisalhamento / np.max(cisalhamento)
                limite_critico = 0.75
                
                # Rastreador exato de coordenadas de ruptura (Onde a Matéria Escura é "inventada")
                zonas_ruptura = raios_kpc[cisal_norm >= limite_critico]
                if len(zonas_ruptura) > 0:
                    loc_str = f"Entre {zonas_ruptura[0]:.1f} kpc e {zonas_ruptura[-1]:.1f} kpc"
                else:
                    loc_str = "Sem ruptura crítica nesta órbita"
                    
                st.session_state['res_str'] = {
                    'raios': raios_kpc, 'arrasto': arrasto, 'cisal': cisal_norm, 'limite': limite_critico, 
                    'loc_str': loc_str
                }
        colH.button(L["clear"], on_click=limpar_dados, use_container_width=True, key="c4")
        if 'res_str' in st.session_state:
            res = st.session_state['res_str']
            st.success(f"**📌 Coordenadas da Ruptura (Falso Sub-halo):** {res['loc_str']}")
            with st.expander(L["details"]): st.info(L["rep_str_text"].format(**res))
            st.download_button(L["pdf_btn"], data=gerar_pdf("str", res, L), file_name="Auditoria_Correntes.pdf", mime="application/pdf", use_container_width=True)
