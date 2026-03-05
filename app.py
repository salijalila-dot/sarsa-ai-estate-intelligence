import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
import json
import hashlib
import io
import zipfile
from datetime import datetime
from pathlib import Path
import time

# CONFIGURATION
st.set_page_config(
    page_title="SarSa AI | Professional Real Estate Marketing Suite",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize AI
GOOGLE_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

# Data paths
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"
PROPERTIES_FILE = DATA_DIR / "properties.json"

# DATA FUNCTIONS
def load_json(filepath, default=None):
    if default is None:
        default = {}
    try:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return default

def save_json(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_data():
    return load_json(USERS_FILE, {"users": {}})

def save_user_data(data):
    return save_json(USERS_FILE, data)

def get_properties_data():
    return load_json(PROPERTIES_FILE, {"properties": []})

def save_properties_data(data):
    return save_json(PROPERTIES_FILE, data)

# SESSION STATE
def init_session_state():
    defaults = {
        "authenticated": False, "user_email": None, "user_name": None, "user_tier": "free",
        "credits_used_this_month": 0, "current_property_id": None, "property_name": "",
        "prop_type": "", "price": "", "location": "", "tone": "", "custom_inst": "",
        "target_lang_input": "English", "uploaded_photos": [], "hero_photo_index": 0,
        "content_generated": False, "content_saved": False, "has_unsaved_changes": False,
        "generated_sections": {"prime_listing": "", "social_media": "", "video_script": "", "technical_specs": ""},
        "current_view": "dashboard", "show_upgrade_modal": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# LANGUAGE SYSTEM
LANGUAGES = {
    "English": {
        "brand_name": "SarSa AI", "nav_dashboard": "Dashboard", "nav_new_property": "New Property",
        "nav_logout": "Logout", "dashboard_title": "Property Marketing Dashboard",
        "btn_create_new": "Create New Listing", "recent_properties": "Recent Properties",
        "empty_state_title": "No properties yet", "editor_title": "Create Marketing Assets",
        "section_basic_info": "Basic Information", "section_photos": "Property Photos",
        "field_property_name": "Property Name", "field_property_type": "Property Type",
        "field_price": "Market Price", "field_location": "Location",
        "field_strategy": "Marketing Strategy", "ph_property_name": "e.g., Sunset Villa",
        "ph_property_type": "e.g., Luxury 4BR Villa", "ph_price": "e.g., $1,250,000",
        "strategies": ["Standard Professional", "Ultra-Luxury Premium", "Investment Opportunity", "Modern Minimalist", "Family-Friendly"],
        "btn_generate": "GENERATE MARKETING PACKAGE", "tab_prime": "Prime Listing",
        "tab_social": "Social Media Kit", "tab_video": "Video Script", "tab_tech": "Technical Specs",
        "save_btn": "Save Changes", "saved_msg": "Saved successfully",
        "unsaved_indicator": "Unsaved Changes", "saved_indicator": "All Changes Saved",
        "generated_indicator": "Generated - Save to preserve",
        "warning_unsaved": "You have unsaved changes. Save first.",
        "download_prime": "Listing (TXT)", "download_social": "Social (TXT)",
        "download_video": "Video (TXT)", "download_tech": "Tech (TXT)",
        "download_all": "Download All (ZIP)",
        "filename_prime": "{property_name}_Prime_Listing.txt",
        "filename_social": "{property_name}_Social_Kit.txt",
        "filename_video": "{property_name}_Video_Script.txt",
        "filename_tech": "{property_name}_Tech_Specs.txt",
        "filename_all": "{property_name}_Complete_Package.zip"
    }
}

for lang in ["Türkçe", "Español", "Deutsch", "Français", "Português", "日本語", "中文", "العربية"]:
    LANGUAGES[lang] = LANGUAGES["English"].copy()

def get_text(key, **kwargs):
    lang = st.session_state.get("target_lang_input", "English")
    text = LANGUAGES.get(lang, LANGUAGES["English"]).get(key, key)
    if isinstance(text, list):
        return text
    try:
        return text.format(**kwargs)
    except:
        return text

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #f8fafc; }
h1, h2, h3 { color: #0f172a !important; }
.stButton>button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white !important;
    border-radius: 10px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    border: none;
    transition: all 0.2s;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
}
.stButton>button:disabled {
    background: #cbd5e1;
    cursor: not-allowed;
    transform: none;
}
.badge-success {
    background: #f0fdf4;
    color: #059669;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 10px;
}
.badge-warning {
    background: #fef3c7;
    color: #d97706;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 10px;
}
.badge-info {
    background: #eff6ff;
    color: #1d4ed8;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 10px;
}
.property-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: all 0.2s;
    margin-bottom: 1rem;
}
.property-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    border-color: #3b82f6;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# AUTHENTICATION
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; padding: 3rem 0;'><h1>🏢</h1><h2>SarSa AI</h2><p>Professional Real Estate Marketing</p></div>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        with tab1:
            with st.form("login"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Sign In", use_container_width=True):
                    data = get_user_data()
                    if email in data["users"] and data["users"][email]["password"] == hash_password(password):
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_name = data["users"][email].get("name", email)
                        st.session_state.user_tier = data["users"][email].get("tier", "free")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        with tab2:
            with st.form("signup"):
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if len(password) < 8:
                        st.error("Password too short")
                    elif email and name:
                        data = get_user_data()
                        if email in data["users"]:
                            st.error("Email exists")
                        else:
                            data["users"][email] = {
                                "name": name, "email": email,
                                "password": hash_password(password),
                                "tier": "free", "created_at": datetime.now().isoformat()
                            }
                            save_user_data(data)
                            st.success("Account created! Please sign in.")

# SIDEBAR
def render_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>🏢 SarSa AI</h2>", unsafe_allow_html=True)
        st.markdown("---")
        if st.session_state.user_name:
            st.markdown(f"<p><b>{st.session_state.user_name}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 0.8rem; color: #64748b;'>{st.session_state.user_tier.upper()}</p>", unsafe_allow_html=True)

        if st.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.current_view == "dashboard" else "secondary"):
            st.session_state.current_view = "dashboard"
            st.rerun()
        if st.button("➕ New Property", use_container_width=True, type="primary" if st.session_state.current_view == "editor" else "secondary"):
            st.session_state.current_view = "editor"
            st.rerun()
        if st.button("🏠 My Properties", use_container_width=True, type="primary" if st.session_state.current_view == "properties" else "secondary"):
            st.session_state.current_view = "properties"
            st.rerun()

        st.markdown("---")
        credits = 3 if st.session_state.user_tier == "free" else (50 if st.session_state.user_tier == "pro" else 999999)
        used = st.session_state.credits_used_this_month
        st.markdown(f"<p>Credits: {used}/{credits if credits < 999999 else '∞'}</p>", unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# DASHBOARD
def dashboard_view():
    st.markdown("<h1>📊 Dashboard</h1>", unsafe_allow_html=True)

    data = get_properties_data()
    user_props = [p for p in data.get("properties", []) if p.get("user_email") == st.session_state.user_email]

    cols = st.columns(4)
    stats = [
        (len(user_props), "Total Properties"),
        (len([p for p in user_props if datetime.fromisoformat(p.get("created_at", "2000-01-01")).month == datetime.now().month]), "This Month"),
        (max(0, 3 - st.session_state.credits_used_this_month), "Credits Left"),
        ("24%", "Conversion")
    ]
    for col, (val, label) in zip(cols, stats):
        with col:
            st.markdown(f"<div style='background: white; padding: 1.5rem; border-radius: 12px; text-align: center; border: 1px solid #e2e8f0;'><h2 style='margin: 0; color: #0f172a;'>{val}</h2><p style='color: #64748b; margin: 0;'>{label}</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Create New Listing", use_container_width=True, type="primary"):
        st.session_state.current_property_id = None
        st.session_state.property_name = ""
        st.session_state.prop_type = ""
        st.session_state.content_generated = False
        st.session_state.content_saved = False
        st.session_state.has_unsaved_changes = False
        st.session_state.generated_sections = {"prime_listing": "", "social_media": "", "video_script": "", "technical_specs": ""}
        st.session_state.current_view = "editor"
        st.rerun()

    st.markdown("<br><h3>Recent Properties</h3>", unsafe_allow_html=True)

    if not user_props:
        st.info("No properties yet. Create your first listing!")
    else:
        user_props.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        cols = st.columns(3)
        for idx, prop in enumerate(user_props[:6]):
            with cols[idx % 3]:
                st.markdown(f"<div class='property-card'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='margin: 0 0 0.5rem 0;'>{prop.get('name', 'Untitled')}</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #64748b; margin: 0;'>{prop.get('property_type', 'No type')}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='margin: 0.5rem 0 0 0; font-weight: 600;'>{prop.get('price', 'No price')}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                if st.button("Open", key=f"open_{prop['id']}", use_container_width=True):
                    load_property(prop['id'])
                    st.session_state.current_view = "editor"
                    st.rerun()

def load_property(prop_id):
    data = get_properties_data()
    prop = next((p for p in data.get("properties", []) if p["id"] == prop_id), None)
    if prop:
        st.session_state.current_property_id = prop_id
        st.session_state.property_name = prop.get("name", "")
        st.session_state.prop_type = prop.get("property_type", "")
        st.session_state.price = prop.get("price", "")
        st.session_state.location = prop.get("location", "")
        st.session_state.tone = prop.get("strategy", "")
        st.session_state.target_lang_input = prop.get("target_language", "English")
        st.session_state.custom_inst = prop.get("special_notes", "")
        st.session_state.generated_sections = prop.get("sections", {})
        st.session_state.content_generated = True
        st.session_state.content_saved = True
        st.session_state.has_unsaved_changes = False

# EDITOR
def editor_view():
    credits_limit = 3 if st.session_state.user_tier == "free" else (50 if st.session_state.user_tier == "pro" else 999999)

    if st.session_state.credits_used_this_month >= credits_limit:
        st.error("Monthly limit reached. Upgrade your plan.")
        return

    st.markdown(f"<h1>{get_text('editor_title')}</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"<h3>{get_text('section_basic_info')}</h3>", unsafe_allow_html=True)
        st.session_state.property_name = st.text_input(get_text("field_property_name"), value=st.session_state.property_name, placeholder=get_text("ph_property_name"))
        st.session_state.prop_type = st.text_input(get_text("field_property_type"), value=st.session_state.prop_type, placeholder=get_text("ph_property_type"))
        st.session_state.price = st.text_input(get_text("field_price"), value=st.session_state.price, placeholder=get_text("ph_price"))
        st.session_state.location = st.text_input("Location", value=st.session_state.location)

        strategies = get_text("strategies")
        current = st.session_state.tone if st.session_state.tone in strategies else strategies[0]
        st.session_state.tone = st.selectbox(get_text("field_strategy"), strategies, index=strategies.index(current) if current in strategies else 0)

        langs = list(LANGUAGES.keys())
        st.session_state.target_lang_input = st.selectbox("Output Language", langs, index=langs.index(st.session_state.target_lang_input) if st.session_state.target_lang_input in langs else 0)
        st.session_state.custom_inst = st.text_area("Special Notes", value=st.session_state.custom_inst)

    with col2:
        st.markdown(f"<h3>{get_text('section_photos')}</h3>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload Photos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

        if uploaded:
            st.session_state.uploaded_photos = uploaded
            cols = st.columns(min(len(uploaded), 4))
            for idx, file in enumerate(uploaded):
                with cols[idx % 4]:
                    img = Image.open(file)
                    is_hero = idx == st.session_state.hero_photo_index
                    if is_hero:
                        st.markdown("<span style='background: #f59e0b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem;'>HERO</span>", unsafe_allow_html=True)
                    st.image(img, use_container_width=True)
                    if st.button("⭐ Set Hero", key=f"hero_{idx}"):
                        st.session_state.hero_photo_index = idx
                        st.rerun()

        if st.session_state.has_unsaved_changes:
            st.warning(get_text("warning_unsaved"))

        can_generate = st.session_state.uploaded_photos and st.session_state.prop_type and not st.session_state.has_unsaved_changes

        if st.button(get_text("btn_generate"), use_container_width=True, type="primary", disabled=not can_generate):
            generate_ai_content()

    if st.session_state.content_generated:
        render_results()

def generate_ai_content():
    with st.spinner("Generating..."):
        try:
            images = [Image.open(f) for f in st.session_state.uploaded_photos]

            prompt = f"""Create real estate marketing content for: {st.session_state.prop_type} in {st.session_state.location}
Price: {st.session_state.price} | Strategy: {st.session_state.tone}

Use EXACT headers:
## PRIME_LISTING - Compelling sales copy (300 words)
## SOCIAL_MEDIA_KIT - Instagram, Facebook, LinkedIn posts with hashtags
## VIDEO_SCRIPT - 60-sec cinematic script with scenes and voiceover
## TECHNICAL_SPECS - Professional specs and features list

Language: {st.session_state.target_lang_input}"""

            response = model.generate_content([prompt] + images)
            text = response.text

            sections = {"prime_listing": "", "social_media": "", "video_script": "", "technical_specs": ""}
            if "## PRIME_LISTING" in text:
                sections["prime_listing"] = text.split("## PRIME_LISTING")[1].split("##")[0].strip()
            if "## SOCIAL_MEDIA_KIT" in text:
                sections["social_media"] = text.split("## SOCIAL_MEDIA_KIT")[1].split("##")[0].strip()
            if "## VIDEO_SCRIPT" in text:
                sections["video_script"] = text.split("## VIDEO_SCRIPT")[1].split("##")[0].strip()
            if "## TECHNICAL_SPECS" in text:
                sections["technical_specs"] = text.split("## TECHNICAL_SPECS")[1].strip()

            st.session_state.generated_sections = sections
            st.session_state.content_generated = True
            st.session_state.content_saved = False
            st.session_state.has_unsaved_changes = False
            st.session_state.credits_used_this_month += 1
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

def render_results():
    st.markdown("---")

    if st.session_state.has_unsaved_changes:
        st.markdown("<div class='badge-warning'>Unsaved Changes - Save to preserve edits</div>", unsafe_allow_html=True)
    elif st.session_state.content_saved:
        st.markdown("<div class='badge-success'>All Changes Saved</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='badge-info'>New Content Generated - Click Save to preserve</div>", unsafe_allow_html=True)

    tabs = st.tabs([get_text("tab_prime"), get_text("tab_social"), get_text("tab_video"), get_text("tab_tech")])
    keys = ["prime_listing", "social_media", "video_script", "technical_specs"]
    edited = {}

    for tab, key in zip(tabs, keys):
        with tab:
            original = st.session_state.generated_sections.get(key, "")
            new_val = st.text_area("Content", value=original, height=300, key=f"edit_{key}", label_visibility="collapsed")
            edited[key] = new_val
            if new_val != original:
                st.session_state.has_unsaved_changes = True

    if st.button(get_text("save_btn"), type="primary", use_container_width=True):
        for key in keys:
            st.session_state.generated_sections[key] = edited[key]
        st.session_state.content_saved = True
        st.session_state.has_unsaved_changes = False
        save_to_db()
        st.success(get_text("saved_msg"))
        st.rerun()

    st.markdown("---")
    st.markdown("<h3>Export Options</h3>", unsafe_allow_html=True)

    name = (st.session_state.property_name or "Property").replace(" ", "_")[:50]

    cols = st.columns(5)
    exports = [
        (get_text("download_prime"), get_text("filename_prime").format(property_name=name), "prime_listing"),
        (get_text("download_social"), get_text("filename_social").format(property_name=name), "social_media"),
        (get_text("download_video"), get_text("filename_video").format(property_name=name), "video_script"),
        (get_text("download_tech"), get_text("filename_tech").format(property_name=name), "technical_specs"),
    ]

    for col, (label, filename, key) in zip(cols[:4], exports):
        with col:
            content = st.session_state.generated_sections[key]
            st.download_button(label, data=content, file_name=filename, mime="text/plain", use_container_width=True)

    with cols[4]:
        if st.button(get_text("download_all"), use_container_width=True):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for filename, key in [(e[1], e[2]) for e in exports]:
                    section_name = filename.split('_', 1)[1].replace('.txt', '').replace('_', ' ').upper()
                    content = f"{section_name}\n{'='*50}\n\n{st.session_state.generated_sections[key]}"
                    zf.writestr(filename, content)
            zip_buffer.seek(0)
            st.download_button("📥 Download ZIP", data=zip_buffer.getvalue(), file_name=get_text("filename_all").format(property_name=name), mime="application/zip", use_container_width=True)

def save_to_db():
    data = get_properties_data()
    prop_id = st.session_state.current_property_id or f"prop_{int(time.time())}"

    prop_data = {
        "id": prop_id,
        "user_email": st.session_state.user_email,
        "name": st.session_state.property_name or "Untitled",
        "property_type": st.session_state.prop_type,
        "price": st.session_state.price,
        "location": st.session_state.location,
        "strategy": st.session_state.tone,
        "target_language": st.session_state.target_lang_input,
        "special_notes": st.session_state.custom_inst,
        "sections": st.session_state.generated_sections,
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    existing = next((i for i, p in enumerate(data["properties"]) if p["id"] == prop_id), None)
    if existing is not None:
        data["properties"][existing] = prop_data
    else:
        data["properties"].append(prop_data)
        st.session_state.current_property_id = prop_id

    save_properties_data(data)

# MAIN
def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        render_sidebar()
        if st.session_state.current_view == "dashboard":
            dashboard_view()
        elif st.session_state.current_view == "editor":
            editor_view()
        elif st.session_state.current_view == "properties":
            dashboard_view()

if __name__ == "__main__":
    main()
