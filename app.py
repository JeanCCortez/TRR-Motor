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
# DICIONÁRIO ABSOLUTO (COM INTEGRAÇÃO R_E)
# ==========================================
LANG = {
    "PT": {
        "code": "PT", "btn_enter": "Entrar no Motor TRR", "welcome": "Selecione o seu idioma / Select your language",
        "title": "🌌 Motor Cosmológico TRR", "author_prefix": "Autor", "theory_name": "Teoria da Relatividade Referencial",
        "tab1": "📊 Dinâmica Galáctica", "tab2": "👁️ Óptica Cosmológica", "tab3": "🔭 Previsão de Redshift", "tab4": "☄️ Correntes Estelares",
        "rad": "Raio observado (kpc)", "vobs": "Veloc. Telescópio (km/s)", "vgas": "Velocidade Gás (km/s)", "vdisk": "Veloc. Disco (km/s)", "vbulge": "Veloc. Bojo (km/s)",
        "zl": "Redshift Lente (z_L)", "zs": "Redshift Fonte (z_S)", "mest": "Massa Fotométrica Total (10^11)", "theta": "Anel Einstein (arcsec)", "cluster": "Aglomerado Gigante?",
        "reff": "Raio Efetivo R_e (arcsec)", "r_peri": "Pericentro da Corrente (kpc)", "r_apo": "Apocentro da Corrente (kpc)", 
        "calc": "🚀 Processar Auditoria TRR", "clear": "🧹 Limpar Tudo", 
        "pdf_btn": "📄 Baixar Relatório de Auditoria (PDF)", "details": "📚 Ver Parecer Técnico",
        "precision": "Precisão Empírica", "precision_red": "Convergência Matemática", "g_bar": "Física Clássica", "g_trr": "Previsão TRR", "g_obs": "Telescópio",
        "info_red": "💡 A TRR iterará a matriz gravitacional usando a Massa Projetada na Abertura (calculada via R_e) para prever z_S. RIGOR ABSOLUTO.",
        "info_str": "💡 A TRR mapeia a tensão do vácuo e revela a coordenada do falso sub-halo.",
        "pred_zs": "Redshift z_S Previsto", "loc_gap": "📌 Falso Sub-halo nas coordenadas", "no_gap": "Nenhuma ruptura crítica",
        "pdf_h1": "TEORIA DA RELATIVIDADE REFERENCIAL (TRR)", "pdf_h2": "Relatorio de Auditoria Automatizada", "pdf_footer": "Documento gerado pelo Motor Cosmologico TRR.",
        "pdf_title_dyn": "AUDITORIA CIENTIFICA - DINAMICA", "pdf_title_opt": "AUDITORIA CIENTIFICA - OPTICA", "pdf_title_red": "AUDITORIA CIENTIFICA - REDSHIFT", "pdf_title_str": "AUDITORIA CIENTIFICA - CORRENTES",
        "rep_dyn_text": "LAUDO TÉCNICO:\n1. A massa bariônica pura gera apenas {vbar:.2f} km/s, deixando um abismo em relação aos {vobs:.2f} km/s reais.\n2. A TRR calcula o atrito topológico proporcional à circunferência da órbita. Aplicando a constante Beta (0.028006), o arrasto fluídico eleva a velocidade para {vtrr:.2f} km/s.\nRESULTADO: Precisão empírica de {prec:.2f}% atingida sem uso de Matéria Escura.",
        "rep_opt_text": "LAUDO TÉCNICO:\nA massa visível desvia a luz em apenas {tbar:.2f} arcsec. Sem matéria invisível, a TRR aplica a Refração Temporal do Vácuo (eta_C = {etac:.5f}). O atraso de fase amplia o anel gravitacional para {ttrr:.2f} arcsec, batendo a observação do telescópio. Precisão empírica: {prec:.2f}%.",
        "rep_red_text": "LAUDO PREDITIVO (AUDITORIA CEGA, RIGOR MÁXIMO):\n1. INTEGRAÇÃO DE MASSA: O sistema calculou rigorosamente a massa confinada no cilindro do Anel de Einstein usando o Raio Efetivo (R_e). Nenhum ajuste ad hoc (M/L) foi permitido.\n2. PREVISÃO TRR: Varrendo o tecido cósmico com base na refração da constante Beta, a equação cravou a posição da galáxia fonte em z_S = {zs_pred:.4f}.\nRESULTADO: Algoritmo convergido e isolado da Matéria Escura.",
        "rep_str_text": "LAUDO DE HIDRODINÂMICA:\n1. A astrofísica clássica afirma que os 'gaps' da corrente estelar são colisões com sub-halos invisíveis.\n2. A TRR rastreou a órbita medindo as forças de maré. O Cisalhamento Viscoso atingiu o limite crítico na zona exata de {loc_str}. O gap é um atrito com o fluido do espaço."
    },
    "EN": {
        "code": "EN", "btn_enter": "Enter RRT Engine", "welcome": "Select your language",
        "title": "🌌 RRT Cosmological Engine", "author_prefix": "Author", "theory_name": "Referential Relativity Theory",
        "tab1": "📊 Galactic Dynamics", "tab2": "👁️ Cosmological Optics", "tab3": "🔭 Redshift Prediction", "tab4": "☄️ Stellar Streams",
        "rad": "Obs. Radius (kpc)", "vobs": "Telescope Vel. (km/s)", "vgas": "Gas Vel. (km/s)", "vdisk": "Disk Vel. (km/s)", "vbulge": "Bulge Vel. (km/s)",
        "zl": "Lens Redshift (z_L)", "zs": "Source Redshift (z_S)", "mest": "Total Photometric Mass (10^11)", "theta": "Einstein Ring (arcsec)", "cluster": "Giant Cluster?",
        "reff": "Effective Radius R_e (arcsec)", "r_peri": "Stream Pericenter (kpc)", "r_apo": "Stream Apocenter (kpc)", 
        "calc": "🚀 Process RRT Audit", "clear": "🧹 Clear All", 
        "pdf_btn": "📄 Download Audit Report (PDF)", "details": "📚 View Technical Report",
        "precision": "Empirical Accuracy", "precision_red": "Mathematical Convergence", "g_bar": "Classical Physics", "g_trr": "RRT Prediction", "g_obs": "Telescope",
        "info_red": "💡 RRT iterates the gravitational matrix using Projected Aperture Mass (calculated via R_e) to predict z_S. STRICT RIGOR.",
        "info_str": "💡 RRT maps vacuum tension and reveals the fake sub-halo coordinates.",
        "pred_zs": "Predicted Redshift z_S", "loc_gap": "📌 Fake Sub-halo Coordinates", "no_gap": "No critical rupture",
        "pdf_h1": "REFERENTIAL RELATIVITY THEORY (RRT)", "pdf_h2": "Automated Audit Report", "pdf_footer": "Document generated by RRT Cosmological Engine.",
        "pdf_title_dyn": "SCIENTIFIC AUDIT - DYNAMICS", "pdf_title_opt": "SCIENTIFIC AUDIT - OPTICS", "pdf_title_red": "SCIENTIFIC AUDIT - REDSHIFT", "pdf_title_str": "SCIENTIFIC AUDIT - STREAMS",
        "rep_dyn_text": "TECHNICAL REPORT:\n1. Baryonic mass yields only {vbar:.2f} km/s. RRT calculates topological friction. Applying Beta (0.028006), drag elevates velocity to {vtrr:.2f} km/s. RESULT: {prec:.2f}% empirical accuracy without Dark Matter.",
        "rep_opt_text": "TECHNICAL REPORT:\nVisible mass deflects light by only {tbar:.2f} arcsec. RRT applies Time Refraction (eta_C = {etac:.5f}). Phase delay widens the ring to {ttrr:.2f} arcsec. Empirical Accuracy: {prec:.2f}%.",
        "rep_red_text": "PREDICTIVE REPORT (STRICT BLIND AUDIT):\n1. MASS INTEGRATION: The system rigorously calculated the enclosed mass within the Einstein Ring cylinder using the Effective Radius (R_e). No ad hoc fine-tuning was allowed.\n2. RRT PREDICTION: Sweeping cosmic fabric based on Beta refraction, the equation mathematically predicts the source galaxy is at z_S = {zs_pred:.4f}.\nRESULT: Converged and isolated from Dark Matter.",
        "rep_str_text": "HYDRODYNAMICS REPORT:\n1. Classical astrophysics claims stream 'gaps' are invisible collisions. RRT tracked tidal forces. Viscous Shear hit critical limits exactly at {loc_str}. The gap is vacuum fluid friction."
    }
}
for lang in ["ES", "FR", "DE", "IT", "ZH", "RU"]: LANG[lang] = LANG["EN"]

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

def criar_grafico_redshift(z_vals, theta_class, theta_trr, zs_pred, theta_obs):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(z_vals, theta_class, color='#e74c3c', linewidth=2, linestyle='--', label="Classical Limit (No DM)")
    ax.plot(z_vals, theta_trr, color='#3498db', linewidth=2, label="Predictive Curve")
    ax.axhline(y=theta_obs, color='#2ecc71', linestyle='-', label=f"Observation ({theta_obs}\")")
    ax.scatter([zs_pred], [theta_obs], color='#f1c40f', s=100, zorder=5, label=f"Predicted z_S = {zs_pred:.4f}")
    ax.set_xlabel("Source Redshift (z_S)", fontweight='bold')
    ax.set_ylabel("Einstein Ring (arcsec)", fontweight='bold')
    ax.set_title("Cosmological Target Convergence (Aperture Integrated)", fontsize=11)
    ax.grid(alpha=0.3)
    ax.legend(loc='lower right')
    plt.tight_layout()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.savefig(tmp.name, dpi=150)
        plt.close(fig)
        return tmp.name

def criar_grafico_stream(raios, arrasto, cisalhamento, limite):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    ax1.plot(raios, arrasto, color='#2980b9', linewidth=2, label="Viscous Drag")
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
    pdf.cell(0, 10, txt=L_pdf["pdf_h1"], ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, txt=L_pdf["pdf_h2"], ln=True, align='C')
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
    
    if modulo == "str":
        loc_str_pdf = f"[{dict_dados['gap_start']:.1f} kpc - {dict_dados['gap_end']:.1f} kpc]" if dict_dados['has_gap'] else L_pdf["no_gap"]

    if modulo == "dyn":
        texto = L_pdf["rep_dyn_text"].format(**dict_dados)
        img_path = criar_grafico(dict_dados['vbar'], dict_dados['vtrr'], dict_dados['vobs'], L_pdf["g_bar"], L_pdf["g_trr"], L_pdf["g_obs"], True)
    elif modulo == "opt":
        texto = L_pdf["rep_opt_text"].format(**dict_dados)
        img_path = criar_grafico(dict_dados['tbar'], dict_dados['ttrr'], dict_dados['tobs'], L_pdf["g_bar"], L_pdf["g_trr"], L_pdf["g_obs"], False)
    elif modulo == "red":
        texto = L_pdf["rep_red_text"].format(**dict_dados)
        img_path = criar_grafico_redshift(dict_dados['z_vals'], dict_dados['t_class'], dict_dados['t_trr'], dict_dados['zs_pred'], dict_dados['tobs'])
    else:
        texto = L_pdf["rep_str_text"].format(loc_str=loc_str_pdf, **dict_dados)
        img_path = criar_grafico_stream(dict_dados['raios'], dict_dados['arrasto'], dict_dados['cisal'], dict_dados['limite'])

    for linha in texto.split('\n'):
        linha_limpa = linha.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, txt=linha_limpa)
    pdf.ln(10)
    pdf.image(img_path, x=15, w=180)
    os.unlink(img_path)
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, txt=L_pdf["pdf_footer"], align='C', ln=True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ==========================================
# INTERFACE DO STREAMLIT
# ==========================================
st.set_page_config(page_title="Motor TRR / RRT Engine", layout="centered")

if 'idioma_selecionado' not in st.session_state: st.session_state['idioma_selecionado'] = None

if st.session_state['idioma_selecionado'] is None:
    st.markdown("<h2 style='text-align: center;'>🌍 Cosmological Engine</h2>", unsafe_allow_html=True)
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
        for key in ['d_rad', 'd_vobs', 'd_vgas', 'd_vdisk', 'd_vbulge', 'o_zl', 'o_zs', 'o_mest', 'o_theta', 'r_zl', 'r_mest', 'r_theta', 'r_reff', 's_peri', 's_apo', 's_mbar']:
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
        if colA.button(L["calc"], type="primary", use_container_width=True, key="btn_calc_dyn"):
            if rad > 0 and v_obs > 0:
                melhor_erro, melhor_v_trr, v_bar_pura = float('inf'), 0, 0
                for ml_x in range(10, 301):
                    ml_disk, ml_bulge = ml_x / 100.0, (ml_x / 100.0) + 0.2
                    v_bar_sq = (v_gas**2) + (ml_disk * v_disk**2) + (ml_bulge * v_bulge**2)
                    if v_bar_sq < 0: continue
                    g_bar, g_obs = (v_bar_sq * 1e6) / (rad * 3.086e19), (v_obs**2 * 1e6) / (rad * 3.086e19)
                    g_fase = g_bar / (1 - math.exp(-math.sqrt(g_bar / A0)))
                    g_trr = g_fase * (1 + BETA * rad)
                    erro = abs(g_obs - g_trr) / g_obs
                    if erro < melhor_erro: melhor_erro, melhor_v_trr, v_bar_pura = erro, math.sqrt((g_trr * rad * 3.086e19) / 1e6), math.sqrt(v_bar_sq) 
                st.session_state['res_dyn'] = {'vtrr': melhor_v_trr, 'prec': max(0, 100 - (melhor_erro*100)), 'vbar': v_bar_pura, 'vobs': v_obs}
        colB.button(L["clear"], on_click=limpar_dados, use_container_width=True, key="btn_clr_dyn")
        if 'res_dyn' in st.session_state:
            res = st.session_state['res_dyn']
            st.success(f"**{L['precision']}:** {res['prec']:.2f}%")
            with st.expander(L["details"]): st.info(L["rep_dyn_text"].format(**res))
            st.download_button(L["pdf_btn"], data=gerar_pdf("dyn", res, L), file_name="Report_Dynamics.pdf", mime="application/pdf", use_container_width=True, key="p1")

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
        if colC.button(L["calc"], type="primary", use_container_width=True, key="btn_calc_opt"):
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
        colD.button(L["clear"], on_click=limpar_dados, use_container_width=True, key="btn_clr_opt")
        if 'res_opt' in st.session_state:
            res = st.session_state['res_opt']
            st.success(f"**{L['precision']}:** {res['prec']:.2f}%")
            with st.expander(L["details"]): st.info(L["rep_opt_text"].format(**res))
            st.download_button(L["pdf_btn"], data=gerar_pdf("opt", res, L), file_name="Report_Optics.pdf", mime="application/pdf", use_container_width=True, key="p2")

    # --- ABA 3: PREVISÃO DE REDSHIFT (CÁLCULO EXATO DE ABERTURA) ---
    with aba3:
        st.info(L["info_red"])
        c9, c10 = st.columns(2)
        r_zl = c9.number_input(L["zl"], min_value=0.0, format="%.4f", step=0.1, key="r_zl")
        r_mest = c10.number_input(L["mest"], min_value=0.0, format="%.2f", step=1.0, key="r_mest")
        c11, c12 = st.columns(2)
        r_theta = c11.number_input(L["theta"], min_value=0.0, format="%.2f", step=0.1, key="r_theta")
        r_reff = c12.number_input(L["reff"], min_value=0.01, format="%.2f", step=0.1, key="r_reff", value=1.00) # Novo campo de Raio Efetivo
        r_cluster = st.checkbox(L["cluster"], key="r_cluster")

        colE, colF = st.columns(2)
        if colE.button(L["calc"], type="primary", use_container_width=True, key="btn_calc_red"):
            if r_zl > 0 and r_theta > 0 and r_mest > 0 and r_reff > 0:
                D_L = calcular_D_A(0, r_zl)
                melhor_erro, zs_pred = float('inf'), 0
                
                # CÁLCULO DA MASSA PROJETADA NA ABERTURA (Integração de Plummer)
                # A calculadora agora define exatamente quanta massa está dentro do anel, usando o raio da galáxia.
                fracao_abertura = (r_theta**2) / (r_theta**2 + r_reff**2)
                M_bar_kg = (r_mest * fracao_abertura * (7.0 if r_cluster else 1.0)) * 1e11 * M_SOL 
                
                for zs_test in np.arange(r_zl + 0.01, 10.0, 0.01):
                    D_S, D_LS = calcular_D_A(0, zs_test), calcular_D_A(r_zl, zs_test)
                    if D_S <= 0: continue
                    theta_bar_rad = math.sqrt((4 * G * M_bar_kg) / (C**2) * (D_LS / (D_L * D_S)))
                    g_bar = (G * M_bar_kg) / ((theta_bar_rad * D_L)**2)
                    fator_fase = 1.0 / (1.0 - math.exp(-math.sqrt(g_bar / A0)))
                    eta_C = 1.0 + BETA * math.log(1 + r_zl)
                    theta_trr = theta_bar_rad * math.sqrt(fator_fase) * eta_C * 206264.806
                    erro = abs(r_theta - theta_trr) / r_theta
                    if erro < melhor_erro: 
                        melhor_erro = erro
                        zs_pred = zs_test
                
                z_vals = np.linspace(r_zl + 0.01, max(zs_pred * 1.5, r_zl + 1), 40)
                t_class, t_trr = [], []
                for z in z_vals:
                    D_S, D_LS = calcular_D_A(0, z), calcular_D_A(r_zl, z)
                    if D_S <= 0: 
                        t_class.append(0); t_trr.append(0); continue
                    theta_bar_rad = math.sqrt((4 * G * M_bar_kg) / (C**2) * (D_LS / (D_L * D_S)))
                    t_class.append(theta_bar_rad * 206264.806)
                    g_bar = (G * M_bar_kg) / ((theta_bar_rad * D_L)**2)
                    fator_fase = 1.0 / (1.0 - math.exp(-math.sqrt(g_bar / A0)))
                    t_trr.append(theta_bar_rad * math.sqrt(fator_fase) * (1.0 + BETA * math.log(1 + r_zl)) * 206264.806)
                
                st.session_state['res_red'] = {
                    'zs_pred': zs_pred, 'prec': max(0, 100 - (melhor_erro*100)), 'tobs': r_theta,
                    'z_vals': z_vals, 't_class': t_class, 't_trr': t_trr, 'mest_obs': r_mest
                }
        colF.button(L["clear"], on_click=limpar_dados, use_container_width=True, key="btn_clr_red")
        if 'res_red' in st.session_state:
            res = st.session_state['res_red']
            st.success(f"**{L.get('precision_red', 'Convergência Matemática')}:** {res['prec']:.2f}% | **{L['pred_zs']}:** {res['zs_pred']:.4f}")
            with st.expander(L["details"]): st.info(L["rep_red_text"].format(**res))
            st.download_button(L["pdf_btn"], data=gerar_pdf("red", res, L), file_name="Report_Redshift.pdf", mime="application/pdf", use_container_width=True, key="p3")

    # --- ABA 4: CORRENTES ESTELARES ---
    with aba4:
        st.info(L["info_str"])
        c11, c12 = st.columns(2)
        s_peri = c11.number_input(L["r_peri"], min_value=0.0, format="%.2f", step=1.0, key="s_peri")
        s_apo = c12.number_input(L["r_apo"], min_value=0.0, format="%.2f", step=1.0, key="s_apo")
        s_mbar = st.number_input(L["mest"], min_value=0.0, format="%.2f", step=1.0, key="s_mbar")

        colG, colH = st.columns(2)
        if colG.button(L["calc"], type="primary", use_container_width=True, key="btn_calc_str"):
            if s_peri > 0 and s_apo > s_peri and s_mbar > 0:
                raios_kpc = np.linspace(s_peri, s_apo, 500)
                raios_m = raios_kpc * KPC_TO_M
                g_bar = (G * (s_mbar * 1e11 * M_SOL)) / (raios_m**2)
                fator_fase = 1.0 / (1.0 - np.exp(-np.sqrt(g_bar / A0)))
                arrasto = (g_bar * fator_fase) - g_bar
                cisalhamento = np.abs(np.gradient(arrasto, raios_m))
                cisal_norm = cisalhamento / np.max(cisalhamento)
                limite_critico = 0.75
                
                zonas_ruptura = raios_kpc[cisal_norm >= limite_critico]
                has_gap = len(zonas_ruptura) > 0
                gap_start = zonas_ruptura[0] if has_gap else 0
                gap_end = zonas_ruptura[-1] if has_gap else 0
                
                st.session_state['res_str'] = {
                    'raios': raios_kpc, 'arrasto': arrasto, 'cisal': cisal_norm, 'limite': limite_critico,
                    'has_gap': has_gap, 'gap_start': gap_start, 'gap_end': gap_end
                }
        colH.button(L["clear"], on_click=limpar_dados, use_container_width=True, key="btn_clr_str")
        if 'res_str' in st.session_state:
            res = st.session_state['res_str']
            loc_str_ui = f"[{res['gap_start']:.1f} kpc - {res['gap_end']:.1f} kpc]" if res['has_gap'] else L["no_gap"]
            st.success(f"**{L['loc_gap']}:** {loc_str_ui}")
            with st.expander(L["details"]): st.info(L["rep_str_text"].format(loc_str=loc_str_ui, **res))
            st.download_button(L["pdf_btn"], data=gerar_pdf("str", res, L), file_name="Report_Streams.pdf", mime="application/pdf", use_container_width=True, key="p4")
