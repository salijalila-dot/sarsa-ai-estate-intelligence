import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
from datetime import datetime

# ─── AI CONFIGURATION ───────────────────────────────────────────────────────
# API Key erişimi düzeltildi
GOOGLE_API_KEY = st.secrets
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

# ─── LANGUAGE SYSTEM (Fixed Syntax Error) ───────────────────────────────────
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
        "tones":,
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
        "furnishing_opts":,
        "target_audience": "Target Audience",
        "audience_opts":,
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
        "err_connection": "Connection Error: Could not reach the AI service. Please check your internet connection.",
        "err_quota": "Quota Exceeded: The service is temporarily at capacity. Please try again in a minute.",
        "err_image": "Image Error: One or more photos could not be processed. Use clear JPG/PNG files.",
        "err_generic": "An unexpected error occurred. Please try again.",
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
        "service_desc": "Hepsi Bir Arada Görsel Mülk Zekası ve Küresel Satış Otomasyonu",
        "subtitle": "Mülk fotoğraflarını anında profesyonel ilanlara, sosyal medya kitlerine, sinematik senaryolara, teknik şartnamelere, e-posta kampanyalarına ve SEO metinlerine dönüştürün.",
        "settings": "Yapılandırma",
        "target_lang": "İlan Yazım Dili...",
        "prop_type": "Emlak Tipi",
        "price": "Pazar Fiyatı",
        "location": "Konum",
        "tone": "Pazarlama Stratejisi",
        "tones":,
        "ph_prop": "Örn: 3+1 Daire, Müstakil Villa...",
        "ph_price": "Örn: 5.000.000 TL veya $2.500/ay...",
        "ph_loc": "Örn: Beşiktaş, İstanbul...",
        "bedrooms": "Yatak Odası",
        "bathrooms": "Banyo",
        "area": "Alan",
        "year_built": "İnşaat Yılı",
        "ph_beds": "Örn: 3",
        "ph_baths": "Örn: 2",
        "ph_area": "Örn: 185 m2",
        "ph_year": "Örn: 2022",
        "furnishing": "Eşya Durumu",
        "furnishing_opts":,
        "target_audience": "Hedef Kitle",
        "audience_opts":,
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
        "err_connection": "Bağlantı Hatası: AI servisine ulaşılamadı. İnternetinizi kontrol edin.",
        "err_quota": "API Kotası Aşıldı: Servis geçici olarak dolu. Lütfen bir dakika sonra tekrar deneyin.",
        "err_image": "Görsel Hatası: Fotoğraflar işlenemedi. Lütfen net JPG/PNG dosyaları kullanın.",
        "err_generic": "Beklenmedik bir hata oluştu. Lütfen tekrar deneyin.",
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
        "extra_details": "Ek Mülk Detaylari",
        "marketing_config": "Pazarlama Ayarları",
        "interface_lang": "Arayüz Dili",
        "config_section": "Yapılandırma",
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

# ─── CSS (PRO SIDEBAR & UI FIXES) ──────────────────────────────────────────
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif!important; }
.stApp { background-color: #f0f4f8!important; }
div[data-testid="stInputInstructions"] { display: none!important; }
#MainMenu, footer { display: none!important; }
span[data-testid="stIconMaterial"] { display: none!important; }

/* ── PRO SIDEBAR BUTTONS (CUSTOM EMOJIS) ── */
/* 1. Sidebar Kapatma Butonu (Sidebar açıkken) */
 button {
    background-color: #0f172a!important;
    border: 1px solid #1e293b!important;
    border-radius: 8px!important;
    width: 2.5rem!important;
    height: 2.5rem!important;
    display: flex!important;
    align-items: center!important;
    justify-content: center!important;
}
 button:after {
    content: "➡️"!important;
    font-size: 1.2rem!important;
}
 button svg { display: none!important; }

/* 2. Sidebar Açma Butonu (Sidebar kapalıyken) */
 button {
    background-color: #0f172a!important;
    border: 1px solid #1e293b!important;
    border-radius: 8px!important;
    width: 2.5rem!important;
    height: 2.5rem!important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2)!important;
    display: flex!important;
    align-items: center!important;
    justify-content: center!important;
}
 button:after {
    content: "⬅️"!important;
    font-size: 1.2rem!important;
}
 button svg { display: none!important; }

.block-container {
    background: white; padding: 2.5rem 3rem!important;
    border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.06);
    margin-top: 1.5rem; border: 1px solid #e2e8f0;
}
h1 { color: #0f172a!important; font-weight: 800!important; text-align: center; }

 { background: #ffffff!important; border-right: 1px solid #e2e8f0!important; }

.stButton > button {
    background: #0f172a!important; color: white!important;
    border-radius: 12px!important; padding: 14px 24px!important;
    font-weight: 700!important; font-size: 0.95rem!important;
    width: 100%!important; border: none!important;
    transition: all 0.25s ease!important;
    box-shadow: 0 4px 15px rgba(15,23,42,0.3)!important;
}

.stTabs [aria-selected="true"] {
    background-color: #0f172a!important; color: white!important;
    border-radius: 8px 8px 0 0!important;
}
</style>
""")

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    logo_img = load_logo("SarSa_Logo_Transparent.png")
    if logo_img:
        st.image(logo_img, use_container_width=True)
    else:
        st.html("""
        <div style="text-align:center; padding:0.8rem 0 0.5rem;">
          <span style="font-size:1.8rem; font-weight:800; color:#0f172a;">SarSa</span>
          <span style="font-size:1.8rem; font-weight:800; background:linear-gradient(135deg,#3b82f6,#8b5cf6);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;"> AI</span>
          <div style="font-size:0.62rem;color:#94a3b8;letter-spacing:2px;text-transform:uppercase;margin-top:2px;">
          Real Estate Intelligence</div>
        </div>""")

    st.markdown("<br>", unsafe_allow_html=True)
    current_ui_lang = st.selectbox("🌐 Interface Language", list(ui_languages.keys()), index=0)
    t = ui_languages[current_ui_lang]

    st.markdown("---")
    st.header(t["settings"])

    st.session_state.target_lang_input = st.text_input(f"✍️ {t['target_lang']}", value=st.session_state.target_lang_input)
    st.session_state.prop_type = st.text_input(t["prop_type"], value=st.session_state.prop_type, placeholder=t["ph_prop"])
    st.session_state.price = st.text_input(t["price"], value=st.session_state.price, placeholder=t["ph_price"])
    st.session_state.location = st.text_input(t["location"], value=st.session_state.location, placeholder=t["ph_loc"])

    tones = t["tones"]
    current_tone_idx = tones.index(st.session_state.tone) if st.session_state.tone in tones else 0
    st.session_state.tone = st.selectbox(t["tone"], tones, index=current_tone_idx)

    st.session_state.custom_inst = st.text_area(f"📝 {t['custom_inst']}", value=st.session_state.custom_inst, placeholder=t["custom_inst_ph"], height=100)

    st.html(f"""<div style="font-size:0.68rem; font-weight:800; color:#94a3b8; text-transform:uppercase; letter-spacing:1.4px; padding:0.6rem 0 0.3rem 0; border-bottom:1px solid #f1f5f9; margin-bottom:0.4rem;">🔑 {t['extra_details']}</div>""")

    col1, col2 = st.columns(2)
    with col1: st.session_state.bedrooms = st.text_input(t["bedrooms"], value=st.session_state.bedrooms, placeholder=t["ph_beds"])
    with col2: st.session_state.bathrooms = st.text_input(t["bathrooms"], value=st.session_state.bathrooms, placeholder=t["ph_baths"])
    
    col3, col4 = st.columns(2)
    with col3: st.session_state.area_size = st.text_input(t["area"], value=st.session_state.area_size, placeholder=t["ph_area"])
    with col4: st.session_state.year_built = st.text_input(t["year_built"], value=st.session_state.year_built, placeholder=t["ph_year"])

    furnishing_opts = t["furnishing_opts"]
    furnishing_sel = st.selectbox(t["furnishing"], furnishing_opts, index=st.session_state.furnishing_idx)
    st.session_state.furnishing_idx = furnishing_opts.index(furnishing_sel)

    audience_opts = t["audience_opts"]
    audience_sel = st.selectbox(t["target_audience"], audience_opts, index=st.session_state.audience_idx)
    st.session_state.audience_idx = audience_opts.index(audience_sel)

    st.html(f"""<div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:0.7rem 1rem; font-size:0.78rem; color:#1e40af; margin-top:0.8rem; line-height:1.5;">💡 {t['pro_tip']}</div>""")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(f"🗑️ {t['clear_btn']}", use_container_width=True):
        for k in ["uretilen_ilan", "prop_type", "price", "location", "tone", "custom_inst", "bedrooms", "bathrooms", "area_size", "year_built"]:
            st.session_state[k] = ""
        st.session_state.furnishing_idx = 0
        st.session_state.audience_idx = 0
        st.rerun()

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
st.html(f"<h1>🏢 {t['title']}</h1>")
st.html(f"<p style='text-align:center; color:#0f172a; font-weight:700; font-size:1.35rem; letter-spacing:0.3px; margin-bottom:5px;'>{t['service_desc']}</p>")
st.html(f"<div style='text-align:center; color:#64748b; font-size:1rem; max-width:850px; margin:0 auto 2rem auto; line-height:1.6;'>{t['subtitle']}</div>")

uploaded_files = st.file_uploader(f"📸 {t['upload_label']}", type=["jpg", "png", "webp", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    images_for_ai = [Image.open(f) for f in uploaded_files]
    n = len(images_for_ai)
    st.html(f"<div style='display:inline-flex;align-items:center;gap:6px;background:#dbeafe;color:#1d4ed8;border-radius:20px;padding:4px 12px;font-size:0.78rem;font-weight:700;margin-bottom:0.8rem;'>📷 {n} {t['photos_uploaded']}</div>")

    cols = st.columns(min(n, 4))
    for i, img in enumerate(images_for_ai):
        with cols[i % min(n, 4)]: st.image(img, use_container_width=True)

    if st.button(f"🚀 {t['btn']}"):
        with st.spinner(t["loading"]):
            p_type  = st.session_state.prop_type or "Property"
            p_loc   = st.session_state.location or "Undisclosed Location"
            p_price = st.session_state.price or "Price upon request"
            p_furn  = furnishing_sel if furnishing_sel!= t["furnishing_opts"] else "Not specified"
            p_aud   = audience_sel if audience_sel!= t["audience_opts"] else "General Market"

            details = f"PROPERTY DETAILS:\n- Type: {p_type}\n- Location: {p_loc}\n- Price: {p_price}\n- Bedrooms: {st.session_state.bedrooms}\n- Bathrooms: {st.session_state.bathrooms}\n- Area: {st.session_state.area_size}\n- Year: {st.session_state.year_built}\n- Furnishing: {p_furn}\n- Audience: {p_aud}\n- Tone: {st.session_state.tone}"
            
            prompt = f"You are a Senior Real Estate Strategist for SarSa AI. OUTPUT LANGUAGE: {st.session_state.target_lang_input}. {details}. Generate 6 SECTIONS: SECTION_1 (Listing), SECTION_2 (Social Kit), SECTION_3 (Video Script), SECTION_4 (Tech Specs), SECTION_5 (Email), SECTION_6 (SEO)."

            try:
                response = model.generate_content([prompt] + images_for_ai)
                st.session_state.uretilen_ilan = response.text
            except Exception as e:
                err_msg = str(e).lower()
                if "quota" in err_msg: st.error(t["err_quota"])
                elif "connection" in err_msg: st.error(t["err_connection"])
                elif "image" in err_msg: st.error(t["err_image"])
                else: st.error(f"{t['err_generic']} ({str(e)})")

    if st.session_state.uretilen_ilan:
        raw = st.session_state.uretilen_ilan
        sec = {str(i): "" for i in range(1, 7)}
        for p in raw.split("##"):
            p = p.strip()
            for n in ["1", "2", "3", "4", "5", "6"]:
                if p.startswith(f"SECTION_{n}"):
                    content = p.strip().lstrip("—-– \n")
                    if ":" in content[:10]: content = content.split(":", 1)[-1].strip()
                    sec[n] = content
                    break

        st.markdown("---")
        st.html(f"""<div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);border-radius:14px; padding:1.2rem 1.8rem;margin-bottom:1rem;display:flex;align-items:center;justify-content:space-between;"><div><div style="font-size:1.1rem;font-weight:800;color:#fff;">💎 {t['result']}</div><div style="font-size:0.8rem;color:#94a3b8;margin-top:3px;">{st.session_state.prop_type} — {st.session_state.tone}</div></div></div>""")

        tabs = st.tabs([f"📝 {t['tab_main']}", f"📱 {t['tab_social']}", f"🎬 {t['tab_video']}", f"⚙️ {t['tab_tech']}", f"✉️ {t['tab_email']}", f"🔍 {t['tab_seo']}"])
        suffixes = ["listing", "social", "video", "tech", "email", "seo"]
        
        for i, tab in enumerate(tabs):
            with tab:
                label_key = f"label_{suffixes[i]}"
                edited = st.text_area(t[label_key], value=sec[str(i+1)], height=450, key=f"txt_{i}")
                c1, c2 = st.columns(2)
                with c1: 
                    if st.button(f"💾 {t['save_btn']}", key=f"save_{i}"): st.success(t["saved_msg"])
                with c2: st.download_button(f"📥 {t['download']}", data=edited, file_name=f"sarsa_{suffixes[i]}.txt", key=f"dl_{i}")

else:
    # ── EMPTY STATE (ALL BLUE TAGS) ──
    st.html(f"""
    <div style="text-align:center;padding:4rem 2rem;color:#94a3b8; border:2px dashed #e2e8f0;border-radius:16px;background:#fafbfc;">
        <div style="font-size:3.5rem;margin-bottom:1rem;opacity:0.5;">🏘️</div>
        <div style="font-size:1.25rem;font-weight:700;color:#475569;margin-bottom:0.8rem;">{t['result']}</div>
        <div style="font-size:0.9rem;max-width:420px;margin:0 auto;line-height:1.6;color:#64748b;">{t['empty']}</div>
        <div style="display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:1.4rem;">
            <span style="background:#dbeafe;color:#1d4ed8;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #bfdbfe;">📝 {t['tab_main']}</span>
            <span style="background:#dbeafe;color:#1d4ed8;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #bfdbfe;">📱 {t['tab_social']}</span>
            <span style="background:#dbeafe;color:#1d4ed8;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #bfdbfe;">🎬 {t['tab_video']}</span>
            <span style="background:#dbeafe;color:#1d4ed8;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #bfdbfe;">⚙️ {t['tab_tech']}</span>
            <span style="background:#dbeafe;color:#1d4ed8;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #bfdbfe;">✉️ {t['tab_email']}</span>
            <span style="background:#dbeafe;color:#1d4ed8;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #bfdbfe;">🔍 {t['tab_seo']}</span>
        </div>
    </div>
    """)
