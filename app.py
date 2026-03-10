import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
from datetime import datetime
from supabase import create_client, Client

# ─── SUPABASE CONFIGURATION ────────────────────────────────────────────────
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ─── SESSION STATE INITIALIZATION ──────────────────────────────────────────
if 'auth_lang' not in st.session_state:
    st.session_state.auth_lang = "English"
    
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# ─── AUTH LANGUAGES (ALL 9 LANGUAGES ADDED & UPDATED) ───────────────────────────────
auth_texts = {
    "English": {
        "access": "SarSa AI Access", "login": "Login", "register": "Register", "email": "Email", "password": "Password", 
        "btn_login": "Login", "btn_reg": "Create Account", "success_reg": "Registration successful! Check your email to verify your account.", 
        "error_login": "Login failed. You are not registered, or your Email/Password is incorrect.", "verify_msg": "⚠️ Please verify your email:", "btn_check": "I verified, let me in", 
        "unpaid_msg": "Subscription required.", "upgrade_title": "🚀 Professional Plan", "pay_btn": "Subscribe Now",
        "welcome_title": "Welcome to SarSa AI", "welcome_desc": "The All-in-One Visual Property Intelligence & Global Sales Automation platform. Transform your property photos into professional assets in seconds.", "login_prompt": "Log in to use the application",
        "forgot_pw": "Forgot Password?", "btn_reset": "Send Reset Link", "reset_success": "Reset link sent to your email."
    },
    "Türkçe": {
        "access": "SarSa AI Erişimi", "login": "Giriş Yap", "register": "Kayıt Ol", "email": "E-posta", "password": "Şifre", 
        "btn_login": "Oturum Aç", "btn_reg": "Hesap Oluştur", "success_reg": "Kayıt başarılı! Hesabınızı onaylamak için e-postanızı kontrol edin.", 
        "error_login": "Giriş başarısız. Kayıtlı değilsiniz veya E-posta/Şifreniz hatalı.", "verify_msg": "⚠️ Lütfen e-postanızı onaylayın:", "btn_check": "Onayladım, içeri al", 
        "unpaid_msg": "Abonelik gerekiyor.", "upgrade_title": "🚀 Profesyonel Paket", "pay_btn": "Şimdi Abone Ol",
        "welcome_title": "SarSa AI'a Hoş Geldiniz", "welcome_desc": "Hepsi Bir Arada Görsel Mülk Zekâsı ve Küresel Satış Otomasyonu platformu. Mülk fotoğraflarınızı saniyeler içinde profesyonel varlıklara dönüştürün.", "login_prompt": "Uygulamayı kullanmak için giriş yapın",
        "forgot_pw": "Şifremi Unuttum?", "btn_reset": "Sıfırlama Bağlantısı Gönder", "reset_success": "Sıfırlama bağlantısı e-postanıza gönderildi."
    },
    "Español": {
        "access": "Acceso a SarSa AI", "login": "Iniciar Sesión", "register": "Registrarse", "email": "Correo", "password": "Clave", 
        "btn_login": "Entrar", "btn_reg": "Crear Cuenta", "success_reg": "¡Registro exitoso! Revisa tu email para verificar tu cuenta.", 
        "error_login": "Error. No estás registrado o tu Correo/Clave es incorrecto.", "verify_msg": "⚠️ Verifica tu email:", "btn_check": "Ya verifiqué, entrar", 
        "unpaid_msg": "Suscripción necesaria.", "upgrade_title": "🚀 Plan Profesional", "pay_btn": "Suscribirse Ahora",
        "welcome_title": "Bienvenido a SarSa AI", "welcome_desc": "La plataforma todo en uno de Inteligencia Visual de Propiedades y Automatización de Ventas. Transforme sus fotos en activos profesionales en segundos.", "login_prompt": "Inicie sesión para usar la aplicación",
        "forgot_pw": "¿Olvidaste tu contraseña?", "btn_reset": "Enviar enlace", "reset_success": "Enlace de restablecimiento enviado."
    },
    "Deutsch": {
        "access": "SarSa AI Zugang", "login": "Anmelden", "register": "Registrieren", "email": "E-Mail", "password": "Passwort", 
        "btn_login": "Login", "btn_reg": "Konto Erstellen", "success_reg": "Erfolgreich! Bitte bestätigen Sie Ihre E-Mail.", 
        "error_login": "Login fehlgeschlagen. Nicht registriert oder E-Mail/Passwort falsch.", "verify_msg": "⚠️ E-Mail bestätigen:", "btn_check": "Bestätigt, einloggen", 
        "unpaid_msg": "Abo erforderlich.", "upgrade_title": "🚀 Profi-Paket", "pay_btn": "Jetzt Abonnieren",
        "welcome_title": "Willkommen bei SarSa AI", "welcome_desc": "Die All-in-One-Plattform für visuelle Immobilienintelligenz. Verwandeln Sie Ihre Immobilienfotos in Sekundenschnelle in professionelle Assets.", "login_prompt": "Melden Sie sich an, um die App zu nutzen",
        "forgot_pw": "Passwort vergessen?", "btn_reset": "Link senden", "reset_success": "Link an E-Mail gesendet."
    },
    "Français": {
        "access": "Accès SarSa AI", "login": "Connexion", "register": "S'inscrire", "email": "Email", "password": "Mot de passe", 
        "btn_login": "Se connecter", "btn_reg": "Créer un compte", "success_reg": "Succès ! Vérifiez vos emails pour confirmer.", 
        "error_login": "Échec. Vous n'êtes pas inscrit ou Email/Mot de passe incorrect.", "verify_msg": "⚠️ Vérifiez votre email :", "btn_check": "Vérifié, entrer", 
        "unpaid_msg": "Abonnement requis.", "upgrade_title": "🚀 Pack Professionnel", "pay_btn": "S'abonner Maintenant",
        "welcome_title": "Bienvenue sur SarSa AI", "welcome_desc": "La plateforme d'Intelligence Visuelle Immobilière et d'Automatisation des Ventes. Transformez vos photos en atouts professionnels en quelques secondes.", "login_prompt": "Connectez-vous pour utiliser l'application",
        "forgot_pw": "Mot de passe oublié ?", "btn_reset": "Envoyer le lien", "reset_success": "Lien envoyé par e-mail."
    },
    "Português": {
        "access": "Acesso SarSa AI", "login": "Entrar", "register": "Registar", "email": "Email", "password": "Senha", 
        "btn_login": "Login", "btn_reg": "Criar Conta", "success_reg": "Sucesso! Verifique seu email para confirmar a conta.", 
        "error_login": "Falha. Não registado ou Email/Senha incorretos.", "verify_msg": "⚠️ Verifique seu email:", "btn_check": "Verificado, entrar", 
        "unpaid_msg": "Assinatura necessária.", "upgrade_title": "🚀 Plano Profissional", "pay_btn": "Assinar Agora",
        "welcome_title": "Bem-vindo ao SarSa AI", "welcome_desc": "A plataforma tudo-em-um de Inteligência Imobiliária Visual e Automação de Vendas. Transforme as suas fotos em ativos profissionais em segundos.", "login_prompt": "Faça login para usar o aplicativo",
        "forgot_pw": "Esqueceu a senha?", "btn_reset": "Enviar link", "reset_success": "Link enviado para seu e-mail."
    },
    "日本語": {
        "access": "SarSa AI アクセス", "login": "ログイン", "register": "新規登録", "email": "メール", "password": "パスワード", 
        "btn_login": "ログイン", "btn_reg": "アカウント作成", "success_reg": "登録完了！メールを確認してアカウントを認証してください。", 
        "error_login": "ログイン失敗。未登録か、メール/パスワードが間違っています。", "verify_msg": "⚠️ メールを認証してください:", "btn_check": "認証済み、入る", 
        "unpaid_msg": "サブスクリプションが必要です。", "upgrade_title": "🚀 プロフェッショナルプラン", "pay_btn": "今すぐ購読",
        "welcome_title": "SarSa AI へようこそ", "welcome_desc": "オールインワンの視覚的物件インテリジェンス＆販売自動化プラットフォーム。物件の写真を数秒でプロフェッショナルな資産に変換します。", "login_prompt": "アプリを使用するにはログインしてください",
        "forgot_pw": "パスワードをお忘れですか？", "btn_reset": "リンクを送信", "reset_success": "リセットリンクが送信されました。"
    },
    "简体中文": {
        "access": "SarSa AI 访问", "login": "登录", "register": "注册", "email": "邮箱", "password": "密码", 
        "btn_login": "登录", "btn_reg": "创建账号", "success_reg": "注册成功！请检查邮箱以验证账号。", 
        "error_login": "登录失败。您未注册，或邮箱/密码错误。", "verify_msg": "⚠️ 请验证您的邮箱:", "btn_check": "已验证，进入", 
        "unpaid_msg": "需要订阅。", "upgrade_title": "🚀 专业版方案", "pay_btn": "立即订阅",
        "welcome_title": "欢迎来到 SarSa AI", "welcome_desc": "全方位房产视觉智能与全球销售自动化平台。在几秒钟内将您的房产照片转化为专业的营销资产。", "login_prompt": "登录以使用该应用程序",
        "forgot_pw": "忘记密码？", "btn_reset": "发送重置链接", "reset_success": "重置链接已发送到您的邮箱。"
    },
    "العربية": {
        "access": "دخول SarSa AI", "login": "تسجيل الدخول", "register": "إنشاء حساب", "email": "البريد", "password": "كلمة السر", 
        "btn_login": "دخول", "btn_reg": "إنشاء حساب", "success_reg": "تم التسجيل بنجاح! تحقق من بريدك لتأكيد الحساب.", 
        "error_login": "فشل الدخول. أنت غير مسجل، أو البريد/كلمة السر خاطئة.", "verify_msg": "⚠️ يرجى تأكيد بريدك:", "btn_check": "تم التأكيد، دخول", 
        "unpaid_msg": "يتطلب اشتراكاً نشطاً.", "upgrade_title": "🚀 الباقة الاحترافية", "pay_btn": "اشترك الآن",
        "welcome_title": "مرحباً بك في SarSa AI", "welcome_desc": "منصة الذكاء البصري المتكامل للعقارات وأتمتة المبيعات العالمية. حول صور عقاراتك إلى أصول احترافية في ثوانٍ.", "login_prompt": "قم بتسجيل الدخول لاستخدام التطبيق",
        "forgot_pw": "نسيت كلمة السر؟", "btn_reset": "إرسال رابط الاستعادة", "reset_success": "تم إرسال رابط إعادة التعيين."
    }
}


# ─── AUTH FUNCTIONS ────────────────────────────────────────────────────────
def get_status():
    if st.session_state.get('is_logged_in'):
        return "paid", st.session_state.user_email

    try:
        user_resp = supabase.auth.get_user()
        if not user_resp or not user_resp.user:
            return "logged_out", None
        
        user = user_resp.user
        
        if not user.email_confirmed_at:
            return "unverified", user.email

        st.session_state.is_logged_in = True
        st.session_state.user_email = user.email
        return "paid", user.email
    except Exception as e:
        return "logged_out", None

# ─── UI FLOW ───────────────────────────────────────────────────────────────
auth_status, user_email = get_status()

def update_lang():
    st.session_state.auth_lang = st.session_state.lang_selector

if auth_status != "paid":
    st.selectbox("🌐 Select Language / Dil Seçin", list(auth_texts.keys()), 
                 index=list(auth_texts.keys()).index(st.session_state.auth_lang),
                 key="lang_selector", on_change=update_lang)

at = auth_texts.get(st.session_state.auth_lang, auth_texts["English"])

if auth_status == "logged_out":
    col_logo, col_text = st.columns([1, 6])
    
    with col_logo:
        if os.path.exists("SarSa_Logo_Transparent.png"):
            st.image(Image.open("SarSa_Logo_Transparent.png"), use_container_width=True)
            
    with col_text:
        st.markdown(f"<h1 style='text-align:left; color:#0f172a; font-weight:800; margin-top:0; padding-top:0;'>{at['welcome_title']}</h1>", unsafe_allow_html=True)
        
    st.markdown(f"<p style='font-size:1.15rem; color:#475569; font-weight:500; margin-bottom:2rem;'>{at['welcome_desc']}</p>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid #e2e8f0; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='text-align:center; color:#0f172a; margin-bottom:1.5rem;'>{at['login_prompt']}</h3>", unsafe_allow_html=True)

    st.markdown("""<style>.stTabs [data-baseweb="tab-list"] {justify-content: center;}</style>""", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([f"🔑 {at['login']}", f"📝 {at['register']}"])

    with tab1:
        with st.form("l_form"):
            e = st.text_input(at['email'])
            p = st.text_input(at['password'], type="password")
            submit_l = st.form_submit_button(at['btn_login'], use_container_width=True)
            
            if submit_l:
                try:
                    res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                    if res.user:
                        st.session_state.is_logged_in = True
                        st.session_state.user_email = e
                        st.success("Giriş başarılı!")
                        st.rerun()
                except Exception as ex:
                    error_msg = str(ex)
                    if "Email not confirmed" in error_msg:
                        st.error(f"{at['verify_msg']} {e}")
                    elif "Invalid login credentials" in error_msg:
                        st.error(f"❌ {at['error_login']}")
                    else:
                        st.error(f"Sistem Hatası: {error_msg}")

    with tab2:
        with st.form("r_form"):
            ne = st.text_input(at['email'])
            np = st.text_input(at['password'] + " (Min 6)", type="password")
            if st.form_submit_button(at['btn_reg'], use_container_width=True):
                try:
                    res = supabase.auth.sign_up({"email": ne, "password": np})
                    if res.user:
                        st.success(f"✅ {at['success_reg']}")
                except Exception as ex: 
                    error_msg = str(ex)
                    if "User already registered" in error_msg:
                        st.error("Bu e-posta adresi zaten kayıtlı. Lütfen giriş yapın.")
                    else:
                        st.error(f"Kayıt Hatası: {ex}")

# GATEKEEPER - GİRİŞ YAPILMADIYSA UYGULAMANIN GERİ KALANINI DURDUR
if auth_status != "paid":
    st.stop()


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
        "btn": "GENERATE SELECTED ASSETS",
        "upload_label": "Drop Property Photos Here",
        "result": "Executive Preview",
        "loading": "Crafting your premium marketing ecosystem...",
        "empty": "Upload property photos and fill in the details on the left to generate complete professional marketing assets.",
        "download": "Export Section (TXT)",
        "save_btn": "Save Changes",
        "saved_msg": "Saved!",
        "error": "Error:",
        "clear_btn": "Reset Form",
        "select_sections": "Select Assets to Generate",
        "tab_main": "Prime Listing",
        "tab_social": "Social Media Kit",
        "tab_video": "Video Scripts",
        "tab_tech": "Technical Specs",
        "tab_email": "Email Campaign",
        "tab_seo": "SEO & Web Copy",
        "tab_photo": "Photo Guide",
        "label_main": "Sales Copy",
        "label_social": "Social Media Content",
        "label_video": "Video Script",
        "label_tech": "Technical Specifications",
        "label_email": "Email Campaign",
        "label_seo": "SEO & Web Copy",
        "label_photo": "Photography Recommendations",
        "extra_details": "Extra Property Details",
        "interface_lang": "Interface Language",
        "logout": "Logout",
        "acc_settings": "Account Settings",
        "update_pw": "Update Password",
        "new_pw": "New Password",
        "btn_update": "Update Now",
        "danger_zone": "Danger Zone",
        "delete_confirm": "I want to permanently delete my account.",
        "btn_delete": "Delete Account",
        "pw_min_err": "Minimum 6 characters required."
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
        "ph_loc": "Örn: Beşiktaş, İstanbul veya Dubai Marina...",
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
        "audience_opts": ["Genel Pazar", "Lüks Alıcılar", "Yatırımcılar & ROI Odaklı", "Yabancılar & Uluslararası", "İlk Ev Alıcıları", "Tatil / Kiralık Pazar", "Ticari Kiracılar"],
        "custom_inst": "Özel Notlar ve Öne Çıkan Özellikler",
        "custom_inst_ph": "Örn: Özel havuz, panoramik manzara, akıllı ev sistemi, okula yakın...",
        "btn": "SEÇİLİ VARLIKLARI OLUŞTUR",
        "upload_label": "Fotoğrafları Buraya Bırakın",
        "result": "Yönetici Önizlemesi",
        "loading": "Premium pazarlama ekosisteminiz hazırlanıyor...",
        "empty": "Profesyonel analiz için görsel bekleniyor. Fotoğrafları yükleyin ve soldaki bilgileri doldurun.",
        "download": "Bölümü İndir (TXT)",
        "save_btn": "Kaydet",
        "saved_msg": "Kaydedildi!",
        "error": "Hata:",
        "clear_btn": "Formu Temizle",
        "select_sections": "Oluşturulacak Bölümleri Seçin",
        "tab_main": "Ana İlan",
        "tab_social": "Sosyal Medya Kiti",
        "tab_video": "Video Senaryoları",
        "tab_tech": "Teknik Özellikler",
        "tab_email": "E-posta Kampanyası",
        "tab_seo": "SEO & Web Metni",
        "tab_photo": "Fotoğraf Rehberi",
        "label_main": "Satış Metni",
        "label_social": "Sosyal Medya",
        "label_video": "Video Script",
        "label_tech": "Teknik Detaylar",
        "label_email": "E-posta Kampanyası",
        "label_seo": "SEO & Web Metni",
        "label_photo": "Fotoğraf Tavsiyeleri",
        "extra_details": "Ek Mülk Detayları",
        "interface_lang": "Arayüz Dili",
        "logout": "Çıkış Yap",
        "acc_settings": "Hesap Ayarları",
        "update_pw": "Şifre Güncelle",
        "new_pw": "Yeni Şifre",
        "btn_update": "Şifreyi Güncelle",
        "danger_zone": "Tehlikeli Bölge",
        "delete_confirm": "Hesabımı kalıcı olarak silmek istiyorum.",
        "btn_delete": "Hesabı Sil",
        "pw_min_err": "Şifre en az 6 karakter olmalıdır."
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
        "ph_loc": "Ej: Madrid, España o Marbella...",
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
        "btn": "GENERAR ACTIVOS SELECCIONADOS",
        "upload_label": "Subir Fotos de la Propiedad",
        "result": "Vista Previa Ejecutiva",
        "loading": "Creando su ecosistema de marketing premium...",
        "empty": "Esperando imágenes para análisis profesional. Suba fotos y complete los detalles a la izquierda.",
        "download": "Exportar Sección (TXT)",
        "save_btn": "Guardar Cambios",
        "saved_msg": "¡Guardado!",
        "error": "Error:",
        "clear_btn": "Limpiar Formulario",
        "select_sections": "Seleccionar Secciones a Generar",
        "tab_main": "Anuncio Premium",
        "tab_social": "Kit de Redes Sociales",
        "tab_video": "Guiones de Video",
        "tab_tech": "Especificaciones",
        "tab_email": "Campaña de Email",
        "tab_seo": "SEO & Web Copy",
        "tab_photo": "Guía de Fotos",
        "label_main": "Texto de Ventas",
        "label_social": "Contenido Social",
        "label_video": "Guion de Video",
        "label_tech": "Ficha Técnica",
        "label_email": "Campaña de Email",
        "label_seo": "SEO & Web Copy",
        "label_photo": "Recomendaciones de Fotografía",
        "extra_details": "Detalles Adicionales",
        "interface_lang": "Idioma de Interfaz",
        "logout": "Cerrar Sesión",
        "acc_settings": "Cuenta",
        "update_pw": "Actualizar Contraseña",
        "new_pw": "Nueva Contraseña",
        "btn_update": "Actualizar Ahora",
        "danger_zone": "Zona de Peligro",
        "delete_confirm": "Quiero eliminar mi cuenta permanentemente.",
        "btn_delete": "Eliminar Cuenta",
        "pw_min_err": "Mínimo 6 caracteres requeridos."
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
        "ph_loc": "Z.B. Berlin, Deutschland oder Hamburg...",
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
        "btn": "AUSGEWÄHLTE ASSETS ERSTELLEN",
        "upload_label": "Fotos hier hochladen",
        "result": "Executive-Vorschau",
        "loading": "Ihr Marketing-Ökosystem wird erstellt...",
        "empty": "Warte auf Bilder für die Analyse. Laden Sie Fotos hoch und füllen Sie die Details aus.",
        "download": "Abschnitt Exportieren (TXT)",
        "save_btn": "Speichern",
        "saved_msg": "Gespeichert!",
        "error": "Fehler:",
        "clear_btn": "Formular Zurücksetzen",
        "select_sections": "Zu erstellende Bereiche wählen",
        "tab_main": "Premium-Exposé",
        "tab_social": "Social Media Kit",
        "tab_video": "Videoskripte",
        "tab_tech": "Tech-Details",
        "tab_email": "E-Mail-Kampagne",
        "tab_seo": "SEO & Webtext",
        "tab_photo": "Foto-Guide",
        "label_main": "Verkaufstext",
        "label_social": "Social-Media-Content",
        "label_video": "Videoskript",
        "label_tech": "Technische Daten",
        "label_email": "E-Mail-Kampagne",
        "label_seo": "SEO & Webtext",
        "label_photo": "Fotografie-Empfehlungen",
        "extra_details": "Weitere Details",
        "interface_lang": "Oberfläche Sprache",
        "logout": "Abmelden",
        "acc_settings": "Kontoeinstellungen",
        "update_pw": "Passwort ändern",
        "new_pw": "Neues Passwort",
        "btn_update": "Jetzt aktualisieren",
        "danger_zone": "Gefahrenzone",
        "delete_confirm": "Ich möchte mein Konto dauerhaft löschen.",
        "btn_delete": "Konto löschen",
        "pw_min_err": "Mindestens 6 Zeichen erforderlich."
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
        "ph_loc": "Ex: Paris, Côte d'Azur ou Lyon...",
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
        "btn": "GÉNÉRER LES ACTIFS SÉLECTIONNÉS",
        "upload_label": "Déposer les Photos Ici",
        "result": "Aperçu Exécutif",
        "loading": "Préparation de votre écosystème marketing...",
        "empty": "En attente d' images pour analyse. Déposez des photos et remplissez les détails à gauche.",
        "download": "Exporter Section (TXT)",
        "save_btn": "Enregistrer",
        "saved_msg": "Enregistré !",
        "error": "Erreur :",
        "clear_btn": "Réinitialiser",
        "select_sections": "Sélectionner les sections à générer",
        "tab_main": "Annonce Premium",
        "tab_social": "Kit Réseaux Sociaux",
        "tab_video": "Scripts Vidéo",
        "tab_tech": "Spécifications",
        "tab_email": "Campagne Email",
        "tab_seo": "SEO & Web Copy",
        "tab_photo": "Guide Photo",
        "label_main": "Texte de Vente",
        "label_social": "Contenu Social",
        "label_video": "Script Vidéo",
        "label_tech": "Détails Techniques",
        "label_email": "Campagne Email",
        "label_seo": "SEO & Web Copy",
        "label_photo": "Recommandations Photographiques",
        "extra_details": "Détails Supplémentaires",
        "interface_lang": "Langue Interface",
        "logout": "Déconnexion",
        "acc_settings": "Paramètres",
        "update_pw": "Changer MDP",
        "new_pw": "Nouveau MDP",
        "btn_update": "Mettre à jour",
        "danger_zone": "Zone de Danger",
        "delete_confirm": "Supprimer définitivement mon compte.",
        "btn_delete": "Supprimer le compte",
        "pw_min_err": "6 caractères minimum."
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
        "ph_loc": "Ex: Lisboa, Algarve ou Porto...",
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
        "btn": "GERAR ATIVOS SELECIONADOS",
        "upload_label": "Enviar Fotos do Imóvel",
        "result": "Pré-visualização Executiva",
        "loading": "Preparando seu ecossistema de marketing...",
        "empty": "Aguardando imagens para análise. Envie fotos e preencha os detalhes à esquerda.",
        "download": "Exportar Secção (TXT)",
        "save_btn": "Salvar Alterações",
        "saved_msg": "Salvo!",
        "error": "Erro:",
        "clear_btn": "Limpar Formulário",
        "select_sections": "Selecionar Seções a Gerar",
        "tab_main": "Anúncio Premium",
        "tab_social": "Kit Redes Sociais",
        "tab_video": "Roteiros de Vídeo",
        "tab_tech": "Especificações",
        "tab_email": "Campanha de Email",
        "tab_seo": "SEO & Web Copy",
        "tab_photo": "Guia de Fotos",
        "label_main": "Texto de Vendas",
        "label_social": "Conteúdo Social",
        "label_video": "Roteiro de Vídeo",
        "label_tech": "Especificações Técnicas",
        "label_email": "Campanha Email",
        "label_seo": "SEO & Web Copy",
        "label_photo": "Recomendações de Fotografia",
        "extra_details": "Detalhes Adicionais",
        "interface_lang": "Idioma Interface",
        "logout": "Sair",
        "acc_settings": "Configurações",
        "update_pw": "Alterar Senha",
        "new_pw": "Nova Senha",
        "btn_update": "Atualizar Agora",
        "danger_zone": "Zona de Perigo",
        "delete_confirm": "Quero excluir minha conta permanentemente.",
        "btn_delete": "Excluir Conta",
        "pw_min_err": "Mínimo de 6 caracteres."
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
        "ph_loc": "例: 東京都港区、大阪、ドバイ...",
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
        "btn": "選択した資産を生成",
        "upload_label": "ここに物件写真をアップロード",
        "result": "エグゼクティブ・プレビュー",
        "loading": "プレミアム・マーケティング・エコシステムを構築中...",
        "empty": "分析用の画像を待機中。写真をアップロードし、左側に詳細を入力してください。",
        "download": "セクションを書き出し (TXT)",
        "save_btn": "変更を保存",
        "saved_msg": "保存完了！",
        "error": "エラー:",
        "clear_btn": "フォームをリセット",
        "select_sections": "生成するセクションを選択",
        "tab_main": "プレミアム広告",
        "tab_social": "SNSキット",
        "tab_video": "動画台本",
        "tab_tech": "技術仕様",
        "tab_email": "メールキャンペーン",
        "tab_seo": "SEO ＆ Webコピー",
        "tab_photo": "写真ガイド",
        "label_main": "セールスコピー",
        "label_social": "SNSコンテンツ",
        "label_video": "動画シナリオ",
        "label_tech": "技術詳細",
        "label_email": "メールキャンペーン",
        "label_seo": "SEOテキスト",
        "label_photo": "撮影のアドバイス",
        "extra_details": "物件詳細情報",
        "interface_lang": "インターフェース言語",
        "logout": "ログアウト",
        "acc_settings": "アカウント設定",
        "update_pw": "パスワード変更",
        "new_pw": "新しいパスワード",
        "btn_update": "今すぐ更新",
        "danger_zone": "危険区域",
        "delete_confirm": "アカウントを完全に削除します。",
        "btn_delete": "アカウント削除",
        "pw_min_err": "6文字以上必要です。"
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
        "ph_loc": "例如：上海浦东新区、北京或伦敦...",
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
        "btn": "生成所选资产",
        "upload_label": "在此上传房产照片",
        "result": "高级预览",
        "loading": "正在打造您的专属营销生态系统...",
        "empty": "等待照片进行专业分析。请上传照片并在左侧填写详细信息。",
        "download": "导出此部分 (TXT)",
        "save_btn": "保存更改",
        "saved_msg": "已保存！",
        "error": "错误：",
        "clear_btn": "重置表单",
        "select_sections": "选择要生成的章节",
        "tab_main": "优质房源",
        "tab_social": "社媒包",
        "tab_video": "视频脚本",
        "tab_tech": "技术规格",
        "tab_email": "邮件营销",
        "tab_seo": "SEO 网页文案",
        "tab_photo": "拍摄指南",
        "label_main": "销售文案",
        "label_social": "社媒内容",
        "label_video": "视频脚本",
        "label_tech": "技术规格",
        "label_email": "邮件营销",
        "label_seo": "SEO 文案",
        "label_photo": "摄影建议",
        "extra_details": "额外房产细节",
        "interface_lang": "界面语言",
        "logout": "退出登录",
        "acc_settings": "账户设置",
        "update_pw": "更改密码",
        "new_pw": "新密码",
        "btn_update": "立即更新",
        "danger_zone": "危险区域",
        "delete_confirm": "我确认要永久删除我的账户。",
        "btn_delete": "删除账户",
        "pw_min_err": "密码至少需要6位。"
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
        "btn": "إنشاء الأصول المختارة",
        "upload_label": "ضع صور العقار هنا",
        "result": "معاينة تنفيذية",
        "loading": "جاري تجهيز منظومتك التسويقية الفاخرة...",
        "empty": "في انتظار الصور لبدء التحليل المهني. ارفع الصور واملأ التفاصيل على اليسار.",
        "download": "تصدير القسم (TXT)",
        "save_btn": "حفظ التغييرات",
        "saved_msg": "تم الحفظ!",
        "error": "خطأ:",
        "clear_btn": "إعادة تعيين",
        "select_sections": "اختر الأقسام المراد إنشاؤها",
        "tab_main": "الإعلان الرئيسي",
        "tab_social": "حقيبة التواصل",
        "tab_video": "سيناريو الفيديو",
        "tab_tech": "المواصفات الفنية",
        "tab_email": "حملة البريد",
        "tab_seo": "نصوص الويب وSEO",
        "tab_photo": "دليل التصوير",
        "label_main": "نص المبيعات",
        "label_social": "محتوى التواصل",
        "label_video": "سيناريو الفيديو",
        "label_tech": "المواصفات الفنية",
        "label_email": "حملة البريد الإلكتروني",
        "label_seo": "نص SEO",
        "label_photo": "توصيات التصوير الفوتوغرافي",
        "extra_details": "تفاصيل العقار الإضافية",
        "interface_lang": "لغة الواجهة",
        "logout": "تسجيل الخروج",
        "acc_settings": "إعدادات الحساب",
        "update_pw": "تحديث كلمة السر",
        "new_pw": "كلمة سر جديدة",
        "btn_update": "تحديث الآن",
        "danger_zone": "منطقة خطر",
        "delete_confirm": "أريد حذف حسابي نهائياً.",
        "btn_delete": "حذف الحساب",
        "pw_min_err": "يجب أن تكون 6 خانات على الأقل."
    }
}


# ─── SESSION STATE ───────────────────────────────────────────────────────────
for key, val in [
    ("uretilen_ilan", ""), ("prop_type", ""), ("price", ""),
    ("location", ""), ("tone", ""), ("custom_inst", ""),
    ("target_lang_input", "English"), ("bedrooms", ""),
    ("bathrooms", ""), ("area_size", ""), ("year_built", ""),
    ("furnishing_idx", 0), ("audience_idx", 0), ("selected_sections", [])
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
button[kind="headerNoPadding"] {
    opacity: 1 !important;
    visibility: visible !important;
    display: block !important;
}
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
.stTabs [aria-selected="true"] {
    background-color: #0f172a !important; color: white !important;
    border-radius: 8px 8px 0 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    logo_img = load_logo("SarSa_Logo_Transparent.png")
    if logo_img:
        st.image(logo_img, use_container_width=True)
    else:
        st.markdown("<div style='text-align:center; padding:0.8rem 0 0.5rem;'><span style='font-size:1.8rem; font-weight:800; color:#0f172a;'>SarSa</span><span style='font-size:1.8rem; font-weight:800; background:linear-gradient(135deg,#3b82f6,#8b5cf6); -webkit-background-clip:text;-webkit-text-fill-color:transparent;'> AI</span></div>", unsafe_allow_html=True)

    # --- Üst Kısım: Dil Seçimi ve Çıkış ---
    current_ui_lang = st.selectbox("🌐 Interface Language", list(ui_languages.keys()), 
                                   index=list(ui_languages.keys()).index(st.session_state.auth_lang) if st.session_state.auth_lang in ui_languages else 0)
    t = ui_languages[current_ui_lang]
    st.session_state.auth_lang = current_ui_lang # Senkronizasyon
    
    if st.button(f"🚪 {t.get('logout', 'Logout')}", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.is_logged_in = False
        st.session_state.user_email = None
        st.rerun()

    st.markdown("---")
    
    # --- Yeni: Hesap Ayarları Paneli (Dinamik) ---
    with st.expander(f"⚙️ {t.get('acc_settings', 'Account Settings')}"):
        st.subheader(t.get('update_pw', 'Update Password'))
        new_pw = st.text_input(t.get('new_pw', 'New Password'), type="password", key="settings_new_pw")
        if st.button(t.get('btn_update', 'Update')):
            if len(new_pw) < 6:
                st.warning(t.get('pw_min_err', 'Min 6 chars'))
            else:
                try:
                    supabase.auth.update_user({"password": new_pw})
                    st.success(t.get('saved_msg', 'OK'))
                except Exception as e:
                    st.error(f"{e}")

        st.markdown("---")
        st.subheader(t.get('danger_zone', 'Danger Zone'))
        confirm_delete = st.checkbox(t.get('delete_confirm', 'Confirm'))
        if st.button(f"❌ {t.get('btn_delete', 'Delete')}", type="primary", use_container_width=True):
            if confirm_delete:
                try:
                    user_id = supabase.auth.get_user().user.id
                    # Not: Bu RPC fonksiyonunun veritabanında tanımlı olması gerekir
                    supabase.rpc('soft_delete_profile', {'p_id': user_id, 'p_actor': user_id}).execute()
                    supabase.auth.sign_out()
                    st.session_state.is_logged_in = False
                    st.rerun()
                except Exception as e:
                    st.error(f"{e}")

    st.markdown("---")
    st.header(t["settings"])

    st.session_state.target_lang_input = st.text_input(f"✍️ {t['target_lang']}", value=st.session_state.target_lang_input)
    st.session_state.prop_type = st.text_input(t["prop_type"], value=st.session_state.prop_type, placeholder=t["ph_prop"])
    st.session_state.price = st.text_input(t["price"], value=st.session_state.price, placeholder=t["ph_price"])
    st.session_state.location = st.text_input(t["location"], value=st.session_state.location, placeholder=t["ph_loc"])

    current_tone_idx = t["tones"].index(st.session_state.tone) if st.session_state.tone in t["tones"] else 0
    st.session_state.tone = st.selectbox(t["tone"], t["tones"], index=current_tone_idx)
    st.session_state.custom_inst = st.text_area(f"📝 {t['custom_inst']}", value=st.session_state.custom_inst, placeholder=t["custom_inst_ph"], height=100)

    st.markdown(f"<div style='font-size:0.68rem; font-weight:800; color:#94a3b8; text-transform:uppercase; letter-spacing:1.4px; padding:0.6rem 0 0.3rem 0; border-bottom:1px solid #f1f5f9; margin-bottom:0.4rem;'>🛠️ {t['select_sections']}</div>", unsafe_allow_html=True)
    
    available_sections = {
        "1": t["tab_main"], "2": t["tab_social"], "3": t["tab_video"], 
        "4": t["tab_tech"], "5": t["tab_email"], "6": t["tab_seo"], "7": t["tab_photo"]
    }
    
    st.session_state.selected_sections = st.multiselect(
        "", options=list(available_sections.keys()), 
        format_func=lambda x: available_sections[x],
        default=st.session_state.selected_sections if st.session_state.selected_sections else list(available_sections.keys())
    )

    st.markdown(f"<div style='font-size:0.68rem; font-weight:800; color:#94a3b8; text-transform:uppercase; letter-spacing:1.4px; padding:0.6rem 0 0.3rem 0; border-bottom:1px solid #f1f5f9; margin-bottom:0.4rem;'>🔑 {t['extra_details']}</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1: st.session_state.bedrooms = st.text_input(t["bedrooms"], value=st.session_state.bedrooms, placeholder=t["ph_beds"])
    with col2: st.session_state.bathrooms = st.text_input(t["bathrooms"], value=st.session_state.bathrooms, placeholder=t["ph_baths"])
    col3, col4 = st.columns(2)
    with col3: st.session_state.area_size = st.text_input(t["area"], value=st.session_state.area_size, placeholder=t["ph_area"])
    with col4: st.session_state.year_built = st.text_input(t["year_built"], value=st.session_state.year_built, placeholder=t["ph_year"])

    st.session_state.furnishing_idx = t["furnishing_opts"].index(st.selectbox(t["furnishing"], t["furnishing_opts"], index=st.session_state.furnishing_idx if st.session_state.furnishing_idx < len(t["furnishing_opts"]) else 0))
    st.session_state.audience_idx = t["audience_opts"].index(st.selectbox(t["target_audience"], t["audience_opts"], index=st.session_state.audience_idx if st.session_state.audience_idx < len(t["audience_opts"]) else 0))

    if st.button(f"🗑️ {t['clear_btn']}", use_container_width=True):
        for k in ["uretilen_ilan", "prop_type", "price", "location", "bedrooms", "bathrooms", "area_size", "year_built", "custom_inst"]: st.session_state[k] = ""
        st.session_state.selected_sections = []
        st.rerun()


# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
st.markdown(f"<h1>🏢 {t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#0f172a; font-weight:700; font-size:1.35rem;'>{t['service_desc']}</p>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(f"📸 {t['upload_label']}", type=["jpg", "png", "webp", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    images_for_ai = [Image.open(f) for f in uploaded_files]
    cols = st.columns(min(len(images_for_ai), 4))
    for i, img in enumerate(images_for_ai):
        with cols[i % 4]: st.image(img, use_container_width=True)

    if st.button(f"🚀 {t['btn']}"):
        with st.spinner(t["loading"]):
            p_furn = t["furnishing_opts"][st.session_state.furnishing_idx]
            p_aud = t["audience_opts"][st.session_state.audience_idx]
            details = f"Type: {st.session_state.prop_type}, Loc: {st.session_state.location}, Price: {st.session_state.price}, Beds: {st.session_state.bedrooms}, Baths: {st.session_state.bathrooms}, Area: {st.session_state.area_size}, Year: {st.session_state.year_built}, Furn: {p_furn}, Audience: {p_aud}, Tone: {st.session_state.tone}, Notes: {st.session_state.custom_inst}"
            
            section_prompts = {
                "1": "## SECTION_1\n[Write the full PRIME LISTING here - minimum 600 words]",
                "2": "## SECTION_2\n[Write the complete SOCIAL MEDIA KIT here - Posts for IG, FB, LinkedIn, TikTok]",
                "3": "## SECTION_3\n[Write the full CINEMATIC VIDEO SCRIPT here]",
                "4": "## SECTION_4\n[Write the full TECHNICAL SPECIFICATIONS here]",
                "5": "## SECTION_5\n[Write the full EMAIL CAMPAIGN here - 3 complete email templates]",
                "6": "## SECTION_6\n[Write the full SEO & WEB COPY here - Metadata, keywords, Ads copy]",
                "7": "## SECTION_7\n[Write the full PHOTOGRAPHY RECOMMENDATIONS here]"
            }
            
            active_prompts = "\n\n".join([section_prompts[s] for s in st.session_state.selected_sections])

            prompt = f"""You are a world-class AI Real Estate Copywriter. Write ALL content in {st.session_state.target_lang_input}.
            PROPERTY DETAILS: {details}

            Analyze the photos and write extensive content ONLY for the following sections as requested:

            {active_prompts}"""
            
            try:
                response = model.generate_content([prompt] + images_for_ai)
                st.session_state.uretilen_ilan = response.text
            except Exception as e:
                st.error(f"{t['error']} {e}")

    if st.session_state.uretilen_ilan:
        raw = st.session_state.uretilen_ilan
        sec = {str(i): "" for i in range(1, 8)}
        
        for p in raw.split("##"):
            p = p.strip()
            for n in ["1", "2", "3", "4", "5", "6", "7"]:
                if p.upper().startswith(f"SECTION_{n}"):
                    content = p[len(f"SECTION_{n}"):].strip()
                    if content.startswith("—") or content.startswith("-") or content.startswith(":"):
                        content = content.lstrip("—-–: \n").strip()
                    sec[n] = content
                    break

        active_tabs_indices = [int(i)-1 for i in st.session_state.selected_sections if sec[i]]
        if active_tabs_indices:
            tab_labels = [f"📝 {t['tab_main']}", f"📱 {t['tab_social']}", f"🎬 {t['tab_video']}", f"⚙️ {t['tab_tech']}", f"✉️ {t['tab_email']}", f"🔍 {t['tab_seo']}", f"📸 {t['tab_photo']}"]
            ui_labels = [t["label_main"], t["label_social"], t["label_video"], t["label_tech"], t["label_email"], t["label_seo"], t["label_photo"]]
            
            tabs = st.tabs([tab_labels[i] for i in active_tabs_indices])
            ts = datetime.now().strftime("%Y%m%d_%H%M")
            
            for i, tab_idx in enumerate(active_tabs_indices):
                with tabs[i]:
                    idx = str(tab_idx + 1)
                    edited = st.text_area(ui_labels[tab_idx], value=sec[idx], height=450, key=f"txt_{idx}")
                    c1, c2 = st.columns(2)
                    with c1: 
                        if st.button(f"💾 {t['save_btn']}", key=f"save_{idx}"): st.success(t['saved_msg'])
                    with c2: 
                        st.download_button(f"📥 {t['download']}", edited, file_name=f"sarsa_{idx}_{ts}.txt", key=f"dl_{idx}")
else:
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
            <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">✉️ {t['tab_email']}</span>
            <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">🔍 {t['tab_seo']}</span>
            <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">📸 {t.get('tab_photo', 'Photo Guide')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
