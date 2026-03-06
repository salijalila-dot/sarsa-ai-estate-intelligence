import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
import re
from datetime import datetime

# --- AI CONFIG ---
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="SarSa AI | Real Estate Intelligence Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
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
        "title": "SarSa AI", "tagline": "Real Estate Intelligence Platform",
        "subtitle": "Transform property photos into a complete professional marketing suite — listings, social media, video scripts, tech specs, emails & SEO — in seconds.",
        "nav_gen": "🏠  Generate", "nav_tools": "⚡  Agent Tools", "nav_hist": "📁  History",
        "prop_section": "Property Details", "agent_section": "Agent Profile",
        "target_lang": "Output Language", "prop_type": "Property Type", "price": "Asking Price",
        "location": "Location", "beds": "Beds", "baths": "Baths", "sqm": "Size m²",
        "year": "Year Built", "parking": "Parking", "amenities": "Key Features",
        "tone": "Strategy", "notes": "Special Notes",
        "tones": ["⭐ Standard Pro","💎 Ultra-Luxury","📈 Investment","🏡 Family Comfort","🎨 Modern Minimalist","🏖️ Vacation Rental","🏗️ New Development","🏢 Commercial"],
        "agent_name": "Your Name", "agent_co": "Agency / Company", "agent_phone": "Phone", "agent_email": "Email",
        "ph_lang": "e.g. English, French, Arabic…", "ph_prop": "e.g. Luxury Villa, 3-Bed Apartment…",
        "ph_price": "e.g. $850,000 or €2,400/mo", "ph_loc": "e.g. Miami Beach, FL",
        "ph_beds": "3", "ph_baths": "2", "ph_sqm": "150", "ph_year": "2020",
        "ph_park": "1 garage", "ph_amen": "Pool, gym, sea view…",
        "ph_notes": "Renovated kitchen, near metro…",
        "ph_an": "Sarah Johnson", "ph_ac": "Luxe Realty Group",
        "ph_ap": "+1 305 000 0000", "ph_ae": "sarah@luxerealty.com",
        "upload_label": "📸  Drop property photos here — JPG, PNG, WEBP",
        "btn": "✦  GENERATE COMPLETE MARKETING PACKAGE",
        "regen": "↺  Regenerate", "save_hist": "💾  Save to History", "saved_ok": "✅ Saved!",
        "dl_all": "⬇  Download All", "dl": "⬇  Download", "copy": "⎘  Copy", "copied": "✅ Copied!",
        "result_title": "Your Marketing Package",
        "tab1": "📝 Listing", "tab2": "📱 Social Media", "tab3": "🎬 Video Script",
        "tab4": "⚙️ Tech Specs", "tab5": "📧 Emails", "tab6": "🔍 SEO Pack",
        "lbl1": "Prime Listing Copy", "lbl2": "Social Media Kit", "lbl3": "Video Script",
        "lbl4": "Technical Specs", "lbl5": "Email Templates", "lbl6": "SEO & Digital Pack",
        "words": "words", "chars": "chars",
        "fh_ok": "✅ Fair housing — no issues flagged",
        "fh_warn": "⚠️ Review flagged terms: ",
        "unsaved": "● Unsaved edits", "all_saved": "✔ All saved",
        "loading": ["🔍 Analyzing photos…","✍️ Writing listing copy…","📱 Building social kit…",
                    "🎬 Scripting video…","⚙️ Compiling specs…","📧 Drafting emails…","🔍 Building SEO pack…","✅ Finalizing…"],
        "empty_title": "Your marketing package will appear here",
        "empty_sub": "Upload property photos · Fill in details · Hit Generate",
        "photo": "Photo", "error": "Error: ",
        "tools_title": "AI Agent Toolbox", "tools_sub": "One click. Professional output. Instantly.",
        "tool_run": "Generate →", "tool_clear": "✕  Clear", "tool_dl": "⬇  Download",
        "hist_title": "Saved Listings", "hist_empty": "No saved listings yet.",
        "hist_load": "Load", "hist_del": "Delete", "hist_dl": "Download",
    },
    "Türkçe": {
        "title": "SarSa AI", "tagline": "Gayrimenkul Zeka Platformu",
        "subtitle": "Mülk fotoğraflarını saniyeler içinde eksiksiz profesyonel pazarlama paketine dönüştürün.",
        "nav_gen": "🏠  Oluştur", "nav_tools": "⚡  Araçlar", "nav_hist": "📁  Geçmiş",
        "prop_section": "Mülk Bilgileri", "agent_section": "Temsilci Profili",
        "target_lang": "Çıktı Dili", "prop_type": "Emlak Tipi", "price": "Fiyat",
        "location": "Konum", "beds": "Yatak", "baths": "Banyo", "sqm": "m²",
        "year": "Yapım Yılı", "parking": "Otopark", "amenities": "Özellikler",
        "tone": "Strateji", "notes": "Özel Notlar",
        "tones": ["⭐ Standart Pro","💎 Ultra-Lüks","📈 Yatırım","🏡 Aile Konforu","🎨 Modern Minimalist","🏖️ Tatil Kiralaması","🏗️ Yeni Proje","🏢 Ticari"],
        "agent_name": "Adınız", "agent_co": "Acente / Şirket", "agent_phone": "Telefon", "agent_email": "E-posta",
        "ph_lang": "örn. Türkçe, İngilizce…", "ph_prop": "örn. Lüks Villa, 3+1 Daire…",
        "ph_price": "örn. 5.000.000₺ veya $2.500/ay", "ph_loc": "örn. Beşiktaş, İstanbul",
        "ph_beds": "3", "ph_baths": "2", "ph_sqm": "150", "ph_year": "2020",
        "ph_park": "1 garaj", "ph_amen": "Havuz, spor salonu, deniz manzarası…",
        "ph_notes": "Tadilatlı mutfak, metroya yakın…",
        "ph_an": "Ayşe Kaya", "ph_ac": "Lüks Emlak A.Ş.",
        "ph_ap": "+90 532 000 0000", "ph_ae": "ayse@luksemalik.com",
        "upload_label": "📸  Mülk fotoğraflarını buraya bırakın — JPG, PNG, WEBP",
        "btn": "✦  TAM PAZARLAMA PAKETİ OLUŞTUR",
        "regen": "↺  Yeniden Oluştur", "save_hist": "💾  Geçmişe Kaydet", "saved_ok": "✅ Kaydedildi!",
        "dl_all": "⬇  Tümünü İndir", "dl": "⬇  İndir", "copy": "⎘  Kopyala", "copied": "✅ Kopyalandı!",
        "result_title": "Pazarlama Paketiniz",
        "tab1": "📝 İlan", "tab2": "📱 Sosyal Medya", "tab3": "🎬 Video Senaryosu",
        "tab4": "⚙️ Teknik", "tab5": "📧 E-postalar", "tab6": "🔍 SEO",
        "lbl1": "Ana İlan Metni", "lbl2": "Sosyal Medya Kiti", "lbl3": "Video Senaryosu",
        "lbl4": "Teknik Özellikler", "lbl5": "E-posta Şablonları", "lbl6": "SEO & Dijital Paket",
        "words": "kelime", "chars": "karakter",
        "fh_ok": "✅ Adil konut — sorun yok",
        "fh_warn": "⚠️ İşaretlenen terimler: ",
        "unsaved": "● Kaydedilmemiş değişiklikler", "all_saved": "✔ Tümü kaydedildi",
        "loading": ["🔍 Fotoğraflar analiz ediliyor…","✍️ İlan metni yazılıyor…","📱 Sosyal medya kiti oluşturuluyor…",
                    "🎬 Video senaryosu yazılıyor…","⚙️ Teknik özellikler derleniyor…","📧 E-postalar hazırlanıyor…","🔍 SEO paketi oluşturuluyor…","✅ Tamamlanıyor…"],
        "empty_title": "Pazarlama paketiniz burada görünecek",
        "empty_sub": "Fotoğraf yükleyin · Bilgileri doldurun · Oluştur'a basın",
        "photo": "Fotoğraf", "error": "Hata: ",
        "tools_title": "AI Ajan Araç Kutusu", "tools_sub": "Tek tıkla. Anında profesyonel sonuç.",
        "tool_run": "Oluştur →", "tool_clear": "✕  Temizle", "tool_dl": "⬇  İndir",
        "hist_title": "Kayıtlı İlanlar", "hist_empty": "Henüz kayıtlı ilan yok.",
        "hist_load": "Yükle", "hist_del": "Sil", "hist_dl": "İndir",
    },
    "Español": {
        "title": "SarSa AI", "tagline": "Plataforma de Inteligencia Inmobiliaria",
        "subtitle": "Convierte fotos de propiedades en un paquete completo de marketing profesional en segundos.",
        "nav_gen": "🏠  Generar", "nav_tools": "⚡  Herramientas", "nav_hist": "📁  Historial",
        "prop_section": "Detalles Propiedad", "agent_section": "Perfil Agente",
        "target_lang": "Idioma Salida", "prop_type": "Tipo Propiedad", "price": "Precio",
        "location": "Ubicación", "beds": "Hab.", "baths": "Baños", "sqm": "m²",
        "year": "Año", "parking": "Garaje", "amenities": "Características",
        "tone": "Estrategia", "notes": "Notas Especiales",
        "tones": ["⭐ Estándar Pro","💎 Ultra-Lujo","📈 Inversión","🏡 Familiar","🎨 Minimalista","🏖️ Vacacional","🏗️ Nueva Construcción","🏢 Comercial"],
        "agent_name": "Tu Nombre", "agent_co": "Agencia / Empresa", "agent_phone": "Teléfono", "agent_email": "Email",
        "ph_lang": "ej. Español, Inglés…", "ph_prop": "ej. Villa de Lujo, Piso 3 hab…",
        "ph_price": "ej. $850,000 o €2,400/mes", "ph_loc": "ej. Centro de Madrid",
        "ph_beds": "3", "ph_baths": "2", "ph_sqm": "150", "ph_year": "2020",
        "ph_park": "1 garaje", "ph_amen": "Piscina, gimnasio, vistas…",
        "ph_notes": "Cocina reformada, cerca del metro…",
        "ph_an": "Carlos García", "ph_ac": "Luxe Realty Group",
        "ph_ap": "+34 600 000 000", "ph_ae": "carlos@luxerealty.es",
        "upload_label": "📸  Arrastra fotos aquí — JPG, PNG, WEBP",
        "btn": "✦  GENERAR PAQUETE COMPLETO DE MARKETING",
        "regen": "↺  Regenerar", "save_hist": "💾  Guardar", "saved_ok": "✅ ¡Guardado!",
        "dl_all": "⬇  Descargar Todo", "dl": "⬇  Descargar", "copy": "⎘  Copiar", "copied": "✅ ¡Copiado!",
        "result_title": "Tu Paquete de Marketing",
        "tab1": "📝 Anuncio", "tab2": "📱 Redes Sociales", "tab3": "🎬 Guión",
        "tab4": "⚙️ Especificaciones", "tab5": "📧 Emails", "tab6": "🔍 SEO",
        "lbl1": "Texto del Anuncio", "lbl2": "Kit Redes Sociales", "lbl3": "Guión de Vídeo",
        "lbl4": "Especificaciones", "lbl5": "Plantillas Email", "lbl6": "Pack SEO & Digital",
        "words": "palabras", "chars": "caracteres",
        "fh_ok": "✅ Vivienda justa — sin problemas", "fh_warn": "⚠️ Revisar: ",
        "unsaved": "● Cambios sin guardar", "all_saved": "✔ Todo guardado",
        "loading": ["🔍 Analizando fotos…","✍️ Redactando anuncio…","📱 Kit redes…",
                    "🎬 Guión…","⚙️ Especificaciones…","📧 Emails…","🔍 SEO…","✅ Finalizando…"],
        "empty_title": "Tu paquete aparecerá aquí",
        "empty_sub": "Sube fotos · Rellena detalles · Genera",
        "photo": "Foto", "error": "Error: ",
        "tools_title": "Caja de Herramientas IA", "tools_sub": "Un clic. Resultado profesional. Instantáneo.",
        "tool_run": "Generar →", "tool_clear": "✕  Limpiar", "tool_dl": "⬇  Descargar",
        "hist_title": "Listados Guardados", "hist_empty": "Aún no hay listados guardados.",
        "hist_load": "Cargar", "hist_del": "Eliminar", "hist_dl": "Descargar",
    },
    "Deutsch": {
        "title": "SarSa AI", "tagline": "Immobilien-Intelligenz-Plattform",
        "subtitle": "Verwandeln Sie Fotos in Sekunden in ein vollständiges professionelles Marketing-Paket.",
        "nav_gen": "🏠  Erstellen", "nav_tools": "⚡  Makler-Tools", "nav_hist": "📁  Verlauf",
        "prop_section": "Objektdetails", "agent_section": "Makler-Profil",
        "target_lang": "Ausgabesprache", "prop_type": "Objekttyp", "price": "Preis",
        "location": "Standort", "beds": "Zimmer", "baths": "Bad", "sqm": "m²",
        "year": "Baujahr", "parking": "Stellplatz", "amenities": "Merkmale",
        "tone": "Strategie", "notes": "Notizen",
        "tones": ["⭐ Standard-Profi","💎 Ultra-Luxus","📈 Investment","🏡 Familie","🎨 Modern-Minimalistisch","🏖️ Ferienmiete","🏗️ Neubau","🏢 Gewerbe"],
        "agent_name": "Ihr Name", "agent_co": "Agentur / Firma", "agent_phone": "Telefon", "agent_email": "E-Mail",
        "ph_lang": "z.B. Deutsch, Englisch…", "ph_prop": "z.B. Luxusvilla, 3-Zi-Wohnung…",
        "ph_price": "z.B. 850.000€ oder 2.400€/Mo", "ph_loc": "z.B. München Innenstadt",
        "ph_beds": "3", "ph_baths": "2", "ph_sqm": "150", "ph_year": "2020",
        "ph_park": "Tiefgarage", "ph_amen": "Pool, Gym, Meerblick…",
        "ph_notes": "Renovierte Küche, U-Bahn-Nähe…",
        "ph_an": "Thomas Müller", "ph_ac": "Luxe Realty GmbH",
        "ph_ap": "+49 89 000 0000", "ph_ae": "thomas@luxerealty.de",
        "upload_label": "📸  Objektfotos hier ablegen — JPG, PNG, WEBP",
        "btn": "✦  KOMPLETTES MARKETING-PAKET ERSTELLEN",
        "regen": "↺  Neu erstellen", "save_hist": "💾  Im Verlauf speichern", "saved_ok": "✅ Gespeichert!",
        "dl_all": "⬇  Alles herunterladen", "dl": "⬇  Herunterladen", "copy": "⎘  Kopieren", "copied": "✅ Kopiert!",
        "result_title": "Ihr Marketing-Paket",
        "tab1": "📝 Exposé", "tab2": "📱 Social Media", "tab3": "🎬 Videoskript",
        "tab4": "⚙️ Technik", "tab5": "📧 E-Mails", "tab6": "🔍 SEO",
        "lbl1": "Exposé-Text", "lbl2": "Social-Media-Kit", "lbl3": "Video-Skript",
        "lbl4": "Technische Daten", "lbl5": "E-Mail-Vorlagen", "lbl6": "SEO & Digital-Paket",
        "words": "Wörter", "chars": "Zeichen",
        "fh_ok": "✅ Fairness — keine Probleme", "fh_warn": "⚠️ Prüfen: ",
        "unsaved": "● Ungespeicherte Änderungen", "all_saved": "✔ Alles gespeichert",
        "loading": ["🔍 Fotos analysieren…","✍️ Exposé erstellen…","📱 Social-Kit…",
                    "🎬 Videoskript…","⚙️ Daten kompilieren…","📧 E-Mails…","🔍 SEO-Paket…","✅ Abschluss…"],
        "empty_title": "Ihr Paket erscheint hier",
        "empty_sub": "Fotos hochladen · Details ausfüllen · Erstellen",
        "photo": "Foto", "error": "Fehler: ",
        "tools_title": "KI-Tools für Makler", "tools_sub": "Ein Klick. Sofort professionell.",
        "tool_run": "Erstellen →", "tool_clear": "✕  Löschen", "tool_dl": "⬇  Herunterladen",
        "hist_title": "Gespeicherte Objekte", "hist_empty": "Noch keine Objekte.",
        "hist_load": "Laden", "hist_del": "Löschen", "hist_dl": "Herunterladen",
    },
    "Français": {
        "title": "SarSa AI", "tagline": "Plateforme d'Intelligence Immobilière",
        "subtitle": "Transformez des photos en pack marketing complet en quelques secondes.",
        "nav_gen": "🏠  Générer", "nav_tools": "⚡  Outils Agent", "nav_hist": "📁  Historique",
        "prop_section": "Détails du Bien", "agent_section": "Profil Agent",
        "target_lang": "Langue de Sortie", "prop_type": "Type de Bien", "price": "Prix",
        "location": "Localisation", "beds": "Chambres", "baths": "SDB", "sqm": "m²",
        "year": "Année", "parking": "Parking", "amenities": "Équipements",
        "tone": "Stratégie", "notes": "Notes Spéciales",
        "tones": ["⭐ Standard Pro","💎 Ultra-Luxe","📈 Investissement","🏡 Familial","🎨 Minimaliste","🏖️ Location Vacances","🏗️ Neuf","🏢 Commercial"],
        "agent_name": "Votre Nom", "agent_co": "Agence / Société", "agent_phone": "Téléphone", "agent_email": "Email",
        "ph_lang": "ex. Français, Anglais…", "ph_prop": "ex. Villa de Luxe, Apt T3…",
        "ph_price": "ex. 850 000€ ou 2 400€/mois", "ph_loc": "ex. Paris 16ème",
        "ph_beds": "3", "ph_baths": "2", "ph_sqm": "150", "ph_year": "2020",
        "ph_park": "1 garage", "ph_amen": "Piscine, sport, vue mer…",
        "ph_notes": "Cuisine rénovée, proche métro…",
        "ph_an": "Marie Dupont", "ph_ac": "Luxe Realty France",
        "ph_ap": "+33 6 00 00 00 00", "ph_ae": "marie@luxerealty.fr",
        "upload_label": "📸  Déposez les photos ici — JPG, PNG, WEBP",
        "btn": "✦  GÉNÉRER LE PACK MARKETING COMPLET",
        "regen": "↺  Régénérer", "save_hist": "💾  Sauvegarder", "saved_ok": "✅ Sauvegardé!",
        "dl_all": "⬇  Tout télécharger", "dl": "⬇  Télécharger", "copy": "⎘  Copier", "copied": "✅ Copié!",
        "result_title": "Votre Pack Marketing",
        "tab1": "📝 Annonce", "tab2": "📱 Réseaux Sociaux", "tab3": "🎬 Script Vidéo",
        "tab4": "⚙️ Specs", "tab5": "📧 Emails", "tab6": "🔍 SEO",
        "lbl1": "Texte Annonce", "lbl2": "Kit Réseaux Sociaux", "lbl3": "Script Vidéo",
        "lbl4": "Fiche Technique", "lbl5": "Templates Email", "lbl6": "Pack SEO & Digital",
        "words": "mots", "chars": "caractères",
        "fh_ok": "✅ Logement équitable — OK", "fh_warn": "⚠️ Vérifier: ",
        "unsaved": "● Non enregistré", "all_saved": "✔ Tout enregistré",
        "loading": ["🔍 Analyse photos…","✍️ Rédaction annonce…","📱 Kit réseaux…",
                    "🎬 Script vidéo…","⚙️ Specs…","📧 Emails…","🔍 SEO…","✅ Finalisation…"],
        "empty_title": "Votre pack apparaîtra ici",
        "empty_sub": "Chargez des photos · Remplissez · Générez",
        "photo": "Photo", "error": "Erreur: ",
        "tools_title": "Outils IA pour Agents", "tools_sub": "Un clic. Résultat professionnel.",
        "tool_run": "Générer →", "tool_clear": "✕  Effacer", "tool_dl": "⬇  Télécharger",
        "hist_title": "Biens Sauvegardés", "hist_empty": "Aucun bien sauvegardé.",
        "hist_load": "Charger", "hist_del": "Supprimer", "hist_dl": "Télécharger",
    },
    "Português": {
        "title": "SarSa AI", "tagline": "Plataforma de Inteligência Imobiliária",
        "subtitle": "Transforme fotos num pacote completo de marketing profissional em segundos.",
        "nav_gen": "🏠  Gerar", "nav_tools": "⚡  Ferramentas", "nav_hist": "📁  Histórico",
        "prop_section": "Detalhes do Imóvel", "agent_section": "Perfil do Agente",
        "target_lang": "Idioma de Saída", "prop_type": "Tipo de Imóvel", "price": "Preço",
        "location": "Localização", "beds": "Quartos", "baths": "WC", "sqm": "m²",
        "year": "Ano", "parking": "Garagem", "amenities": "Características",
        "tone": "Estratégia", "notes": "Notas Especiais",
        "tones": ["⭐ Profissional","💎 Ultra-Luxo","📈 Investimento","🏡 Familiar","🎨 Minimalista","🏖️ Férias","🏗️ Nova Construção","🏢 Comercial"],
        "agent_name": "O Seu Nome", "agent_co": "Agência / Empresa", "agent_phone": "Telefone", "agent_email": "Email",
        "ph_lang": "ex. Português, Inglês…", "ph_prop": "ex. Villa de Luxo, Apt T3…",
        "ph_price": "ex. 850.000€ ou 2.400€/mês", "ph_loc": "ex. Lisboa, Chiado",
        "ph_beds": "3", "ph_baths": "2", "ph_sqm": "150", "ph_year": "2020",
        "ph_park": "1 garagem", "ph_amen": "Piscina, ginásio, vista mar…",
        "ph_notes": "Cozinha renovada, metro próximo…",
        "ph_an": "Ana Silva", "ph_ac": "Luxe Realty Portugal",
        "ph_ap": "+351 91 000 0000", "ph_ae": "ana@luxerealty.pt",
        "upload_label": "📸  Arraste fotos aqui — JPG, PNG, WEBP",
        "btn": "✦  GERAR PACOTE COMPLETO DE MARKETING",
        "regen": "↺  Regenerar", "save_hist": "💾  Guardar", "saved_ok": "✅ Guardado!",
        "dl_all": "⬇  Descarregar Tudo", "dl": "⬇  Descarregar", "copy": "⎘  Copiar", "copied": "✅ Copiado!",
        "result_title": "O Seu Pacote de Marketing",
        "tab1": "📝 Anúncio", "tab2": "📱 Redes Sociais", "tab3": "🎬 Guião",
        "tab4": "⚙️ Especificações", "tab5": "📧 Emails", "tab6": "🔍 SEO",
        "lbl1": "Texto Anúncio", "lbl2": "Kit Redes Sociais", "lbl3": "Guião de Vídeo",
        "lbl4": "Especificações", "lbl5": "Templates Email", "lbl6": "Pack SEO & Digital",
        "words": "palavras", "chars": "caracteres",
        "fh_ok": "✅ Habitação justa — OK", "fh_warn": "⚠️ Rever: ",
        "unsaved": "● Não guardado", "all_saved": "✔ Tudo guardado",
        "loading": ["🔍 A analisar fotos…","✍️ A redigir anúncio…","📱 Kit redes…",
                    "🎬 Guião vídeo…","⚙️ Specs…","📧 Emails…","🔍 SEO…","✅ A finalizar…"],
        "empty_title": "O seu pacote aparecerá aqui",
        "empty_sub": "Carregue fotos · Preencha · Gere",
        "photo": "Foto", "error": "Erro: ",
        "tools_title": "Ferramentas IA para Agentes", "tools_sub": "Um clique. Resultado profissional.",
        "tool_run": "Gerar →", "tool_clear": "✕  Limpar", "tool_dl": "⬇  Descarregar",
        "hist_title": "Imóveis Guardados", "hist_empty": "Ainda sem imóveis guardados.",
        "hist_load": "Carregar", "hist_del": "Apagar", "hist_dl": "Descarregar",
    },
    "日本語": {
        "title": "SarSa AI", "tagline": "不動産インテリジェンスプラットフォーム",
        "subtitle": "物件写真を秒単位でプロのマーケティングパッケージに変換します。",
        "nav_gen": "🏠  生成", "nav_tools": "⚡  エージェントツール", "nav_hist": "📁  履歴",
        "prop_section": "物件詳細", "agent_section": "エージェントプロフィール",
        "target_lang": "出力言語", "prop_type": "物件種別", "price": "価格",
        "location": "所在地", "beds": "寝室", "baths": "浴室", "sqm": "㎡",
        "year": "築年", "parking": "駐車場", "amenities": "特徴",
        "tone": "戦略", "notes": "特記事項",
        "tones": ["⭐ スタンダード","💎 高級","📈 投資","🏡 ファミリー","🎨 モダンミニマル","🏖️ バケーション","🏗️ 新築","🏢 商業"],
        "agent_name": "お名前", "agent_co": "会社名", "agent_phone": "電話", "agent_email": "メール",
        "ph_lang": "例: 日本語、英語…", "ph_prop": "例: 3LDK、高級別荘…",
        "ph_price": "例: 5,000万円、月20万円", "ph_loc": "例: 東京都港区",
        "ph_beds": "3", "ph_baths": "2", "ph_sqm": "150", "ph_year": "2020",
        "ph_park": "1台", "ph_amen": "プール、ジム、海景…",
        "ph_notes": "リノベ済み、駅近…",
        "ph_an": "田中 太郎", "ph_ac": "ラックスリアルティ",
        "ph_ap": "+81 3 0000 0000", "ph_ae": "tanaka@luxerealty.jp",
        "upload_label": "📸  物件写真をここにドロップ — JPG、PNG、WEBP",
        "btn": "✦  完全なマーケティングパッケージを生成",
        "regen": "↺  再生成", "save_hist": "💾  履歴に保存", "saved_ok": "✅ 保存しました！",
        "dl_all": "⬇  全てダウンロード", "dl": "⬇  ダウンロード", "copy": "⎘  コピー", "copied": "✅ コピー完了！",
        "result_title": "マーケティングパッケージ",
        "tab1": "📝 広告", "tab2": "📱 SNSキット", "tab3": "🎬 動画台本",
        "tab4": "⚙️ 技術仕様", "tab5": "📧 メール", "tab6": "🔍 SEO",
        "lbl1": "物件広告", "lbl2": "SNSキット", "lbl3": "動画台本",
        "lbl4": "技術仕様書", "lbl5": "メールテンプレート", "lbl6": "SEOパック",
        "words": "語", "chars": "文字",
        "fh_ok": "✅ 公正住宅 — 問題なし", "fh_warn": "⚠️ 要確認: ",
        "unsaved": "● 未保存の変更", "all_saved": "✔ 全て保存済み",
        "loading": ["🔍 写真を分析中…","✍️ 広告を作成中…","📱 SNSキット…",
                    "🎬 動画台本…","⚙️ 仕様…","📧 メール…","🔍 SEO…","✅ 仕上げ中…"],
        "empty_title": "パッケージはここに表示されます",
        "empty_sub": "写真をアップロード · 詳細を入力 · 生成",
        "photo": "写真", "error": "エラー: ",
        "tools_title": "AIエージェントツール", "tools_sub": "ワンクリックでプロ品質を。",
        "tool_run": "生成 →", "tool_clear": "✕  クリア", "tool_dl": "⬇  ダウンロード",
        "hist_title": "保存済み物件", "hist_empty": "まだ保存された物件がありません。",
        "hist_load": "読込", "hist_del": "削除", "hist_dl": "ダウンロード",
    },
    "中文 (简体)": {
        "title": "SarSa AI", "tagline": "房地产智能平台",
        "subtitle": "将房产照片在几秒钟内转化为完整的专业营销套餐。",
        "nav_gen": "🏠  生成", "nav_tools": "⚡  经纪人工具", "nav_hist": "📁  历史",
        "prop_section": "房产详情", "agent_section": "经纪人资料",
        "target_lang": "输出语言", "prop_type": "房产类型", "price": "价格",
        "location": "地点", "beds": "卧室", "baths": "浴室", "sqm": "㎡",
        "year": "建造年份", "parking": "车位", "amenities": "特征",
        "tone": "策略", "notes": "备注",
        "tones": ["⭐ 标准专业","💎 顶奢","📈 投资","🏡 家庭","🎨 简约","🏖️ 度假","🏗️ 新开发","🏢 商业"],
        "agent_name": "姓名", "agent_co": "公司", "agent_phone": "电话", "agent_email": "邮箱",
        "ph_lang": "如 中文、英文…", "ph_prop": "如 豪华别墅、3室2厅…",
        "ph_price": "如 $850,000 或 $2,400/月", "ph_loc": "如 上海市浦东新区",
        "ph_beds": "3", "ph_baths": "2", "ph_sqm": "150", "ph_year": "2020",
        "ph_park": "1个车位", "ph_amen": "泳池、健身房、海景…",
        "ph_notes": "翻新厨房，靠近地铁…",
        "ph_an": "张伟", "ph_ac": "豪华地产集团",
        "ph_ap": "+86 138 0000 0000", "ph_ae": "zhang@luxerealty.cn",
        "upload_label": "📸  将房产照片拖放到此处 — JPG、PNG、WEBP",
        "btn": "✦  生成完整营销套餐",
        "regen": "↺  重新生成", "save_hist": "💾  保存到历史", "saved_ok": "✅ 已保存！",
        "dl_all": "⬇  下载全部", "dl": "⬇  下载", "copy": "⎘  复制", "copied": "✅ 已复制！",
        "result_title": "您的营销套餐",
        "tab1": "📝 房源", "tab2": "📱 社交媒体", "tab3": "🎬 视频脚本",
        "tab4": "⚙️ 技术规格", "tab5": "📧 邮件", "tab6": "🔍 SEO",
        "lbl1": "房源描述", "lbl2": "社交媒体套件", "lbl3": "视频脚本",
        "lbl4": "技术规格", "lbl5": "邮件模板", "lbl6": "SEO数字营销包",
        "words": "词", "chars": "字符",
        "fh_ok": "✅ 公平住房 — 无问题", "fh_warn": "⚠️ 请检查: ",
        "unsaved": "● 未保存的更改", "all_saved": "✔ 全部已保存",
        "loading": ["🔍 正在分析照片…","✍️ 正在撰写描述…","📱 社交套件…",
                    "🎬 视频脚本…","⚙️ 技术规格…","📧 邮件…","🔍 SEO套件…","✅ 正在完成…"],
        "empty_title": "您的营销套餐将显示在这里",
        "empty_sub": "上传照片 · 填写详情 · 点击生成",
        "photo": "照片", "error": "错误: ",
        "tools_title": "AI经纪人工具箱", "tools_sub": "一键即得专业成果。",
        "tool_run": "生成 →", "tool_clear": "✕  清除", "tool_dl": "⬇  下载",
        "hist_title": "已保存房源", "hist_empty": "还没有保存的房源。",
        "hist_load": "加载", "hist_del": "删除", "hist_dl": "下载",
    },
    "العربية": {
        "title": "SarSa AI", "tagline": "منصة الذكاء العقاري",
        "subtitle": "حوّل صور العقارات إلى حزمة تسويقية احترافية متكاملة في ثوانٍ.",
        "nav_gen": "🏠  إنشاء", "nav_tools": "⚡  أدوات الوكيل", "nav_hist": "📁  السجل",
        "prop_section": "تفاصيل العقار", "agent_section": "ملف الوكيل",
        "target_lang": "لغة المحتوى", "prop_type": "نوع العقار", "price": "السعر",
        "location": "الموقع", "beds": "غرف النوم", "baths": "الحمامات", "sqm": "م²",
        "year": "سنة البناء", "parking": "موقف", "amenities": "المميزات",
        "tone": "الاستراتيجية", "notes": "ملاحظات خاصة",
        "tones": ["⭐ احترافي","💎 فخامة فائقة","📈 استثماري","🏡 عائلي","🎨 عصري بسيط","🏖️ عطلات","🏗️ مشروع جديد","🏢 تجاري"],
        "agent_name": "اسمك", "agent_co": "الوكالة / الشركة", "agent_phone": "الهاتف", "agent_email": "البريد",
        "ph_lang": "مثال: العربية، الإنجليزية…", "ph_prop": "مثال: فيلا فاخرة، شقة 3 غرف…",
        "ph_price": "مثال: $850,000 أو $2,400/شهر", "ph_loc": "مثال: دبي، وسط المدينة",
        "ph_beds": "3", "ph_baths": "2", "ph_sqm": "150", "ph_year": "2020",
        "ph_park": "موقف مغطى", "ph_amen": "مسبح، صالة، إطلالة بحرية…",
        "ph_notes": "مطبخ مجدد، قرب المترو…",
        "ph_an": "محمد الأحمد", "ph_ac": "مجموعة لوكس العقارية",
        "ph_ap": "+971 50 000 0000", "ph_ae": "m@luxerealty.ae",
        "upload_label": "📸  اسحب صور العقار وأفلتها هنا — JPG، PNG، WEBP",
        "btn": "✦  إنشاء حزمة تسويقية متكاملة",
        "regen": "↺  إعادة الإنشاء", "save_hist": "💾  حفظ في السجل", "saved_ok": "✅ تم الحفظ!",
        "dl_all": "⬇  تحميل الكل", "dl": "⬇  تحميل", "copy": "⎘  نسخ", "copied": "✅ تم النسخ!",
        "result_title": "حزمتك التسويقية",
        "tab1": "📝 الإعلان", "tab2": "📱 التواصل الاجتماعي", "tab3": "🎬 سيناريو الفيديو",
        "tab4": "⚙️ المواصفات", "tab5": "📧 البريد الإلكتروني", "tab6": "🔍 حزمة SEO",
        "lbl1": "نص الإعلان", "lbl2": "مجموعة التواصل", "lbl3": "سيناريو الفيديو",
        "lbl4": "المواصفات التقنية", "lbl5": "قوالب البريد", "lbl6": "حزمة SEO الرقمية",
        "words": "كلمة", "chars": "حرف",
        "fh_ok": "✅ الإسكان العادل — لا مشاكل", "fh_warn": "⚠️ راجع: ",
        "unsaved": "● تغييرات غير محفوظة", "all_saved": "✔ تم الحفظ",
        "loading": ["🔍 تحليل الصور…","✍️ كتابة الإعلان…","📱 التواصل الاجتماعي…",
                    "🎬 سيناريو الفيديو…","⚙️ المواصفات…","📧 البريد…","🔍 حزمة SEO…","✅ الانتهاء…"],
        "empty_title": "ستظهر حزمتك التسويقية هنا",
        "empty_sub": "ارفع الصور · أدخل التفاصيل · اضغط إنشاء",
        "photo": "صورة", "error": "خطأ: ",
        "tools_title": "أدوات الوكيل بالذكاء الاصطناعي", "tools_sub": "نقرة واحدة. نتيجة احترافية فورية.",
        "tool_run": "إنشاء ←", "tool_clear": "✕  مسح", "tool_dl": "⬇  تحميل",
        "hist_title": "العقارات المحفوظة", "hist_empty": "لا توجد عقارات محفوظة بعد.",
        "hist_load": "تحميل", "hist_del": "حذف", "hist_dl": "تحميل",
    },
}

# --- SESSION STATE ---
_defaults = {
    "page": "generate",
    "s1": "", "s2": "", "s3": "", "s4": "", "s5": "", "s6": "",
    "output_ready": False,
    "dirty": False,
    "history": [],
    "tool_out": "",
    "tool_title": "",
    "write_in": "English",
    "prop_type": "", "price": "", "location": "",
    "beds": "", "baths": "", "sqm": "", "year_built": "",
    "parking": "", "amenities": "", "custom_inst": "",
    "strategy_idx": 0,
    "agent_name": "", "agent_co": "", "agent_phone": "", "agent_email": "",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

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
    agent_parts = [x for x in [ss.agent_name, ss.agent_company if "agent_company" in ss else ss.get("agent_co",""), ss.agent_phone, ss.agent_email] if x]
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

Generate a COMPLETE 6-section package. Use EXACTLY these markers — never skip any:

## SECTION_1 — PRIME LISTING COPY
450–650 words. Structure: ALL-CAPS headline → emotional opening (3–4 sentences) → living spaces (reference photos) → kitchen/bathrooms → outdoor/amenities → location highlights → value proposition → CTA with agent contact.

## SECTION_2 — SOCIAL MEDIA KIT
📸 INSTAGRAM: Full caption (2200 chars) + 25 hashtags (10 property, 8 location, 7 lifestyle)
👥 FACEBOOK: 200–280 words, community-focused, price shown
💼 LINKEDIN: 150–200 words, investment angle, professional
🐦 X/TWITTER: Max 270 chars + 4 hashtags
📱 WHATSAPP: Max 155 chars, price + feature + contact

## SECTION_3 — CINEMATIC VIDEO SCRIPT
Title card → 7 scenes each with [CAMERA:] [VOICEOVER:] [DURATION:] → Music direction → Closing card with agent details → YouTube description (150 words) + 10 tags

## SECTION_4 — TECHNICAL SPECIFICATIONS
Key specs table → Room-by-room breakdown from photos → Amenities checklist (✓/—) → Building notes → Legal placeholder → Contact info

## SECTION_5 — EMAIL TEMPLATES
📧 EMAIL 1 — JUST LISTED: Subject + 150–200 word body + signature
📧 EMAIL 2 — POST-VIEWING FOLLOW-UP: Subject + 120–150 words + signature
📧 EMAIL 3 — PRICE REDUCTION ALERT: Subject + 110–130 words + signature

## SECTION_6 — SEO & DIGITAL MARKETING
20 ranked SEO keywords → 3 meta descriptions (155 chars each) → Google Ads (3 headlines 30 chars, 2 descriptions 90 chars) → Instagram hashtags by category → 10 YouTube tags → 5 Pinterest board names → Posting calendar (best day + time per platform)

Write every word in {lang}. Reference real photo details. Zero filler."""

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

def full_export_text():
    ss = st.session_state
    return (f"SARSA AI — COMPLETE MARKETING PACKAGE\n{'='*60}\n"
            f"Property: {ss.prop_type} | {ss.location} | {ss.price}\n"
            f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}\n{'='*60}\n\n"
            + "\n\n".join(
                f"{'─'*60}\nSECTION {i}\n{'─'*60}\n{ss.get(f's{i}','')}"
                for i in range(1, 7)
            ))

# --- CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Syne:wght@700;800&display=swap');

/* BASE */
html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
.stApp { background: #0C0C0F !important; }

/* HIDE CHROME */
#MainMenu, footer, header, .stDeployButton,
div[data-testid="stInputInstructions"],
span[data-testid="stIconMaterial"],
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none !important; visibility: hidden !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #111118 !important;
    border-right: 1px solid #1C1C26 !important;
    width: 278px !important; min-width: 278px !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding: 1.1rem 0.95rem 2rem !important;
}
section[data-testid="stSidebar"] label {
    color: #52526A !important; font-size: 0.68rem !important;
    font-weight: 700 !important; letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    background: #16161E !important; border: 1px solid #22222E !important;
    border-radius: 7px !important; color: #E2E2EE !important;
    font-size: 0.84rem !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
}
section[data-testid="stSidebar"] input:focus,
section[data-testid="stSidebar"] textarea:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.14) !important; outline: none !important;
}
section[data-testid="stSidebar"] input::placeholder,
section[data-testid="stSidebar"] textarea::placeholder { color: #33334A !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #16161E !important; border: 1px solid #22222E !important;
    border-radius: 7px !important; color: #E2E2EE !important; font-size: 0.84rem !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #52526A !important; }

/* DROPDOWN MENUS */
[data-baseweb="popover"], [data-baseweb="menu"] {
    background: #1A1A24 !important; border: 1px solid #22222E !important;
    border-radius: 9px !important; box-shadow: 0 8px 32px rgba(0,0,0,0.55) !important;
}
[role="option"] {
    color: #E2E2EE !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.84rem !important; padding: 8px 14px !important; background: transparent !important;
}
[role="option"]:hover { background: #22222E !important; }
[role="option"][aria-selected="true"] { background: #C9A84C !important; color: #0C0C0F !important; }

/* NAV BUTTONS — active state */
div.sarsa-nav-active > div > button,
div.sarsa-nav-active > div[data-testid="stButton"] > button {
    background: #C9A84C !important; color: #0C0C0F !important;
    border: none !important; font-weight: 700 !important;
}
/* NAV BUTTONS — inactive */
div.sarsa-nav-inactive > div > button,
div.sarsa-nav-inactive > div[data-testid="stButton"] > button {
    background: transparent !important; color: #7070888 !important;
    border: none !important; font-weight: 500 !important; color: #707088 !important;
}
div.sarsa-nav-inactive > div > button:hover,
div.sarsa-nav-inactive > div[data-testid="stButton"] > button:hover {
    background: #1C1C26 !important; color: #E2E2EE !important;
}
/* All sidebar buttons shape */
section[data-testid="stSidebar"] .stButton > button {
    border-radius: 8px !important; padding: 8px 12px !important;
    font-size: 0.85rem !important; width: 100% !important;
    text-align: left !important; transition: all 0.15s !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* MAIN AREA */
.block-container {
    background: transparent !important;
    padding: 1.75rem 2.25rem 5rem !important;
    max-width: 1300px !important;
}

/* UPLOAD ZONE */
[data-testid="stFileUploader"] {
    background: #13131A !important; border: 2px dashed #22222E !important;
    border-radius: 14px !important; transition: all 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #C9A84C !important; background: #15151D !important;
}
[data-testid="stFileUploader"] label {
    color: #52526A !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    text-transform: none !important; letter-spacing: 0 !important; font-size: 0.9rem !important;
}
[data-testid="stFileUploader"] section { padding: 1.5rem !important; }
[data-testid="stFileUploaderDropzone"] { border: none !important; background: transparent !important; }

/* GENERATE BUTTON */
div.sarsa-gen-btn > div > button,
div.sarsa-gen-btn > div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #C9A84C 0%, #E8C870 100%) !important;
    color: #0C0C0F !important; border: none !important;
    border-radius: 10px !important; padding: 0.88rem 2rem !important;
    font-family: 'Syne', sans-serif !important; font-size: 0.88rem !important;
    font-weight: 800 !important; letter-spacing: 0.06em !important;
    width: 100% !important; cursor: pointer !important;
    box-shadow: 0 4px 22px rgba(201,168,76,0.28) !important;
    transition: all 0.2s !important;
}
div.sarsa-gen-btn > div > button:hover,
div.sarsa-gen-btn > div[data-testid="stButton"] > button:hover {
    box-shadow: 0 6px 32px rgba(201,168,76,0.48) !important;
    transform: translateY(-1px) !important;
}

/* ALL OTHER BUTTONS */
.stButton > button {
    background: #16161E !important; color: #C0C0D4 !important;
    border: 1px solid #22222E !important; border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.82rem !important; font-weight: 600 !important;
    padding: 0.46rem 1rem !important; cursor: pointer !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #1C1C26 !important; border-color: #C9A84C !important; color: #F0F0FA !important;
}
.stButton > button:active { transform: scale(0.98) !important; }

/* DOWNLOAD BUTTONS */
.stDownloadButton > button {
    background: #16161E !important; color: #C0C0D4 !important;
    border: 1px solid #22222E !important; border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.82rem !important; font-weight: 600 !important;
    padding: 0.46rem 1rem !important; cursor: pointer !important;
    transition: all 0.15s !important;
}
.stDownloadButton > button:hover {
    background: #1C1C26 !important; border-color: #C9A84C !important; color: #F0F0FA !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: #13131A !important; border-radius: 10px !important;
    padding: 4px !important; border: 1px solid #1C1C26 !important;
    gap: 2px !important; flex-wrap: wrap !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 7px !important;
    color: #52526A !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.8rem !important;
    padding: 7px 13px !important; border: none !important;
    white-space: nowrap !important; transition: all 0.15s !important;
}
.stTabs [data-baseweb="tab"]:hover { background: #1A1A24 !important; color: #E2E2EE !important; }
.stTabs [aria-selected="true"] {
    background: #C9A84C !important; color: #0C0C0F !important; font-weight: 700 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.1rem !important; }

/* TEXT AREAS */
.stTextArea textarea {
    background: #13131A !important; border: 1px solid #1C1C26 !important;
    border-radius: 10px !important; color: #E2E2EE !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.89rem !important; line-height: 1.72 !important;
    padding: 1rem !important; resize: vertical !important;
    caret-color: #C9A84C !important; transition: border-color 0.15s !important;
}
.stTextArea textarea:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.1) !important; outline: none !important;
}
.stTextArea label { display: none !important; }

/* PROGRESS */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #C9A84C, #E8C870) !important;
}
.stProgress > div > div { background: #16161E !important; height: 5px !important; border-radius: 99px !important; }

/* ALERTS */
.stAlert {
    background: #13131A !important; border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.86rem !important; color: #C0C0D4 !important;
}

/* SCROLLBAR */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0C0C0F; }
::-webkit-scrollbar-thumb { background: #22222E; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #C9A84C; }

/* EXPANDER */
[data-testid="stExpander"] {
    background: #13131A !important; border: 1px solid #1C1C26 !important; border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    color: #C0C0D4 !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.88rem !important;
}
[data-testid="stExpander"] summary:hover { color: #F0F0FA !important; }

/* CUSTOM COMPONENTS */
.sarsa-page-header { margin-bottom: 1.75rem; padding-bottom: 1.2rem; border-bottom: 1px solid #1C1C26; }
.sarsa-page-title { font-family: 'Syne', sans-serif; font-size: clamp(1.5rem,2.8vw,2.1rem); font-weight: 800; color: #F0F0FA; line-height: 1.1; margin-bottom: 0.25rem; }
.sarsa-page-title .gold { color: #C9A84C; }
.sarsa-page-sub { font-size: 0.87rem; color: #52526A; line-height: 1.5; }
.sarsa-logo-name { font-family: 'Syne', sans-serif; font-size: 1.28rem; font-weight: 800; color: #F0F0FA; }
.sarsa-logo-name span { color: #C9A84C; }
.sarsa-logo-sub { font-size: 0.59rem; color: #33334A; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 1px; }
.sarsa-section-head { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #33334A; margin: 1rem 0 0.45rem; font-family: 'Plus Jakarta Sans', sans-serif; }
.sarsa-divider { height: 1px; background: linear-gradient(90deg, rgba(201,168,76,0.35), transparent); margin: 1.2rem 0; }
.sarsa-output-title { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; color: #F0F0FA; margin-bottom: 2px; }
.sarsa-status-unsaved { font-size: 0.76rem; font-weight: 600; color: #F59E0B; font-family: 'Plus Jakarta Sans', sans-serif; }
.sarsa-status-saved { font-size: 0.76rem; font-weight: 600; color: #4ADE80; font-family: 'Plus Jakarta Sans', sans-serif; }
.sarsa-wc-row { display: flex; gap: 7px; align-items: center; margin: 7px 0 10px; flex-wrap: wrap; }
.sarsa-wc-chip { background: #16161E; color: #52526A; font-size: 0.71rem; font-weight: 600; padding: 3px 10px; border-radius: 20px; border: 1px solid #1C1C26; font-family: 'Plus Jakarta Sans', sans-serif; }
.sarsa-fh-ok { display:inline-flex;align-items:center;gap:5px;background:rgba(74,222,128,0.07);color:#4ADE80;border:1px solid rgba(74,222,128,0.2);border-radius:20px;padding:3px 12px;font-size:0.74rem;font-weight:600;font-family:'Plus Jakarta Sans',sans-serif;margin:5px 0 10px; }
.sarsa-fh-warn { display:inline-flex;align-items:center;gap:5px;background:rgba(245,158,11,0.07);color:#FBB824;border:1px solid rgba(245,158,11,0.2);border-radius:20px;padding:3px 12px;font-size:0.74rem;font-weight:600;font-family:'Plus Jakarta Sans',sans-serif;margin:5px 0 10px; }
.sarsa-copy-btn { display:block;width:100%;background:#16161E;color:#C0C0D4;border:1px solid #22222E;border-radius:8px;padding:7px 16px;font-size:0.82rem;font-weight:600;font-family:'Plus Jakarta Sans',sans-serif;cursor:pointer;transition:all 0.15s;text-align:center; }
.sarsa-copy-btn:hover { background:#1C1C26;border-color:#C9A84C;color:#F0F0FA; }
.sarsa-empty { background:#13131A;border:2px dashed #1C1C26;border-radius:16px;padding:5rem 2rem;text-align:center;margin-top:0.5rem; }
.sarsa-empty-icon { font-size:2.8rem;margin-bottom:0.9rem; }
.sarsa-empty-title { font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:700;color:#F0F0FA;margin-bottom:0.35rem; }
.sarsa-empty-sub { font-size:0.87rem;color:#52526A; }
.sarsa-tool-card { background:#13131A;border:1px solid #1C1C26;border-radius:12px;padding:1.05rem 1.15rem;margin-bottom:0.6rem;transition:border-color 0.15s; }
.sarsa-tool-card:hover { border-color:#C9A84C; }
.sarsa-tool-name { font-family:'Syne',sans-serif;font-weight:700;font-size:0.91rem;color:#F0F0FA;margin-bottom:3px; }
.sarsa-tool-desc { font-size:0.79rem;color:#52526A;line-height:1.45; }
.sarsa-tool-out-header { background:#13131A;border:1px solid #1C1C26;border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.9rem; }
.sarsa-hist-card { background:#13131A;border:1px solid #1C1C26;border-radius:11px;padding:0.95rem 1.1rem;margin-bottom:0.6rem; }
.photo-caption { text-align:center;color:#33334A;font-size:0.68rem;margin-top:2px;font-family:'Plus Jakarta Sans',sans-serif; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    logo_img = load_logo("SarSa_Logo_Transparent.png")
    if logo_img:
        st.image(logo_img, use_container_width=True)
    else:
        st.markdown("""
        <div style='padding:0.2rem 0 1rem'>
            <div class='sarsa-logo-name'>Sar<span>Sa</span> AI</div>
            <div class='sarsa-logo-sub'>Real Estate Intelligence</div>
        </div>""", unsafe_allow_html=True)

    # Language
    ui_lang = st.selectbox("🌐 Interface Language", list(ui_languages.keys()), index=0, key="ui_lang_sel")
    t = ui_languages[ui_lang]

    st.markdown("<div class='sarsa-divider'></div>", unsafe_allow_html=True)

    # Navigation
    st.markdown("<div class='sarsa-section-head'>Navigation</div>", unsafe_allow_html=True)
    for pid, plabel in [("generate", t["nav_gen"]), ("tools", t["nav_tools"]), ("history", t["nav_hist"])]:
        css = "sarsa-nav-active" if st.session_state.page == pid else "sarsa-nav-inactive"
        st.markdown(f"<div class='{css}'>", unsafe_allow_html=True)
        if st.button(plabel, key=f"nav_{pid}", use_container_width=True):
            st.session_state.page = pid
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sarsa-divider'></div>", unsafe_allow_html=True)

    # Property details
    st.markdown(f"<div class='sarsa-section-head'>{t['prop_section']}</div>", unsafe_allow_html=True)
    st.session_state.write_in   = st.text_input(t["target_lang"], value=st.session_state.write_in,  placeholder=t["ph_lang"], key="si_wi")
    st.session_state.prop_type  = st.text_input(t["prop_type"],   value=st.session_state.prop_type,  placeholder=t["ph_prop"], key="si_pt")
    st.session_state.price      = st.text_input(t["price"],       value=st.session_state.price,       placeholder=t["ph_price"], key="si_pr")
    st.session_state.location   = st.text_input(t["location"],    value=st.session_state.location,    placeholder=t["ph_loc"], key="si_lo")
    c1, c2 = st.columns(2)
    with c1: st.session_state.beds      = st.text_input(t["beds"],    value=st.session_state.beds,      placeholder=t["ph_beds"],  key="si_bd")
    with c2: st.session_state.baths     = st.text_input(t["baths"],   value=st.session_state.baths,     placeholder=t["ph_baths"], key="si_ba")
    c3, c4 = st.columns(2)
    with c3: st.session_state.sqm       = st.text_input(t["sqm"],     value=st.session_state.sqm,       placeholder=t["ph_sqm"],   key="si_sq")
    with c4: st.session_state.year_built= st.text_input(t["year"],    value=st.session_state.year_built, placeholder=t["ph_year"], key="si_yr")
    st.session_state.parking    = st.text_input(t["parking"],     value=st.session_state.parking,     placeholder=t["ph_park"],  key="si_pk")
    st.session_state.amenities  = st.text_input(t["amenities"],   value=st.session_state.amenities,   placeholder=t["ph_amen"],  key="si_am")

    strats = t["tones"]
    sidx = st.session_state.strategy_idx if st.session_state.strategy_idx < len(strats) else 0
    chosen = st.selectbox(t["tone"], strats, index=sidx, key="si_st")
    st.session_state.strategy_idx = strats.index(chosen)

    st.session_state.custom_inst = st.text_area(t["notes"], value=st.session_state.custom_inst, placeholder=t["ph_notes"], height=65, key="si_no")

    st.markdown("<div class='sarsa-divider'></div>", unsafe_allow_html=True)

    # Agent profile
    st.markdown(f"<div class='sarsa-section-head'>{t['agent_section']}</div>", unsafe_allow_html=True)
    st.session_state.agent_name  = st.text_input(t["agent_name"],  value=st.session_state.agent_name,  placeholder=t["ph_an"], key="si_an")
    st.session_state.agent_co    = st.text_input(t["agent_co"],    value=st.session_state.agent_co,    placeholder=t["ph_ac"], key="si_ac")
    st.session_state.agent_phone = st.text_input(t["agent_phone"], value=st.session_state.agent_phone, placeholder=t["ph_ap"], key="si_ap")
    st.session_state.agent_email = st.text_input(t["agent_email"], value=st.session_state.agent_email, placeholder=t["ph_ae"], key="si_ae")


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS — copy button & section renderer
# ═══════════════════════════════════════════════════════════════════════════════
def copy_btn(text, lbl_copy, lbl_copied, uid):
    safe = text.replace("\\","\\\\").replace("`","\\`").replace("$","\\$").replace("'","\\'")
    lc = lbl_copy.replace("'","\\'"); ld = lbl_copied.replace("'","\\'")
    st.markdown(f"""
    <button class='sarsa-copy-btn' id='cpb_{uid}'
      onclick="navigator.clipboard.writeText(`{safe}`).then(()=>{{
        var b=document.getElementById('cpb_{uid}');
        b.textContent='{ld}';
        setTimeout(()=>b.textContent='{lc}',2000);
      }})"
    >{lc}</button>""", unsafe_allow_html=True)

def render_section(sk, fname, show_fhc=False):
    val = st.session_state.get(sk, "")
    new = st.text_area("", value=val, height=490, key=f"ta_{sk}", label_visibility="collapsed")
    if new != val:
        st.session_state[sk] = new
        st.session_state.dirty = True
    w = len(new.split()) if new else 0
    c = len(new) if new else 0
    st.markdown(f"<div class='sarsa-wc-row'><span class='sarsa-wc-chip'>📊 {w} {t['words']}</span><span class='sarsa-wc-chip'>✏️ {c} {t['chars']}</span></div>", unsafe_allow_html=True)
    if show_fhc and new:
        flags = check_fair_housing(new)
        if flags:
            st.markdown(f"<div class='sarsa-fh-warn'>{t['fh_warn']}{', '.join(flags)}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='sarsa-fh-ok'>{t['fh_ok']}</div>", unsafe_allow_html=True)
    bc1, bc2 = st.columns(2)
    with bc1:
        st.download_button(t["dl"], data=new,
            file_name=f"sarsa_{fname}_{datetime.now().strftime('%Y%m%d')}.txt",
            key=f"dl_{sk}", use_container_width=True)
    with bc2:
        copy_btn(new, t["copy"], t["copied"], sk)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: GENERATE
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "generate":

    st.markdown(f"""
    <div class='sarsa-page-header'>
        <div class='sarsa-page-title'>{t['title']} <span class='gold'>{t['tagline']}</span></div>
        <div class='sarsa-page-sub'>{t['subtitle']}</div>
    </div>""", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        t["upload_label"], type=["jpg","jpeg","png","webp"],
        accept_multiple_files=True, label_visibility="visible")

    if uploaded_files:
        images_for_ai = [Image.open(f) for f in uploaded_files]
        n = min(len(images_for_ai), 6)
        cols = st.columns(n)
        for i, img in enumerate(images_for_ai):
            with cols[i % n]:
                st.image(img, use_container_width=True)
                st.markdown(f"<p class='photo-caption'>{t['photo']} {i+1}</p>", unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sarsa-gen-btn'>", unsafe_allow_html=True)
        do_gen = st.button(t["btn"], use_container_width=True, key="main_gen_btn")
        st.markdown("</div>", unsafe_allow_html=True)

        if do_gen:
            strategy = t["tones"][st.session_state.strategy_idx]
            prompt = build_prompt(st.session_state.write_in or "English", strategy)
            prog = st.progress(0)
            status = st.empty()
            steps = t["loading"]
            try:
                for i, step in enumerate(steps[:-1]):
                    status.info(step)
                    prog.progress(int((i+1)/len(steps)*88))
                status.info(steps[-1])
                resp = model.generate_content([prompt] + images_for_ai)
                raw = resp.text
                for n_s in range(1, 7):
                    st.session_state[f"s{n_s}"] = extract_section(raw, n_s)
                st.session_state.output_ready = True
                st.session_state.dirty = False
                prog.progress(100)
                status.success("✅  Package ready!")
            except Exception as e:
                status.error(f"{t['error']}{e}")
                prog.empty()
    else:
        if not st.session_state.output_ready:
            st.markdown(f"""
            <div class='sarsa-empty'>
                <div class='sarsa-empty-icon'>🏡</div>
                <div class='sarsa-empty-title'>{t['empty_title']}</div>
                <div class='sarsa-empty-sub'>{t['empty_sub']}</div>
            </div>""", unsafe_allow_html=True)

    # OUTPUT
    if st.session_state.output_ready:
        st.markdown("<div class='sarsa-divider'></div>", unsafe_allow_html=True)

        # Action bar
        ac1, ac2, ac3, ac4, ac5 = st.columns([3.2, 1.25, 1.0, 1.2, 1.2])
        with ac1:
            st.markdown(f"<div class='sarsa-output-title'>{t['result_title']}</div>", unsafe_allow_html=True)
            if st.session_state.dirty:
                st.markdown(f"<div class='sarsa-status-unsaved'>{t['unsaved']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='sarsa-status-saved'>{t['all_saved']}</div>", unsafe_allow_html=True)
        with ac2:
            if st.button(t["save_hist"], use_container_width=True, key="save_hist_btn"):
                save_to_history()
                st.session_state.dirty = False
                st.success(t["saved_ok"])
        with ac3:
            if st.button(t["regen"], use_container_width=True, key="regen_btn"):
                for k in ["s1","s2","s3","s4","s5","s6"]:
                    st.session_state[k] = ""
                st.session_state.output_ready = False
                st.session_state.dirty = False
                st.rerun()
        with ac4:
            st.download_button(t["dl_all"], data=full_export_text(),
                file_name=f"sarsa_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                key="dl_all_btn", use_container_width=True)
        with ac5:
            copy_btn("\n\n".join(st.session_state.get(f"s{i}","") for i in range(1,7)),
                     t["copy"], t["copied"], "all_secs")

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

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

    st.markdown(f"""
    <div class='sarsa-page-header'>
        <div class='sarsa-page-title'>{t['tools_title']}</div>
        <div class='sarsa-page-sub'>{t['tools_sub']}</div>
    </div>""", unsafe_allow_html=True)

    ss = st.session_state
    lang  = ss.write_in or "English"
    name  = ss.agent_name  or "the agent"
    co    = ss.agent_co    or "the agency"
    loc   = ss.location    or "the local market"
    prop  = ss.prop_type   or "residential property"
    price = ss.price       or "market price"
    beds  = ss.beds        or "N/A"
    baths = ss.baths       or "N/A"
    sqm   = ss.sqm         or "N/A"
    phone = ss.agent_phone or "phone not provided"
    email = ss.agent_email or "email not provided"
    today = datetime.now().strftime("%B %d, %Y")

    TOOLS = [
        ("objection","💬 Objection Handler",
         "Master responses to the 10 toughest client objections using FEEL-FELT-FOUND",
         f"You are the world's top real estate sales coach.\nWrite a COMPLETE OBJECTION HANDLING PLAYBOOK.\nAgent: {name} | Agency: {co} | Market: {loc}\nLanguage: {lang}\n\nHandle EXACTLY these 10 objections using FEEL-FELT-FOUND + confident closing line:\n1. 'Your commission is too high'\n2. 'I'll wait for the market to improve'\n3. 'I can sell it myself (FSBO)'\n4. 'Another agent offered a lower fee'\n5. 'The asking price is too high'\n6. 'I need more time to think'\n7. 'We're not in a rush to sell'\n8. 'The property needs too much work'\n9. 'I'm already talking to another agent'\n10. 'I want to try selling privately first'\n\nFormat each: **Bold objection** → FEEL (1 sentence) → FELT (1 sentence) → FOUND (2 sentences) → CLOSING LINE (confident, 1 sentence)."),

        ("cma","📊 CMA Report Template",
         "Professional comparative market analysis for seller presentations",
         f"Write a COMPARATIVE MARKET ANALYSIS REPORT.\nProperty: {prop} | Location: {loc} | Price: {price}\nPrepared by: {name} | {co}\nLanguage: {lang}\n\nSections: Executive Summary, Subject Property Profile, Market Conditions, 3 Comparable Sales templates (table format), Price Analysis, Recommended Listing Price, DOM Forecast (3 scenarios), Marketing Strategy Recommendation, Agent Opinion of Value, Disclaimer."),

        ("cold_email","📧 Cold Outreach Emails",
         "Three targeted prospecting emails: potential sellers, landlords, expired listings",
         f"Write 3 high-converting cold outreach emails.\nAgent: {name} | Agency: {co} | Phone: {phone} | Email: {email}\nTarget area: {loc}\nLanguage: {lang}\n\nEMAIL 1 — POTENTIAL SELLER: Subject + 150-word warm value-first body + signature\nEMAIL 2 — LANDLORD/INVESTOR: Subject + 150-word ROI-angle body + signature\nEMAIL 3 — EXPIRED LISTING: Subject + 130-word empathy + fresh-approach body + signature"),

        ("negotiation","🤝 Negotiation Scripts",
         "Word-for-word scripts for every negotiation scenario agents face",
         f"Write a REAL ESTATE NEGOTIATION SCRIPT PLAYBOOK.\nProperty: {prop} | Location: {loc} | Price: {price}\nAgent: {name} | {co}\nLanguage: {lang}\n\n6 scenarios — each with Opening Line, 3 Talking Points, Counter Proposal, What NOT to Say, Closing Line:\n1. Responding to a lowball offer\n2. Multiple offers — create urgency\n3. Buyer requests price reduction after inspection\n4. Buyer requests seller pays closing costs\n5. Request to extend closing date\n6. Deal falling apart — save it"),

        ("bio","👤 Agent Biography",
         "Three professional bios: 55 words (micro), 160 words (standard), 320 words (full)",
         f"Write 3 professional real estate agent biographies.\nAgent: {name} | Agency: {co} | Market: {loc}\nPhone: {phone} | Email: {email}\nLanguage: {lang}\n\nVERSION 1 — MICRO (55 words max): 1st person, for Instagram/business cards\nVERSION 2 — STANDARD (160 words): 3rd person, for website/portals/LinkedIn\nVERSION 3 — FULL (320 words): 3rd person, for press/media, include awards placeholder"),

        ("openhouse","🏠 Open House Event Guide",
         "Complete event guide: prep checklist, scripts, tour points, follow-ups",
         f"Write a COMPLETE OPEN HOUSE EVENT GUIDE.\nProperty: {prop} | Location: {loc} | Price: {price}\nBeds: {beds} | Baths: {baths} | Size: {sqm} m²\nAgent: {name} | Phone: {phone}\nLanguage: {lang}\n\nInclude: Pre-event checklist (12 tasks), Welcome scripts (45 sec + 2 min), Room-by-room tour (8 rooms), Top 6 selling points, 4 price objection responses, Sign-in opener, 5 qualifying questions, Offer conversation guide, Same-day SMS (155 chars), Same-day WhatsApp, Next-day email (subject + 130 words)"),

        ("followup","📞 Follow-Up Sequence",
         "14-day multi-channel follow-up with every message written out",
         f"Write a COMPLETE 14-DAY POST-VIEWING FOLLOW-UP SEQUENCE.\nProperty: {prop} | Location: {loc} | Price: {price}\nAgent: {name} | Phone: {phone} | Email: {email}\nLanguage: {lang}\n\nWrite every message in full:\nDay 0: SMS (155 chars) + WhatsApp (200 chars)\nDay 1: Email subject + 150-word warm recap + signature\nDay 3: Email subject + 130-word neighbourhood highlights + signature\nDay 5: SMS (120 chars)\nDay 7: Email subject + 120-word market update + signature\nDay 10: Phone call outline (2-min, 6 points)\nDay 14: Email subject + 100-word final opportunity + signature"),

        ("investment","💰 Investment Analysis Memo",
         "Full ROI, yield, and cash flow analysis for investor presentations",
         f"Write a REAL ESTATE INVESTMENT ANALYSIS MEMO.\nProperty: {prop} | Location: {loc} | Price: {price}\nSize: {sqm} m² | Beds: {beds}\nPrepared by: {name} | {co}\nLanguage: {lang}\n\nInclude: Investment Snapshot (3 bullets), Acquisition Costs, Rental Income (Airbnb vs long-term), Gross Yield, Operating Expenses, NOI, Cap Rate, Cash-on-Cash Return (25% deposit assumed), 5-Year Appreciation (3 scenarios), Break-Even Timeline, 3 Exit Strategies, 5 Risk Factors, Investment Verdict, Disclaimer."),

        ("checklist","✅ Transaction Checklists",
         "Complete buyer and seller transaction checklists (70+ tasks total)",
         f"Create COMPREHENSIVE REAL ESTATE TRANSACTION CHECKLISTS.\nAgent: {name} | Agency: {co}\nLanguage: {lang}\n\nSELLER CHECKLIST (36+ tasks, 6 phases): Pre-Listing Prep, Active Listing, Offer & Negotiation, Under Contract, Pre-Closing, Closing Day\nBUYER CHECKLIST (33+ tasks, 6 phases): Pre-Search Prep, Property Search, Making an Offer, Under Contract, Financing & Inspection, Closing & Moving In\nFormat: ☐ Task | Responsible | Notes"),

        ("neighborhood","🗺️ Neighbourhood Guide",
         "Comprehensive buyer's area guide that overcomes location hesitation",
         f"Write a NEIGHBOURHOOD GUIDE FOR BUYERS.\nArea: {loc} | Property: {prop} | Price: {price}\nPrepared by: {name} | {co}\nLanguage: {lang}\n\n10 sections: Area Character, Transport & Commuting, Schools & Education, Dining/Shopping/Entertainment, Parks & Outdoor, Healthcare & Services, Safety & Community, Property Market Overview, 5 Reasons Locals Love It, Future Growth + Agent Recommendation + Disclaimer."),

        ("press","📰 Press Releases",
         "Two AP-style press releases: property launch and market update",
         f"Write 2 AP-style press releases.\nAgency: {co} | Agent: {name} | Phone: {phone} | Email: {email}\nProperty: {prop} | Location: {loc} | Price: {price} | Date: {today}\nLanguage: {lang}\n\nPR 1 — PROPERTY LAUNCH: FOR IMMEDIATE RELEASE, headline, subheading, dateline, lead, 2 property paragraphs, market context, agent quote, boilerplate, ###, media contact\nPR 2 — MARKET UPDATE: Same structure, market commentary focus. Both 380–420 words, AP style."),

        ("mortgage","🏦 Buyer's Finance Guide",
         "Complete mortgage guide: types, costs, application steps, glossary",
         f"Write a BUYER'S FINANCE AND MORTGAGE GUIDE.\nMarket: {loc}\nPrepared by: {name} | {co}\nLanguage: {lang}\n\n12 sections: Why Finance Planning Matters, Borrowing Capacity, Deposit Requirements, Mortgage Types (comparison table), Complete Buying Costs (% estimates), Application Process (8 steps), Common Rejection Reasons (8), First-Time Buyer Advantages, Investor Mortgages, Remortgaging Strategy, Glossary (18 terms plain English), Next Steps & Disclaimer."),
    ]

    # Show existing tool output
    if ss.tool_out:
        st.markdown(f"<div class='sarsa-tool-out-header'><span style='font-family:Syne,sans-serif;font-weight:700;color:#C9A84C;font-size:0.91rem;'>📄 {ss.tool_title}</span></div>", unsafe_allow_html=True)
        edited = st.text_area("", value=ss.tool_out, height=520, key="tool_ta", label_visibility="collapsed")
        w = len(edited.split()) if edited else 0
        c = len(edited) if edited else 0
        st.markdown(f"<div class='sarsa-wc-row'><span class='sarsa-wc-chip'>📊 {w} {t['words']}</span><span class='sarsa-wc-chip'>✏️ {c} {t['chars']}</span></div>", unsafe_allow_html=True)
        tc1, tc2, tc3 = st.columns(3)
        with tc1:
            st.download_button(t["tool_dl"], data=edited,
                file_name=f"sarsa_tool_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                key="tool_dl_btn", use_container_width=True)
        with tc2:
            copy_btn(edited, t["copy"], t["copied"], "tool_main")
        with tc3:
            if st.button(t["tool_clear"], use_container_width=True, key="tool_clear_btn"):
                ss.tool_out = ""; ss.tool_title = ""
                st.rerun()
        st.markdown("<div class='sarsa-divider'></div>", unsafe_allow_html=True)

    # Tool grid
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
                            st.error(f"{t['error']}{e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "history":

    hist = st.session_state.get("history", [])
    st.markdown(f"""
    <div class='sarsa-page-header'>
        <div class='sarsa-page-title'>{t['hist_title']}</div>
        <div class='sarsa-page-sub'>{len(hist)} saved listing{"s" if len(hist) != 1 else ""}</div>
    </div>""", unsafe_allow_html=True)

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
                        st.text_area("", value=entry.get(f"s{ni+1}",""), height=260,
                            key=f"hs{ni+1}_{i}", label_visibility="collapsed", disabled=True)
                hc1, hc2, hc3 = st.columns(3)
                with hc1:
                    if st.button(t["hist_load"], key=f"hl_{i}", use_container_width=True):
                        for n in range(1, 7):
                            st.session_state[f"s{n}"] = entry.get(f"s{n}","")
                        st.session_state.output_ready = True
                        st.session_state.dirty = False
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
