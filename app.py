import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
import re
from datetime import datetime

# --- AI CONFIG ---
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="SarSa AI | Real Estate Intelligence Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOGO LOADER ---
@st.cache_data
def load_logo(file_path):
    if os.path.exists(file_path):
        return Image.open(file_path)
    return None

# --- LANGUAGE SYSTEM ---
ui_languages = {
    "English": {
        "title": "SarSa AI | Real Estate Intelligence Platform",
        "service_desc": "All-in-One Visual Property Intelligence & Global Sales Automation",
        "subtitle": "Transform property photos into premium listings, social media kits, cinematic video scripts, email sequences, technical specs & SEO packs — instantly.",
        "settings": "⚙️ Configuration",
        "target_lang": "✍️ Write Listing In...",
        "prop_type": "Property Type", "price": "Market Price", "location": "Location",
        "beds": "Bedrooms", "baths": "Bathrooms", "sqm": "Size (m²)",
        "year": "Year Built", "parking": "Parking", "amenities": "Key Features",
        "tone": "Strategy",
        "tones": ["Standard Pro", "Ultra-Luxury", "Investment Potential", "Modern Minimalist", "Family Comfort", "Vacation Rental", "New Development", "Commercial"],
        "custom_inst": "📝 Special Notes",
        "agent_section": "👤 Agent Profile",
        "agent_name": "Your Name", "agent_co": "Agency / Company",
        "agent_phone": "Phone", "agent_email": "Email",
        "ph_prop": "E.g., 3+1 Apartment, Luxury Villa...",
        "ph_price": "E.g., $500,000 or £2,000/mo...",
        "ph_loc": "E.g., Manhattan, NY or London, UK...",
        "ph_beds": "e.g. 3", "ph_baths": "e.g. 2", "ph_sqm": "e.g. 150",
        "ph_year": "e.g. 2020", "ph_park": "e.g. 1 garage",
        "ph_amen": "e.g. Pool, gym, sea view",
        "custom_inst_ph": "E.g., High ceilings, near metro...",
        "ph_an": "e.g. Sarah Johnson", "ph_ac": "e.g. Luxe Realty Group",
        "ph_ap": "e.g. +1 305 000 0000", "ph_ae": "e.g. sarah@luxerealty.com",
        "btn": "🚀 GENERATE COMPLETE MARKETING PACKAGE",
        "upload_label": "📸 Drop Property Photos Here",
        "result": "💎 Your Marketing Package",
        "loading": "Crafting your premium marketing package...",
        "empty": "Awaiting visuals to start professional analysis.",
        "download": "📥 Export Full Package",
        "dl_section": "📥 Download",
        "save_btn": "💾 Save to History",
        "saved_msg": "✅ Saved to history!",
        "error": "Error:",
        "nav_gen": "🏠 Generate", "nav_tools": "⚡ Agent Tools", "nav_hist": "📁 History",
        "tab1": "📝 Prime Listing", "tab2": "📱 Social Media Kit",
        "tab3": "🎬 Video Script", "tab4": "⚙️ Technical Specs",
        "tab5": "📧 Email Templates", "tab6": "🔍 SEO Pack",
        "lbl1": "Sales Copy", "lbl2": "Social Media Content",
        "lbl3": "Video Script", "lbl4": "Technical Specifications",
        "lbl5": "Email Templates", "lbl6": "SEO & Digital Pack",
        "words": "words", "chars": "chars",
        "fh_ok": "✅ Fair housing check — no issues",
        "fh_warn": "⚠️ Review flagged terms: ",
        "copy_btn": "📋 Copy", "copied": "✅ Copied!",
        "regen": "🔄 Regenerate",
        "tools_title": "⚡ AI Agent Power Tools",
        "tools_sub": "Professional tools for real estate agents — one click, instant results.",
        "tool_run": "▶ Generate", "tool_clear": "✕ Clear",
        "hist_title": "📁 Saved Listings",
        "hist_empty": "No saved listings yet. Generate and save your first one.",
        "hist_load": "Load", "hist_del": "Delete", "hist_dl": "Download",
    },
    "Türkçe": {
        "title": "SarSa AI | Gayrimenkul Zeka Platformu",
        "service_desc": "Hepsi Bir Arada Görsel Mülk Zekası ve Küresel Satış Otomasyonu",
        "subtitle": "Mülk fotoğraflarını anında profesyonel ilanlara, sosyal medya kitlerine, video senaryolarına, e-posta şablonlarına ve SEO paketine dönüştürün.",
        "settings": "⚙️ Yapılandırma",
        "target_lang": "✍️ İlan Yazım Dili...",
        "prop_type": "Emlak Tipi", "price": "Pazar Fiyatı", "location": "Konum",
        "beds": "Yatak Odası", "baths": "Banyo", "sqm": "Alan (m²)",
        "year": "Yapım Yılı", "parking": "Otopark", "amenities": "Özellikler",
        "tone": "Strateji",
        "tones": ["Standart Pro", "Ultra-Lüks", "Yatırım Potansiyeli", "Modern Minimalist", "Aile Konforu", "Tatil Kiralaması", "Yeni Proje", "Ticari"],
        "custom_inst": "📝 Özel Notlar",
        "agent_section": "👤 Temsilci Profili",
        "agent_name": "Adınız", "agent_co": "Acente / Şirket",
        "agent_phone": "Telefon", "agent_email": "E-posta",
        "ph_prop": "Örn: 3+1 Daire, Müstakil Villa...",
        "ph_price": "Örn: 5.000.000 TL veya $2.500/ay...",
        "ph_loc": "Örn: Beşiktaş, İstanbul...",
        "ph_beds": "örn. 3", "ph_baths": "örn. 2", "ph_sqm": "örn. 150",
        "ph_year": "örn. 2020", "ph_park": "örn. 1 kapalı garaj",
        "ph_amen": "örn. Havuz, spor salonu, deniz manzarası",
        "custom_inst_ph": "Örn: Yüksek tavanlar, metroya yakın...",
        "ph_an": "örn. Ayşe Kaya", "ph_ac": "örn. Lüks Emlak A.Ş.",
        "ph_ap": "örn. +90 532 000 0000", "ph_ae": "örn. ayse@luksemalik.com",
        "btn": "🚀 TAM PAZARLAMA PAKETİ OLUŞTUR",
        "upload_label": "📸 Fotoğrafları Buraya Bırakın",
        "result": "💎 Pazarlama Paketiniz",
        "loading": "Premium pazarlama paketiniz hazırlanıyor...",
        "empty": "Profesyonel analiz için görsel bekleniyor.",
        "download": "📥 Tam Paketi İndir",
        "dl_section": "📥 İndir",
        "save_btn": "💾 Geçmişe Kaydet",
        "saved_msg": "✅ Geçmişe kaydedildi!",
        "error": "Hata:",
        "nav_gen": "🏠 Oluştur", "nav_tools": "⚡ Araçlar", "nav_hist": "📁 Geçmiş",
        "tab1": "📝 Ana İlan", "tab2": "📱 Sosyal Medya",
        "tab3": "🎬 Video Senaryosu", "tab4": "⚙️ Teknik Özellikler",
        "tab5": "📧 E-postalar", "tab6": "🔍 SEO Paketi",
        "lbl1": "Satış Metni", "lbl2": "Sosyal Medya İçeriği",
        "lbl3": "Video Senaryosu", "lbl4": "Teknik Özellikler",
        "lbl5": "E-posta Şablonları", "lbl6": "SEO & Dijital Paket",
        "words": "kelime", "chars": "karakter",
        "fh_ok": "✅ Adil konut kontrolü — sorun yok",
        "fh_warn": "⚠️ İşaretlenen terimleri inceleyin: ",
        "copy_btn": "📋 Kopyala", "copied": "✅ Kopyalandı!",
        "regen": "🔄 Yeniden Oluştur",
        "tools_title": "⚡ AI Ajan Güç Araçları",
        "tools_sub": "Emlak profesyonelleri için araçlar — tek tıkla anında sonuç.",
        "tool_run": "▶ Oluştur", "tool_clear": "✕ Temizle",
        "hist_title": "📁 Kayıtlı İlanlar",
        "hist_empty": "Henüz kayıtlı ilan yok.",
        "hist_load": "Yükle", "hist_del": "Sil", "hist_dl": "İndir",
    },
    "Español": {
        "title": "SarSa AI | Motor de Inteligencia Inmobiliaria",
        "service_desc": "Inteligencia Visual de Propiedades y Automatización de Ventas Globales",
        "subtitle": "Convierte fotos en anuncios premium, kits de redes, guiones de video, emails y SEO al instante.",
        "settings": "⚙️ Configuración",
        "target_lang": "✍️ Escribir en...",
        "prop_type": "Tipo de Propiedad", "price": "Precio de Mercado", "location": "Ubicación",
        "beds": "Habitaciones", "baths": "Baños", "sqm": "Superficie (m²)",
        "year": "Año", "parking": "Garaje", "amenities": "Características",
        "tone": "Estrategia",
        "tones": ["Profesional Estándar", "Ultra-Lujo", "Potencial de Inversión", "Minimalista Moderno", "Confort Familiar", "Alquiler Vacacional", "Nueva Construcción", "Comercial"],
        "custom_inst": "📝 Notas Especiales",
        "agent_section": "👤 Perfil del Agente",
        "agent_name": "Tu Nombre", "agent_co": "Agencia / Empresa",
        "agent_phone": "Teléfono", "agent_email": "Email",
        "ph_prop": "Ej: Apartamento 3+1, Villa de Lujo...",
        "ph_price": "Ej: $500.000 o €1.500/mes...",
        "ph_loc": "Ej: Madrid, España...",
        "ph_beds": "ej. 3", "ph_baths": "ej. 2", "ph_sqm": "ej. 150",
        "ph_year": "ej. 2020", "ph_park": "ej. 1 garaje",
        "ph_amen": "ej. Piscina, gimnasio, vistas al mar",
        "custom_inst_ph": "Ej: Techos altos, cerca del metro...",
        "ph_an": "ej. Carlos García", "ph_ac": "ej. Luxe Realty Group",
        "ph_ap": "ej. +34 600 000 000", "ph_ae": "ej. carlos@luxerealty.es",
        "btn": "🚀 GENERAR PAQUETE DE MARKETING COMPLETO",
        "upload_label": "📸 Subir Fotos Aquí",
        "result": "💎 Tu Paquete de Marketing",
        "loading": "Creando tu paquete de marketing premium...",
        "empty": "Esperando imágenes para análisis profesional.",
        "download": "📥 Exportar Paquete Completo",
        "dl_section": "📥 Descargar",
        "save_btn": "💾 Guardar en Historial",
        "saved_msg": "✅ ¡Guardado!",
        "error": "Error:",
        "nav_gen": "🏠 Generar", "nav_tools": "⚡ Herramientas", "nav_hist": "📁 Historial",
        "tab1": "📝 Anuncio Premium", "tab2": "📱 Kit de Redes",
        "tab3": "🎬 Guión de Vídeo", "tab4": "⚙️ Especificaciones",
        "tab5": "📧 Emails", "tab6": "🔍 SEO",
        "lbl1": "Texto de Ventas", "lbl2": "Contenido Social",
        "lbl3": "Guión de Vídeo", "lbl4": "Ficha Técnica",
        "lbl5": "Plantillas de Email", "lbl6": "Pack SEO & Digital",
        "words": "palabras", "chars": "caracteres",
        "fh_ok": "✅ Vivienda justa — sin problemas",
        "fh_warn": "⚠️ Revisar términos: ",
        "copy_btn": "📋 Copiar", "copied": "✅ ¡Copiado!",
        "regen": "🔄 Regenerar",
        "tools_title": "⚡ Herramientas IA para Agentes",
        "tools_sub": "Herramientas profesionales — un clic, resultados instantáneos.",
        "tool_run": "▶ Generar", "tool_clear": "✕ Limpiar",
        "hist_title": "📁 Listados Guardados",
        "hist_empty": "Aún no hay listados guardados.",
        "hist_load": "Cargar", "hist_del": "Eliminar", "hist_dl": "Descargar",
    },
    "Deutsch": {
        "title": "SarSa AI | Immobilien-Intelligenz-Plattform",
        "service_desc": "All-in-One Visuelle Objektintelligenz & Globale Verkaufsautomatisierung",
        "subtitle": "Verwandeln Sie Fotos sofort in Premium-Exposés, Social-Media-Kits, Videoskripte, E-Mails und SEO-Pakete.",
        "settings": "⚙️ Konfiguration",
        "target_lang": "✍️ Erstellen in...",
        "prop_type": "Objekttyp", "price": "Marktpreis", "location": "Standort",
        "beds": "Zimmer", "baths": "Bad", "sqm": "Fläche (m²)",
        "year": "Baujahr", "parking": "Stellplatz", "amenities": "Merkmale",
        "tone": "Strategie",
        "tones": ["Standard-Profi", "Ultra-Luxus", "Investitionspotenzial", "Modern-Minimalistisch", "Familienkomfort", "Ferienmiete", "Neubau", "Gewerbe"],
        "custom_inst": "📝 Notizen",
        "agent_section": "👤 Makler-Profil",
        "agent_name": "Ihr Name", "agent_co": "Agentur / Firma",
        "agent_phone": "Telefon", "agent_email": "E-Mail",
        "ph_prop": "Z.B. 3-Zimmer-Wohnung, Luxusvilla...",
        "ph_price": "Z.B. 500.000€ oder 2.000€/Monat...",
        "ph_loc": "Z.B. Berlin, Deutschland...",
        "ph_beds": "z.B. 3", "ph_baths": "z.B. 2", "ph_sqm": "z.B. 150",
        "ph_year": "z.B. 2020", "ph_park": "z.B. 1 Tiefgarage",
        "ph_amen": "z.B. Pool, Gym, Meerblick",
        "custom_inst_ph": "Z.B. Hohe Decken, U-Bahn-Nähe...",
        "ph_an": "z.B. Thomas Müller", "ph_ac": "z.B. Luxe Realty GmbH",
        "ph_ap": "z.B. +49 89 000 0000", "ph_ae": "z.B. thomas@luxerealty.de",
        "btn": "🚀 KOMPLETTES MARKETING-PAKET ERSTELLEN",
        "upload_label": "📸 Fotos hier hochladen",
        "result": "💎 Ihr Marketing-Paket",
        "loading": "Ihr Marketing-Paket wird erstellt...",
        "empty": "Warte auf Bilder für die Analyse.",
        "download": "📥 Gesamtpaket exportieren",
        "dl_section": "📥 Herunterladen",
        "save_btn": "💾 Im Verlauf speichern",
        "saved_msg": "✅ Gespeichert!",
        "error": "Fehler:",
        "nav_gen": "🏠 Erstellen", "nav_tools": "⚡ Makler-Tools", "nav_hist": "📁 Verlauf",
        "tab1": "📝 Premium-Exposé", "tab2": "📱 Social Media Kit",
        "tab3": "🎬 Videoskripte", "tab4": "⚙️ Tech-Details",
        "tab5": "📧 E-Mails", "tab6": "🔍 SEO-Paket",
        "lbl1": "Verkaufstext", "lbl2": "Social Media Content",
        "lbl3": "Video-Skript", "lbl4": "Technische Daten",
        "lbl5": "E-Mail-Vorlagen", "lbl6": "SEO & Digital-Paket",
        "words": "Wörter", "chars": "Zeichen",
        "fh_ok": "✅ Fairness-Check — keine Probleme",
        "fh_warn": "⚠️ Prüfen: ",
        "copy_btn": "📋 Kopieren", "copied": "✅ Kopiert!",
        "regen": "🔄 Neu erstellen",
        "tools_title": "⚡ KI-Tools für Makler",
        "tools_sub": "Professionelle Tools — ein Klick, sofortige Ergebnisse.",
        "tool_run": "▶ Erstellen", "tool_clear": "✕ Löschen",
        "hist_title": "📁 Gespeicherte Objekte",
        "hist_empty": "Noch keine gespeicherten Objekte.",
        "hist_load": "Laden", "hist_del": "Löschen", "hist_dl": "Herunterladen",
    },
    "Français": {
        "title": "SarSa AI | Plateforme d'Intelligence Immobilière",
        "service_desc": "Intelligence Visuelle Immobilière et Automatisation des Ventes Globales",
        "subtitle": "Transformez vos photos en annonces premium, kits réseaux sociaux, scripts vidéo, emails et SEO instantanément.",
        "settings": "⚙️ Configuration",
        "target_lang": "✍️ Rédiger en...",
        "prop_type": "Type de Bien", "price": "Prix du Marché", "location": "Localisation",
        "beds": "Chambres", "baths": "SDB", "sqm": "Surface (m²)",
        "year": "Année", "parking": "Parking", "amenities": "Équipements",
        "tone": "Stratégie",
        "tones": ["Standard Pro", "Ultra-Luxe", "Potentiel d'Investissement", "Minimaliste Moderne", "Confort Familial", "Location Vacances", "Neuf", "Commercial"],
        "custom_inst": "📝 Notes Spéciales",
        "agent_section": "👤 Profil Agent",
        "agent_name": "Votre Nom", "agent_co": "Agence / Société",
        "agent_phone": "Téléphone", "agent_email": "Email",
        "ph_prop": "Ex: Appartement T4, Villa de Luxe...",
        "ph_price": "Ex: 500.000€ ou 1.500€/mois...",
        "ph_loc": "Ex: Paris, France...",
        "ph_beds": "ex. 3", "ph_baths": "ex. 2", "ph_sqm": "ex. 150",
        "ph_year": "ex. 2020", "ph_park": "ex. 1 garage",
        "ph_amen": "ex. Piscine, sport, vue mer",
        "custom_inst_ph": "Ex: Plafonds hauts, proche métro...",
        "ph_an": "ex. Marie Dupont", "ph_ac": "ex. Luxe Realty France",
        "ph_ap": "ex. +33 6 00 00 00 00", "ph_ae": "ex. marie@luxerealty.fr",
        "btn": "🚀 GÉNÉRER LE PACK MARKETING COMPLET",
        "upload_label": "📸 Déposer les Photos Ici",
        "result": "💎 Votre Pack Marketing",
        "loading": "Préparation de votre pack marketing premium...",
        "empty": "En attente d'images pour analyse.",
        "download": "📥 Exporter le Pack Complet",
        "dl_section": "📥 Télécharger",
        "save_btn": "💾 Sauvegarder",
        "saved_msg": "✅ Sauvegardé !",
        "error": "Erreur :",
        "nav_gen": "🏠 Générer", "nav_tools": "⚡ Outils Agent", "nav_hist": "📁 Historique",
        "tab1": "📝 Annonce Premium", "tab2": "📱 Kit Réseaux Sociaux",
        "tab3": "🎬 Scripts Vidéo", "tab4": "⚙️ Spécifications",
        "tab5": "📧 Emails", "tab6": "🔍 SEO",
        "lbl1": "Texte de Vente", "lbl2": "Contenu Social",
        "lbl3": "Script Vidéo", "lbl4": "Détails Techniques",
        "lbl5": "Templates Email", "lbl6": "Pack SEO & Digital",
        "words": "mots", "chars": "caractères",
        "fh_ok": "✅ Logement équitable — OK",
        "fh_warn": "⚠️ Vérifier: ",
        "copy_btn": "📋 Copier", "copied": "✅ Copié !",
        "regen": "🔄 Régénérer",
        "tools_title": "⚡ Outils IA pour Agents",
        "tools_sub": "Outils professionnels — un clic, résultats instantanés.",
        "tool_run": "▶ Générer", "tool_clear": "✕ Effacer",
        "hist_title": "📁 Biens Sauvegardés",
        "hist_empty": "Aucun bien sauvegardé.",
        "hist_load": "Charger", "hist_del": "Supprimer", "hist_dl": "Télécharger",
    },
    "Português": {
        "title": "SarSa AI | Motor de Inteligência Imobiliária",
        "service_desc": "Inteligência Visual Imobiliária e Automação de Vendas Globais",
        "subtitle": "Transforme fotos em anúncios premium, kits de redes sociais, roteiros de vídeo, emails e SEO instantaneamente.",
        "settings": "⚙️ Configuração",
        "target_lang": "✍️ Escrever em...",
        "prop_type": "Tipo de Imóvel", "price": "Preço de Mercado", "location": "Localização",
        "beds": "Quartos", "baths": "WC", "sqm": "Área (m²)",
        "year": "Ano", "parking": "Garagem", "amenities": "Características",
        "tone": "Estratégia",
        "tones": ["Profissional Padrão", "Ultra-Luxo", "Potencial de Investimento", "Minimalista Moderno", "Conforto Familiar", "Férias", "Nova Construção", "Comercial"],
        "custom_inst": "📝 Notas Especiais",
        "agent_section": "👤 Perfil do Agente",
        "agent_name": "O Seu Nome", "agent_co": "Agência / Empresa",
        "agent_phone": "Telefone", "agent_email": "Email",
        "ph_prop": "Ex: Apartamento T3, Moradia de Luxo...",
        "ph_price": "Ex: 500.000€ ou 1.500€/mês...",
        "ph_loc": "Ex: Lisboa, Portugal...",
        "ph_beds": "ex. 3", "ph_baths": "ex. 2", "ph_sqm": "ex. 150",
        "ph_year": "ex. 2020", "ph_park": "ex. 1 garagem",
        "ph_amen": "ex. Piscina, ginásio, vista mar",
        "custom_inst_ph": "Ex: Tetos altos, perto do metrô...",
        "ph_an": "ex. Ana Silva", "ph_ac": "ex. Luxe Realty Portugal",
        "ph_ap": "ex. +351 91 000 0000", "ph_ae": "ex. ana@luxerealty.pt",
        "btn": "🚀 GERAR PACOTE DE MARKETING COMPLETO",
        "upload_label": "📸 Enviar Fotos Aqui",
        "result": "💎 O Seu Pacote de Marketing",
        "loading": "Preparando seu pacote de marketing premium...",
        "empty": "Aguardando imagens para análise.",
        "download": "📥 Exportar Pacote Completo",
        "dl_section": "📥 Descarregar",
        "save_btn": "💾 Guardar no Histórico",
        "saved_msg": "✅ Guardado!",
        "error": "Erro:",
        "nav_gen": "🏠 Gerar", "nav_tools": "⚡ Ferramentas", "nav_hist": "📁 Histórico",
        "tab1": "📝 Anúncio Premium", "tab2": "📱 Kit Redes Sociais",
        "tab3": "🎬 Roteiros de Vídeo", "tab4": "⚙️ Especificações",
        "tab5": "📧 Emails", "tab6": "🔍 SEO",
        "lbl1": "Texto de Vendas", "lbl2": "Conteúdo Social",
        "lbl3": "Script de Vídeo", "lbl4": "Especificações Técnicas",
        "lbl5": "Templates de Email", "lbl6": "Pack SEO & Digital",
        "words": "palavras", "chars": "caracteres",
        "fh_ok": "✅ Habitação justa — sem problemas",
        "fh_warn": "⚠️ Rever: ",
        "copy_btn": "📋 Copiar", "copied": "✅ Copiado!",
        "regen": "🔄 Regenerar",
        "tools_title": "⚡ Ferramentas IA para Agentes",
        "tools_sub": "Ferramentas profissionais — um clique, resultados instantâneos.",
        "tool_run": "▶ Gerar", "tool_clear": "✕ Limpar",
        "hist_title": "📁 Imóveis Guardados",
        "hist_empty": "Ainda sem imóveis guardados.",
        "hist_load": "Carregar", "hist_del": "Apagar", "hist_dl": "Descarregar",
    },
    "日本語": {
        "title": "SarSa AI | 不動産インテリジェンスプラットフォーム",
        "service_desc": "オールインワン物件インテリジェンス＆グローバル販売自動化",
        "subtitle": "物件写真をプレミアム広告、SNSキット、動画台本、メールテンプレート、SEOパックに瞬時に変換。",
        "settings": "⚙️ 設定",
        "target_lang": "✍️ 作成言語...",
        "prop_type": "物件種別", "price": "市場価格", "location": "所在地",
        "beds": "寝室", "baths": "浴室", "sqm": "面積 (㎡)",
        "year": "築年", "parking": "駐車場", "amenities": "特徴・設備",
        "tone": "戦略",
        "tones": ["スタンダードプロ", "ウルトララグジュアリー", "投資ポテンシャル", "モダンミニマリスト", "ファミリーコンフォート", "バケーション", "新築", "商業"],
        "custom_inst": "📝 特記事項",
        "agent_section": "👤 エージェントプロフィール",
        "agent_name": "お名前", "agent_co": "会社・代理店",
        "agent_phone": "電話", "agent_email": "メール",
        "ph_prop": "例：3LDKマンション、高級別荘...",
        "ph_price": "例：5000万円、月20万円...",
        "ph_loc": "例：東京都港区...",
        "ph_beds": "例. 3", "ph_baths": "例. 2", "ph_sqm": "例. 150",
        "ph_year": "例. 2020", "ph_park": "例. 1台",
        "ph_amen": "例. プール、ジム、海景",
        "custom_inst_ph": "例：高い天井、駅近...",
        "ph_an": "例. 田中 太郎", "ph_ac": "例. ラックスリアルティ",
        "ph_ap": "例. +81 3 0000 0000", "ph_ae": "例. tanaka@luxerealty.jp",
        "btn": "🚀 完全なマーケティングパッケージを生成",
        "upload_label": "📸 ここに写真をアップロード",
        "result": "💎 マーケティングパッケージ",
        "loading": "プレミアムマーケティングパッケージを構築中...",
        "empty": "分析用の画像を待機中。",
        "download": "📥 パッケージ全体をエクスポート",
        "dl_section": "📥 ダウンロード",
        "save_btn": "💾 履歴に保存",
        "saved_msg": "✅ 保存しました！",
        "error": "エラー:",
        "nav_gen": "🏠 生成", "nav_tools": "⚡ エージェントツール", "nav_hist": "📁 履歴",
        "tab1": "📝 プレミアム広告", "tab2": "📱 SNSキット",
        "tab3": "🎬 動画台本", "tab4": "⚙️ 技術仕様",
        "tab5": "📧 メール", "tab6": "🔍 SEOパック",
        "lbl1": "セールスコピー", "lbl2": "SNSコンテンツ",
        "lbl3": "動画台本", "lbl4": "技術仕様",
        "lbl5": "メールテンプレート", "lbl6": "SEO＆デジタルパック",
        "words": "語", "chars": "文字",
        "fh_ok": "✅ 公正住宅 — 問題なし",
        "fh_warn": "⚠️ 要確認: ",
        "copy_btn": "📋 コピー", "copied": "✅ コピー完了！",
        "regen": "🔄 再生成",
        "tools_title": "⚡ AIエージェントツール",
        "tools_sub": "不動産プロ向けツール — ワンクリックで即プロ品質。",
        "tool_run": "▶ 生成", "tool_clear": "✕ クリア",
        "hist_title": "📁 保存済み物件",
        "hist_empty": "まだ保存された物件がありません。",
        "hist_load": "読込", "hist_del": "削除", "hist_dl": "ダウンロード",
    },
    "中文 (简体)": {
        "title": "SarSa AI | 房地产智能平台",
        "service_desc": "全方位房产视觉智能与全球销售自动化",
        "subtitle": "立即将房产照片转化为优质房源描述、社交媒体包、视频脚本、邮件模板和SEO套件。",
        "settings": "⚙️ 配置",
        "target_lang": "✍️ 编写语言...",
        "prop_type": "房产类型", "price": "市场价格", "location": "地点",
        "beds": "卧室", "baths": "浴室", "sqm": "面积 (㎡)",
        "year": "建造年份", "parking": "车位", "amenities": "主要特征",
        "tone": "策略",
        "tones": ["标准专业", "顶奢豪宅", "投资潜力", "现代简约", "家庭舒适", "度假租赁", "新开发", "商业"],
        "custom_inst": "📝 特别备注",
        "agent_section": "👤 经纪人资料",
        "agent_name": "您的姓名", "agent_co": "中介 / 公司",
        "agent_phone": "电话", "agent_email": "邮箱",
        "ph_prop": "如 豪华别墅、3室2厅...",
        "ph_price": "如 $500,000 或 $2,000/月...",
        "ph_loc": "如 上海市浦东新区...",
        "ph_beds": "如. 3", "ph_baths": "如. 2", "ph_sqm": "如. 150",
        "ph_year": "如. 2020", "ph_park": "如. 1个车位",
        "ph_amen": "如. 泳池、健身房、海景",
        "custom_inst_ph": "如：挑高天花板，靠近地铁...",
        "ph_an": "如. 张伟", "ph_ac": "如. 豪华地产集团",
        "ph_ap": "如. +86 138 0000 0000", "ph_ae": "如. zhang@luxerealty.cn",
        "btn": "🚀 生成完整营销套餐",
        "upload_label": "📸 在此处上传照片",
        "result": "💎 您的营销套餐",
        "loading": "正在打造您的高端营销套餐...",
        "empty": "等待图像进行分析。",
        "download": "📥 导出完整套餐",
        "dl_section": "📥 下载",
        "save_btn": "💾 保存到历史",
        "saved_msg": "✅ 已保存！",
        "error": "错误:",
        "nav_gen": "🏠 生成", "nav_tools": "⚡ 经纪人工具", "nav_hist": "📁 历史",
        "tab1": "📝 优质房源", "tab2": "📱 社交媒体包",
        "tab3": "🎬 视频脚本", "tab4": "⚙️ 技术细节",
        "tab5": "📧 邮件模板", "tab6": "🔍 SEO套件",
        "lbl1": "销售文案", "lbl2": "社媒内容",
        "lbl3": "视频脚本", "lbl4": "技术规格",
        "lbl5": "邮件模板", "lbl6": "SEO与数字营销包",
        "words": "词", "chars": "字符",
        "fh_ok": "✅ 公平住房 — 无问题",
        "fh_warn": "⚠️ 请检查: ",
        "copy_btn": "📋 复制", "copied": "✅ 已复制！",
        "regen": "🔄 重新生成",
        "tools_title": "⚡ AI经纪人工具箱",
        "tools_sub": "专业工具 — 一键即得专业成果。",
        "tool_run": "▶ 生成", "tool_clear": "✕ 清除",
        "hist_title": "📁 已保存房源",
        "hist_empty": "还没有保存的房源。",
        "hist_load": "加载", "hist_del": "删除", "hist_dl": "下载",
    },
    "العربية": {
        "title": "SarSa AI | منصة الذكاء العقاري",
        "service_desc": "ذكاء العقارات البصري المتكامل وأتمتة المبيعات العالمية",
        "subtitle": "حوّل صور العقارات إلى إعلانات مميزة، باقات التواصل الاجتماعي، سيناريوهات الفيديو، البريد الإلكتروني وحزم SEO فوراً.",
        "settings": "⚙️ الإعدادات",
        "target_lang": "✍️ لغة الكتابة...",
        "prop_type": "نوع العقار", "price": "سعر السوق", "location": "الموقع",
        "beds": "غرف النوم", "baths": "الحمامات", "sqm": "المساحة (م²)",
        "year": "سنة البناء", "parking": "موقف السيارات", "amenities": "المميزات",
        "tone": "الاستراتيجية",
        "tones": ["احترافي قياسي", "فخامة فائقة", "إمكانات استثمارية", "عصري بسيط", "راحة عائلية", "إيجار عطلات", "مشروع جديد", "تجاري"],
        "custom_inst": "📝 ملاحظات خاصة",
        "agent_section": "👤 ملف الوكيل",
        "agent_name": "اسمك", "agent_co": "الوكالة / الشركة",
        "agent_phone": "الهاتف", "agent_email": "البريد الإلكتروني",
        "ph_prop": "مثال: شقة 3+1، فيلا فاخرة...",
        "ph_price": "مثال: $500,000 أو $2,000 شهرياً...",
        "ph_loc": "مثال: دبي، الإمارات...",
        "ph_beds": "مثال. 3", "ph_baths": "مثال. 2", "ph_sqm": "مثال. 150",
        "ph_year": "مثال. 2020", "ph_park": "مثال. موقف مغطى",
        "ph_amen": "مثال. مسبح، صالة رياضية، إطلالة بحرية",
        "custom_inst_ph": "مثال: أسقف عالية، بالقرب من المترو...",
        "ph_an": "مثال. محمد الأحمد", "ph_ac": "مثال. مجموعة لوكس العقارية",
        "ph_ap": "مثال. +971 50 000 0000", "ph_ae": "مثال. m@luxerealty.ae",
        "btn": "🚀 إنشاء حزمة تسويقية متكاملة",
        "upload_label": "📸 ضع الصور هنا",
        "result": "💎 حزمتك التسويقية",
        "loading": "جاري تجهيز حزمتك التسويقية الفاخرة...",
        "empty": "في انتظار الصور لبدء التحليل المهني.",
        "download": "📥 تصدير الحزمة الكاملة",
        "dl_section": "📥 تحميل",
        "save_btn": "💾 حفظ في السجل",
        "saved_msg": "✅ تم الحفظ!",
        "error": "خطأ:",
        "nav_gen": "🏠 إنشاء", "nav_tools": "⚡ أدوات الوكيل", "nav_hist": "📁 السجل",
        "tab1": "📝 إعلان مميز", "tab2": "📱 باقة التواصل",
        "tab3": "🎬 سيناريوهات الفيديو", "tab4": "⚙️ تفاصيل",
        "tab5": "📧 البريد الإلكتروني", "tab6": "🔍 حزمة SEO",
        "lbl1": "نص المبيعات", "lbl2": "محتوى التواصل",
        "lbl3": "سيناريو الفيديو", "lbl4": "المواصفات الفنية",
        "lbl5": "قوالب البريد الإلكتروني", "lbl6": "حزمة SEO الرقمية",
        "words": "كلمة", "chars": "حرف",
        "fh_ok": "✅ الإسكان العادل — لا مشاكل",
        "fh_warn": "⚠️ راجع المصطلحات: ",
        "copy_btn": "📋 نسخ", "copied": "✅ تم النسخ!",
        "regen": "🔄 إعادة الإنشاء",
        "tools_title": "⚡ أدوات الوكيل بالذكاء الاصطناعي",
        "tools_sub": "أدوات احترافية — نقرة واحدة، نتائج فورية.",
        "tool_run": "▶ إنشاء", "tool_clear": "✕ مسح",
        "hist_title": "📁 العقارات المحفوظة",
        "hist_empty": "لا توجد عقارات محفوظة بعد.",
        "hist_load": "تحميل", "hist_del": "حذف", "hist_dl": "تحميل",
    },
}

# --- SESSION STATE ---
for key, val in [
    ("page", "generate"),
    ("uretilen_ilan", ""), ("s1",""), ("s2",""), ("s3",""), ("s4",""), ("s5",""), ("s6",""),
    ("output_ready", False),
    ("history", []),
    ("tool_out", ""), ("tool_title", ""),
    ("prop_type", ""), ("price", ""), ("location", ""),
    ("beds", ""), ("baths", ""), ("sqm", ""), ("year_built", ""),
    ("parking", ""), ("amenities", ""), ("custom_inst", ""),
    ("tone", ""), ("target_lang_input", "English"),
    ("agent_name", ""), ("agent_co", ""), ("agent_phone", ""), ("agent_email", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# --- CSS: YOUR ORIGINAL STYLE + ENHANCEMENTS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');
html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background-color: #f8fafc; }

div[data-testid="stInputInstructions"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
span[data-testid="stIconMaterial"] { display: none !important; }

.block-container {
    background: white;
    padding: 2.5rem 3rem !important;
    border-radius: 20px;
    box-shadow: 0 15px 45px rgba(0,0,0,0.04);
    margin-top: 1.5rem;
    border: 1px solid #e2e8f0;
}
h1 { color: #0f172a !important; font-weight: 800 !important; text-align: center; }

button, [data-baseweb="tab"], [data-testid="stFileUploader"],
div[data-baseweb="select"], div[role="button"], .stSelectbox div {
    cursor: pointer !important;
}
.stTextInput input, .stTextArea textarea { cursor: text !important; }

.stButton > button {
    background: #0f172a;
    color: white !important;
    border-radius: 10px;
    padding: 12px 20px;
    font-weight: 700;
    width: 100%;
    border: none;
    font-size: 0.9rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #1e293b;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    transform: translateY(-1px);
}

.stDownloadButton > button {
    background: white !important;
    color: #0f172a !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    border-color: #0f172a !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9;
    border-radius: 12px;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.82rem;
    color: #64748b;
    padding: 8px 14px;
    white-space: nowrap;
}
.stTabs [aria-selected="true"] {
    background-color: #0f172a !important;
    color: white !important;
    border-radius: 8px;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

.stTextArea textarea {
    border-radius: 12px;
    border: 1.5px solid #e2e8f0;
    font-size: 0.9rem;
    line-height: 1.7;
    background: #fafafa;
    transition: border-color 0.2s;
}
.stTextArea textarea:focus {
    border-color: #0f172a !important;
    box-shadow: 0 0 0 3px rgba(15,23,42,0.06) !important;
    background: white;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #0f172a, #334155) !important;
}

/* NAV BUTTONS */
div.nav-active > div > button,
div.nav-active > div[data-testid="stButton"] > button {
    background: #0f172a !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(15,23,42,0.2) !important;
}
div.nav-inactive > div > button,
div.nav-inactive > div[data-testid="stButton"] > button {
    background: #f1f5f9 !important;
    color: #475569 !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: none !important;
}
div.nav-inactive > div > button:hover,
div.nav-inactive > div[data-testid="stButton"] > button:hover {
    background: #e2e8f0 !important;
    color: #0f172a !important;
}

/* COPY BTN */
.sarsa-copy-btn {
    display: block; width: 100%;
    background: white; color: #0f172a;
    border: 2px solid #e2e8f0; border-radius: 10px;
    padding: 8px 16px; font-size: 0.85rem; font-weight: 600;
    font-family: 'Plus Jakarta Sans', sans-serif;
    cursor: pointer; transition: all 0.2s; text-align: center;
}
.sarsa-copy-btn:hover { border-color: #0f172a; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

/* STAT CHIPS */
.sarsa-chips { display: flex; gap: 8px; margin: 8px 0 12px; flex-wrap: wrap; }
.sarsa-chip {
    background: #f1f5f9; color: #64748b;
    font-size: 0.72rem; font-weight: 600;
    padding: 3px 10px; border-radius: 20px;
    border: 1px solid #e2e8f0;
}
.sarsa-fh-ok {
    display: inline-flex; align-items: center; gap: 5px;
    background: #f0fdf4; color: #16a34a;
    border: 1px solid #bbf7d0; border-radius: 20px;
    padding: 3px 12px; font-size: 0.75rem; font-weight: 600;
    margin: 5px 0 12px;
}
.sarsa-fh-warn {
    display: inline-flex; align-items: center; gap: 5px;
    background: #fffbeb; color: #d97706;
    border: 1px solid #fde68a; border-radius: 20px;
    padding: 3px 12px; font-size: 0.75rem; font-weight: 600;
    margin: 5px 0 12px;
}

/* TOOL CARDS */
.sarsa-tool-card {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.6rem;
    transition: all 0.2s;
}
.sarsa-tool-card:hover { border-color: #94a3b8; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.sarsa-tool-name { font-weight: 700; font-size: 0.95rem; color: #0f172a; margin-bottom: 4px; }
.sarsa-tool-desc { font-size: 0.8rem; color: #64748b; line-height: 1.4; }

/* HISTORY CARDS */
.sarsa-hist-card {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.55rem;
}

/* SECTION DIVIDER */
.sarsa-divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }

/* EMPTY STATE */
.sarsa-empty {
    background: #f8fafc;
    border: 2px dashed #e2e8f0;
    border-radius: 16px;
    padding: 4rem 2rem;
    text-align: center;
    margin-top: 0.5rem;
}
.sarsa-empty-icon { font-size: 2.5rem; margin-bottom: 0.8rem; }
.sarsa-empty-title { font-size: 1.2rem; font-weight: 700; color: #0f172a; margin-bottom: 0.3rem; }
.sarsa-empty-sub { font-size: 0.88rem; color: #94a3b8; }

/* RESULT HEADER */
.sarsa-result-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem; }
.sarsa-result-title { font-size: 1.4rem; font-weight: 800; color: #0f172a; }
</style>
""", unsafe_allow_html=True)

# --- HELPERS ---
FAIR_HOUSING_TERMS = [
    "adults only", "no children", "white neighborhood",
    "christian neighborhood", "english speaking only", "families only",
]

def check_fair_housing(text):
    tl = text.lower()
    return [term for term in FAIR_HOUSING_TERMS if term in tl]

def extract_section(raw, n):
    m = re.search(rf"##\s*SECTION_{n}.*?(?=##\s*SECTION_|\Z)", raw, re.DOTALL | re.IGNORECASE)
    if not m:
        return ""
    lines = m.group(0).strip().splitlines()
    return "\n".join(lines[1:]).strip()

def build_prompt(lang, strategy):
    ss = st.session_state
    agent_parts = [x for x in [ss.agent_name, ss.agent_co, ss.agent_phone, ss.agent_email] if x]
    agent_info = " | ".join(agent_parts) if agent_parts else "not provided"
    prop_block = f"""Property: {ss.prop_type or 'Residential Property'} | Location: {ss.location or 'Undisclosed'} | Price: {ss.price or 'Price on Request'}
Beds: {ss.beds or 'N/A'} | Baths: {ss.baths or 'N/A'} | Size: {ss.sqm or 'N/A'} m² | Year: {ss.year_built or 'N/A'} | Parking: {ss.parking or 'N/A'}
Features: {ss.amenities or 'TBC'} | Notes: {ss.custom_inst or 'None'}
Agent: {agent_info}"""
    return f"""You are SarSa AI — the world's most advanced real estate marketing platform.
PROPERTY DATA:
{prop_block}
STRATEGY: {strategy}
OUTPUT LANGUAGE: {lang} — write ALL content in this language.

Carefully analyse every uploaded photo. Note architecture, finishes, light, views, condition.

Generate a COMPLETE 6-section package. Use EXACTLY these markers:

## SECTION_1 — PRIME LISTING COPY
450–650 words. ALL-CAPS headline → emotional opening (3–4 sentences) → living spaces (reference photos) → kitchen/bathrooms → outdoor/amenities → location highlights → value proposition → CTA with agent contact.

## SECTION_2 — SOCIAL MEDIA KIT
📸 INSTAGRAM: Full caption (up to 2200 chars) + 25 hashtags
👥 FACEBOOK: 200–280 words, community-focused, price prominent
💼 LINKEDIN: 150–200 words, investment angle
🐦 X/TWITTER: Max 270 chars + 4 hashtags
📱 WHATSAPP: Max 155 chars, price + feature + contact

## SECTION_3 — CINEMATIC VIDEO SCRIPT
Title card → 7 scenes each with [CAMERA:] [VOICEOVER:] [DURATION:] → Music direction → Closing card with agent details → YouTube description (150 words) + 10 tags

## SECTION_4 — TECHNICAL SPECIFICATIONS
Key specs table → Room-by-room from photos → Amenities checklist (✓/—) → Building notes → Legal placeholder → Contact info

## SECTION_5 — EMAIL TEMPLATES
📧 EMAIL 1 — JUST LISTED: Subject + 150–200 word body + signature
📧 EMAIL 2 — POST-VIEWING: Subject + 120–150 word body + signature
📧 EMAIL 3 — PRICE REDUCTION: Subject + 110–130 word body + signature

## SECTION_6 — SEO & DIGITAL MARKETING
20 ranked SEO keywords → 3 meta descriptions (155 chars each with CTA) → Google Ads (3 headlines 30 chars, 2 descriptions 90 chars) → Instagram hashtags by category → 10 YouTube tags → 5 Pinterest board names → Posting calendar (best day + time per platform)

Write every word in {lang}. Reference real photo details. Zero generic filler."""

def save_to_history():
    ss = st.session_state
    entry = {
        "id": str(datetime.now().timestamp()),
        "date": datetime.now().strftime("%d %b %Y · %H:%M"),
        "prop": ss.prop_type or "Property",
        "loc": ss.location or "—",
        "price": ss.price or "—",
        "s1": ss.s1, "s2": ss.s2, "s3": ss.s3,
        "s4": ss.s4, "s5": ss.s5, "s6": ss.s6,
    }
    ss.history.insert(0, entry)
    if len(ss.history) > 50:
        ss.history = ss.history[:50]

def full_export():
    ss = st.session_state
    out = f"SARSA AI — COMPLETE MARKETING PACKAGE\n{'='*60}\n"
    out += f"Property: {ss.prop_type} | {ss.location} | {ss.price}\n"
    out += f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}\n{'='*60}\n\n"
    for i in range(1, 7):
        out += f"{'─'*60}\nSECTION {i}\n{'─'*60}\n{ss.get(f's{i}','')}\n\n"
    return out

def copy_btn(text, lbl, lbl_done, uid):
    safe = text.replace("\\","\\\\").replace("`","\\`").replace("$","\\$").replace("'","\\'")
    l1 = lbl.replace("'","\\'"); l2 = lbl_done.replace("'","\\'")
    st.markdown(f"""<button class='sarsa-copy-btn' id='cpb_{uid}'
      onclick="navigator.clipboard.writeText(`{safe}`).then(()=>{{
        var b=document.getElementById('cpb_{uid}');b.textContent='{l2}';
        setTimeout(()=>b.textContent='{l1}',2000);}})">
    {l1}</button>""", unsafe_allow_html=True)

def render_section(sk, fname, show_fhc=False):
    val = st.session_state.get(sk, "")
    new = st.text_area("", value=val, height=480, key=f"ta_{sk}", label_visibility="collapsed")
    if new != val:
        st.session_state[sk] = new
    w = len(new.split()) if new else 0
    c = len(new) if new else 0
    st.markdown(f"<div class='sarsa-chips'><span class='sarsa-chip'>📊 {w} {t['words']}</span><span class='sarsa-chip'>✏️ {c} {t['chars']}</span></div>", unsafe_allow_html=True)
    if show_fhc and new:
        flags = check_fair_housing(new)
        if flags:
            st.markdown(f"<div class='sarsa-fh-warn'>{t['fh_warn']}{', '.join(flags)}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='sarsa-fh-ok'>{t['fh_ok']}</div>", unsafe_allow_html=True)
    bc1, bc2 = st.columns(2)
    with bc1:
        st.download_button(t["dl_section"], data=new,
            file_name=f"sarsa_{fname}_{datetime.now().strftime('%Y%m%d')}.txt",
            key=f"dl_{sk}", use_container_width=True)
    with bc2:
        copy_btn(new, t["copy_btn"], t["copied"], sk)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — YOUR ORIGINAL STRUCTURE + NEW FIELDS
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    logo_img = load_logo("SarSa_Logo_Transparent.png")
    if logo_img:
        st.image(logo_img, use_container_width=True)
    else:
        st.markdown("<h2 style='text-align:center; color:#0f172a;'>SARSA AI</h2>", unsafe_allow_html=True)

    current_ui_lang = st.selectbox("🌐 Interface Language", list(ui_languages.keys()), index=0)
    t = ui_languages[current_ui_lang]

    st.markdown("---")

    # Navigation
    st.markdown("**Navigation**")
    for pid, plabel in [("generate", t["nav_gen"]), ("tools", t["nav_tools"]), ("history", t["nav_hist"])]:
        css = "nav-active" if st.session_state.page == pid else "nav-inactive"
        st.markdown(f"<div class='{css}'>", unsafe_allow_html=True)
        if st.button(plabel, key=f"nav_{pid}", use_container_width=True):
            st.session_state.page = pid
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header(t["settings"])

    st.session_state.target_lang_input = st.text_input(t["target_lang"], value=st.session_state.target_lang_input)
    st.session_state.prop_type = st.text_input(t["prop_type"], value=st.session_state.prop_type, placeholder=t["ph_prop"])
    st.session_state.price = st.text_input(t["price"], value=st.session_state.price, placeholder=t["ph_price"])
    st.session_state.location = st.text_input(t["location"], value=st.session_state.location, placeholder=t["ph_loc"])

    c1, c2 = st.columns(2)
    with c1: st.session_state.beds = st.text_input(t["beds"], value=st.session_state.beds, placeholder=t["ph_beds"])
    with c2: st.session_state.baths = st.text_input(t["baths"], value=st.session_state.baths, placeholder=t["ph_baths"])
    c3, c4 = st.columns(2)
    with c3: st.session_state.sqm = st.text_input(t["sqm"], value=st.session_state.sqm, placeholder=t["ph_sqm"])
    with c4: st.session_state.year_built = st.text_input(t["year"], value=st.session_state.year_built, placeholder=t["ph_year"])

    st.session_state.parking = st.text_input(t["parking"], value=st.session_state.parking, placeholder=t["ph_park"])
    st.session_state.amenities = st.text_input(t["amenities"], value=st.session_state.amenities, placeholder=t["ph_amen"])

    strats = t["tones"]
    current_tone_idx = strats.index(st.session_state.tone) if st.session_state.tone in strats else 0
    st.session_state.tone = st.selectbox(t["tone"], strats, index=current_tone_idx)
    st.session_state.custom_inst = st.text_area(t["custom_inst"], value=st.session_state.custom_inst, placeholder=t["custom_inst_ph"])

    st.markdown("---")
    st.subheader(t["agent_section"])
    st.session_state.agent_name = st.text_input(t["agent_name"], value=st.session_state.agent_name, placeholder=t["ph_an"])
    st.session_state.agent_co = st.text_input(t["agent_co"], value=st.session_state.agent_co, placeholder=t["ph_ac"])
    st.session_state.agent_phone = st.text_input(t["agent_phone"], value=st.session_state.agent_phone, placeholder=t["ph_ap"])
    st.session_state.agent_email = st.text_input(t["agent_email"], value=st.session_state.agent_email, placeholder=t["ph_ae"])


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: GENERATE
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "generate":

    st.markdown(f"<h1>🏢 {t['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#0f172a; font-weight:700; font-size:1.3rem; letter-spacing:0.3px; margin-bottom:5px;'>{t['service_desc']}</p>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; color:#64748b; font-size:1rem; max-width:800px; margin: 0 auto 2rem auto; line-height:1.6;'>{t['subtitle']}</div>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(t["upload_label"], type=["jpg","png","webp","jpeg"], accept_multiple_files=True)

    if uploaded_files:
        images_for_ai = [Image.open(f) for f in uploaded_files]
        cols = st.columns(min(len(images_for_ai), 4))
        for i, img in enumerate(images_for_ai):
            with cols[i % 4]:
                st.image(img, use_container_width=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button(t["btn"], use_container_width=True):
            strategy = st.session_state.tone or t["tones"][0]
            prompt = build_prompt(st.session_state.target_lang_input or "English", strategy)
            prog = st.progress(0)
            status = st.empty()
            loading_steps = [
                "🔍 Analyzing property photos…",
                "✍️ Writing premium listing copy…",
                "📱 Building social media kit…",
                "🎬 Scripting the video…",
                "⚙️ Compiling technical specs…",
                "📧 Drafting email templates…",
                "🔍 Building SEO pack…",
                "✅ Finalizing your package…",
            ]
            try:
                for i, step in enumerate(loading_steps[:-1]):
                    status.info(step)
                    prog.progress(int((i + 1) / len(loading_steps) * 88))
                status.info(loading_steps[-1])
                response = model.generate_content([prompt] + images_for_ai)
                raw = response.text
                st.session_state.uretilen_ilan = raw
                for n in range(1, 7):
                    st.session_state[f"s{n}"] = extract_section(raw, n)
                st.session_state.output_ready = True
                prog.progress(100)
                status.success("✅ Your marketing package is ready!")
            except Exception as e:
                status.error(f"{t['error']} {e}")
                prog.empty()

    else:
        if not st.session_state.output_ready:
            st.markdown(f"""
            <div class='sarsa-empty'>
                <div class='sarsa-empty-icon'>🏡</div>
                <div class='sarsa-empty-title'>{t['empty_title'] if 'empty_title' in t else t['empty']}</div>
                <div class='sarsa-empty-sub'>Upload property photos · Fill in the details · Hit Generate</div>
            </div>""", unsafe_allow_html=True)

    # OUTPUT
    if st.session_state.output_ready:
        st.markdown("<div class='sarsa-divider'></div>", unsafe_allow_html=True)

        # Result header row
        rc1, rc2, rc3, rc4 = st.columns([3, 1.2, 1.2, 1.4])
        with rc1:
            st.markdown(f"<div class='sarsa-result-title'>{t['result']}</div>", unsafe_allow_html=True)
        with rc2:
            if st.button(t["save_btn"], use_container_width=True, key="save_main"):
                save_to_history()
                st.success(t["saved_msg"])
        with rc3:
            if st.button(t["regen"], use_container_width=True, key="regen_main"):
                for k in ["s1","s2","s3","s4","s5","s6","uretilen_ilan"]:
                    st.session_state[k] = ""
                st.session_state.output_ready = False
                st.rerun()
        with rc4:
            st.download_button(t["download"], data=full_export(),
                file_name=f"sarsa_full_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                key="dl_full", use_container_width=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            t["tab1"], t["tab2"], t["tab3"], t["tab4"], t["tab5"], t["tab6"]])
        with tab1: render_section("s1", "listing",   show_fhc=True)
        with tab2: render_section("s2", "social")
        with tab3: render_section("s3", "video")
        with tab4: render_section("s4", "techspecs")
        with tab5: render_section("s5", "emails")
        with tab6: render_section("s6", "seo")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: AGENT TOOLS
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "tools":

    st.markdown(f"<h1>{t['tools_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#64748b; margin-bottom:1.5rem;'>{t['tools_sub']}</p>", unsafe_allow_html=True)

    ss = st.session_state
    lang  = ss.target_lang_input or "English"
    name  = ss.agent_name  or "the agent"
    co    = ss.agent_co    or "the agency"
    loc   = ss.location    or "the local market"
    prop  = ss.prop_type   or "residential property"
    price = ss.price       or "market price"
    beds  = ss.beds        or "N/A"
    sqm   = ss.sqm         or "N/A"
    phone = ss.agent_phone or "phone not provided"
    email = ss.agent_email or "email not provided"
    today = datetime.now().strftime("%B %d, %Y")

    TOOLS = [
        ("objection","💬 Objection Handler",
         "Master responses to the 10 toughest client objections using FEEL-FELT-FOUND",
         f"You are the world's top real estate sales coach.\nWrite a COMPLETE OBJECTION HANDLING PLAYBOOK.\nAgent: {name} | Agency: {co} | Market: {loc}\nLanguage: {lang}\n\nHandle these 10 objections using FEEL-FELT-FOUND + confident closing line:\n1. 'Your commission is too high'\n2. 'I'll wait for the market to improve'\n3. 'I can sell it myself (FSBO)'\n4. 'Another agent offered a lower fee'\n5. 'The asking price is too high'\n6. 'I need more time to think'\n7. 'We're not in a rush to sell'\n8. 'The property needs too much work'\n9. 'I'm already talking to another agent'\n10. 'I want to try selling privately first'\n\nFormat each: **Bold objection** → FEEL → FELT → FOUND → CLOSING LINE."),
        ("cma","📊 CMA Report Template",
         "Professional comparative market analysis for seller presentations",
         f"Write a COMPARATIVE MARKET ANALYSIS REPORT.\nProperty: {prop} | Location: {loc} | Price: {price}\nPrepared by: {name} | {co}\nLanguage: {lang}\n\nSections: Executive Summary, Subject Property Profile, Market Conditions, 3 Comparable Sales, Price Analysis, Recommended Price, DOM Forecast, Marketing Strategy, Agent Opinion of Value, Disclaimer."),
        ("cold_email","📧 Cold Outreach Emails",
         "Three high-converting prospecting emails for sellers, landlords & expired listings",
         f"Write 3 cold outreach emails.\nAgent: {name} | Agency: {co} | Phone: {phone} | Email: {email}\nTarget area: {loc}\nLanguage: {lang}\n\nEMAIL 1 — POTENTIAL SELLER: Subject + 150-word warm body + signature\nEMAIL 2 — LANDLORD/INVESTOR: Subject + 150-word ROI-angle body + signature\nEMAIL 3 — EXPIRED LISTING: Subject + 130-word empathy + fresh-approach body + signature"),
        ("negotiation","🤝 Negotiation Scripts",
         "Word-for-word scripts for every negotiation scenario agents face",
         f"Write a REAL ESTATE NEGOTIATION SCRIPT PLAYBOOK.\nProperty: {prop} | Location: {loc} | Price: {price}\nAgent: {name} | {co}\nLanguage: {lang}\n\n6 scenarios with Opening Line, 3 Talking Points, Counter Proposal, What NOT to Say, Closing Line:\n1. Responding to a lowball offer\n2. Multiple offers — create urgency\n3. Buyer requests price reduction after inspection\n4. Buyer requests seller pays closing costs\n5. Request to extend closing date\n6. Deal falling apart — save it"),
        ("bio","👤 Agent Biography",
         "Three professional bios: 55-word micro, 160-word standard, 320-word full",
         f"Write 3 professional real estate agent biographies.\nAgent: {name} | Agency: {co} | Market: {loc}\nPhone: {phone} | Email: {email}\nLanguage: {lang}\n\nVERSION 1 — MICRO (55 words): 1st person, for Instagram/business cards\nVERSION 2 — STANDARD (160 words): 3rd person, for website/LinkedIn\nVERSION 3 — FULL (320 words): 3rd person, press/media, include awards placeholder"),
        ("openhouse","🏠 Open House Event Guide",
         "Complete prep checklist, welcome scripts, tour points & same-day follow-ups",
         f"Write a COMPLETE OPEN HOUSE EVENT GUIDE.\nProperty: {prop} | Location: {loc} | Price: {price} | Beds: {beds} | Size: {sqm} m²\nAgent: {name} | Phone: {phone}\nLanguage: {lang}\n\nInclude: Pre-event checklist (12 tasks), Welcome scripts (45 sec + 2 min), Room-by-room tour (8 rooms), Top 6 selling points, 4 price objection responses, Sign-in opener, 5 qualifying questions, Same-day SMS (155 chars), Same-day WhatsApp, Next-day email"),
        ("followup","📞 14-Day Follow-Up Sequence",
         "Complete multi-channel follow-up with every message written out in full",
         f"Write a COMPLETE 14-DAY POST-VIEWING FOLLOW-UP SEQUENCE.\nProperty: {prop} | Location: {loc} | Price: {price}\nAgent: {name} | Phone: {phone} | Email: {email}\nLanguage: {lang}\n\nDay 0: SMS (155 chars) + WhatsApp (200 chars)\nDay 1: Email 150-word warm recap\nDay 3: Email 130-word neighbourhood highlights\nDay 5: SMS check-in\nDay 7: Email 120-word market update\nDay 10: Phone call outline (2-min, 6 points)\nDay 14: Email 100-word final opportunity"),
        ("investment","💰 Investment Analysis Memo",
         "Full ROI, yield and cash flow analysis for investor presentations",
         f"Write a REAL ESTATE INVESTMENT ANALYSIS MEMO.\nProperty: {prop} | Location: {loc} | Price: {price} | Size: {sqm} m²\nPrepared by: {name} | {co}\nLanguage: {lang}\n\nInclude: Snapshot, Acquisition Costs, Rental Income (Airbnb vs long-term), Gross Yield, NOI, Cap Rate, Cash-on-Cash Return, 5-Year Appreciation (3 scenarios), Break-Even, 3 Exit Strategies, 5 Risk Factors, Verdict, Disclaimer."),
        ("checklist","✅ Transaction Checklists",
         "Complete step-by-step buyer and seller transaction checklists (70+ tasks)",
         f"Create REAL ESTATE TRANSACTION CHECKLISTS.\nAgent: {name} | Agency: {co}\nLanguage: {lang}\n\nSELLER CHECKLIST (36+ tasks, 6 phases): Pre-Listing, Active Listing, Offer & Negotiation, Under Contract, Pre-Closing, Closing Day\nBUYER CHECKLIST (33+ tasks, 6 phases): Pre-Search, Property Search, Making Offer, Under Contract, Financing & Inspection, Closing & Moving\nFormat: ☐ Task | Responsible | Notes"),
        ("neighborhood","🗺️ Neighbourhood Guide",
         "Comprehensive buyer's area guide that overcomes location hesitation",
         f"Write a NEIGHBOURHOOD GUIDE FOR BUYERS.\nArea: {loc} | Property: {prop} | Price: {price}\nPrepared by: {name} | {co}\nLanguage: {lang}\n\n10 sections: Area Character, Transport, Schools, Dining/Shopping, Parks, Healthcare, Safety, Property Market, 5 Reasons Locals Love It, Future Growth + Agent Recommendation + Disclaimer."),
        ("press","📰 Press Releases",
         "Two AP-style press releases: property launch and market update",
         f"Write 2 AP-style press releases.\nAgency: {co} | Agent: {name} | Phone: {phone} | Email: {email}\nProperty: {prop} | Location: {loc} | Price: {price} | Date: {today}\nLanguage: {lang}\n\nPR 1 — PROPERTY LAUNCH: FOR IMMEDIATE RELEASE, headline, subheading, dateline, lead, 2 property paragraphs, market context, agent quote, boilerplate, ###, media contact\nPR 2 — MARKET UPDATE: Same structure, market commentary. Both 380–420 words."),
        ("mortgage","🏦 Buyer's Finance Guide",
         "Complete mortgage guide: types, costs, application steps and glossary",
         f"Write a BUYER'S FINANCE AND MORTGAGE GUIDE.\nMarket: {loc}\nPrepared by: {name} | {co}\nLanguage: {lang}\n\n12 sections: Why Finance Planning Matters, Borrowing Capacity, Deposit Requirements, Mortgage Types (comparison table), Complete Buying Costs, Application Process (8 steps), Common Rejection Reasons, First-Time Buyer Advantages, Investor Mortgages, Remortgaging, Glossary (18 terms), Next Steps & Disclaimer."),
    ]

    # Show existing output
    if ss.tool_out:
        st.markdown(f"<div style='background:#f1f5f9;border-radius:10px;padding:0.7rem 1rem;margin-bottom:1rem;font-weight:700;color:#0f172a;'>📄 {ss.tool_title}</div>", unsafe_allow_html=True)
        edited = st.text_area("", value=ss.tool_out, height=500, key="tool_ta", label_visibility="collapsed")
        w = len(edited.split()) if edited else 0
        c = len(edited) if edited else 0
        st.markdown(f"<div class='sarsa-chips'><span class='sarsa-chip'>📊 {w} {t['words']}</span><span class='sarsa-chip'>✏️ {c} {t['chars']}</span></div>", unsafe_allow_html=True)
        tc1, tc2, tc3 = st.columns(3)
        with tc1:
            st.download_button(t["dl_section"], data=edited,
                file_name=f"sarsa_tool_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                key="tool_dl", use_container_width=True)
        with tc2:
            copy_btn(edited, t["copy_btn"], t["copied"], "tool_main")
        with tc3:
            if st.button(t["tool_clear"], use_container_width=True, key="tool_clear"):
                ss.tool_out = ""; ss.tool_title = ""
                st.rerun()
        st.markdown("<div class='sarsa-divider'></div>", unsafe_allow_html=True)

    for i in range(0, len(TOOLS), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(TOOLS): break
            tid, tname, tdesc, tprompt = TOOLS[idx]
            with col:
                st.markdown(f"<div class='sarsa-tool-card'><div class='sarsa-tool-name'>{tname}</div><div class='sarsa-tool-desc'>{tdesc}</div></div>", unsafe_allow_html=True)
                if st.button(t["tool_run"], key=f"tool_{tid}", use_container_width=True):
                    with st.spinner(f"✨ {tname}…"):
                        try:
                            r = model.generate_content(tprompt)
                            ss.tool_out = r.text; ss.tool_title = tname
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t['error']} {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "history":

    hist = st.session_state.get("history", [])
    st.markdown(f"<h1>{t['hist_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#64748b; margin-bottom:1.5rem;'>{len(hist)} saved listing{'s' if len(hist) != 1 else ''}</p>", unsafe_allow_html=True)

    if not hist:
        st.markdown(f"""
        <div class='sarsa-empty'>
            <div class='sarsa-empty-icon'>📁</div>
            <div class='sarsa-empty-title'>{t['hist_title']}</div>
            <div class='sarsa-empty-sub'>{t['hist_empty']}</div>
        </div>""", unsafe_allow_html=True)
    else:
        for i, entry in enumerate(hist):
            label = f"🏢  {entry['prop']}  ·  {entry['loc']}  ·  {entry['price']}  ·  {entry['date']}"
            with st.expander(label, expanded=(i == 0)):
                h_tabs = st.tabs([t["tab1"], t["tab2"], t["tab3"], t["tab4"]])
                for ni, ht in enumerate(h_tabs):
                    with ht:
                        st.text_area("", value=entry.get(f"s{ni+1}",""), height=250,
                            key=f"hs{ni+1}_{i}", label_visibility="collapsed", disabled=True)
                hc1, hc2, hc3 = st.columns(3)
                with hc1:
                    if st.button(t["hist_load"], key=f"hl_{i}", use_container_width=True):
                        for n in range(1, 7):
                            st.session_state[f"s{n}"] = entry.get(f"s{n}", "")
                        st.session_state.output_ready = True
                        st.session_state.page = "generate"
                        st.rerun()
                with hc2:
                    exp = "\n\n".join(entry.get(f"s{n}","") for n in range(1,7))
                    st.download_button(t["hist_dl"], data=exp,
                        file_name=f"sarsa_history_{entry['id'][:8]}.txt",
                        key=f"hd_{i}", use_container_width=True)
                with hc3:
                    if st.button(t["hist_del"], key=f"hdel_{i}", use_container_width=True):
                        st.session_state.history.pop(i)
                        st.rerun()
