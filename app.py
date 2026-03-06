import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
from datetime import datetime

# ─── AI CONFIGURATION ───────────────────────────────────────────────────────
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = 'gemini-2.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SarSa AI | Real Estate Intelligence Platform",
    page_icon="🏢",
    layout="wide"
)

@st.cache_data
def load_logo(file_path):
    if os.path.exists(file_path):
        return Image.open(file_path)
    return None

# ─── LANGUAGE SYSTEM ────────────────────────────────────────────────────────
ui_languages = {
    "English": {
        "title": "SarSa AI | Real Estate Intelligence Platform",
        "service_desc": "All-in-One Visual Property Intelligence & Global Sales Automation",
        "subtitle": "Transform property photos into premium listings, social media kits, cinematic video scripts, technical specs, email campaigns and SEO copy — instantly.",
        "settings": "Configuration",
        "target_lang": "Write Listing In...",
        "prop_type": "Property Type",
        "price": "Market Price",
        "location": "Location",
        "tone": "Marketing Strategy",
        "tones": ["Standard Pro", "Ultra-Luxury", "Investment Focus", "Modern Minimalist", "Family Living", "Vacation Rental", "Commercial"],
        "ph_prop": "E.g., 3+1 Apartment, Luxury Villa...",
        "ph_price": "E.g., $850,000 or £2,000/mo...",
        "ph_loc": "E.g., Manhattan, NY or Dubai Marina...",
        "bedrooms": "Bedrooms",
        "bathrooms": "Bathrooms",
        "area": "Area",
        "year_built": "Year Built",
        "ph_beds": "E.g., 3",
        "ph_baths": "E.g., 2",
        "ph_area": "E.g., 185 sqm",
        "ph_year": "E.g., 2022",
        "furnishing": "Furnishing",
        "furnishing_opts": ["Not Specified", "Fully Furnished", "Semi-Furnished", "Unfurnished"],
        "target_audience": "Target Audience",
        "audience_opts": ["General Market", "Luxury Buyers", "Investors & ROI Focus", "Expats & Internationals", "First-Time Buyers", "Vacation / Holiday Market", "Commercial Tenants"],
        "custom_inst": "Special Notes & Highlights",
        "custom_inst_ph": "E.g., Private pool, panoramic sea view, smart home, near international school...",
        "btn": "GENERATE COMPLETE MARKETING ASSETS",
        "upload_label": "Drop Property Photos Here",
        "result": "Executive Preview",
        "loading": "Crafting your premium marketing ecosystem...",
        "empty": "Upload property photos and fill in the details on the left to generate complete professional marketing assets.",
        "download": "Export Section (TXT)",
        "download_all": "Export ALL Sections (TXT)",
        "save_btn": "Save Changes",
        "saved_msg": "Saved!",
        "error": "Error:",
        "clear_btn": "Reset Form",
        "tab_main": "Prime Listing",
        "tab_social": "Social Media Kit",
        "tab_video": "Video Scripts",
        "tab_tech": "Technical Specs",
        "tab_email": "Email Campaign",
        "tab_seo": "SEO & Web Copy",
        "label_main": "Sales Copy",
        "label_social": "Social Media Content",
        "label_video": "Video Script",
        "label_tech": "Technical Specifications",
        "label_email": "Email Campaign",
        "label_seo": "SEO & Web Copy",
        "photos_uploaded": "photos loaded",
        "pro_tip": "Pro Tip: Upload 3-6 photos including exterior, interior, and key features for richest output.",
        "extra_details": "Extra Property Details",
        "marketing_config": "Marketing Settings",
        "interface_lang": "Interface Language",
        "config_section": "Configuration",
    },
    "Turkce": {
        "title": "SarSa AI | Gayrimenkul Zeka Platformu",
        "service_desc": "Hepsi Bir Arada Gorsel Mulk Zekas ve Kuresel Satis Otomasyonu",
        "subtitle": "Mulk fotograflarini aninda profesyonel ilanlara, sosyal medya kitlerine, sinematik senaryolara, teknik sartnamelere, e-posta kampanyalarina ve SEO metinlerine donusturun.",
        "settings": "Yapilandirma",
        "target_lang": "Ilan Yazim Dili...",
        "prop_type": "Emlak Tipi",
        "price": "Pazar Fiyati",
        "location": "Konum",
        "tone": "Pazarlama Stratejisi",
        "tones": ["Standart Profesyonel", "Ultra-Luks", "Yatirim Odakli", "Modern Minimalist", "Aile Yasami", "Tatil Kiralik", "Ticari"],
        "ph_prop": "Orn: 3+1 Daire, Mustakil Villa...",
        "ph_price": "Orn: 5.000.000 TL veya $2.500/ay...",
        "ph_loc": "Orn: Besiktas, Istanbul...",
        "bedrooms": "Yatak Odasi",
        "bathrooms": "Banyo",
        "area": "Alan",
        "year_built": "Insaat Yili",
        "ph_beds": "Orn: 3",
        "ph_baths": "Orn: 2",
        "ph_area": "Orn: 185 m2",
        "ph_year": "Orn: 2022",
        "furnishing": "Esya Durumu",
        "furnishing_opts": ["Belirtilmedi", "Tam Esyali", "Yari Esyali", "Esyasiz"],
        "target_audience": "Hedef Kitle",
        "audience_opts": ["Genel Pazar", "Luks Alicilar", "Yatirimcilar & ROI", "Yabanciplar & Uluslararasi", "Ilk Ev Alicilari", "Tatil / Kiralik Pazar", "Ticari Kiracilar"],
        "custom_inst": "Ozel Notlar ve One Cikan Ozellikler",
        "custom_inst_ph": "Orn: Ozel havuz, panoramik manzara, akilli ev sistemi...",
        "btn": "TUM PAZARLAMA VARLIKLARINI OLUSTUR",
        "upload_label": "Fotograflari Buraya Birakin",
        "result": "Yonetici Onizlemesi",
        "loading": "Premium pazarlama ekosisteminiz hazirlaniyor...",
        "empty": "Profesyonel analiz icin gorsel bekleniyor. Fotograflari yukleyin ve soldaki bilgileri doldurun.",
        "download": "Bolumu Indir (TXT)",
        "download_all": "Tum Bolumleri Disari Aktar (TXT)",
        "save_btn": "Kaydet",
        "saved_msg": "Kaydedildi!",
        "error": "Hata:",
        "clear_btn": "Formu Temizle",
        "tab_main": "Ana Ilan",
        "tab_social": "Sosyal Medya Kiti",
        "tab_video": "Video Senaryolari",
        "tab_tech": "Teknik Ozellikler",
        "tab_email": "E-posta Kampanyasi",
        "tab_seo": "SEO & Web Metni",
        "label_main": "Satis Metni",
        "label_social": "Sosyal Medya",
        "label_video": "Video Script",
        "label_tech": "Teknik Detaylar",
        "label_email": "E-posta Kampanyasi",
        "label_seo": "SEO & Web Metni",
        "photos_uploaded": "fotograf yuklendi",
        "pro_tip": "Ipucu: En iyi sonuc icin dis mekan, ic mekan ve onemli ozellikleri iceren 3-6 fotograf yukleyin.",
        "extra_details": "Ek Mulk Detaylari",
        "marketing_config": "Pazarlama Ayarlari",
        "interface_lang": "Arayuz Dili",
        "config_section": "Yapilandirma",
    },
    "Espanol": {
        "title": "SarSa AI | Plataforma de Inteligencia Inmobiliaria",
        "service_desc": "Inteligencia Visual de Propiedades y Automatizacion de Ventas Globales",
        "subtitle": "Convierta fotos en anuncios premium, kits de redes sociales, guiones de video, fichas tecnicas, campanas de email y copy SEO al instante.",
        "settings": "Configuracion",
        "target_lang": "Escribir en...",
        "prop_type": "Tipo de Propiedad",
        "price": "Precio de Mercado",
        "location": "Ubicacion",
        "tone": "Estrategia de Marketing",
        "tones": ["Profesional Estandar", "Ultra-Lujo", "Enfoque de Inversion", "Minimalista Moderno", "Vida Familiar", "Alquiler Vacacional", "Comercial"],
        "ph_prop": "Ej: Apartamento 3+1, Villa de Lujo...",
        "ph_price": "Ej: $850.000 o EUR1.500/mes...",
        "ph_loc": "Ej: Madrid, Espana...",
        "bedrooms": "Dormitorios",
        "bathrooms": "Banos",
        "area": "Area",
        "year_built": "Ano de Construccion",
        "ph_beds": "Ej: 3",
        "ph_baths": "Ej: 2",
        "ph_area": "Ej: 185 m2",
        "ph_year": "Ej: 2022",
        "furnishing": "Amueblado",
        "furnishing_opts": ["No especificado", "Completamente Amueblado", "Semi-Amueblado", "Sin Amueblar"],
        "target_audience": "Publico Objetivo",
        "audience_opts": ["Mercado General", "Compradores de Lujo", "Inversores & ROI", "Extranjeros & Internacionales", "Primeros Compradores", "Mercado Vacacional", "Inquilinos Comerciales"],
        "custom_inst": "Notas Especiales y Caracteristicas",
        "custom_inst_ph": "Ej: Piscina privada, vistas al mar, domotica...",
        "btn": "GENERAR ACTIVOS DE MARKETING COMPLETOS",
        "upload_label": "Subir Fotos de la Propiedad",
        "result": "Vista Previa Ejecutiva",
        "loading": "Creando su ecosistema de marketing premium...",
        "empty": "Esperando imagenes para analisis profesional. Suba fotos y complete los detalles a la izquierda.",
        "download": "Exportar Seccion (TXT)",
        "download_all": "Exportar TODO (TXT)",
        "save_btn": "Guardar Cambios",
        "saved_msg": "Guardado!",
        "error": "Error:",
        "clear_btn": "Limpiar Formulario",
        "tab_main": "Anuncio Premium",
        "tab_social": "Kit de Redes Sociales",
        "tab_video": "Guiones de Video",
        "tab_tech": "Especificaciones",
        "tab_email": "Campana de Email",
        "tab_seo": "SEO & Web Copy",
        "label_main": "Texto de Ventas",
        "label_social": "Contenido Social",
        "label_video": "Guion de Video",
        "label_tech": "Ficha Tecnica",
        "label_email": "Campana de Email",
        "label_seo": "SEO & Web Copy",
        "photos_uploaded": "fotos cargadas",
        "pro_tip": "Consejo Pro: Sube 3-6 fotos incluyendo exterior, interior y caracteristicas clave.",
        "extra_details": "Detalles Adicionales",
        "marketing_config": "Configuracion de Marketing",
        "interface_lang": "Idioma de Interfaz",
        "config_section": "Configuracion",
    },
    "Deutsch": {
        "title": "SarSa AI | Immobilien-Intelligenz-Plattform",
        "service_desc": "All-in-One Visuelle Objektintelligenz & Globale Verkaufsautomatisierung",
        "subtitle": "Verwandeln Sie Fotos sofort in Premium-Exposes, Social-Media-Kits, Videoskripte, Datenblaetter, E-Mail-Kampagnen und SEO-Texte.",
        "settings": "Konfiguration",
        "target_lang": "Erstellen in...",
        "prop_type": "Objekttyp",
        "price": "Marktpreis",
        "location": "Standort",
        "tone": "Marketingstrategie",
        "tones": ["Standard-Profi", "Ultra-Luxus", "Investitionsfokus", "Modern-Minimalistisch", "Familienleben", "Ferienmiete", "Gewerbe"],
        "ph_prop": "Z.B. 3-Zimmer-Wohnung, Luxusvilla...",
        "ph_price": "Z.B. 850.000EUR oder 2.000EUR/Monat...",
        "ph_loc": "Z.B. Berlin, Deutschland...",
        "bedrooms": "Schlafzimmer",
        "bathrooms": "Badezimmer",
        "area": "Flaeche",
        "year_built": "Baujahr",
        "ph_beds": "Z.B. 3",
        "ph_baths": "Z.B. 2",
        "ph_area": "Z.B. 185 m2",
        "ph_year": "Z.B. 2022",
        "furnishing": "Moeblierung",
        "furnishing_opts": ["Nicht angegeben", "Vollmoebliert", "Teilmoebliert", "Unmoebliert"],
        "target_audience": "Zielgruppe",
        "audience_opts": ["Allgemeiner Markt", "Luxuskaeufer", "Investoren & ROI", "Expats & Internationale", "Erstkaeufer", "Ferienmarkt", "Gewerbemieter"],
        "custom_inst": "Notizen & Besonderheiten",
        "custom_inst_ph": "Z.B. Privatpool, Panoramasicht, Smart-Home...",
        "btn": "KOMPLETTE MARKETING-ASSETS ERSTELLEN",
        "upload_label": "Fotos hier hochladen",
        "result": "Executive-Vorschau",
        "loading": "Ihr Marketing-Oekosystem wird erstellt...",
        "empty": "Warte auf Bilder fuer die Analyse. Laden Sie Fotos hoch und fuellen Sie die Details aus.",
        "download": "Abschnitt Exportieren (TXT)",
        "download_all": "ALLES Exportieren (TXT)",
        "save_btn": "Speichern",
        "saved_msg": "Gespeichert!",
        "error": "Fehler:",
        "clear_btn": "Formular Zuruecksetzen",
        "tab_main": "Premium-Expose",
        "tab_social": "Social Media Kit",
        "tab_video": "Videoskripte",
        "tab_tech": "Tech-Details",
        "tab_email": "E-Mail-Kampagne",
        "tab_seo": "SEO & Webtext",
        "label_main": "Verkaufstext",
        "label_social": "Social-Media-Content",
        "label_video": "Videoskript",
        "label_tech": "Technische Daten",
        "label_email": "E-Mail-Kampagne",
        "label_seo": "SEO & Webtext",
        "photos_uploaded": "Fotos geladen",
        "pro_tip": "Tipp: Laden Sie 3-6 Fotos mit Aussen-, Innenansichten und Highlights hoch.",
        "extra_details": "Weitere Details",
        "marketing_config": "Marketing-Einstellungen",
        "interface_lang": "Oberflaeche Sprache",
        "config_section": "Konfiguration",
    },
    "Francais": {
        "title": "SarSa AI | Plateforme d'Intelligence Immobiliere",
        "service_desc": "Intelligence Visuelle Immobiliere et Automatisation des Ventes Globales",
        "subtitle": "Transformez vos photos en annonces premium, kits reseaux sociaux, scripts video, fiches techniques, campagnes email et copy SEO instantanement.",
        "settings": "Configuration",
        "target_lang": "Rediger en...",
        "prop_type": "Type de Bien",
        "price": "Prix du Marche",
        "location": "Localisation",
        "tone": "Strategie Marketing",
        "tones": ["Standard Pro", "Ultra-Luxe", "Focus Investissement", "Minimaliste Moderne", "Vie de Famille", "Location Saisonniere", "Commercial"],
        "ph_prop": "Ex: Appartement T4, Villa de Luxe...",
        "ph_price": "Ex: 850.000EUR ou 1.500EUR/mois...",
        "ph_loc": "Ex: Paris, Cote d'Azur...",
        "bedrooms": "Chambres",
        "bathrooms": "Salles de Bain",
        "area": "Surface",
        "year_built": "Annee de Construction",
        "ph_beds": "Ex: 3",
        "ph_baths": "Ex: 2",
        "ph_area": "Ex: 185 m2",
        "ph_year": "Ex: 2022",
        "furnishing": "Ameublement",
        "furnishing_opts": ["Non specifie", "Entierement Meuble", "Semi-Meuble", "Non Meuble"],
        "target_audience": "Audience Cible",
        "audience_opts": ["Marche General", "Acheteurs de Luxe", "Investisseurs & ROI", "Expatries & Internationaux", "Primo-Accedants", "Marche Vacances", "Locataires Commerciaux"],
        "custom_inst": "Notes Speciales & Points Forts",
        "custom_inst_ph": "Ex: Piscine privee, vue panoramique, domotique...",
        "btn": "GENERER LES ACTIFS MARKETING COMPLETS",
        "upload_label": "Deposer les Photos Ici",
        "result": "Apercu Executif",
        "loading": "Preparation de votre ecosysteme marketing...",
        "empty": "En attente d'images pour analyse. Deposez des photos et remplissez les details a gauche.",
        "download": "Exporter Section (TXT)",
        "download_all": "Exporter TOUT (TXT)",
        "save_btn": "Enregistrer",
        "saved_msg": "Enregistre!",
        "error": "Erreur:",
        "clear_btn": "Reinitialiser",
        "tab_main": "Annonce Premium",
        "tab_social": "Kit Reseaux Sociaux",
        "tab_video": "Scripts Video",
        "tab_tech": "Specifications",
        "tab_email": "Campagne Email",
        "tab_seo": "SEO & Web Copy",
        "label_main": "Texte de Vente",
        "label_social": "Contenu Social",
        "label_video": "Script Video",
        "label_tech": "Details Techniques",
        "label_email": "Campagne Email",
        "label_seo": "SEO & Web Copy",
        "photos_uploaded": "photos chargees",
        "pro_tip": "Conseil Pro: Telechargez 3 a 6 photos incluant l'exterieur, l'interieur et les atouts.",
        "extra_details": "Details Supplementaires",
        "marketing_config": "Parametres Marketing",
        "interface_lang": "Langue Interface",
        "config_section": "Configuration",
    },
    "Portugues": {
        "title": "SarSa AI | Plataforma de Inteligencia Imobiliaria",
        "service_desc": "Inteligencia Visual Imobiliaria e Automacao de Vendas Globais",
        "subtitle": "Transforme fotos em anuncios premium, kits de redes sociais, roteiros de video, fichas tecnicas, campanhas de email e copy SEO instantaneamente.",
        "settings": "Configuracao",
        "target_lang": "Escrever em...",
        "prop_type": "Tipo de Imovel",
        "price": "Preco de Mercado",
        "location": "Localizacao",
        "tone": "Estrategia de Marketing",
        "tones": ["Profissional Padrao", "Ultra-Luxo", "Foco em Investimento", "Minimalista Moderno", "Vida Familiar", "Aluguel de Temporada", "Comercial"],
        "ph_prop": "Ex: Apartamento T3, Moradia de Luxo...",
        "ph_price": "Ex: EUR500.000 ou EUR1.500/mes...",
        "ph_loc": "Ex: Lisboa, Algarve...",
        "bedrooms": "Quartos",
        "bathrooms": "Banheiros",
        "area": "Area",
        "year_built": "Ano de Construcao",
        "ph_beds": "Ex: 3",
        "ph_baths": "Ex: 2",
        "ph_area": "Ex: 185 m2",
        "ph_year": "Ex: 2022",
        "furnishing": "Mobiliario",
        "furnishing_opts": ["Nao especificado", "Completamente Mobilado", "Semi-Mobilado", "Sem Mobilia"],
        "target_audience": "Publico-Alvo",
        "audience_opts": ["Mercado Geral", "Compradores de Luxo", "Investidores & ROI", "Expats e Internacionais", "Primeiros Compradores", "Mercado de Ferias", "Inquilinos Comerciais"],
        "custom_inst": "Notas Especiais e Destaques",
        "custom_inst_ph": "Ex: Piscina privativa, vista panoramica, casa inteligente...",
        "btn": "GERAR ATIVOS DE MARKETING COMPLETOS",
        "upload_label": "Enviar Fotos do Imovel",
        "result": "Pre-visualizacao Executiva",
        "loading": "Preparando seu ecossistema de marketing...",
        "empty": "Aguardando imagens para analise. Envie fotos e preencha os detalhes a esquerda.",
        "download": "Exportar Secao (TXT)",
        "download_all": "Exportar TUDO (TXT)",
        "save_btn": "Salvar Alteracoes",
        "saved_msg": "Salvo!",
        "error": "Erro:",
        "clear_btn": "Limpar Formulario",
        "tab_main": "Anuncio Premium",
        "tab_social": "Kit Redes Sociais",
        "tab_video": "Roteiros de Video",
        "tab_tech": "Especificacoes",
        "tab_email": "Campanha de Email",
        "tab_seo": "SEO & Web Copy",
        "label_main": "Texto de Vendas",
        "label_social": "Conteudo Social",
        "label_video": "Roteiro de Video",
        "label_tech": "Especificacoes Tecnicas",
        "label_email": "Campanha Email",
        "label_seo": "SEO & Web Copy",
        "photos_uploaded": "fotos carregadas",
        "pro_tip": "Dica Pro: Envie 3-6 fotos incluindo exterior, interior e caracteristicas principais.",
        "extra_details": "Detalhes Adicionais",
        "marketing_config": "Configuracoes de Marketing",
        "interface_lang": "Idioma Interface",
        "config_section": "Configuracao",
    },
    "Japanese": {
        "title": "SarSa AI | Fudosan Intelligence Platform",
        "service_desc": "Allinone Bukken Intelligence & Global Hanbai Jidoka",
        "subtitle": "Bukken shashin wo premium kokoku, SNS kit, doga daihon, gijutsu shiyosho, mail campaign, SEO copy ni henkan.",
        "settings": "Settei",
        "target_lang": "Sakusei gengo...",
        "prop_type": "Bukken shubetsu",
        "price": "Shijo kakaku",
        "location": "Shozaichi",
        "tone": "Marketing senryaku",
        "tones": ["Standard Pro", "Ultra Luxury", "Toshi juushi", "Modern Minimalist", "Family muke", "Vacation Rental", "Shogyoyo"],
        "ph_prop": "Rei: 3LDK Mansion, Luxury Bessou...",
        "ph_price": "Rei: 5000man en, tsuki 20man en...",
        "ph_loc": "Rei: Tokyo Minato-ku...",
        "bedrooms": "Shinshitsu su",
        "bathrooms": "Yokushitsu su",
        "area": "Menseki",
        "year_built": "Kenchiku nen",
        "ph_beds": "Rei: 3",
        "ph_baths": "Rei: 2",
        "ph_area": "Rei: 185 sqm",
        "ph_year": "Rei: 2022",
        "furnishing": "Kagu",
        "furnishing_opts": ["Mishitei", "Full kagu tsuki", "Han kagu tsuki", "Kagu nashi"],
        "target_audience": "Target so",
        "audience_opts": ["Ippan shijo", "Furoso buyer", "Toshika & ROI", "Gaikokujin", "Sho-konya", "Vacation shijo", "Tenant"],
        "custom_inst": "Tokki jiko & Appeal point",
        "custom_inst_ph": "Rei: Private pool, Panorama view, Smart home...",
        "btn": "KANZEN NA MARKETING SHISAN WO SESEI",
        "upload_label": "Koko ni shashin wo upload",
        "result": "Executive Preview",
        "loading": "Marketing ecosystem wo kochiku chuu...",
        "empty": "Bunseki yo no gazo wo taiki chuu. Shashin to meisai wo nyuryoku shite kudasai.",
        "download": "Section wo Export (TXT)",
        "download_all": "Zen section export (TXT)",
        "save_btn": "Henka wo hozon",
        "saved_msg": "Hozon kanryo!",
        "error": "Error:",
        "clear_btn": "Form wo reset",
        "tab_main": "Premium kokoku",
        "tab_social": "SNS Kit",
        "tab_video": "Doga daihon",
        "tab_tech": "Gijutsu shiyosho",
        "tab_email": "Mail Campaign",
        "tab_seo": "SEO & Web Copy",
        "label_main": "Sales Copy",
        "label_social": "SNS Content",
        "label_video": "Doga daihon",
        "label_tech": "Gijutsu shiyosho",
        "label_email": "Mail Campaign",
        "label_seo": "SEO Text",
        "photos_uploaded": "mai no shashin",
        "pro_tip": "Hint: Gaikan, naikan, tokuchou wo fukumu 3-6 mai no shashin de saiyo no kekka.",
        "extra_details": "Shosai joho",
        "marketing_config": "Marketing settei",
        "interface_lang": "Interface gengo",
        "config_section": "Settei",
    },
    "Chinese": {
        "title": "SarSa AI | Fangdichan Zhineng Pingtai",
        "service_desc": "Quanfangwei Fangchan Shijue Zhineng yu Quanqiu Xiaoshou Zidonghua",
        "subtitle": "Liji jiang fangchan zhaopian zhuanhua wei youzhi fangyuan miaoshu, shejiaoメディア bao, shipin jiaobense, jishu guige, youjian yingxiao he SEO wenant.",
        "settings": "Peizhì",
        "target_lang": "Bianxie yuyan...",
        "prop_type": "Fangchan leixing",
        "price": "Shichang jiage",
        "location": "Didian",
        "tone": "Yingxiao celue",
        "tones": ["Biaozhun zhuanye", "Dingzhe haozhai", "Touzi qianzhi", "Xiandai jianyue", "Jiating shenghuo", "Dujia zuli", "Shangyedifang"],
        "ph_prop": "Liru: 3 woshi gongyu, haohuan bieshu...",
        "ph_price": "Liru: $5,000,000 huo $2,000/yue...",
        "ph_loc": "Liru: Shanghai Pudong Xinqu...",
        "bedrooms": "Woshi",
        "bathrooms": "Xishoujian",
        "area": "Mianji",
        "year_built": "Jianzao nianfen",
        "ph_beds": "Liru: 3",
        "ph_baths": "Liru: 2",
        "ph_area": "Liru: 185 pingfangmi",
        "ph_year": "Liru: 2022",
        "furnishing": "Zhuangxiu qingkuang",
        "furnishing_opts": ["Wei zhiding", "Quan zhuangxiu", "Ban zhuangxiu", "Maopi"],
        "target_audience": "Mubiao shozhong",
        "audience_opts": ["Dazhong shichang", "Haohuan maijia", "Touzizhe & ROI", "Waiji renshi", "Shouchi goufang zhe", "Dujia shichang", "Shangye zuhu"],
        "custom_inst": "Tebie beizhu he liangdian",
        "custom_inst_ph": "Liru: Siren youyong chi, quanjing shiye, zhineng jiaju...",
        "btn": "SHENGCHENG WANZHENG YINGXIAO ZICHAN",
        "upload_label": "Zai chuchu shangchuan fangchan zhaopian",
        "result": "Gaoguan yulan",
        "loading": "Zhengzai daizao nin de gaoduan yingxiao shengtai...",
        "empty": "Dengdai tupian jinxing fenxi. Shangchuan zhaopian bing tianxie zuoce de xiangqing.",
        "download": "Daochu bujian (TXT)",
        "download_all": "Daochu quanbu (TXT)",
        "save_btn": "Baocun gengge",
        "saved_msg": "Yi baocun!",
        "error": "Cuowu:",
        "clear_btn": "Chongzhi biaodan",
        "tab_main": "Youzhi fangyuan",
        "tab_social": "Shejiao meiti bao",
        "tab_video": "Shipin jiaobense",
        "tab_tech": "Jishu xijie",
        "tab_email": "Youjian yingxiao",
        "tab_seo": "SEO he wangye wenamt",
        "label_main": "Xiaoshou wenamt",
        "label_social": "Shejiaoメディア neirong",
        "label_video": "Shipin jiaobense",
        "label_tech": "Jishu guige",
        "label_email": "Youjian yingxiao",
        "label_seo": "SEO wenamt",
        "photos_uploaded": "zhang zhaopian yi jiazai",
        "pro_tip": "Tishi: Shangchuan 3-6 zhang bao gua waimian, neibu he zhuyao tezheng de zhaopian yi huo zui jia xiaoguo.",
        "extra_details": "Ewai xiangqing",
        "marketing_config": "Yingxiao shezhi",
        "interface_lang": "Jemian yuyan",
        "config_section": "Peizhì",
    },
    "Arabic": {
        "title": "SarSa AI | Mansat al-Dhaka' al-Aqari",
        "service_desc": "Dhaka' al-Aqarat al-Basari al-Mutakamil wa Atmtat al-Mabiaat al-Alamiyya",
        "subtitle": "Hawwil suwar al-aqarat ila ilan mumayyaza, baqat tawasul ijtimaii, sinariyuhat video, muwasafat fanniyya, hamalat barid wa nusus SEO fawran.",
        "settings": "Al-Idadat",
        "target_lang": "Lughat al-kitaba...",
        "prop_type": "Naw' al-aqar",
        "price": "Si'r al-suq",
        "location": "Al-mawqi'",
        "tone": "Istiratijiyyat al-tarsiq",
        "tones": ["Ihtirafi qiyasi", "Fakhama fa'iqa", "Tarkiz al-istithmar", "Asri basit", "Al-hayat al-a'iliyya", "Al-iqar al-mawsimi", "Tijari"],
        "ph_prop": "Mithal: Fila 3 ghuraf, shaqqa istudio...",
        "ph_price": "Mithal: $850,000 aw $2,500 shahriyyan...",
        "ph_loc": "Mithal: Dubai, al-Riyadh, Abu Dhabi...",
        "bedrooms": "Ghuraf al-nawm",
        "bathrooms": "Al-hammam",
        "area": "Al-masa'a",
        "year_built": "Sana al-bina'",
        "ph_beds": "Mithal: 3",
        "ph_baths": "Mithal: 2",
        "ph_area": "Mithal: 185 m2",
        "ph_year": "Mithal: 2022",
        "furnishing": "Al-tathith",
        "furnishing_opts": ["Ghair muhadad", "Mufruush bilkamil", "Mufruush juz'iyyan", "Ghair mufruush"],
        "target_audience": "Al-jumhuur al-mustahdaf",
        "audience_opts": ["Al-suq al-amm", "Mushtaruu al-fakhama", "Al-mustathmiroon & ROI", "Al-mughtariboon wa al-dawliyyoon", "Awwal shuqqa", "Suq al-ijazat", "Al-musta'jiroon al-tijariyyoon"],
        "custom_inst": "Mulahazat khasa wa mazaya",
        "custom_inst_ph": "Mithal: Masbah khass, ittila' banuramiyya, nizam al-bayt al-dhaki...",
        "btn": "INSHA' USUL TARSIQIYYA MUTAKAMALAH",
        "upload_label": "Dha' suwar al-aqar huna",
        "result": "Mu'ayana tanfidhiyya",
        "loading": "Jari tahdir manzumatik al-tarsiqiyya al-fakhira...",
        "empty": "Fi intizar al-suwar libad' al-tahlil al-mihni. Arfa' al-suwar wa imla' al-tafasil ala al-yisar.",
        "download": "Tasdir al-qism (TXT)",
        "download_all": "Tasdir al-kull (TXT)",
        "save_btn": "Hafz al-taghayyurat",
        "saved_msg": "Tamma al-hafz!",
        "error": "Khata':",
        "clear_btn": "I'adat tashbib al-namuzaj",
        "tab_main": "Ilan mumayyaz",
        "tab_social": "Baqat al-tawasul al-ijtimaii",
        "tab_video": "Sinariyuhat al-video",
        "tab_tech": "Tafasil tiqniyya",
        "tab_email": "Hamla al-barid al-iliktrouni",
        "tab_seo": "SEO wa nass al-web",
        "label_main": "Nass al-mabiaat",
        "label_social": "Muhtawa al-tawasul",
        "label_video": "Sinaryu al-video",
        "label_tech": "Al-muwasafat al-fanniyya",
        "label_email": "Hamla al-barid",
        "label_seo": "Nass SEO wa al-web",
        "photos_uploaded": "suwar mahmula",
        "pro_tip": "Nasiha: Arfa' 3-6 suwar tatadamman al-kharij wa al-dakhil wa al-mazaya al-ra'isiyya lilhusul ala afdal al-nata'ij.",
        "extra_details": "Tafasil idafiyya",
        "marketing_config": "I'dadat al-tarsiq",
        "interface_lang": "Lughat al-wajha",
        "config_section": "Al-Idadat",
    },
}

# ─── SESSION STATE ───────────────────────────────────────────────────────────
for key, val in [
    ("uretilen_ilan", ""), ("prop_type", ""), ("price", ""),
    ("location", ""), ("tone", ""), ("custom_inst", ""),
    ("target_lang_input", "English"), ("bedrooms", ""),
    ("bathrooms", ""), ("area_size", ""), ("year_built", ""),
    ("furnishing_idx", 0), ("audience_idx", 0),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
.stApp { background-color: #f0f4f8 !important; }
div[data-testid="stInputInstructions"] { display: none !important; }
#MainMenu, footer { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
span[data-testid="stIconMaterial"] { display: none !important; }

.block-container {
    background: white; padding: 2.5rem 3rem !important;
    border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.06);
    margin-top: 1.5rem; border: 1px solid #e2e8f0;
}
h1 { color: #0f172a !important; font-weight: 800 !important; text-align: center; }

[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stSelectbox label {
    font-size: 0.74rem !important; font-weight: 700 !important;
    color: #64748b !important; text-transform: uppercase !important; letter-spacing: 0.7px !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea {
    border-radius: 8px !important; border: 1.5px solid #e2e8f0 !important;
    background: #f8fafc !important; font-size: 0.875rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stTextArea textarea:focus {
    border-color: #0f172a !important; background: #fff !important;
    box-shadow: 0 0 0 3px rgba(15,23,42,0.08) !important;
}

button, [data-baseweb="tab"], [data-testid="stFileUploader"],
div[data-baseweb="select"], div[role="button"], .stSelectbox div { cursor: pointer !important; }
.stTextInput input, .stTextArea textarea { cursor: text !important; }

.stButton > button {
    background: #0f172a !important; color: white !important;
    border-radius: 12px !important; padding: 14px 24px !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    width: 100% !important; border: none !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 15px rgba(15,23,42,0.3) !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    background: #1e293b !important; box-shadow: 0 8px 25px rgba(15,23,42,0.4) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stDownloadButton"] > button {
    background: #f8fafc !important; color: #334155 !important;
    border: 1.5px solid #e2e8f0 !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.82rem !important; box-shadow: none !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #f1f5f9 !important; border-color: #0f172a !important;
    color: #0f172a !important; box-shadow: 0 2px 8px rgba(15,23,42,0.1) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: transparent !important; gap: 4px !important;
    border-bottom: 2px solid #e2e8f0 !important; padding-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600 !important; font-size: 0.82rem !important;
    color: #64748b !important; border-radius: 8px 8px 0 0 !important;
    padding: 0.7rem 1.1rem !important; background: transparent !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { background: #f8fafc !important; color: #0f172a !important; }
.stTabs [aria-selected="true"] {
    background-color: #0f172a !important; color: white !important;
    border-radius: 8px 8px 0 0 !important;
}

.stTextArea textarea {
    border-radius: 12px !important; border: 1.5px solid #e2e8f0 !important;
    background: #fafbfc !important; font-size: 0.875rem !important;
    line-height: 1.7 !important; transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: #0f172a !important; background: #fff !important;
    box-shadow: 0 0 0 3px rgba(15,23,42,0.07) !important;
}

[data-testid="stFileUploader"] {
    border-radius: 14px !important; border: 2px dashed #cbd5e1 !important;
    background: #f8fafc !important; transition: all 0.3s !important; padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover { border-color: #0f172a !important; background: #f0f4f8 !important; }
[data-testid="stImage"] img { border-radius: 10px !important; }
.stInfo, .stSuccess { border-radius: 12px !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    logo_img = load_logo("SarSa_Logo_Transparent.png")
    if logo_img:
        st.image(logo_img, use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:0.8rem 0 0.5rem;">
          <span style="font-size:1.8rem; font-weight:800; color:#0f172a;">SarSa</span>
          <span style="font-size:1.8rem; font-weight:800; background:linear-gradient(135deg,#3b82f6,#8b5cf6);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;"> AI</span>
          <div style="font-size:0.62rem;color:#94a3b8;letter-spacing:2px;text-transform:uppercase;margin-top:2px;">
          Real Estate Intelligence</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Interface Language (ALWAYS VISIBLE AT TOP) ──
    current_ui_lang = st.selectbox(
        "🌐 Interface Language",
        list(ui_languages.keys()),
        index=0
    )
    t = ui_languages[current_ui_lang]

    st.markdown("---")

    # ── ⚙️ CONFIGURATION (original section - preserved exactly) ──
    st.header(t["settings"])

    st.session_state.target_lang_input = st.text_input(
        f"✍️ {t['target_lang']}",
        value=st.session_state.target_lang_input,
        placeholder="English, Francais, العربية, 日本語..."
    )
    st.session_state.prop_type = st.text_input(
        t["prop_type"], value=st.session_state.prop_type, placeholder=t["ph_prop"]
    )
    st.session_state.price = st.text_input(
        t["price"], value=st.session_state.price, placeholder=t["ph_price"]
    )
    st.session_state.location = st.text_input(
        t["location"], value=st.session_state.location, placeholder=t["ph_loc"]
    )

    current_tone_idx = t["tones"].index(st.session_state.tone) if st.session_state.tone in t["tones"] else 0
    st.session_state.tone = st.selectbox(t["tone"], t["tones"], index=current_tone_idx)

    st.session_state.custom_inst = st.text_area(
        f"📝 {t['custom_inst']}",
        value=st.session_state.custom_inst,
        placeholder=t["custom_inst_ph"],
        height=100
    )

    # ── 🔑 EXTRA PROPERTY DETAILS (new — added below) ──
    st.markdown(f"""
    <div style="font-size:0.68rem; font-weight:800; color:#94a3b8; text-transform:uppercase;
    letter-spacing:1.4px; padding:0.6rem 0 0.3rem 0; border-bottom:1px solid #f1f5f9; margin-bottom:0.4rem;">
    🔑 {t['extra_details']}</div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.bedrooms = st.text_input(
            t["bedrooms"], value=st.session_state.bedrooms, placeholder=t["ph_beds"]
        )
    with col2:
        st.session_state.bathrooms = st.text_input(
            t["bathrooms"], value=st.session_state.bathrooms, placeholder=t["ph_baths"]
        )
    col3, col4 = st.columns(2)
    with col3:
        st.session_state.area_size = st.text_input(
            t["area"], value=st.session_state.area_size, placeholder=t["ph_area"]
        )
    with col4:
        st.session_state.year_built = st.text_input(
            t["year_built"], value=st.session_state.year_built, placeholder=t["ph_year"]
        )

    furnishing_opts = t["furnishing_opts"]
    furnishing_sel = st.selectbox(t["furnishing"], furnishing_opts, index=st.session_state.furnishing_idx)
    st.session_state.furnishing_idx = furnishing_opts.index(furnishing_sel)

    # ── 🎯 MARKETING SETTINGS (new) ──
    st.markdown(f"""
    <div style="font-size:0.68rem; font-weight:800; color:#94a3b8; text-transform:uppercase;
    letter-spacing:1.4px; padding:0.6rem 0 0.3rem 0; border-bottom:1px solid #f1f5f9; margin-bottom:0.4rem;">
    🎯 {t['marketing_config']}</div>""", unsafe_allow_html=True)

    audience_opts = t["audience_opts"]
    audience_sel = st.selectbox(t["target_audience"], audience_opts, index=st.session_state.audience_idx)
    st.session_state.audience_idx = audience_opts.index(audience_sel)

    # ── PRO TIP ──
    st.markdown(f"""
    <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px;
    padding:0.7rem 1rem; font-size:0.78rem; color:#1e40af; margin-top:0.8rem; line-height:1.5;">
    💡 {t['pro_tip']}</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(f"🗑️ {t['clear_btn']}", use_container_width=True):
        for k in ["uretilen_ilan", "prop_type", "price", "location", "tone",
                  "custom_inst", "bedrooms", "bathrooms", "area_size", "year_built"]:
            st.session_state[k] = ""
        st.session_state.furnishing_idx = 0
        st.session_state.audience_idx = 0
        st.rerun()

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
st.markdown(f"<h1>🏢 {t['title']}</h1>", unsafe_allow_html=True)
st.markdown(
    f"<p style='text-align:center; color:#0f172a; font-weight:700; font-size:1.35rem;"
    f"letter-spacing:0.3px; margin-bottom:5px;'>{t['service_desc']}</p>", unsafe_allow_html=True
)
st.markdown(
    f"<div style='text-align:center; color:#64748b; font-size:1rem; max-width:850px;"
    f"margin:0 auto 2rem auto; line-height:1.6;'>{t['subtitle']}</div>", unsafe_allow_html=True
)

# ── File Uploader ──
uploaded_files = st.file_uploader(
    f"📸 {t['upload_label']}",
    type=["jpg", "png", "webp", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    images_for_ai = [Image.open(f) for f in uploaded_files]
    n = len(images_for_ai)

    st.markdown(
        f"<div style='display:inline-flex;align-items:center;gap:6px;background:#dbeafe;"
        f"color:#1d4ed8;border-radius:20px;padding:4px 12px;font-size:0.78rem;"
        f"font-weight:700;margin-bottom:0.8rem;'>📷 {n} {t['photos_uploaded']}</div>",
        unsafe_allow_html=True
    )

    cols = st.columns(min(n, 4))
    for i, img in enumerate(images_for_ai):
        with cols[i % min(n, 4)]:
            st.image(img, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(f"🚀 {t['btn']}"):
        with st.spinner(t["loading"]):
            p_type  = st.session_state.prop_type or "Property"
            p_loc   = st.session_state.location or "Undisclosed Location"
            p_price = st.session_state.price or "Price upon request"
            p_furn  = furnishing_sel if furnishing_sel != t["furnishing_opts"][0] else "Not specified"
            p_aud   = audience_sel if audience_sel != t["audience_opts"][0] else "General Market"

            details = f"""
PROPERTY DETAILS:
- Type: {p_type}
- Location: {p_loc}
- Price: {p_price}
- Bedrooms: {st.session_state.bedrooms or 'Determine from photos'}
- Bathrooms: {st.session_state.bathrooms or 'Determine from photos'}
- Area: {st.session_state.area_size or 'Determine from photos'}
- Year Built: {st.session_state.year_built or 'Not specified'}
- Furnishing: {p_furn}
- Target Audience: {p_aud}
- Marketing Strategy: {st.session_state.tone}
- Special Notes: {st.session_state.custom_inst or 'None'}
"""
            prompt = f"""You are a world-class Senior Real Estate Strategist, Copywriter and Marketing Director for SarSa AI — the global leader in AI-powered property intelligence.

OUTPUT LANGUAGE: Write ALL content in {st.session_state.target_lang_input}. Every word of output must be in this language.

{details}

Analyze every uploaded photo deeply: architectural style, finishes, lighting, spatial flow, standout features, condition, and lifestyle appeal. Use photo observations as foundation for all content.

Generate all 6 sections EXACTLY as structured:

## SECTION_1 — PRIME LISTING
World-class property listing:
• Powerful headline (ALL CAPS)
• 4 rich paragraphs: lifestyle narrative, architectural highlights, outdoor/community, investment value
• Bullet list of 12+ specific features observed from photos and provided details
• Strong CTA closing paragraph
Minimum 600 words, vivid and emotionally resonant.

## SECTION_2 — SOCIAL MEDIA KIT
Platform-ready content:
• INSTAGRAM (3 posts): Visual direction + 180-word caption + 25 hashtags each
• FACEBOOK (2 posts): Community-angle, 220 words each
• LINKEDIN (1 post): Investment/professional angle, 200 words
• TWITTER/X (3 tweets): Under 280 chars, punchy
• TIKTOK/REELS (1): 3-second hook + 15-second spoken script
• PINTEREST (1): Inspirational 100-word description + 10 keywords

## SECTION_3 — CINEMATIC VIDEO SCRIPT
Full production script:
• Film title and tagline
• Production notes: runtime (90-150 sec), music style, VO tone
• 10+ scenes: SCENE | TIMECODE | SHOT TYPE | VISUAL | VOICEOVER
• Drone opening, interior walkthrough, lifestyle closing
• Director's post-production notes

## SECTION_4 — TECHNICAL SPECIFICATIONS
Professional data sheet:
• Full property specs table
• Construction & materials from photos
• Smart home / tech features
• Energy & sustainability notes
• Location & infrastructure analysis
• Investment analysis: rental yield estimate, market positioning
• Legal & ownership framework notes
• Photography recommendations: missing angles, reshoot suggestions

## SECTION_5 — EMAIL CAMPAIGN
Three email templates:
EMAIL 1 — New Listing Alert (blast): Subject + 300-word body + PS
EMAIL 2 — Personal Pitch (warm lead): Subject + 260-word body with [personalization tokens]
EMAIL 3 — Follow-up / Offer Update: Subject + 220-word body

## SECTION_6 — SEO & WEB COPY
Complete digital package:
• SEO page title (60 chars max)
• Meta description (155 chars max)
• Primary keyword + 8 secondary keywords with search intent
• H1/H2/H3 heading hierarchy
• 500-word SEO web description
• 5 Google Ads headlines (30 chars each)
• 2 Google Ads descriptions (90 chars each)
• Schema.org markup recommendation
• 3 blog post title ideas for organic traffic"""

            try:
                response = model.generate_content([prompt] + images_for_ai)
                st.session_state.uretilen_ilan = response.text
            except Exception as e:
                st.error(f"{t['error']} {e}")

    # ── RESULTS ──
    if st.session_state.uretilen_ilan:
        raw = st.session_state.uretilen_ilan
        sec = {str(i): "" for i in range(1, 7)}
        for p in raw.split("##"):
            p = p.strip()
            for n in ["1", "2", "3", "4", "5", "6"]:
                if p.startswith(f"SECTION_{n}"):
                    content = p[len(f"SECTION_{n}"):].strip().lstrip("—-– \n")
                    if ":" in content[:10]:
                        content = content.split(":", 1)[-1].strip()
                    sec[n] = content
                    break

        st.markdown("---")
        prop_display = f"{st.session_state.prop_type} · {st.session_state.location}" if st.session_state.prop_type else t["result"]
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);border-radius:14px;
        padding:1.2rem 1.8rem;margin-bottom:1rem;display:flex;align-items:center;justify-content:space-between;">
            <div>
                <div style="font-size:1.1rem;font-weight:800;color:#fff;">💎 {t['result']}</div>
                <div style="font-size:0.8rem;color:#94a3b8;margin-top:3px;">{prop_display} — {st.session_state.tone}</div>
            </div>
            <div style="font-size:0.75rem;color:#64748b;background:rgba(255,255,255,0.1);
            padding:4px 12px;border-radius:20px;color:#cbd5e1;">{datetime.now().strftime('%H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            f"📝 {t['tab_main']}", f"📱 {t['tab_social']}", f"🎬 {t['tab_video']}",
            f"⚙️ {t['tab_tech']}", f"✉️ {t['tab_email']}", f"🔍 {t['tab_seo']}"
        ])

        ts = datetime.now().strftime("%Y%m%d_%H%M")
        results = {}

        def render_tab(tab_obj, label, n, suffix):
            with tab_obj:
                edited = st.text_area(label, value=sec[n], height=450, key=f"txt_{n}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"💾 {t['save_btn']}", key=f"save_{n}", use_container_width=True):
                        sec[n] = edited
                        st.success(f"✅ {t['saved_msg']}")
                with c2:
                    st.download_button(
                        f"📥 {t['download']}", data=edited,
                        file_name=f"sarsa_{suffix}_{ts}.txt", key=f"dl_{n}", use_container_width=True
                    )
                return edited

        results["1"] = render_tab(tab1, t["label_main"], "1", "listing")
        results["2"] = render_tab(tab2, t["label_social"], "2", "social")
        results["3"] = render_tab(tab3, t["label_video"], "3", "video")
        results["4"] = render_tab(tab4, t["label_tech"], "4", "tech")
        results["5"] = render_tab(tab5, t["label_email"], "5", "email")
        results["6"] = render_tab(tab6, t["label_seo"], "6", "seo")

        st.markdown("---")
        prop_slug = (st.session_state.prop_type or "property").replace(" ", "_")[:20].lower()
        all_content = f"""SARSA AI — COMPLETE MARKETING ASSETS
Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}
Property: {st.session_state.prop_type or 'N/A'}
Location: {st.session_state.location or 'N/A'}
Price: {st.session_state.price or 'N/A'}
Language: {st.session_state.target_lang_input}
Strategy: {st.session_state.tone}
{"="*60}

{t['label_main'].upper()}
{"="*60}
{results["1"]}

{t['label_social'].upper()}
{"="*60}
{results["2"]}

{t['label_video'].upper()}
{"="*60}
{results["3"]}

{t['label_tech'].upper()}
{"="*60}
{results["4"]}

{t['label_email'].upper()}
{"="*60}
{results["5"]}

{t['label_seo'].upper()}
{"="*60}
{results["6"]}
"""
        ca, cb = st.columns([2, 1])
        with ca:
            st.download_button(
                label=f"📥 {t['download_all']}",
                data=all_content,
                file_name=f"sarsa_complete_{prop_slug}_{ts}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with cb:
            st.markdown(f"""
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
            padding:0.7rem 1rem;font-size:0.78rem;color:#64748b;text-align:center;">
            ✅ 6 {t['tab_main'].split()[0] if t['tab_main'] else 'sections'} ready · {datetime.now().strftime('%H:%M')}
            </div>""", unsafe_allow_html=True)

else:
    # ── EMPTY STATE ──
    st.markdown(f"""
    <div style="text-align:center;padding:4rem 2rem;color:#94a3b8;
    border:2px dashed #e2e8f0;border-radius:16px;background:#fafbfc;">
        <div style="font-size:3.5rem;margin-bottom:1rem;opacity:0.5;">🏘️</div>
        <div style="font-size:1.25rem;font-weight:700;color:#475569;margin-bottom:0.8rem;">
            {t.get('result', 'Executive Preview')}</div>
        <div style="font-size:0.9rem;max-width:420px;margin:0 auto;line-height:1.6;color:#64748b;">
            {t['empty']}
        </div>
        <div style="display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:1.4rem;">
            <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">📝 {t['tab_main']}</span>
            <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">📱 {t['tab_social']}</span>
            <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">🎬 {t['tab_video']}</span>
            <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">⚙️ {t['tab_tech']}</span>
            <span style="background:#dbeafe;color:#1d4ed8;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #bfdbfe;">✉️ {t['tab_email']}</span>
            <span style="background:#dbeafe;color:#1d4ed8;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #bfdbfe;">🔍 {t['tab_seo']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
