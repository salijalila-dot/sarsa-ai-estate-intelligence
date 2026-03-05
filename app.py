import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
import json
import time
import re
from datetime import datetime
import io
import base64

# ============================================================
# CONFIGURATION
# ============================================================
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = 'gemini-2.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

st.set_page_config(
    page_title="SarSa AI | Real Estate Intelligence Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# LOGO LOADER
# ============================================================
@st.cache_data
def load_logo(file_path):
    if os.path.exists(file_path):
        return Image.open(file_path)
    return None

# ============================================================
# UI LANGUAGE SYSTEM
# ============================================================
ui_languages = {
    "English": {
        "app_title": "SarSa AI",
        "tagline": "The #1 AI Platform for Real Estate Professionals",
        "nav_generate": "🚀 Generate",
        "nav_tools": "🛠️ AI Tools",
        "nav_history": "📁 History",
        "nav_templates": "📋 Templates",
        "nav_analytics": "📊 Analytics",
        "nav_settings": "⚙️ Settings",
        "settings": "⚙️ Configuration",
        "target_lang": "✍️ Write Content In...",
        "prop_type": "Property Type",
        "price": "Market Price",
        "location": "Location",
        "tone": "Marketing Strategy",
        "tones": ["Standard Pro", "Ultra-Luxury", "Investment Potential", "Modern Minimalist", "Family Comfort", "Commercial/Office", "Student Housing", "Vacation Rental", "New Development"],
        "ph_prop": "E.g., 3+1 Apartment, Luxury Villa...",
        "ph_price": "E.g., $500,000 or £2,000/mo...",
        "ph_loc": "E.g., Manhattan, NY or London, UK...",
        "bedrooms": "Bedrooms",
        "bathrooms": "Bathrooms",
        "sqft": "Size (sqm/sqft)",
        "year_built": "Year Built",
        "parking": "Parking Spaces",
        "amenities": "Key Amenities",
        "custom_inst": "📝 Special Notes",
        "custom_inst_ph": "E.g., High ceilings, near metro, recently renovated...",
        "btn": "🚀 GENERATE COMPLETE MARKETING PACKAGE",
        "upload_label": "📸 Upload Property Photos",
        "result": "💎 Marketing Package",
        "loading": "✨ Crafting your premium marketing package...",
        "empty": "Upload property photos to generate your complete marketing package.",
        "download_all": "📥 Download All (TXT)",
        "download_tab": "📥 Download This Section",
        "copy_btn": "📋 Copy to Clipboard",
        "save_btn": "💾 Save Changes",
        "saved_msg": "✅ Saved!",
        "error": "Error:",
        "tab_main": "📝 Listing",
        "tab_social": "📱 Social Media",
        "tab_video": "🎬 Video Script",
        "tab_tech": "⚙️ Tech Specs",
        "tab_email": "📧 Email Templates",
        "tab_seo": "🔍 SEO Pack",
        "label_main": "Sales Copy",
        "label_social": "Social Media Content",
        "label_video": "Video Script",
        "label_tech": "Technical Specifications",
        "label_email": "Email Templates",
        "label_seo": "SEO Keywords & Meta",
        "unsaved_warning": "⚠️ You have unsaved changes!",
        "unsaved_indicator": "📝 Unsaved Changes",
        "saved_indicator": "✅ All Saved",
        "tool_email_title": "📧 Cold Email Generator",
        "tool_email_desc": "Generate buyer/seller outreach emails",
        "tool_objection_title": "💬 Objection Handler",
        "tool_objection_desc": "AI responses to common client objections",
        "tool_cma_title": "📊 Market Analysis Report",
        "tool_cma_desc": "Generate a CMA-style market insights report",
        "tool_negotiation_title": "🤝 Negotiation Script",
        "tool_negotiation_desc": "Get a full negotiation talking points script",
        "tool_bio_title": "👤 Agent Bio Generator",
        "tool_bio_desc": "Write a professional agent biography",
        "tool_openhouse_title": "🏠 Open House Script",
        "tool_openhouse_desc": "Generate an open house presentation script",
        "tool_followup_title": "📞 Follow-Up Messages",
        "tool_followup_desc": "Post-viewing follow-up SMS and email templates",
        "tool_checklist_title": "✅ Transaction Checklist",
        "tool_checklist_desc": "Complete buyer/seller transaction checklist",
        "tool_neighborhood_title": "🗺️ Neighborhood Guide",
        "tool_neighborhood_desc": "AI-powered local area guide for buyers",
        "tool_investment_title": "💰 Investment Analysis",
        "tool_investment_desc": "ROI and rental yield analysis template",
        "tool_press_title": "📰 Press Release",
        "tool_press_desc": "Generate a property or agency press release",
        "history_empty": "No saved listings yet. Generate your first one!",
        "history_title": "📁 Saved Listings",
        "delete_btn": "🗑️ Delete",
        "load_btn": "📂 Load",
        "analytics_title": "📊 Usage Analytics",
        "lang_select": "🌐 Interface Language",
        "upgrade_banner": "🔓 Unlock unlimited generations — Upgrade to Pro",
        "free_remaining": "Free generations remaining today",
        "char_count": "characters",
        "word_count": "words",
        "regenerate": "🔄 Regenerate",
        "compliance_check": "⚖️ Fair Housing Check",
        "compliance_pass": "✅ No fair housing issues detected.",
        "compliance_warn": "⚠️ Review flagged terms:",
    },
    "Türkçe": {
        "app_title": "SarSa AI",
        "tagline": "Gayrimenkul Profesyonelleri için #1 AI Platformu",
        "nav_generate": "🚀 Oluştur",
        "nav_tools": "🛠️ AI Araçları",
        "nav_history": "📁 Geçmiş",
        "nav_templates": "📋 Şablonlar",
        "nav_analytics": "📊 Analitik",
        "nav_settings": "⚙️ Ayarlar",
        "settings": "⚙️ Yapılandırma",
        "target_lang": "✍️ İlan Yazım Dili...",
        "prop_type": "Emlak Tipi",
        "price": "Pazar Fiyatı",
        "location": "Konum",
        "tone": "Pazarlama Stratejisi",
        "tones": ["Standart Profesyonel", "Ultra-Lüks", "Yatırım Potansiyeli", "Modern Minimalist", "Aile Konforu", "Ticari/Ofis", "Öğrenci Konutu", "Tatil Kiralaması", "Yeni Geliştirme"],
        "ph_prop": "Örn: 3+1 Daire, Müstakil Villa...",
        "ph_price": "Örn: 5.000.000 TL veya $2.500/ay...",
        "ph_loc": "Örn: Beşiktaş, İstanbul...",
        "bedrooms": "Yatak Odası",
        "bathrooms": "Banyo",
        "sqft": "Alan (m²)",
        "year_built": "Yapım Yılı",
        "parking": "Otopark",
        "amenities": "Temel Olanaklar",
        "custom_inst": "📝 Özel Notlar",
        "custom_inst_ph": "Örn: Yüksek tavanlar, metroya yakın, yeni tadilat...",
        "btn": "🚀 TAM PAZARLAMA PAKETİ OLUŞTUR",
        "upload_label": "📸 Mülk Fotoğraflarını Yükle",
        "result": "💎 Pazarlama Paketi",
        "loading": "✨ Premium pazarlama paketiniz hazırlanıyor...",
        "empty": "Tam pazarlama paketinizi oluşturmak için mülk fotoğraflarını yükleyin.",
        "download_all": "📥 Tümünü İndir (TXT)",
        "download_tab": "📥 Bu Bölümü İndir",
        "copy_btn": "📋 Panoya Kopyala",
        "save_btn": "💾 Kaydet",
        "saved_msg": "✅ Kaydedildi!",
        "error": "Hata:",
        "tab_main": "📝 İlan",
        "tab_social": "📱 Sosyal Medya",
        "tab_video": "🎬 Video Script",
        "tab_tech": "⚙️ Teknik",
        "tab_email": "📧 E-posta",
        "tab_seo": "🔍 SEO",
        "label_main": "Satış Metni",
        "label_social": "Sosyal Medya İçeriği",
        "label_video": "Video Senaryosu",
        "label_tech": "Teknik Özellikler",
        "label_email": "E-posta Şablonları",
        "label_seo": "SEO Anahtar Kelimeleri",
        "unsaved_warning": "⚠️ Kaydedilmemiş değişiklikler var!",
        "unsaved_indicator": "📝 Kaydedilmemiş",
        "saved_indicator": "✅ Kaydedildi",
        "tool_email_title": "📧 Soğuk E-posta Üreteci",
        "tool_email_desc": "Alıcı/satıcı için sosyal yardım e-postaları oluşturun",
        "tool_objection_title": "💬 İtiraz İşleyici",
        "tool_objection_desc": "Müşteri itirazlarına AI yanıtları",
        "tool_cma_title": "📊 Pazar Analizi Raporu",
        "tool_cma_desc": "CMA tarzı pazar analiz raporu oluşturun",
        "tool_negotiation_title": "🤝 Müzakere Senaryosu",
        "tool_negotiation_desc": "Tam müzakere konuşma noktaları senaryosu",
        "tool_bio_title": "👤 Temsilci Biyografi Oluşturucu",
        "tool_bio_desc": "Profesyonel temsilci biyografisi yazın",
        "tool_openhouse_title": "🏠 Açık Ev Senaryosu",
        "tool_openhouse_desc": "Açık ev sunum senaryosu oluşturun",
        "tool_followup_title": "📞 Takip Mesajları",
        "tool_followup_desc": "Görüntüleme sonrası SMS ve e-posta şablonları",
        "tool_checklist_title": "✅ İşlem Kontrol Listesi",
        "tool_checklist_desc": "Alıcı/satıcı işlem kontrol listesi",
        "tool_neighborhood_title": "🗺️ Mahalle Rehberi",
        "tool_neighborhood_desc": "Alıcılar için AI destekli yerel alan rehberi",
        "tool_investment_title": "💰 Yatırım Analizi",
        "tool_investment_desc": "ROI ve kira geliri analiz şablonu",
        "tool_press_title": "📰 Basın Bülteni",
        "tool_press_desc": "Mülk veya acente basın bülteni oluşturun",
        "history_empty": "Henüz kayıtlı ilan yok. İlk ilanınızı oluşturun!",
        "history_title": "📁 Kayıtlı İlanlar",
        "delete_btn": "🗑️ Sil",
        "load_btn": "📂 Yükle",
        "analytics_title": "📊 Kullanım Analitiği",
        "lang_select": "🌐 Arayüz Dili",
        "upgrade_banner": "🔓 Sınırsız üretim için Pro'ya yükseltin",
        "free_remaining": "Bugün kalan ücretsiz üretim",
        "char_count": "karakter",
        "word_count": "kelime",
        "regenerate": "🔄 Yeniden Oluştur",
        "compliance_check": "⚖️ Adil Konut Kontrolü",
        "compliance_pass": "✅ Adil konut sorunu tespit edilmedi.",
        "compliance_warn": "⚠️ İşaretlenen ifadeleri inceleyin:",
    },
    "Español": {
        "app_title": "SarSa AI",
        "tagline": "La Plataforma de IA #1 para Profesionales Inmobiliarios",
        "nav_generate": "🚀 Generar",
        "nav_tools": "🛠️ Herramientas IA",
        "nav_history": "📁 Historial",
        "nav_templates": "📋 Plantillas",
        "nav_analytics": "📊 Analítica",
        "nav_settings": "⚙️ Ajustes",
        "settings": "⚙️ Configuración",
        "target_lang": "✍️ Escribir en...",
        "prop_type": "Tipo de Propiedad",
        "price": "Precio de Mercado",
        "location": "Ubicación",
        "tone": "Estrategia de Marketing",
        "tones": ["Profesional Estándar", "Ultra-Lujo", "Potencial de Inversión", "Minimalista Moderno", "Confort Familiar", "Comercial/Oficina", "Vivienda Estudiantil", "Alquiler Vacacional", "Nueva Construcción"],
        "ph_prop": "Ej: Apartamento 3+1, Villa de Lujo...",
        "ph_price": "Ej: $500.000 o €1.500/mes...",
        "ph_loc": "Ej: Madrid, España...",
        "bedrooms": "Dormitorios",
        "bathrooms": "Baños",
        "sqft": "Superficie (m²)",
        "year_built": "Año de construcción",
        "parking": "Plazas de garaje",
        "amenities": "Comodidades principales",
        "custom_inst": "📝 Notas Especiales",
        "custom_inst_ph": "Ej: Techos altos, cerca del metro...",
        "btn": "🚀 GENERAR PAQUETE COMPLETO DE MARKETING",
        "upload_label": "📸 Subir Fotos de la Propiedad",
        "result": "💎 Paquete de Marketing",
        "loading": "✨ Creando su paquete premium de marketing...",
        "empty": "Suba fotos para generar su paquete completo de marketing.",
        "download_all": "📥 Descargar Todo (TXT)",
        "download_tab": "📥 Descargar Esta Sección",
        "copy_btn": "📋 Copiar al Portapapeles",
        "save_btn": "💾 Guardar Cambios",
        "saved_msg": "✅ ¡Guardado!",
        "error": "Error:",
        "tab_main": "📝 Anuncio",
        "tab_social": "📱 Redes Sociales",
        "tab_video": "🎬 Guion de Video",
        "tab_tech": "⚙️ Especificaciones",
        "tab_email": "📧 Plantillas Email",
        "tab_seo": "🔍 Pack SEO",
        "label_main": "Texto de Ventas",
        "label_social": "Contenido Social",
        "label_video": "Guion de Video",
        "label_tech": "Ficha Técnica",
        "label_email": "Plantillas de Email",
        "label_seo": "Keywords SEO",
        "unsaved_warning": "⚠️ Tienes cambios sin guardar",
        "unsaved_indicator": "📝 Sin Guardar",
        "saved_indicator": "✅ Guardado",
        "tool_email_title": "📧 Generador de Cold Email",
        "tool_email_desc": "Genera emails de contacto para compradores/vendedores",
        "tool_objection_title": "💬 Manejador de Objeciones",
        "tool_objection_desc": "Respuestas IA a objeciones comunes de clientes",
        "tool_cma_title": "📊 Informe de Análisis de Mercado",
        "tool_cma_desc": "Genera un informe de análisis de mercado tipo CMA",
        "tool_negotiation_title": "🤝 Guion de Negociación",
        "tool_negotiation_desc": "Guion completo de puntos de negociación",
        "tool_bio_title": "👤 Generador de Bio del Agente",
        "tool_bio_desc": "Escribe una biografía profesional del agente",
        "tool_openhouse_title": "🏠 Guion de Open House",
        "tool_openhouse_desc": "Genera un guion de presentación para open house",
        "tool_followup_title": "📞 Mensajes de Seguimiento",
        "tool_followup_desc": "Plantillas SMS y email post-visita",
        "tool_checklist_title": "✅ Lista de Verificación",
        "tool_checklist_desc": "Lista completa de transacción comprador/vendedor",
        "tool_neighborhood_title": "🗺️ Guía del Vecindario",
        "tool_neighborhood_desc": "Guía local para compradores con IA",
        "tool_investment_title": "💰 Análisis de Inversión",
        "tool_investment_desc": "Plantilla de análisis ROI y rendimiento de alquiler",
        "tool_press_title": "📰 Nota de Prensa",
        "tool_press_desc": "Genera una nota de prensa para una propiedad o agencia",
        "history_empty": "Aún no hay listados guardados. ¡Genera el primero!",
        "history_title": "📁 Listados Guardados",
        "delete_btn": "🗑️ Eliminar",
        "load_btn": "📂 Cargar",
        "analytics_title": "📊 Analítica de Uso",
        "lang_select": "🌐 Idioma de la Interfaz",
        "upgrade_banner": "🔓 Generaciones ilimitadas — Actualiza a Pro",
        "free_remaining": "Generaciones gratuitas restantes hoy",
        "char_count": "caracteres",
        "word_count": "palabras",
        "regenerate": "🔄 Regenerar",
        "compliance_check": "⚖️ Verificación de Vivienda Justa",
        "compliance_pass": "✅ No se detectaron problemas de vivienda justa.",
        "compliance_warn": "⚠️ Revise los términos marcados:",
    },
    "Deutsch": {
        "app_title": "SarSa AI",
        "tagline": "Die #1 KI-Plattform für Immobilienprofis",
        "nav_generate": "🚀 Erstellen",
        "nav_tools": "🛠️ KI-Tools",
        "nav_history": "📁 Verlauf",
        "nav_templates": "📋 Vorlagen",
        "nav_analytics": "📊 Analyse",
        "nav_settings": "⚙️ Einstellungen",
        "settings": "⚙️ Konfiguration",
        "target_lang": "✍️ Erstellen in...",
        "prop_type": "Objekttyp",
        "price": "Marktpreis",
        "location": "Standort",
        "tone": "Marketingstrategie",
        "tones": ["Standard-Profi", "Ultra-Luxus", "Investitionspotenzial", "Modern-Minimalistisch", "Familienkomfort", "Gewerbe/Büro", "Studentenwohnen", "Ferienmiete", "Neubau"],
        "ph_prop": "Z.B. 3-Zimmer-Wohnung, Luxusvilla...",
        "ph_price": "Z.B. 500.000€ oder 2.000€/Monat...",
        "ph_loc": "Z.B. Berlin, Deutschland...",
        "bedrooms": "Schlafzimmer",
        "bathrooms": "Badezimmer",
        "sqft": "Fläche (m²)",
        "year_built": "Baujahr",
        "parking": "Stellplätze",
        "amenities": "Ausstattungsmerkmale",
        "custom_inst": "📝 Notizen",
        "custom_inst_ph": "Z.B. Hohe Decken, U-Bahn-Nähe...",
        "btn": "🚀 KOMPLETTES MARKETING-PAKET ERSTELLEN",
        "upload_label": "📸 Fotos hochladen",
        "result": "💎 Marketing-Paket",
        "loading": "✨ Ihr Premium-Marketing-Paket wird erstellt...",
        "empty": "Laden Sie Fotos hoch, um Ihr komplettes Marketing-Paket zu erstellen.",
        "download_all": "📥 Alles herunterladen (TXT)",
        "download_tab": "📥 Diesen Abschnitt herunterladen",
        "copy_btn": "📋 In Zwischenablage kopieren",
        "save_btn": "💾 Speichern",
        "saved_msg": "✅ Gespeichert!",
        "error": "Fehler:",
        "tab_main": "📝 Exposé",
        "tab_social": "📱 Social Media",
        "tab_video": "🎬 Videoskript",
        "tab_tech": "⚙️ Technik",
        "tab_email": "📧 E-Mail-Vorlagen",
        "tab_seo": "🔍 SEO-Paket",
        "label_main": "Verkaufstext",
        "label_social": "Social-Media-Content",
        "label_video": "Video-Skript",
        "label_tech": "Technische Daten",
        "label_email": "E-Mail-Vorlagen",
        "label_seo": "SEO-Keywords",
        "unsaved_warning": "⚠️ Ungespeicherte Änderungen!",
        "unsaved_indicator": "📝 Ungespeichert",
        "saved_indicator": "✅ Gespeichert",
        "tool_email_title": "📧 Kalt-E-Mail-Generator",
        "tool_email_desc": "Kontaktmails für Käufer/Verkäufer generieren",
        "tool_objection_title": "💬 Einwand-Handler",
        "tool_objection_desc": "KI-Antworten auf Kundeneinwände",
        "tool_cma_title": "📊 Marktanalyse-Bericht",
        "tool_cma_desc": "CMA-artigen Marktanalysebericht erstellen",
        "tool_negotiation_title": "🤝 Verhandlungsskript",
        "tool_negotiation_desc": "Vollständiges Verhandlungsargument-Skript",
        "tool_bio_title": "👤 Makler-Bio-Generator",
        "tool_bio_desc": "Professionelle Makler-Biografie schreiben",
        "tool_openhouse_title": "🏠 Tag der offenen Tür",
        "tool_openhouse_desc": "Präsentationsskript für offene Besichtigung",
        "tool_followup_title": "📞 Nachfass-Nachrichten",
        "tool_followup_desc": "SMS- und E-Mail-Vorlagen nach Besichtigung",
        "tool_checklist_title": "✅ Transaktions-Checkliste",
        "tool_checklist_desc": "Vollständige Käufer/Verkäufer-Checkliste",
        "tool_neighborhood_title": "🗺️ Nachbarschafts-Guide",
        "tool_neighborhood_desc": "KI-gestützter Ortsführer für Käufer",
        "tool_investment_title": "💰 Investitionsanalyse",
        "tool_investment_desc": "ROI- und Mietrendite-Analysevorlage",
        "tool_press_title": "📰 Pressemitteilung",
        "tool_press_desc": "Pressemitteilung für Objekt oder Agentur",
        "history_empty": "Noch keine gespeicherten Listings. Erstellen Sie Ihr erstes!",
        "history_title": "📁 Gespeicherte Listings",
        "delete_btn": "🗑️ Löschen",
        "load_btn": "📂 Laden",
        "analytics_title": "📊 Nutzungsanalysen",
        "lang_select": "🌐 Oberflächensprache",
        "upgrade_banner": "🔓 Unbegrenzte Generierungen — Auf Pro upgraden",
        "free_remaining": "Verbleibende kostenlose Generierungen heute",
        "char_count": "Zeichen",
        "word_count": "Wörter",
        "regenerate": "🔄 Neu generieren",
        "compliance_check": "⚖️ Fairness-Prüfung",
        "compliance_pass": "✅ Keine Fairness-Probleme erkannt.",
        "compliance_warn": "⚠️ Markierte Begriffe prüfen:",
    },
    "Français": {
        "app_title": "SarSa AI",
        "tagline": "La Plateforme IA #1 pour les Professionnels de l'Immobilier",
        "nav_generate": "🚀 Générer",
        "nav_tools": "🛠️ Outils IA",
        "nav_history": "📁 Historique",
        "nav_templates": "📋 Modèles",
        "nav_analytics": "📊 Analytique",
        "nav_settings": "⚙️ Paramètres",
        "settings": "⚙️ Configuration",
        "target_lang": "✍️ Rédiger en...",
        "prop_type": "Type de Bien",
        "price": "Prix du Marché",
        "location": "Localisation",
        "tone": "Stratégie Marketing",
        "tones": ["Standard Pro", "Ultra-Luxe", "Potentiel d'Investissement", "Minimaliste Moderne", "Confort Familial", "Commercial/Bureau", "Logement Étudiant", "Location Vacances", "Nouvelle Construction"],
        "ph_prop": "Ex: Appartement T4, Villa de Luxe...",
        "ph_price": "Ex: 500.000€ ou 1.500€/mois...",
        "ph_loc": "Ex: Paris, France...",
        "bedrooms": "Chambres",
        "bathrooms": "Salles de bain",
        "sqft": "Surface (m²)",
        "year_built": "Année de construction",
        "parking": "Places de parking",
        "amenities": "Équipements principaux",
        "custom_inst": "📝 Notes Spéciales",
        "custom_inst_ph": "Ex: Plafonds hauts, proche métro...",
        "btn": "🚀 GÉNÉRER LE PACK MARKETING COMPLET",
        "upload_label": "📸 Télécharger les Photos",
        "result": "💎 Pack Marketing",
        "loading": "✨ Création de votre pack marketing premium...",
        "empty": "Téléchargez des photos pour générer votre pack marketing complet.",
        "download_all": "📥 Tout Télécharger (TXT)",
        "download_tab": "📥 Télécharger Cette Section",
        "copy_btn": "📋 Copier",
        "save_btn": "💾 Enregistrer",
        "saved_msg": "✅ Enregistré !",
        "error": "Erreur :",
        "tab_main": "📝 Annonce",
        "tab_social": "📱 Réseaux Sociaux",
        "tab_video": "🎬 Script Vidéo",
        "tab_tech": "⚙️ Spécifications",
        "tab_email": "📧 Modèles Email",
        "tab_seo": "🔍 Pack SEO",
        "label_main": "Texte de Vente",
        "label_social": "Contenu Social",
        "label_video": "Script Vidéo",
        "label_tech": "Détails Techniques",
        "label_email": "Modèles d'Email",
        "label_seo": "Mots-clés SEO",
        "unsaved_warning": "⚠️ Modifications non enregistrées !",
        "unsaved_indicator": "📝 Non Enregistré",
        "saved_indicator": "✅ Enregistré",
        "tool_email_title": "📧 Générateur d'Emails",
        "tool_email_desc": "Emails de prospection acheteurs/vendeurs",
        "tool_objection_title": "💬 Gestionnaire d'Objections",
        "tool_objection_desc": "Réponses IA aux objections clients",
        "tool_cma_title": "📊 Rapport d'Analyse Marché",
        "tool_cma_desc": "Rapport d'analyse de marché type CMA",
        "tool_negotiation_title": "🤝 Script de Négociation",
        "tool_negotiation_desc": "Script complet de points de négociation",
        "tool_bio_title": "👤 Générateur de Bio Agent",
        "tool_bio_desc": "Rédiger une biographie professionnelle",
        "tool_openhouse_title": "🏠 Script Portes Ouvertes",
        "tool_openhouse_desc": "Script de présentation pour visite",
        "tool_followup_title": "📞 Messages de Suivi",
        "tool_followup_desc": "Modèles SMS et email post-visite",
        "tool_checklist_title": "✅ Checklist Transaction",
        "tool_checklist_desc": "Checklist complète acheteur/vendeur",
        "tool_neighborhood_title": "🗺️ Guide du Quartier",
        "tool_neighborhood_desc": "Guide local IA pour acheteurs",
        "tool_investment_title": "💰 Analyse d'Investissement",
        "tool_investment_desc": "Modèle d'analyse ROI et rendement locatif",
        "tool_press_title": "📰 Communiqué de Presse",
        "tool_press_desc": "Communiqué pour un bien ou une agence",
        "history_empty": "Pas encore de listings sauvegardés. Créez le premier !",
        "history_title": "📁 Listings Sauvegardés",
        "delete_btn": "🗑️ Supprimer",
        "load_btn": "📂 Charger",
        "analytics_title": "📊 Analytique d'Utilisation",
        "lang_select": "🌐 Langue de l'Interface",
        "upgrade_banner": "🔓 Générations illimitées — Passez à Pro",
        "free_remaining": "Générations gratuites restantes aujourd'hui",
        "char_count": "caractères",
        "word_count": "mots",
        "regenerate": "🔄 Régénérer",
        "compliance_check": "⚖️ Vérification Logement Équitable",
        "compliance_pass": "✅ Aucun problème détecté.",
        "compliance_warn": "⚠️ Termes à vérifier :",
    },
    "Português": {
        "app_title": "SarSa AI", "tagline": "A Plataforma de IA #1 para Profissionais Imobiliários",
        "nav_generate": "🚀 Gerar", "nav_tools": "🛠️ Ferramentas IA", "nav_history": "📁 Histórico",
        "nav_templates": "📋 Modelos", "nav_analytics": "📊 Analítica", "nav_settings": "⚙️ Configurações",
        "settings": "⚙️ Configuração", "target_lang": "✍️ Escrever em...", "prop_type": "Tipo de Imóvel",
        "price": "Preço de Mercado", "location": "Localização", "tone": "Estratégia de Marketing",
        "tones": ["Profissional Padrão", "Ultra-Luxo", "Potencial de Investimento", "Minimalista Moderno", "Conforto Familiar", "Comercial/Escritório", "Moradia Estudantil", "Aluguel de Férias", "Nova Construção"],
        "ph_prop": "Ex: Apartamento T3, Moradia de Luxo...", "ph_price": "Ex: 500.000€ ou 1.500€/mês...",
        "ph_loc": "Ex: Lisboa, Portugal...", "bedrooms": "Quartos", "bathrooms": "Casas de Banho",
        "sqft": "Área (m²)", "year_built": "Ano de Construção", "parking": "Lugares de Estacionamento",
        "amenities": "Comodidades Principais", "custom_inst": "📝 Notas Especiais",
        "custom_inst_ph": "Ex: Tetos altos, perto do metrô...", "btn": "🚀 GERAR PACOTE COMPLETO DE MARKETING",
        "upload_label": "📸 Enviar Fotos do Imóvel", "result": "💎 Pacote de Marketing",
        "loading": "✨ Criando seu pacote premium de marketing...", "empty": "Envie fotos para gerar seu pacote completo.",
        "download_all": "📥 Baixar Tudo (TXT)", "download_tab": "📥 Baixar Esta Seção",
        "copy_btn": "📋 Copiar", "save_btn": "💾 Salvar", "saved_msg": "✅ Salvo!",
        "error": "Erro:", "tab_main": "📝 Anúncio", "tab_social": "📱 Redes Sociais",
        "tab_video": "🎬 Roteiro", "tab_tech": "⚙️ Técnico", "tab_email": "📧 E-mails", "tab_seo": "🔍 SEO",
        "label_main": "Texto de Vendas", "label_social": "Conteúdo Social", "label_video": "Roteiro de Vídeo",
        "label_tech": "Especificações", "label_email": "Modelos de E-mail", "label_seo": "Keywords SEO",
        "unsaved_warning": "⚠️ Alterações não salvas!", "unsaved_indicator": "📝 Não Salvo", "saved_indicator": "✅ Salvo",
        "tool_email_title": "📧 Gerador de Cold Email", "tool_email_desc": "E-mails de contato para compradores/vendedores",
        "tool_objection_title": "💬 Tratamento de Objeções", "tool_objection_desc": "Respostas IA a objeções comuns",
        "tool_cma_title": "📊 Relatório de Análise", "tool_cma_desc": "Relatório de análise de mercado CMA",
        "tool_negotiation_title": "🤝 Script de Negociação", "tool_negotiation_desc": "Script completo de negociação",
        "tool_bio_title": "👤 Gerador de Bio", "tool_bio_desc": "Escreva uma biografia profissional",
        "tool_openhouse_title": "🏠 Script de Visita", "tool_openhouse_desc": "Script de apresentação para visita",
        "tool_followup_title": "📞 Mensagens de Acompanhamento", "tool_followup_desc": "SMS e e-mail pós-visita",
        "tool_checklist_title": "✅ Checklist de Transação", "tool_checklist_desc": "Checklist completa comprador/vendedor",
        "tool_neighborhood_title": "🗺️ Guia do Bairro", "tool_neighborhood_desc": "Guia local IA para compradores",
        "tool_investment_title": "💰 Análise de Investimento", "tool_investment_desc": "ROI e análise de rendimento",
        "tool_press_title": "📰 Comunicado de Imprensa", "tool_press_desc": "Comunicado para imóvel ou agência",
        "history_empty": "Nenhum listing salvo ainda. Crie o primeiro!", "history_title": "📁 Listings Salvos",
        "delete_btn": "🗑️ Apagar", "load_btn": "📂 Carregar", "analytics_title": "📊 Analítica de Uso",
        "lang_select": "🌐 Idioma da Interface", "upgrade_banner": "🔓 Gerações ilimitadas — Atualizar para Pro",
        "free_remaining": "Gerações gratuitas restantes hoje", "char_count": "caracteres", "word_count": "palavras",
        "regenerate": "🔄 Regenerar", "compliance_check": "⚖️ Verificação de Habitação Justa",
        "compliance_pass": "✅ Nenhum problema detectado.", "compliance_warn": "⚠️ Termos a revisar:",
    },
    "日本語": {
        "app_title": "SarSa AI", "tagline": "不動産プロフェッショナル向け#1 AIプラットフォーム",
        "nav_generate": "🚀 生成", "nav_tools": "🛠️ AIツール", "nav_history": "📁 履歴",
        "nav_templates": "📋 テンプレート", "nav_analytics": "📊 分析", "nav_settings": "⚙️ 設定",
        "settings": "⚙️ 設定", "target_lang": "✍️ 作成言語...", "prop_type": "物件種別",
        "price": "市場価格", "location": "所在地", "tone": "マーケティング戦略",
        "tones": ["スタンダードプロ", "ウルトラ高級", "投資ポテンシャル", "モダンミニマル", "ファミリー向け", "商業/オフィス", "学生向け住居", "バケーションレンタル", "新築物件"],
        "ph_prop": "例：3LDKマンション、高級別荘...", "ph_price": "例：5000万円、月20万円...",
        "ph_loc": "例：東京都港区...", "bedrooms": "寝室数", "bathrooms": "バスルーム数",
        "sqft": "面積（㎡）", "year_built": "建築年", "parking": "駐車スペース", "amenities": "主要設備",
        "custom_inst": "📝 特記事項", "custom_inst_ph": "例：高い天井、駅近、リノベーション済み...",
        "btn": "🚀 完全なマーケティングパッケージを生成", "upload_label": "📸 物件写真をアップロード",
        "result": "💎 マーケティングパッケージ", "loading": "✨ プレミアムマーケティングパッケージを作成中...",
        "empty": "完全なマーケティングパッケージを生成するために写真をアップロードしてください。",
        "download_all": "📥 すべてダウンロード (TXT)", "download_tab": "📥 このセクションをダウンロード",
        "copy_btn": "📋 クリップボードにコピー", "save_btn": "💾 保存", "saved_msg": "✅ 保存完了！",
        "error": "エラー:", "tab_main": "📝 物件広告", "tab_social": "📱 SNSキット",
        "tab_video": "🎬 動画台本", "tab_tech": "⚙️ 技術仕様", "tab_email": "📧 メールテンプレート", "tab_seo": "🔍 SEOパック",
        "label_main": "セールスコピー", "label_social": "SNSコンテンツ", "label_video": "動画台本",
        "label_tech": "技術仕様", "label_email": "メールテンプレート", "label_seo": "SEOキーワード",
        "unsaved_warning": "⚠️ 未保存の変更があります！", "unsaved_indicator": "📝 未保存", "saved_indicator": "✅ 保存済み",
        "tool_email_title": "📧 コールドメール生成", "tool_email_desc": "買主・売主向けアウトリーチメール生成",
        "tool_objection_title": "💬 異議対応", "tool_objection_desc": "一般的な顧客異議へのAI回答",
        "tool_cma_title": "📊 市場分析レポート", "tool_cma_desc": "CMA形式の市場分析レポート生成",
        "tool_negotiation_title": "🤝 交渉スクリプト", "tool_negotiation_desc": "完全な交渉ポイントスクリプト",
        "tool_bio_title": "👤 エージェント自己紹介", "tool_bio_desc": "プロフェッショナルな自己紹介文を作成",
        "tool_openhouse_title": "🏠 内覧スクリプト", "tool_openhouse_desc": "内覧案内のプレゼンテーションスクリプト",
        "tool_followup_title": "📞 フォローアップメッセージ", "tool_followup_desc": "内覧後のSMS・メールテンプレート",
        "tool_checklist_title": "✅ 取引チェックリスト", "tool_checklist_desc": "買主・売主の完全な取引チェックリスト",
        "tool_neighborhood_title": "🗺️ 地域ガイド", "tool_neighborhood_desc": "買主向けAI地域ガイド",
        "tool_investment_title": "💰 投資分析", "tool_investment_desc": "ROIと賃貸利回り分析テンプレート",
        "tool_press_title": "📰 プレスリリース", "tool_press_desc": "物件または会社のプレスリリース生成",
        "history_empty": "保存済み物件情報がありません。最初のものを作成してください！", "history_title": "📁 保存済み物件",
        "delete_btn": "🗑️ 削除", "load_btn": "📂 読み込み", "analytics_title": "📊 使用分析",
        "lang_select": "🌐 インターフェース言語", "upgrade_banner": "🔓 無制限生成 — Proにアップグレード",
        "free_remaining": "本日の残り無料生成数", "char_count": "文字", "word_count": "単語",
        "regenerate": "🔄 再生成", "compliance_check": "⚖️ 公正住宅チェック",
        "compliance_pass": "✅ 公正住宅の問題は検出されませんでした。", "compliance_warn": "⚠️ 確認が必要な用語:",
    },
    "中文 (简体)": {
        "app_title": "SarSa AI", "tagline": "房地产专业人士的#1人工智能平台",
        "nav_generate": "🚀 生成", "nav_tools": "🛠️ AI工具", "nav_history": "📁 历史",
        "nav_templates": "📋 模板", "nav_analytics": "📊 分析", "nav_settings": "⚙️ 设置",
        "settings": "⚙️ 配置", "target_lang": "✍️ 编写语言...", "prop_type": "房产类型",
        "price": "市场价格", "location": "地点", "tone": "营销策略",
        "tones": ["标准专业", "顶奢豪宅", "投资潜力", "现代简约", "家庭舒适", "商业/办公", "学生住宅", "度假租赁", "新开发"],
        "ph_prop": "例如：3居室公寓，豪华别墅...", "ph_price": "例如：$500,000 或 $2,000/月...",
        "ph_loc": "例如：上海市浦东新区...", "bedrooms": "卧室", "bathrooms": "浴室",
        "sqft": "面积（平米）", "year_built": "建造年份", "parking": "停车位", "amenities": "主要设施",
        "custom_inst": "📝 特别备注", "custom_inst_ph": "例如：挑高天花板，靠近地铁，新装修...",
        "btn": "🚀 生成完整营销套餐", "upload_label": "📸 上传房产照片",
        "result": "💎 营销套餐", "loading": "✨ 正在打造您的高端营销套餐...",
        "empty": "上传房产照片以生成完整营销套餐。",
        "download_all": "📥 下载全部 (TXT)", "download_tab": "📥 下载此部分",
        "copy_btn": "📋 复制", "save_btn": "💾 保存", "saved_msg": "✅ 已保存！",
        "error": "错误:", "tab_main": "📝 房源", "tab_social": "📱 社交媒体",
        "tab_video": "🎬 视频脚本", "tab_tech": "⚙️ 技术", "tab_email": "📧 邮件模板", "tab_seo": "🔍 SEO",
        "label_main": "销售文案", "label_social": "社媒内容", "label_video": "视频脚本",
        "label_tech": "技术规格", "label_email": "邮件模板", "label_seo": "SEO关键词",
        "unsaved_warning": "⚠️ 有未保存的更改！", "unsaved_indicator": "📝 未保存", "saved_indicator": "✅ 已保存",
        "tool_email_title": "📧 冷邮件生成器", "tool_email_desc": "生成买家/卖家联系邮件",
        "tool_objection_title": "💬 异议处理", "tool_objection_desc": "AI回应常见客户异议",
        "tool_cma_title": "📊 市场分析报告", "tool_cma_desc": "生成CMA式市场分析报告",
        "tool_negotiation_title": "🤝 谈判脚本", "tool_negotiation_desc": "完整谈判要点脚本",
        "tool_bio_title": "👤 经纪人简介生成", "tool_bio_desc": "撰写专业经纪人简介",
        "tool_openhouse_title": "🏠 开放参观脚本", "tool_openhouse_desc": "生成开放参观演示脚本",
        "tool_followup_title": "📞 跟进消息", "tool_followup_desc": "看房后短信和邮件模板",
        "tool_checklist_title": "✅ 交易清单", "tool_checklist_desc": "完整买家/卖家交易清单",
        "tool_neighborhood_title": "🗺️ 社区指南", "tool_neighborhood_desc": "AI驱动的买家本地指南",
        "tool_investment_title": "💰 投资分析", "tool_investment_desc": "ROI和租金收益率分析模板",
        "tool_press_title": "📰 新闻稿", "tool_press_desc": "生成房产或中介新闻稿",
        "history_empty": "还没有保存的房源。生成您的第一个！", "history_title": "📁 已保存房源",
        "delete_btn": "🗑️ 删除", "load_btn": "📂 加载", "analytics_title": "📊 使用分析",
        "lang_select": "🌐 界面语言", "upgrade_banner": "🔓 无限生成 — 升级到专业版",
        "free_remaining": "今日剩余免费生成次数", "char_count": "字符", "word_count": "词",
        "regenerate": "🔄 重新生成", "compliance_check": "⚖️ 公平住房检查",
        "compliance_pass": "✅ 未检测到公平住房问题。", "compliance_warn": "⚠️ 请检查标记的术语:",
    },
    "العربية": {
        "app_title": "SarSa AI", "tagline": "منصة الذكاء الاصطناعي الأولى للمحترفين العقاريين",
        "nav_generate": "🚀 إنشاء", "nav_tools": "🛠️ أدوات الذكاء الاصطناعي", "nav_history": "📁 السجل",
        "nav_templates": "📋 القوالب", "nav_analytics": "📊 التحليلات", "nav_settings": "⚙️ الإعدادات",
        "settings": "⚙️ الإعدادات", "target_lang": "✍️ لغة الكتابة...", "prop_type": "نوع العقار",
        "price": "سعر السوق", "location": "الموقع", "tone": "استراتيجية التسويق",
        "tones": ["احترافي قياسي", "فخامة فائقة", "إمكانات استثمارية", "عصري بسيط", "راحة عائلية", "تجاري/مكتبي", "سكن طلابي", "إيجار عطلات", "مشروع جديد"],
        "ph_prop": "مثال: شقة 3+1، فيلا فاخرة...", "ph_price": "مثال: $500,000 أو $2,000 شهرياً...",
        "ph_loc": "مثال: دبي، الإمارات...", "bedrooms": "غرف النوم", "bathrooms": "الحمامات",
        "sqft": "المساحة (م²)", "year_built": "سنة البناء", "parking": "أماكن الوقوف", "amenities": "المرافق الرئيسية",
        "custom_inst": "📝 ملاحظات خاصة", "custom_inst_ph": "مثال: أسقف عالية، قرب المترو...",
        "btn": "🚀 إنشاء حزمة تسويقية متكاملة", "upload_label": "📸 رفع صور العقار",
        "result": "💎 الحزمة التسويقية", "loading": "✨ جارٍ إعداد حزمتك التسويقية الفاخرة...",
        "empty": "ارفع صور العقار لإنشاء حزمتك التسويقية الكاملة.",
        "download_all": "📥 تحميل الكل (TXT)", "download_tab": "📥 تحميل هذا القسم",
        "copy_btn": "📋 نسخ", "save_btn": "💾 حفظ", "saved_msg": "✅ تم الحفظ!",
        "error": "خطأ:", "tab_main": "📝 الإعلان", "tab_social": "📱 التواصل الاجتماعي",
        "tab_video": "🎬 سيناريو الفيديو", "tab_tech": "⚙️ التفاصيل", "tab_email": "📧 قوالب البريد", "tab_seo": "🔍 حزمة SEO",
        "label_main": "نص المبيعات", "label_social": "محتوى التواصل", "label_video": "سيناريو الفيديو",
        "label_tech": "المواصفات الفنية", "label_email": "قوالب البريد الإلكتروني", "label_seo": "كلمات SEO",
        "unsaved_warning": "⚠️ لديك تغييرات غير محفوظة!", "unsaved_indicator": "📝 غير محفوظ", "saved_indicator": "✅ محفوظ",
        "tool_email_title": "📧 منشئ البريد الإلكتروني", "tool_email_desc": "إنشاء رسائل للمشترين والبائعين",
        "tool_objection_title": "💬 معالج الاعتراضات", "tool_objection_desc": "ردود AI على اعتراضات العملاء الشائعة",
        "tool_cma_title": "📊 تقرير تحليل السوق", "tool_cma_desc": "إنشاء تقرير تحليل سوق",
        "tool_negotiation_title": "🤝 سيناريو التفاوض", "tool_negotiation_desc": "سيناريو كامل لنقاط التفاوض",
        "tool_bio_title": "👤 منشئ السيرة الذاتية", "tool_bio_desc": "كتابة سيرة ذاتية احترافية للوكيل",
        "tool_openhouse_title": "🏠 سيناريو المعرض المفتوح", "tool_openhouse_desc": "إنشاء سيناريو عرض للمعرض المفتوح",
        "tool_followup_title": "📞 رسائل المتابعة", "tool_followup_desc": "قوالب SMS والبريد بعد المعاينة",
        "tool_checklist_title": "✅ قائمة التحقق من المعاملات", "tool_checklist_desc": "قائمة تحقق كاملة للمشتري/البائع",
        "tool_neighborhood_title": "🗺️ دليل الحي", "tool_neighborhood_desc": "دليل المنطقة المحلية للمشترين",
        "tool_investment_title": "💰 تحليل الاستثمار", "tool_investment_desc": "نموذج تحليل العائد على الاستثمار",
        "tool_press_title": "📰 البيان الصحفي", "tool_press_desc": "إنشاء بيان صحفي للعقار أو الوكالة",
        "history_empty": "لا توجد قوائم محفوظة بعد. أنشئ أولاً!", "history_title": "📁 القوائم المحفوظة",
        "delete_btn": "🗑️ حذف", "load_btn": "📂 تحميل", "analytics_title": "📊 تحليلات الاستخدام",
        "lang_select": "🌐 لغة الواجهة", "upgrade_banner": "🔓 توليدات غير محدودة — الترقية إلى Pro",
        "free_remaining": "التوليدات المجانية المتبقية اليوم", "char_count": "حرف", "word_count": "كلمة",
        "regenerate": "🔄 إعادة التوليد", "compliance_check": "⚖️ فحص الإسكان العادل",
        "compliance_pass": "✅ لم يتم اكتشاف مشاكل في الإسكان العادل.", "compliance_warn": "⚠️ مراجعة المصطلحات المميزة:",
    },
}

# ============================================================
# SESSION STATE INIT
# ============================================================
defaults = {
    "uretilen_ilan": "",
    "prop_type": "", "price": "", "location": "",
    "tone": "", "custom_inst": "", "target_lang_input": "English",
    "has_unsaved_changes": False,
    "active_page": "generate",
    "saved_listings": [],
    "generations_today": 0,
    "last_gen_date": str(datetime.now().date()),
    "tool_output": "",
    "agent_name": "", "agent_phone": "", "agent_email": "", "agent_company": "",
    "bedrooms": "", "bathrooms": "", "sqft": "", "year_built": "", "parking": "",
    "amenities": "",
    "sec1": "", "sec2": "", "sec3": "", "sec4": "", "sec5": "", "sec6": "",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Reset daily counter if new day
today = str(datetime.now().date())
if st.session_state.last_gen_date != today:
    st.session_state.generations_today = 0
    st.session_state.last_gen_date = today

# ============================================================
# FAIR HOUSING COMPLIANCE CHECKER
# ============================================================
FAIR_HOUSING_FLAGS = [
    "family-friendly", "families only", "perfect for couples", "no children",
    "adults only", "christian", "jewish", "muslim", "catholic", "white neighborhood",
    "english only", "american only", "exclusive community", "gated for safety",
    "safe neighborhood" , "good school district" # can imply racial steering
]

def check_fair_housing(text):
    text_lower = text.lower()
    flagged = [term for term in FAIR_HOUSING_FLAGS if term in text_lower]
    return flagged

# ============================================================
# CSS STYLING — PROFESSIONAL DARK THEME
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}

/* Hide streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
div[data-testid="stInputInstructions"] { display: none !important; }

/* Main background */
.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1a2e 50%, #0a0f1e 100%) !important;
}

/* Main container */
.block-container {
    background: transparent !important;
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 1400px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b27 100%) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.2) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1rem !important;
}

/* Hero Header */
.hero-header {
    background: linear-gradient(135deg, #1a1f3e 0%, #0f172a 50%, #1a1f3e 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at center, rgba(99,102,241,0.08) 0%, transparent 60%);
    pointer-events: none;
}

.hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
}

.hero-tagline {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 400;
    margin-top: 0.5rem;
    letter-spacing: 0.5px;
}

/* Stat pills */
.stat-pill {
    display: inline-block;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: #a5b4fc;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 4px;
}

/* Nav Buttons */
.stButton>button {
    background: rgba(99, 102, 241, 0.1) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}

.stButton>button:hover {
    background: rgba(99, 102, 241, 0.25) !important;
    border-color: rgba(99, 102, 241, 0.5) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2) !important;
}

/* Generate button */
.generate-btn > div > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 16px 24px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4) !important;
}

.generate-btn > div > button:hover {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    box-shadow: 0 6px 25px rgba(99, 102, 241, 0.5) !important;
    transform: translateY(-2px) !important;
}

/* Cards */
.feature-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease;
}

.feature-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    background: rgba(99, 102, 241, 0.05);
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(99, 102, 241, 0.6) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(99, 102, 241, 0.2) !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    font-weight: 700 !important;
}

/* Labels */
.stTextInput label, .stTextArea label, .stSelectbox label, .stFileUploader label {
    color: #94a3b8 !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px !important;
}

/* Section headers */
h1, h2, h3 {
    color: #e2e8f0 !important;
}

/* Sidebar labels */
section[data-testid="stSidebar"] label {
    color: #94a3b8 !important;
}

section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    background: rgba(255,255,255,0.05) !important;
}

/* Tool card */
.tool-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
}

.tool-card:hover {
    border-color: rgba(99, 102, 241, 0.5);
    background: rgba(99, 102, 241, 0.08);
    transform: translateY(-2px);
}

.tool-card-title {
    color: #e2e8f0;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 4px;
}

.tool-card-desc {
    color: #64748b;
    font-size: 0.85rem;
}

/* Badges */
.badge-unsaved {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-block;
}

.badge-saved {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-block;
}

/* History card */
.history-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}

.history-card-title {
    color: #e2e8f0;
    font-weight: 700;
    font-size: 0.95rem;
}

.history-card-meta {
    color: #64748b;
    font-size: 0.8rem;
    margin-top: 3px;
}

/* Upgrade Banner */
.upgrade-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15));
    border: 1px solid rgba(99, 102, 241, 0.4);
    border-radius: 12px;
    padding: 12px 16px;
    text-align: center;
    color: #a5b4fc;
    font-weight: 600;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

/* Word count */
.wc-bar {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 8px;
    padding: 6px 12px;
    color: #64748b;
    font-size: 0.8rem;
    margin-top: 4px;
    display: inline-block;
}

/* Alert / Info overrides */
.stAlert {
    background: rgba(99,102,241,0.08) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #a5b4fc !important;
}

/* Spinner override */
.stSpinner > div {
    border-top-color: #6366f1 !important;
}

/* Divider */
hr {
    border-color: rgba(99, 102, 241, 0.2) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(99,102,241,0.05) !important;
    border: 2px dashed rgba(99,102,241,0.3) !important;
    border-radius: 14px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0f1e; }
::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 3px; }

/* Select boxes */
div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.05) !important;
    border-color: rgba(99,102,241,0.25) !important;
    color: #e2e8f0 !important;
}

/* Metric */
[data-testid="stMetricValue"] {
    color: #6366f1 !important;
    font-weight: 800 !important;
}

[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
}

/* Nav active state - sidebar */
.nav-active {
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.25)) !important;
    border-color: rgba(99,102,241,0.5) !important;
}

/* Compliance ok */
.compliance-ok {
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 8px;
    padding: 8px 12px;
    color: #6ee7b7;
    font-size: 0.85rem;
}

.compliance-warn-box {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 8px;
    padding: 8px 12px;
    color: #fcd34d;
    font-size: 0.85rem;
}

span[data-testid="stIconMaterial"] {
    font-size: 0px !important;
    color: transparent !important;
}
span[data-testid="stIconMaterial"]::before {
    content: "←" !important;
    font-size: 18px !important;
    color: #94a3b8 !important;
    visibility: visible !important;
    display: block !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    logo_img = load_logo("SarSa_Logo_Transparent.png")
    if logo_img:
        st.image(logo_img, use_container_width=True)
    else:
        st.markdown("<h2 style='text-align:center; background: linear-gradient(135deg,#6366f1,#8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight:900;'>SarSa AI</h2>", unsafe_allow_html=True)

    current_ui_lang = st.selectbox("🌐 Language", list(ui_languages.keys()), index=0)
    t = ui_languages[current_ui_lang]

    st.markdown("---")

    # Navigation
    st.markdown("<p style='color:#64748b; font-size:0.75rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;'>NAVIGATION</p>", unsafe_allow_html=True)

    pages = [
        ("generate", t["nav_generate"]),
        ("tools", t["nav_tools"]),
        ("history", t["nav_history"]),
        ("analytics", t["nav_analytics"]),
    ]
    for page_key, page_label in pages:
        if st.button(page_label, key=f"nav_{page_key}"):
            st.session_state.active_page = page_key

    st.markdown("---")

    # Agent Profile (for personalized outputs)
    st.markdown("<p style='color:#64748b; font-size:0.75rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;'>AGENT PROFILE</p>", unsafe_allow_html=True)
    st.session_state.agent_name = st.text_input("👤 Agent Name", value=st.session_state.agent_name, placeholder="Jane Smith")
    st.session_state.agent_company = st.text_input("🏢 Agency / Company", value=st.session_state.agent_company, placeholder="Luxe Realty Group")

    with st.expander("📞 Contact Details"):
        st.session_state.agent_phone = st.text_input("Phone", value=st.session_state.agent_phone, placeholder="+1 555 000 0000")
        st.session_state.agent_email = st.text_input("Email", value=st.session_state.agent_email, placeholder="jane@luxerealty.com")

    st.markdown("---")

    # Property Configuration
    st.markdown(f"<p style='color:#64748b; font-size:0.75rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;'>{t['settings'].upper()}</p>", unsafe_allow_html=True)

    st.session_state.target_lang_input = st.text_input(t["target_lang"], value=st.session_state.target_lang_input)
    st.session_state.prop_type = st.text_input(t["prop_type"], value=st.session_state.prop_type, placeholder=t["ph_prop"])
    st.session_state.price = st.text_input(t["price"], value=st.session_state.price, placeholder=t["ph_price"])
    st.session_state.location = st.text_input(t["location"], value=st.session_state.location, placeholder=t["ph_loc"])

    col_a, col_b = st.columns(2)
    with col_a:
        st.session_state.bedrooms = st.text_input(t["bedrooms"], value=st.session_state.bedrooms, placeholder="3")
    with col_b:
        st.session_state.bathrooms = st.text_input(t["bathrooms"], value=st.session_state.bathrooms, placeholder="2")

    col_c, col_d = st.columns(2)
    with col_c:
        st.session_state.sqft = st.text_input(t["sqft"], value=st.session_state.sqft, placeholder="120")
    with col_d:
        st.session_state.year_built = st.text_input(t["year_built"], value=st.session_state.year_built, placeholder="2020")

    st.session_state.parking = st.text_input(t["parking"], value=st.session_state.parking, placeholder="1")
    st.session_state.amenities = st.text_input(t["amenities"], value=st.session_state.amenities, placeholder="Pool, Gym, Balcony...")

    current_tone_idx = t["tones"].index(st.session_state.tone) if st.session_state.tone in t["tones"] else 0
    st.session_state.tone = st.selectbox(t["tone"], t["tones"], index=current_tone_idx)

    st.session_state.custom_inst = st.text_area(t["custom_inst"], value=st.session_state.custom_inst,
                                                  placeholder=t["custom_inst_ph"], height=80)

    st.markdown("---")

    # Upgrade Banner
    FREE_LIMIT = 10
    remaining = max(0, FREE_LIMIT - st.session_state.generations_today)
    st.markdown(f"""
    <div class='upgrade-banner'>
        {t['upgrade_banner']}<br>
        <span style='color:#c7d2fe; font-size:0.75rem;'>{t['free_remaining']}: <b>{remaining}/{FREE_LIMIT}</b></span>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def build_property_context():
    ctx = f"""
    Property Type: {st.session_state.prop_type or 'Property'}
    Location: {st.session_state.location or 'undisclosed location'}
    Market Price: {st.session_state.price or 'undisclosed'}
    Bedrooms: {st.session_state.bedrooms or 'N/A'}
    Bathrooms: {st.session_state.bathrooms or 'N/A'}
    Size: {st.session_state.sqft or 'N/A'} sqm/sqft
    Year Built: {st.session_state.year_built or 'N/A'}
    Parking: {st.session_state.parking or 'N/A'}
    Amenities: {st.session_state.amenities or 'N/A'}
    Marketing Strategy: {st.session_state.tone or 'Standard Pro'}
    Special Notes: {st.session_state.custom_inst or 'None'}
    Agent: {st.session_state.agent_name or 'the agent'}
    Agency: {st.session_state.agent_company or 'the agency'}
    """
    return ctx

def word_count_bar(text, t):
    wc = len(text.split()) if text else 0
    cc = len(text) if text else 0
    return f"<span class='wc-bar'>📊 {wc} {t['word_count']} · {cc} {t['char_count']}</span>"

def save_listing_to_history():
    entry = {
        "id": str(time.time()),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prop_type": st.session_state.prop_type or "Property",
        "location": st.session_state.location or "Unknown",
        "price": st.session_state.price or "",
        "content": st.session_state.uretilen_ilan,
        "sec1": st.session_state.sec1,
        "sec2": st.session_state.sec2,
        "sec3": st.session_state.sec3,
        "sec4": st.session_state.sec4,
        "sec5": st.session_state.sec5,
        "sec6": st.session_state.sec6,
    }
    st.session_state.saved_listings.insert(0, entry)
    # Keep max 20 listings
    if len(st.session_state.saved_listings) > 20:
        st.session_state.saved_listings = st.session_state.saved_listings[:20]

# ============================================================
# HERO HEADER (Always Visible)
# ============================================================
st.markdown(f"""
<div class='hero-header'>
    <div class='hero-title'>🏢 {t['app_title']}</div>
    <div class='hero-tagline'>{t['tagline']}</div>
    <div style='margin-top:1rem;'>
        <span class='stat-pill'>✨ AI-Powered</span>
        <span class='stat-pill'>🌍 9 Languages</span>
        <span class='stat-pill'>📦 6 Output Types</span>
        <span class='stat-pill'>🛠️ 12 Agent Tools</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# PAGE: GENERATE
# ============================================================
if st.session_state.active_page == "generate":

    uploaded_files = st.file_uploader(
        t["upload_label"],
        type=["jpg", "png", "webp", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        images_for_ai = [Image.open(f) for f in uploaded_files]

        # Photo gallery
        n_cols = min(len(images_for_ai), 5)
        cols = st.columns(n_cols)
        for i, img in enumerate(images_for_ai):
            with cols[i % n_cols]:
                st.image(img, use_container_width=True)
                st.markdown(f"<div style='text-align:center; color:#64748b; font-size:0.75rem;'>Photo {i+1}</div>", unsafe_allow_html=True)

        st.markdown("")

        with st.container():
            st.markdown("<div class='generate-btn'>", unsafe_allow_html=True)
            generate_clicked = st.button(t["btn"], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if generate_clicked:
            FREE_LIMIT = 10
            if st.session_state.generations_today >= FREE_LIMIT:
                st.warning(f"⚠️ Daily free limit reached. Upgrade to Pro for unlimited generations. Contact: hello@sarsa-ai.com")
            else:
                with st.spinner(t["loading"]):
                    ctx = build_property_context()
                    agent_sig = ""
                    if st.session_state.agent_name:
                        agent_sig = f"\n\nAgent Contact: {st.session_state.agent_name} | {st.session_state.agent_phone or ''} | {st.session_state.agent_email or ''} | {st.session_state.agent_company or ''}"

                    expert_prompt = f"""You are SarSa AI — the world's most advanced real estate marketing AI. 
You are a senior luxury real estate copywriter, social media strategist, video director, SEO expert, and marketing consultant rolled into one.

PROPERTY DATA:
{ctx}
TARGET LANGUAGE: {st.session_state.target_lang_input}
{agent_sig}

Analyze all provided photos carefully. Then generate a COMPLETE, PREMIUM marketing package.

Use EXACTLY these section markers:

## SECTION_1 — PRIME LISTING (Sales Copy)
Write a compelling, professional property listing (400-600 words). Include:
- Magnetic headline
- Evocative opening paragraph
- Key features & lifestyle benefits (use vivid, sensory language)
- Location highlights
- Call to action
{agent_sig}

## SECTION_2 — SOCIAL MEDIA KIT
Write 5 separate posts:
📸 INSTAGRAM (Caption with emojis + 25 hashtags, max 2200 chars)
👥 FACEBOOK (Conversational, community-focused, 200-300 words)
💼 LINKEDIN (Professional investment angle, 150-200 words)
🐦 X/TWITTER (Punchy, 280 chars max)
📱 WHATSAPP BROADCAST (Short, direct, includes price & contact)

## SECTION_3 — CINEMATIC VIDEO SCRIPT
Write a full 60-second video script with:
- SCENE-BY-SCENE breakdown (with camera directions)
- VOICEOVER text for each scene
- BACKGROUND MUSIC suggestion
- TITLE CARDS text
- CALL TO ACTION closing

## SECTION_4 — TECHNICAL SPECIFICATIONS
Complete data sheet:
- Property Details Table (all specs)
- Features & Amenities checklist (use ✓)
- Room-by-room breakdown from photos
- Building/complex information
- Legal/ownership notes placeholder
- Energy & utilities notes

## SECTION_5 — EMAIL TEMPLATES
Write 3 professional email templates:
1. BUYER INQUIRY RESPONSE (warm, informative)
2. PRICE REDUCTION ANNOUNCEMENT (urgent but professional)
3. JUST LISTED ANNOUNCEMENT (exciting, FOMO-driven)
Each with Subject Line + Body. Include agent signature if provided.

## SECTION_6 — SEO & HASHTAG PACK
- 15 SEO Keywords (ranked by search volume potential)
- 3 Meta Descriptions (155 chars each)
- 1 Google Ads headline (30 chars) + description (90 chars)
- 30 Instagram hashtags (organized by category: property, location, lifestyle)
- 10 YouTube/Video tags
- 5 Pinterest board suggestions

Write everything in {st.session_state.target_lang_input}. Be specific, premium, and persuasive. Never be generic."""

                    try:
                        response = model.generate_content([expert_prompt] + images_for_ai)
                        raw = response.text
                        st.session_state.uretilen_ilan = raw
                        st.session_state.has_unsaved_changes = False
                        st.session_state.generations_today += 1

                        # Parse sections
                        def extract_section(text, sec_num):
                            pattern = rf"## SECTION_{sec_num}.*?(?=## SECTION_|\Z)"
                            match = re.search(pattern, text, re.DOTALL)
                            if match:
                                chunk = match.group(0)
                                # Remove the header line
                                lines = chunk.strip().split('\n')
                                return '\n'.join(lines[1:]).strip()
                            return ""

                        st.session_state.sec1 = extract_section(raw, 1)
                        st.session_state.sec2 = extract_section(raw, 2)
                        st.session_state.sec3 = extract_section(raw, 3)
                        st.session_state.sec4 = extract_section(raw, 4)
                        st.session_state.sec5 = extract_section(raw, 5)
                        st.session_state.sec6 = extract_section(raw, 6)

                    except Exception as e:
                        st.error(f"{t['error']} {e}")

    else:
        st.markdown(f"""
        <div style='background: rgba(99,102,241,0.05); border: 2px dashed rgba(99,102,241,0.25); border-radius: 16px; padding: 3rem; text-align:center; margin: 1rem 0;'>
            <div style='font-size:3rem; margin-bottom:1rem;'>📸</div>
            <div style='color:#64748b; font-size:1.1rem;'>{t["empty"]}</div>
        </div>
        """, unsafe_allow_html=True)

    # ---- RESULTS ----
    if st.session_state.uretilen_ilan:
        st.markdown("---")

        # Status badge + save button
        col_badge, col_save = st.columns([3, 1])
        with col_badge:
            st.markdown(f"<h3 style='color:#e2e8f0; margin-bottom:0;'>{t['result']}</h3>", unsafe_allow_html=True)
            if st.session_state.has_unsaved_changes:
                st.markdown(f"<span class='badge-unsaved'>{t['unsaved_indicator']}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='badge-saved'>{t['saved_indicator']}</span>", unsafe_allow_html=True)
        with col_save:
            if st.button(t["save_btn"], use_container_width=True):
                st.session_state.has_unsaved_changes = False
                save_listing_to_history()
                st.success(t["saved_msg"])

        # Tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            t["tab_main"], t["tab_social"], t["tab_video"],
            t["tab_tech"], t["tab_email"], t["tab_seo"]
        ])

        sections_data = [
            (tab1, "sec1", t["label_main"]),
            (tab2, "sec2", t["label_social"]),
            (tab3, "sec3", t["label_video"]),
            (tab4, "sec4", t["label_tech"]),
            (tab5, "sec5", t["label_email"]),
            (tab6, "sec6", t["label_seo"]),
        ]

        for tab_obj, sec_key, label in sections_data:
            with tab_obj:
                current_val = st.session_state.get(sec_key, "")
                edited_val = st.text_area(label, value=current_val, height=420, key=f"txt_{sec_key}")

                if edited_val != current_val:
                    st.session_state[sec_key] = edited_val
                    st.session_state.has_unsaved_changes = True

                # Word count
                st.markdown(word_count_bar(edited_val, t), unsafe_allow_html=True)

                # Fair housing check for listing
                if sec_key == "sec1" and edited_val:
                    flagged = check_fair_housing(edited_val)
                    if flagged:
                        st.markdown(f"<div class='compliance-warn-box'>{t['compliance_warn']} {', '.join(flagged)}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='compliance-ok'>{t['compliance_pass']}</div>", unsafe_allow_html=True)

                # Download individual section
                if edited_val:
                    st.download_button(
                        t["download_tab"],
                        data=edited_val,
                        file_name=f"sarsa_{sec_key}_{datetime.now().strftime('%Y%m%d')}.txt",
                        key=f"dl_{sec_key}",
                        use_container_width=True
                    )

        # Download All
        st.markdown("---")
        full_export = f"""SARSA AI — COMPLETE MARKETING PACKAGE
Property: {st.session_state.prop_type} | {st.session_state.location} | {st.session_state.price}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Agent: {st.session_state.agent_name} | {st.session_state.agent_company}
{'='*60}

📝 PRIME LISTING
{'='*60}
{st.session_state.sec1}

📱 SOCIAL MEDIA KIT
{'='*60}
{st.session_state.sec2}

🎬 VIDEO SCRIPT
{'='*60}
{st.session_state.sec3}

⚙️ TECHNICAL SPECIFICATIONS
{'='*60}
{st.session_state.sec4}

📧 EMAIL TEMPLATES
{'='*60}
{st.session_state.sec5}

🔍 SEO & HASHTAG PACK
{'='*60}
{st.session_state.sec6}
"""
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                t["download_all"],
                data=full_export,
                file_name=f"sarsa_complete_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                use_container_width=True
            )
        with dl_col2:
            # Regenerate button
            if st.button(t["regenerate"], use_container_width=True):
                st.session_state.uretilen_ilan = ""
                st.session_state.sec1 = st.session_state.sec2 = st.session_state.sec3 = ""
                st.session_state.sec4 = st.session_state.sec5 = st.session_state.sec6 = ""
                st.rerun()

# ============================================================
# PAGE: AI TOOLS
# ============================================================
elif st.session_state.active_page == "tools":

    st.markdown("<h2 style='color:#e2e8f0; margin-bottom:0.5rem;'>🛠️ AI Power Tools for Real Estate Agents</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;'>Professional tools to run every part of your real estate business.</p>", unsafe_allow_html=True)

    tools = [
        ("email", t["tool_email_title"], t["tool_email_desc"],
         "Generate a professional cold outreach email for a real estate agent.\n\nContext:\n- Agent: {agent}\n- Agency: {company}\n- Tool: Reaching out to potential property sellers in {location}\n- Property focus: {prop_type}\n- Price range: {price}\n\nWrite 2 versions:\n1. Warm, relationship-building approach\n2. Direct, value-focused approach\n\nEach with Subject Line + Body. Sign with agent details."),

        ("objection", t["tool_objection_title"], t["tool_objection_desc"],
         "You are a top real estate sales coach. Create a comprehensive OBJECTION HANDLING GUIDE for real estate agents.\n\nAgent context: {agent}, {company}, location: {location}\n\nCover the 10 most common objections agents face:\n1. 'Your commission is too high'\n2. 'I'll wait until the market improves'\n3. 'I can sell it myself'\n4. 'Another agent offered a lower fee'\n5. 'The price is too high'\n6. 'I need to think about it'\n7. 'I don't need an agent to buy'\n8. 'The property needs too much work'\n9. 'I'm already working with another agent'\n10. 'The neighborhood isn't right for me'\n\nFor each: Acknowledge → Reframe → Close technique. Use professional, confident language."),

        ("cma", t["tool_cma_title"], t["tool_cma_desc"],
         "Create a professional Comparative Market Analysis (CMA) report template for:\n\nProperty: {prop_type}\nLocation: {location}\nAsking Price: {price}\nAgent: {agent} | {company}\n\nInclude:\n1. Executive Summary\n2. Subject Property Overview\n3. Market Conditions Analysis (current trends)\n4. Comparable Sales Analysis framework (3-5 comps template)\n5. Price Per Square Foot Analysis\n6. Days on Market Analysis\n7. Absorption Rate\n8. Recommended Pricing Strategy\n9. Marketing Recommendations\n10. Agent Opinion of Value\n\nMake it professional, data-driven and persuasive. Add placeholder data examples."),

        ("negotiation", t["tool_negotiation_title"], t["tool_negotiation_desc"],
         "Create a comprehensive NEGOTIATION SCRIPT for a real estate agent.\n\nContext:\n- Agent representing: SELLER\n- Property: {prop_type} at {location}\n- Asking price: {price}\n- Agent: {agent} | {company}\n\nWrite a full script covering:\n1. Opening position statement\n2. Anchoring technique\n3. How to respond to lowball offers\n4. How to handle inspection repair requests\n5. How to counter closing cost requests\n6. How to create urgency (multiple offers scenario)\n7. How to negotiate contingency removals\n8. Closing the deal script\n\nInclude exact phrases, tone guidance, and silence strategies."),

        ("bio", t["tool_bio_title"], t["tool_bio_desc"],
         "Write 3 professional real estate agent biography versions:\n\nAgent: {agent}\nAgency/Company: {company}\nLocation/Market: {location}\nContact: {phone} | {email}\n\nVersion 1 — SHORT BIO (50 words): For social media profiles\nVersion 2 — MEDIUM BIO (150 words): For website 'About' page\nVersion 3 — LONG BIO (300 words): For marketing materials, press releases\n\nTone: Professional, trustworthy, personable. Emphasize expertise, local knowledge, and client success. Include a compelling value proposition."),

        ("openhouse", t["tool_openhouse_title"], t["tool_openhouse_desc"],
         "Write a complete OPEN HOUSE PRESENTATION SCRIPT for:\n\nProperty: {prop_type}\nLocation: {location}\nPrice: {price}\nBedrooms: {bedrooms} | Bathrooms: {bathrooms} | Size: {sqft}\nAmenities: {amenities}\nAgent: {agent} | {company}\n\nInclude:\n1. Welcome greeting script (at the door)\n2. Property tour talking points (room by room)\n3. Key selling points to emphasize\n4. How to handle price objections during the tour\n5. Sign-in sheet conversation starter\n6. Closing conversation (getting offers/follow-ups)\n7. Follow-up SMS script (send same evening)\n8. 'Thank you for visiting' email template\n\nMake it warm, engaging and professionally scripted."),

        ("followup", t["tool_followup_title"], t["tool_followup_desc"],
         "Create a complete POST-VIEWING FOLLOW-UP SEQUENCE for:\n\nProperty: {prop_type} at {location} | Price: {price}\nAgent: {agent} | {company} | {phone} | {email}\n\nWrite:\n1. SMS follow-up (send 2 hours after viewing) — max 160 chars\n2. WhatsApp follow-up (more friendly, include emoji)\n3. Email Day 1: Warm follow-up with property details\n4. Email Day 3: Value-add (neighborhood info, market stats)\n5. Email Day 7: 'Still interested?' gentle nudge\n6. Email Day 14: Final follow-up / price update alert\n7. Call script outline for Day 2 phone call\n\nTone: Helpful, not pushy. Build trust and value at every touchpoint."),

        ("checklist", t["tool_checklist_title"], t["tool_checklist_desc"],
         "Create a COMPLETE REAL ESTATE TRANSACTION CHECKLIST.\n\nCreate two comprehensive checklists:\n\n🏠 SELLER'S TRANSACTION CHECKLIST\nFrom 'Decide to Sell' to 'Close of Escrow' — every step, document, and task.\n\n🔑 BUYER'S TRANSACTION CHECKLIST\nFrom 'Start Search' to 'Move-In Day' — every step, document, and deadline.\n\nFor each item include:\n✓ Task description\n✓ Who is responsible (Buyer/Seller/Agent/Lender/Title)\n✓ Typical timeline\n✓ Key notes/warnings\n\nMake it comprehensive — at least 30 items per checklist. Format clearly with sections."),

        ("neighborhood", t["tool_neighborhood_title"], t["tool_neighborhood_desc"],
         "Write a detailed NEIGHBORHOOD GUIDE for buyers considering:\n\nLocation: {location}\nProperty Type: {prop_type}\nPrice Range: {price}\nPrepared by: {agent} | {company}\n\nInclude:\n1. Area Overview & Character\n2. Transportation & Commute\n3. Schools & Education\n4. Shopping & Restaurants\n5. Healthcare & Medical\n6. Parks & Recreation\n7. Safety & Community\n8. Market Trends & Investment Outlook\n9. 'What Locals Love About This Area'\n10. Upcoming Development & Future Growth\n\nMake it informative, positive but honest. Add a professional disclaimer at the end."),

        ("investment", t["tool_investment_title"], t["tool_investment_desc"],
         "Create a professional REAL ESTATE INVESTMENT ANALYSIS for:\n\nProperty: {prop_type}\nLocation: {location}\nPurchase Price: {price}\nBedrooms: {bedrooms} | Size: {sqft}\nAgent: {agent} | {company}\n\nInclude:\n1. Investment Summary\n2. Purchase Cost Breakdown (price, fees, taxes estimate)\n3. Rental Income Potential (estimated monthly/annual)\n4. Gross Rental Yield calculation\n5. Estimated Operating Expenses\n6. Net Operating Income (NOI)\n7. Cap Rate Analysis\n8. Cash-on-Cash Return (assuming 20% down)\n9. 5-Year Appreciation Projection\n10. Break-Even Analysis\n11. Exit Strategy Options\n12. Risk Factors\n\nUse placeholder numbers. Format as a professional investment memo."),

        ("press", t["tool_press_title"], t["tool_press_desc"],
         "Write a professional PRESS RELEASE for:\n\nAgency: {company}\nAgent: {agent}\nProperty: {prop_type} at {location}\nPrice: {price}\nContact: {phone} | {email}\nDate: {date}\n\nWrite 2 press releases:\n\n1. PROPERTY LAUNCH PRESS RELEASE\n- Headline (punchy, newsworthy)\n- Dateline\n- Opening paragraph (who, what, where, when, why)\n- Property details & highlights\n- Quote from agent\n- About the agency\n- Media contact info\n\n2. MARKET UPDATE PRESS RELEASE\n- Market conditions headline\n- Market statistics framework\n- Expert commentary section\n- Agency positioning\n- Call to action\n\nAP style formatting. Professional and newsworthy tone."),
    ]

    # Tool selector
    tool_cols = st.columns(3)
    for idx, (tool_key, tool_title, tool_desc, _) in enumerate(tools):
        with tool_cols[idx % 3]:
            st.markdown(f"""
            <div class='tool-card'>
                <div class='tool-card-title'>{tool_title}</div>
                <div class='tool-card-desc'>{tool_desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Generate →", key=f"tool_btn_{tool_key}", use_container_width=True):
                with st.spinner(f"✨ Generating {tool_title}..."):
                    ctx = build_property_context()
                    # Build context substitutions
                    tool_prompt = tools[idx][3].format(
                        agent=st.session_state.agent_name or "the agent",
                        company=st.session_state.agent_company or "the agency",
                        location=st.session_state.location or "the area",
                        prop_type=st.session_state.prop_type or "property",
                        price=st.session_state.price or "market price",
                        bedrooms=st.session_state.bedrooms or "N/A",
                        bathrooms=st.session_state.bathrooms or "N/A",
                        sqft=st.session_state.sqft or "N/A",
                        amenities=st.session_state.amenities or "various amenities",
                        phone=st.session_state.agent_phone or "contact number",
                        email=st.session_state.agent_email or "email address",
                        date=datetime.now().strftime("%B %d, %Y"),
                    )
                    full_prompt = f"Write everything in {st.session_state.target_lang_input}.\n\n{tool_prompt}"
                    try:
                        response = model.generate_content(full_prompt)
                        st.session_state.tool_output = response.text
                        st.session_state.tool_output_title = tool_title
                    except Exception as e:
                        st.error(f"{t['error']} {e}")

    # Show tool output
    if st.session_state.get("tool_output"):
        st.markdown("---")
        st.markdown(f"<h3 style='color:#e2e8f0;'>{st.session_state.get('tool_output_title', 'Output')}</h3>", unsafe_allow_html=True)
        tool_edited = st.text_area("", value=st.session_state.tool_output, height=500, key="tool_output_area")
        st.markdown(word_count_bar(tool_edited, t), unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "📥 Download",
                data=tool_edited,
                file_name=f"sarsa_tool_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                use_container_width=True
            )
        with col_b:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.tool_output = ""
                st.rerun()

# ============================================================
# PAGE: HISTORY
# ============================================================
elif st.session_state.active_page == "history":

    st.markdown(f"<h2 style='color:#e2e8f0;'>{t['history_title']}</h2>", unsafe_allow_html=True)

    if not st.session_state.saved_listings:
        st.markdown(f"""
        <div style='background: rgba(99,102,241,0.05); border: 2px dashed rgba(99,102,241,0.2); border-radius: 16px; padding: 3rem; text-align:center;'>
            <div style='font-size:3rem; margin-bottom:1rem;'>📁</div>
            <div style='color:#64748b;'>{t['history_empty']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color:#64748b;'>{len(st.session_state.saved_listings)} saved listing(s)</p>", unsafe_allow_html=True)

        for i, entry in enumerate(st.session_state.saved_listings):
            with st.expander(f"🏢 {entry['prop_type']} — {entry['location']} | {entry['price']} | {entry['date']}"):
                tab_h1, tab_h2, tab_h3 = st.tabs(["📝 Listing", "📱 Social", "🎬 Video"])

                with tab_h1:
                    st.text_area("", value=entry.get("sec1", entry.get("content", "")), height=300, key=f"h_sec1_{i}")
                with tab_h2:
                    st.text_area("", value=entry.get("sec2", ""), height=300, key=f"h_sec2_{i}")
                with tab_h3:
                    st.text_area("", value=entry.get("sec3", ""), height=300, key=f"h_sec3_{i}")

                col_load, col_dl, col_del = st.columns(3)
                with col_load:
                    if st.button(t["load_btn"], key=f"load_{i}", use_container_width=True):
                        st.session_state.uretilen_ilan = entry.get("content", "")
                        st.session_state.sec1 = entry.get("sec1", "")
                        st.session_state.sec2 = entry.get("sec2", "")
                        st.session_state.sec3 = entry.get("sec3", "")
                        st.session_state.sec4 = entry.get("sec4", "")
                        st.session_state.sec5 = entry.get("sec5", "")
                        st.session_state.sec6 = entry.get("sec6", "")
                        st.session_state.active_page = "generate"
                        st.rerun()
                with col_dl:
                    export_data = f"""SARSA AI EXPORT
{entry['prop_type']} | {entry['location']} | {entry['price']}
Saved: {entry['date']}

{entry.get('content', entry.get('sec1', ''))}"""
                    st.download_button("📥 Download", data=export_data,
                                       file_name=f"sarsa_{entry['id']}.txt",
                                       key=f"dl_h_{i}", use_container_width=True)
                with col_del:
                    if st.button(t["delete_btn"], key=f"del_{i}", use_container_width=True):
                        st.session_state.saved_listings.pop(i)
                        st.rerun()

# ============================================================
# PAGE: ANALYTICS
# ============================================================
elif st.session_state.active_page == "analytics":

    st.markdown(f"<h2 style='color:#e2e8f0;'>{t['analytics_title']}</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🚀 Generations Today", st.session_state.generations_today)
    with col2:
        st.metric("📁 Saved Listings", len(st.session_state.saved_listings))
    with col3:
        FREE_LIMIT = 10
        st.metric("🔓 Free Credits Left", max(0, FREE_LIMIT - st.session_state.generations_today))
    with col4:
        st.metric("🌍 Languages Available", "9")

    st.markdown("---")

    # Quick tips
    st.markdown("<h3 style='color:#e2e8f0;'>💡 Pro Tips for Maximum Results</h3>", unsafe_allow_html=True)

    tips = [
        ("📸", "Upload 5-10 high quality photos (exterior + each room) for the best AI output"),
        ("🌅", "Always include the best exterior/view shot as the FIRST photo uploaded"),
        ("📍", "Fill in ALL configuration fields — more data = better, more specific content"),
        ("🎯", "Choose the right Strategy for your market (Ultra-Luxury for premium properties)"),
        ("✍️", "Use Special Notes to mention any unique features not visible in photos"),
        ("💾", "Save every generation to History so you can reuse and compare outputs"),
        ("🔄", "Not happy? Regenerate — each generation is unique and may be even better"),
        ("📧", "Always add your Agent Profile for branded, personalized outputs"),
        ("🔍", "Use the SEO Pack tab to optimize your Zillow/MLS/website listings"),
        ("🛠️", "Explore AI Tools for client emails, negotiation scripts and more daily workflows"),
    ]

    for emoji, tip in tips:
        st.markdown(f"""
        <div class='feature-card' style='padding: 1rem;'>
            <span style='font-size:1.3rem;'>{emoji}</span>
            <span style='color:#94a3b8; font-size:0.9rem; margin-left:10px;'>{tip}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.25); border-radius: 16px; padding: 2rem; text-align:center;'>
        <div style='color:#a5b4fc; font-size:1.3rem; font-weight:800; margin-bottom:0.5rem;'>🚀 Ready to Go Pro?</div>
        <div style='color:#64748b; font-size:0.9rem; margin-bottom:1rem;'>Unlimited generations · Priority AI · PDF exports · Team accounts · White-label options</div>
        <div style='color:#6366f1; font-weight:700;'>Contact us: hello@sarsa-ai.com</div>
    </div>
    """, unsafe_allow_html=True)
