import streamlit as st
import math

# --- CONSTANTES DA TEORIA ---
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

# --- DICIONÁRIO DE IDIOMAS ---
LANG = {
    "PT": {"title": "🌌 Motor Cosmológico TRR", "rad": "Raio observado (kpc)", "vobs": "Velocidade Obs (km/s)", "vgas": "Velocidade Gás (km/s)", "vdisk": "Veloc. Disco (km/s)", "vbulge": "Veloc. Haste/Bojo (km/s)", "calc": "Processar TRR (Dinâmica)", "zl": "Redshift Lente (z_L)", "zs": "Redshift Fonte (z_S)", "mest": "Massa Estelar (10^11 M_sol)", "theta": "Anel Einstein (arcsec)", "calc_opt": "Processar TRR (Óptica)"},
    "EN": {"title": "🌌 TRR Cosmological Engine", "rad": "Observed Radius (kpc)", "vobs": "Obs Velocity (km/s)", "vgas": "Gas Velocity (km/s)", "vdisk": "Disk Velocity (km/s)", "vbulge": "Bar/Bulge Vel. (km/s)", "calc": "Process TRR (Dynamics)", "zl": "Lens Redshift (z_L)", "zs": "Source Redshift (z_S)", "mest": "Stellar Mass (10^11 M_sol)", "theta": "Einstein Ring (arcsec)", "calc_opt": "Process TRR (Optics)"},
    "ES": {"title": "🌌 Motor Cosmológico TRR", "rad": "Radio observado (kpc)", "vobs": "Velocidad Obs (km/s)", "vgas": "Velocidad Gas (km/s)", "vdisk": "Veloc. Disco (km/s)", "vbulge": "Veloc. Barra (km/s)", "calc": "Procesar TRR (Dinámica)", "zl": "Redshift Lente (z_L)", "zs": "Redshift Fuente (z_S)", "mest": "Masa Estelar (10^11 M_sol)", "theta": "Anillo Einstein (arcsec)", "calc_opt": "Procesar TRR (Óptica)"},
    "FR": {"title": "🌌 Moteur Cosmologique TRR", "rad": "Rayon observé (kpc)", "vobs": "Vitesse Obs (km/s)", "vgas": "Vitesse Gaz (km/s)", "vdisk": "Vitesse Disque (km/s)", "vbulge": "Vit. Bulbe/Barre (km/s)", "calc": "Traiter TRR (Dynamique)", "zl": "Redshift Lentille (z_L)", "zs": "Redshift Source (z_S)", "mest": "Masse Stellaire (10^11)", "theta": "Anneau d'Einstein", "calc_opt": "Traiter TRR (Optique)"},
    "DE": {"title": "🌌 TRR Kosmologischer Motor", "rad": "Beobachteter Radius (kpc)", "vobs": "Beob Geschw. (km/s)", "vgas": "Gas Geschw. (km/s)", "vdisk": "Scheiben Geschw. (km/s)", "vbulge": "Balken Geschw. (km/s)", "calc": "TRR Verarbeiten (Dynamik)", "zl": "Linsen-Rotverschiebung (z_L)", "zs": "Quellen-Rotverschiebung (z_S)", "mest": "Stellare Masse (10^11)", "theta": "Einsteinring (arcsec)", "calc_opt": "TRR Verarbeiten (Optik)"},
    "IT": {"title": "🌌 Motore Cosmologico TRR", "rad": "Raggio osservato (kpc)", "vobs": "Velocità Oss (km/s)", "vgas": "Velocità Gas (km/s)", "vdisk": "Veloc. Disco (km/s)", "vbulge": "Veloc. Barra (km/s)", "calc": "Elabora TRR (Dinamica)", "zl": "Redshift Lente (z_L)", "zs": "Redshift Sorgente (z_S)", "mest": "Massa Stellare (10^11)", "theta": "Anello di Einstein", "calc_opt": "Elabora TRR (Ottica)"},
    "ZH": {"title": "🌌 TRR 宇宙引擎", "rad": "观测半径 (kpc)", "vobs": "观测速度 (km/s)", "vgas": "气体速度 (km/s)", "vdisk": "星盘速度 (km/s)", "vbulge": "棒状速度 (km/s)", "calc": "运行 TRR (动力学)", "zl": "透镜红移 (z_L)", "zs": "光源红移 (z_S)", "mest": "恒星质量 (10^11)", "theta": "爱因斯坦环 (arcsec)", "calc_opt": "运行 TRR (光学)"},
    "RU": {"title": "🌌 Двигатель TRR", "rad": "Набл. радиус (кпк)", "vobs": "Набл. скорость (км/с)", "vgas": "Скор. газа (км/с)", "vdisk": "Скор. диска (км/с)", "vbulge": "Скор. бара (км/с)", "calc": "Анализ TRR (Динамика)", "zl": "Красн. смещение линзы (z_L)", "zs": "Красн. смещение ист. (z_S)", "mest": "Звездная масса (10^11)", "theta": "Кольцо Эйнштейна", "calc_opt": "Анализ TRR (Оптика)"}
}

st.set_page_config(page_title="Motor TRR", layout="centered", initial_sidebar_state="expanded")

# --- BARRA LATERAL (IDIOMAS) ---
with st.sidebar:
    idioma_escolhido = st.selectbox(
        "🌎 Language / Idioma", 
        ["PT", "EN", "ES", "FR", "DE", "IT", "ZH", "RU"]
    )
    L = LANG[idioma_escolhido]
    st.markdown("---")
    st.markdown("**Autor:** Jean Cortez\n\n*Teoria da Relatividade Referencial*")

st.title(L["title"])

aba1, aba2 = st.tabs(["📊 " + L["calc"].split(" (")[1].replace(")",""), "👁️ " + L["calc_opt"].split(" (")[1].replace(")","")])

# === ABA 1: DINÂMICA ===
with aba1:
    c1, c2 = st.columns(2)
    rad = c1.number_input(L["rad"], min_value=0.0, format="%.2f", step=1.0)
    v_obs = c2.number_input(L["vobs"], min_value=0.0, format="%.2f", step=10.0)
    
    c3, c4 = st.columns(2)
    v_gas = c3.number_input(L["vgas"], format="%.2f", step=5.0)
    v_disk = c4.number_input(L["vdisk"], min_value=0.0, format="%.2f", step=10.0)
    v_bulge = st.number_input(L["vbulge"], min_value=0.0, format="%.2f", step=10.0)

    if st.button(L["calc"], type="primary"):
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
            
            precisao = max(0, 100 - (melhor_erro*100))
            st.success(f"**Precisão / Accuracy:** {precisao:.2f}%")
            st.info(f"**V_TRR:** {melhor_v_trr:.2f} km/s (Obs: {v_obs:.2f} km/s)\n\n**M/L Disk:** {melhor_ml:.2f} | **M/L Bulge:** {melhor_ml + 0.2:.2f}")

# === ABA 2: ÓPTICA ===
with aba2:
    c5, c6 = st.columns(2)
    zl = c5.number_input(L["zl"], min_value=0.0, format="%.4f", step=0.1)
    zs = c6.number_input(L["zs"], min_value=0.0, format="%.4f", step=0.1)
    
    c7, c8 = st.columns(2)
    mest = c7.number_input(L["mest"], min_value=0.0, format="%.2f", step=1.0)
    theta = c8.number_input(L["theta"], min_value=0.0, format="%.2f", step=0.1)
    is_cluster = st.checkbox("Giant Cluster / Aglomerado?")

    if st.button(L["calc_opt"], type="primary"):
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

            precisao = max(0, 100 - (melhor_erro*100))
            st.success(f"**Precisão / Accuracy:** {precisao:.2f}%")
            st.info(f"**Theta_TRR:** {melhor_theta_trr:.2f} arcsec (Obs: {theta:.2f})\n\n**M/L Optimized:** {melhor_fator:.2f}\n\n**Refraction Index (Cortez):** {1.0 + BETA * math.log(1 + zl):.5f}")