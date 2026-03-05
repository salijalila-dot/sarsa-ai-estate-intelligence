import streamlit as st
from PIL import Image
import google.generativeai as genai
import os

# --- AI YAPILANDIRMASI ---
# Not: Streamlit Cloud'da "Secrets" kısmına GEMINI_API_KEY eklenmiş olmalıdır.
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = 'gemini-1.5-flash' # Hızlı ve verimli model
model = genai.GenerativeModel(MODEL_NAME)

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="SarSa AI | Real Estate Analysis & Marketing Engine",
    page_icon="🏢",
    layout="wide"
)

# --- LOGO YÜKLEME ---
@st.cache_data
def load_logo(file_path):
    if os.path.exists(file_path):
        return Image.open(file_path)
    return None

# --- GLOBAL DİL SİSTEMİ ---
ui_languages = {
    "English": {
        "title": "SarSa AI | Real Estate Intelligence",
        "service_desc": "All-in-One Visual Property Intelligence",
        "settings": "⚙️ Configuration",
        "target_lang": "✍️ Write Listing In...",
        "prop_type": "Property Type",
        "price": "Market Price",
        "location": "Location",
        "tone": "Strategy",
        "tones": ["Standard Pro", "Ultra-Luxury", "Investment Potential", "Modern Minimalist", "Family Comfort"],
        "custom_inst": "📝 Special Notes",
        "btn": "🚀 GENERATE CONTENT",
        "upload_label": "📸 Drop Property Photos Here",
        "result": "💎 Executive Preview",
        "download_all": "📦 Export ALL (Combined)",
        "save_btn": "💾 Save Changes",
        "saved_msg": "✅ All changes saved!",
        "tab_main": "📝 Prime Listing",
        "tab_social": "📱 Social Media Kit",
        "tab_video": "🎬 Video Scripts",
        "tab_tech": "⚙️ Technical Specs",
    },
    "Türkçe": {
        "title": "SarSa AI | Emlak Zekası",
        "service_desc": "Hepsi Bir Arada Görsel Mülk Analizi",
        "settings": "⚙️ Yapılandırma",
        "target_lang": "✍️ İlan Yazım Dili...",
        "prop_type": "Emlak Tipi",
        "price": "Pazar Fiyatı",
        "location": "Konum",
        "tone": "Strateji",
        "tones": ["Standart Profesyonel", "Ultra-Lüks", "Yatırım Potansiyeli", "Modern Minimalist", "Aile Konforu"],
        "custom_inst": "📝 Özel Notlar",
        "btn": "🚀 İÇERİKLERİ OLUŞTUR",
        "upload_label": "📸 Fotoğrafları Buraya Bırakın",
        "result": "💎 Yönetici Önizlemesi",
        "download_all": "📦 HEPSİNİ İNDİR (Tek Dosya)",
        "save_btn": "💾 Değişiklikleri Kaydet",
        "saved_msg": "✅ Değişiklikler kaydedildi!",
        "tab_main": "📝 Ana İlan",
        "tab_social": "📱 Sosyal Medya",
        "tab_video": "🎬 Video Senaryosu",
        "tab_tech": "⚙️ Teknik Özellikler",
    },
    # Diğer diller buraya eklenebilir (Español, Français vb. yukarıdaki yapıya göre)
}

# --- SESSION STATE (OTURUM YÖNETİMİ) ---
# Kullanıcının düzenlemelerini kaybetmemesi için state yönetimi
initial_keys = {
    "listing": "", 
    "social": "", 
    "video": "", 
    "tech": "",
    "is_generated": False
}
for key, val in initial_keys.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- SIDEBAR (YAN MENÜ) ---
with st.sidebar:
    logo_img = load_logo("SarSa_Logo_Transparent.png")
    if logo_img:
        st.image(logo_img, use_container_width=True)
    
    st.divider()
    selected_ui_lang = st.selectbox("🌐 Interface Language", list(ui_languages.keys()))
    t = ui_languages[selected_ui_lang]
    
    st.markdown(f"### {t['settings']}")
    target_lang = st.text_input(t['target_lang'], value="English")
    prop_type = st.text_input(t['prop_type'], placeholder="e.g. Luxury Villa")
    price = st.text_input(t['price'], placeholder="e.g. $1.2M")
    location = st.text_input(t['location'], placeholder="e.g. Bali, Indonesia")
    strategy = st.selectbox(t['tone'], t['tones'])
    special_notes = st.text_area(t['custom_inst'], placeholder="Extra details...")

# --- ANA EKRAN ---
st.title(t['title'])
st.caption(t['service_desc'])

# Fotoğraf Yükleme Alanı
uploaded_files = st.file_uploader(t['upload_label'], type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if st.button(t['btn'], type="primary"):
    if uploaded_files:
        with st.spinner("AI is analyzing and writing..."):
            # Burası AI üretim mantığının olduğu yerdir. 
            # Örnek olarak placeholder dolduruyoruz:
            st.session_state.listing = f"Premium listing for {prop_type} in {location}..."
            st.session_state.social = f"Instagram Post: Check out this {prop_type}!"
            st.session_state.video = "Scene 1: Drone shot of the property..."
            st.session_state.tech = f"Price: {price}\nType: {prop_type}"
            st.session_state.is_generated = True
    else:
        st.warning("Please upload photos first!")

# --- EDİTLENEBİLİR ÖNİZLEME VE KAYIT SİSTEMİ ---
if st.session_state.is_generated:
    st.divider()
    st.subheader(t['result'])
    
    # AUTO-SAVE ENGELLEME: Form yapısı
    with st.form("edit_form"):
        tab1, tab2, tab3, tab4 = st.tabs([t['tab_main'], t['tab_social'], t['tab_video'], t['tab_tech']])
        
        with tab1:
            edited_listing = st.text_area("Sales Copy", value=st.session_state.listing, height=300)
        with tab2:
            edited_social = st.text_area("Social Media Content", value=st.session_state.social, height=300)
        with tab3:
            edited_video = st.text_area("Video Script", value=st.session_state.video, height=300)
        with tab4:
            edited_tech = st.text_area("Technical Specifications", value=st.session_state.tech, height=300)
            
        # Manuel Kayıt Butonu
        save_trigger = st.form_submit_button(t['save_btn'])
        
        if save_trigger:
            st.session_state.listing = edited_listing
            st.session_state.social = edited_social
            st.session_state.video = edited_video
            st.session_state.tech = edited_tech
            st.toast(t['saved_msg'])

    # --- GELİŞMİŞ DIŞA AKTARMA (EXPORT) SEÇENEKLERİ ---
    st.markdown("### 📥 Export Options")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.download_button("📄 Listing TXT", st.session_state.listing, file_name="listing.txt")
    with col2:
        st.download_button("📱 Social TXT", st.session_state.social, file_name="social_kit.txt")
    with col3:
        st.download_button("🎬 Video TXT", st.session_state.video, file_name="video_script.txt")
    with col4:
        st.download_button("⚙️ Specs TXT", st.session_state.tech, file_name="technical_specs.txt")
    
    st.divider()
    # Hepsini Bir Arada İndirme
    combined_text = f"{t['tab_main']}\n{st.session_state.listing}\n\n{t['tab_social']}\n{st.session_state.social}..."
    st.download_button(t['download_all'], combined_text, file_name="sarsa_ai_complete_package.txt", type="primary", use_container_width=True)
