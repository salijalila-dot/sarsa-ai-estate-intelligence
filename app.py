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
    "Türkçe": {
        "title": "SarSa AI | Gayrimenkul Zekâ Platformu",
        "service_desc": "Hepsi Bir Arada Görsel Mülk Zekâsı ve Küresel Satış Otomasyonu",
        "subtitle": "Mülk fotoğraflarını anında profesyonel ilanlara, sosyal medya kitlerine, sinematik senaryolara, teknik şartnamelere, e-posta kampanyalarına ve SEO metinlerine dönüştürün.",
        "settings": "Yapılandırma",
        "target_lang": "İlan Yazım Dili...",
        "prop_type": "Emlak Tipi",
        "price": "Pazar Fiyatı",
        "location": "Konum",
        "tone": "Pazarlama Stratejisi",
        "tones": ["Standart Profesyonel", "Ultra-Lüks", "Yatırım Odaklı", "Modern Minimalist", "Aile Yaşamı", "Tatil Kiralık", "Ticari"],
        "ph_prop": "Örn: 3+1 Daire, Müstakil Villa...",
        "ph_price": "Örn: 5.000.000 TL veya $2.500/ay...",
        "ph_loc": "Örn: Beşiktaş, İstanbul...",
        "bedrooms": "Yatak Odası",
        "bathrooms": "Banyo",
        "area": "Alan",
        "year_built": "İnşaat Yılı",
        "ph_beds": "Örn: 3",
        "ph_baths": "Örn: 2",
        "ph_area": "Örn: 185 m²",
        "ph_year": "Örn: 2022",
        "furnishing": "Eşya Durumu",
        "furnishing_opts": ["Belirtilmedi", "Tam Eşyalı", "Yarı Eşyalı", "Eşyasız"],
        "target_audience": "Hedef Kitle",
        "audience_opts": ["Genel Pazar", "Lüks Alıcılar", "Yatırımcılar & ROI", "Yabancılar & Uluslararası", "İlk Ev Alıcıları", "Tatil / Kiralık Pazar", "Ticari Kiracılar"],
        "custom_inst": "Özel Notlar ve Öne Çıkan Özellikler",
        "custom_inst_ph": "Örn: Özel havuz, panoramik manzara, akıllı ev sistemi...",
        "btn": "TÜM PAZARLAMA VARLIKLARINI OLUŞTUR",
        "upload_label": "Fotoğrafları Buraya Bırakın",
        "result": "Yönetici Önizlemesi",
        "loading": "Premium pazarlama ekosisteminiz hazırlanıyor...",
        "empty": "Profesyonel analiz için görsel bekleniyor. Fotoğrafları yükleyin ve soldaki bilgileri doldurun.",
        "download": "Bölümü İndir (TXT)",
        "download_all": "Tüm Bölümleri Dışarı Aktar (TXT)",
        "save_btn": "Kaydet",
        "saved_msg": "Kaydedildi!",
        "error": "Hata:",
        "clear_btn": "Formu Temizle",
        "tab_main": "Ana İlan",
        "tab_social": "Sosyal Medya Kiti",
        "tab_video": "Video Senaryoları",
        "tab_tech": "Teknik Özellikler",
        "tab_email": "E-posta Kampanyası",
        "tab_seo": "SEO & Web Metni",
        "label_main": "Satış Metni",
        "label_social": "Sosyal Medya",
        "label_video": "Video Script",
        "label_tech": "Teknik Detaylar",
        "label_email": "E-posta Kampanyası",
        "label_seo": "SEO & Web Metni",
        "photos_uploaded": "fotoğraf yüklendi",
        "pro_tip": "İpucu: En iyi sonuç için dış mekan, iç mekan ve önemli özellikleri içeren 3-6 fotoğraf yükleyin.",
        "extra_details": "Ek Mülk Detayları",
        "marketing_config": "Pazarlama Ayarları",
        "interface_lang": "Arayüz Dili",
        "config_section": "Yapılandırma",
    },
    "Español": {
        "title": "SarSa AI | Plataforma de Inteligencia Inmobiliaria",
        "service_desc": "Inteligencia Visual de Propiedades y Automatización de Ventas Globales",
        "subtitle": "Convierta fotos en anuncios premium, kits de redes sociales, guiones de video, fichas técnicas, campañas de email y copy SEO al instante.",
        "settings": "Configuración",
        "target_lang": "Escribir en...",
        "prop_type": "Tipo de Propiedad",
        "price": "Precio de Mercado",
        "location": "Ubicación",
        "tone": "Estrategia de Marketing",
        "tones": ["Profesional Estándar", "Ultra-Lujo", "Enfoque de Inversión", "Minimalista Moderno", "Vida Familiar", "Alquiler Vacacional", "Comercial"],
        "ph_prop": "Ej: Apartamento 3+1, Villa de Lujo...",
        "ph_price": "Ej: $850.000 o EUR 1.500/mes...",
        "ph_loc": "Ej: Madrid, España...",
        "bedrooms": "Dormitorios",
        "bathrooms": "Baños",
        "area": "Área",
        "year_built": "Año de Construcción",
        "ph_beds": "Ej: 3",
        "ph_baths": "Ej: 2",
        "ph_area": "Ej: 185 m²",
        "ph_year": "Ej: 2022",
        "furnishing": "Amueblado",
        "furnishing_opts": ["No especificado", "Completamente Amueblado", "Semi-Amueblado", "Sin Amueblar"],
        "target_audience": "Público Objetivo",
        "audience_opts": ["Mercado General", "Compradores de Lujo", "Inversores & ROI", "Extranjeros & Internacionales", "Primeros Compradores", "Mercado Vacacional", "Inquilinos Comerciales"],
        "custom_inst": "Notas Especiales y Características",
        "custom_inst_ph": "Ej: Piscina privada, vistas al mar, domótica...",
        "btn": "GENERAR ACTIVOS DE MARKETING COMPLETOS",
        "upload_label": "Subir Fotos de la Propiedad",
        "result": "Vista Previa Ejecutiva",
        "loading": "Creando su ecosistema de marketing premium...",
        "empty": "Esperando imágenes para análisis profesional. Suba fotos y complete los detalles a la izquierda.",
        "download": "Exportar Sección (TXT)",
        "download_all": "Exportar TODO (TXT)",
        "save_btn": "Guardar Cambios",
        "saved_msg": "¡Guardado!",
        "error": "Error:",
        "clear_btn": "Limpiar Formulario",
        "tab_main": "Anuncio Premium",
        "tab_social": "Kit de Redes Sociales",
        "tab_video": "Guiones de Video",
        "tab_tech": "Especificaciones",
        "tab_email": "Campaña de Email",
        "tab_seo": "SEO & Web Copy",
        "label_main": "Texto de Ventas",
        "label_social": "Contenido Social",
        "label_video": "Guion de Video",
        "label_tech": "Ficha Técnica",
        "label_email": "Campaña de Email",
        "label_seo": "SEO & Web Copy",
        "photos_uploaded": "fotos cargadas",
        "pro_tip": "Consejo Pro: Sube 3-6 fotos incluyendo exterior, interior y características clave.",
        "extra_details": "Detalles Adicionales",
        "marketing_config": "Configuración de Marketing",
        "interface_lang": "Idioma de Interfaz",
        "config_section": "Configuración",
    },
    "Deutsch": {
        "title": "SarSa AI | Immobilien-Intelligenz-Plattform",
        "service_desc": "All-in-One Visuelle Objektintelligenz & Globale Verkaufsautomatisierung",
        "subtitle": "Verwandeln Sie Fotos sofort in Premium-Exposés, Social-Media-Kits, Videoskripte, Datenblätter, E-Mail-Kampagnen und SEO-Texte.",
        "settings": "Konfiguration",
        "target_lang": "Erstellen in...",
        "prop_type": "Objekttyp",
        "price": "Marktpreis",
        "location": "Standort",
        "tone": "Marketingstrategie",
        "tones": ["Standard-Profi", "Ultra-Luxus", "Investitionsfokus", "Modern-Minimalistisch", "Familienleben", "Ferienmiete", "Gewerbe"],
        "ph_prop": "Z.B. 3-Zimmer-Wohnung, Luxusvilla...",
        "ph_price": "Z.B. 850.000€ oder 2.000€/Monat...",
        "ph_loc": "Z.B. Berlin, Deutschland...",
        "bedrooms": "Schlafzimmer",
        "bathrooms": "Badezimmer",
        "area": "Fläche",
        "year_built": "Baujahr",
        "ph_beds": "Z.B. 3",
        "ph_baths": "Z.B. 2",
        "ph_area": "Z.B. 185 m²",
        "ph_year": "Z.B. 2022",
        "furnishing": "Möblierung",
        "furnishing_opts": ["Nicht angegeben", "Vollmöbliert", "Teilmöbliert", "Unmöbliert"],
        "target_audience": "Zielgruppe",
        "audience_opts": ["Allgemeiner Markt", "Luxuskäufer", "Investoren & ROI", "Expats & Internationale", "Erstkäufer", "Ferienmarkt", "Gewerbemieter"],
        "custom_inst": "Notizen & Besonderheiten",
        "custom_inst_ph": "Z.B. Privatpool, Panoramasicht, Smart-Home...",
        "btn": "KOMPLETTE MARKETING-ASSETS ERSTELLEN",
        "upload_label": "Fotos hier hochladen",
        "result": "Executive-Vorschau",
        "loading": "Ihr Marketing-Ökosystem wird erstellt...",
        "empty": "Warte auf Bilder für die Analyse. Laden Sie Fotos hoch und füllen Sie die Details aus.",
        "download": "Abschnitt Exportieren (TXT)",
        "download_all": "ALLES Exportieren (TXT)",
        "save_btn": "Speichern",
        "saved_msg": "Gespeichert!",
        "error": "Fehler:",
        "clear_btn": "Formular Zurücksetzen",
        "tab_main": "Premium-Exposé",
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
        "pro_tip": "Tipp: Laden Sie 3-6 Fotos mit Außen-, Innenansichten und Highlights hoch.",
        "extra_details": "Weitere Details",
        "marketing_config": "Marketing-Einstellungen",
        "interface_lang": "Oberfläche Sprache",
        "config_section": "Konfiguration",
    },
    "Français": {
        "title": "SarSa AI | Plateforme d'Intelligence Immobilière",
        "service_desc": "Intelligence Visuelle Immobilière et Automatisation des Ventes Globales",
        "subtitle": "Transformez vos photos en annonces premium, kits réseaux sociaux, scripts vidéo, fiches techniques, campagnes email et copy SEO instantanément.",
        "settings": "Configuration",
        "target_lang": "Rédiger en...",
        "prop_type": "Type de Bien",
        "price": "Prix du Marché",
        "location": "Localisation",
        "tone": "Stratégie Marketing",
        "tones": ["Standard Pro", "Ultra-Luxe", "Focus Investissement", "Minimaliste Moderne", "Vie de Famille", "Location Saisonnière", "Commercial"],
        "ph_prop": "Ex: Appartement T4, Villa de Luxe...",
        "ph_price": "Ex: 850.000€ ou 1.500€/mois...",
        "ph_loc": "Ex: Paris, Côte d'Azur...",
        "bedrooms": "Chambres",
        "bathrooms": "Salles de Bain",
        "area": "Surface",
        "year_built": "Année de Construction",
        "ph_beds": "Ex: 3",
        "ph_baths": "Ex: 2",
        "ph_area": "Ex: 185 m²",
        "ph_year": "Ex: 2022",
        "furnishing": "Ameublement",
        "furnishing_opts": ["Non spécifié", "Entièrement Meublé", "Semi-Meublé", "Non Meublé"],
        "target_audience": "Audience Cible",
        "audience_opts": ["Marché Général", "Acheteurs de Luxe", "Investisseurs & ROI", "Expatriés & Internationaux", "Primo-Accédants", "Marché Vacances", "Locataires Commerciaux"],
        "custom_inst": "Notes Spéciales & Points Forts",
        "custom_inst_ph": "Ex: Piscine privée, vue panoramique, domotique...",
        "btn": "GÉNÉRER LES ACTIFS MARKETING COMPLETS",
        "upload_label": "Déposer les Photos Ici",
        "result": "Aperçu Exécutif",
        "loading": "Préparation de votre écosystème marketing...",
        "empty": "En attente d'images pour analyse. Déposez des photos et remplissez les détails à gauche.",
        "download": "Exporter Section (TXT)",
        "download_all": "Exporter TOUT (TXT)",
        "save_btn": "Enregistrer",
        "saved_msg": "Enregistré !",
        "error": "Erreur :",
        "clear_btn": "Réinitialiser",
        "tab_main": "Annonce Premium",
        "tab_social": "Kit Réseaux Sociaux",
        "tab_video": "Scripts Vidéo",
        "tab_tech": "Spécifications",
        "tab_email": "Campagne Email",
        "tab_seo": "SEO & Web Copy",
        "label_main": "Texte de Vente",
        "label_social": "Contenu Social",
        "label_video": "Script Vidéo",
        "label_tech": "Détails Techniques",
        "label_email": "Campagne Email",
        "label_seo": "SEO & Web Copy",
        "photos_uploaded": "photos chargées",
        "pro_tip": "Conseil Pro: Téléchargez 3 à 6 photos incluant l'extérieur, l'intérieur et les atouts.",
        "extra_details": "Détails Supplémentaires",
        "marketing_config": "Paramètres Marketing",
        "interface_lang": "Langue Interface",
        "config_section": "Configuration",
    },
    "Português": {
        "title": "SarSa AI | Plataforma de Inteligência Imobiliária",
        "service_desc": "Inteligência Visual Imobiliária e Automação de Vendas Globais",
        "subtitle": "Transforme fotos em anúncios premium, kits de redes sociais, roteiros de vídeo, fichas técnicas, campanhas de email e copy SEO instantaneamente.",
        "settings": "Configuração",
        "target_lang": "Escrever em...",
        "prop_type": "Tipo de Imóvel",
        "price": "Preço de Mercado",
        "location": "Localização",
        "tone": "Estratégia de Marketing",
        "tones": ["Profissional Padrão", "Ultra-Luxo", "Foco em Investimento", "Minimalista Moderno", "Vida Familiar", "Aluguel de Temporada", "Comercial"],
        "ph_prop": "Ex: Apartamento T3, Moradia de Luxo...",
        "ph_price": "Ex: 500.000€ ou 1.500€/mês...",
        "ph_loc": "Ex: Lisboa, Algarve...",
        "bedrooms": "Quartos",
        "bathrooms": "Banheiros",
        "area": "Área",
        "year_built": "Ano de Construção",
        "ph_beds": "Ex: 3",
        "ph_baths": "Ex: 2",
        "ph_area": "Ex: 185 m²",
        "ph_year": "Ex: 2022",
        "furnishing": "Mobiliário",
        "furnishing_opts": ["Não especificado", "Completamente Mobilado", "Semi-Mobilado", "Sem Mobília"],
        "target_audience": "Público-Alvo",
        "audience_opts": ["Mercado Geral", "Compradores de Luxo", "Investidores & ROI", "Expats e Internacionais", "Primeiros Compradores", "Mercado de Férias", "Inquilinos Comerciais"],
        "custom_inst": "Notas Especiais e Destaques",
        "custom_inst_ph": "Ex: Piscina privativa, vista panorâmica, casa inteligente...",
        "btn": "GERAR ATIVOS DE MARKETING COMPLETOS",
        "upload_label": "Enviar Fotos do Imóvel",
        "result": "Pré-visualização Executiva",
        "loading": "Preparando seu ecossistema de marketing...",
        "empty": "Aguardando imagens para análise. Envie fotos e preencha os detalhes à esquerda.",
        "download": "Exportar Secção (TXT)",
        "download_all": "Exportar TUDO (TXT)",
        "save_btn": "Salvar Alterações",
        "saved_msg": "Salvo!",
        "error": "Erro:",
        "clear_btn": "Limpar Formulário",
        "tab_main": "Anúncio Premium",
        "tab_social": "Kit Redes Sociais",
        "tab_video": "Roteiros de Vídeo",
        "tab_tech": "Especificações",
        "tab_email": "Campanha de Email",
        "tab_seo": "SEO & Web Copy",
        "label_main": "Texto de Vendas",
        "label_social": "Conteúdo Social",
        "label_video": "Roteiro de Vídeo",
        "label_tech": "Especificações Técnicas",
        "label_email": "Campanha Email",
        "label_seo": "SEO & Web Copy",
        "photos_uploaded": "fotos carregadas",
        "pro_tip": "Dica Pro: Envie 3-6 fotos incluindo exterior, interior e características principais.",
        "extra_details": "Detalhes Adicionais",
        "marketing_config": "Configurações de Marketing",
        "interface_lang": "Idioma Interface",
        "config_section": "Configuração",
    },
    "日本語": {
        "title": "SarSa AI | 不動産インテリジェンス・プラットフォーム",
        "service_desc": "オールインワン視覚的物件インテリジェンス＆グローバル販売自動化",
        "subtitle": "物件写真をプレミアム広告、SNSキット、動画台本、技術仕様書、メールキャンペーン、SEOコピーに瞬時に変換します。",
        "settings": "設定",
        "target_lang": "作成言語...",
        "prop_type": "物件種別",
        "price": "市場価格",
        "location": "所在地",
        "tone": "マーケティング戦略",
        "tones": ["標準プロ", "ウルトラ・ラグジュアリー", "投資重視", "モダン・ミニマリスト", "ファミリー向け", "バケーションレンタル", "商業用"],
        "ph_prop": "例: 3LDKマンション、高級別荘...",
        "ph_price": "例: 8500万円 または 月20万円...",
        "ph_loc": "例: 東京都港区、ドバイマリーナ...",
        "bedrooms": "寝室数",
        "bathrooms": "浴室数",
        "area": "面積",
        "year_built": "建築年",
        "ph_beds": "例: 3",
        "ph_baths": "例: 2",
        "ph_area": "例: 185 m²",
        "ph_year": "例: 2022",
        "furnishing": "家具",
        "furnishing_opts": ["未指定", "フル家具付き", "一部家具付き", "家具なし"],
        "target_audience": "ターゲット層",
        "audience_opts": ["一般市場", "富裕層バイヤー", "投資家 & ROI重視", "海外居住者", "初めての購入者", "休暇・別荘市場", "商業テナント"],
        "custom_inst": "特記事項 ＆ アピールポイント",
        "custom_inst_ph": "例: プライベートプール、パノラマビュー、スマートホーム...",
        "btn": "完全なマーケティング資産を生成",
        "upload_label": "ここに物件写真をアップロード",
        "result": "エグゼクティブ・プレビュー",
        "loading": "プレミアム・マーケティング・エコシステムを構築中...",
        "empty": "分析用の画像を待機中。写真をアップロードし、左側に詳細を入力してください。",
        "download": "セクションを書き出し (TXT)",
        "download_all": "全セクション書き出し (TXT)",
        "save_btn": "変更を保存",
        "saved_msg": "保存完了！",
        "error": "エラー:",
        "clear_btn": "フォームをリセット",
        "tab_main": "プレミアム広告",
        "tab_social": "SNSキット",
        "tab_video": "動画台本",
        "tab_tech": "技術仕様",
        "tab_email": "メールキャンペーン",
        "tab_seo": "SEO ＆ Webコピー",
        "label_main": "セールスコピー",
        "label_social": "SNSコンテンツ",
        "label_video": "動画シナリオ",
        "label_tech": "技術詳細",
        "label_email": "メールキャンペーン",
        "label_seo": "SEOテキスト",
        "photos_uploaded": "枚の写真が読み込まれました",
        "pro_tip": "ヒント: 外観、内装、主要な特徴を含む3〜6枚の写真をアップロードすると、最高の解析結果が得られます。",
        "extra_details": "物件詳細情報",
        "marketing_config": "マーケティング設定",
        "interface_lang": "インターフェース言語",
        "config_section": "設定",
    },
    "简体中文": {
        "title": "SarSa AI | 房地产智能平台",
        "service_desc": "全方位房产视觉智能与全球销售自动化",
        "subtitle": "立即将房产照片转化为优质房源描述、社交媒体包、视频脚本、技术规格、邮件营销和 SEO 文案。",
        "settings": "配置",
        "target_lang": "编写语言...",
        "prop_type": "房产类型",
        "price": "市场价格",
        "location": "地点",
        "tone": "营销策略",
        "tones": ["标准专业", "顶级豪宅", "投资价值", "现代简约", "家庭生活", "度假租赁", "商业办公"],
        "ph_prop": "例如：3室1厅公寓、豪华别墅...",
        "ph_price": "例如：$850,000 或 $2,000/月...",
        "ph_loc": "例如：上海浦東新区、伦敦...",
        "bedrooms": "卧室",
        "bathrooms": "卫生间",
        "area": "面积",
        "year_built": "建造年份",
        "ph_beds": "例如：3",
        "ph_baths": "例如：2",
        "ph_area": "例如：185 平方米",
        "ph_year": "例如：2022",
        "furnishing": "装修情况",
        "furnishing_opts": ["未指定", "精装修（含家具）", "简装修", "毛坯房"],
        "target_audience": "目标受众",
        "audience_opts": ["大众市场", "豪宅买家", "投资者 & 投资回报", "外籍人士", "首次购房者", "度假市场", "商业租客"],
        "custom_inst": "特别备注与亮点",
        "custom_inst_ph": "例如：私人泳池、全景海景、智能家居、临近国际学校...",
        "btn": "生成完整营销资产",
        "upload_label": "在此上传房产照片",
        "result": "高级预览",
        "loading": "正在打造您的专属营销生态系统...",
        "empty": "等待照片进行专业分析。请上传照片并在左侧填写详细信息。",
        "download": "导出此部分 (TXT)",
        "download_all": "导出全部内容 (TXT)",
        "save_btn": "保存更改",
        "saved_msg": "已保存！",
        "error": "错误：",
        "clear_btn": "重置表单",
        "tab_main": "优质房源",
        "tab_social": "社媒包",
        "tab_video": "视频脚本",
        "tab_tech": "技术规格",
        "tab_email": "邮件营销",
        "tab_seo": "SEO 网页文案",
        "label_main": "销售文案",
        "label_social": "社媒内容",
        "label_video": "视频脚本",
        "label_tech": "技术规格",
        "label_email": "邮件营销",
        "label_seo": "SEO 文案",
        "photos_uploaded": "张照片已加载",
        "pro_tip": "提示：上传 3-6 张包含外观、内饰和核心特征的照片以获得最佳效果。",
        "extra_details": "额外房产细节",
        "marketing_config": "营销设置",
        "interface_lang": "界面语言",
        "config_section": "配置",
    },
    "العربية": {
        "title": "SarSa AI | منصة الذكاء العقاري",
        "service_desc": "الذكاء البصري المتكامل للعقارات وأتمتة المبيعات العالمية",
        "subtitle": "حول صور العقارات فوراً إلى إعلانات مميزة، حقائب تواصل اجتماعي، سيناريوهات فيديو، مواصفات فنية، حملات بريدية ونصوص SEO.",
        "settings": "الإعدادات",
        "target_lang": "لغة الكتابة...",
        "prop_type": "نوع العقار",
        "price": "سعر السوق",
        "location": "الموقع",
        "tone": "استراتيجية التسويق",
        "tones": ["احترافي قياسي", "فخامة فائقة", "تركيز استثماري", "عصري بسيط", "حياة عائلية", "تأجير سياحي", "تجاري"],
        "ph_prop": "مثال: شقة 3+1، فيلا فاخرة...",
        "ph_price": "مثال: 850,000$ أو 2,500$ شهرياً...",
        "ph_loc": "مثال: دبي مارينا، الرياض، القاهرة...",
        "bedrooms": "غرف النوم",
        "bathrooms": "الحمامات",
        "area": "المساحة",
        "year_built": "سنة البناء",
        "ph_beds": "مثال: 3",
        "ph_baths": "مثال: 2",
        "ph_area": "مثال: 185 م²",
        "ph_year": "مثال: 2022",
        "furnishing": "حالة التأثيث",
        "furnishing_opts": ["غير محدد", "مفروش بالكامل", "مفروش جزئياً", "غير مفروش"],
        "target_audience": "الجمهور المستهدف",
        "audience_opts": ["السوق العام", "مشتري الفخامة", "المستثمرون", "المغتربون", "مشتري لأول مرة", "سوق العطلات", "مستأجر تجاري"],
        "custom_inst": "ملاحظات خاصة ومميزات",
        "custom_inst_ph": "مثال: مسبح خاص، إطلالة بانورامية، منزل ذكي...",
        "btn": "إنشاء الأصول التسويقية الكاملة",
        "upload_label": "ضع صور العقار هنا",
        "result": "معاينة تنفيذية",
        "loading": "جاري تجهيز منظومتك التسويقية الفاخرة...",
        "empty": "في انتظار الصور لبدء التحليل المهني. ارفع الصور واملأ التفاصيل على اليسار.",
        "download": "تصدير القسم (TXT)",
        "download_all": "تصدير الكل (TXT)",
        "save_btn": "حفظ التغييرات",
        "saved_msg": "تم الحفظ!",
        "error": "خطأ:",
        "clear_btn": "إعادة تعيين",
        "tab_main": "الإعلان الرئيسي",
        "tab_social": "حقيبة التواصل",
        "tab_video": "سيناريو الفيديو",
        "tab_tech": "المواصفات الفنية",
        "tab_email": "حملة البريد",
        "tab_seo": "نصوص الويب وSEO",
        "label_main": "نص المبيعات",
        "label_social": "محتوى التواصل",
        "label_video": "سيناريو الفيديو",
        "label_tech": "المواصفات الفنية",
        "label_email": "حملة البريد الإلكتروني",
        "label_seo": "نص SEO",
        "photos_uploaded": "صور تم تحميلها",
        "pro_tip": "نصيحة: ارفع 3-6 صور تشمل التصميم الخارجي والداخلي والمميزات الرئيسية لأفضل النتائج.",
        "extra_details": "تفاصيل العقار الإضافية",
        "marketing_config": "إعدادات التسويق",
        "interface_lang": "لغة الواجهة",
        "config_section": "الإعدادات",
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
span[data-testid="stIconMaterial"] { 
    font-family: "Material Symbols Rounded", "Material Icons" !important; 
}
/* Sidebar kapatma butonunu her zaman görünür kıl */
button[kind="headerNoPadding"] {
    opacity: 1 !important;
    visibility: visible !important;
    display: block !important;
}

/* Sidebar açıkken butonun yerini sabitle ve tıklanabilirliğini koru */
section[data-testid="stSidebar"] + div + button {
    opacity: 1 !important;
}


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