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
# DICIONÁRIO ABSOLUTO (8 IDIOMAS)
# ==========================================
LANG = {
    "PT": {
        "code": "PT", "welcome": "Selecione o seu idioma",
        "title": "🌌 Motor Cosmológico TRR", "author_prefix": "Autor", "theory_name": "Teoria da Relatividade Referencial",
        "tab1": "📊 Dinâmica Galáctica", "tab2": "👁️ Óptica Cosmológica", "tab3": "🔭 Previsão de Redshift", "tab4": "☄️ Correntes Estelares",
        "prov_title": "🗂️ Proveniência de Dados", 
        "prov_info": "Para garantir a reprodutibilidade, este motor processa dados brutos de:",
        "prov_warn": "⚠️ Nenhum parâmetro ad-hoc de matéria escura é injetado aqui.",
        "cat_list": "* SDSS DR16Q\n* SPARC (CWRU)\n* SLACS Survey\n* ESA Gaia\n* JWST/MAST\n* LIGO/Virgo",
        "rad": "Raio observado (kpc)", "vobs": "Veloc. Telescópio (km/s)", "vgas": "Velocidade Gás (km/s)", "vdisk": "Veloc. Disco (km/s)", "vbulge": "Veloc. Bojo (km/s)",
        "zl": "Redshift Lente (z_L)", "zs": "Redshift Fonte (z_S)", "mest": "Massa Fotométrica Total (10^11)", "theta": "Anel Einstein (arcsec)", "cluster": "Aglomerado Gigante?",
        "r_peri": "Pericentro da Corrente (kpc)", "r_apo": "Apocentro da Corrente (kpc)",
        "calc": "🚀 Processar Auditoria TRR", "clear": "🧹 Limpar Tudo",
        "pdf_btn": "📄 Baixar Relatório de Auditoria (PDF)", "details": "📚 Ver Parecer Técnico",
        "precision": "Precisão Empírica", "precision_red": "Convergência Matemática", "g_bar": "Física Clássica", "g_trr": "Previsão TRR", "g_obs": "Telescópio",
        "info_dyn": "💡 A TRR calcula o atrito topológico do vácuo para prever a velocidade de rotação sem Matéria Escura.",
        "info_opt": "💡 A TRR aplica o Índice de Refração Temporal (eta_C) para amplificar o desvio gravitacional.",
        "info_red": "💡 A TRR itera a matriz usando a Massa Bariônica Total para prever o tempo-espaço da Fonte (z_S).",
        "info_str": "💡 A TRR mapeia o cisalhamento viscoso do vácuo, revelando a coordenada real da ruptura.",
        "pred_zs": "Redshift z_S Previsto", "loc_gap": "📌 Ruptura nas coordenadas", "no_gap": "Nenhuma ruptura crítica",
        "pdf_h1": "TEORIA DA RELATIVIDADE REFERENCIAL (TRR)", "pdf_h2": "Relatorio de Auditoria Automatizada", "pdf_footer": "Documento gerado pelo Motor Cosmologico TRR.",
        "pdf_title_dyn": "AUDITORIA CIENTIFICA - DINAMICA", "pdf_title_opt": "AUDITORIA CIENTIFICA - OPTICA", "pdf_title_red": "AUDITORIA CIENTIFICA - REDSHIFT", "pdf_title_str": "AUDITORIA CIENTIFICA - CORRENTES",
        "rep_dyn_text": "LAUDO TÉCNICO:\n1. A massa bariônica pura gera {vbar:.2f} km/s.\n2. A TRR calcula o atrito topológico (Beta=0.028006). RESULTADO: Precisão de {prec:.2f}% sem Matéria Escura.",
        "rep_opt_text": "LAUDO TÉCNICO:\nA massa visível desvia a luz em {tbar:.2f} arcsec. A TRR aplica a Refração Temporal (eta_C = {etac:.5f}), demonstrando convergência teórica para o anel de {tobs:.2f} arcsec. Precisão: {prec:.2f}%.",
        "rep_red_text": "LAUDO PREDITIVO (AUDITORIA CEGA):\n1. A TRR travou a massa total como limite fluídico.\n2. O algoritmo prediz que a galáxia fonte está em z_S = {zs_pred:.4f}.\nRESULTADO: Convergência pura isolada da Matéria Escura.",
        "rep_str_text": "LAUDO DE HIDRODINÂMICA:\nO Cisalhamento Viscoso atingiu o limite crítico de ruptura na zona de {loc_str}. O gap é um efeito de atrito com o fluido do espaço (Phase 3)."
    },
    "EN": {
        "code": "EN", "welcome": "Select Language",
        "title": "🌌 RRT Cosmological Engine", "author_prefix": "Author", "theory_name": "Referential Relativity Theory",
        "tab1": "📊 Galactic Dynamics", "tab2": "👁️ Cosmological Optics", "tab3": "🔭 Redshift Prediction", "tab4": "☄️ Stellar Streams",
        "prov_title": "🗂️ Data Provenance", 
        "prov_info": "To ensure reproducibility, this engine processes raw data from:",
        "prov_warn": "⚠️ No ad-hoc dark matter parameters are injected here.",
        "cat_list": "* SDSS DR16Q\n* SPARC (CWRU)\n* SLACS Survey\n* ESA Gaia\n* JWST/MAST\n* LIGO/Virgo",
        "rad": "Obs. Radius (kpc)", "vobs": "Telescope Vel. (km/s)", "vgas": "Gas Vel. (km/s)", "vdisk": "Disk Vel. (km/s)", "vbulge": "Bulge Vel. (km/s)",
        "zl": "Lens Redshift (z_L)", "zs": "Source Redshift (z_S)", "mest": "Total Photometric Mass (10^11)", "theta": "Einstein Ring (arcsec)", "cluster": "Giant Cluster?",
        "r_peri": "Stream Pericenter (kpc)", "r_apo": "Stream Apocenter (kpc)",
        "calc": "🚀 Process RRT Audit", "clear": "🧹 Clear All",
        "pdf_btn": "📄 Download Report (PDF)", "details": "📚 View Technical Report",
        "precision": "Empirical Accuracy", "precision_red": "Math Convergence", "g_bar": "Classical Physics", "g_trr": "RRT Prediction", "g_obs": "Telescope",
        "info_dyn": "💡 RRT calculates topological vacuum friction to predict rotation velocity without Dark Matter.",
        "info_opt": "💡 RRT applies Time Refraction (eta_C) to amplify gravitational deflection using visible mass only.",
        "info_red": "💡 RRT iterates using Total Baryonic Mass to predict the Source space-time (z_S).",
        "info_str": "💡 RRT maps vacuum viscous shear, revealing the real coordinates of structural gaps.",
        "pred_zs": "Predicted Redshift z_S", "loc_gap": "📌 Rupture Coordinates", "no_gap": "No critical rupture",
        "pdf_h1": "REFERENTIAL RELATIVITY THEORY (RRT)", "pdf_h2": "Automated Audit Report", "pdf_footer": "Document generated by RRT Cosmological Engine.",
        "pdf_title_dyn": "SCIENTIFIC AUDIT - DYNAMICS", "pdf_title_opt": "SCIENTIFIC AUDIT - OPTICS", "pdf_title_red": "SCIENTIFIC AUDIT - REDSHIFT", "pdf_title_str": "SCIENTIFIC AUDIT - STREAMS",
        "rep_dyn_text": "TECHNICAL REPORT:\n1. Baryonic mass yields {vbar:.2f} km/s. 2. RRT fluid drag (Beta=0.028006) elevates velocity to {vtrr:.2f} km/s.\nRESULT: {prec:.2f}% accuracy achieved without Dark Matter.",
        "rep_opt_text": "TECHNICAL REPORT:\nVisible mass deflects at {tbar:.2f} arcsec. RRT applies Time Refraction (eta_C = {etac:.5f}), providing theoretical convergence for {tobs:.2f} arcsec. Accuracy: {prec:.2f}%.",
        "rep_red_text": "PREDICTIVE REPORT (STRICT BLIND AUDIT):\n1. RRT locked total mass as the spatial fluid limit. 2. Predicts source galaxy at z_S = {zs_pred:.4f}.\nRESULT: Pure algorithmic convergence.",
        "rep_str_text": "HYDRODYNAMICS REPORT:\nViscous Shear hit critical rupture limits at {loc_str}. Structural gaps are deterministic vacuum friction effects."
    },
    "ES": {
        "code": "ES", "welcome": "Seleccione su idioma",
        "title": "🌌 Motor Cosmológico TRR", "author_prefix": "Autor", "theory_name": "Teoría de la Relatividad Referencial",
        "tab1": "📊 Dinámica Galáctica", "tab2": "👁️ Óptica Cosmológica", "tab3": "🔭 Predicción de Redshift", "tab4": "☄️ Corrientes Estelares",
        "prov_title": "🗂️ Procedencia de Datos", 
        "prov_info": "Para garantizar la reproducibilidad, este motor procesa datos brutos de:",
        "prov_warn": "⚠️ Aquí no se inyectan parámetros ad-hoc de materia oscura.",
        "cat_list": "* SDSS DR16Q\n* SPARC (CWRU)\n* SLACS Survey\n* ESA Gaia\n* JWST/MAST\n* LIGO/Virgo",
        "rad": "Radio observado (kpc)", "vobs": "Velocidad Telescopio", "vgas": "Velocidad Gas", "vdisk": "Veloc. Disco", "vbulge": "Veloc. Bulbo",
        "zl": "Redshift Lente (z_L)", "zs": "Redshift Fuente (z_S)", "mest": "Masa Fotométrica (10^11)", "theta": "Anillo Einstein (arcsec)", "cluster": "¿Cúmulo Gigante?",
        "r_peri": "Pericentro (kpc)", "r_apo": "Apocentro (kpc)",
        "calc": "🚀 Procesar Auditoría TRR", "clear": "🧹 Limpiar Todo",
        "pdf_btn": "📄 Descargar Reporte (PDF)", "details": "📚 Ver Informe Técnico",
        "precision": "Precisión Empírica", "precision_red": "Convergencia Matemática", "g_bar": "Física Clásica", "g_trr": "Predicción TRR", "g_obs": "Telescopio",
        "info_dyn": "💡 La TRR calcula la fricción topológica del vacío para predecir la rotación sin Materia Oscura.",
        "info_opt": "💡 La TRR aplica el Índice de Refracción Temporal para amplificar el desvío gravitacional.",
        "info_red": "💡 La TRR itera la masa bariónica total para predecir el espacio-tiempo de la fuente.",
        "info_str": "💡 La TRR mapea la cizalladura viscosa del vacío, revelando las coordenadas de ruptura.",
        "pred_zs": "Redshift z_S Previsto", "loc_gap": "📌 Ruptura en coordenadas", "no_gap": "Sin ruptura crítica",
        "pdf_h1": "TEORIA DE LA RELATIVIDAD REFERENCIAL", "pdf_h2": "Reporte de Auditoria", "pdf_footer": "Generado por Motor Cosmologico TRR.",
        "pdf_title_dyn": "AUDITORIA - DINAMICA", "pdf_title_opt": "AUDITORIA - OPTICA", "pdf_title_red": "AUDITORIA - REDSHIFT", "pdf_title_str": "AUDITORIA - CORRIENTES",
        "rep_dyn_text": "REPORTE TÉCNICO:\n1. Masa bariónica genera {vbar:.2f} km/s. 2. TRR (Beta=0.028) eleva a {vtrr:.2f} km/s.\nRESULTADO: Precisión {prec:.2f}% sin Materia Oscura.",
        "rep_opt_text": "REPORTE TÉCNICO:\nMasa visible desvía {tbar:.2f} arcsec. TRR aplica Refracción Temporal (eta_C = {etac:.5f}), logrando {tobs:.2f} arcsec. Precisión: {prec:.2f}%.",
        "rep_red_text": "REPORTE PREDITIVO:\n1. TRR usó masa total como límite fluido. 2. Predice galaxia en z_S = {zs_pred:.4f}.\nRESULTADO: Convergencia pura.",
        "rep_str_text": "REPORTE HIDRODINÁMICO:\nCizalladura Viscosa alcanzó límite de ruptura en {loc_str}."
    },
    "FR": {
        "code": "FR", "welcome": "Sélectionnez votre langue",
        "title": "🌌 Moteur Cosmologique TRR", "author_prefix": "Auteur", "theory_name": "Théorie de la Relativité Référentielle",
        "tab1": "📊 Dynamique Galactique", "tab2": "👁️ Optique Cosmologique", "tab3": "🔭 Prédiction Redshift", "tab4": "☄️ Courants Stellaires",
        "prov_title": "🗂️ Provenance des Données", 
        "prov_info": "Pour garantir la reproductibilité, ce moteur traite les données brutes de:",
        "prov_warn": "⚠️ Aucun paramètre ad-hoc de matière noire n'est injecté ici.",
        "cat_list": "* SDSS DR16Q\n* SPARC (CWRU)\n* SLACS Survey\n* ESA Gaia\n* JWST/MAST\n* LIGO/Virgo",
        "rad": "Rayon (kpc)", "vobs": "Vitesse Télescope", "vgas": "Vitesse Gaz", "vdisk": "Vitesse Disque", "vbulge": "Vitesse Bulbe",
        "zl": "Redshift Lentille", "zs": "Redshift Source", "mest": "Masse Photométrique", "theta": "Anneau Einstein", "cluster": "Amas Géant?",
        "r_peri": "Péricentre (kpc)", "r_apo": "Apocentre (kpc)",
        "calc": "🚀 Lancer l'Audit TRR", "clear": "🧹 Tout Effacer",
        "pdf_btn": "📄 Télécharger le Rapport (PDF)", "details": "📚 Voir le Rapport Technique",
        "precision": "Précision Empirique", "precision_red": "Convergence Mathématique", "g_bar": "Physique Classique", "g_trr": "Prédiction TRR", "g_obs": "Télescope",
        "info_dyn": "💡 La TRR calcule le frottement topologique du vide sans matière noire.",
        "info_opt": "💡 La TRR applique l'Indice de Réfraction Temporelle pour amplifier la déviation.",
        "info_red": "💡 La TRR itère la masse baryonique totale pour prédire l'espace-temps de la source.",
        "info_str": "💡 La TRR cartographie le cisaillement visqueux du vide.",
        "pred_zs": "Redshift z_S Prédit", "loc_gap": "📌 Rupture aux coordonnées", "no_gap": "Aucune rupture critique",
        "pdf_h1": "THEORIE DE LA RELATIVITE REFERENTIELLE", "pdf_h2": "Rapport d'Audit", "pdf_footer": "Genere par le Moteur TRR.",
        "pdf_title_dyn": "AUDIT - DYNAMIQUE", "pdf_title_opt": "AUDIT - OPTIQUE", "pdf_title_red": "AUDIT - REDSHIFT", "pdf_title_str": "AUDIT - COURANTS",
        "rep_dyn_text": "RAPPORT TECHNIQUE:\n1. Masse génère {vbar:.2f} km/s. 2. TRR élève à {vtrr:.2f} km/s.\nRESULTAT: Précision {prec:.2f}%.",
        "rep_opt_text": "RAPPORT TECHNIQUE:\nDéviation visible {tbar:.2f}. TRR applique Réfraction (eta_C = {etac:.5f}), atteignant {tobs:.2f}. Précision: {prec:.2f}%.",
        "rep_red_text": "RAPPORT PREDITIF:\nPrédiction galaxie à z_S = {zs_pred:.4f}.",
        "rep_str_text": "RAPPORT:\nCisaillement visqueux a atteint la limite à {loc_str}."
    },
    "DE": {
        "code": "DE", "welcome": "Wählen Sie Ihre Sprache",
        "title": "🌌 RRT Kosmologische Engine", "author_prefix": "Autor", "theory_name": "Referenzielle Relativitätstheorie",
        "tab1": "📊 Galaktische Dynamik", "tab2": "👁️ Kosmologische Optik", "tab3": "🔭 Redshift-Vorhersage", "tab4": "☄️ Sternströme",
        "prov_title": "🗂️ Datenherkunft", 
        "prov_info": "Um die Reproduzierbarkeit zu gewährleisten, verarbeitet diese Engine Rohdaten von:",
        "prov_warn": "⚠️ Hier werden keine Ad-hoc-Parameter für dunkle Materie injiziert.",
        "cat_list": "* SDSS DR16Q\n* SPARC (CWRU)\n* SLACS Survey\n* ESA Gaia\n* JWST/MAST\n* LIGO/Virgo",
        "rad": "Radius (kpc)", "vobs": "Teleskopgeschw.", "vgas": "Gasgeschw.", "vdisk": "Scheibengeschw.", "vbulge": "Bulge-Geschw.",
        "zl": "Redshift Linse", "zs": "Redshift Quelle", "mest": "Photometrische Masse", "theta": "Einsteinring", "cluster": "Riesencluster?",
        "r_peri": "Perizentrum (kpc)", "r_apo": "Apozentrum (kpc)",
        "calc": "🚀 RRT-Audit starten", "clear": "🧹 Alles löschen",
        "pdf_btn": "📄 Bericht herunterladen (PDF)", "details": "📚 Technischen Bericht anzeigen",
        "precision": "Empirische Genauigkeit", "precision_red": "Mathematische Konvergenz", "g_bar": "Klassische Physik", "g_trr": "RRT Vorhersage", "g_obs": "Teleskop",
        "info_dyn": "💡 RRT berechnet topologische Vakuumreibung ohne Dunkle Materie.",
        "info_opt": "💡 RRT wendet den zeitlichen Brechungsindex an.",
        "info_red": "💡 RRT verwendet die totale baryonische Masse, um z_S vorherzusagen.",
        "info_str": "💡 RRT kartiert die viskose Scherung des Vakuums.",
        "pred_zs": "Vorhergesagter z_S", "loc_gap": "📌 Bruchkoordinaten", "no_gap": "Kein kritischer Bruch",
        "pdf_h1": "REFERENZIELLE RELATIVITÄTSTHEORIE", "pdf_h2": "Audit-Bericht", "pdf_footer": "Generiert von RRT Engine.",
        "pdf_title_dyn": "AUDIT - DYNAMIK", "pdf_title_opt": "AUDIT - OPTIK", "pdf_title_red": "AUDIT - REDSHIFT", "pdf_title_str": "AUDIT - STROEME",
        "rep_dyn_text": "TECHNISCHER BERICHT:\n1. Baryonische Masse: {vbar:.2f} km/s. 2. RRT-Vorhersage: {vtrr:.2f} km/s.\nERGEBNIS: Genauigkeit {prec:.2f}%.",
        "rep_opt_text": "TECHNISCHER BERICHT:\nSichtbare Masse {tbar:.2f}. RRT erreicht {tobs:.2f}. Genauigkeit: {prec:.2f}%.",
        "rep_red_text": "VORHERSAGE:\nGalaxie bei z_S = {zs_pred:.4f}.",
        "rep_str_text": "BERICHT:\nViskose Scherung erreicht bei {loc_str}."
    },
    "JA": {
        "code": "JA", "welcome": "言語を選択してください",
        "title": "🌌 RRT 宇宙エンジン", "author_prefix": "著者", "theory_name": "参照相対性理論",
        "tab1": "📊 銀河動力学", "tab2": "👁️ 宇宙光学", "tab3": "🔭 赤方偏移予測", "tab4": "☄️ 恒星ストリーム",
        "prov_title": "🗂️ データソース", 
        "prov_info": "再現性を確保するため、このエンジンは以下の生データを処理します:",
        "prov_warn": "⚠️ 暗黒物質の場当たり的なパラメータはここに注入されていません。",
        "cat_list": "* SDSS DR16Q\n* SPARC (CWRU)\n* SLACS Survey\n* ESA Gaia\n* JWST/MAST\n* LIGO/Virgo",
        "rad": "半径 (kpc)", "vobs": "望遠鏡速度", "vgas": "ガス速度", "vdisk": "ディスク速度", "vbulge": "バルジ速度",
        "zl": "レンズ赤方偏移", "zs": "ソース赤方偏移", "mest": "測光質量", "theta": "アインシュタイン環", "cluster": "巨大クラスター？",
        "r_peri": "近点 (kpc)", "r_apo": "遠点 (kpc)",
        "calc": "🚀 RRT 監査を開始", "clear": "🧹 全てクリア",
        "pdf_btn": "📄 レポートをダウンロード (PDF - EN)", "details": "📚 技術レポートを見る",
        "precision": "経験的精度", "precision_red": "数学的収束", "g_bar": "古典物理学", "g_trr": "RRT 予測", "g_obs": "望遠鏡",
        "info_dyn": "💡 RRTは暗黒物質なしで真空の位相的摩擦を計算します。",
        "info_opt": "💡 RRTは時間的屈折率を適用します。",
        "info_red": "💡 RRTは総バリオン質量を使用してz_Sを予測します。",
        "info_str": "💡 RRTは真空の粘性せん断をマッピングします。",
        "pred_zs": "予測 z_S", "loc_gap": "📌 破壊座標", "no_gap": "臨界破壊なし",
        "pdf_h1": "REFERENTIAL RELATIVITY THEORY (RRT)", "pdf_h2": "Automated Audit Report", "pdf_footer": "Document generated by RRT Cosmological Engine."
    },
    "ZH": {
        "code": "ZH", "welcome": "请选择语言",
        "title": "🌌 RRT 宇宙引擎", "author_prefix": "作者", "theory_name": "参照相对论",
        "tab1": "📊 星系动力学", "tab2": "👁️ 宇宙光学", "tab3": "🔭 红移预测", "tab4": "☄️ 恒星流",
        "prov_title": "🗂️ 数据来源", 
        "prov_info": "为确保独立可重复性，本引擎处理以下原始数据：",
        "prov_warn": "⚠️ 本引擎未注入任何暗物质参数。",
        "cat_list": "* SDSS DR16Q\n* SPARC (CWRU)\n* SLACS Survey\n* ESA Gaia\n* JWST/MAST\n* LIGO/Virgo",
        "rad": "观测半径 (kpc)", "vobs": "望远镜速度 (km/s)", "vgas": "气体速度", "vdisk": "星盘速度", "vbulge": "核球速度",
        "zl": "透镜红移 (z_L)", "zs": "光源红移 (z_S)", "mest": "光度质量 (10^11)", "theta": "爱因斯坦环 (arcsec)", "cluster": "巨型星系团？",
        "r_peri": "流近星点 (kpc)", "r_apo": "流远星点 (kpc)",
        "calc": "🚀 运行 RRT 审计", "clear": "🧹 清除所有",
        "pdf_btn": "📄 下载审计报告 (PDF - EN)", "details": "📚 查看技术意见",
        "precision": "经验精度", "precision_red": "数学收敛", "g_bar": "经典物理", "g_trr": "RRT 预测", "g_obs": "望远镜",
        "info_dyn": "💡 RRT 计算真空拓扑摩擦，无需暗物质即可预测旋转速度。",
        "info_opt": "💡 RRT 应用时间折射率 (eta_C) 放大引力偏转。",
        "info_red": "💡 RRT 使用绝对总质量迭代引力矩阵来预测光源 (z_S)。",
        "info_str": "💡 RRT 映射真空粘性剪切，揭示结构断裂的真实坐标。",
        "pred_zs": "预测红移 z_S", "loc_gap": "📌 断裂坐标", "no_gap": "无关键断裂",
        "pdf_h1": "REFERENTIAL RELATIVITY THEORY (RRT)", "pdf_h2": "Automated Audit Report", "pdf_footer": "Document generated by RRT Cosmological Engine."
    },
    "RU": {
        "code": "RU", "welcome": "Выберите язык",
        "title": "🌌 Двигатель ТРО", "author_prefix": "Автор", "theory_name": "Теория Референциальной Относительности",
        "tab1": "📊 Динамика", "tab2": "👁️ Оптика", "tab3": "🔭 Прогноз Redshift", "tab4": "☄️ Потоки",
        "prov_title": "🗂️ Источники данных", 
        "prov_info": "Для обеспечения воспроизводимости этот двигатель обрабатывает данные из:",
        "prov_warn": "⚠️ В этот двигатель не вводятся параметры темной материи.",
        "cat_list": "* SDSS DR16Q\n* SPARC (CWRU)\n* SLACS Survey\n* ESA Gaia\n* JWST/MAST\n* LIGO/Virgo",
        "rad": "Радиус (кпк)", "vobs": "Скор. телескопа", "vgas": "Скор. газа", "vdisk": "Скор. диска", "vbulge": "Скор. бара",
        "zl": "Redshift линзы", "zs": "Redshift ист.", "mest": "Полная массa (10^11)", "theta": "Кольцо (arcsec)", "cluster": "Скопление?",
        "r_peri": "Перицентр (кпк)", "r_apo": "Апоцентр (кпк)",
        "calc": "🚀 Начать аудит ТРО", "clear": "🧹 Очистить",
        "pdf_btn": "📄 Скачать отчет (PDF - EN)", "details": "📚 Технический отчет",
        "precision": "Точность", "precision_red": "Сходимость", "g_bar": "Классика", "g_trr": "Прогноз ТРО", "g_obs": "Телескоп",
        "info_dyn": "💡 ТРО рассчитывает топологическое трение вакуума без темной материи.",
        "info_opt": "💡 ТРО применяет индекс временного преломления для усиления отклонения.",
        "info_red": "💡 ТРО использует полную массу для прогнозирования z_S источника.",
        "info_str": "💡 ТРО отображает вязкий сдвиг вакуума, выявляя координаты разрыва.",
        "pred_zs": "Прогноз z_S", "loc_gap": "📌 Координаты разрыва", "no_gap": "Нет разрыва",
        "pdf_h1": "REFERENTIAL RELATIVITY THEORY (RRT)", "pdf_h2": "Automated Audit Report", "pdf_footer": "Document generated by RRT Cosmological Engine."
    }
}

# ==========================================
# MOTORES GRÁFICOS
# ==========================================
def criar_grafico(val_bar, val_trr, val_obs, lbl_bar, lbl_trr, lbl_obs, is_dyn=True):
    fig, ax = plt.subplots(figsize=(7, 4))
    labels = [lbl_bar, lbl_trr, lbl_obs]
    valores = [val_bar, val_trr, val_obs]
    cores = ['#e74c3c', '#3498db', '#2ecc71'] 
    ax.bar(labels, valores, color=cores, width=0.6)
    ax.set_ylabel("Vel. (km/s)" if is_dyn else "Dev (arcsec)", fontweight='bold')
    plt.tight_layout()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.savefig(tmp.name, dpi=150)
        plt.close(fig)
        return tmp.name

def criar_grafico_redshift(z_vals, theta_class, theta_trr, zs_pred, theta_obs):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(z_vals, theta_class, color='#e74c3c', linestyle='--', label="Classical")
    ax.plot(z_vals, theta_trr, color='#3498db', label="RRT Prediction")
    ax.axhline(y=theta_obs, color='#2ecc71', label=f"Obs ({theta_obs}\")")
    ax.scatter([zs_pred], [theta_obs], color='#f1c40f', s=100, zorder=5)
    ax.set_xlabel("Source Redshift (z_S)"); ax.set_ylabel("Einstein Ring (arcsec)")
    ax.legend(); plt.tight_layout()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.savefig(tmp.name, dpi=150)
        plt.close(fig)
        return tmp.name

def criar_grafico_stream(raios, arrasto, cisalhamento, limite):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    ax1.plot(raios, arrasto, color='#2980b9', label="Viscous Drag")
    ax2.plot(raios, cisalhamento, color='#8e44ad', label="Viscous Shear")
    ax2.axhline(y=limite, color='#e74c3c', linestyle='--')
    ax2.fill_between(raios, cisalhamento, limite, where=(cisalhamento >= limite), color='#e74c3c', alpha=0.4)
    plt.tight_layout()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.savefig(tmp.name, dpi=150)
        plt.close(fig)
        return tmp.name

# ==========================================
# GERADOR DE PDF (HYBRID LOGIC: EN for RU/ZH/JA)
# ==========================================
def gerar_pdf(modulo, dict_dados, L_original):
    # Regra de Segurança: Idiomas com fontes não-latinas geram PDF em Inglês
    if L_original["code"] in ["ZH", "RU", "JA"]:
        L_pdf = LANG["EN"]
    else:
        L_pdf = L_original
        
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=L_pdf["pdf_h1"].encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, txt=L_pdf["pdf_h2"].encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    pdf.line(10, 28, 200, 28); pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    titulos = {"dyn": L_pdf["pdf_title_dyn"], "opt": L_pdf["pdf_title_opt"], "red": L_pdf["pdf_title_red"], "str": L_pdf["pdf_title_str"]}
    pdf.cell(0, 10, txt=titulos[modulo].encode('latin-1', 'replace').decode('latin-1'), ln=True); pdf.ln(5)
    pdf.set_font("Arial", size=11)
    
    if modulo == "dyn":
        texto = L_pdf["rep_dyn_text"].format(**dict_dados)
        img = criar_grafico(dict_dados['vbar'], dict_dados['vtrr'], dict_dados['vobs'], L_pdf["g_bar"], L_pdf["g_trr"], L_pdf["g_
