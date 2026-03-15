import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components
import time

# ─── PAGE CONFIG (must be first) ──────────────────────────────────────────────
st.set_page_config(page_title="SarSa AI | Real Estate Intelligence", page_icon="🏢", layout="wide")

# ─── HASH FRAGMENT → QUERY PARAM REDIRECT (Güncellenmiş) ──────────────────────
components.html("""
<script>
(function() {
    var hash = window.parent.location.hash;
    if (hash && hash.includes('access_token')) {
        var currentSearch = window.parent.location.search;
        var hashQuery = hash.substring(1); // baştaki '#' işaretini at
        
        // Eğer URL'de halihazırda '?' varsa '&' ile ekle, yoksa '?' ile ekle
        var separator = currentSearch ? '&' : '?';

        // Eğer URL'de zaten access_token yoksa, hash'tekileri URL'e ekle ve yönlendir
        if (!currentSearch.includes('access_token')) {
            var newUrl = window.parent.location.origin + window.parent.location.pathname + currentSearch + separator + hashQuery;
            window.parent.location.href = newUrl;
        }
    }
})();
</script>
""", height=0)

# ─── SUPABASE CONFIGURATION ───────────────────────────────────────────────────
SUPABASE_URL: str = st.secrets["SUPABASE_URL"]
SUPABASE_KEY: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── SESSION STATE INITIALIZATION ─────────────────────────────────────────────
query_params = st.query_params

# URL'de dil parametresi varsa onu al, yoksa English olarak başlat (Hafıza özelliği)
initial_lang = query_params.get("lang", "English")

if 'auth_lang'              not in st.session_state: st.session_state.auth_lang              = initial_lang
if 'is_logged_in'           not in st.session_state: st.session_state.is_logged_in           = False
if 'user_email'             not in st.session_state: st.session_state.user_email             = None
if 'recovery_mode'          not in st.session_state: st.session_state.recovery_mode          = False
if 'access_token'           not in st.session_state: st.session_state.access_token           = None
if 'refresh_token'          not in st.session_state: st.session_state.refresh_token          = None
if 'show_email_confirmed'   not in st.session_state: st.session_state.show_email_confirmed   = False  

for key_name, val in [
    ("uretilen_ilan", ""), ("prop_type", ""), ("price", ""),
    ("location", ""), ("tone", ""), ("custom_inst", ""),
    ("target_lang_input", "English"), ("bedrooms", ""),
    ("bathrooms", ""), ("area_size", ""), ("year_built", ""),
    ("furnishing_idx", 0), ("audience_idx", 0), ("selected_sections", [])
]:
    if key_name not in st.session_state:
        st.session_state[key_name] = val

# ─── EMAIL HELPER — Delete Confirmation ───────────────────────────────────────
def send_delete_confirmation_email(to_email: str, confirm_token: str, cancel_token: str):
    app_url     = "https://sarsa-ai-estateintelligence.streamlit.app/"
    confirm_url = f"{app_url}?action=confirm_delete&token={confirm_token}"
    cancel_url  = f"{app_url}?action=cancel_delete&token={cancel_token}"
    html_body = f"""
    <div style="font-family:'Arial',sans-serif;max-width:620px;margin:0 auto;padding:30px;background:#f8fafc;border-radius:16px;">
      <div style="background:white;border-radius:12px;padding:36px;box-shadow:0 4px 20px rgba(0,0,0,0.07);">
        <div style="text-align:center;margin-bottom:28px;">
          <h2 style="color:#0f172a;font-size:22px;margin:0;">⚠️ Account Deletion Request</h2>
          <p style="color:#64748b;margin-top:8px;font-size:14px;">SarSa AI | Real Estate Intelligence</p>
        </div>
        <p style="color:#334155;font-size:16px;line-height:1.6;">
          We received a request to <strong>permanently delete</strong> the SarSa AI account associated with:<br>
          <strong style="color:#0f172a;">{to_email}</strong>
        </p>
        <p style="color:#ef4444;font-size:15px;font-weight:600;">This action is irreversible. All your data will be permanently removed.</p>
        <div style="text-align:center;margin:32px 0;">
          <a href="{confirm_url}" style="background-color:#dc2626;color:white;padding:14px 32px;border-radius:10px;text-decoration:none;font-weight:700;font-size:16px;display:inline-block;margin-bottom:14px;">
            Yes, Delete My Account
          </a><br>
          <a href="{cancel_url}" style="background-color:#0f172a;color:white;padding:14px 32px;border-radius:10px;text-decoration:none;font-weight:700;font-size:16px;display:inline-block;">
            Cancel - Keep My Account Safe
          </a>
        </div>
        <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;">
        <p style="color:#94a3b8;font-size:13px;text-align:center;">
          This link expires in <strong>24 hours</strong>.<br>
          If you did not request this, simply ignore this email.
        </p>
      </div>
    </div>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "SarSa AI - Confirm Account Deletion"
        msg["From"]    = st.secrets["SMTP_USER"]
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html"))
        smtp_host = st.secrets.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(st.secrets.get("SMTP_PORT", 587))
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo(); server.starttls()
            server.login(st.secrets["SMTP_USER"], st.secrets["SMTP_PASS"])
            server.sendmail(st.secrets["SMTP_USER"], to_email, msg.as_string())
        return True, ""
    except Exception as smtp_err:
        return False, str(smtp_err)

def is_email_registered(email: str) -> bool:
    try:
        svc = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"])
        users_resp = svc.auth.admin.list_users()
        registered = [u.email.lower() for u in users_resp if u.email]
        return email.lower().strip() in registered
    except Exception:
        return True

# ─── GLOBAL SESSION RESTORE (Ensures Auth Context is active) ──────────────────
if st.session_state.access_token and st.session_state.refresh_token:
    try:
        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
    except Exception as e:
        pass # Ignore silently, token might be expired

# ─── QUERY PARAM HANDLERS & ROUTING ───────────────────────────────────────────
action = query_params.get("action")

# 1) PKCE Flow & Code Exchange
if "code" in query_params:
    try:
        res = supabase.auth.exchange_code_for_session({"auth_code": query_params["code"]})
        if res and hasattr(res, 'session') and res.session:
            st.session_state.access_token = res.session.access_token
            st.session_state.refresh_token = res.session.refresh_token
            supabase.auth.set_session(res.session.access_token, res.session.refresh_token)
    except Exception:
        pass

# 2) Implicit Flow (Yedek - Hash fragment redirect üzerinden gelen)
if "access_token" in query_params:
    _at = query_params.get("access_token")
    _rt = query_params.get("refresh_token")
    if _at:
        st.session_state.access_token = _at
        st.session_state.refresh_token = _rt
        try:
            supabase.auth.set_session(_at, _rt)
        except Exception:
            pass

# 3) Eylem (Action) Yönlendirmeleri
if action == "signup_confirm" or query_params.get("type") == "signup":
    st.session_state.show_email_confirmed = True
    st.session_state.is_logged_in = False
    
    # URL'yi temizle ama dili koru
    current_lang = st.session_state.auth_lang
    st.query_params.clear()
    st.query_params["lang"] = current_lang
    st.rerun()

elif action == "reset_pw" or query_params.get("type") == "recovery":
    st.session_state.recovery_mode = True
    st.session_state.is_logged_in = False
    
    # URL'yi temizle ama dili koru
    current_lang = st.session_state.auth_lang
    st.query_params.clear()
    st.query_params["lang"] = current_lang
    st.rerun()

# 4) Hesap Silme Onayı
elif action == "confirm_delete":
    token = query_params.get("token", "")
    try:
        result = supabase.table("pending_deletions").select("*").eq("confirm_token", token).execute()
        if result.data:
            record     = result.data[0]
            expires_at = datetime.fromisoformat(record.get("expires_at","").replace("Z","+00:00"))
            if datetime.now(timezone.utc) < expires_at:
                try:
                    svc = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"])
                    svc.auth.admin.delete_user(record["user_id"])
                except Exception:
                    pass 
                
                supabase.table("pending_deletions").delete().eq("confirm_token", token).execute()
                
                for _k in ["is_logged_in","user_email","access_token","refresh_token"]:
                    st.session_state[_k] = None if _k != "is_logged_in" else False
                st.query_params.clear()
                
                st.markdown("""
                <div style='text-align:center;padding:5rem 2rem;'>
                  <div style='font-size:5rem;margin-bottom:1rem;'>👋</div>
                  <h1 style='color:#0f172a;font-weight:800;'>Account Deleted</h1>
                  <p style='color:#475569;font-size:1.15rem;margin-top:1rem;line-height:1.7;'>
                    Your SarSa AI account has been <strong>permanently deleted</strong>.<br>
                    All your data has been removed from our systems.
                  </p>
                  <p style='color:#94a3b8;margin-top:2rem;font-size:0.95rem;'>You have been logged out.</p>
                </div>""", unsafe_allow_html=True)
                st.stop()
            else:
                st.error("This confirmation link has expired (24h limit). Please request a new deletion from Account Settings.")
        else:
            st.error("Invalid or already used link.")
    except Exception as e:
        st.error(f"Error during account deletion: {e}")
    st.stop()

# 5) Hesap Silme İptali
elif action == "cancel_delete":
    token = query_params.get("token", "")
    try:
        supabase.table("pending_deletions").delete().eq("cancel_token", token).execute()
    except Exception:
        pass
    st.query_params.clear()
    st.success("Account deletion cancelled. Your account is completely safe!")
    time.sleep(2)
    st.rerun()

# ─── PERSISTENT SESSION CHECK ─────────────────────────────────────────────────
# ÖNEMLİ DÜZELTME: recovery_mode içindeyken session check yapıp token'ları silmesini engelledik.
if st.session_state.access_token and not st.session_state.is_logged_in and not st.session_state.recovery_mode:
    try:
        _check = supabase.auth.get_user()
        if _check and _check.user:
            st.session_state.is_logged_in = True
            st.session_state.user_email   = _check.user.email
    except Exception:
        st.session_state.access_token  = None
        st.session_state.refresh_token = None
        st.session_state.is_logged_in  = False

# ─── TEXT DICTIONARIES (9 LANGUAGES) ──────────────────────────────────────────
auth_texts = {
    "English": {
        "access":"SarSa AI Access","login":"Login","register":"Register",
        "email":"Email","password":"Password","btn_login":"Login",
        "btn_reg":"Create Account",
        "success_reg":"Registration successful! Check your email to verify your account.",
        "error_login":"Login failed. You are not registered, or your Email/Password is incorrect.",
        "verify_msg":"Please verify your email:","btn_check":"I verified, let me in",
        "unpaid_msg":"Subscription required.","upgrade_title":"Professional Plan",
        "pay_btn":"Subscribe Now","welcome_title":"Welcome to SarSa AI",
        "welcome_desc":"The All-in-One Visual Property Intelligence & Global Sales Automation platform. Transform your property photos into professional assets in seconds.",
        "login_prompt":"Log in to use the application",
        "forgot_pw":"Forgot Password?","btn_reset":"Send Reset Link",
        "reset_success":"Password reset link sent! Check your inbox.",
        "reset_not_found":"No account found with this email address. Please register first.",
        "reset_invalid_email":"Please enter a valid email address.",
        "email_confirmed_title":"✅ Email Verified Successfully!",
        "email_confirmed_msg":"Your SarSa AI account has been confirmed and is ready to use.",
        "email_confirmed_sub":"Click the button below to go to the login page and get started.",
        "email_confirmed_btn":"🔑 Go to Login",
        "pw_reset_title":"Set Your New Password",
        "pw_reset_desc":"Enter a new password for your account. You will be logged in automatically after saving.",
        "pw_reset_btn":"✅ Set Password & Login",
        "pw_reset_cancel":"❌ Cancel",
        "pw_reset_success":"✅ Password updated successfully! Logging you in...",
        "pw_reset_min_err":"❌ Password must be at least 6 characters!",
        "new_pw_label":"New Password",
        "lang_select_label": "🌐 Select Language"
    },
    "Türkçe": {
        "access":"SarSa AI Erişimi","login":"Giriş Yap","register":"Kayıt Ol",
        "email":"E-posta","password":"Şifre","btn_login":"Oturum Aç",
        "btn_reg":"Hesap Oluştur",
        "success_reg":"Kayıt başarılı! Hesabınızı onaylamak için e-postanızı kontrol edin.",
        "error_login":"Giriş başarısız. Kayıtlı değilsiniz veya E-posta/Şifreniz hatalı.",
        "verify_msg":"Lütfen e-postanızı onaylayın:","btn_check":"Onayladım, içeri al",
        "unpaid_msg":"Abonelik gerekiyor.","upgrade_title":"Profesyonel Paket",
        "pay_btn":"Şimdi Abone Ol","welcome_title":"SarSa AI'a Hoş Geldiniz",
        "welcome_desc":"Hepsi Bir Arada Görsel Mülk Zekâsı ve Küresel Satış Otomasyonu platformu. Mülk fotoğraflarınızı saniyeler içinde profesyonel varlıklara dönüştürün.",
        "login_prompt":"Uygulamayı kullanmak için giriş yapın",
        "forgot_pw":"Şifremi Unuttum?","btn_reset":"Sıfırlama Bağlantısı Gönder",
        "reset_success":"Şifre sıfırlama bağlantısı gönderildi! Gelen kutunuzu kontrol edin.",
        "reset_not_found":"Bu e-posta adresiyle kayıtlı hesap bulunamadı. Lütfen önce kayıt olun.",
        "reset_invalid_email":"Lütfen geçerli bir e-posta adresi girin.",
        "email_confirmed_title":"✅ E-posta Başarıyla Doğrulandı!",
        "email_confirmed_msg":"SarSa AI hesabınız onaylandı ve kullanıma hazır.",
        "email_confirmed_sub":"Giriş sayfasına gitmek ve başlamak için aşağıdaki butona tıklayın.",
        "email_confirmed_btn":"🔑 Giriş Sayfasına Git",
        "pw_reset_title":"Yeni Şifrenizi Belirleyin",
        "pw_reset_desc":"Hesabınız için yeni bir şifre girin. Kaydettikten sonra otomatik olarak giriş yapılacaksınız.",
        "pw_reset_btn":"✅ Şifreyi Kaydet ve Giriş Yap",
        "pw_reset_cancel":"❌ İptal",
        "pw_reset_success":"✅ Şifre başarıyla güncellendi! Giriş yapılıyor...",
        "pw_reset_min_err":"❌ Şifre en az 6 karakter olmalıdır!",
        "new_pw_label":"Yeni Şifre",
        "lang_select_label": "🌐 Dil Seçin"
    },
    "Español": {
        "access":"Acceso a SarSa AI","login":"Iniciar Sesión","register":"Registrarse",
        "email":"Correo","password":"Clave","btn_login":"Entrar",
        "btn_reg":"Crear Cuenta",
        "success_reg":"Registro exitoso! Revisa tu email para verificar tu cuenta.",
        "error_login":"Error. No estás registrado o tu Correo/Clave es incorrecto.",
        "verify_msg":"Verifica tu email:","btn_check":"Ya verifiqué, entrar",
        "unpaid_msg":"Suscripción necesaria.","upgrade_title":"Plan Profesional",
        "pay_btn":"Suscribirse Ahora","welcome_title":"Bienvenido a SarSa AI",
        "welcome_desc":"La plataforma todo en uno de Inteligencia Visual de Propiedades y Automatización de Ventas. Transforme sus fotos en activos profesionales en segundos.",
        "login_prompt":"Inicie sesión para usar la aplicación",
        "forgot_pw":"Olvidaste tu contraseña?","btn_reset":"Enviar enlace",
        "reset_success":"¡Enlace de restablecimiento enviado! Revisa tu bandeja.",
        "reset_not_found":"No se encontró ninguna cuenta con este correo. Por favor regístrate primero.",
        "reset_invalid_email":"Por favor ingresa un correo válido.",
        "email_confirmed_title":"✅ ¡Email Verificado Exitosamente!",
        "email_confirmed_msg":"Tu cuenta de SarSa AI ha sido confirmada y está lista para usar.",
        "email_confirmed_sub":"Haz clic abajo para ir a la página de inicio de sesión.",
        "email_confirmed_btn":"🔑 Ir al Login",
        "pw_reset_title":"Establece tu Nueva Contraseña",
        "pw_reset_desc":"Ingresa una nueva contraseña. Iniciarás sesión automáticamente al guardar.",
        "pw_reset_btn":"✅ Guardar Contraseña e Iniciar Sesión",
        "pw_reset_cancel":"❌ Cancelar",
        "pw_reset_success":"✅ ¡Contraseña actualizada! Iniciando sesión...",
        "pw_reset_min_err":"❌ Mínimo 6 caracteres requeridos.",
        "new_pw_label":"Nueva Contraseña",
        "lang_select_label": "🌐 Seleccionar Idioma"
    },
    "Deutsch": {
        "access":"SarSa AI Zugang","login":"Anmelden","register":"Registrieren",
        "email":"E-Mail","password":"Passwort","btn_login":"Login",
        "btn_reg":"Konto Erstellen",
        "success_reg":"Erfolgreich! Bitte bestätigen Sie Ihre E-Mail.",
        "error_login":"Login fehlgeschlagen. Nicht registriert oder E-Mail/Passwort falsch.",
        "verify_msg":"E-Mail bestätigen:","btn_check":"Bestätigt, einloggen",
        "unpaid_msg":"Abo erforderlich.","upgrade_title":"Profi-Paket",
        "pay_btn":"Jetzt Abonnieren","welcome_title":"Willkommen bei SarSa AI",
        "welcome_desc":"Die All-in-One-Plattform für visuelle Immobilienintelligenz. Verwandeln Sie Ihre Immobilienfotos in Sekundenschnelle in professionelle Assets.",
        "login_prompt":"Melden Sie sich an, um die App zu nutzen",
        "forgot_pw":"Passwort vergessen?","btn_reset":"Link senden",
        "reset_success":"Link gesendet! Überprüfen Sie Ihren Posteingang.",
        "reset_not_found":"Kein Konto mit dieser E-Mail gefunden. Bitte zuerst registrieren.",
        "reset_invalid_email":"Bitte gültige E-Mail-Adresse eingeben.",
        "email_confirmed_title":"✅ E-Mail erfolgreich verifiziert!",
        "email_confirmed_msg":"Ihr SarSa AI-Konto wurde bestätigt und ist einsatzbereit.",
        "email_confirmed_sub":"Klicken Sie unten, um zur Anmeldeseite zu gelangen.",
        "email_confirmed_btn":"🔑 Zur Anmeldung",
        "pw_reset_title":"Neues Passwort festlegen",
        "pw_reset_desc":"Geben Sie ein neues Passwort ein. Sie werden automatisch eingeloggt.",
        "pw_reset_btn":"✅ Passwort speichern & einloggen",
        "pw_reset_cancel":"❌ Abbrechen",
        "pw_reset_success":"✅ Passwort aktualisiert! Einloggen...",
        "pw_reset_min_err":"❌ Mindestens 6 Zeichen erforderlich.",
        "new_pw_label":"Neues Passwort",
        "lang_select_label": "🌐 Sprache Wählen"
    },
    "Français": {
        "access":"Accès SarSa AI","login":"Connexion","register":"S'inscrire",
        "email":"Email","password":"Mot de passe","btn_login":"Se connecter",
        "btn_reg":"Créer un compte",
        "success_reg":"Succes! Vérifiez vos emails pour confirmer.",
        "error_login":"Echec. Vous n'êtes pas inscrit ou Email/Mot de passe incorrect.",
        "verify_msg":"Vérifiez votre email:","btn_check":"Vérifié, entrer",
        "unpaid_msg":"Abonnement requis.","upgrade_title":"Pack Professionnel",
        "pay_btn":"S'abonner Maintenant","welcome_title":"Bienvenue sur SarSa AI",
        "welcome_desc":"La plateforme d'Intelligence Visuelle Immobilière et d'Automatisation des Ventes. Transformez vos photos en atouts professionnels en quelques secondes.",
        "login_prompt":"Connectez-vous pour utiliser l'application",
        "forgot_pw":"Mot de passe oublié?","btn_reset":"Envoyer le lien",
        "reset_success":"Lien envoyé ! Vérifiez votre boîte de réception.",
        "reset_not_found":"Aucun compte trouvé avec cet email. Veuillez d'abord vous inscrire.",
        "reset_invalid_email":"Veuillez entrer une adresse email valide.",
        "email_confirmed_title":"✅ Email vérifié avec succès !",
        "email_confirmed_msg":"Votre compte SarSa AI a été confirmé et est prêt à l'emploi.",
        "email_confirmed_sub":"Cliquez ci-dessous pour accéder à la page de connexion.",
        "email_confirmed_btn":"🔑 Aller à la connexion",
        "pw_reset_title":"Définissez votre nouveau mot de passe",
        "pw_reset_desc":"Entrez un nouveau mot de passe. Vous serez connecté automatiquement après.",
        "pw_reset_btn":"✅ Enregistrer & Se connecter",
        "pw_reset_cancel":"❌ Annuler",
        "pw_reset_success":"✅ Mot de passe mis à jour ! Connexion en cours...",
        "pw_reset_min_err":"❌ 6 caractères minimum.",
        "new_pw_label":"Nouveau mot de passe",
        "lang_select_label": "🌐 Choisir la Langue"
    },
    "Português": {
        "access":"Acesso SarSa AI","login":"Entrar","register":"Registar",
        "email":"Email","password":"Senha","btn_login":"Login",
        "btn_reg":"Criar Conta",
        "success_reg":"Sucesso! Verifique seu email para confirmar a conta.",
        "error_login":"Falha. Não registado ou Email/Senha incorretos.",
        "verify_msg":"Verifique seu email:","btn_check":"Verificado, entrar",
        "unpaid_msg":"Assinatura necessária.","upgrade_title":"Plano Profissional",
        "pay_btn":"Assinar Agora","welcome_title":"Bem-vindo ao SarSa AI",
        "welcome_desc":"A plataforma tudo-em-um de Inteligência Imobiliária Visual e Automação de Vendas. Transforme as suas fotos em ativos profissionais em segundos.",
        "login_prompt":"Faça login para usar o aplicativo",
        "forgot_pw":"Esqueceu a senha?","btn_reset":"Enviar link",
        "reset_success":"Link enviado! Verifique sua caixa de entrada.",
        "reset_not_found":"Nenhuma conta encontrada com este email. Por favor registe-se primeiro.",
        "reset_invalid_email":"Por favor insira um endereço de email válido.",
        "email_confirmed_title":"✅ Email Verificado com Sucesso!",
        "email_confirmed_msg":"Sua conta SarSa AI foi confirmada e está pronta para uso.",
        "email_confirmed_sub":"Clique abaixo para ir à página de login e começar.",
        "email_confirmed_btn":"🔑 Ir para o Login",
        "pw_reset_title":"Defina sua Nova Senha",
        "pw_reset_desc":"Insira uma nova senha. Você será logado automaticamente após salvar.",
        "pw_reset_btn":"✅ Salvar Senha & Entrar",
        "pw_reset_cancel":"❌ Cancelar",
        "pw_reset_success":"✅ Senha atualizada! Entrando...",
        "pw_reset_min_err":"❌ Mínimo de 6 caracteres.",
        "new_pw_label":"Nova Senha",
        "lang_select_label": "🌐 Selecionar Idioma"
    },
    "日本語": {
        "access":"SarSa AI アクセス","login":"ログイン","register":"新規登録",
        "email":"メール","password":"パスワード","btn_login":"ログイン",
        "btn_reg":"アカウント作成",
        "success_reg":"登録完了！メールを確認してアカウントを認証してください。",
        "error_login":"ログイン失敗。未登録か、メール/パスワードが間違っています。",
        "verify_msg":"メールを認証してください:","btn_check":"認証済み、入る",
        "unpaid_msg":"サブスクリプションが必要です。","upgrade_title":"プロフェッショナルプラン",
        "pay_btn":"今すぐ購読","welcome_title":"SarSa AI へようこそ",
        "welcome_desc":"オールインワンの視覚的物件インテリジェンス＆販売自動化プラットフォーム。物件の写真を数秒でプロフェッショナルな資産に変換します。",
        "login_prompt":"アプリを使用するにはログインしてください",
        "forgot_pw":"パスワードをお忘れですか？","btn_reset":"リンクを送信",
        "reset_success":"リセットリンクを送信しました！受信トレイをご確認ください。",
        "reset_not_found":"このメールアドレスのアカウントが見つかりません。先に登録してください。",
        "reset_invalid_email":"有効なメールアドレスを入力してください。",
        "email_confirmed_title":"✅ メールが正常に認証されました！",
        "email_confirmed_msg":"SarSa AI アカウントが確認され、ご利用いただけます。",
        "email_confirmed_sub":"下のボタンをクリックしてログインページに移動してください。",
        "email_confirmed_btn":"🔑 ログインページへ",
        "pw_reset_title":"新しいパスワードを設定",
        "pw_reset_desc":"新しいパスワードを入力してください。保存後に自動的にログインされます。",
        "pw_reset_btn":"✅ パスワードを保存してログイン",
        "pw_reset_cancel":"❌ キャンセル",
        "pw_reset_success":"✅ パスワードが更新されました！ログイン中...",
        "pw_reset_min_err":"❌ 6文字以上必要です。",
        "new_pw_label":"新しいパスワード",
        "lang_select_label": "🌐 言語を選択"
    },
    "简体中文": {
        "access":"SarSa AI 访问","login":"登录","register":"注册",
        "email":"邮箱","password":"密码","btn_login":"登录",
        "btn_reg":"创建账号",
        "success_reg":"注册成功！请检查邮箱以验证账号。",
        "error_login":"登录失败。您未注册，或邮箱/密码错误。",
        "verify_msg":"请验证您的邮箱:","btn_check":"已验证，进入",
        "unpaid_msg":"需要订阅。","upgrade_title":"专业版方案",
        "pay_btn":"立即订阅","welcome_title":"欢迎来到 SarSa AI",
        "welcome_desc":"全方位房产视觉智能与全球销售自动化平台。在几秒钟内将您的房产照片转化为专业的营销资产。",
        "login_prompt":"登录以使用该应用程序",
        "forgot_pw":"忘记密码？","btn_reset":"发送重置链接",
        "reset_success":"重置链接已发送！请检查您的邮箱。",
        "reset_not_found":"未找到使用此邮箱注册的账号，请先注册。",
        "reset_invalid_email":"请输入有效的电子邮件地址。",
        "email_confirmed_title":"✅ 邮箱验证成功！",
        "email_confirmed_msg":"您的 SarSa AI 账户已确认，可以开始使用。",
        "email_confirmed_sub":"点击下方按钮前往登录页面开始使用。",
        "email_confirmed_btn":"🔑 前往登录",
        "pw_reset_title":"设置您的新密码",
        "pw_reset_desc":"为您的账号输入新密码。保存后将自动登录。",
        "pw_reset_btn":"✅ 保存密码并登录",
        "pw_reset_cancel":"❌ 取消",
        "pw_reset_success":"✅ 密码已更新！正在登录...",
        "pw_reset_min_err":"❌ 密码至少需要6位。",
        "new_pw_label":"新密码",
        "lang_select_label": "🌐 选择语言"
    },
    "العربية": {
        "access":"دخول SarSa AI","login":"تسجيل الدخول","register":"إنشاء حساب",
        "email":"البريد","password":"كلمة السر","btn_login":"دخول",
        "btn_reg":"إنشاء حساب",
        "success_reg":"تم التسجيل بنجاح! تحقق من بريدك لتأكيد الحساب.",
        "error_login":"فشل الدخول. أنت غير مسجل، أو البريد/كلمة السر خاطئة.",
        "verify_msg":"يرجى تأكيد بريدك:","btn_check":"تم التأكيد، دخول",
        "unpaid_msg":"يتطلب اشتراكاً نشطاً.","upgrade_title":"الباقة الاحترافية",
        "pay_btn":"اشترك الآن","welcome_title":"مرحباً بك في SarSa AI",
        "welcome_desc":"منصة الذكاء البصري المتكامل للعقارات وأتمتة المبيعات العالمية. حول صور عقاراتك إلى أصول احترافية في ثوانٍ.",
        "login_prompt":"قم بتسجيل الدخول لاستخدام التطبيق",
        "forgot_pw":"نسيت كلمة السر؟","btn_reset":"إرسال رابط الاستعادة",
        "reset_success":"تم إرسال رابط إعادة التعيين! تحقق من صندوق الوارد.",
        "reset_not_found":"لم يتم العثور على حساب بهذا البريد. يرجى التسجيل أولاً.",
        "reset_invalid_email":"يرجى إدخال عنوان بريد إلكتروني صالح.",
        "email_confirmed_title":"✅ تم التحقق من البريد بنجاح!",
        "email_confirmed_msg":"تم تأكيد حساب SarSa AI الخاص بك وهو جاهز للاستخدام.",
        "email_confirmed_sub":"انقر على الزر أدناه للانتقال إلى صفحة تسجيل الدخول.",
        "email_confirmed_btn":"🔑 الذهاب إلى تسجيل الدخول",
        "pw_reset_title":"تعيين كلمة المرور الجديدة",
        "pw_reset_desc":"أدخل كلمة مرور جديدة لحسابك. سيتم تسجيل دخولك تلقائياً بعد الحفظ.",
        "pw_reset_btn":"✅ حفظ كلمة المرور وتسجيل الدخول",
        "pw_reset_cancel":"❌ إلغاء",
        "pw_reset_success":"✅ تم تحديث كلمة المرور! جاري تسجيل الدخول...",
        "pw_reset_min_err":"❌ يجب أن تكون 6 خانات على الأقل.",
        "new_pw_label":"كلمة المرور الجديدة",
        "lang_select_label": "🌐 اختر اللغة"
    }
}

ui_languages = {
    "English": { "title": "SarSa AI | Real Estate Intelligence Platform", "service_desc": "All-in-One Visual Property Intelligence & Global Sales Automation", "subtitle": "Transform property photos into premium listings, social media kits, cinematic video scripts, technical specs, email campaigns and SEO copy — instantly.", "settings": "Configuration", "target_lang": "Write Listing In...", "prop_type": "Property Type", "price": "Market Price", "location": "Location", "tone": "Marketing Strategy", "tones": ["Standard Pro", "Ultra-Luxury", "Investment Focus", "Modern Minimalist", "Family Living", "Vacation Rental", "Commercial"], "ph_prop": "E.g., 3+1 Apartment, Luxury Villa...", "ph_price": "E.g., $850,000 or £2,000/mo...", "ph_loc": "E.g., Manhattan, NY or Dubai Marina...", "bedrooms": "Bedrooms", "bathrooms": "Bathrooms", "area": "Area", "year_built": "Year Built", "ph_beds": "E.g., 3", "ph_baths": "E.g., 2", "ph_area": "E.g., 185 sqm", "ph_year": "E.g., 2022", "furnishing": "Furnishing", "furnishing_opts": ["Not Specified", "Fully Furnished", "Semi-Furnished", "Unfurnished"], "target_audience": "Target Audience", "audience_opts": ["General Market", "Luxury Buyers", "Investors & ROI Focus", "Expats & Internationals", "First-Time Buyers", "Vacation / Holiday Market", "Commercial Tenants"], "custom_inst": "Special Notes & Highlights", "custom_inst_ph": "E.g., Private pool, panoramic sea view, smart home...", "btn": "GENERATE SELECTED ASSETS", "upload_label": "Drop Property Photos Here", "result": "Executive Preview", "loading": "Crafting your premium marketing ecosystem...", "empty": "Upload property photos and fill in the details on the left to generate complete professional marketing assets.", "download": "Export Section (TXT)", "save_btn": "Save Changes", "saved_msg": "Saved!", "error": "Error:", "clear_btn": "Reset Form", "select_sections": "Select Assets to Generate", "tab_main": "Prime Listing", "tab_social": "Social Media Kit", "tab_video": "Video Scripts", "tab_tech": "Technical Specs", "tab_email": "Email Campaign", "tab_seo": "SEO & Web Copy", "tab_photo": "Photo Guide", "label_main": "Sales Copy", "label_social": "Social Media Content", "label_video": "Video Script", "label_tech": "Technical Specifications", "label_email": "Email Campaign", "label_seo": "SEO & Web Copy", "label_photo": "Photography Recommendations", "extra_details": "Extra Property Details", "interface_lang": "Interface Language", "logout": "Logout", "acc_settings": "Account Settings", "update_pw": "Update Password", "new_pw": "New Password", "btn_update": "Update Now", "danger_zone": "Danger Zone", "delete_confirm": "I want to permanently delete my account.", "btn_delete": "Delete Account", "pw_min_err": "Minimum 6 characters required.", "delete_email_sent": "Confirmation email sent! Check your inbox and click the link to confirm deletion.", "delete_email_fail": "Failed to send email. Please check SMTP settings in secrets." },
    "Türkçe": { "title": "SarSa AI | Gayrimenkul Zekâ Platformu", "service_desc": "Hepsi Bir Arada Görsel Mülk Zekâsı ve Küresel Satış Otomasyonu", "subtitle": "Mülk fotoğraflarını anında profesyonel ilanlara, sosyal medya kitlerine, sinematik senaryolara, teknik şartnamelere, e-posta kampanyalarına ve SEO metinlerine dönüştürün.", "settings": "Yapılandırma", "target_lang": "İlan Yazım Dili...", "prop_type": "Emlak Tipi", "price": "Pazar Fiyatı", "location": "Konum", "tone": "Pazarlama Stratejisi", "tones": ["Standart Profesyonel", "Ultra-Lüks", "Yatırım Odaklı", "Modern Minimalist", "Aile Yaşamı", "Tatil Kiralık", "Ticari"], "ph_prop": "Örn: 3+1 Daire, Müstakil Villa...", "ph_price": "Örn: 5.000.000 TL veya $2.500/ay...", "ph_loc": "Örn: Beşiktaş, İstanbul veya Dubai Marina...", "bedrooms": "Yatak Odası", "bathrooms": "Banyo", "area": "Alan", "year_built": "İnşaat Yılı", "ph_beds": "Örn: 3", "ph_baths": "Örn: 2", "ph_area": "Örn: 185 m²", "ph_year": "Örn: 2022", "furnishing": "Eşya Durumu", "furnishing_opts": ["Belirtilmedi", "Tam Eşyalı", "Yarı Eşyalı", "Eşyasız"], "target_audience": "Hedef Kitle", "audience_opts": ["Genel Pazar", "Lüks Alıcılar", "Yatırımcılar & ROI Odaklı", "Yabancılar & Uluslararası", "İlk Ev Alıcıları", "Tatil / Kiralık Pazar", "Ticari Kiracılar"], "custom_inst": "Özel Notlar ve Öne Çıkan Özellikler", "custom_inst_ph": "Örn: Özel havuz, panoramik manzara, akıllı ev sistemi...", "btn": "SEÇİLİ VARLIKLARI OLUŞTUR", "upload_label": "Fotoğrafları Buraya Bırakın", "result": "Yönetici Önizlemesi", "loading": "Premium pazarlama ekosisteminiz hazırlanıyor...", "empty": "Profesyonel analiz için görsel bekleniyor. Fotoğrafları yükleyin ve soldaki bilgileri doldurun.", "download": "Bölümü İndir (TXT)", "save_btn": "Kaydet", "saved_msg": "Kaydedildi!", "error": "Hata:", "clear_btn": "Formu Temizle", "select_sections": "Oluşturulacak Bölümleri Seçin", "tab_main": "Ana İlan", "tab_social": "Sosyal Medya Kiti", "tab_video": "Video Senaryoları", "tab_tech": "Teknik Özellikler", "tab_email": "E-posta Kampanyası", "tab_seo": "SEO & Web Metni", "tab_photo": "Fotoğraf Rehberi", "label_main": "Satış Metni", "label_social": "Sosyal Medya", "label_video": "Video Script", "label_tech": "Teknik Detaylar", "label_email": "E-posta Kampanyası", "label_seo": "SEO & Web Metni", "label_photo": "Fotoğraf Tavsiyeleri", "extra_details": "Ek Mülk Detayları", "interface_lang": "Arayüz Dili", "logout": "Çıkış Yap", "acc_settings": "Hesap Ayarları", "update_pw": "Şifre Güncelle", "new_pw": "Yeni Şifre", "btn_update": "Şifreyi Güncelle", "danger_zone": "Tehlikeli Bölge", "delete_confirm": "Hesabımı kalıcı olarak silmek istiyorum.", "btn_delete": "Hesabı Sil", "pw_min_err": "Şifre en az 6 karakter olmalıdır.", "delete_email_sent": "Onay e-postası gönderildi! Gelen kutunuzu kontrol edin ve silmeyi onaylamak için bağlantıya tıklayın.", "delete_email_fail": "E-posta gönderilemedi. Lütfen SMTP ayarlarını kontrol edin." },
    "Español": { "title": "SarSa AI | Plataforma de Inteligencia Inmobiliaria", "service_desc": "Inteligencia Visual de Propiedades y Automatización de Ventas Globales", "subtitle": "Convierta fotos en anuncios premium, kits de redes sociales, guiones de video, fichas técnicas, campañas de email y copy SEO al instante.", "settings": "Configuración", "target_lang": "Escribir en...", "prop_type": "Tipo de Propiedad", "price": "Precio de Mercado", "location": "Ubicación", "tone": "Estrategia de Marketing", "tones": ["Profesional Estándar", "Ultra-Lujo", "Enfoque de Inversión", "Minimalista Moderno", "Vida Familiar", "Alquiler Vacacional", "Comercial"], "ph_prop": "Ej: Apartamento 3+1, Villa de Lujo...", "ph_price": "Ej: $850.000 o EUR 1.500/mes...", "ph_loc": "Ej: Madrid, España o Marbella...", "bedrooms": "Dormitorios", "bathrooms": "Baños", "area": "Área", "year_built": "Año de Construcción", "ph_beds": "Ej: 3", "ph_baths": "Ej: 2", "ph_area": "Ej: 185 m²", "ph_year": "Ej: 2022", "furnishing": "Amueblado", "furnishing_opts": ["No especificado", "Completamente Amueblado", "Semi-Amueblado", "Sin Amueblar"], "target_audience": "Público Objetivo", "audience_opts": ["Mercado General", "Compradores de Lujo", "Inversores & ROI", "Extranjeros & Internacionales", "Primeros Compradores", "Mercado Vacacional", "Inquilinos Comerciales"], "custom_inst": "Notas Especiales y Características", "custom_inst_ph": "Ej: Piscina privada, vistas al mar, domótica...", "btn": "GENERAR ACTIVOS SELECCIONADOS", "upload_label": "Subir Fotos de la Propiedad", "result": "Vista Previa Ejecutiva", "loading": "Creando su ecosistema de marketing premium...", "empty": "Esperando imágenes para análisis profesional. Suba fotos y complete los detalles a la izquierda.", "download": "Exportar Sección (TXT)", "save_btn": "Guardar Cambios", "saved_msg": "Guardado!", "error": "Error:", "clear_btn": "Limpiar Formulario", "select_sections": "Seleccionar Secciones a Generar", "tab_main": "Anuncio Premium", "tab_social": "Kit de Redes Sociales", "tab_video": "Guiones de Video", "tab_tech": "Especificaciones", "tab_email": "Campaña de Email", "tab_seo": "SEO & Web Copy", "tab_photo": "Guía de Fotos", "label_main": "Texto de Ventas", "label_social": "Contenido Social", "label_video": "Guion de Video", "label_tech": "Ficha Técnica", "label_email": "Campaña de Email", "label_seo": "SEO & Web Copy", "label_photo": "Recomendaciones de Fotografía", "extra_details": "Detalles Adicionales", "interface_lang": "Idioma de Interfaz", "logout": "Cerrar Sesión", "acc_settings": "Cuenta", "update_pw": "Actualizar Contraseña", "new_pw": "Nueva Contraseña", "btn_update": "Actualizar Ahora", "danger_zone": "Zona de Peligro", "delete_confirm": "Quiero eliminar mi cuenta permanentemente.", "btn_delete": "Eliminar Cuenta", "pw_min_err": "Mínimo 6 caracteres requeridos.", "delete_email_sent": "Email de confirmación enviado! Revisa tu bandeja de entrada.", "delete_email_fail": "Error al enviar email. Verifique la configuración SMTP." },
    "Deutsch": { "title": "SarSa AI | Immobilien-Intelligenz-Plattform", "service_desc": "All-in-One Visuelle Objektintelligenz & Globale Verkaufsautomatisierung", "subtitle": "Verwandeln Sie Fotos sofort in Premium-Exposés, Social-Media-Kits, Videoskripte, Datenblätter, E-Mail-Kampagnen und SEO-Texte.", "settings": "Konfiguration", "target_lang": "Erstellen in...", "prop_type": "Objekttyp", "price": "Marktpreis", "location": "Standort", "tone": "Marketingstrategie", "tones": ["Standard-Profi", "Ultra-Luxus", "Investitionsfokus", "Modern-Minimalistisch", "Familienleben", "Ferienmiete", "Gewerbe"], "ph_prop": "Z.B. 3-Zimmer-Wohnung, Luxusvilla...", "ph_price": "Z.B. 850.000€ oder 2.000€/Monat...", "ph_loc": "Z.B. Berlin, Deutschland oder Hamburg...", "bedrooms": "Schlafzimmer", "bathrooms": "Badezimmer", "area": "Fläche", "year_built": "Baujahr", "ph_beds": "Z.B. 3", "ph_baths": "Z.B. 2", "ph_area": "Z.B. 185 m²", "ph_year": "Z.B. 2022", "furnishing": "Möblierung", "furnishing_opts": ["Nicht angegeben", "Vollmöbliert", "Teilmöbliert", "Unmöbliert"], "target_audience": "Zielgruppe", "audience_opts": ["Allgemeiner Markt", "Luxuskäufer", "Investoren & ROI", "Expats & Internationale", "Erstkäufer", "Ferienmarkt", "Gewerbemieter"], "custom_inst": "Notizen & Besonderheiten", "custom_inst_ph": "Z.B. Privatpool, Panoramasicht, Smart-Home...", "btn": "AUSGEWÄHLTE ASSETS ERSTELLEN", "upload_label": "Fotos hier hochladen", "result": "Executive-Vorschau", "loading": "Ihr Marketing-Ökosystem wird erstellt...", "empty": "Warte auf Bilder für die Analyse. Laden Sie Fotos hoch und füllen Sie die Details aus.", "download": "Abschnitt Exportieren (TXT)", "save_btn": "Speichern", "saved_msg": "Gespeichert!", "error": "Fehler:", "clear_btn": "Formular Zurücksetzen", "select_sections": "Zu erstellende Bereiche wählen", "tab_main": "Premium-Exposé", "tab_social": "Social Media Kit", "tab_video": "Videoskripte", "tab_tech": "Tech-Details", "tab_email": "E-Mail-Kampagne", "tab_seo": "SEO & Webtext", "tab_photo": "Foto-Guide", "label_main": "Verkaufstext", "label_social": "Social-Media-Content", "label_video": "Videoskript", "label_tech": "Technische Daten", "label_email": "E-Mail-Kampagne", "label_seo": "SEO & Webtext", "label_photo": "Fotografie-Empfehlungen", "extra_details": "Weitere Details", "interface_lang": "Oberfläche Sprache", "logout": "Abmelden", "acc_settings": "Kontoeinstellungen", "update_pw": "Passwort ändern", "new_pw": "Neues Passwort", "btn_update": "Jetzt aktualisieren", "danger_zone": "Gefahrenzone", "delete_confirm": "Ich möchte mein Konto dauerhaft löschen.", "btn_delete": "Konto löschen", "pw_min_err": "Mindestens 6 Zeichen erforderlich.", "delete_email_sent": "Bestätigungs-E-Mail gesendet! Überprüfen Sie Ihren Posteingang.", "delete_email_fail": "E-Mail konnte nicht gesendet werden. SMTP-Einstellungen prüfen." },
    "Français": { "title": "SarSa AI | Plateforme d'Intelligence Immobilière", "service_desc": "Intelligence Visuelle Immobilière et Automatisation des Ventes Globales", "subtitle": "Transformez vos photos en annonces premium, kits réseaux sociaux, scripts vidéo, fiches techniques, campagnes email et copy SEO instantanément.", "settings": "Configuration", "target_lang": "Rédiger en...", "prop_type": "Type de Bien", "price": "Prix du Marché", "location": "Localisation", "tone": "Stratégie Marketing", "tones": ["Standard Pro", "Ultra-Luxe", "Focus Investissement", "Minimaliste Moderne", "Vie de Famille", "Location Saisonnière", "Commercial"], "ph_prop": "Ex: Appartement T4, Villa de Luxe...", "ph_price": "Ex: 850.000€ ou 1.500€/mois...", "ph_loc": "Ex: Paris, Côte d'Azur ou Lyon...", "bedrooms": "Chambres", "bathrooms": "Salles de Bain", "area": "Surface", "year_built": "Année de Construction", "ph_beds": "Ex: 3", "ph_baths": "Ex: 2", "ph_area": "Ex: 185 m²", "ph_year": "Ex: 2022", "furnishing": "Ameublement", "furnishing_opts": ["Non spécifié", "Entièrement Meublé", "Semi-Meublé", "Non Meublé"], "target_audience": "Audience Cible", "audience_opts": ["Marché Général", "Acheteurs de Luxe", "Investisseurs & ROI", "Expatriés & Internationaux", "Primo-Accédants", "Marché Vacances", "Locataires Commerciaux"], "custom_inst": "Notes Spéciales & Points Forts", "custom_inst_ph": "Ex: Piscine privée, vue panoramique, domotique...", "btn": "GÉNÉRER LES ACTIFS SÉLECTIONNÉS", "upload_label": "Déposer les Photos Ici", "result": "Aperçu Exécutif", "loading": "Préparation de votre écosystème marketing...", "empty": "En attente d'images pour analyse. Déposez des photos et remplissez les détails à gauche.", "download": "Exporter Section (TXT)", "save_btn": "Enregistrer", "saved_msg": "Enregistré!", "error": "Erreur:", "clear_btn": "Réinitialiser", "select_sections": "Sélectionner les sections à générer", "tab_main": "Annonce Premium", "tab_social": "Kit Réseaux Sociaux", "tab_video": "Scripts Vidéo", "tab_tech": "Spécifications", "tab_email": "Campagne Email", "tab_seo": "SEO & Web Copy", "tab_photo": "Guide Photo", "label_main": "Texte de Vente", "label_social": "Contenido Social", "label_video": "Script Vidéo", "label_tech": "Détails Techniques", "label_email": "Campagne Email", "label_seo": "SEO & Web Copy", "label_photo": "Recommandations Photographiques", "extra_details": "Détails Supplémentaires", "interface_lang": "Langue Interface", "logout": "Déconnexion", "acc_settings": "Paramètres", "update_pw": "Changer MDP", "new_pw": "Nouveau MDP", "btn_update": "Mettre à jour", "danger_zone": "Zone de Danger", "delete_confirm": "Supprimer définitivement mon compte.", "btn_delete": "Supprimer le compte", "pw_min_err": "6 caractères minimum.", "delete_email_sent": "Email de confirmation envoyé! Vérifiez votre boîte.", "delete_email_fail": "Echec d'envoi. Vérifiez les paramètres SMTP." },
    "Português": { "title": "SarSa AI | Plataforma de Inteligência Imobiliária", "service_desc": "Inteligência Visual Imobiliária e Automação de Vendas Globais", "subtitle": "Transforme fotos em anúncios premium, kits de redes sociais, roteiros de vídeo, fichas técnicas, campanhas de email e copy SEO instantaneamente.", "settings": "Configuração", "target_lang": "Escrever em...", "prop_type": "Tipo de Imóvel", "price": "Preço de Mercado", "location": "Localização", "tone": "Estratégia de Marketing", "tones": ["Profissional Padrão", "Ultra-Luxo", "Foco em Investimento", "Minimalista Moderno", "Vida Familiar", "Aluguel de Temporada", "Comercial"], "ph_prop": "Ex: Apartamento T3, Moradia de Luxo...", "ph_price": "Ex: 500.000€ ou 1.500€/mês...", "ph_loc": "Ex: Lisboa, Algarve ou Porto...", "bedrooms": "Quartos", "bathrooms": "Banheiros", "area": "Área", "year_built": "Ano de Construção", "ph_beds": "Ex: 3", "ph_baths": "Ex: 2", "ph_area": "Ex: 185 m²", "ph_year": "Ex: 2022", "furnishing": "Mobiliário", "furnishing_opts": ["Não especificado", "Completamente Mobilado", "Semi-Mobilado", "Sem Mobília"], "target_audience": "Público-Alvo", "audience_opts": ["Mercado Geral", "Compradores de Luxo", "Investidores & ROI", "Expats e Internacionais", "Primeiros Compradores", "Mercado de Férias", "Inquilinos Comerciais"], "custom_inst": "Notas Especiais e Destaques", "custom_inst_ph": "Ex: Piscina privativa, vista panorâmica, casa inteligente...", "btn": "GERAR ATIVOS SELECIONADOS", "upload_label": "Enviar Fotos do Imóvel", "result": "Pré-visualização Executiva", "loading": "Preparando seu ecossistema de marketing...", "empty": "Aguardando imagens para análise. Envie fotos e preencha os detalhes à esquerda.", "download": "Exportar Secção (TXT)", "save_btn": "Salvar Alterações", "saved_msg": "Salvo!", "error": "Erro:", "clear_btn": "Limpar Formulário", "select_sections": "Selecionar Seções a Gerar", "tab_main": "Anúncio Premium", "tab_social": "Kit Redes Sociais", "tab_video": "Roteiros de Vídeo", "tab_tech": "Especificações", "tab_email": "Campanha de Email", "tab_seo": "SEO & Web Copy", "tab_photo": "Guia de Fotos", "label_main": "Texto de Vendas", "label_social": "Conteúdo Social", "label_video": "Roteiro de Vídeo", "label_tech": "Especificações Técnicas", "label_email": "Campanha Email", "label_seo": "SEO & Web Copy", "label_photo": "Recomendações de Fotografia", "extra_details": "Detalhes Adicionais", "interface_lang": "Idioma Interface", "logout": "Sair", "acc_settings": "Configurações", "update_pw": "Alterar Senha", "new_pw": "Nova Senha", "btn_update": "Atualizar Agora", "danger_zone": "Zona de Perigo", "delete_confirm": "Quero excluir minha conta permanentemente.", "btn_delete": "Excluir Conta", "pw_min_err": "Mínimo de 6 caracteres.", "delete_email_sent": "Email de confirmação enviado! Verifique sua caixa de entrada.", "delete_email_fail": "Falha ao enviar email. Verifique as configurações SMTP." },
    "日本語": { "title": "SarSa AI | 不動産インテリジェンス・プラットフォーム", "service_desc": "オールインワン視覚的物件インテリジェンス＆グローバル販売自動化", "subtitle": "物件写真をプレミアム広告、SNSキット、動画台本、技術仕様書、メールキャンペーン、SEOコピーに瞬時に変換します。", "settings": "設定", "target_lang": "作成言語...", "prop_type": "物件種別", "price": "市場価格", "location": "所在地", "tone": "マーケティング戦略", "tones": ["標準プロ", "ウルトラ・ラグジュアリー", "投資重視", "モダン・ミニマリスト", "ファミリー向け", "バケーションレンタル", "商業用"], "ph_prop": "例: 3LDKマンション、高級別荘...", "ph_price": "例: 8500万円 または 月20万円...", "ph_loc": "例: 東京都港区、大阪、ドバイ...", "bedrooms": "寝室数", "bathrooms": "浴室数", "area": "面積", "year_built": "建築年", "ph_beds": "例: 3", "ph_baths": "例: 2", "ph_area": "例: 185 m²", "ph_year": "例: 2022", "furnishing": "家具", "furnishing_opts": ["未指定", "フル家具付き", "一部家具付き", "家具なし"], "target_audience": "ターゲット層", "audience_opts": ["一般市場", "富裕層バイヤー", "投資家 & ROI重視", "海外居住者", "初めての購入者", "休暇・別荘市場", "商業テナント"], "custom_inst": "特記事項 ＆ アピールポイント", "custom_inst_ph": "例: プライベートプール、パノラマビュー、スマートホーム...", "btn": "選択した資産を生成", "upload_label": "ここに物件写真をアップロード", "result": "エグゼクティブ・プレビュー", "loading": "プレミアム・マーケティング・エコシステムを構築中...", "empty": "分析用の画像を待機中。写真をアップロードし、左側に詳細を入力してください。", "download": "セクションを書き出し (TXT)", "save_btn": "変更を保存", "saved_msg": "保存完了！", "error": "エラー:", "clear_btn": "フォームをリセット", "select_sections": "生成するセクションを選択", "tab_main": "プレミアム広告", "tab_social": "SNSキット", "tab_video": "動画台本", "tab_tech": "技術仕様", "tab_email": "メールキャンペーン", "tab_seo": "SEO ＆ Webコピー", "tab_photo": "写真ガイド", "label_main": "セールスコピー", "label_social": "SNSコンテンツ", "label_video": "動画シナリオ", "label_tech": "技術詳細", "label_email": "メールキャンペーン", "label_seo": "SEOテキスト", "label_photo": "撮影のアドバイス", "extra_details": "物件詳細情報", "interface_lang": "インターフェース言語", "logout": "ログアウト", "acc_settings": "アカウント設定", "update_pw": "パスワード変更", "new_pw": "新しいパスワード", "btn_update": "今すぐ更新", "danger_zone": "危険区域", "delete_confirm": "アカウントを完全に削除します。", "btn_delete": "アカウント削除", "pw_min_err": "6文字以上必要です。", "delete_email_sent": "確認メールを送信しました！受信トレイを確認してください。", "delete_email_fail": "メールの送信に失敗しました。SMTP設定を確認してください。" },
    "简体中文": { "title": "SarSa AI | 房地产智能平台", "service_desc": "全方位房产视觉智能与全球销售自动化", "subtitle": "立即将房产照片转化为优质房源描述、社交媒体包、视频脚本、技术规格、邮件营销和 SEO 文案。", "settings": "配置", "target_lang": "编写语言...", "prop_type": "房产类型", "price": "市场价格", "location": "地点", "tone": "营销策略", "tones": ["标准专业", "顶级豪宅", "投资价值", "现代简约", "家庭生活", "度假租赁", "商业办公"], "ph_prop": "例如：3室1厅公寓、豪华别墅...", "ph_price": "例如：$850,000 或 $2,000/月...", "ph_loc": "例如：上海浦东新区、北京或伦敦...", "bedrooms": "卧室", "bathrooms": "卫生间", "area": "面积", "year_built": "建造年份", "ph_beds": "例如：3", "ph_baths": "例如：2", "ph_area": "例如：185 平方米", "ph_year": "例如：2022", "furnishing": "装修情况", "furnishing_opts": ["未指定", "精装修（含家具）", "简装修", "毛坯房"], "target_audience": "目标受众", "audience_opts": ["大众市场", "豪宅买家", "投资者 & 投资回报", "外籍人士", "首次购房者", "度假市场", "商业租客"], "custom_inst": "特别备注与亮点", "custom_inst_ph": "例如：私人泳池、全景海景、智能家居、临近国际学校...", "btn": "生成所选资产", "upload_label": "在此上传房产照片", "result": "高级预览", "loading": "正在打造您的专属营销生态系统...", "empty": "等待照片进行专业分析。请上传照片并在左侧填写详细信息。", "download": "导出此部分 (TXT)", "save_btn": "保存更改", "saved_msg": "已保存！", "error": "错误：", "clear_btn": "重置表单", "select_sections": "选择要生成的章节", "tab_main": "优质房源", "tab_social": "社媒包", "tab_video": "视频脚本", "tab_tech": "技术规格", "tab_email": "邮件营销", "tab_seo": "SEO 网页文案", "tab_photo": "拍摄指南", "label_main": "销售文案", "label_social": "社媒内容", "label_video": "视频脚本", "label_tech": "技术规格", "label_email": "邮件营销", "label_seo": "SEO 文案", "label_photo": "摄影建议", "extra_details": "额外房产细节", "interface_lang": "界面语言", "logout": "退出登录", "acc_settings": "账户设置", "update_pw": "更改密码", "new_pw": "新密码", "btn_update": "立即更新", "danger_zone": "危险区域", "delete_confirm": "我确认要永久删除我的账户。", "btn_delete": "删除账户", "pw_min_err": "密码至少需要6位。", "delete_email_sent": "确认邮件已发送！请检查您的收件箱。", "delete_email_fail": "发送邮件失败。请检查SMTP设置。" },
    "العربية": { "title": "SarSa AI | منصة الذكاء العقاري", "service_desc": "الذكاء البصري المتكامل للعقارات وأتمتة المبيعات العالمية", "subtitle": "حول صور العقارات فوراً إلى إعلانات مميزة، حقائب تواصل اجتماعي، سيناريوهات فيديو، مواصفات فنية، حملات بريدية ونصوص SEO.", "settings": "الإعدادات", "target_lang": "لغة الكتابة...", "prop_type": "نوع العقار", "price": "سعر السوق", "location": "الموقع", "tone": "استراتيجية التسويق", "tones": ["احترافي قياسي", "فخامة فائقة", "تركيز استثماري", "عصري بسيط", "حياة عائلية", "تأجير سياحي", "تجاري"], "ph_prop": "مثال: شقة 3+1، فيلا فاخرة...", "ph_price": "مثال: 850,000$ أو 2,500$ شهرياً...", "ph_loc": "مثال: دبي مارينا، الرياض، القاهرة...", "bedrooms": "غرف النوم", "bathrooms": "الحمامات", "area": "المساحة", "year_built": "سنة البناء", "ph_beds": "مثال: 3", "ph_baths": "مثال: 2", "ph_area": "مثال: 185 م²", "ph_year": "مثال: 2022", "furnishing": "حالة التأثيث", "furnishing_opts": ["غير محدد", "مفروش بالكامل", "مفروش جزئياً", "غير مفروش"], "target_audience": "الجمهور المستهدف", "audience_opts": ["السوق العام", "مشتري الفخامة", "المستثمرون", "المغتربون", "مشتري لأول مرة", "سوق العطلات", "مستأجر تجاري"], "custom_inst": "ملاحظات خاصة ومميزات", "custom_inst_ph": "مثال: مسبح خاص، إطلالة بانورامية، منزل ذكي...", "btn": "إنشاء الأصول المختارة", "upload_label": "ضع صور العقار هنا", "result": "معاينة تنفيذية", "loading": "جاري تجهيز منظومتك التسويقية الفاخرة...", "empty": "في انتظار الصور لبدء التحليل المهني. ارفع الصور واملأ التفاصيل على اليسار.", "download": "تصدير القسم (TXT)", "save_btn": "حفظ التغييرات", "saved_msg": "تم الحفظ!", "error": "خطأ:", "clear_btn": "إعادة تعيين", "select_sections": "اختر الأقسام المراد إنشاؤها", "tab_main": "الإعلان الرئيسي", "tab_social": "حقيبة التواصل", "tab_video": "سيناريو الفيديو", "tab_tech": "المواصفات الفنية", "tab_email": "حملة البريد", "tab_seo": "نصوص الويب وSEO", "tab_photo": "دليل التصوير", "label_main": "نص المبيعات", "label_social": "محتوى التواصل", "label_video": "سيناريو الفيديو", "label_tech": "المواصفات الفنية", "label_email": "حملة البريد الإلكتروني", "label_seo": "نص SEO", "label_photo": "توصيات التصوير الفوتوغرافي", "extra_details": "تفاصيل العقار الإضافية", "interface_lang": "لغة الواجهة", "logout": "تسجيل الخروج", "acc_settings": "إعدادات الحساب", "update_pw": "تحديث كلمة السر", "new_pw": "كلمة سر جديدة", "btn_update": "تحديث الآن", "danger_zone": "منطقة خطر", "delete_confirm": "أريد حذف حسابي نهائياً.", "btn_delete": "حذف الحساب", "pw_min_err": "يجب أن تكون 6 خانات على الأقل.", "delete_email_sent": "تم إرسال بريد التأكيد! تحقق من صندوق الوارد.", "delete_email_fail": "فشل إرسال البريد. تحقق من إعدادات SMTP." }
}

# ─── AUTH PAGE SHARED CSS ──────────────────────────────────────────────────────
_auth_page_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #f0f4f8 0%, #e8edf5 100%) !important; }
#MainMenu, footer, div[data-testid="stDecoration"] { display: none !important; }
.block-container { max-width: 560px !important; margin: 2.5rem auto !important;
    background: white; border-radius: 24px; padding: 3rem !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }
.stButton > button { background: #0f172a !important; color: white !important;
    border-radius: 12px !important; padding: 14px 24px !important;
    font-weight: 700 !important; font-size: 0.95rem !important; width: 100% !important;
    border: none !important; transition: all 0.25s ease !important;
    box-shadow: 0 4px 15px rgba(15,23,42,0.25) !important; }
.stButton > button:hover { background: #1e293b !important; transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(15,23,42,0.35) !important; }
</style>
"""

# ─── LANGUAGE HELPER FUNCTION ─────────────────────────────────────────────────
def update_lang_global(key):
    st.session_state.auth_lang = st.session_state[key]
    # Seçilen dili URL'e kaydet ki F5 yapılınca unutmasın
    st.query_params["lang"] = st.session_state.auth_lang

# ═══════════════════════════════════════════════════════════════════════════════
# ─── PAGE 1: EMAIL CONFIRMED — Dedicated full page ───────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.get('show_email_confirmed'):
    at = auth_texts.get(st.session_state.auth_lang, auth_texts["English"])
    st.markdown(_auth_page_css, unsafe_allow_html=True)

    st.selectbox(
        at.get("lang_select_label", "🌐 Select Language"),
        list(auth_texts.keys()),
        index=list(auth_texts.keys()).index(st.session_state.auth_lang) if st.session_state.auth_lang in auth_texts else 0,
        key="_lang_confirmed", on_change=update_lang_global, args=("_lang_confirmed",)
    )
    at = auth_texts.get(st.session_state.auth_lang, auth_texts["English"])

    st.markdown(f"""
    <div style="text-align:center; padding: 1.5rem 0 2rem;">
        <div style="font-size:5.5rem; line-height:1; margin-bottom:1.2rem;
                    filter: drop-shadow(0 4px 12px rgba(34,197,94,0.3));">✅</div>
        <h1 style="color:#0f172a; font-weight:800; font-size:2.2rem; margin:0 0 0.8rem;">
            {at.get("email_confirmed_title","✅ Email Verified Successfully!")}
        </h1>
        <p style="color:#475569; font-size:1.1rem; line-height:1.7; margin:0 0 0.5rem;">
            {at.get("email_confirmed_msg","Your account has been confirmed and is ready to use.")}
        </p>
        <p style="color:#94a3b8; font-size:0.95rem;">
            {at.get("email_confirmed_sub","Click the button below to go to the login page.")}
        </p>
    </div>
    <hr style="border:none; border-top:1px solid #f1f5f9; margin: 0 0 1.8rem;">
    """, unsafe_allow_html=True)

    if st.button(at.get("email_confirmed_btn", "🔑 Go to Login"), use_container_width=True):
        st.session_state.show_email_confirmed = False
        st.rerun()

    st.markdown("""
    <p style="text-align:center; color:#cbd5e1; font-size:0.8rem; margin-top:2rem;">
        SarSa AI | Real Estate Intelligence
    </p>""", unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# ─── PAGE 2: PASSWORD RECOVERY FORM (FIXED) ───────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.recovery_mode:
    _at_rec = auth_texts.get(st.session_state.auth_lang, auth_texts["English"])
    st.markdown(_auth_page_css, unsafe_allow_html=True)

    st.selectbox(
        _at_rec.get("lang_select_label", "🌐 Select Language"),
        list(auth_texts.keys()),
        index=list(auth_texts.keys()).index(st.session_state.auth_lang) if st.session_state.auth_lang in auth_texts else 0,
        key="_lang_recovery", on_change=update_lang_global, args=("_lang_recovery",)
    )
    _at_rec = auth_texts.get(st.session_state.auth_lang, auth_texts["English"])

    st.markdown(f"""
    <div style='text-align:center; padding:1rem 0 1.5rem;'>
      <div style='font-size:3.5rem; margin-bottom:0.6rem;'>🔒</div>
      <h1 style='color:#0f172a; font-weight:800; font-size:1.8rem; margin:0;'>
        {_at_rec.get("pw_reset_title","Set Your New Password")}
      </h1>
      <p style='color:#64748b; margin-top:0.6rem; font-size:0.97rem; line-height:1.6;'>
        {_at_rec.get("pw_reset_desc","Enter a new password for your account.")}
      </p>
    </div>
    <hr style="border:none; border-top:1px solid #f1f5f9; margin: 0 0 1.5rem;">
    """, unsafe_allow_html=True)

    with st.form("recovery_form"):
        new_password_recovery = st.text_input(
            _at_rec.get("new_pw_label", "New Password"),
            type="password", placeholder="••••••••"
        )
        col_sub, col_can = st.columns(2)
        with col_sub:
            submit_recovery = st.form_submit_button(
                _at_rec.get("pw_reset_btn", "✅ Set Password & Login"),
                use_container_width=True
            )
        with col_can:
            cancel_recovery = st.form_submit_button(
                _at_rec.get("pw_reset_cancel", "❌ Cancel"),
                use_container_width=True
            )

        if cancel_recovery:
            st.session_state.recovery_mode = False
            st.rerun()

        if submit_recovery:
            if len(new_password_recovery) < 6:
                st.error(_at_rec.get("pw_reset_min_err", "❌ Password must be at least 6 characters!"))
            else:
                try:
                    # 1. ÖNEMLİ: Önce session'ı manuel olarak tekrar doğrula
                    # Hem access_token hem de refresh_token kullanmalısın
                    access_token = st.session_state.get('access_token')
                    refresh_token = st.session_state.get('refresh_token')
                    
                    if access_token:
                        # Supabase'e bu tokenlarla oturum açtığını zorla söyle (JS'deki useEffect işi)
                        supabase.auth.set_session(access_token, refresh_token)
                        
                        # 2. Şimdi şifreyi güncelle
                        response = supabase.auth.update_user({"password": new_password_recovery})
                        
                        # Hata kontrolü (Supabase response içinde error dönebilir)
                        if hasattr(response, 'error') and response.error:
                            st.error(f"Hata: {response.error.message}")
                        else:
                            st.success(_at_rec.get("pw_reset_success", "✅ Password updated!"))
                            st.session_state.recovery_mode = False
                            st.session_state.is_logged_in = True
                            # Bilgileri güncelle
                            user_data = supabase.auth.get_user()
                            st.session_state.user_email = user_data.user.email
                            time.sleep(1.5)
                            st.rerun()
                    else:
                        st.error("Auth session missing. Please request a new reset link.")
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    if "invalid" in error_msg or "expired" in error_msg:
                        st.error("Technical Error: Link invalid or expired.")
                    else:
                        st.error(f"Update failed: {str(e)}")


# ─── AUTH FUNCTIONS ────────────────────────────────────────────────────────────
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
        st.session_state.user_email   = user.email
        return "paid", user.email
    except Exception:
        return "logged_out", None

auth_status, user_email = get_status()

# ─── CSS STYLING ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
.stApp { background-color: #f0f4f8 !important; }
div[data-testid="stInputInstructions"] { display: none !important; }
#MainMenu, footer { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
span[data-testid="stIconMaterial"] { font-family: "Material Symbols Rounded", "Material Icons" !important; }
button[kind="headerNoPadding"] { opacity: 1 !important; visibility: visible !important; display: block !important; }
section[data-testid="stSidebar"] + div + button { opacity: 1 !important; }
.block-container { background: white; padding: 2.5rem 3rem !important; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.06); margin-top: 1.5rem; border: 1px solid #e2e8f0; }
h1 { color: #0f172a !important; font-weight: 800 !important; text-align: center; }
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stSelectbox label { font-size: 0.74rem !important; font-weight: 700 !important; color: #64748b !important; text-transform: uppercase !important; letter-spacing: 0.7px !important; }
[data-testid="stSidebar"] .stTextInput input, [data-testid="stSidebar"] .stTextArea textarea { border-radius: 8px !important; border: 1.5px solid #e2e8f0 !important; background: #f8fafc !important; font-size: 0.875rem !important; transition: border-color 0.2s !important; }
.stButton > button { background: #0f172a !important; color: white !important; border-radius: 12px !important; padding: 14px 24px !important; font-weight: 700 !important; font-size: 0.95rem !important; width: 100% !important; border: none !important; transition: all 0.25s ease !important; box-shadow: 0 4px 15px rgba(15,23,42,0.3) !important; letter-spacing: 0.3px !important; }
.stButton > button:hover { background: #1e293b !important; box-shadow: 0 8px 25px rgba(15,23,42,0.4) !important; transform: translateY(-1px) !important; }
.stTabs [aria-selected="true"] { background-color: #0f172a !important; color: white !important; border-radius: 8px 8px 0 0 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_logo(file_path):
    if os.path.exists(file_path): return Image.open(file_path)
    return None

# ─── LOGIN / REGISTER SCREENS ─────────────────────────────────────────────────
if auth_status != "paid":
    at_temp = auth_texts.get(st.session_state.auth_lang, auth_texts["English"])
    st.selectbox(
        at_temp.get("lang_select_label", "🌐 Select Language"),
        list(auth_texts.keys()),
        index=list(auth_texts.keys()).index(st.session_state.auth_lang) if st.session_state.auth_lang in auth_texts else 0,
        key="lang_selector", on_change=update_lang_global, args=("lang_selector",)
    )
    at = auth_texts.get(st.session_state.auth_lang, auth_texts["English"])

    col_logo, col_text = st.columns([1, 6])
    with col_logo:
        logo_login = load_logo("SarSa_Logo_Transparent.png")
        if logo_login: st.image(logo_login, use_container_width=True)
    with col_text:
        st.markdown(f"<h1 style='text-align:left;color:#0f172a;font-weight:800;margin-top:0;padding-top:0;'>{at['welcome_title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.15rem;color:#475569;font-weight:500;margin-bottom:2rem;'>{at['welcome_desc']}</p>", unsafe_allow_html=True)

    st.markdown(f"<h3 style='text-align:center;color:#0f172a;margin-bottom:1.5rem;'>{at['login_prompt']}</h3>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([f"🔑 {at['login']}", f"📝 {at['register']}", f"❓ {at['forgot_pw']}"])

    with tab1:
        with st.form("login_form"):
            email_log = st.text_input(at["email"])
            pw_log    = st.text_input(at["password"], type="password")
            if st.form_submit_button(at["btn_login"]):
                try:
                    response = supabase.auth.sign_in_with_password({"email": email_log, "password": pw_log})
                    if response.session:
                        st.session_state.access_token  = response.session.access_token
                        st.session_state.refresh_token = response.session.refresh_token
                    st.session_state.is_logged_in = True
                    st.session_state.user_email   = response.user.email
                    st.rerun()
                except Exception as ex:
                    error_msg = str(ex)
                    if "Email not confirmed" in error_msg:
                        st.error(f"{at['verify_msg']} {email_log}")
                    elif "Invalid login credentials" in error_msg:
                        st.error(f"❌ {at['error_login']}")
                    else:
                        st.error(error_msg)

    with tab2:
        with st.form("register_form"):
            email_reg = st.text_input(at["email"])
            pw_reg    = st.text_input(at["password"] + " (Min 6)", type="password")
            if st.form_submit_button(at["btn_reg"]):
                try:
                    supabase.auth.sign_up({
                        "email": email_reg,
                        "password": pw_reg,
                        "options": {"email_redirect_to": "https://sarsa-ai-estateintelligence.streamlit.app/?action=signup_confirm"}
                    })
                    st.success(f"✅ {at['success_reg']}")
                except Exception as ex:
                    error_msg = str(ex)
                    if "User already registered" in error_msg:
                        st.error("This email is already registered. Please log in.")
                    else:
                        st.error(f"Error: {ex}")

    with tab3:
        with st.form("forgot_pw_form"):
            email_reset = st.text_input(at["email"], placeholder="your@email.com")
            if st.form_submit_button(at["btn_reset"]):
                email_reset = email_reset.strip()
                if not email_reset or "@" not in email_reset:
                    st.error(at.get("reset_invalid_email", "Please enter a valid email address."))
                else:
                    with st.spinner("Checking..."):
                        email_exists = is_email_registered(email_reset)
                    if not email_exists:
                        st.error(at.get("reset_not_found",
                            "No account found with this email address. Please register first."))
                    else:
                        try:
                            supabase.auth.reset_password_for_email(
                                email_reset,
                                {"redirect_to": "https://sarsa-ai-estateintelligence.streamlit.app/?action=reset_pw"}
                            )
                            st.success(f"✅ {at['reset_success']}")
                        except Exception as e:
                            st.error(f"Error: {e}")
    st.stop()

# ─── AI CONFIGURATION ─────────────────────────────────────────────────────────
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = 'gemini-2.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

# ─── SIDEBAR & ACCOUNT SETTINGS ───────────────────────────────────────────────
with st.sidebar:
    logo_img = load_logo("SarSa_Logo_Transparent.png")
    if logo_img:
        st.image(logo_img, use_container_width=True)
    else:
        st.markdown("<div style='text-align:center;padding:0.8rem 0 0.5rem;'><span style='font-size:1.8rem;font-weight:800;color:#0f172a;'>SarSa</span><span style='font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#3b82f6,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'> AI</span></div>", unsafe_allow_html=True)

    st.divider()
    
    at_side = auth_texts.get(st.session_state.auth_lang, auth_texts["English"])
    current_ui_lang = st.selectbox(
        at_side.get("lang_select_label", "🌐 Interface Language"),
        list(ui_languages.keys()),
        index=list(ui_languages.keys()).index(st.session_state.auth_lang) if st.session_state.auth_lang in ui_languages else 0,
        key="ui_lang_sidebar", on_change=update_lang_global, args=("ui_lang_sidebar",)
    )
    t = ui_languages[st.session_state.auth_lang]

    with st.expander(f"⚙️ {t['acc_settings']}"):
        st.write(st.session_state.user_email)
        st.subheader(t["update_pw"])
        new_pw = st.text_input(t["new_pw"], type="password", key="settings_new_pw")
        if st.button(t["btn_update"], key="settings_update_btn"):
            if len(new_pw) < 6:
                st.warning(t["pw_min_err"])
            else:
                try:
                    if st.session_state.access_token:
                        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
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
                    if st.session_state.access_token:
                        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
                    user_resp = supabase.auth.get_user()
                    if user_resp and user_resp.user:
                        u_id    = user_resp.user.id
                        u_email = user_resp.user.email
                        confirm_token = str(uuid.uuid4())
                        cancel_token  = str(uuid.uuid4())
                        expires_at    = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
                        supabase.table("pending_deletions").insert({
                            "user_id": u_id, "user_email": u_email,
                            "confirm_token": confirm_token, "cancel_token": cancel_token,
                            "expires_at": expires_at
                        }).execute()
                        sent, smtp_err = send_delete_confirmation_email(u_email, confirm_token, cancel_token)
                        if sent:
                            st.success(t.get("delete_email_sent", "Confirmation email sent!"))
                        else:
                            st.error(f"{t.get('delete_email_fail','Failed to send email.')} — {smtp_err}")
                    else:
                        st.error("Could not retrieve user. Please logout and log back in.")
                except Exception as e:
                    st.error(f"{t['error']} {e}")
            else:
                st.warning("Please confirm deletion.")

    if st.button(f"🚪 {t['logout']}", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.is_logged_in  = False
        st.session_state.user_email    = None
        st.session_state.access_token  = None
        st.session_state.refresh_token = None
        st.query_params.clear()
        st.rerun()

    st.markdown("---")
    st.header(t["settings"])

    st.session_state.target_lang_input = st.text_input(f"✍️ {t['target_lang']}", value=st.session_state.target_lang_input)
    st.session_state.prop_type = st.text_input(t["prop_type"], value=st.session_state.prop_type, placeholder=t["ph_prop"])
    st.session_state.price     = st.text_input(t["price"],     value=st.session_state.price,     placeholder=t["ph_price"])
    st.session_state.location  = st.text_input(t["location"],  value=st.session_state.location,  placeholder=t["ph_loc"])

    current_tone_idx = t["tones"].index(st.session_state.tone) if st.session_state.tone in t["tones"] else 0
    st.session_state.tone         = st.selectbox(t["tone"], t["tones"], index=current_tone_idx)
    st.session_state.audience_idx = st.selectbox(t["target_audience"], range(len(t["audience_opts"])), index=st.session_state.audience_idx, format_func=lambda x: t["audience_opts"][x])

    with st.expander(f"➕ {t['extra_details']}"):
        st.session_state.bedrooms       = st.text_input(t["bedrooms"],   value=st.session_state.bedrooms,   placeholder=t["ph_beds"])
        st.session_state.bathrooms      = st.text_input(t["bathrooms"],  value=st.session_state.bathrooms,  placeholder=t["ph_baths"])
        st.session_state.area_size      = st.text_input(t["area"],       value=st.session_state.area_size,  placeholder=t["ph_area"])
        st.session_state.year_built     = st.text_input(t["year_built"], value=st.session_state.year_built, placeholder=t["ph_year"])
        st.session_state.furnishing_idx = st.selectbox(t["furnishing"], range(len(t["furnishing_opts"])), index=st.session_state.furnishing_idx, format_func=lambda x: t["furnishing_opts"][x])

    st.session_state.custom_inst = st.text_area(f"📝 {t['custom_inst']}", value=st.session_state.custom_inst, placeholder=t["custom_inst_ph"], height=100)
    st.markdown("---")

    st.subheader(t["select_sections"])
    section_options = {
        t["tab_main"]:   "main",  t["tab_social"]: "social",
        t["tab_video"]:  "video", t["tab_tech"]:   "tech",
        t["tab_email"]:  "email", t["tab_seo"]:    "seo",
        t["tab_photo"]:  "photo"
    }
    st.session_state.selected_sections = st.multiselect(
        "Seçenekler:", options=list(section_options.keys()),
        default=list(section_options.keys()), label_visibility="collapsed"
    )

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
st.markdown(f"<h1 style='text-align:center;'>🏢 {t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;color:#64748b;font-size:1.1rem;margin-bottom:2rem;'>{t.get('subtitle',t['service_desc'])}</p>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(f"📸 {t['upload_label']}", type=["jpg","png","webp","jpeg"], accept_multiple_files=True)

if uploaded_files:
    images_for_ai = [Image.open(f) for f in uploaded_files]
    cols = st.columns(min(len(images_for_ai), 4))
    for i, img in enumerate(images_for_ai):
        with cols[i % 4]:
            st.image(img, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(f"🚀 {t.get('btn','GENERATE SELECTED ASSETS')}", use_container_width=True):
        if not st.session_state.selected_sections:
            st.warning("Please select at least one asset to generate from the sidebar.")
        else:
            with st.spinner(t.get('loading','Crafting your premium marketing ecosystem...')):
                st.success("Talebiniz AI'a iletildi! Seçtiğiniz alanlar için içerikler hazırlanıyor.")
            
            prompt_context = f"""
            Target Language: {st.session_state.target_lang_input}
            Property Type: {st.session_state.prop_type}
            Price: {st.session_state.price}
            Location: {st.session_state.location}
            Marketing Strategy/Tone: {st.session_state.tone}
            Target Audience: {t['audience_opts'][st.session_state.audience_idx]}
            Bedrooms: {st.session_state.bedrooms}
            Bathrooms: {st.session_state.bathrooms}
            Area: {st.session_state.area_size}
            Year Built: {st.session_state.year_built}
            Furnishing: {t['furnishing_opts'][st.session_state.furnishing_idx]}
            Special Notes: {st.session_state.custom_inst}
            """

            tabs = st.tabs(st.session_state.selected_sections)
            
            for idx, selected_tab in enumerate(st.session_state.selected_sections):
                with tabs[idx]:
                    st.subheader(selected_tab)
                    with st.spinner(f"AI is generating {selected_tab}..."):
                        specific_prompt = f"""
                        Based on the provided images and the following property details:
                        {prompt_context}
                        
                        Please generate a highly professional '{selected_tab}' for this real estate property. 
                        Write the final response entirely in {st.session_state.target_lang_input}. 
                        Make it engaging and strictly tailored to the requested marketing strategy and target audience.
                        """
                        try:
                            response = model.generate_content([specific_prompt] + images_for_ai)
                            generated_text = response.text
                            st.markdown(generated_text)
                            
                            st.download_button(
                                label=f"📥 {t['download']} - {selected_tab}", 
                                data=generated_text, 
                                file_name=f"SarSa_{selected_tab.replace(' ', '_')}.txt", 
                                key=f"dl_{idx}"
                            )
                        except Exception as e:
                            st.error(f"AI Generation Error: {e}")
else:
    st.markdown(f"""
    <div style='text-align:center;padding:3rem;background:#f8fafc;border-radius:12px;border:2px dashed #cbd5e1;margin-top:2rem;'>
      <h3 style='color:#475569;'>🏘️ {t.get('result','Executive Preview')}</h3>
      <p style='color:#94a3b8;'>{t['empty']}</p>
      <div style="display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:1.4rem;">
        <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">📝 {t['tab_main']}</span>
        <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">📱 {t['tab_social']}</span>
        <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">🎬 {t['tab_video']}</span>
        <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">⚙️ {t['tab_tech']}</span>
        <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">✉️ {t['tab_email']}</span>
        <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">🔍 {t['tab_seo']}</span>
        <span style="background:#f1f5f9;color:#475569;font-size:0.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;">📸 {t.get('tab_photo','Photo Guide')}</span>
      </div>
    </div>""", unsafe_allow_html=True)