import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
from datetime import datetime
from supabase import create_client, Client

# ─── PAGE CONFIG (En üstte olmalı) ──────────────────────────────────────────
st.set_page_config(page_title="SarSa AI | Real Estate Intelligence", page_icon="🏢", layout="wide")

# ─── SUPABASE CONFIGURATION ────────────────────────────────────────────────
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ─── SESSION STATE INITIALIZATION ──────────────────────────────────────────
if 'auth_lang' not in st.session_state: st.session_state.auth_lang = "English"
if 'is_logged_in' not in st.session_state: st.session_state.is_logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'recovery_mode' not in st.session_state: st.session_state.recovery_mode = False

for key, val in [ 
    ("uretilen_ilan", ""), ("prop_type", ""), ("price", ""), 
    ("location", ""), ("tone", ""), ("custom_inst", ""), 
    ("target_lang_input", "English"), ("bedrooms", ""), 
    ("bathrooms", ""), ("area_size", ""), ("year_built", ""), 
    ("furnishing_idx", 0), ("audience_idx", 0), ("selected_sections", []) 
]: 
    if key not in st.session_state:
        st.session_state[key] = val

# ─── TEXT DICTIONARIES (9 LANGUAGES) ───────────────────────────────────────
auth_texts = {
    "English": { "login": "Login", "register": "Register", "email": "Email", "password": "Password", "btn_login": "Login", "btn_reg": "Create Account", "success_reg": "Registration successful! Check your email to verify your account.", "error_login": "Login failed. You are not registered, or your Email/Password is incorrect.", "welcome_title": "Welcome to SarSa AI", "welcome_desc": "The All-in-One Visual Property Intelligence & Global Sales Automation platform. Transform your property photos into professional assets in seconds.", "forgot_pw": "Forgot Password?", "btn_reset": "Send Reset Link", "reset_success": "Reset link sent to your email." },
    "Türkçe": { "login": "Giriş Yap", "register": "Kayıt Ol", "email": "E-posta", "password": "Şifre", "btn_login": "Oturum Aç", "btn_reg": "Hesap Oluştur", "success_reg": "Kayıt başarılı! Hesabınızı onaylamak için e-postanızı kontrol edin.", "error_login": "Giriş başarısız. Kayıtlı değilsiniz veya E-posta/Şifreniz hatalı.", "welcome_title": "SarSa AI'a Hoş Geldiniz", "welcome_desc": "Hepsi Bir Arada Görsel Mülk Zekâsı ve Küresel Satış Otomasyonu platformu. Mülk fotoğraflarınızı saniyeler içinde profesyonel varlıklara dönüştürün.", "forgot_pw": "Şifremi Unuttum?", "btn_reset": "Sıfırlama Bağlantısı Gönder", "reset_success": "Sıfırlama bağlantısı e-postanıza gönderildi." },
    "Español": { "login": "Iniciar Sesión", "register": "Registrarse", "email": "Correo", "password": "Clave", "btn_login": "Entrar", "btn_reg": "Crear Cuenta", "success_reg": "¡Registro exitoso! Revisa tu email para verificar tu cuenta.", "error_login": "Error. No estás registrado o tu Correo/Clave es incorrecto.", "welcome_title": "Bienvenido a SarSa AI", "welcome_desc": "La plataforma todo en uno de Inteligencia Visual de Propiedades y Automatización de Ventas.", "forgot_pw": "¿Olvidaste tu contraseña?", "btn_reset": "Enviar enlace", "reset_success": "Enlace de restablecimiento enviado." },
    "Deutsch": { "login": "Anmelden", "register": "Registrieren", "email": "E-Mail", "password": "Passwort", "btn_login": "Login", "btn_reg": "Konto Erstellen", "success_reg": "Erfolgreich! Bitte bestätigen Sie Ihre E-Mail.", "error_login": "Login fehlgeschlagen. Nicht registriert oder E-Mail/Passwort falsch.", "welcome_title": "Willkommen bei SarSa AI", "welcome_desc": "Die All-in-One-Plattform für visuelle Immobilienintelligenz.", "forgot_pw": "Passwort vergessen?", "btn_reset": "Link senden", "reset_success": "Link an E-Mail gesendet." },
    "Français": { "login": "Connexion", "register": "S'inscrire", "email": "Email", "password": "Mot de passe", "btn_login": "Se connecter", "btn_reg": "Créer un compte", "success_reg": "Succès ! Vérifiez vos emails pour confirmer.", "error_login": "Échec. Vous n'êtes pas inscrit ou Email/Mot de passe incorrect.", "welcome_title": "Bienvenue sur SarSa AI", "welcome_desc": "La plateforme d'Intelligence Visuelle Immobilière et d'Automatisation des Ventes.", "forgot_pw": "Mot de passe oublié ?", "btn_reset": "Envoyer le lien", "reset_success": "Lien envoyé par e-mail." },
    "Português": { "login": "Entrar", "register": "Registar", "email": "Email", "password": "Senha", "btn_login": "Login", "btn_reg": "Criar Conta", "success_reg": "Sucesso! Verifique seu email para confirmar a conta.", "error_login": "Falha. Não registado ou Email/Senha incorretos.", "welcome_title": "Bem-vindo ao SarSa AI", "welcome_desc": "A plataforma tudo-em-um de Inteligência Imobiliária Visual e Automação de Vendas.", "forgot_pw": "Esqueceu a senha?", "btn_reset": "Enviar link", "reset_success": "Link enviado para seu e-mail." },
    "日本語": { "login": "ログイン", "register": "新規登録", "email": "メール", "password": "パスワード", "btn_login": "ログイン", "btn_reg": "アカウント作成", "success_reg": "登録完了！メールを確認してアカウントを認証してください。", "error_login": "ログイン失敗。未登録か、メール/パスワードが間違っています。", "welcome_title": "SarSa AI へようこそ", "welcome_desc": "オールインワンの視覚的物件インテリジェンス＆販売自動化プラットフォーム。", "forgot_pw": "パスワードをお忘れですか？", "btn_reset": "リンクを送信", "reset_success": "リセットリンクが送信されました。" },
    "简体中文": { "login": "登录", "register": "注册", "email": "邮箱", "password": "密码", "btn_login": "登录", "btn_reg": "创建账号", "success_reg": "注册成功！请检查邮箱以验证账号。", "error_login": "登录失败。您未注册，或邮箱/密码错误。", "welcome_title": "欢迎来到 SarSa AI", "welcome_desc": "全方位房产视觉智能与全球销售自动化平台。", "forgot_pw": "忘记密码？", "btn_reset": "发送重置链接", "reset_success": "重置链接已发送到您的邮箱。" },
    "العربية": { "login": "تسجيل الدخول", "register": "إنشاء حساب", "email": "البريد", "password": "كلمة السر", "btn_login": "دخول", "btn_reg": "إنشاء حساب", "success_reg": "تم التسجيل بنجاح! تحقق من بريدك لتأكيد الحساب.", "error_login": "فشل الدخول. أنت غير مسجل، أو البريد/كلمة السر خاطئة.", "welcome_title": "مرحباً بك في SarSa AI", "welcome_desc": "منصة الذكاء البصري المتكامل للعقارات وأتمتة المبيعات العالمية.", "forgot_pw": "نسيت كلمة السر؟", "btn_reset": "إرسال رابط الاستعادة", "reset_success": "تم إرسال رابط إعادة التعيين." }
}

ui_languages = {
    "English": { "title": "SarSa AI | Real Estate Intelligence Platform", "service_desc": "All-in-One Visual Property Intelligence & Global Sales Automation", "settings": "Configuration", "target_lang": "Write Listing In...", "prop_type": "Property Type", "price": "Market Price", "location": "Location", "tone": "Marketing Strategy", "tones": ["Standard Pro", "Ultra-Luxury", "Investment Focus", "Modern Minimalist", "Family Living", "Vacation Rental", "Commercial"], "ph_prop": "E.g., 3+1 Apartment, Luxury Villa...", "ph_price": "E.g., $850,000 or £2,000/mo...", "ph_loc": "E.g., Manhattan, NY or Dubai Marina...", "custom_inst": "Special Notes & Highlights", "custom_inst_ph": "E.g., Private pool, panoramic sea view, smart home...", "upload_label": "Drop Property Photos Here", "result": "Executive Preview", "empty": "Upload property photos and fill in the details on the left to generate complete professional marketing assets.", "acc_settings": "Account Settings", "update_pw": "Update Password", "new_pw": "New Password", "btn_update": "Update Now", "danger_zone": "Danger Zone", "delete_confirm": "I want to permanently delete my account.", "btn_delete": "Delete Account", "pw_min_err": "Minimum 6 characters required.", "logout": "Logout", "saved_msg": "Saved!", "error": "Error:" },
    "Türkçe": { "title": "SarSa AI | Gayrimenkul Zekâ Platformu", "service_desc": "Hepsi Bir Arada Görsel Mülk Zekâsı ve Küresel Satış Otomasyonu", "settings": "Yapılandırma", "target_lang": "İlan Yazım Dili...", "prop_type": "Emlak Tipi", "price": "Pazar Fiyatı", "location": "Konum", "tone": "Pazarlama Stratejisi", "tones": ["Standart Profesyonel", "Ultra-Lüks", "Yatırım Odaklı", "Modern Minimalist", "Aile Yaşamı", "Tatil Kiralık", "Ticari"], "ph_prop": "Örn: 3+1 Daire, Müstakil Villa...", "ph_price": "Örn: 5.000.000 TL veya $2.500/ay...", "ph_loc": "Örn: Beşiktaş, İstanbul veya Dubai Marina...", "custom_inst": "Özel Notlar ve Öne Çıkan Özellikler", "custom_inst_ph": "Örn: Özel havuz, panoramik manzara, akıllı ev sistemi...", "upload_label": "Fotoğrafları Buraya Bırakın", "result": "Yönetici Önizlemesi", "empty": "Profesyonel analiz için görsel bekleniyor. Fotoğrafları yükleyin ve soldaki bilgileri doldurun.", "acc_settings": "Hesap Ayarları", "update_pw": "Şifre Güncelle", "new_pw": "Yeni Şifre", "btn_update": "Şifreyi Güncelle", "danger_zone": "Tehlikeli Bölge", "delete_confirm": "Hesabımı kalıcı olarak silmek istiyorum.", "btn_delete": "Hesabı Sil", "pw_min_err": "Şifre en az 6 karakter olmalıdır.", "logout": "Çıkış Yap", "saved_msg": "Kaydedildi!", "error": "Hata:" },
    "Español": { "title": "SarSa AI | Plataforma de Inteligencia Inmobiliaria", "service_desc": "Inteligencia Visual de Propiedades y Automatización de Ventas Globales", "settings": "Configuración", "target_lang": "Escribir en...", "prop_type": "Tipo de Propiedad", "price": "Precio de Mercado", "location": "Ubicación", "tone": "Estrategia de Marketing", "tones": ["Profesional Estándar", "Ultra-Lujo", "Enfoque de Inversión", "Minimalista Moderno", "Vida Familiar", "Alquiler Vacacional", "Comercial"], "ph_prop": "Ej: Apartamento 3+1, Villa de Lujo...", "ph_price": "Ej: $850.000 o EUR 1.500/mes...", "ph_loc": "Ej: Madrid, España...", "custom_inst": "Notas Especiales y Características", "custom_inst_ph": "Ej: Piscina privada, vistas al mar, domótica...", "upload_label": "Subir Fotos de la Propiedad", "result": "Vista Previa Ejecutiva", "empty": "Esperando imágenes para análisis profesional. Suba fotos y complete los detalles a la izquierda.", "acc_settings": "Cuenta", "update_pw": "Actualizar Contraseña", "new_pw": "Nueva Contraseña", "btn_update": "Actualizar Ahora", "danger_zone": "Zona de Peligro", "delete_confirm": "Quiero eliminar mi cuenta permanentemente.", "btn_delete": "Eliminar Cuenta", "pw_min_err": "Mínimo 6 caracteres requeridos.", "logout": "Cerrar Sesión", "saved_msg": "¡Guardado!", "error": "Error:" },
    "Deutsch": { "title": "SarSa AI | Immobilien-Intelligenz-Plattform", "service_desc": "All-in-One Visuelle Objektintelligenz & Globale Verkaufsautomatisierung", "settings": "Konfiguration", "target_lang": "Erstellen in...", "prop_type": "Objekttyp", "price": "Marktpreis", "location": "Standort", "tone": "Marketingstrategie", "tones": ["Standard-Profi", "Ultra-Luxus", "Investitionsfokus", "Modern-Minimalistisch", "Familienleben", "Ferienmiete", "Gewerbe"], "ph_prop": "Z.B. 3-Zimmer-Wohnung, Luxusvilla...", "ph_price": "Z.B. 850.000€ oder 2.000€/Monat...", "ph_loc": "Z.B. Berlin, Deutschland...", "custom_inst": "Notizen & Besonderheiten", "custom_inst_ph": "Z.B. Privatpool, Panoramasicht, Smart-Home...", "upload_label": "Fotos hier hochladen", "result": "Executive-Vorschau", "empty": "Warte auf Bilder für die Analyse. Laden Sie Fotos hoch und füllen Sie die Details aus.", "acc_settings": "Kontoeinstellungen", "update_pw": "Passwort ändern", "new_pw": "Neues Passwort", "btn_update": "Jetzt aktualisieren", "danger_zone": "Gefahrenzone", "delete_confirm": "Ich möchte mein Konto dauerhaft löschen.", "btn_delete": "Konto löschen", "pw_min_err": "Mindestens 6 Zeichen erforderlich.", "logout": "Abmelden", "saved_msg": "Gespeichert!", "error": "Fehler:" },
    "Français": { "title": "SarSa AI | Plateforme d'Intelligence Immobilière", "service_desc": "Intelligence Visuelle Immobilière et Automatisation des Ventes Globales", "settings": "Configuration", "target_lang": "Rédiger en...", "prop_type": "Type de Bien", "price": "Prix du Marché", "location": "Localisation", "tone": "Stratégie Marketing", "tones": ["Standard Pro", "Ultra-Luxe", "Focus Investissement", "Minimaliste Moderne", "Vie de Famille", "Location Saisonnière", "Commercial"], "ph_prop": "Ex: Appartement T4, Villa de Luxe...", "ph_price": "Ex: 850.000€ ou 1.500€/mois...", "ph_loc": "Ex: Paris, Côte d'Azur...", "custom_inst": "Notes Spéciales & Points Forts", "custom_inst_ph": "Ex: Piscine privée, vue panoramique, domotique...", "upload_label": "Déposer les Photos Ici", "result": "Aperçu Exécutif", "empty": "En attente d'images pour analyse. Déposez des photos et remplissez les détails à gauche.", "acc_settings": "Paramètres", "update_pw": "Changer MDP", "new_pw": "Nouveau MDP", "btn_update": "Mettre à jour", "danger_zone": "Zone de Danger", "delete_confirm": "Supprimer définitivement mon compte.", "btn_delete": "Supprimer le compte", "pw_min_err": "6 caractères minimum.", "logout": "Déconnexion", "saved_msg": "Enregistré !", "error": "Erreur :" },
    "Português": { "title": "SarSa AI | Plataforma de Inteligência Imobiliária", "service_desc": "Inteligência Visual Imobiliária e Automação de Vendas Globais", "settings": "Configuração", "target_lang": "Escrever em...", "prop_type": "Tipo de Imóvel", "price": "Preço de Mercado", "location": "Localização", "tone": "Estratégia de Marketing", "tones": ["Profissional Padrão", "Ultra-Luxo", "Foco em Investimento", "Minimalista Moderno", "Vida Familiar", "Aluguel de Temporada", "Comercial"], "ph_prop": "Ex: Apartamento T3, Moradia de Luxo...", "ph_price": "Ex: 500.000€ ou 1.500€/mês...", "ph_loc": "Ex: Lisboa, Algarve...", "custom_inst": "Notas Especiais e Destaques", "custom_inst_ph": "Ex: Piscina privativa, vista panorâmica, casa inteligente...", "upload_label": "Enviar Fotos do Imóvel", "result": "Pré-visualização Executiva", "empty": "Aguardando imagens para análise. Envie fotos e preencha os detalhes à esquerda.", "acc_settings": "Configurações", "update_pw": "Alterar Senha", "new_pw": "Nova Senha", "btn_update": "Atualizar Agora", "danger_zone": "Zona de Perigo", "delete_confirm": "Quero excluir minha conta permanentemente.", "btn_delete": "Excluir Conta", "pw_min_err": "Mínimo de 6 caracteres.", "logout": "Sair", "saved_msg": "Salvo!", "error": "Erro:" },
    "日本語": { "title": "SarSa AI | 不動産インテリジェンス・プラットフォーム", "service_desc": "オールインワン視覚的物件インテリジェンス＆グローバル販売自動化", "settings": "設定", "target_lang": "作成言語...", "prop_type": "物件種別", "price": "市場価格", "location": "所在地", "tone": "マーケティング戦略", "tones": ["標準プロ", "ウルトラ・ラグジュアリー", "投資重視", "モダン・ミニマリスト", "ファミリー向け", "バケーションレンタル", "商業用"], "ph_prop": "例: 3LDKマンション、高級別荘...", "ph_price": "例: 8500万円 または 月20万円...", "ph_loc": "例: 東京都港区、大阪...", "custom_inst": "特記事項 ＆ アピールポイント", "custom_inst_ph": "例: プライベートプール、パノラマビュー、スマートホーム...", "upload_label": "ここに物件写真をアップロード", "result": "エグゼクティブ・プレビュー", "empty": "分析用の画像を待機中。写真をアップロードし、左側に詳細を入力してください。", "acc_settings": "アカウント設定", "update_pw": "パスワード変更", "new_pw": "新しいパスワード", "btn_update": "今すぐ更新", "danger_zone": "危険区域", "delete_confirm": "アカウントを完全に削除します。", "btn_delete": "アカウント削除", "pw_min_err": "6文字以上必要です。", "logout": "ログアウト", "saved_msg": "保存完了！", "error": "エラー:" },
    "简体中文": { "title": "SarSa AI | 房地产智能平台", "service_desc": "全方位房产视觉智能与全球销售自动化", "settings": "配置", "target_lang": "编写语言...", "prop_type": "房产类型", "price": "市场价格", "location": "地点", "tone": "营销策略", "tones": ["标准专业", "顶级豪宅", "投资价值", "现代简约", "家庭生活", "度假租赁", "商业办公"], "ph_prop": "例如：3室1厅公寓、豪华别墅...", "ph_price": "例如：$850,000 或 $2,000/月...", "ph_loc": "例如：上海浦东新区、北京...", "custom_inst": "特别备注与亮点", "custom_inst_ph": "例如：私人泳池、全景海景、智能家居...", "upload_label": "在此上传房产照片", "result": "高级预览", "empty": "等待照片进行专业分析。请上传照片并在左侧填写详细信息。", "acc_settings": "账户设置", "update_pw": "更改密码", "new_pw": "新密码", "btn_update": "立即更新", "danger_zone": "危险区域", "delete_confirm": "我确认要永久删除我的账户。", "btn_delete": "删除账户", "pw_min_err": "密码至少需要6位。", "logout": "退出登录", "saved_msg": "已保存！", "error": "错误：" },
    "العربية": { "title": "SarSa AI | منصة الذكاء العقاري", "service_desc": "الذكاء البصري المتكامل للعقارات وأتمتة المبيعات العالمية", "settings": "الإعدادات", "target_lang": "لغة الكتابة...", "prop_type": "نوع العقار", "price": "سعر السوق", "location": "الموقع", "tone": "استراتيجية التسويق", "tones": ["احترافي قياسي", "فخامة فائقة", "تركيز استثماري", "عصري بسيط", "حياة عائلية", "تأجير سياحي", "تجاري"], "ph_prop": "مثال: شقة 3+1، فيلا فاخرة...", "ph_price": "مثال: 850,000$ أو 2,500$ شهرياً...", "ph_loc": "مثال: دبي مارينا، الرياض...", "custom_inst": "ملاحظات خاصة ومميزات", "custom_inst_ph": "مثال: مسبح خاص، إطلالة بانورامية، منزل ذكي...", "upload_label": "ضع صور العقار هنا", "result": "معاينة تنفيذية", "empty": "في انتظار الصور لبدء التحليل المهني. ارفع الصور واملأ التفاصيل على اليسار.", "acc_settings": "إعدادات الحساب", "update_pw": "تحديث كلمة السر", "new_pw": "كلمة سر جديدة", "btn_update": "تحديث الآن", "danger_zone": "منطقة خطر", "delete_confirm": "أريد حذف حسابي نهائياً.", "btn_delete": "حذف الحساب", "pw_min_err": "يجب أن تكون 6 خانات على الأقل.", "logout": "تسجيل الخروج", "saved_msg": "تم الحفظ!", "error": "خطأ:" }
}

# ─── URL QUERY PARAMS YAKALAYICI (ŞİFRE SIFIRLAMA & PKCE İÇİN EN ÜSTTE) ─────
query_params = st.query_params

# Supabase PKCE akışı için URL'de gelen 'code' token değişimini yapar
if "code" in query_params:
    try:
        supabase.auth.exchange_code_for_session({"auth_code": query_params["code"]})
        st.session_state.is_logged_in = True
        st.session_state.recovery_mode = True
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Token error: {e}")

# Eski tip hash yerine query_params üzerinden recovery kontrolü
if "type" in query_params and query_params["type"] == "recovery":
    st.session_state.recovery_mode = True
    st.query_params.clear()
    st.rerun()

if st.session_state.recovery_mode:
    st.warning("🔒 Reset Your Password")
    with st.form("recovery_form"):
        new_password_recovery = st.text_input("New Password", type="password", help="Minimum 6 characters")
        if st.form_submit_button("Set New Password & Login"):
            if len(new_password_recovery) < 6:
                st.error("❌ Password must be at least 6 characters!")
            else:
                try:
                    supabase.auth.update_user({"password": new_password_recovery})
                    st.success("✅ Password updated! You are being redirected...")
                    st.session_state.recovery_mode = False
                    st.session_state.is_logged_in = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    st.stop() # Şifre sıfırlanana kadar arka planı durdur

# ─── AUTH FUNCTIONS ────────────────────────────────────────────────────────
def get_status(): 
    if st.session_state.get('is_logged_in'): 
        return "paid", st.session_state.user_email
    return "logged_out", None

# ─── UI FLOW ───────────────────────────────────────────────────────────────
def update_lang(): 
    st.session_state.auth_lang = st.session_state.lang_selector

auth_status, user_email = get_status()

# ─── CSS STYLING (ESKİ KODDAN KORUNAN MUHTEŞEM TASARIM) ─────────────────────
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

@st.cache_data 
def load_logo(file_path): 
    if os.path.exists(file_path): return Image.open(file_path) 
    return None

# ─── GİRİŞ VE KAYIT EKRANLARI (GÜVENLİ YENİ YAPI) ──────────────────────────
if auth_status != "paid": 
    st.selectbox("🌐 Select Language / Dil Seçin", list(auth_texts.keys()), index=list(auth_texts.keys()).index(st.session_state.auth_lang) if st.session_state.auth_lang in auth_texts else 0, key="lang_selector", on_change=update_lang)
    at = auth_texts.get(st.session_state.auth_lang, auth_texts["English"])
    
    col_logo, col_text = st.columns([1, 6])
    with col_logo:
        logo_login = load_logo("SarSa_Logo_Transparent.png")
        if logo_login: st.image(logo_login, use_container_width=True)
    with col_text:
        st.markdown(f"<h1 style='text-align:left; color:#0f172a; font-weight:800; margin-top:0; padding-top:0;'>{at['welcome_title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.15rem; color:#475569; font-weight:500; margin-bottom:2rem;'>{at['welcome_desc']}</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([f"🔑 {at['login']}", f"📝 {at['register']}", f"❓ {at['forgot_pw']}"])
    
    with tab1:
        with st.form("login_form"):
            email_log = st.text_input(at["email"])
            pw_log = st.text_input(at["password"], type="password")
            if st.form_submit_button(at["btn_login"]):
                try:
                    response = supabase.auth.sign_in_with_password({"email": email_log, "password": pw_log})
                    st.session_state.is_logged_in = True
                    st.session_state.user_email = response.user.email
                    st.rerun()
                except Exception as e:
                    st.error(at["error_login"])
                    
    with tab2:
        with st.form("register_form"):
            email_reg = st.text_input(at["email"])
            pw_reg = st.text_input(at["password"] + " (Min 6)", type="password")
            if st.form_submit_button(at["btn_reg"]):
                try:
                    # Yönlendirme URL'si dahil edildi!
                    supabase.auth.sign_up({
                        "email": email_reg, 
                        "password": pw_reg,
                        "options": {"email_redirect_to": "https://sarsa-ai-estateintelligence.streamlit.app/"}
                    })
                    st.success(f"✅ {at['success_reg']}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab3:
        with st.form("forgot_pw_form"):
            email_reset = st.text_input(at["email"])
            if st.form_submit_button(at["btn_reset"]):
                try:
                    supabase.auth.reset_password_for_email(email_reset)
                    st.success(at["reset_success"])
                except Exception as e:
                    st.error(f"Error: {e}")
    st.stop()

# ─── AI CONFIGURATION ───────────────────────────────────────────────────────
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY) 
MODEL_NAME = 'gemini-2.5-flash' 
model = genai.GenerativeModel(MODEL_NAME)


# ─── SIDEBAR & ACCOUNT SETTINGS (ESKİ KODDAKİ TÜM GİRİŞ ALANLARI DAHİL) ─────
with st.sidebar: 
    logo_img = load_logo("SarSa_Logo_Transparent.png") 
    if logo_img:
        st.image(logo_img, use_container_width=True) 
    else: 
        st.markdown("<div style='text-align:center; padding:0.8rem 0 0.5rem;'><span style='font-size:1.8rem; font-weight:800; color:#0f172a;'>SarSa</span><span style='font-size:1.8rem; font-weight:800; background:linear-gradient(135deg,#3b82f6,#8b5cf6); -webkit-background-clip:text;-webkit-text-fill-color:transparent;'> AI</span></div>", unsafe_allow_html=True)
    
    st.divider()
    t = ui_languages.get(st.session_state.auth_lang, ui_languages["English"])
    
    # Hesap Ayarları Paneli
    with st.expander(f"⚙️ {t['acc_settings']}"):
        st.write(st.session_state.user_email)
        
        st.subheader(t["update_pw"])
        new_pw = st.text_input(t["new_pw"], type="password", key="settings_new_pw")
        if st.button(t["btn_update"], key="settings_update_btn"):
            if len(new_pw) < 6:
                st.error(t["pw_min_err"])
            else:
                try:
                    supabase.auth.update_user({"password": new_pw})
                    st.success(t["saved_msg"])
                except Exception as e:
                    st.error(f"{t['error']} {e}")
        
        st.divider()
        st.subheader(t["danger_zone"])
        confirm_del = st.checkbox(t["delete_confirm"])
        if st.button(f"❌ {t['btn_delete']}", type="primary", use_container_width=True):
            if confirm_del:
                try:
                    user_resp = supabase.auth.get_user()
                    if user_resp and user_resp.user:
                        supabase.rpc('soft_delete_profile', {'p_id': user_resp.user.id, 'p_actor': user_resp.user.id}).execute()
                    supabase.auth.sign_out()
                    st.session_state.is_logged_in = False
                    st.session_state.user_email = None
                    st.rerun()
                except Exception as e:
                    st.error(f"{t['error']} {e}")
            else:
                st.warning("Lütfen silme işlemini onaylayın.")
                
        if st.button(f"🚪 {t['logout']}", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.is_logged_in = False
            st.session_state.user_email = None
            st.rerun()

    st.markdown("---")
    
    # AI Girdi Parametreleri (Eski Koddan EKSİKSİZ şekilde taşındı)
    st.header(t["settings"])

    st.session_state.target_lang_input = st.text_input(f"✍️ {t['target_lang']}", value=st.session_state.target_lang_input)
    st.session_state.prop_type = st.text_input(t["prop_type"], value=st.session_state.prop_type, placeholder=t["ph_prop"])
    st.session_state.price = st.text_input(t["price"], value=st.session_state.price, placeholder=t["ph_price"])
    st.session_state.location = st.text_input(t["location"], value=st.session_state.location, placeholder=t["ph_loc"])

    current_tone_idx = t["tones"].index(st.session_state.tone) if st.session_state.tone in t["tones"] else 0
    st.session_state.tone = st.selectbox(t["tone"], t["tones"], index=current_tone_idx)
    st.session_state.custom_inst = st.text_area(f"📝 {t['custom_inst']}", value=st.session_state.custom_inst, placeholder=t["custom_inst_ph"], height=100)


# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
st.markdown(f"<h1 style='text-align: center;'>🏢 {t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;'>{t['service_desc']}</p>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(f"📸 {t['upload_label']}", type=["jpg", "png", "webp", "jpeg"], accept_multiple_files=True) 

if uploaded_files: 
    images_for_ai = [Image.open(f) for f in uploaded_files] 
    cols = st.columns(min(len(images_for_ai), 4)) 
    for i, img in enumerate(images_for_ai): 
        with cols[i % 4]: 
            st.image(img, use_container_width=True)
    
    # AI Tarafına istek atacak Buton Alanı (Gelecekte logic buraya bağlanabilir)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 OLUŞTUR (GENERATE)", use_container_width=True):
        st.info("AI Logic buraya entegre edilecek!")
        
else: 
    st.markdown(f"""
    <div style='text-align:center; padding: 3rem; background: #f8fafc; border-radius: 12px; border: 2px dashed #cbd5e1; margin-top: 2rem;'>
        <h3 style='color: #475569;'>🏘️ {t.get('result', 'Executive Preview')}</h3>
        <p style='color: #94a3b8;'>{t['empty']}</p>
    </div>
    """, unsafe_allow_html=True)
