import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
import json
import time
from datetime import datetime

# --- AI CONFIGURATION ---
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = 'gemini-2.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="SarSa AI | Real Estate Intelligence Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_logo(file_path):
    if os.path.exists(file_path):
        return Image.open(file_path)
    return None

# ─────────────────────────────────────────────
# LANGUAGE SYSTEM
# ─────────────────────────────────────────────
ui_languages = {
    "English": {
        "title": "SarSa AI | Real Estate Intelligence Platform",
        "service_desc": "All-in-One Visual Property Intelligence & Global Sales Automation",
        "subtitle": "Transform property photos into premium listings, social media kits, cinematic video scripts, and technical data sheets instantly.",
        "settings": "Configuration",
        "interface_lang": "🌐 Interface Language",
        "target_lang": "✍️ Write Listing In...",
        "prop_type": "Property Type",
        "price": "Market Price",
        "location": "Location",
        "tone": "Marketing Strategy",
        "bedrooms": "Bedrooms",
        "bathrooms": "Bathrooms",
        "area": "Area (sqm / sqft)",
        "year_built": "Year Built",
        "furnishing": "Furnishing",
        "furnishing_opts": ["Not Specified", "Fully Furnished", "Semi-Furnished", "Unfurnished"],
        "target_audience": "Target Audience",
        "audience_opts": ["General Market", "Luxury Buyers", "Investors", "Expats & Internationals", "First-Time Buyers", "Vacation / Holiday Market"],
        "tones": ["Standard Pro", "Ultra-Luxury", "Investment Focus", "Modern Minimalist", "Family Living", "Vacation Rental"],
        "ph_prop": "E.g., 3-Bed Luxury Villa, Studio Apartment...",
        "ph_price": "E.g., $850,000 or €2,500/month...",
        "ph_loc": "E.g., Dubai Marina, Bali, Manhattan...",
        "ph_beds": "E.g., 3",
        "ph_baths": "E.g., 2",
        "ph_area": "E.g., 185",
        "ph_year": "E.g., 2023",
        "custom_inst": "📝 Special Notes & Highlights",
        "custom_inst_ph": "E.g., Private pool, panoramic sea view, smart home system, near international school...",
        "btn": "✨ GENERATE COMPLETE MARKETING ASSETS",
        "upload_label": "📸 Drop Property Photos Here",
        "upload_hint": "JPG, PNG, WEBP, JPEG · Up to 200MB per file",
        "result": "💎 Executive Preview",
        "loading": "Crafting your premium marketing ecosystem...",
        "empty_title": "Ready to Transform Your Listing",
        "empty_sub": "Upload property photos and fill in the details on the left to generate complete marketing assets.",
        "download_all": "📥 Export All (TXT)",
        "download_tab": "📥 Export This Section",
        "copy_btn": "📋 Copy",
        "save_btn": "💾 Save Changes",
        "saved_msg": "✅ Changes saved!",
        "error": "Error:",
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
        "photos_uploaded": "photos uploaded",
        "generating": "Generating...",
        "features": ["Prime Listing", "Social Media Kit", "Cinematic Script", "Tech Specs", "Email Campaign", "SEO Copy"],
        "pro_tip": "💡 Pro Tip",
        "pro_tip_text": "Upload 3–6 photos including exterior, interior, and key features for best results.",
        "clear_btn": "🗑️ Clear All",
        "history_title": "Recent Generations",
        "no_history": "No previous generations this session.",
    },
    "Türkçe": {
        "title": "SarSa AI | Gayrimenkul Zeka Platformu",
        "service_desc": "Hepsi Bir Arada Görsel Mülk Zekası ve Küresel Satış Otomasyonu",
        "subtitle": "Mülk fotoğraflarını anında profesyonel ilanlara, sosyal medya kitlerine, sinematik video senaryolarına ve teknik şartnamelere dönüştürün.",
        "settings": "Yapılandırma",
        "interface_lang": "🌐 Arayüz Dili",
        "target_lang": "✍️ İlan Dili...",
        "prop_type": "Emlak Tipi",
        "price": "Pazar Fiyatı",
        "location": "Konum",
        "tone": "Pazarlama Stratejisi",
        "bedrooms": "Yatak Odası",
        "bathrooms": "Banyo",
        "area": "Alan (m²)",
        "year_built": "İnşaat Yılı",
        "furnishing": "Eşya Durumu",
        "furnishing_opts": ["Belirtilmedi", "Tam Eşyalı", "Yarı Eşyalı", "Eşyasız"],
        "target_audience": "Hedef Kitle",
        "audience_opts": ["Genel Pazar", "Lüks Alıcılar", "Yatırımcılar", "Yabancılar & Uluslararası", "İlk Ev Alıcıları", "Tatil / Kiralık Pazar"],
        "tones": ["Standart Profesyonel", "Ultra-Lüks", "Yatırım Odaklı", "Modern Minimalist", "Aile Yaşamı", "Tatil Kiralık"],
        "ph_prop": "Örn: 3+1 Lüks Villa, Stüdyo Daire...",
        "ph_price": "Örn: 5.000.000 TL veya $2.500/ay...",
        "ph_loc": "Örn: Beşiktaş, İstanbul...",
        "ph_beds": "Örn: 3",
        "ph_baths": "Örn: 2",
        "ph_area": "Örn: 185",
        "ph_year": "Örn: 2023",
        "custom_inst": "📝 Özel Notlar ve Öne Çıkan Özellikler",
        "custom_inst_ph": "Örn: Özel havuz, panoramik manzara, akıllı ev sistemi...",
        "btn": "✨ TÜM PAZARLAMA VARLIKLARINI OLUŞTUR",
        "upload_label": "📸 Fotoğrafları Buraya Bırakın",
        "upload_hint": "JPG, PNG, WEBP, JPEG · Dosya başına 200MB'a kadar",
        "result": "💎 Yönetici Önizlemesi",
        "loading": "Premium pazarlama ekosisteminiz hazırlanıyor...",
        "empty_title": "İlanınızı Dönüştürmeye Hazır",
        "empty_sub": "Fotoğraf yükleyin ve soldaki bilgileri doldurun.",
        "download_all": "📥 Tümünü Dışa Aktar (TXT)",
        "download_tab": "📥 Bu Bölümü Dışa Aktar",
        "copy_btn": "📋 Kopyala",
        "save_btn": "💾 Değişiklikleri Kaydet",
        "saved_msg": "✅ Kaydedildi!",
        "error": "Hata:",
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
        "label_email": "E-posta",
        "label_seo": "SEO Metni",
        "photos_uploaded": "fotoğraf yüklendi",
        "generating": "Oluşturuluyor...",
        "features": ["Ana İlan", "Sosyal Medya", "Sinematik Script", "Teknik Özellikler", "E-posta", "SEO"],
        "pro_tip": "💡 Pro İpucu",
        "pro_tip_text": "En iyi sonuç için dış mekan, iç mekan ve önemli özellikleri içeren 3-6 fotoğraf yükleyin.",
        "clear_btn": "🗑️ Temizle",
        "history_title": "Son Üretimler",
        "no_history": "Bu oturumda üretim yok.",
    },
    "Español": {
        "title": "SarSa AI | Plataforma de Inteligencia Inmobiliaria",
        "service_desc": "Inteligencia Visual de Propiedades y Automatización de Ventas Globales",
        "subtitle": "Convierta fotos en anuncios premium, kits de redes sociales, guiones de video y fichas técnicas al instante.",
        "settings": "Configuración",
        "interface_lang": "🌐 Idioma de Interfaz",
        "target_lang": "✍️ Escribir Anuncio En...",
        "prop_type": "Tipo de Propiedad",
        "price": "Precio de Mercado",
        "location": "Ubicación",
        "tone": "Estrategia de Marketing",
        "bedrooms": "Dormitorios",
        "bathrooms": "Baños",
        "area": "Área (m²)",
        "year_built": "Año de Construcción",
        "furnishing": "Amueblado",
        "furnishing_opts": ["No especificado", "Completamente Amueblado", "Semi-Amueblado", "Sin Amueblar"],
        "target_audience": "Público Objetivo",
        "audience_opts": ["Mercado General", "Compradores de Lujo", "Inversores", "Extranjeros e Internacionales", "Primeros Compradores", "Mercado Vacacional"],
        "tones": ["Profesional Estándar", "Ultra-Lujo", "Enfoque de Inversión", "Minimalista Moderno", "Vida Familiar", "Alquiler Vacacional"],
        "ph_prop": "Ej: Villa 3 Hab., Apartamento Estudio...",
        "ph_price": "Ej: $850,000 o €2,500/mes...",
        "ph_loc": "Ej: Madrid, Marbella, Miami...",
        "ph_beds": "Ej: 3",
        "ph_baths": "Ej: 2",
        "ph_area": "Ej: 185",
        "ph_year": "Ej: 2023",
        "custom_inst": "📝 Notas Especiales y Características",
        "custom_inst_ph": "Ej: Piscina privada, vistas al mar, domótica...",
        "btn": "✨ GENERAR ACTIVOS DE MARKETING COMPLETOS",
        "upload_label": "📸 Subir Fotos de la Propiedad",
        "upload_hint": "JPG, PNG, WEBP, JPEG · Hasta 200MB por archivo",
        "result": "💎 Vista Previa Ejecutiva",
        "loading": "Creando su ecosistema de marketing premium...",
        "empty_title": "Listo para Transformar su Anuncio",
        "empty_sub": "Suba fotos y complete los detalles a la izquierda.",
        "download_all": "📥 Exportar Todo (TXT)",
        "download_tab": "📥 Exportar Esta Sección",
        "copy_btn": "📋 Copiar",
        "save_btn": "💾 Guardar Cambios",
        "saved_msg": "✅ ¡Guardado!",
        "error": "Error:",
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
        "label_email": "Campaña Email",
        "label_seo": "Texto SEO",
        "photos_uploaded": "fotos subidas",
        "generating": "Generando...",
        "features": ["Anuncio Premium", "Redes Sociales", "Script Cinematico", "Especificaciones", "Email", "SEO"],
        "pro_tip": "💡 Consejo Pro",
        "pro_tip_text": "Sube 3-6 fotos incluyendo exterior, interior y características principales para mejores resultados.",
        "clear_btn": "🗑️ Limpiar Todo",
        "history_title": "Generaciones Recientes",
        "no_history": "Sin generaciones previas esta sesión.",
    },
    "Deutsch": {
        "title": "SarSa AI | Immobilien-Intelligenz-Plattform",
        "service_desc": "All-in-One Visuelle Objektintelligenz & Globale Verkaufsautomatisierung",
        "subtitle": "Verwandeln Sie Fotos sofort in Premium-Exposés, Social-Media-Kits, Videoskripte und Datenblätter.",
        "settings": "Konfiguration",
        "interface_lang": "🌐 Oberflächensprache",
        "target_lang": "✍️ Exposé-Sprache...",
        "prop_type": "Objekttyp",
        "price": "Marktpreis",
        "location": "Standort",
        "tone": "Marketingstrategie",
        "bedrooms": "Schlafzimmer",
        "bathrooms": "Badezimmer",
        "area": "Fläche (m²)",
        "year_built": "Baujahr",
        "furnishing": "Möblierung",
        "furnishing_opts": ["Nicht angegeben", "Vollmöbliert", "Teilmöbliert", "Unmöbliert"],
        "target_audience": "Zielgruppe",
        "audience_opts": ["Allgemeiner Markt", "Luxuskäufer", "Investoren", "Expats & Internationale", "Erstkäufer", "Ferienmarkt"],
        "tones": ["Standard-Profi", "Ultra-Luxus", "Investitionsfokus", "Modern-Minimalistisch", "Familienleben", "Ferienmiete"],
        "ph_prop": "Z.B. 3-Zimmer-Wohnung, Luxusvilla...",
        "ph_price": "Z.B. 850.000€ oder 2.500€/Monat...",
        "ph_loc": "Z.B. Berlin, München, Hamburg...",
        "ph_beds": "Z.B. 3",
        "ph_baths": "Z.B. 2",
        "ph_area": "Z.B. 185",
        "ph_year": "Z.B. 2023",
        "custom_inst": "📝 Notizen & Besonderheiten",
        "custom_inst_ph": "Z.B. Privatpool, Panoramasicht, Smart-Home...",
        "btn": "✨ KOMPLETTE MARKETING-ASSETS ERSTELLEN",
        "upload_label": "📸 Fotos hier hochladen",
        "upload_hint": "JPG, PNG, WEBP, JPEG · Bis 200MB pro Datei",
        "result": "💎 Executive-Vorschau",
        "loading": "Ihr Marketing-Ökosystem wird erstellt...",
        "empty_title": "Bereit zur Transformation",
        "empty_sub": "Laden Sie Fotos hoch und füllen Sie die Details aus.",
        "download_all": "📥 Alles Exportieren (TXT)",
        "download_tab": "📥 Diesen Abschnitt Exportieren",
        "copy_btn": "📋 Kopieren",
        "save_btn": "💾 Änderungen Speichern",
        "saved_msg": "✅ Gespeichert!",
        "error": "Fehler:",
        "tab_main": "Premium-Exposé",
        "tab_social": "Social-Media-Kit",
        "tab_video": "Videoskripte",
        "tab_tech": "Tech-Details",
        "tab_email": "E-Mail-Kampagne",
        "tab_seo": "SEO & Webtext",
        "label_main": "Verkaufstext",
        "label_social": "Social-Media-Content",
        "label_video": "Videoskript",
        "label_tech": "Technische Daten",
        "label_email": "E-Mail-Kampagne",
        "label_seo": "SEO-Text",
        "photos_uploaded": "Fotos hochgeladen",
        "generating": "Wird erstellt...",
        "features": ["Premium-Exposé", "Social Media", "Kino-Skript", "Tech-Details", "E-Mail", "SEO"],
        "pro_tip": "💡 Profi-Tipp",
        "pro_tip_text": "Laden Sie 3-6 Fotos mit Außenansicht, Innenräumen und Besonderheiten für beste Ergebnisse hoch.",
        "clear_btn": "🗑️ Alles Löschen",
        "history_title": "Letzte Erstellungen",
        "no_history": "Keine Erstellungen in dieser Sitzung.",
    },
    "Français": {
        "title": "SarSa AI | Plateforme d'Intelligence Immobilière",
        "service_desc": "Intelligence Visuelle Immobilière et Automatisation des Ventes Globales",
        "subtitle": "Transformez vos photos en annonces premium, kits réseaux sociaux, scripts vidéo et fiches techniques instantanément.",
        "settings": "Configuration",
        "interface_lang": "🌐 Langue de l'Interface",
        "target_lang": "✍️ Rédiger en...",
        "prop_type": "Type de Bien",
        "price": "Prix du Marché",
        "location": "Localisation",
        "tone": "Stratégie Marketing",
        "bedrooms": "Chambres",
        "bathrooms": "Salles de Bain",
        "area": "Surface (m²)",
        "year_built": "Année de Construction",
        "furnishing": "Ameublement",
        "furnishing_opts": ["Non spécifié", "Entièrement Meublé", "Semi-Meublé", "Non Meublé"],
        "target_audience": "Audience Cible",
        "audience_opts": ["Marché Général", "Acheteurs de Luxe", "Investisseurs", "Expatriés & Internationaux", "Primo-Accédants", "Marché Vacances"],
        "tones": ["Standard Pro", "Ultra-Luxe", "Focus Investissement", "Minimaliste Moderne", "Vie de Famille", "Location Saisonnière"],
        "ph_prop": "Ex: Villa 3 Ch., Appartement Studio...",
        "ph_price": "Ex: 850.000€ ou 2.500€/mois...",
        "ph_loc": "Ex: Paris, Côte d'Azur, Monaco...",
        "ph_beds": "Ex: 3",
        "ph_baths": "Ex: 2",
        "ph_area": "Ex: 185",
        "ph_year": "Ex: 2023",
        "custom_inst": "📝 Notes Spéciales & Points Forts",
        "custom_inst_ph": "Ex: Piscine privée, vue panoramique, domotique...",
        "btn": "✨ GÉNÉRER LES ACTIFS MARKETING COMPLETS",
        "upload_label": "📸 Déposer les Photos Ici",
        "upload_hint": "JPG, PNG, WEBP, JPEG · Jusqu'à 200MB par fichier",
        "result": "💎 Aperçu Exécutif",
        "loading": "Préparation de votre écosystème marketing premium...",
        "empty_title": "Prêt à Transformer Votre Annonce",
        "empty_sub": "Téléchargez des photos et remplissez les détails à gauche.",
        "download_all": "📥 Exporter Tout (TXT)",
        "download_tab": "📥 Exporter Cette Section",
        "copy_btn": "📋 Copier",
        "save_btn": "💾 Enregistrer",
        "saved_msg": "✅ Enregistré !",
        "error": "Erreur :",
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
        "label_seo": "Texte SEO",
        "photos_uploaded": "photos téléchargées",
        "generating": "Génération en cours...",
        "features": ["Annonce Premium", "Réseaux Sociaux", "Script Cinéma", "Spécifications", "Email", "SEO"],
        "pro_tip": "💡 Conseil Pro",
        "pro_tip_text": "Téléchargez 3 à 6 photos incluant l'extérieur, l'intérieur et les atouts pour de meilleurs résultats.",
        "clear_btn": "🗑️ Tout Effacer",
        "history_title": "Générations Récentes",
        "no_history": "Aucune génération dans cette session.",
    },
    "Português": {
        "title": "SarSa AI | Plataforma de Inteligência Imobiliária",
        "service_desc": "Inteligência Visual Imobiliária e Automação de Vendas Globais",
        "subtitle": "Transforme fotos em anúncios premium, kits de redes sociais, roteiros de vídeo e fichas técnicas instantaneamente.",
        "settings": "Configuração",
        "interface_lang": "🌐 Idioma da Interface",
        "target_lang": "✍️ Escrever Anúncio Em...",
        "prop_type": "Tipo de Imóvel",
        "price": "Preço de Mercado",
        "location": "Localização",
        "tone": "Estratégia de Marketing",
        "bedrooms": "Quartos",
        "bathrooms": "Banheiros",
        "area": "Área (m²)",
        "year_built": "Ano de Construção",
        "furnishing": "Mobiliário",
        "furnishing_opts": ["Não especificado", "Completamente Mobilado", "Semi-Mobilado", "Sem Mobília"],
        "target_audience": "Público-Alvo",
        "audience_opts": ["Mercado Geral", "Compradores de Luxo", "Investidores", "Expats e Internacionais", "Primeiros Compradores", "Mercado de Férias"],
        "tones": ["Profissional Padrão", "Ultra-Luxo", "Foco em Investimento", "Minimalista Moderno", "Vida Familiar", "Aluguel de Temporada"],
        "ph_prop": "Ex: Villa 3 quartos, Apartamento Studio...",
        "ph_price": "Ex: R$2.500.000 ou €2.500/mês...",
        "ph_loc": "Ex: Lisboa, Algarve, São Paulo...",
        "ph_beds": "Ex: 3",
        "ph_baths": "Ex: 2",
        "ph_area": "Ex: 185",
        "ph_year": "Ex: 2023",
        "custom_inst": "📝 Notas Especiais e Destaques",
        "custom_inst_ph": "Ex: Piscina privativa, vista panorâmica, casa inteligente...",
        "btn": "✨ GERAR ATIVOS DE MARKETING COMPLETOS",
        "upload_label": "📸 Enviar Fotos do Imóvel",
        "upload_hint": "JPG, PNG, WEBP, JPEG · Até 200MB por arquivo",
        "result": "💎 Pré-visualização Executiva",
        "loading": "Preparando seu ecossistema de marketing premium...",
        "empty_title": "Pronto para Transformar seu Anúncio",
        "empty_sub": "Faça upload das fotos e preencha os detalhes à esquerda.",
        "download_all": "📥 Exportar Tudo (TXT)",
        "download_tab": "📥 Exportar Esta Seção",
        "copy_btn": "📋 Copiar",
        "save_btn": "💾 Salvar Alterações",
        "saved_msg": "✅ Salvo!",
        "error": "Erro:",
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
        "label_seo": "Texto SEO",
        "photos_uploaded": "fotos enviadas",
        "generating": "Gerando...",
        "features": ["Anúncio Premium", "Redes Sociais", "Script Cinemático", "Especificações", "Email", "SEO"],
        "pro_tip": "💡 Dica Pro",
        "pro_tip_text": "Envie 3 a 6 fotos incluindo exterior, interior e características principais para melhores resultados.",
        "clear_btn": "🗑️ Limpar Tudo",
        "history_title": "Gerações Recentes",
        "no_history": "Sem gerações anteriores nesta sessão.",
    },
    "日本語": {
        "title": "SarSa AI | 不動産インテリジェンス・プラットフォーム",
        "service_desc": "オールインワン物件インテリジェンス＆グローバル販売自動化",
        "subtitle": "物件写真をプレミアム広告、SNSキット、動画台本、技術仕様書に瞬時に変換。",
        "settings": "設定",
        "interface_lang": "🌐 インターフェース言語",
        "target_lang": "✍️ 作成言語...",
        "prop_type": "物件種別",
        "price": "市場価格",
        "location": "所在地",
        "tone": "マーケティング戦略",
        "bedrooms": "寝室数",
        "bathrooms": "浴室数",
        "area": "面積（㎡）",
        "year_built": "建築年",
        "furnishing": "家具",
        "furnishing_opts": ["未指定", "フル家具付", "半家具付", "家具なし"],
        "target_audience": "ターゲット層",
        "audience_opts": ["一般市場", "富裕層バイヤー", "投資家", "外国人・海外在住", "初購入者", "バケーション市場"],
        "tones": ["スタンダードプロ", "ウルトララグジュアリー", "投資重視", "モダンミニマリスト", "ファミリー向け", "バケーションレンタル"],
        "ph_prop": "例：3LDKマンション、高級別荘...",
        "ph_price": "例：5000万円、月20万円...",
        "ph_loc": "例：東京都港区...",
        "ph_beds": "例：3",
        "ph_baths": "例：2",
        "ph_area": "例：185",
        "ph_year": "例：2023",
        "custom_inst": "📝 特記事項・アピールポイント",
        "custom_inst_ph": "例：プライベートプール、パノラマビュー、スマートホーム...",
        "btn": "✨ 完全なマーケティング資産を生成",
        "upload_label": "📸 ここに写真をアップロード",
        "upload_hint": "JPG, PNG, WEBP, JPEG · ファイルあたり200MBまで",
        "result": "💎 エグゼクティブプレビュー",
        "loading": "マーケティングエコシステムを構築中...",
        "empty_title": "物件掲載を最高品質へ",
        "empty_sub": "写真をアップロードして左側の詳細情報を入力してください。",
        "download_all": "📥 すべて出力（TXT）",
        "download_tab": "📥 このセクションを出力",
        "copy_btn": "📋 コピー",
        "save_btn": "💾 変更を保存",
        "saved_msg": "✅ 保存完了！",
        "error": "エラー:",
        "tab_main": "プレミアム広告",
        "tab_social": "SNSキット",
        "tab_video": "動画台本",
        "tab_tech": "技術仕様",
        "tab_email": "メールキャンペーン",
        "tab_seo": "SEO・Webコピー",
        "label_main": "セールスコピー",
        "label_social": "SNSコンテンツ",
        "label_video": "動画台本",
        "label_tech": "技術仕様",
        "label_email": "メールキャンペーン",
        "label_seo": "SEOテキスト",
        "photos_uploaded": "枚の写真アップロード済",
        "generating": "生成中...",
        "features": ["プレミアム広告", "SNS", "シネマスクリプト", "技術仕様", "メール", "SEO"],
        "pro_tip": "💡 プロヒント",
        "pro_tip_text": "外観・内観・特徴を含む3〜6枚の写真をアップロードすると最良の結果が得られます。",
        "clear_btn": "🗑️ すべて削除",
        "history_title": "最近の生成",
        "no_history": "このセッションに生成はありません。",
    },
    "中文 (简体)": {
        "title": "SarSa AI | 房地产智能平台",
        "service_desc": "全方位房产视觉智能与全球销售自动化",
        "subtitle": "立即将房产照片转化为优质房源描述、社交媒体包、电影级视频脚本和技术规格。",
        "settings": "配置",
        "interface_lang": "🌐 界面语言",
        "target_lang": "✍️ 编写语言...",
        "prop_type": "房产类型",
        "price": "市场价格",
        "location": "地点",
        "tone": "营销策略",
        "bedrooms": "卧室",
        "bathrooms": "浴室",
        "area": "面积（㎡）",
        "year_built": "建造年份",
        "furnishing": "装修情况",
        "furnishing_opts": ["未指定", "全装修", "半装修", "毛坯"],
        "target_audience": "目标受众",
        "audience_opts": ["大众市场", "豪华买家", "投资者", "外籍人士和国际买家", "首次购房者", "度假市场"],
        "tones": ["标准专业", "顶奢豪宅", "投资潜力", "现代简约", "家庭生活", "度假租赁"],
        "ph_prop": "例如：3居室公寓，豪华别墅...",
        "ph_price": "例如：¥5,000,000 或 $2,000/月...",
        "ph_loc": "例如：上海市浦东新区...",
        "ph_beds": "例如：3",
        "ph_baths": "例如：2",
        "ph_area": "例如：185",
        "ph_year": "例如：2023",
        "custom_inst": "📝 特别备注和亮点",
        "custom_inst_ph": "例如：私人泳池、全景视野、智能家居系统...",
        "btn": "✨ 生成完整营销资产",
        "upload_label": "📸 在此处上传房产照片",
        "upload_hint": "JPG、PNG、WEBP、JPEG · 每个文件最大200MB",
        "result": "💎 高管预览",
        "loading": "正在打造您的高端营销生态系统...",
        "empty_title": "准备好提升您的房源",
        "empty_sub": "上传房产照片并填写左侧的详细信息。",
        "download_all": "📥 导出全部（TXT）",
        "download_tab": "📥 导出此部分",
        "copy_btn": "📋 复制",
        "save_btn": "💾 保存更改",
        "saved_msg": "✅ 已保存！",
        "error": "错误:",
        "tab_main": "优质房源",
        "tab_social": "社交媒体包",
        "tab_video": "视频脚本",
        "tab_tech": "技术细节",
        "tab_email": "电子邮件活动",
        "tab_seo": "SEO和网络文案",
        "label_main": "销售文案",
        "label_social": "社媒内容",
        "label_video": "视频脚本",
        "label_tech": "技术规格",
        "label_email": "电子邮件活动",
        "label_seo": "SEO文案",
        "photos_uploaded": "张照片已上传",
        "generating": "生成中...",
        "features": ["优质房源", "社交媒体", "电影脚本", "技术规格", "电子邮件", "SEO"],
        "pro_tip": "💡 专业提示",
        "pro_tip_text": "上传3-6张包括外观、内部和主要特征的照片以获得最佳效果。",
        "clear_btn": "🗑️ 清除全部",
        "history_title": "最近生成",
        "no_history": "本次会话没有之前的生成。",
    },
    "العربية": {
        "title": "SarSa AI | منصة الذكاء العقاري",
        "service_desc": "ذكاء العقارات البصري المتكامل وأتمتة المبيعات العالمية",
        "subtitle": "حوّل صور العقارات إلى إعلانات مميزة، باقات تواصل اجتماعي، سيناريوهات فيديو، ومواصفات فنية فوراً.",
        "settings": "الإعدادات",
        "interface_lang": "🌐 لغة الواجهة",
        "target_lang": "✍️ لغة كتابة الإعلان...",
        "prop_type": "نوع العقار",
        "price": "سعر السوق",
        "location": "الموقع",
        "tone": "استراتيجية التسويق",
        "bedrooms": "غرف النوم",
        "bathrooms": "الحمامات",
        "area": "المساحة (م²)",
        "year_built": "سنة البناء",
        "furnishing": "التأثيث",
        "furnishing_opts": ["غير محدد", "مفروش بالكامل", "مفروش جزئياً", "غير مفروش"],
        "target_audience": "الجمهور المستهدف",
        "audience_opts": ["السوق العام", "مشترو الفخامة", "المستثمرون", "المغتربون والدوليون", "المشترون الأوائل", "سوق العطلات"],
        "tones": ["احترافي قياسي", "فخامة فائقة", "تركيز الاستثمار", "عصري بسيط", "الحياة العائلية", "الإيجار الموسمي"],
        "ph_prop": "مثال: فيلا 3 غرف، شقة استوديو...",
        "ph_price": "مثال: $850,000 أو $2,500 شهرياً...",
        "ph_loc": "مثال: دبي، الرياض، أبوظبي...",
        "ph_beds": "مثال: 3",
        "ph_baths": "مثال: 2",
        "ph_area": "مثال: 185",
        "ph_year": "مثال: 2023",
        "custom_inst": "📝 ملاحظات خاصة ومميزات",
        "custom_inst_ph": "مثال: مسبح خاص، إطلالة بانورامية، نظام المنزل الذكي...",
        "btn": "✨ إنشاء أصول تسويقية متكاملة",
        "upload_label": "📸 ضع صور العقار هنا",
        "upload_hint": "JPG, PNG, WEBP, JPEG · حتى 200MB لكل ملف",
        "result": "💎 معاينة تنفيذية",
        "loading": "جاري تجهيز منظومتك التسويقية الفاخرة...",
        "empty_title": "جاهز لتحويل إعلانك",
        "empty_sub": "ارفع الصور واملأ التفاصيل على اليسار.",
        "download_all": "📥 تصدير الكل (TXT)",
        "download_tab": "📥 تصدير هذا القسم",
        "copy_btn": "📋 نسخ",
        "save_btn": "💾 حفظ التغييرات",
        "saved_msg": "✅ تم الحفظ!",
        "error": "خطأ:",
        "tab_main": "إعلان مميز",
        "tab_social": "باقة التواصل الاجتماعي",
        "tab_video": "سيناريوهات الفيديو",
        "tab_tech": "تفاصيل تقنية",
        "tab_email": "حملة بريد إلكتروني",
        "tab_seo": "SEO ونص الويب",
        "label_main": "نص المبيعات",
        "label_social": "محتوى التواصل",
        "label_video": "سيناريو الفيديو",
        "label_tech": "المواصفات الفنية",
        "label_email": "حملة البريد",
        "label_seo": "نص SEO",
        "photos_uploaded": "صور مرفوعة",
        "generating": "جاري الإنشاء...",
        "features": ["إعلان مميز", "تواصل اجتماعي", "سكريبت سينمائي", "مواصفات تقنية", "بريد إلكتروني", "SEO"],
        "pro_tip": "💡 نصيحة احترافية",
        "pro_tip_text": "ارفع 3-6 صور تتضمن الخارج والداخل والمميزات الرئيسية للحصول على أفضل النتائج.",
        "clear_btn": "🗑️ مسح الكل",
        "history_title": "الإنشاءات الأخيرة",
        "no_history": "لا توجد إنشاءات سابقة في هذه الجلسة.",
    }
}

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "generated_content": "",
    "prop_type": "",
    "price": "",
    "location": "",
    "tone": "",
    "custom_inst": "",
    "target_lang_input": "English",
    "bedrooms": "",
    "bathrooms": "",
    "area": "",
    "year_built": "",
    "furnishing_idx": 0,
    "audience_idx": 0,
    "generation_history": [],
    "is_generating": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────
# MASTER CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* ── GLOBAL ── */
html, body, [class*="st-"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #f0f4f8 !important;
}
h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
    font-family: 'Sora', sans-serif !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stInputInstructions"] { display: none !important; }
.stDeployButton { display: none !important; }
span[data-testid="stIconMaterial"] { display: none !important; }

/* ── MAIN CONTAINER ── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
    background: transparent !important;
}
.main .block-container {
    padding: 0 !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    box-shadow: 4px 0 20px rgba(0,0,0,0.04) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1.2rem 2rem !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stTextArea label,
[data-testid="stSidebar"] .stSelectbox > label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea,
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: #f8fafc !important;
    font-size: 0.88rem !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stTextArea textarea:focus {
    border-color: #3b82f6 !important;
    background: #ffffff !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}

/* ── SIDEBAR SECTION HEADER ── */
.sidebar-section {
    font-family: 'Sora', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    color: #1e293b;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 1.2rem 0 0.6rem 0;
    padding: 0.5rem 0;
    border-bottom: 2px solid #f1f5f9;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── MAIN HEADER ── */
.sarsa-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
    padding: 2.5rem 3rem;
    position: relative;
    overflow: hidden;
}
.sarsa-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.sarsa-header::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: 10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.sarsa-title {
    font-family: 'Sora', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.5px;
}
.sarsa-subtitle-tag {
    display: inline-block;
    background: rgba(59,130,246,0.25);
    color: #93c5fd;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid rgba(59,130,246,0.3);
    margin-bottom: 0.7rem;
}
.sarsa-desc {
    color: #94a3b8;
    font-size: 0.95rem;
    max-width: 600px;
    line-height: 1.6;
    font-weight: 400;
}
.sarsa-features {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 1.2rem;
}
.sarsa-feature-chip {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    color: #e2e8f0;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 20px;
    backdrop-filter: blur(10px);
}

/* ── CONTENT WRAPPER ── */
.content-wrapper {
    padding: 2rem 2.5rem;
}

/* ── UPLOAD ZONE ── */
[data-testid="stFileUploader"] {
    border-radius: 16px !important;
    border: 2px dashed #cbd5e1 !important;
    background: #ffffff !important;
    padding: 1.5rem !important;
    transition: all 0.3s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #3b82f6 !important;
    background: #f0f7ff !important;
}
[data-testid="stFileUploader"] label {
    font-weight: 700 !important;
    color: #1e293b !important;
    font-size: 1rem !important;
    font-family: 'Sora', sans-serif !important;
}
[data-testid="stFileUploader"] small {
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
}

/* ── IMAGE GALLERY ── */
.gallery-wrapper {
    background: #ffffff;
    border-radius: 16px;
    padding: 1rem;
    border: 1px solid #e2e8f0;
    margin-top: 1rem;
}
.gallery-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #dbeafe;
    color: #1d4ed8;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 0.8rem;
}

/* ── GENERATE BUTTON ── */
.stButton > button {
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.5px !important;
    background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem 2rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.35) !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(59,130,246,0.45) !important;
    background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] > button {
    background: #f8fafc !important;
    color: #334155 !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    box-shadow: none !important;
    padding: 0.6rem 1.2rem !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #f1f5f9 !important;
    border-color: #3b82f6 !important;
    color: #1d4ed8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(59,130,246,0.15) !important;
}

/* ── RESULT PANEL ── */
.result-panel {
    background: #ffffff;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    overflow: hidden;
    margin-top: 1.5rem;
}
.result-panel-header {
    background: linear-gradient(90deg, #0f172a 0%, #1e3a5f 100%);
    padding: 1.2rem 1.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.result-panel-title {
    font-family: 'Sora', sans-serif;
    color: #ffffff;
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0;
}
.result-panel-subtitle {
    color: #94a3b8;
    font-size: 0.8rem;
    margin-top: 2px;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f8fafc !important;
    border-radius: 0 !important;
    border-bottom: 1px solid #e2e8f0 !important;
    padding: 0 1.8rem !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    color: #64748b !important;
    padding: 0.9rem 1.2rem !important;
    border-bottom: 3px solid transparent !important;
    background: transparent !important;
    border-radius: 0 !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #1d4ed8 !important;
    background: rgba(59,130,246,0.05) !important;
}
.stTabs [aria-selected="true"] {
    color: #1d4ed8 !important;
    border-bottom: 3px solid #1d4ed8 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 1.5rem 1.8rem !important;
}

/* ── TEXT AREAS ── */
.stTextArea textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    line-height: 1.7 !important;
    border-radius: 12px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: #fafbfc !important;
    color: #1e293b !important;
    padding: 1rem !important;
    resize: vertical !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: #3b82f6 !important;
    background: #fff !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}
.stTextArea label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    color: #64748b !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}

/* ── INFO / WARNING / SUCCESS BOXES ── */
.stInfo, .stSuccess, .stWarning {
    border-radius: 12px !important;
}

/* ── EMPTY STATE ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #94a3b8;
}
.empty-state-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    opacity: 0.6;
}
.empty-state-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #475569;
    margin-bottom: 0.5rem;
}
.empty-state-sub {
    font-size: 0.9rem;
    color: #94a3b8;
    max-width: 400px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── STATS BAR ── */
.stats-bar {
    display: flex;
    gap: 1.5rem;
    padding: 1rem 1.8rem;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    flex-wrap: wrap;
}
.stat-item {
    text-align: center;
}
.stat-number {
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #1d4ed8;
}
.stat-label {
    font-size: 0.7rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── PRO TIP ── */
.pro-tip-box {
    background: linear-gradient(135deg, #eff6ff, #f0fdf4);
    border: 1px solid #bfdbfe;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    margin-top: 0.8rem;
    font-size: 0.82rem;
    color: #1e40af;
    line-height: 1.5;
}

/* ── PHOTO COUNTER BADGE ── */
.photo-badge {
    display: inline-flex;
    align-items: center;
    background: #1d4ed8;
    color: white;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 700;
    gap: 4px;
}

/* ── GENERATION PROGRESS ── */
.gen-progress {
    background: linear-gradient(90deg, #dbeafe, #ede9fe);
    border: 1px solid #bfdbfe;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    color: #1e40af;
    font-weight: 600;
    font-size: 0.95rem;
}

/* ── SPINNER OVERRIDE ── */
.stSpinner > div {
    border-top-color: #3b82f6 !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 3px; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ── CURSOR FIXES ── */
button, [data-baseweb="tab"], [data-testid="stFileUploader"],
div[data-baseweb="select"], .stSelectbox div, .stDownloadButton {
    cursor: pointer !important;
}

/* ── METRIC CARDS ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1rem;
    text-align: center;
}
.metric-card-value {
    font-family: 'Sora', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: #0f172a;
}
.metric-card-label {
    font-size: 0.72rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    logo_img = load_logo("SarSa_Logo_Transparent.png")
    if logo_img:
        st.image(logo_img, use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0 0.5rem 0;">
          <div style="font-family:'Sora',sans-serif; font-size:1.6rem; font-weight:800;
                      background:linear-gradient(135deg,#3b82f6,#8b5cf6); -webkit-background-clip:text;
                      -webkit-text-fill-color:transparent;">SarSa AI</div>
          <div style="font-size:0.7rem; color:#94a3b8; letter-spacing:2px; text-transform:uppercase;">Real Estate Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Interface language at top
    current_ui_lang = st.selectbox(
        "🌐 Interface Language",
        list(ui_languages.keys()),
        index=0,
        key="ui_lang_select"
    )
    t = ui_languages[current_ui_lang]

    st.markdown("---")

    # ── LISTING LANGUAGE ──
    st.markdown(f'<div class="sidebar-section">📝 Output Language</div>', unsafe_allow_html=True)
    st.session_state.target_lang_input = st.text_input(
        t["target_lang"],
        value=st.session_state.target_lang_input,
        label_visibility="collapsed",
        placeholder="E.g., English, Français, Español, 日本語..."
    )

    # ── PROPERTY DETAILS ──
    st.markdown(f'<div class="sidebar-section">🏠 Property Details</div>', unsafe_allow_html=True)

    st.session_state.prop_type = st.text_input(
        t["prop_type"],
        value=st.session_state.prop_type,
        placeholder=t["ph_prop"]
    )
    st.session_state.price = st.text_input(
        t["price"],
        value=st.session_state.price,
        placeholder=t["ph_price"]
    )
    st.session_state.location = st.text_input(
        t["location"],
        value=st.session_state.location,
        placeholder=t["ph_loc"]
    )

    col_b, col_ba = st.columns(2)
    with col_b:
        st.session_state.bedrooms = st.text_input(
            t["bedrooms"],
            value=st.session_state.bedrooms,
            placeholder=t["ph_beds"]
        )
    with col_ba:
        st.session_state.bathrooms = st.text_input(
            t["bathrooms"],
            value=st.session_state.bathrooms,
            placeholder=t["ph_baths"]
        )

    col_a, col_y = st.columns(2)
    with col_a:
        st.session_state.area = st.text_input(
            t["area"],
            value=st.session_state.area,
            placeholder=t["ph_area"]
        )
    with col_y:
        st.session_state.year_built = st.text_input(
            t["year_built"],
            value=st.session_state.year_built,
            placeholder=t["ph_year"]
        )

    furnishing_sel = st.selectbox(
        t["furnishing"],
        t["furnishing_opts"],
        index=st.session_state.furnishing_idx
    )
    st.session_state.furnishing_idx = t["furnishing_opts"].index(furnishing_sel)

    # ── MARKETING SETTINGS ──
    st.markdown(f'<div class="sidebar-section">🎯 Marketing Settings</div>', unsafe_allow_html=True)

    current_tone_idx = t["tones"].index(st.session_state.tone) if st.session_state.tone in t["tones"] else 0
    st.session_state.tone = st.selectbox(
        t["tone"],
        t["tones"],
        index=current_tone_idx
    )

    audience_sel = st.selectbox(
        t["target_audience"],
        t["audience_opts"],
        index=st.session_state.audience_idx
    )
    st.session_state.audience_idx = t["audience_opts"].index(audience_sel)

    # ── SPECIAL NOTES ──
    st.markdown(f'<div class="sidebar-section">✨ Extra Details</div>', unsafe_allow_html=True)
    st.session_state.custom_inst = st.text_area(
        t["custom_inst"],
        value=st.session_state.custom_inst,
        placeholder=t["custom_inst_ph"],
        height=110,
        label_visibility="collapsed"
    )

    # Pro tip
    st.markdown(f"""
    <div class="pro-tip-box">
        {t['pro_tip']}: {t['pro_tip_text']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Clear all button
    if st.button(t["clear_btn"], use_container_width=True):
        for key in ["generated_content", "prop_type", "price", "location", "custom_inst",
                    "bedrooms", "bathrooms", "area", "year_built"]:
            st.session_state[key] = ""
        st.session_state.furnishing_idx = 0
        st.session_state.audience_idx = 0
        st.rerun()


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
t = ui_languages[st.session_state.get("ui_lang_select", "English")]

# ── HEADER ──
feature_chips = "".join([
    f'<span class="sarsa-feature-chip">✓ {f}</span>'
    for f in t["features"]
])

st.markdown(f"""
<div class="sarsa-header">
    <div style="position:relative; z-index:1;">
        <div class="sarsa-subtitle-tag">AI-POWERED · REAL ESTATE</div>
        <h1 class="sarsa-title">🏢 {t['title']}</h1>
        <p class="sarsa-desc">{t['subtitle']}</p>
        <div class="sarsa-features">{feature_chips}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CONTENT AREA ──
st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

# ── FILE UPLOADER ──
uploaded_files = st.file_uploader(
    t["upload_label"],
    type=["jpg", "png", "webp", "jpeg"],
    accept_multiple_files=True,
    help=t["upload_hint"]
)

if uploaded_files:
    # Photo gallery
    n = len(uploaded_files)
    images_for_ai = [Image.open(f) for f in uploaded_files]

    st.markdown(f"""
    <div class="gallery-wrapper">
        <div class="gallery-badge">📷 <span>{n} {t['photos_uploaded']}</span></div>
    </div>
    """, unsafe_allow_html=True)

    cols_per_row = min(n, 5)
    cols = st.columns(cols_per_row)
    for i, img in enumerate(images_for_ai):
        with cols[i % cols_per_row]:
            st.image(img, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── GENERATE BUTTON ──
    gen_btn = st.button(t["btn"], use_container_width=True)

    if gen_btn:
        # Build context string
        prop_details = []
        if st.session_state.prop_type:
            prop_details.append(f"Property Type: {st.session_state.prop_type}")
        if st.session_state.location:
            prop_details.append(f"Location: {st.session_state.location}")
        if st.session_state.price:
            prop_details.append(f"Price: {st.session_state.price}")
        if st.session_state.bedrooms:
            prop_details.append(f"Bedrooms: {st.session_state.bedrooms}")
        if st.session_state.bathrooms:
            prop_details.append(f"Bathrooms: {st.session_state.bathrooms}")
        if st.session_state.area:
            prop_details.append(f"Area: {st.session_state.area}")
        if st.session_state.year_built:
            prop_details.append(f"Year Built: {st.session_state.year_built}")
        if furnishing_sel and furnishing_sel != t["furnishing_opts"][0]:
            prop_details.append(f"Furnishing: {furnishing_sel}")
        if audience_sel and audience_sel != t["audience_opts"][0]:
            prop_details.append(f"Target Audience: {audience_sel}")
        if st.session_state.custom_inst:
            prop_details.append(f"Special Features: {st.session_state.custom_inst}")

        prop_context = "\n".join(prop_details) if prop_details else "Property details to be determined from images"

        expert_prompt = f"""You are a world-class Senior Real Estate Strategist and Marketing Expert for SarSa AI — a global property intelligence platform used by elite real estate agents worldwide.

OUTPUT LANGUAGE: {st.session_state.target_lang_input}. Write ALL output content in this language only.

PROPERTY INFORMATION:
{prop_context}
Marketing Strategy: {st.session_state.tone}

CRITICAL INSTRUCTIONS:
- Analyze the uploaded property photos deeply and extract ALL visible features, architectural details, quality indicators, finishes, and selling points
- Write with extreme professionalism and emotional intelligence appropriate for the target market
- Every section must be complete, detailed, and immediately usable by a real estate professional
- Output exactly in the section format below — no extra commentary

## SECTION_1 — PRIME LISTING (Sales Copy)
[Write a compelling, emotionally resonant property listing. Include:
• Powerful headline
• 3-4 paragraph narrative description with vivid language that paints a lifestyle picture
• Bullet-pointed key features list (min. 10 items)
• Neighborhood/area highlights
• Investment or lifestyle value proposition
• Professional closing statement with call-to-action
Minimum 600 words]

## SECTION_2 — SOCIAL MEDIA KIT
[Create platform-optimized content:
• INSTAGRAM (3 posts) - Each with visual direction, caption (150-200 words), and 20+ targeted hashtags
• FACEBOOK (2 posts) - Longer community-focused posts (200-250 words each)
• LINKEDIN (1 post) - Professional investment-angle post (200 words)
• TWITTER/X (3 tweets) - Punchy, engaging, each under 280 characters
• TIKTOK/REELS (1 video hook) - Opening 3-second hook + 15-second script]

## SECTION_3 — CINEMATIC VIDEO SCRIPT
[Create a complete professional video script:
• Title & Production Notes (duration, music mood, voiceover style)
• Shot-by-shot breakdown with VISUAL description + VOICEOVER text for each shot
• Min. 8 scenes covering: drone exterior, entrance, key rooms, outdoor areas, neighborhood, lifestyle ending
• Music direction and pacing notes
• Total script: 1:30–2:30 minute runtime
Minimum 500 words]

## SECTION_4 — TECHNICAL SPECIFICATIONS
[Comprehensive property data sheet:
• Full property specifications table (type, size, rooms, year, etc.)
• Construction & materials analysis (based on visible features in photos)
• Smart home & technology features
• Energy efficiency notes
• Nearby amenities & infrastructure
• Legal & ownership notes (general)
• Investment metrics (if applicable: rental yield estimate, market comparables notes)
• Viewing & contact instructions template]

## SECTION_5 — EMAIL CAMPAIGN
[Create 2 professional email templates:
EMAIL 1 - "New Listing Alert" (for subscriber list): Subject line + full body (300 words)
EMAIL 2 - "Personal Introduction" (for individual prospect): Subject line + full body (250 words)
Both should have professional structure: greeting, property intro, key highlights, CTA, signature block]

## SECTION_6 — SEO & WEB COPY
[Digital marketing content:
• SEO-optimized webpage title and meta description (160 chars)
• 5 targeted keywords with search intent analysis
• H1, H2, H3 heading structure suggestion
• 400-word SEO web description (naturally incorporating keywords)
• Google Ads headline suggestions (5 headlines, 30 chars each)
• Google Ads description (2 versions, 90 chars each)
• Schema markup property type suggestion]"""

        with st.spinner(t["loading"]):
            try:
                response = model.generate_content([expert_prompt] + images_for_ai)
                st.session_state.generated_content = response.text
                # Save to history
                hist_entry = {
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "prop_type": st.session_state.prop_type or "Property",
                    "location": st.session_state.location or "—",
                }
                st.session_state.generation_history.insert(0, hist_entry)
                if len(st.session_state.generation_history) > 5:
                    st.session_state.generation_history = st.session_state.generation_history[:5]
                st.rerun()
            except Exception as e:
                st.error(f"{t['error']} {str(e)}")

    # ── RESULTS ──
    if st.session_state.generated_content:
        raw = st.session_state.generated_content
        sections = {}
        parts = raw.split("##")
        for p in parts:
            p = p.strip()
            for i in range(1, 7):
                key = f"SECTION_{i}"
                if p.startswith(key):
                    content = p[len(key):].strip()
                    if content.startswith("—"):
                        content = content[1:].strip()
                    content = content.lstrip("-–— \n")
                    sections[i] = content
                    break

        def get_sec(n):
            return sections.get(n, "")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prop_slug = (st.session_state.prop_type or "property").replace(" ", "_")[:20].lower()
        filename = f"sarsa_ai_{prop_slug}_{timestamp}.txt"

        all_export = f"""SARSA AI — COMPLETE MARKETING ASSETS
Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}
Property: {st.session_state.prop_type or 'N/A'}
Location: {st.session_state.location or 'N/A'}
Language: {st.session_state.target_lang_input}
Strategy: {st.session_state.tone}
{'='*60}

PRIME LISTING
{'='*60}
{get_sec(1)}

SOCIAL MEDIA KIT
{'='*60}
{get_sec(2)}

VIDEO SCRIPT
{'='*60}
{get_sec(3)}

TECHNICAL SPECIFICATIONS
{'='*60}
{get_sec(4)}

EMAIL CAMPAIGN
{'='*60}
{get_sec(5)}

SEO & WEB COPY
{'='*60}
{get_sec(6)}
"""

        st.markdown(f"""
        <div class="result-panel">
          <div class="result-panel-header">
            <div>
              <div class="result-panel-title">{t['result']}</div>
              <div class="result-panel-subtitle">
                {st.session_state.prop_type or '—'} · {st.session_state.location or '—'} · {st.session_state.tone}
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            f"📝 {t['tab_main']}",
            f"📱 {t['tab_social']}",
            f"🎬 {t['tab_video']}",
            f"⚙️ {t['tab_tech']}",
            f"✉️ {t['tab_email']}",
            f"🔍 {t['tab_seo']}"
        ])

        def tab_content(label, section_num, key_suffix):
            sec_content = get_sec(section_num)
            updated = st.text_area(
                label,
                value=sec_content,
                height=420,
                key=f"txt_{key_suffix}",
                label_visibility="collapsed"
            )
            col_s, col_d = st.columns([1, 1])
            with col_s:
                if st.button(t["save_btn"], key=f"save_{key_suffix}", use_container_width=True):
                    sections[section_num] = updated
                    combined = raw
                    st.success(t["saved_msg"])
            with col_d:
                st.download_button(
                    t["download_tab"],
                    data=updated,
                    file_name=f"sarsa_{key_suffix}_{timestamp}.txt",
                    key=f"dl_{key_suffix}",
                    use_container_width=True
                )
            return updated

        with tab1:
            tab_content(t["label_main"], 1, "listing")
        with tab2:
            tab_content(t["label_social"], 2, "social")
        with tab3:
            tab_content(t["label_video"], 3, "video")
        with tab4:
            tab_content(t["label_tech"], 4, "tech")
        with tab5:
            tab_content(t["label_email"], 5, "email")
        with tab6:
            tab_content(t["label_seo"], 6, "seo")

        st.markdown("---")
        col_exp1, col_exp2 = st.columns([2, 1])
        with col_exp1:
            st.download_button(
                label=t["download_all"],
                data=all_export,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )
        with col_exp2:
            if st.session_state.generation_history:
                last = st.session_state.generation_history[0]
                st.markdown(f"""
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;
                            padding:0.7rem 1rem; font-size:0.78rem; color:#64748b; text-align:center;">
                    ⏱ Last generated: <strong>{last['timestamp']}</strong>
                </div>
                """, unsafe_allow_html=True)

else:
    # ── EMPTY STATE ──
    st.markdown(f"""
    <div class="result-panel" style="border:2px dashed #e2e8f0; box-shadow:none;">
        <div class="empty-state">
            <div class="empty-state-icon">🏘️</div>
            <div class="empty-state-title">{t['empty_title']}</div>
            <div class="empty-state-sub">{t['empty_sub']}</div>
            <br>
            <div style="display:flex; justify-content:center; gap:10px; flex-wrap:wrap; margin-top:0.5rem;">
                {''.join([f"<span style='background:#f1f5f9; color:#475569; font-size:0.75rem; font-weight:500; padding:5px 12px; border-radius:20px; border:1px solid #e2e8f0;'>✓ {f}</span>" for f in t['features']])}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
