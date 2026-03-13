import streamlit as st
import time
from PIL import Image
import google.generativeai as genai
import os
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Çerez (Cookie) yönetimi için (Sayfa yenilemelerinde hafıza)
try:
    import extra_streamlit_components as stx
except ImportError:
    stx = None
    st.warning("Gelişmiş hafıza (çerez) özellikleri için terminalde 'pip install extra-streamlit-components' çalıştırın.")

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SarSa AI | Real Estate Intelligence",
    page_icon="🏢", layout="wide"
)

@st.cache_resource(experimental_allow_widgets=True)
def get_cookie_manager():
    if stx is not None:
        return stx.CookieManager()
    return None

cookie_manager = get_cookie_manager()

# ─── SUPABASE ─────────────────────────────────────────────────────────────────
SUPABASE_URL: str = st.secrets["SUPABASE_URL"]
SUPABASE_KEY: str = st.secrets["SUPABASE_KEY"]
supabase: Client  = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── SESSION STATE & MEMORY ───────────────────────────────────────────────────
_defaults = {
    "auth_lang":            "English",
    "is_logged_in":         False,
    "user_email":           None,
    "recovery_mode":        False,
    "access_token":         None,
    "refresh_token":        None,
    "show_email_confirmed": False,
    "uretilen_ilan":"", "prop_type":"", "price":"",
    "location":"", "tone":"", "custom_inst":"",
    "target_lang_input":"English", "bedrooms":"",
    "bathrooms":"", "area_size":"", "year_built":"",
    "furnishing_idx":0, "audience_idx":0, "selected_sections":[],
}

for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Çerezlerden (Cookie) verileri al ve Session'a aktar (Sayfa Yenileme Koruması)
if cookie_manager:
    saved_lang = cookie_manager.get(cookie="sarsa_auth_lang")
    if saved_lang and saved_lang != st.session_state.auth_lang:
        st.session_state.auth_lang = saved_lang
    
    saved_access = cookie_manager.get(cookie="sarsa_access_token")
    saved_refresh = cookie_manager.get(cookie="sarsa_refresh_token")
    if saved_access and not st.session_state.access_token:
        st.session_state.access_token = saved_access
        st.session_state.refresh_token = saved_refresh

def save_auth_cookies(access, refresh):
    if cookie_manager:
        cookie_manager.set("sarsa_access_token", access, expires_at=datetime.now() + timedelta(days=7))
        cookie_manager.set("sarsa_refresh_token", refresh, expires_at=datetime.now() + timedelta(days=7))

def clear_auth_cookies():
    if cookie_manager:
        cookie_manager.delete("sarsa_access_token")
        cookie_manager.delete("sarsa_refresh_token")

# ─── RESTORE PERSISTENT SESSION ───────────────────────────────────────────────
if st.session_state.access_token and not st.session_state.is_logged_in:
    try:
        supabase.auth.set_session(
            st.session_state.access_token, st.session_state.refresh_token)
        _chk = supabase.auth.get_user()
        if _chk and _chk.user:
            st.session_state.is_logged_in = True
            st.session_state.user_email   = _chk.user.email
    except Exception:
        st.session_state.access_token  = None
        st.session_state.refresh_token = None
        st.session_state.is_logged_in  = False
        clear_auth_cookies()

# ─── EMAIL: ACCOUNT DELETION ──────────────────────────────────────────────────
def send_delete_confirmation_email(to_email, confirm_token, cancel_token):
    base = "https://sarsa-ai-estateintelligence.streamlit.app/"
    conf = f"{base}?action=confirm_delete&token={confirm_token}"
    canc = f"{base}?action=cancel_delete&token={cancel_token}"
    body = f"""
    <div style="font-family:Arial,sans-serif;max-width:620px;margin:0 auto;
                padding:30px;background:#f8fafc;border-radius:16px;">
      <div style="background:white;border-radius:12px;padding:36px;
                  box-shadow:0 4px 20px rgba(0,0,0,.07);">
        <h2 style="color:#0f172a;text-align:center;">⚠️ Account Deletion Request</h2>
        <p style="color:#64748b;text-align:center;font-size:14px;">SarSa AI | Real Estate Intelligence</p>
        <p style="color:#334155;font-size:16px;line-height:1.6;">
          Permanent deletion requested for:<br>
          <strong style="color:#0f172a;">{to_email}</strong></p>
        <p style="color:#ef4444;font-weight:600;">This action is irreversible.</p>
        <div style="text-align:center;margin:32px 0;">
          <a href="{conf}" style="background:#dc2626;color:white;padding:14px 32px;
             border-radius:10px;text-decoration:none;font-weight:700;
             display:inline-block;margin-bottom:14px;">Yes, Delete My Account</a><br>
          <a href="{canc}" style="background:#0f172a;color:white;padding:14px 32px;
             border-radius:10px;text-decoration:none;font-weight:700;
             display:inline-block;">Cancel – Keep My Account Safe</a>
        </div>
        <p style="color:#94a3b8;font-size:13px;text-align:center;">
          Expires in 24 hours. If you didn't request this, ignore this email.</p>
      </div>
    </div>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "SarSa AI – Confirm Account Deletion"
        msg["From"]    = st.secrets["SMTP_USER"]
        msg["To"]      = to_email
        msg.attach(MIMEText(body, "html"))
        host = st.secrets.get("SMTP_HOST","smtp.gmail.com")
        port = int(st.secrets.get("SMTP_PORT", 587))
        with smtplib.SMTP(host, port) as s:
            s.ehlo(); s.starttls()
            s.login(st.secrets["SMTP_USER"], st.secrets["SMTP_PASS"])
            s.sendmail(st.secrets["SMTP_USER"], to_email, msg.as_string())
        return True, ""
    except Exception as e:
        return False, str(e)

# ─── HELPER: email registered? ────────────────────────────────────────────────
def is_email_registered(email):
    try:
        svc   = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"])
        users = svc.auth.admin.list_users()
        return email.lower().strip() in [u.email.lower() for u in users if u.email]
    except Exception:
        return True

# ─── QUERY PARAMS (ROUTING) ───────────────────────────────────────────────────
qp = st.query_params

if qp.get("error"):
    error_msg = qp.get("error_description", qp.get("error"))
    st.error(f"⚠️ Verification Error: {error_msg}. The link may have expired.")
    st.query_params.clear()

if qp.get("action") == "confirm_delete":
    token = qp.get("token","")
    try:
        row = supabase.table("pending_deletions").select("*").eq("confirm_token",token).execute()
        if row.data:
            rec = row.data[0]
            exp = datetime.fromisoformat(rec["expires_at"].replace("Z","+00:00"))
            if datetime.now(timezone.utc) < exp:
                try:
                    svc = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"])
                    svc.auth.admin.delete_user(rec["user_id"])
                except Exception as e:
                    st.error(f"Deletion error: {e}"); st.stop()
                supabase.table("pending_deletions").delete().eq("confirm_token",token).execute()
                for k in ["is_logged_in","user_email","access_token","refresh_token"]:
                    st.session_state[k] = False if k=="is_logged_in" else None
                clear_auth_cookies()
                st.query_params.clear()
                st.markdown("""<div style='text-align:center;padding:5rem 2rem;'>
                  <div style='font-size:5rem;'>👋</div>
                  <h1 style='color:#0f172a;font-weight:800;'>Account Deleted</h1>
                  <p style='color:#475569;font-size:1.15rem;line-height:1.7;margin-top:1rem;'>
                    Your SarSa AI account has been <strong>permanently deleted</strong>.<br>
                    All data removed.</p>
                  <p style='color:#94a3b8;margin-top:2rem;'>You have been logged out.</p>
                </div>""", unsafe_allow_html=True)
                st.stop()
            else:
                st.error("Link expired (24h). Please request deletion again."); st.stop()
        else:
            st.error("Invalid or already-used link."); st.stop()
    except Exception as e:
        st.error(f"Error: {e}"); st.stop()

if qp.get("action") == "cancel_delete":
    try:
        supabase.table("pending_deletions").delete().eq("cancel_token",qp.get("token","")).execute()
    except Exception:
        pass
    st.query_params.clear()
    st.success("Account deletion cancelled. Your account is safe! ✅")
    time.sleep(2); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PKCE ?code= HANDLER — (TAMAMEN YENİLENMİŞ VE DROPPIN EKLENMİŞ BLOK)
# ══════════════════════════════════════════════════════════════════════════════
if qp.get("code"):
    code = qp.get("code")
    flow_type = qp.get("type", "recovery")

    try:
        # Koddan token alımı (explicit single-arg form)
        resp = supabase.auth.exchange_code_for_session(code)
    except Exception as e:
        st.error(f"Auth exchange failed (Link expired or used): {e}")
        st.query_params.clear()
        time.sleep(2)
        st.rerun()

    access_token = None
    refresh_token = None
    try:
        if isinstance(resp, dict):
            sess = resp.get("data", {}).get("session") or resp.get("session") or resp.get("data")
            if isinstance(sess, dict):
                access_token = sess.get("access_token") or sess.get("accessToken")
                refresh_token = sess.get("refresh_token") or sess.get("refreshToken")
        else:
            sess = getattr(resp, "session", None) or resp
            access_token = getattr(sess, "access_token", None) or getattr(sess, "accessToken", None)
            refresh_token = getattr(sess, "refresh_token", None) or getattr(sess, "refreshToken", None)
    except Exception:
        pass

    if access_token:
        try:
            supabase.auth.set_session(access_token, refresh_token)
            st.session_state.access_token = access_token
            st.session_state.refresh_token = refresh_token
            save_auth_cookies(access_token, refresh_token)
        except Exception as e:
            st.error(f"Could not set session after exchange: {e}")
            st.query_params.clear()
            st.stop()
    else:
        try:
            gs = supabase.auth.get_session()
            if isinstance(gs, dict):
                sess = gs.get("data", {}).get("session") or gs.get("session") or gs.get("data")
                if isinstance(sess, dict):
                    st.session_state.access_token = sess.get("access_token")
                    st.session_state.refresh_token = sess.get("refresh_token")
            else:
                st.session_state.access_token = getattr(gs, "access_token", None) or getattr(gs, "accessToken", None)
                st.session_state.refresh_token = getattr(gs, "refresh_token", None) or getattr(gs, "refreshToken", None)
        except Exception:
            pass

    st.query_params.clear()

    # Yönlendirmeyi burada state üzerinden yapıyoruz
    if flow_type == "signup":
        st.session_state.show_email_confirmed = True
        st.rerun()
    else:
        st.session_state.recovery_mode = True
        if st.session_state.access_token:
            st.session_state.is_logged_in = True
        st.rerun()

# ─── TEXT DICTS ───────────────────────────────────────────────────────────────
# (Tüm dillerin buradadır, eksiltilmemiştir)
auth_texts = {
    "English": {
        "login":"Login","register":"Register","email":"Email","password":"Password",
        "btn_login":"Login","btn_reg":"Create Account",
        "success_reg":"Registration successful! Check your email to verify your account.",
        "error_login":"Login failed. You are not registered, or your Email/Password is incorrect.",
        "verify_msg":"Please verify your email first:",
        "welcome_title":"Welcome to SarSa AI",
        "welcome_desc":"The All-in-One Visual Property Intelligence & Global Sales Automation platform. Transform your property photos into professional assets in seconds.",
        "login_prompt":"Log in to use the application",
        "forgot_pw":"Forgot Password?","btn_reset":"Send Reset Link",
        "reset_success":"Password reset link sent! Check your inbox.",
        "reset_not_found":"No account found with this email. Please register first.",
        "reset_invalid_email":"Please enter a valid email address.",
        "confirmed_title":"✅ Email Verified Successfully!",
        "confirmed_msg":"Your SarSa AI account has been confirmed and is ready to use.",
        "confirmed_sub":"Click the button below to proceed to the login page.",
        "confirmed_btn":"🔑 Go to Login",
        "pw_reset_title":"Set Your New Password",
        "pw_reset_desc":"Enter a new password for your account. You will be logged in automatically after saving.",
        "pw_reset_btn":"✅ Save Password & Login",
        "pw_reset_cancel":"❌ Cancel",
        "pw_reset_success":"✅ Password updated! Logging you in…",
        "pw_reset_min_err":"❌ Password must be at least 6 characters.",
        "new_pw_label":"New Password",
    },
    "Türkçe": {
        "login":"Giriş Yap","register":"Kayıt Ol","email":"E-posta","password":"Şifre",
        "btn_login":"Oturum Aç","btn_reg":"Hesap Oluştur",
        "success_reg":"Kayıt başarılı! Hesabınızı onaylamak için e-postanızı kontrol edin.",
        "error_login":"Giriş başarısız. Kayıtlı değilsiniz veya E-posta/Şifreniz hatalı.",
        "verify_msg":"Lütfen önce e-postanızı onaylayın:",
        "welcome_title":"SarSa AI'a Hoş Geldiniz",
        "welcome_desc":"Hepsi Bir Arada Görsel Mülk Zekâsı ve Küresel Satış Otomasyonu platformu. Mülk fotoğraflarınızı saniyeler içinde profesyonel varlıklara dönüştürün.",
        "login_prompt":"Uygulamayı kullanmak için giriş yapın",
        "forgot_pw":"Şifremi Unuttum?","btn_reset":"Sıfırlama Bağlantısı Gönder",
        "reset_success":"Şifre sıfırlama bağlantısı gönderildi! Gelen kutunuzu kontrol edin.",
        "reset_not_found":"Bu e-posta ile kayıtlı hesap bulunamadı. Lütfen önce kayıt olun.",
        "reset_invalid_email":"Lütfen geçerli bir e-posta adresi girin.",
        "confirmed_title":"✅ E-posta Başarıyla Doğrulandı!",
        "confirmed_msg":"SarSa AI hesabınız onaylandı ve kullanıma hazır.",
        "confirmed_sub":"Giriş sayfasına geçmek için aşağıdaki butona tıklayın.",
        "confirmed_btn":"🔑 Giriş Sayfasına Git",
        "pw_reset_title":"Yeni Şifrenizi Belirleyin",
        "pw_reset_desc":"Hesabınız için yeni bir şifre girin. Kaydettikten sonra otomatik giriş yapılacak.",
        "pw_reset_btn":"✅ Şifreyi Kaydet ve Giriş Yap",
        "pw_reset_cancel":"❌ İptal",
        "pw_reset_success":"✅ Şifre güncellendi! Giriş yapılıyor…",
        "pw_reset_min_err":"❌ Şifre en az 6 karakter olmalıdır.",
        "new_pw_label":"Yeni Şifre",
    },
    "Español": {
        "login":"Iniciar Sesión","register":"Registrarse","email":"Correo","password":"Clave",
        "btn_login":"Entrar","btn_reg":"Crear Cuenta",
        "success_reg":"¡Registro exitoso! Revisa tu email para verificar tu cuenta.",
        "error_login":"Error. No estás registrado o tu Correo/Clave es incorrecto.",
        "verify_msg":"Por favor verifica tu email primero:",
        "welcome_title":"Bienvenido a SarSa AI",
        "welcome_desc":"La plataforma todo en uno de Inteligencia Visual de Propiedades. Transforme sus fotos en activos profesionales en segundos.",
        "login_prompt":"Inicie sesión para usar la aplicación",
        "forgot_pw":"¿Olvidaste tu contraseña?","btn_reset":"Enviar enlace",
        "reset_success":"¡Enlace enviado! Revisa tu bandeja de entrada.",
        "reset_not_found":"No se encontró ninguna cuenta con este correo.",
        "reset_invalid_email":"Por favor ingresa un correo válido.",
        "confirmed_title":"✅ ¡Email Verificado Exitosamente!",
        "confirmed_msg":"Tu cuenta de SarSa AI ha sido confirmada y está lista para usar.",
        "confirmed_sub":"Haz clic abajo para ir a la página de inicio de sesión.",
        "confirmed_btn":"🔑 Ir al Login",
        "pw_reset_title":"Establece tu Nueva Contraseña",
        "pw_reset_desc":"Ingresa una nueva contraseña. Iniciarás sesión automáticamente al guardar.",
        "pw_reset_btn":"✅ Guardar Contraseña e Iniciar Sesión",
        "pw_reset_cancel":"❌ Cancelar",
        "pw_reset_success":"✅ ¡Contraseña actualizada! Iniciando sesión…",
        "pw_reset_min_err":"❌ Mínimo 6 caracteres requeridos.",
        "new_pw_label":"Nueva Contraseña",
    },
    "Deutsch": {
        "login":"Anmelden","register":"Registrieren","email":"E-Mail","password":"Passwort",
        "btn_login":"Login","btn_reg":"Konto Erstellen",
        "success_reg":"Erfolgreich! Bitte bestätigen Sie Ihre E-Mail.",
        "error_login":"Login fehlgeschlagen. Nicht registriert oder E-Mail/Passwort falsch.",
        "verify_msg":"Bitte bestätigen Sie zuerst Ihre E-Mail:",
        "welcome_title":"Willkommen bei SarSa AI",
        "welcome_desc":"Die All-in-One-Plattform für visuelle Immobilienintelligenz. Verwandeln Sie Fotos in Sekundenschnelle in professionelle Assets.",
        "login_prompt":"Melden Sie sich an, um die App zu nutzen",
        "forgot_pw":"Passwort vergessen?","btn_reset":"Link senden",
        "reset_success":"Link gesendet! Überprüfen Sie Ihren Posteingang.",
        "reset_not_found":"Kein Konto mit dieser E-Mail gefunden.",
        "reset_invalid_email":"Bitte gültige E-Mail-Adresse eingeben.",
        "confirmed_title":"✅ E-Mail erfolgreich verifiziert!",
        "confirmed_msg":"Ihr SarSa AI-Konto wurde bestätigt und ist einsatzbereit.",
        "confirmed_sub":"Klicken Sie unten, um zur Anmeldeseite zu gelangen.",
        "confirmed_btn":"🔑 Zur Anmeldung",
        "pw_reset_title":"Neues Passwort festlegen",
        "pw_reset_desc":"Geben Sie ein neues Passwort ein. Sie werden automatisch eingeloggt.",
        "pw_reset_btn":"✅ Passwort speichern & einloggen",
        "pw_reset_cancel":"❌ Abbrechen",
        "pw_reset_success":"✅ Passwort aktualisiert! Einloggen…",
        "pw_reset_min_err":"❌ Mindestens 6 Zeichen erforderlich.",
        "new_pw_label":"Neues Passwort",
    },
    "Français": {
        "login":"Connexion","register":"S'inscrire","email":"Email","password":"Mot de passe",
        "btn_login":"Se connecter","btn_reg":"Créer un compte",
        "success_reg":"Succès ! Vérifiez vos emails pour confirmer.",
        "error_login":"Échec. Vous n'êtes pas inscrit ou Email/Mot de passe incorrect.",
        "verify_msg":"Veuillez d'abord vérifier votre email :",
        "welcome_title":"Bienvenue sur SarSa AI",
        "welcome_desc":"La plateforme d'Intelligence Visuelle Immobilière. Transformez vos photos en atouts professionnels en quelques secondes.",
        "login_prompt":"Connectez-vous pour utiliser l'application",
        "forgot_pw":"Mot de passe oublié ?","btn_reset":"Envoyer le lien",
        "reset_success":"Lien envoyé ! Vérifiez votre boîte de réception.",
        "reset_not_found":"Aucun compte trouvé avec cet email.",
        "reset_invalid_email":"Veuillez entrer une adresse email valide.",
        "confirmed_title":"✅ Email vérifié avec succès !",
        "confirmed_msg":"Votre compte SarSa AI a été confirmé et est prêt à l'emploi.",
        "confirmed_sub":"Cliquez ci-dessous pour accéder à la page de connexion.",
        "confirmed_btn":"🔑 Aller à la connexion",
        "pw_reset_title":"Définissez votre nouveau mot de passe",
        "pw_reset_desc":"Entrez un nouveau mot de passe. Vous serez connecté automatiquement après.",
        "pw_reset_btn":"✅ Enregistrer & Se connecter",
        "pw_reset_cancel":"❌ Annuler",
        "pw_reset_success":"✅ Mot de passe mis à jour ! Connexion en cours…",
        "pw_reset_min_err":"❌ 6 caractères minimum.",
        "new_pw_label":"Nouveau mot de passe",
    },
    "Português": {
        "login":"Entrar","register":"Registar","email":"Email","password":"Senha",
        "btn_login":"Login","btn_reg":"Criar Conta",
        "success_reg":"Sucesso! Verifique seu email para confirmar a conta.",
        "error_login":"Falha. Não registado ou Email/Senha incorretos.",
        "verify_msg":"Por favor verifique primeiro o seu email:",
        "welcome_title":"Bem-vindo ao SarSa AI",
        "welcome_desc":"A plataforma tudo-em-um de Inteligência Imobiliária Visual. Transforme as suas fotos em ativos profissionais em segundos.",
        "login_prompt":"Faça login para usar o aplicativo",
        "forgot_pw":"Esqueceu a senha?","btn_reset":"Enviar link",
        "reset_success":"Link enviado! Verifique sua caixa de entrada.",
        "reset_not_found":"Nenhuma conta encontrada com este email.",
        "reset_invalid_email":"Por favor insira um endereço de email válido.",
        "confirmed_title":"✅ Email Verificado com Sucesso!",
        "confirmed_msg":"Sua conta SarSa AI foi confirmada e está pronta para uso.",
        "confirmed_sub":"Clique abaixo para ir à página de login e começar.",
        "confirmed_btn":"🔑 Ir para o Login",
        "pw_reset_title":"Defina sua Nova Senha",
        "pw_reset_desc":"Insira uma nova senha. Você será logado automaticamente após salvar.",
        "pw_reset_btn":"✅ Salvar Senha & Entrar",
        "pw_reset_cancel":"❌ Cancelar",
        "pw_reset_success":"✅ Senha atualizada! Entrando…",
        "pw_reset_min_err":"❌ Mínimo de 6 caracteres.",
        "new_pw_label":"Nova Senha",
    },
    "日本語": {
        "login":"ログイン","register":"新規登録","email":"メール","password":"パスワード",
        "btn_login":"ログイン","btn_reg":"アカウント作成",
        "success_reg":"登録完了！メールを確認してアカウントを認証してください。",
        "error_login":"ログイン失敗。未登録か、メール/パスワードが間違っています。",
        "verify_msg":"まずメールを認証してください：",
        "welcome_title":"SarSa AI へようこそ",
        "welcome_desc":"オールインワンの視覚的物件インテリジェンス＆販売自動化プラットフォーム。物件の写真を数秒でプロフェッショナルな資産に変換します。",
        "login_prompt":"アプリを使用するにはログインしてください",
        "forgot_pw":"パスワードをお忘れですか？","btn_reset":"リンクを送信",
        "reset_success":"リセットリンクを送信しました！受信トレイをご確認ください。",
        "reset_not_found":"このメールアドレスのアカウントが見つかりません。",
        "reset_invalid_email":"有効なメールアドレスを入力してください。",
        "confirmed_title":"✅ メールが正常に認証されました！",
        "confirmed_msg":"SarSa AI アカウントが確認され、ご利用いただけます。",
        "confirmed_sub":"下のボタンをクリックしてログインページに移動してください。",
        "confirmed_btn":"🔑 ログインページへ",
        "pw_reset_title":"新しいパスワードを設定",
        "pw_reset_desc":"新しいパスワードを入力してください。保存後に自動的にログインされます。",
        "pw_reset_btn":"✅ パスワードを保存してログイン",
        "pw_reset_cancel":"❌ キャンセル",
        "pw_reset_success":"✅ パスワードが更新されました！ログイン中…",
        "pw_reset_min_err":"❌ 6文字以上必要です。",
        "new_pw_label":"新しいパスワード",
    },
    "简体中文": {
        "login":"登录","register":"注册","email":"邮箱","password":"密码",
        "btn_login":"登录","btn_reg":"创建账号",
        "success_reg":"注册成功！请检查邮箱以验证账号。",
        "error_login":"登录失败。您未注册，或邮箱/密码错误。",
        "verify_msg":"请先验证您的邮箱：",
        "welcome_title":"欢迎来到 SarSa AI",
        "welcome_desc":"全方位房产视觉智能与全球销售自动化平台。在几秒钟内将您的房产照片转化为专业的营销资产。",
        "login_prompt":"登录以使用该应用程序",
        "forgot_pw":"忘记密码？","btn_reset":"发送重置链接",
        "reset_success":"重置链接已发送！请检查您的邮箱。",
        "reset_not_found":"未找到使用此邮箱注册的账号，请先注册。",
        "reset_invalid_email":"请输入有效的电子邮件地址。",
        "confirmed_title":"✅ 邮箱验证成功！",
        "confirmed_msg":"您的 SarSa AI 账户已确认，可以开始使用。",
        "confirmed_sub":"点击下方按钮前往登录页面开始使用。",
        "confirmed_btn":"🔑 前往登录",
        "pw_reset_title":"设置您的新密码",
        "pw_reset_desc":"为您的账号输入新密码。保存后将自动登录。",
        "pw_reset_btn":"✅ 保存密码并登录",
        "pw_reset_cancel":"❌ 取消",
        "pw_reset_success":"✅ 密码已更新！正在登录…",
        "pw_reset_min_err":"❌ 密码至少需要6位。",
        "new_pw_label":"新密码",
    },
    "العربية": {
        "login":"تسجيل الدخول","register":"إنشاء حساب","email":"البريد","password":"كلمة السر",
        "btn_login":"دخول","btn_reg":"إنشاء حساب",
        "success_reg":"تم التسجيل بنجاح! تحقق من بريدك لتأكيد الحساب.",
        "error_login":"فشل الدخول. أنت غير مسجل، أو البريد/كلمة السر خاطئة.",
        "verify_msg":"يرجى تأكيد بريدك الإلكتروني أولاً:",
        "welcome_title":"مرحباً بك في SarSa AI",
        "welcome_desc":"منصة الذكاء البصري المتكامل للعقارات وأتمتة المبيعات العالمية. حول صور عقاراتك إلى أصول احترافية في ثوانٍ.",
        "login_prompt":"قم بتسجيل الدخول لاستخدام التطبيق",
        "forgot_pw":"نسيت كلمة السر؟","btn_reset":"إرسال رابط الاستعادة",
        "reset_success":"تم إرسال رابط إعادة التعيين! تحقق من صندوق الوارد.",
        "reset_not_found":"لم يتم العثور على حساب بهذا البريد.",
        "reset_invalid_email":"يرجى إدخال عنوان بريد إلكتروني صالح.",
        "confirmed_title":"✅ تم التحقق من البريد بنجاح!",
        "confirmed_msg":"تم تأكيد حساب SarSa AI الخاص بك وهو جاهز للاستخدام.",
        "confirmed_sub":"انقر على الزر أدناه للانتقال إلى صفحة تسجيل الدخول.",
        "confirmed_btn":"🔑 الذهاب إلى تسجيل الدخول",
        "pw_reset_title":"تعيين كلمة المرور الجديدة",
        "pw_reset_desc":"أدخل كلمة مرور جديدة لحسابك. سيتم تسجيل دخولك تلقائياً بعد الحفظ.",
        "pw_reset_btn":"✅ حفظ كلمة المرور وتسجيل الدخول",
        "pw_reset_cancel":"❌ إلغاء",
        "pw_reset_success":"✅ تم تحديث كلمة المرور! جاري تسجيل الدخول…",
        "pw_reset_min_err":"❌ يجب أن تكون 6 خانات على الأقل.",
        "new_pw_label":"كلمة المرور الجديدة",
    },
}

ui_languages = {
    "English": {
        "title":"SarSa AI | Real Estate Intelligence Platform",
        "service_desc":"All-in-One Visual Property Intelligence & Global Sales Automation",
        "subtitle":"Transform property photos into premium listings, social media kits, cinematic video scripts, technical specs, email campaigns and SEO copy — instantly.",
        "settings":"Configuration","target_lang":"Write Listing In…","prop_type":"Property Type",
        "price":"Market Price","location":"Location","tone":"Marketing Strategy",
        "tones":["Standard Pro","Ultra-Luxury","Investment Focus","Modern Minimalist","Family Living","Vacation Rental","Commercial"],
        "ph_prop":"E.g., 3+1 Apartment, Luxury Villa…","ph_price":"E.g., $850,000 or £2,000/mo…",
        "ph_loc":"E.g., Manhattan, NY or Dubai Marina…","bedrooms":"Bedrooms","bathrooms":"Bathrooms",
        "area":"Area","year_built":"Year Built","ph_beds":"E.g., 3","ph_baths":"E.g., 2",
        "ph_area":"E.g., 185 sqm","ph_year":"E.g., 2022","furnishing":"Furnishing",
        "furnishing_opts":["Not Specified","Fully Furnished","Semi-Furnished","Unfurnished"],
        "target_audience":"Target Audience",
        "audience_opts":["General Market","Luxury Buyers","Investors & ROI Focus","Expats & Internationals","First-Time Buyers","Vacation / Holiday Market","Commercial Tenants"],
        "custom_inst":"Special Notes & Highlights","custom_inst_ph":"E.g., Private pool, panoramic sea view, smart home…",
        "btn":"GENERATE SELECTED ASSETS","upload_label":"Drop Property Photos Here",
        "result":"Executive Preview","loading":"Crafting your premium marketing ecosystem…",
        "empty":"Upload property photos and fill in the details on the left to generate complete professional marketing assets.",
        "download":"Export Section (TXT)","save_btn":"Save Changes","saved_msg":"Saved!",
        "error":"Error:","clear_btn":"Reset Form","select_sections":"Select Assets to Generate",
        "tab_main":"Prime Listing","tab_social":"Social Media Kit","tab_video":"Video Scripts",
        "tab_tech":"Technical Specs","tab_email":"Email Campaign","tab_seo":"SEO & Web Copy","tab_photo":"Photo Guide",
        "label_main":"Sales Copy","label_social":"Social Media Content","label_video":"Video Script",
        "label_tech":"Technical Specifications","label_email":"Email Campaign","label_seo":"SEO & Web Copy",
        "label_photo":"Photography Recommendations","extra_details":"Extra Property Details",
        "interface_lang":"Interface Language","logout":"Logout","acc_settings":"Account Settings",
        "update_pw":"Update Password","new_pw":"New Password","btn_update":"Update Now",
        "danger_zone":"Danger Zone","delete_confirm":"I want to permanently delete my account.",
        "btn_delete":"Delete Account","pw_min_err":"Minimum 6 characters required.",
        "delete_email_sent":"Confirmation email sent! Check your inbox.",
        "delete_email_fail":"Failed to send email. Please check SMTP settings.",
    },
    "Türkçe": {
        "title":"SarSa AI | Gayrimenkul Zekâ Platformu",
        "service_desc":"Hepsi Bir Arada Görsel Mülk Zekâsı ve Küresel Satış Otomasyonu",
        "subtitle":"Mülk fotoğraflarını anında profesyonel ilanlara, sosyal medya kitlerine, sinematik senaryolara, teknik şartnamelere, e-posta kampanyalarına ve SEO metinlerine dönüştürün.",
        "settings":"Yapılandırma","target_lang":"İlan Yazım Dili…","prop_type":"Emlak Tipi",
        "price":"Pazar Fiyatı","location":"Konum","tone":"Pazarlama Stratejisi",
        "tones":["Standart Profesyonel","Ultra-Lüks","Yatırım Odaklı","Modern Minimalist","Aile Yaşamı","Tatil Kiralık","Ticari"],
        "ph_prop":"Örn: 3+1 Daire, Müstakil Villa…","ph_price":"Örn: 5.000.000 TL veya $2.500/ay…",
        "ph_loc":"Örn: Beşiktaş, İstanbul veya Dubai Marina…","bedrooms":"Yatak Odası","bathrooms":"Banyo",
        "area":"Alan","year_built":"İnşaat Yılı","ph_beds":"Örn: 3","ph_baths":"Örn: 2",
        "ph_area":"Örn: 185 m²","ph_year":"Örn: 2022","furnishing":"Eşya Durumu",
        "furnishing_opts":["Belirtilmedi","Tam Eşyalı","Yarı Eşyalı","Eşyasız"],
        "target_audience":"Hedef Kitle",
        "audience_opts":["Genel Pazar","Lüks Alıcılar","Yatırımcılar & ROI Odaklı","Yabancılar & Uluslararası","İlk Ev Alıcıları","Tatil / Kiralık Pazar","Ticari Kiracılar"],
        "custom_inst":"Özel Notlar ve Öne Çıkan Özellikler","custom_inst_ph":"Örn: Özel havuz, panoramik manzara, akıllı ev…",
        "btn":"SEÇİLİ VARLIKLARI OLUŞTUR","upload_label":"Fotoğrafları Buraya Bırakın",
        "result":"Yönetici Önizlemesi","loading":"Premium pazarlama ekosisteminiz hazırlanıyor…",
        "empty":"Profesyonel analiz için görsel bekleniyor. Fotoğrafları yükleyin ve soldaki bilgileri doldurun.",
        "download":"Bölümü İndir (TXT)","save_btn":"Kaydet","saved_msg":"Kaydedildi!",
        "error":"Hata:","clear_btn":"Formu Temizle","select_sections":"Oluşturulacak Bölümleri Seçin",
        "tab_main":"Ana İlan","tab_social":"Sosyal Medya Kiti","tab_video":"Video Senaryoları",
        "tab_tech":"Teknik Özellikler","tab_email":"E-posta Kampanyası","tab_seo":"SEO & Web Metni","tab_photo":"Fotoğraf Rehberi",
        "label_main":"Satış Metni","label_social":"Sosyal Medya","label_video":"Video Script",
        "label_tech":"Teknik Detaylar","label_email":"E-posta Kampanyası","label_seo":"SEO & Web Metni",
        "label_photo":"Fotoğraf Tavsiyeleri","extra_details":"Ek Mülk Detayları",
        "interface_lang":"Arayüz Dili","logout":"Çıkış Yap","acc_settings":"Hesap Ayarları",
        "update_pw":"Şifre Güncelle","new_pw":"Yeni Şifre","btn_update":"Şifreyi Güncelle",
        "danger_zone":"Tehlikeli Bölge","delete_confirm":"Hesabımı kalıcı olarak silmek istiyorum.",
        "btn_delete":"Hesabı Sil","pw_min_err":"Şifre en az 6 karakter olmalıdır.",
        "delete_email_sent":"Onay e-postası gönderildi! Gelen kutunuzu kontrol edin.",
        "delete_email_fail":"E-posta gönderilemedi. SMTP ayarlarını kontrol edin.",
    },
    "Español": {
        "title":"SarSa AI | Plataforma de Inteligencia Inmobiliaria",
        "service_desc":"Inteligencia Visual de Propiedades y Automatización de Ventas Globales",
        "subtitle":"Convierta fotos en anuncios premium, kits de redes sociales, guiones de video, fichas técnicas, campañas de email y copy SEO al instante.",
        "settings":"Configuración","target_lang":"Escribir en…","prop_type":"Tipo de Propiedad",
        "price":"Precio de Mercado","location":"Ubicación","tone":"Estrategia de Marketing",
        "tones":["Profesional Estándar","Ultra-Lujo","Enfoque de Inversión","Minimalista Moderno","Vida Familiar","Alquiler Vacacional","Comercial"],
        "ph_prop":"Ej: Apartamento 3+1, Villa de Lujo…","ph_price":"Ej: $850.000 o EUR 1.500/mes…",
        "ph_loc":"Ej: Madrid, España o Marbella…","bedrooms":"Dormitorios","bathrooms":"Baños",
        "area":"Área","year_built":"Año de Construcción","ph_beds":"Ej: 3","ph_baths":"Ej: 2",
        "ph_area":"Ej: 185 m²","ph_year":"Ej: 2022","furnishing":"Amueblado",
        "furnishing_opts":["No especificado","Completamente Amueblado","Semi-Amueblado","Sin Amueblar"],
        "target_audience":"Público Objetivo",
        "audience_opts":["Mercado General","Compradores de Lujo","Inversores & ROI","Extranjeros & Internacionales","Primeros Compradores","Mercado Vacacional","Inquilinos Comerciales"],
        "custom_inst":"Notas Especiales","custom_inst_ph":"Ej: Piscina privada, vistas al mar, domótica…",
        "btn":"GENERAR ACTIVOS SELECCIONADOS","upload_label":"Subir Fotos de la Propiedad",
        "result":"Vista Previa Ejecutiva","loading":"Creando su ecosistema de marketing premium…",
        "empty":"Esperando imágenes. Suba fotos y complete los detalles a la izquierda.",
        "download":"Exportar Sección (TXT)","save_btn":"Guardar","saved_msg":"¡Guardado!",
        "error":"Error:","clear_btn":"Limpiar","select_sections":"Seleccionar Secciones",
        "tab_main":"Anuncio Premium","tab_social":"Kit de Redes Sociales","tab_video":"Guiones de Video",
        "tab_tech":"Especificaciones","tab_email":"Campaña de Email","tab_seo":"SEO & Web Copy","tab_photo":"Guía de Fotos",
        "label_main":"Texto de Ventas","label_social":"Contenido Social","label_video":"Guion de Video",
        "label_tech":"Ficha Técnica","label_email":"Campaña de Email","label_seo":"SEO & Web Copy",
        "label_photo":"Recomendaciones de Fotografía","extra_details":"Detalles Adicionales",
        "interface_lang":"Idioma de Interfaz","logout":"Cerrar Sesión","acc_settings":"Cuenta",
        "update_pw":"Actualizar Contraseña","new_pw":"Nueva Contraseña","btn_update":"Actualizar Ahora",
        "danger_zone":"Zona de Peligro","delete_confirm":"Quiero eliminar mi cuenta permanentemente.",
        "btn_delete":"Eliminar Cuenta","pw_min_err":"Mínimo 6 caracteres requeridos.",
        "delete_email_sent":"Email de confirmación enviado! Revisa tu bandeja.",
        "delete_email_fail":"Error al enviar email. Verifique la configuración SMTP.",
    },
    "Deutsch": {
        "title":"SarSa AI | Immobilien-Intelligenz-Plattform",
        "service_desc":"All-in-One Visuelle Objektintelligenz & Globale Verkaufsautomatisierung",
        "subtitle":"Verwandeln Sie Fotos sofort in Premium-Exposés, Social-Media-Kits, Videoskripte, Datenblätter, E-Mail-Kampagnen und SEO-Texte.",
        "settings":"Konfiguration","target_lang":"Erstellen in…","prop_type":"Objekttyp",
        "price":"Marktpreis","location":"Standort","tone":"Marketingstrategie",
        "tones":["Standard-Profi","Ultra-Luxus","Investitionsfokus","Modern-Minimalistisch","Familienleben","Ferienmiete","Gewerbe"],
        "ph_prop":"Z.B. 3-Zimmer-Wohnung, Luxusvilla…","ph_price":"Z.B. 850.000€ oder 2.000€/Monat…",
        "ph_loc":"Z.B. Berlin oder Hamburg…","bedrooms":"Schlafzimmer","bathrooms":"Badezimmer",
        "area":"Fläche","year_built":"Baujahr","ph_beds":"Z.B. 3","ph_baths":"Z.B. 2",
        "ph_area":"Z.B. 185 m²","ph_year":"Z.B. 2022","furnishing":"Möblierung",
        "furnishing_opts":["Nicht angegeben","Vollmöbliert","Teilmöbliert","Unmöbliert"],
        "target_audience":"Zielgruppe",
        "audience_opts":["Allgemeiner Markt","Luxuskäufer","Investoren & ROI","Expats & Internationale","Erstkäufer","Ferienmarkt","Gewerbemieter"],
        "custom_inst":"Notizen & Besonderheiten","custom_inst_ph":"Z.B. Privatpool, Panoramasicht, Smart-Home…",
        "btn":"AUSGEWÄHLTE ASSETS ERSTELLEN","upload_label":"Fotos hier hochladen",
        "result":"Executive-Vorschau","loading":"Ihr Marketing-Ökosystem wird erstellt…",
        "empty":"Warte auf Bilder. Laden Sie Fotos hoch und füllen Sie die Details aus.",
        "download":"Abschnitt Exportieren (TXT)","save_btn":"Speichern","saved_msg":"Gespeichert!",
        "error":"Fehler:","clear_btn":"Zurücksetzen","select_sections":"Bereiche wählen",
        "tab_main":"Premium-Exposé","tab_social":"Social Media Kit","tab_video":"Videoskripte",
        "tab_tech":"Tech-Details","tab_email":"E-Mail-Kampagne","tab_seo":"SEO & Webtext","tab_photo":"Foto-Guide",
        "label_main":"Verkaufstext","label_social":"Social-Media-Content","label_video":"Videoskript",
        "label_tech":"Technische Daten","label_email":"E-Mail-Kampagne","label_seo":"SEO & Webtext",
        "label_photo":"Fotografie-Empfehlungen","extra_details":"Weitere Details",
        "interface_lang":"Oberfläche Sprache","logout":"Abmelden","acc_settings":"Kontoeinstellungen",
        "update_pw":"Passwort ändern","new_pw":"Neues Passwort","btn_update":"Jetzt aktualisieren",
        "danger_zone":"Gefahrenzone","delete_confirm":"Ich möchte mein Konto dauerhaft löschen.",
        "btn_delete":"Konto löschen","pw_min_err":"Mindestens 6 Zeichen erforderlich.",
        "delete_email_sent":"Bestätigungs-E-Mail gesendet! Überprüfen Sie Ihren Posteingang.",
        "delete_email_fail":"E-Mail konnte nicht gesendet werden. SMTP-Einstellungen prüfen.",
    },
    "Français": {
        "title":"SarSa AI | Plateforme d'Intelligence Immobilière",
        "service_desc":"Intelligence Visuelle Immobilière et Automatisation des Ventes Globales",
        "subtitle":"Transformez vos photos en annonces premium, kits réseaux sociaux, scripts vidéo, fiches techniques, campagnes email et copy SEO instantanément.",
        "settings":"Configuration","target_lang":"Rédiger en…","prop_type":"Type de Bien",
        "price":"Prix du Marché","location":"Localisation","tone":"Stratégie Marketing",
        "tones":["Standard Pro","Ultra-Luxe","Focus Investissement","Minimaliste Moderne","Vie de Famille","Location Saisonnière","Commercial"],
        "ph_prop":"Ex: Appartement T4, Villa de Luxe…","ph_price":"Ex: 850.000€ ou 1.500€/mois…",
        "ph_loc":"Ex: Paris, Côte d'Azur ou Lyon…","bedrooms":"Chambres","bathrooms":"Salles de Bain",
        "area":"Surface","year_built":"Année de Construction","ph_beds":"Ex: 3","ph_baths":"Ex: 2",
        "ph_area":"Ex: 185 m²","ph_year":"Ex: 2022","furnishing":"Ameublement",
        "furnishing_opts":["Non spécifié","Entièrement Meublé","Semi-Meublé","Non Meublé"],
        "target_audience":"Audience Cible",
        "audience_opts":["Marché Général","Acheteurs de Luxe","Investisseurs & ROI","Expatriés & Internationaux","Primo-Accédants","Marché Vacances","Locataires Commerciaux"],
        "custom_inst":"Notes Spéciales & Points Forts","custom_inst_ph":"Ex: Piscine privée, vue panoramique, domotique…",
        "btn":"GÉNÉRER LES ACTIFS SÉLECTIONNÉS","upload_label":"Déposer les Photos Ici",
        "result":"Aperçu Exécutif","loading":"Préparation de votre écosystème marketing…",
        "empty":"En attente d'images. Déposez des photos et remplissez les détails à gauche.",
        "download":"Exporter Section (TXT)","save_btn":"Enregistrer","saved_msg":"Enregistré !",
        "error":"Erreur:","clear_btn":"Réinitialiser","select_sections":"Sélectionner les sections",
        "tab_main":"Annonce Premium","tab_social":"Kit Réseaux Sociaux","tab_video":"Scripts Vidéo",
        "tab_tech":"Spécifications","tab_email":"Campagne Email","tab_seo":"SEO & Web Copy","tab_photo":"Guide Photo",
        "label_main":"Texte de Vente","label_social":"Contenu Social","label_video":"Script Vidéo",
        "label_tech":"Détails Techniques","label_email":"Campagne Email","label_seo":"SEO & Web Copy",
        "label_photo":"Recommandations Photo","extra_details":"Détails Supplémentaires",
        "interface_lang":"Langue Interface","logout":"Déconnexion","acc_settings":"Paramètres",
        "update_pw":"Changer MDP","new_pw":"Nouveau MDP","btn_update":"Mettre à jour",
        "danger_zone":"Zone de Danger","delete_confirm":"Supprimer définitivement mon compte.",
        "btn_delete":"Supprimer le compte","pw_min_err":"6 caractères minimum.",
        "delete_email_sent":"Email de confirmation envoyé ! Vérifiez votre boîte.",
        "delete_email_fail":"Échec d'envoi. Vérifiez les paramètres SMTP.",
    },
    "Português": {
        "title":"SarSa AI | Plataforma de Inteligência Imobiliária",
        "service_desc":"Inteligência Visual Imobiliária e Automação de Vendas Globais",
        "subtitle":"Transforme fotos em anúncios premium, kits de redes sociais, roteiros de vídeo, fichas técnicas, campanhas de email e copy SEO instantaneamente.",
        "settings":"Configuração","target_lang":"Escrever em…","prop_type":"Tipo de Imóvel",
        "price":"Preço de Mercado","location":"Localização","tone":"Estratégia de Marketing",
        "tones":["Profissional Padrão","Ultra-Luxo","Foco em Investimento","Minimalista Moderno","Vida Familiar","Aluguel de Temporada","Comercial"],
        "ph_prop":"Ex: Apartamento T3, Moradia de Luxo…","ph_price":"Ex: 500.000€ ou 1.500€/mês…",
        "ph_loc":"Ex: Lisboa, Algarve ou Porto…","bedrooms":"Quartos","bathrooms":"Banheiros",
        "area":"Área","year_built":"Ano de Construção","ph_beds":"Ex: 3","ph_baths":"Ex: 2",
        "ph_area":"Ex: 185 m²","ph_year":"Ex: 2022","furnishing":"Mobiliário",
        "furnishing_opts":["Não especificado","Completamente Mobilado","Semi-Mobilado","Sem Mobília"],
        "target_audience":"Público-Alvo",
        "audience_opts":["Mercado Geral","Compradores de Luxo","Investidores & ROI","Expats e Internacionais","Primeiros Compradores","Mercado de Férias","Inquilinos Comerciais"],
        "custom_inst":"Notas Especiais e Destaques","custom_inst_ph":"Ex: Piscina privativa, vista panorâmica, casa inteligente…",
        "btn":"GERAR ATIVOS SELECIONADOS","upload_label":"Enviar Fotos do Imóvel",
        "result":"Pré-visualização Executiva","loading":"Preparando seu ecossistema de marketing…",
        "empty":"Aaguardando imagens. Envie fotos e preencha os detalhes à esquerda.",
        "download":"Exportar Secção (TXT)","save_btn":"Salvar","saved_msg":"Salvo!",
        "error":"Erro:","clear_btn":"Limpar","select_sections":"Selecionar Seções",
        "tab_main":"Anúncio Premium","tab_social":"Kit Redes Sociais","tab_video":"Roteiros de Vídeo",
        "tab_tech":"Especificações","tab_email":"Campanha de Email","tab_seo":"SEO & Web Copy","tab_photo":"Guia de Fotos",
        "label_main":"Texto de Vendas","label_social":"Conteúdo Social","label_video":"Roteiro de Vídeo",
        "label_tech":"Especificações Técnicas","label_email":"Campanha Email","label_seo":"SEO & Web Copy",
        "label_photo":"Recomendações de Fotografia","extra_details":"Detalhes Adicionais",
        "interface_lang":"Idioma Interface","logout":"Sair","acc_settings":"Configurações",
        "update_pw":"Alterar Senha","new_pw":"Nova Senha","btn_update":"Atualizar Agora",
        "danger_zone":"Zona de Perigo","delete_confirm":"Quero excluir minha conta permanentemente.",
        "btn_delete":"Excluir Conta","pw_min_err":"Mínimo de 6 caracteres.",
        "delete_email_sent":"Email de confirmação enviado! Verifique sua caixa de entrada.",
        "delete_email_fail":"Falha ao enviar email. Verifique as configurações SMTP.",
    },
    "日本語": {
        "title":"SarSa AI | 不動産インテリジェンス・プラットフォーム",
        "service_desc":"オールインワン視覚的物件インテリジェンス＆グローバル販売自動化",
        "subtitle":"物件写真をプレミアム広告、SNSキット、動画台本、技術仕様書、メールキャンペーン、SEOコピーに瞬時に変換します。",
        "settings":"設定","target_lang":"作成言語…","prop_type":"物件種別",
        "price":"市場価格","location":"所在地","tone":"マーケティング戦略",
        "tones":["標準プロ","ウルトラ・ラグジュアリー","投資重視","モダン・ミニマリスト","ファミリー向け","バケーションレンタル","商業用"],
        "ph_prop":"例: 3LDKマンション、高級別荘…","ph_price":"例: 8500万円 または 月20万円…",
        "ph_loc":"例: 東京都港区、大阪、ドバイ…","bedrooms":"寝室数","bathrooms":"浴室数",
        "area":"面積","year_built":"建築年","ph_beds":"例: 3","ph_baths":"例: 2",
        "ph_area":"例: 185 m²","ph_year":"例: 2022","furnishing":"家具",
        "furnishing_opts":["未指定","フル家具付き","一部家具付き","家具なし"],
        "target_audience":"ターゲット層",
        "audience_opts":["一般市場","富裕層バイヤー","投資家 & ROI重視","海外居住者","初めての購入者","休暇・別荘市場","商業テナント"],
        "custom_inst":"特記事項 ＆ アピールポイント","custom_inst_ph":"例: プライベートプール、パノラマビュー、スマートホーム…",
        "btn":"選択した資産を生成","upload_label":"ここに物件写真をアップロード",
        "result":"エグゼクティブ・プレビュー","loading":"プレミアム・マーケティング・エコシステムを構築中…",
        "empty":"分析用の画像を待機中。写真をアップロードし、左側に詳細を入力してください。",
        "download":"セクションを書き出し (TXT)","save_btn":"変更を保存","saved_msg":"保存完了！",
        "error":"エラー:","clear_btn":"フォームをリセット","select_sections":"生成するセクションを選択",
        "tab_main":"プレミアム広告","tab_social":"SNSキット","tab_video":"動画台本",
        "tab_tech":"技術仕様","tab_email":"メールキャンペーン","tab_seo":"SEO ＆ Webコピー","tab_photo":"写真ガイド",
        "label_main":"セールスコピー","label_social":"SNSコンテンツ","label_video":"動画シナリオ",
        "label_tech":"技術詳細","label_email":"メールキャンペーン","label_seo":"SEOテキスト",
        "label_photo":"撮影のアドバイス","extra_details":"物件詳細情報",
        "interface_lang":"インターフェース言語","logout":"ログアウト","acc_settings":"アカウント設定",
        "update_pw":"パスワード変更","new_pw":"新しいパスワード","btn_update":"今すぐ更新",
        "danger_zone":"危険区域","delete_confirm":"アカウントを完全に削除します。",
        "btn_delete":"アカウント削除","pw_min_err":"6文字以上必要です。",
        "delete_email_sent":"確認メールを送信しました！受信トレイを確認してください。",
        "delete_email_fail":"メールの送信に失敗しました。SMTP設定を確認してください。",
    },
    "简体中文": {
        "title":"SarSa AI | 房地产智能平台",
        "service_desc":"全方位房产视觉智能与全球销售自动化",
        "subtitle":"立即将房产照片转化为优质房源描述、社交媒体包、视频脚本、技术规格、邮件营销和 SEO 文案。",
        "settings":"配置","target_lang":"编写语言…","prop_type":"房产类型",
        "price":"市场价格","location":"地点","tone":"营销策略",
        "tones":["标准专业","顶级豪宅","投资价值","现代简约","家庭生活","度假租赁","商业办公"],
        "ph_prop":"例如：3室1厅公寓、豪华别墅…","ph_price":"例如：$850,000 或 $2,000/月…",
        "ph_loc":"例如：上海浦东新区、北京或伦敦…","bedrooms":"卧室","bathrooms":"卫生间",
        "area":"面积","year_built":"建造年份","ph_beds":"例如：3","ph_baths":"例如：2",
        "ph_area":"例如：185 平方米","ph_year":"例如：2022","furnishing":"装修情况",
        "furnishing_opts":["未指定","精装修（含家具）","简装修","毛坯房"],
        "target_audience":"目标受众",
        "audience_opts":["大众市场","豪宅买家","投资者 & 投资回报","外籍人士","首次购房者","度假市场","商业租客"],
        "custom_inst":"特别备注与亮点","custom_inst_ph":"例如：私人泳池、全景海景、智能家居…",
        "btn":"生成所选资产","upload_label":"在此上传房产照片",
        "result":"高级预览","loading":"正在打造您的专属营销生态系统…",
        "empty":"等待照片进行专业分析。请上传照片并在左侧填写详细信息。",
        "download":"导出此部分 (TXT)","save_btn":"保存更改","saved_msg":"已保存！",
        "error":"错误：","clear_btn":"重置表单","select_sections":"选择要生成的章节",
        "tab_main":"优质房源","tab_social":"社媒包","tab_video":"视频脚本",
        "tab_tech":"技术规格","tab_email":"邮件营销","tab_seo":"SEO 网页文案","tab_photo":"拍摄指南",
        "label_main":"销售文案","label_social":"社媒内容","label_video":"视频脚本",
        "label_tech":"技术规格","label_email":"邮件营销","label_seo":"SEO 文案",
        "label_photo":"摄影建议","extra_details":"额外房产细节",
        "interface_lang":"界面语言","logout":"退出登录","acc_settings":"账户设置",
        "update_pw":"更改密码","new_pw":"新密码","btn_update":"立即更新",
        "danger_zone":"危险区域","delete_confirm":"我确认要永久删除我的账户。",
        "btn_delete":"删除账户","pw_min_err":"密码至少需要6位。",
        "delete_email_sent":"确认邮件已发送！请检查您的收件箱。",
        "delete_email_fail":"发送邮件失败。请检查SMTP设置。",
    },
    "العربية": {
        "title":"SarSa AI | منصة الذكاء العقاري",
        "service_desc":"الذكاء البصري المتكامل للعقارات وأتمتة المبيعات العالمية",
        "subtitle":"حول صور العقارات فوراً إلى إعلانات مميزة، حقائب تواصل اجتماعي، سيناريوهات فيديو، مواصفات فنية، حملات بريدية ونصوص SEO.",
        "settings":"الإعدادات","target_lang":"لغة الكتابة…","prop_type":"نوع العقار",
        "price":"سعر السوق","location":"الموقع","tone":"استراتيجية التسويق",
        "tones":["احترافي قياسي","فخامة فائقة","تركيز استثماري","عصري بسيط","حياة عائلية","تأجير سياحي","تجاري"],
        "ph_prop":"مثال: شقة 3+1، فيلا فاخرة…","ph_price":"مثال: 850,000$ أو 2,500$ شهرياً…",
        "ph_loc":"مثال: دبي مارينا، الرياض، القاهرة…","bedrooms":"غرف النوم","bathrooms":"الحمامات",
        "area":"المساحة","year_built":"سنة البناء","ph_beds":"مثال: 3","ph_baths":"مثال: 2",
        "ph_area":"مثال: 185 م²","ph_year":"مثال: 2022","furnishing":"حالة التأثيث",
        "furnishing_opts":["غير محدد","مفروش بالكامل","مفروش جزئياً","غير مفروش"],
        "target_audience":"الجمهور المستهدف",
        "audience_opts":["السوق العام","مشتري الفخامة","المستثمرون","المغتربون","مشتري لأول مرة","سوق العطلات","مستأجر تجاري"],
        "custom_inst":"ملاحظات خاصة ومميزات","custom_inst_ph":"مثال: مسبح خاص، إطلالة بانورامية، منزل ذكي…",
        "btn":"إنشاء الأصول المختارة","upload_label":"ضع صور العقار هنا",
        "result":"معاينة تنفيذية","loading":"جاري تجهيز منظومتك التسويقية الفاخرة…",
        "empty":"في انتظار الصور لبدء التحليل المهني. ارفع الصور واملأ التفاصيل على اليسار.",
        "download":"تصدير القسم (TXT)","save_btn":"حفظ التغييرات","saved_msg":"تم الحفظ!",
        "error":"خطأ:","clear_btn":"إعادة تعيين","select_sections":"اختر الأقسام المراد إنشاؤها",
        "tab_main":"الإعلان الرئيسي","tab_social":"حقيبة التواصل","tab_video":"سيناريو الفيديو",
        "tab_tech":"المواصفات الفنية","tab_email":"حملة البريد","tab_seo":"نصوص الويب وSEO","tab_photo":"دليل التصوير",
        "label_main":"نص المبيعات","label_social":"محتوى التواصل","label_video":"سيناريو الفيديو",
        "label_tech":"المواصفات الفنية","label_email":"حملة البريد الإلكتروني","label_seo":"نص SEO",
        "label_photo":"توصيات التصوير","extra_details":"تفاصيل العقار الإضافية",
        "interface_lang":"لغة الواجهة","logout":"تسجيل الخروج","acc_settings":"إعدادات الحساب",
        "update_pw":"تحديث كلمة السر","new_pw":"كلمة سر جديدة","btn_update":"تحديث الآن",
        "danger_zone":"منطقة خطر","delete_confirm":"أريد حذف حسابي نهائياً.",
        "btn_delete":"حذف الحساب","pw_min_err":"يجب أن تكون 6 خانات على الأقل.",
        "delete_email_sent":"تم إرسال بريد التأكيد! تحقق من صندوق الوارد.",
        "delete_email_fail":"فشل إرسال البريد. تحقق من إعدادات SMTP.",
    },
}

# ─── SHARED AUTH CSS ──────────────────────────────────────────────────────────
_AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="st-"]{ font-family:'Plus Jakarta Sans',sans-serif !important; }
.stApp{ background:linear-gradient(135deg,#f0f4f8 0%,#e8edf5 100%) !important; }
#MainMenu,footer,div[data-testid="stDecoration"]{ display:none !important; }
.block-container{
    max-width:540px !important; margin:2rem auto !important;
    background:white; border-radius:24px; padding:2.5rem !important;
    box-shadow:0 20px 60px rgba(0,0,0,0.08); border:1px solid #e2e8f0;
}
.stButton>button{
    background:#0f172a !important; color:white !important;
    border-radius:12px !important; padding:14px 24px !important;
    font-weight:700 !important; font-size:0.95rem !important; width:100% !important;
    border:none !important; transition:all 0.25s ease !important;
    box-shadow:0 4px 15px rgba(15,23,42,0.25) !important;
}
.stButton>button:hover{
    background:#1e293b !important; transform:translateY(-2px) !important;
    box-shadow:0 8px 25px rgba(15,23,42,0.35) !important;
}
</style>"""

# ─── LANGUAGE HELPERS ─────────────────────────────────────────────────────────
def _at(key, fb=""):
    return auth_texts.get(st.session_state.auth_lang, auth_texts["English"]).get(key, fb)

def _ut(key, fb=""):
    return ui_languages.get(st.session_state.auth_lang, ui_languages["English"]).get(key, fb)

def _lang_sel(widget_key):
    langs = list(auth_texts.keys())
    idx   = langs.index(st.session_state.auth_lang) if st.session_state.auth_lang in langs else 0
    sel   = st.selectbox("🌐 Select Language / Dil Seçin", langs, index=idx, key=widget_key)
    if sel != st.session_state.auth_lang:
        st.session_state.auth_lang = sel
        if cookie_manager:
            cookie_manager.set("sarsa_auth_lang", sel, expires_at=datetime.now() + timedelta(days=365))
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE A — EMAIL CONFIRMED (KAYIT SONRASI ŞIK ONAY EKRANI)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.show_email_confirmed:
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)
    _lang_sel("lk_confirmed")

    st.markdown(f"""
    <div style="text-align:center;padding:1.5rem 0 2rem;">
        <div style="font-size:5rem;line-height:1;margin-bottom:1rem;
                    filter:drop-shadow(0 4px 16px rgba(34,197,94,0.4));">✅</div>
        <h1 style="color:#0f172a;font-weight:800;font-size:2rem;margin:0 0 0.8rem;">
            {_at("confirmed_title","✅ Email Verified Successfully!")}
        </h1>
        <p style="color:#475569;font-size:1.05rem;line-height:1.75;margin:0 0 0.4rem;">
            {_at("confirmed_msg","Your account has been confirmed and is ready to use.")}
        </p>
        <p style="color:#94a3b8;font-size:0.9rem;">
            {_at("confirmed_sub","Click the button below to go to the login page.")}
        </p>
    </div>
    <hr style="border:none;border-top:1px solid #f1f5f9;margin:0 0 1.8rem;">
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,3,1])
    with c2:
        if st.button(_at("confirmed_btn","🔑 Go to Login"), use_container_width=True):
            st.session_state.show_email_confirmed = False
            with st.spinner("Yönlendiriliyor..."):
                time.sleep(1)
            st.rerun()

    st.markdown("""<p style="text-align:center;color:#cbd5e1;font-size:0.8rem;margin-top:1.5rem;">
        SarSa AI | Real Estate Intelligence</p>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE B — SET NEW PASSWORD (ŞİFRE SIFIRLAMA LİNKİNDEN GELEN ŞIK EKRAN)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.recovery_mode:
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)
    _lang_sel("lk_recovery")

    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0 1.5rem;">
        <div style="font-size:3.5rem;margin-bottom:0.6rem;">🔒</div>
        <h1 style="color:#0f172a;font-weight:800;font-size:1.8rem;margin:0;">
            {_at("pw_reset_title","Set Your New Password")}
        </h1>
        <p style="color:#64748b;margin-top:0.6rem;font-size:0.97rem;line-height:1.6;">
            {_at("pw_reset_desc","Enter a new password for your account.")}
        </p>
    </div>
    <hr style="border:none;border-top:1px solid #f1f5f9;margin:0 0 1.5rem;">
    """, unsafe_allow_html=True)

    with st.form("recovery_form"):
        new_pw_val = st.text_input(
            _at("new_pw_label","New Password"),
            type="password", placeholder="••••••••"
        )
        cs, cc = st.columns(2)
        with cs: do_save   = st.form_submit_button(_at("pw_reset_btn","✅ Save Password & Login"), use_container_width=True)
        with cc: do_cancel = st.form_submit_button(_at("pw_reset_cancel","❌ Cancel"),              use_container_width=True)

        if do_cancel:
            st.session_state.recovery_mode = False
            st.session_state.is_logged_in  = False
            st.rerun()

        if do_save:
            if len(new_pw_val) < 6:
                st.error(_at("pw_reset_min_err","❌ Password must be at least 6 characters."))
            else:
                try:
                    if st.session_state.access_token:
                        supabase.auth.set_session(
                            st.session_state.access_token,
                            st.session_state.refresh_token)
                    supabase.auth.update_user({"password": new_pw_val})
                    st.success(_at("pw_reset_success","✅ Password updated! Logging you in…"))
                    
                    st.session_state.recovery_mode = False
                    st.session_state.is_logged_in  = True
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating password: {e}")
    st.stop()

# ─── AUTH STATUS ──────────────────────────────────────────────────────────────
def get_status():
    if st.session_state.is_logged_in:
        return "paid", st.session_state.user_email
    try:
        if st.session_state.access_token:
            supabase.auth.set_session(
                st.session_state.access_token, st.session_state.refresh_token)
        ur = supabase.auth.get_user()
        if not ur or not ur.user: return "logged_out", None
        if not ur.user.email_confirmed_at: return "unverified", ur.user.email
        st.session_state.is_logged_in = True
        st.session_state.user_email   = ur.user.email
        return "paid", ur.user.email
    except Exception:
        return "logged_out", None

auth_status, user_email = get_status()

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="st-"]{ font-family:'Plus Jakarta Sans',sans-serif !important; }
.stApp{ background-color:#f0f4f8 !important; }
div[data-testid="stInputInstructions"],#MainMenu,footer,
div[data-testid="stDecoration"]{ display:none !important; }
.block-container{
    background:white; padding:2.5rem 3rem !important; border-radius:20px;
    box-shadow:0 10px 40px rgba(0,0,0,0.06); margin-top:1.5rem; border:1px solid #e2e8f0; }
h1{ color:#0f172a !important; font-weight:800 !important; text-align:center; }
[data-testid="stSidebar"]{ background:#ffffff !important; border-right:1px solid #e2e8f0 !important; }
[data-testid="stSidebar"] label{ font-size:0.74rem !important; font-weight:700 !important;
    color:#64748b !important; text-transform:uppercase !important; letter-spacing:0.7px !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea{
    border-radius:8px !important; border:1.5px solid #e2e8f0 !important;
    background:#f8fafc !important; font-size:0.875rem !important; }
.stButton>button{
    background:#0f172a !important; color:white !important;
    border-radius:12px !important; padding:14px 24px !important;
    font-weight:700 !important; font-size:0.95rem !important; width:100% !important;
    border:none !important; transition:all 0.25s ease !important;
    box-shadow:0 4px 15px rgba(15,23,42,0.3) !important; }
.stButton>button:hover{
    background:#1e293b !important;
    box-shadow:0 8px 25px rgba(15,23,42,0.4) !important; transform:translateY(-1px) !important; }
.stTabs [aria-selected="true"]{
    background-color:#0f172a !important; color:white !important; border-radius:8px 8px 0 0 !important; }
</style>""", unsafe_allow_html=True)

@st.cache_data
def load_logo(p):
    return Image.open(p) if os.path.exists(p) else None

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN / REGISTER PAGE
# ══════════════════════════════════════════════════════════════════════════════
if auth_status != "paid":
    langs = list(auth_texts.keys())
    sel   = st.selectbox(
        "🌐 Select Language / Dil Seçin", langs,
        index=langs.index(st.session_state.auth_lang) if st.session_state.auth_lang in langs else 0,
        key="login_lang")
    if sel != st.session_state.auth_lang:
        st.session_state.auth_lang = sel
        if cookie_manager:
            cookie_manager.set("sarsa_auth_lang", sel, expires_at=datetime.now() + timedelta(days=365))
        st.rerun()
    at = auth_texts[st.session_state.auth_lang]

    cl, ct = st.columns([1, 6])
    with cl:
        logo = load_logo("SarSa_Logo_Transparent.png")
        if logo: st.image(logo, use_container_width=True)
    with ct:
        st.markdown(f"<h1 style='text-align:left;margin-top:0;'>{at['welcome_title']}</h1>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.1rem;color:#475569;font-weight:500;margin-bottom:2rem;'>"
                    f"{at['welcome_desc']}</p>", unsafe_allow_html=True)

    st.markdown(f"<h3 style='text-align:center;color:#0f172a;margin-bottom:1.5rem;'>"
                f"{at['login_prompt']}</h3>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        f"🔑 {at['login']}", f"📝 {at['register']}", f"❓ {at['forgot_pw']}"])

    with tab1:
        with st.form("login_form"):
            em = st.text_input(at["email"])
            pw = st.text_input(at["password"], type="password")
            if st.form_submit_button(at["btn_login"]):
                try:
                    r = supabase.auth.sign_in_with_password({"email": em, "password": pw})
                    if r.session:
                        st.session_state.access_token  = r.session.access_token
                        st.session_state.refresh_token = r.session.refresh_token
                        save_auth_cookies(r.session.access_token, r.session.refresh_token)
                    st.session_state.is_logged_in = True
                    st.session_state.user_email   = r.user.email
                    st.rerun()
                except Exception as ex:
                    msg = str(ex)
                    if "Email not confirmed" in msg: st.error(f"{at['verify_msg']} {em}")
                    elif "Invalid login credentials" in msg: st.error(f"❌ {at['error_login']}")
                    else: st.error(msg)

    with tab2:
        with st.form("register_form"):
            er = st.text_input(at["email"])
            pr = st.text_input(at["password"] + " (Min 6)", type="password")
            if st.form_submit_button(at["btn_reg"]):
                try:
                    supabase.auth.sign_up({
                        "email": er, "password": pr,
                        "options": {"email_redirect_to": "https://sarsa-ai-estateintelligence.streamlit.app/"}
                    })
                    st.success(f"✅ {at['success_reg']}")
                except Exception as ex:
                    msg = str(ex)
                    if "User already registered" in msg: st.error("This email is already registered.")
                    else: st.error(f"Error: {ex}")

    with tab3:
        with st.form("forgot_form"):
            er2 = st.text_input(at["email"], placeholder="your@email.com")
            if st.form_submit_button(at["btn_reset"]):
                er2 = er2.strip()
                if not er2 or "@" not in er2:
                    st.error(at["reset_invalid_email"])
                else:
                    with st.spinner("Checking…"):
                        exists = is_email_registered(er2)
                    if not exists:
                        st.error(at["reset_not_found"])
                    else:
                        try:
                            supabase.auth.reset_password_for_email(
                                er2,
                                {"redirect_to": "https://sarsa-ai-estateintelligence.streamlit.app/"})
                            st.success(f"✅ {at['reset_success']}")
                        except Exception as e:
                            st.error(f"Error: {e}")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# AI + SIDEBAR (ANA UYGULAMA)
# ══════════════════════════════════════════════════════════════════════════════
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

with st.sidebar:
    logo = load_logo("SarSa_Logo_Transparent.png")
    if logo: st.image(logo, use_container_width=True)
    else:
        st.markdown("<div style='text-align:center;padding:.8rem 0 .5rem;'>"
                    "<span style='font-size:1.8rem;font-weight:800;color:#0f172a;'>SarSa</span>"
                    "<span style='font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#3b82f6,#8b5cf6);"
                    "-webkit-background-clip:text;-webkit-text-fill-color:transparent;'> AI</span></div>",
                    unsafe_allow_html=True)
    st.divider()

    all_ui  = list(ui_languages.keys())
    cur_idx = all_ui.index(st.session_state.auth_lang) if st.session_state.auth_lang in all_ui else 0
    sel_ui  = st.selectbox(f"🌐 {_ut('interface_lang','Interface Language')}",
                           all_ui, index=cur_idx, key="sb_lang")
    if sel_ui != st.session_state.auth_lang:
        st.session_state.auth_lang = sel_ui
        if cookie_manager:
            cookie_manager.set("sarsa_auth_lang", sel_ui, expires_at=datetime.now() + timedelta(days=365))
        st.rerun()
    t = ui_languages[st.session_state.auth_lang]

    with st.expander(f"⚙️ {t['acc_settings']}"):
        st.write(st.session_state.user_email)
        st.subheader(t["update_pw"])
        new_pw_sb = st.text_input(t["new_pw"], type="password", key="sb_pw")
        if st.button(t["btn_update"], key="sb_upd"):
            if len(new_pw_sb) < 6: st.warning(t["pw_min_err"])
            else:
                try:
                    if st.session_state.access_token:
                        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
                    supabase.auth.update_user({"password": new_pw_sb})
                    st.success(t["saved_msg"])
                except Exception as e: st.error(f"{t['error']} {e}")
        st.divider()
        st.subheader(t["danger_zone"])
        chk_del = st.checkbox(t["delete_confirm"])
        if st.button(f"❌ {t['btn_delete']}", type="primary", use_container_width=True):
            if chk_del:
                try:
                    if st.session_state.access_token:
                        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
                    ur = supabase.auth.get_user()
                    if ur and ur.user:
                        ct_tok = str(uuid.uuid4()); ca_tok = str(uuid.uuid4())
                        exp = (datetime.now(timezone.utc)+timedelta(hours=24)).isoformat()
                        supabase.table("pending_deletions").insert({
                            "user_id":ur.user.id,"user_email":ur.user.email,
                            "confirm_token":ct_tok,"cancel_token":ca_tok,"expires_at":exp
                        }).execute()
                        ok, err = send_delete_confirmation_email(ur.user.email, ct_tok, ca_tok)
                        if ok: st.success(t["delete_email_sent"])
                        else:  st.error(f"{t['delete_email_fail']} — {err}")
                    else: st.error("Could not retrieve user. Please log out and log back in.")
                except Exception as e: st.error(f"{t['error']} {e}")
            else: st.warning("Please tick the confirmation checkbox first.")

    if st.button(f"🚪 {t['logout']}", use_container_width=True):
        with st.spinner("Çıkış yapılıyor..."):
            supabase.auth.sign_out()
            for k in ["is_logged_in","user_email","access_token","refresh_token"]:
                st.session_state[k] = False if k=="is_logged_in" else None
            clear_auth_cookies()
            time.sleep(1)
        st.rerun()

    st.markdown("---")
    st.header(t["settings"])
    st.session_state.target_lang_input = st.text_input(f"✍️ {t['target_lang']}", value=st.session_state.target_lang_input)
    st.session_state.prop_type = st.text_input(t["prop_type"], value=st.session_state.prop_type, placeholder=t["ph_prop"])
    st.session_state.price     = st.text_input(t["price"],     value=st.session_state.price,     placeholder=t["ph_price"])
    st.session_state.location  = st.text_input(t["location"],  value=st.session_state.location,  placeholder=t["ph_loc"])
    tone_idx = t["tones"].index(st.session_state.tone) if st.session_state.tone in t["tones"] else 0
    st.session_state.tone         = st.selectbox(t["tone"], t["tones"], index=tone_idx)
    st.session_state.audience_idx = st.selectbox(t["target_audience"], range(len(t["audience_opts"])),
        index=st.session_state.audience_idx, format_func=lambda x: t["audience_opts"][x])
    with st.expander(f"➕ {t['extra_details']}"):
        st.session_state.bedrooms       = st.text_input(t["bedrooms"],   value=st.session_state.bedrooms,   placeholder=t["ph_beds"])
        st.session_state.bathrooms      = st.text_input(t["bathrooms"],  value=st.session_state.bathrooms,  placeholder=t["ph_baths"])
        st.session_state.area_size      = st.text_input(t["area"],       value=st.session_state.area_size,  placeholder=t["ph_area"])
        st.session_state.year_built     = st.text_input(t["year_built"], value=st.session_state.year_built, placeholder=t["ph_year"])
        st.session_state.furnishing_idx = st.selectbox(t["furnishing"], range(len(t["furnishing_opts"])),
            index=st.session_state.furnishing_idx, format_func=lambda x: t["furnishing_opts"][x])
    st.session_state.custom_inst = st.text_area(f"📝 {t['custom_inst']}", value=st.session_state.custom_inst,
        placeholder=t["custom_inst_ph"], height=100)
    st.markdown("---")
    st.subheader(t["select_sections"])
    sec_opts = {t["tab_main"]:"main", t["tab_social"]:"social", t["tab_video"]:"video",
                t["tab_tech"]:"tech", t["tab_email"]:"email", t["tab_seo"]:"seo", t["tab_photo"]:"photo"}
    st.session_state.selected_sections = st.multiselect(
        "Sections:", options=list(sec_opts.keys()),
        default=list(sec_opts.keys()), label_visibility="collapsed")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"<h1 style='text-align:center;'>🏢 {t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;color:#64748b;font-size:1.1rem;margin-bottom:2rem;'>"
            f"{t.get('subtitle',t['service_desc'])}</p>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(f"📸 {t['upload_label']}",
    type=["jpg","png","webp","jpeg"], accept_multiple_files=True)

if uploaded_files:
    imgs = [Image.open(f) for f in uploaded_files]
    cols = st.columns(min(len(imgs),4))
    for i, img in enumerate(imgs):
        with cols[i%4]: st.image(img, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(f"🚀 {t.get('btn','GENERATE SELECTED ASSETS')}", use_container_width=True):
        if not st.session_state.selected_sections:
            st.warning("Please select at least one section from the sidebar.")
        else:
            with st.spinner(t.get("loading","Crafting your premium marketing ecosystem…")):
                st.success("Request received! Generating content for selected sections…")
            tabs = st.tabs(st.session_state.selected_sections)
            for idx, sec in enumerate(st.session_state.selected_sections):
                with tabs[idx]:
                    st.subheader(sec)
                    st.write(f"AI-generated content for '{sec}' will appear here.")
                    st.button(f"📥 {t['download']} – {sec}", key=f"dl_{idx}")
else:
    st.markdown(f"""
    <div style='text-align:center;padding:3rem;background:#f8fafc;border-radius:12px;
                border:2px dashed #cbd5e1;margin-top:2rem;'>
      <h3 style='color:#475569;'>🏘️ {t.get("result","Executive Preview")}</h3>
      <p style='color:#94a3b8;'>{t["empty"]}</p>
      <div style="display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:1.4rem;">
        {"".join(f"<span style='background:#f1f5f9;color:#475569;font-size:.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;'>{lb}</span>" for lb in [f"📝 {t['tab_main']}",f"📱 {t['tab_social']}",f"🎬 {t['tab_video']}",f"⚙️ {t['tab_tech']}",f"✉️ {t['tab_email']}",f"🔍 {t['tab_seo']}",f"📸 {t.get('tab_photo','Photo Guide')}"])}
      </div>
    </div>""", unsafe_allow_html=True)
import streamlit as st
import time
from PIL import Image
import google.generativeai as genai
import os
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Çerez (Cookie) yönetimi için (Sayfa yenilemelerinde hafıza)
try:
    import extra_streamlit_components as stx
except ImportError:
    stx = None
    st.warning("Gelişmiş hafıza (çerez) özellikleri için terminalde 'pip install extra-streamlit-components' çalıştırın.")

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SarSa AI | Real Estate Intelligence",
    page_icon="🏢", layout="wide"
)

# Cache (bellek) kullanmadan doğrudan tanımlıyoruz
def get_cookie_manager():
    return stx.CookieManager()

cookie_manager = get_cookie_manager()


# ─── SUPABASE ─────────────────────────────────────────────────────────────────
SUPABASE_URL: str = st.secrets["SUPABASE_URL"]
SUPABASE_KEY: str = st.secrets["SUPABASE_KEY"]
supabase: Client  = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── SESSION STATE & MEMORY ───────────────────────────────────────────────────
_defaults = {
    "auth_lang":            "English",
    "is_logged_in":         False,
    "user_email":           None,
    "recovery_mode":        False,
    "access_token":         None,
    "refresh_token":        None,
    "show_email_confirmed": False,
    "uretilen_ilan":"", "prop_type":"", "price":"",
    "location":"", "tone":"", "custom_inst":"",
    "target_lang_input":"English", "bedrooms":"",
    "bathrooms":"", "area_size":"", "year_built":"",
    "furnishing_idx":0, "audience_idx":0, "selected_sections":[],
}

for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Çerezlerden (Cookie) verileri al ve Session'a aktar (Sayfa Yenileme Koruması)
if cookie_manager:
    saved_lang = cookie_manager.get(cookie="sarsa_auth_lang")
    if saved_lang and saved_lang != st.session_state.auth_lang:
        st.session_state.auth_lang = saved_lang
    
    saved_access = cookie_manager.get(cookie="sarsa_access_token")
    saved_refresh = cookie_manager.get(cookie="sarsa_refresh_token")
    if saved_access and not st.session_state.access_token:
        st.session_state.access_token = saved_access
        st.session_state.refresh_token = saved_refresh

def save_auth_cookies(access, refresh):
    if cookie_manager:
        cookie_manager.set("sarsa_access_token", access, expires_at=datetime.now() + timedelta(days=7))
        cookie_manager.set("sarsa_refresh_token", refresh, expires_at=datetime.now() + timedelta(days=7))

def clear_auth_cookies():
    if cookie_manager:
        cookie_manager.delete("sarsa_access_token")
        cookie_manager.delete("sarsa_refresh_token")

# ─── RESTORE PERSISTENT SESSION ───────────────────────────────────────────────
if st.session_state.access_token and not st.session_state.is_logged_in:
    try:
        supabase.auth.set_session(
            st.session_state.access_token, st.session_state.refresh_token)
        _chk = supabase.auth.get_user()
        if _chk and _chk.user:
            st.session_state.is_logged_in = True
            st.session_state.user_email   = _chk.user.email
    except Exception:
        st.session_state.access_token  = None
        st.session_state.refresh_token = None
        st.session_state.is_logged_in  = False
        clear_auth_cookies()

# ─── EMAIL: ACCOUNT DELETION ──────────────────────────────────────────────────
def send_delete_confirmation_email(to_email, confirm_token, cancel_token):
    base = "https://sarsa-ai-estateintelligence.streamlit.app/"
    conf = f"{base}?action=confirm_delete&token={confirm_token}"
    canc = f"{base}?action=cancel_delete&token={cancel_token}"
    body = f"""
    <div style="font-family:Arial,sans-serif;max-width:620px;margin:0 auto;
                padding:30px;background:#f8fafc;border-radius:16px;">
      <div style="background:white;border-radius:12px;padding:36px;
                  box-shadow:0 4px 20px rgba(0,0,0,.07);">
        <h2 style="color:#0f172a;text-align:center;">⚠️ Account Deletion Request</h2>
        <p style="color:#64748b;text-align:center;font-size:14px;">SarSa AI | Real Estate Intelligence</p>
        <p style="color:#334155;font-size:16px;line-height:1.6;">
          Permanent deletion requested for:<br>
          <strong style="color:#0f172a;">{to_email}</strong></p>
        <p style="color:#ef4444;font-weight:600;">This action is irreversible.</p>
        <div style="text-align:center;margin:32px 0;">
          <a href="{conf}" style="background:#dc2626;color:white;padding:14px 32px;
             border-radius:10px;text-decoration:none;font-weight:700;
             display:inline-block;margin-bottom:14px;">Yes, Delete My Account</a><br>
          <a href="{canc}" style="background:#0f172a;color:white;padding:14px 32px;
             border-radius:10px;text-decoration:none;font-weight:700;
             display:inline-block;">Cancel – Keep My Account Safe</a>
        </div>
        <p style="color:#94a3b8;font-size:13px;text-align:center;">
          Expires in 24 hours. If you didn't request this, ignore this email.</p>
      </div>
    </div>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "SarSa AI – Confirm Account Deletion"
        msg["From"]    = st.secrets["SMTP_USER"]
        msg["To"]      = to_email
        msg.attach(MIMEText(body, "html"))
        host = st.secrets.get("SMTP_HOST","smtp.gmail.com")
        port = int(st.secrets.get("SMTP_PORT", 587))
        with smtplib.SMTP(host, port) as s:
            s.ehlo(); s.starttls()
            s.login(st.secrets["SMTP_USER"], st.secrets["SMTP_PASS"])
            s.sendmail(st.secrets["SMTP_USER"], to_email, msg.as_string())
        return True, ""
    except Exception as e:
        return False, str(e)

# ─── HELPER: email registered? ────────────────────────────────────────────────
def is_email_registered(email):
    try:
        svc   = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"])
        users = svc.auth.admin.list_users()
        return email.lower().strip() in [u.email.lower() for u in users if u.email]
    except Exception:
        return True

# ─── QUERY PARAMS (ROUTING) ───────────────────────────────────────────────────
qp = st.query_params

if qp.get("error"):
    error_msg = qp.get("error_description", qp.get("error"))
    st.error(f"⚠️ Verification Error: {error_msg}. The link may have expired.")
    st.query_params.clear()

if qp.get("action") == "confirm_delete":
    token = qp.get("token","")
    try:
        row = supabase.table("pending_deletions").select("*").eq("confirm_token",token).execute()
        if row.data:
            rec = row.data[0]
            exp = datetime.fromisoformat(rec["expires_at"].replace("Z","+00:00"))
            if datetime.now(timezone.utc) < exp:
                try:
                    svc = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"])
                    svc.auth.admin.delete_user(rec["user_id"])
                except Exception as e:
                    st.error(f"Deletion error: {e}"); st.stop()
                supabase.table("pending_deletions").delete().eq("confirm_token",token).execute()
                for k in ["is_logged_in","user_email","access_token","refresh_token"]:
                    st.session_state[k] = False if k=="is_logged_in" else None
                clear_auth_cookies()
                st.query_params.clear()
                st.markdown("""<div style='text-align:center;padding:5rem 2rem;'>
                  <div style='font-size:5rem;'>👋</div>
                  <h1 style='color:#0f172a;font-weight:800;'>Account Deleted</h1>
                  <p style='color:#475569;font-size:1.15rem;line-height:1.7;margin-top:1rem;'>
                    Your SarSa AI account has been <strong>permanently deleted</strong>.<br>
                    All data removed.</p>
                  <p style='color:#94a3b8;margin-top:2rem;'>You have been logged out.</p>
                </div>""", unsafe_allow_html=True)
                st.stop()
            else:
                st.error("Link expired (24h). Please request deletion again."); st.stop()
        else:
            st.error("Invalid or already-used link."); st.stop()
    except Exception as e:
        st.error(f"Error: {e}"); st.stop()

if qp.get("action") == "cancel_delete":
    try:
        supabase.table("pending_deletions").delete().eq("cancel_token",qp.get("token","")).execute()
    except Exception:
        pass
    st.query_params.clear()
    st.success("Account deletion cancelled. Your account is safe! ✅")
    time.sleep(2); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PKCE ?code= HANDLER — (TAMAMEN YENİLENMİŞ VE DROPPIN EKLENMİŞ BLOK)
# ══════════════════════════════════════════════════════════════════════════════
if qp.get("code"):
    code = qp.get("code")
    flow_type = qp.get("type", "recovery")

    try:
        # Koddan token alımı (explicit single-arg form)
        resp = supabase.auth.exchange_code_for_session(code)
    except Exception as e:
        st.error(f"Auth exchange failed (Link expired or used): {e}")
        st.query_params.clear()
        time.sleep(2)
        st.rerun()

    access_token = None
    refresh_token = None
    try:
        if isinstance(resp, dict):
            sess = resp.get("data", {}).get("session") or resp.get("session") or resp.get("data")
            if isinstance(sess, dict):
                access_token = sess.get("access_token") or sess.get("accessToken")
                refresh_token = sess.get("refresh_token") or sess.get("refreshToken")
        else:
            sess = getattr(resp, "session", None) or resp
            access_token = getattr(sess, "access_token", None) or getattr(sess, "accessToken", None)
            refresh_token = getattr(sess, "refresh_token", None) or getattr(sess, "refreshToken", None)
    except Exception:
        pass

    if access_token:
        try:
            supabase.auth.set_session(access_token, refresh_token)
            st.session_state.access_token = access_token
            st.session_state.refresh_token = refresh_token
            save_auth_cookies(access_token, refresh_token)
        except Exception as e:
            st.error(f"Could not set session after exchange: {e}")
            st.query_params.clear()
            st.stop()
    else:
        try:
            gs = supabase.auth.get_session()
            if isinstance(gs, dict):
                sess = gs.get("data", {}).get("session") or gs.get("session") or gs.get("data")
                if isinstance(sess, dict):
                    st.session_state.access_token = sess.get("access_token")
                    st.session_state.refresh_token = sess.get("refresh_token")
            else:
                st.session_state.access_token = getattr(gs, "access_token", None) or getattr(gs, "accessToken", None)
                st.session_state.refresh_token = getattr(gs, "refresh_token", None) or getattr(gs, "refreshToken", None)
        except Exception:
            pass

    st.query_params.clear()

    # Yönlendirmeyi burada state üzerinden yapıyoruz
    if flow_type == "signup":
        st.session_state.show_email_confirmed = True
        st.rerun()
    else:
        st.session_state.recovery_mode = True
        if st.session_state.access_token:
            st.session_state.is_logged_in = True
        st.rerun()

# ─── TEXT DICTS ───────────────────────────────────────────────────────────────
# (Tüm dillerin buradadır, eksiltilmemiştir)
auth_texts = {
    "English": {
        "login":"Login","register":"Register","email":"Email","password":"Password",
        "btn_login":"Login","btn_reg":"Create Account",
        "success_reg":"Registration successful! Check your email to verify your account.",
        "error_login":"Login failed. You are not registered, or your Email/Password is incorrect.",
        "verify_msg":"Please verify your email first:",
        "welcome_title":"Welcome to SarSa AI",
        "welcome_desc":"The All-in-One Visual Property Intelligence & Global Sales Automation platform. Transform your property photos into professional assets in seconds.",
        "login_prompt":"Log in to use the application",
        "forgot_pw":"Forgot Password?","btn_reset":"Send Reset Link",
        "reset_success":"Password reset link sent! Check your inbox.",
        "reset_not_found":"No account found with this email. Please register first.",
        "reset_invalid_email":"Please enter a valid email address.",
        "confirmed_title":"✅ Email Verified Successfully!",
        "confirmed_msg":"Your SarSa AI account has been confirmed and is ready to use.",
        "confirmed_sub":"Click the button below to proceed to the login page.",
        "confirmed_btn":"🔑 Go to Login",
        "pw_reset_title":"Set Your New Password",
        "pw_reset_desc":"Enter a new password for your account. You will be logged in automatically after saving.",
        "pw_reset_btn":"✅ Save Password & Login",
        "pw_reset_cancel":"❌ Cancel",
        "pw_reset_success":"✅ Password updated! Logging you in…",
        "pw_reset_min_err":"❌ Password must be at least 6 characters.",
        "new_pw_label":"New Password",
    },
    "Türkçe": {
        "login":"Giriş Yap","register":"Kayıt Ol","email":"E-posta","password":"Şifre",
        "btn_login":"Oturum Aç","btn_reg":"Hesap Oluştur",
        "success_reg":"Kayıt başarılı! Hesabınızı onaylamak için e-postanızı kontrol edin.",
        "error_login":"Giriş başarısız. Kayıtlı değilsiniz veya E-posta/Şifreniz hatalı.",
        "verify_msg":"Lütfen önce e-postanızı onaylayın:",
        "welcome_title":"SarSa AI'a Hoş Geldiniz",
        "welcome_desc":"Hepsi Bir Arada Görsel Mülk Zekâsı ve Küresel Satış Otomasyonu platformu. Mülk fotoğraflarınızı saniyeler içinde profesyonel varlıklara dönüştürün.",
        "login_prompt":"Uygulamayı kullanmak için giriş yapın",
        "forgot_pw":"Şifremi Unuttum?","btn_reset":"Sıfırlama Bağlantısı Gönder",
        "reset_success":"Şifre sıfırlama bağlantısı gönderildi! Gelen kutunuzu kontrol edin.",
        "reset_not_found":"Bu e-posta ile kayıtlı hesap bulunamadı. Lütfen önce kayıt olun.",
        "reset_invalid_email":"Lütfen geçerli bir e-posta adresi girin.",
        "confirmed_title":"✅ E-posta Başarıyla Doğrulandı!",
        "confirmed_msg":"SarSa AI hesabınız onaylandı ve kullanıma hazır.",
        "confirmed_sub":"Giriş sayfasına geçmek için aşağıdaki butona tıklayın.",
        "confirmed_btn":"🔑 Giriş Sayfasına Git",
        "pw_reset_title":"Yeni Şifrenizi Belirleyin",
        "pw_reset_desc":"Hesabınız için yeni bir şifre girin. Kaydettikten sonra otomatik giriş yapılacak.",
        "pw_reset_btn":"✅ Şifreyi Kaydet ve Giriş Yap",
        "pw_reset_cancel":"❌ İptal",
        "pw_reset_success":"✅ Şifre güncellendi! Giriş yapılıyor…",
        "pw_reset_min_err":"❌ Şifre en az 6 karakter olmalıdır.",
        "new_pw_label":"Yeni Şifre",
    },
    "Español": {
        "login":"Iniciar Sesión","register":"Registrarse","email":"Correo","password":"Clave",
        "btn_login":"Entrar","btn_reg":"Crear Cuenta",
        "success_reg":"¡Registro exitoso! Revisa tu email para verificar tu cuenta.",
        "error_login":"Error. No estás registrado o tu Correo/Clave es incorrecto.",
        "verify_msg":"Por favor verifica tu email primero:",
        "welcome_title":"Bienvenido a SarSa AI",
        "welcome_desc":"La plataforma todo en uno de Inteligencia Visual de Propiedades. Transforme sus fotos en activos profesionales en segundos.",
        "login_prompt":"Inicie sesión para usar la aplicación",
        "forgot_pw":"¿Olvidaste tu contraseña?","btn_reset":"Enviar enlace",
        "reset_success":"¡Enlace enviado! Revisa tu bandeja de entrada.",
        "reset_not_found":"No se encontró ninguna cuenta con este correo.",
        "reset_invalid_email":"Por favor ingresa un correo válido.",
        "confirmed_title":"✅ ¡Email Verificado Exitosamente!",
        "confirmed_msg":"Tu cuenta de SarSa AI ha sido confirmada y está lista para usar.",
        "confirmed_sub":"Haz clic abajo para ir a la página de inicio de sesión.",
        "confirmed_btn":"🔑 Ir al Login",
        "pw_reset_title":"Establece tu Nueva Contraseña",
        "pw_reset_desc":"Ingresa una nueva contraseña. Iniciarás sesión automáticamente al guardar.",
        "pw_reset_btn":"✅ Guardar Contraseña e Iniciar Sesión",
        "pw_reset_cancel":"❌ Cancelar",
        "pw_reset_success":"✅ ¡Contraseña actualizada! Iniciando sesión…",
        "pw_reset_min_err":"❌ Mínimo 6 caracteres requeridos.",
        "new_pw_label":"Nueva Contraseña",
    },
    "Deutsch": {
        "login":"Anmelden","register":"Registrieren","email":"E-Mail","password":"Passwort",
        "btn_login":"Login","btn_reg":"Konto Erstellen",
        "success_reg":"Erfolgreich! Bitte bestätigen Sie Ihre E-Mail.",
        "error_login":"Login fehlgeschlagen. Nicht registriert oder E-Mail/Passwort falsch.",
        "verify_msg":"Bitte bestätigen Sie zuerst Ihre E-Mail:",
        "welcome_title":"Willkommen bei SarSa AI",
        "welcome_desc":"Die All-in-One-Plattform für visuelle Immobilienintelligenz. Verwandeln Sie Fotos in Sekundenschnelle in professionelle Assets.",
        "login_prompt":"Melden Sie sich an, um die App zu nutzen",
        "forgot_pw":"Passwort vergessen?","btn_reset":"Link senden",
        "reset_success":"Link gesendet! Überprüfen Sie Ihren Posteingang.",
        "reset_not_found":"Kein Konto mit dieser E-Mail gefunden.",
        "reset_invalid_email":"Bitte gültige E-Mail-Adresse eingeben.",
        "confirmed_title":"✅ E-Mail erfolgreich verifiziert!",
        "confirmed_msg":"Ihr SarSa AI-Konto wurde bestätigt und ist einsatzbereit.",
        "confirmed_sub":"Klicken Sie unten, um zur Anmeldeseite zu gelangen.",
        "confirmed_btn":"🔑 Zur Anmeldung",
        "pw_reset_title":"Neues Passwort festlegen",
        "pw_reset_desc":"Geben Sie ein neues Passwort ein. Sie werden automatisch eingeloggt.",
        "pw_reset_btn":"✅ Passwort speichern & einloggen",
        "pw_reset_cancel":"❌ Abbrechen",
        "pw_reset_success":"✅ Passwort aktualisiert! Einloggen…",
        "pw_reset_min_err":"❌ Mindestens 6 Zeichen erforderlich.",
        "new_pw_label":"Neues Passwort",
    },
    "Français": {
        "login":"Connexion","register":"S'inscrire","email":"Email","password":"Mot de passe",
        "btn_login":"Se connecter","btn_reg":"Créer un compte",
        "success_reg":"Succès ! Vérifiez vos emails pour confirmer.",
        "error_login":"Échec. Vous n'êtes pas inscrit ou Email/Mot de passe incorrect.",
        "verify_msg":"Veuillez d'abord vérifier votre email :",
        "welcome_title":"Bienvenue sur SarSa AI",
        "welcome_desc":"La plateforme d'Intelligence Visuelle Immobilière. Transformez vos photos en atouts professionnels en quelques secondes.",
        "login_prompt":"Connectez-vous pour utiliser l'application",
        "forgot_pw":"Mot de passe oublié ?","btn_reset":"Envoyer le lien",
        "reset_success":"Lien envoyé ! Vérifiez votre boîte de réception.",
        "reset_not_found":"Aucun compte trouvé avec cet email.",
        "reset_invalid_email":"Veuillez entrer une adresse email valide.",
        "confirmed_title":"✅ Email vérifié avec succès !",
        "confirmed_msg":"Votre compte SarSa AI a été confirmé et est prêt à l'emploi.",
        "confirmed_sub":"Cliquez ci-dessous pour accéder à la page de connexion.",
        "confirmed_btn":"🔑 Aller à la connexion",
        "pw_reset_title":"Définissez votre nouveau mot de passe",
        "pw_reset_desc":"Entrez un nouveau mot de passe. Vous serez connecté automatiquement après.",
        "pw_reset_btn":"✅ Enregistrer & Se connecter",
        "pw_reset_cancel":"❌ Annuler",
        "pw_reset_success":"✅ Mot de passe mis à jour ! Connexion en cours…",
        "pw_reset_min_err":"❌ 6 caractères minimum.",
        "new_pw_label":"Nouveau mot de passe",
    },
    "Português": {
        "login":"Entrar","register":"Registar","email":"Email","password":"Senha",
        "btn_login":"Login","btn_reg":"Criar Conta",
        "success_reg":"Sucesso! Verifique seu email para confirmar a conta.",
        "error_login":"Falha. Não registado ou Email/Senha incorretos.",
        "verify_msg":"Por favor verifique primeiro o seu email:",
        "welcome_title":"Bem-vindo ao SarSa AI",
        "welcome_desc":"A plataforma tudo-em-um de Inteligência Imobiliária Visual. Transforme as suas fotos em ativos profissionais em segundos.",
        "login_prompt":"Faça login para usar o aplicativo",
        "forgot_pw":"Esqueceu a senha?","btn_reset":"Enviar link",
        "reset_success":"Link enviado! Verifique sua caixa de entrada.",
        "reset_not_found":"Nenhuma conta encontrada com este email.",
        "reset_invalid_email":"Por favor insira um endereço de email válido.",
        "confirmed_title":"✅ Email Verificado com Sucesso!",
        "confirmed_msg":"Sua conta SarSa AI foi confirmada e está pronta para uso.",
        "confirmed_sub":"Clique abaixo para ir à página de login e começar.",
        "confirmed_btn":"🔑 Ir para o Login",
        "pw_reset_title":"Defina sua Nova Senha",
        "pw_reset_desc":"Insira uma nova senha. Você será logado automaticamente após salvar.",
        "pw_reset_btn":"✅ Salvar Senha & Entrar",
        "pw_reset_cancel":"❌ Cancelar",
        "pw_reset_success":"✅ Senha atualizada! Entrando…",
        "pw_reset_min_err":"❌ Mínimo de 6 caracteres.",
        "new_pw_label":"Nova Senha",
    },
    "日本語": {
        "login":"ログイン","register":"新規登録","email":"メール","password":"パスワード",
        "btn_login":"ログイン","btn_reg":"アカウント作成",
        "success_reg":"登録完了！メールを確認してアカウントを認証してください。",
        "error_login":"ログイン失敗。未登録か、メール/パスワードが間違っています。",
        "verify_msg":"まずメールを認証してください：",
        "welcome_title":"SarSa AI へようこそ",
        "welcome_desc":"オールインワンの視覚的物件インテリジェンス＆販売自動化プラットフォーム。物件の写真を数秒でプロフェッショナルな資産に変換します。",
        "login_prompt":"アプリを使用するにはログインしてください",
        "forgot_pw":"パスワードをお忘れですか？","btn_reset":"リンクを送信",
        "reset_success":"リセットリンクを送信しました！受信トレイをご確認ください。",
        "reset_not_found":"このメールアドレスのアカウントが見つかりません。",
        "reset_invalid_email":"有効なメールアドレスを入力してください。",
        "confirmed_title":"✅ メールが正常に認証されました！",
        "confirmed_msg":"SarSa AI アカウントが確認され、ご利用いただけます。",
        "confirmed_sub":"下のボタンをクリックしてログインページに移動してください。",
        "confirmed_btn":"🔑 ログインページへ",
        "pw_reset_title":"新しいパスワードを設定",
        "pw_reset_desc":"新しいパスワードを入力してください。保存後に自動的にログインされます。",
        "pw_reset_btn":"✅ パスワードを保存してログイン",
        "pw_reset_cancel":"❌ キャンセル",
        "pw_reset_success":"✅ パスワードが更新されました！ログイン中…",
        "pw_reset_min_err":"❌ 6文字以上必要です。",
        "new_pw_label":"新しいパスワード",
    },
    "简体中文": {
        "login":"登录","register":"注册","email":"邮箱","password":"密码",
        "btn_login":"登录","btn_reg":"创建账号",
        "success_reg":"注册成功！请检查邮箱以验证账号。",
        "error_login":"登录失败。您未注册，或邮箱/密码错误。",
        "verify_msg":"请先验证您的邮箱：",
        "welcome_title":"欢迎来到 SarSa AI",
        "welcome_desc":"全方位房产视觉智能与全球销售自动化平台。在几秒钟内将您的房产照片转化为专业的营销资产。",
        "login_prompt":"登录以使用该应用程序",
        "forgot_pw":"忘记密码？","btn_reset":"发送重置链接",
        "reset_success":"重置链接已发送！请检查您的邮箱。",
        "reset_not_found":"未找到使用此邮箱注册的账号，请先注册。",
        "reset_invalid_email":"请输入有效的电子邮件地址。",
        "confirmed_title":"✅ 邮箱验证成功！",
        "confirmed_msg":"您的 SarSa AI 账户已确认，可以开始使用。",
        "confirmed_sub":"点击下方按钮前往登录页面开始使用。",
        "confirmed_btn":"🔑 前往登录",
        "pw_reset_title":"设置您的新密码",
        "pw_reset_desc":"为您的账号输入新密码。保存后将自动登录。",
        "pw_reset_btn":"✅ 保存密码并登录",
        "pw_reset_cancel":"❌ 取消",
        "pw_reset_success":"✅ 密码已更新！正在登录…",
        "pw_reset_min_err":"❌ 密码至少需要6位。",
        "new_pw_label":"新密码",
    },
    "العربية": {
        "login":"تسجيل الدخول","register":"إنشاء حساب","email":"البريد","password":"كلمة السر",
        "btn_login":"دخول","btn_reg":"إنشاء حساب",
        "success_reg":"تم التسجيل بنجاح! تحقق من بريدك لتأكيد الحساب.",
        "error_login":"فشل الدخول. أنت غير مسجل، أو البريد/كلمة السر خاطئة.",
        "verify_msg":"يرجى تأكيد بريدك الإلكتروني أولاً:",
        "welcome_title":"مرحباً بك في SarSa AI",
        "welcome_desc":"منصة الذكاء البصري المتكامل للعقارات وأتمتة المبيعات العالمية. حول صور عقاراتك إلى أصول احترافية في ثوانٍ.",
        "login_prompt":"قم بتسجيل الدخول لاستخدام التطبيق",
        "forgot_pw":"نسيت كلمة السر؟","btn_reset":"إرسال رابط الاستعادة",
        "reset_success":"تم إرسال رابط إعادة التعيين! تحقق من صندوق الوارد.",
        "reset_not_found":"لم يتم العثور على حساب بهذا البريد.",
        "reset_invalid_email":"يرجى إدخال عنوان بريد إلكتروني صالح.",
        "confirmed_title":"✅ تم التحقق من البريد بنجاح!",
        "confirmed_msg":"تم تأكيد حساب SarSa AI الخاص بك وهو جاهز للاستخدام.",
        "confirmed_sub":"انقر على الزر أدناه للانتقال إلى صفحة تسجيل الدخول.",
        "confirmed_btn":"🔑 الذهاب إلى تسجيل الدخول",
        "pw_reset_title":"تعيين كلمة المرور الجديدة",
        "pw_reset_desc":"أدخل كلمة مرور جديدة لحسابك. سيتم تسجيل دخولك تلقائياً بعد الحفظ.",
        "pw_reset_btn":"✅ حفظ كلمة المرور وتسجيل الدخول",
        "pw_reset_cancel":"❌ إلغاء",
        "pw_reset_success":"✅ تم تحديث كلمة المرور! جاري تسجيل الدخول…",
        "pw_reset_min_err":"❌ يجب أن تكون 6 خانات على الأقل.",
        "new_pw_label":"كلمة المرور الجديدة",
    },
}

ui_languages = {
    "English": {
        "title":"SarSa AI | Real Estate Intelligence Platform",
        "service_desc":"All-in-One Visual Property Intelligence & Global Sales Automation",
        "subtitle":"Transform property photos into premium listings, social media kits, cinematic video scripts, technical specs, email campaigns and SEO copy — instantly.",
        "settings":"Configuration","target_lang":"Write Listing In…","prop_type":"Property Type",
        "price":"Market Price","location":"Location","tone":"Marketing Strategy",
        "tones":["Standard Pro","Ultra-Luxury","Investment Focus","Modern Minimalist","Family Living","Vacation Rental","Commercial"],
        "ph_prop":"E.g., 3+1 Apartment, Luxury Villa…","ph_price":"E.g., $850,000 or £2,000/mo…",
        "ph_loc":"E.g., Manhattan, NY or Dubai Marina…","bedrooms":"Bedrooms","bathrooms":"Bathrooms",
        "area":"Area","year_built":"Year Built","ph_beds":"E.g., 3","ph_baths":"E.g., 2",
        "ph_area":"E.g., 185 sqm","ph_year":"E.g., 2022","furnishing":"Furnishing",
        "furnishing_opts":["Not Specified","Fully Furnished","Semi-Furnished","Unfurnished"],
        "target_audience":"Target Audience",
        "audience_opts":["General Market","Luxury Buyers","Investors & ROI Focus","Expats & Internationals","First-Time Buyers","Vacation / Holiday Market","Commercial Tenants"],
        "custom_inst":"Special Notes & Highlights","custom_inst_ph":"E.g., Private pool, panoramic sea view, smart home…",
        "btn":"GENERATE SELECTED ASSETS","upload_label":"Drop Property Photos Here",
        "result":"Executive Preview","loading":"Crafting your premium marketing ecosystem…",
        "empty":"Upload property photos and fill in the details on the left to generate complete professional marketing assets.",
        "download":"Export Section (TXT)","save_btn":"Save Changes","saved_msg":"Saved!",
        "error":"Error:","clear_btn":"Reset Form","select_sections":"Select Assets to Generate",
        "tab_main":"Prime Listing","tab_social":"Social Media Kit","tab_video":"Video Scripts",
        "tab_tech":"Technical Specs","tab_email":"Email Campaign","tab_seo":"SEO & Web Copy","tab_photo":"Photo Guide",
        "label_main":"Sales Copy","label_social":"Social Media Content","label_video":"Video Script",
        "label_tech":"Technical Specifications","label_email":"Email Campaign","label_seo":"SEO & Web Copy",
        "label_photo":"Photography Recommendations","extra_details":"Extra Property Details",
        "interface_lang":"Interface Language","logout":"Logout","acc_settings":"Account Settings",
        "update_pw":"Update Password","new_pw":"New Password","btn_update":"Update Now",
        "danger_zone":"Danger Zone","delete_confirm":"I want to permanently delete my account.",
        "btn_delete":"Delete Account","pw_min_err":"Minimum 6 characters required.",
        "delete_email_sent":"Confirmation email sent! Check your inbox.",
        "delete_email_fail":"Failed to send email. Please check SMTP settings.",
    },
    "Türkçe": {
        "title":"SarSa AI | Gayrimenkul Zekâ Platformu",
        "service_desc":"Hepsi Bir Arada Görsel Mülk Zekâsı ve Küresel Satış Otomasyonu",
        "subtitle":"Mülk fotoğraflarını anında profesyonel ilanlara, sosyal medya kitlerine, sinematik senaryolara, teknik şartnamelere, e-posta kampanyalarına ve SEO metinlerine dönüştürün.",
        "settings":"Yapılandırma","target_lang":"İlan Yazım Dili…","prop_type":"Emlak Tipi",
        "price":"Pazar Fiyatı","location":"Konum","tone":"Pazarlama Stratejisi",
        "tones":["Standart Profesyonel","Ultra-Lüks","Yatırım Odaklı","Modern Minimalist","Aile Yaşamı","Tatil Kiralık","Ticari"],
        "ph_prop":"Örn: 3+1 Daire, Müstakil Villa…","ph_price":"Örn: 5.000.000 TL veya $2.500/ay…",
        "ph_loc":"Örn: Beşiktaş, İstanbul veya Dubai Marina…","bedrooms":"Yatak Odası","bathrooms":"Banyo",
        "area":"Alan","year_built":"İnşaat Yılı","ph_beds":"Örn: 3","ph_baths":"Örn: 2",
        "ph_area":"Örn: 185 m²","ph_year":"Örn: 2022","furnishing":"Eşya Durumu",
        "furnishing_opts":["Belirtilmedi","Tam Eşyalı","Yarı Eşyalı","Eşyasız"],
        "target_audience":"Hedef Kitle",
        "audience_opts":["Genel Pazar","Lüks Alıcılar","Yatırımcılar & ROI Odaklı","Yabancılar & Uluslararası","İlk Ev Alıcıları","Tatil / Kiralık Pazar","Ticari Kiracılar"],
        "custom_inst":"Özel Notlar ve Öne Çıkan Özellikler","custom_inst_ph":"Örn: Özel havuz, panoramik manzara, akıllı ev…",
        "btn":"SEÇİLİ VARLIKLARI OLUŞTUR","upload_label":"Fotoğrafları Buraya Bırakın",
        "result":"Yönetici Önizlemesi","loading":"Premium pazarlama ekosisteminiz hazırlanıyor…",
        "empty":"Profesyonel analiz için görsel bekleniyor. Fotoğrafları yükleyin ve soldaki bilgileri doldurun.",
        "download":"Bölümü İndir (TXT)","save_btn":"Kaydet","saved_msg":"Kaydedildi!",
        "error":"Hata:","clear_btn":"Formu Temizle","select_sections":"Oluşturulacak Bölümleri Seçin",
        "tab_main":"Ana İlan","tab_social":"Sosyal Medya Kiti","tab_video":"Video Senaryoları",
        "tab_tech":"Teknik Özellikler","tab_email":"E-posta Kampanyası","tab_seo":"SEO & Web Metni","tab_photo":"Fotoğraf Rehberi",
        "label_main":"Satış Metni","label_social":"Sosyal Medya","label_video":"Video Script",
        "label_tech":"Teknik Detaylar","label_email":"E-posta Kampanyası","label_seo":"SEO & Web Metni",
        "label_photo":"Fotoğraf Tavsiyeleri","extra_details":"Ek Mülk Detayları",
        "interface_lang":"Arayüz Dili","logout":"Çıkış Yap","acc_settings":"Hesap Ayarları",
        "update_pw":"Şifre Güncelle","new_pw":"Yeni Şifre","btn_update":"Şifreyi Güncelle",
        "danger_zone":"Tehlikeli Bölge","delete_confirm":"Hesabımı kalıcı olarak silmek istiyorum.",
        "btn_delete":"Hesabı Sil","pw_min_err":"Şifre en az 6 karakter olmalıdır.",
        "delete_email_sent":"Onay e-postası gönderildi! Gelen kutunuzu kontrol edin.",
        "delete_email_fail":"E-posta gönderilemedi. SMTP ayarlarını kontrol edin.",
    },
    "Español": {
        "title":"SarSa AI | Plataforma de Inteligencia Inmobiliaria",
        "service_desc":"Inteligencia Visual de Propiedades y Automatización de Ventas Globales",
        "subtitle":"Convierta fotos en anuncios premium, kits de redes sociales, guiones de video, fichas técnicas, campañas de email y copy SEO al instante.",
        "settings":"Configuración","target_lang":"Escribir en…","prop_type":"Tipo de Propiedad",
        "price":"Precio de Mercado","location":"Ubicación","tone":"Estrategia de Marketing",
        "tones":["Profesional Estándar","Ultra-Lujo","Enfoque de Inversión","Minimalista Moderno","Vida Familiar","Alquiler Vacacional","Comercial"],
        "ph_prop":"Ej: Apartamento 3+1, Villa de Lujo…","ph_price":"Ej: $850.000 o EUR 1.500/mes…",
        "ph_loc":"Ej: Madrid, España o Marbella…","bedrooms":"Dormitorios","bathrooms":"Baños",
        "area":"Área","year_built":"Año de Construcción","ph_beds":"Ej: 3","ph_baths":"Ej: 2",
        "ph_area":"Ej: 185 m²","ph_year":"Ej: 2022","furnishing":"Amueblado",
        "furnishing_opts":["No especificado","Completamente Amueblado","Semi-Amueblado","Sin Amueblar"],
        "target_audience":"Público Objetivo",
        "audience_opts":["Mercado General","Compradores de Lujo","Inversores & ROI","Extranjeros & Internacionales","Primeros Compradores","Mercado Vacacional","Inquilinos Comerciales"],
        "custom_inst":"Notas Especiales","custom_inst_ph":"Ej: Piscina privada, vistas al mar, domótica…",
        "btn":"GENERAR ACTIVOS SELECCIONADOS","upload_label":"Subir Fotos de la Propiedad",
        "result":"Vista Previa Ejecutiva","loading":"Creando su ecosistema de marketing premium…",
        "empty":"Esperando imágenes. Suba fotos y complete los detalles a la izquierda.",
        "download":"Exportar Sección (TXT)","save_btn":"Guardar","saved_msg":"¡Guardado!",
        "error":"Error:","clear_btn":"Limpiar","select_sections":"Seleccionar Secciones",
        "tab_main":"Anuncio Premium","tab_social":"Kit de Redes Sociales","tab_video":"Guiones de Video",
        "tab_tech":"Especificaciones","tab_email":"Campaña de Email","tab_seo":"SEO & Web Copy","tab_photo":"Guía de Fotos",
        "label_main":"Texto de Ventas","label_social":"Contenido Social","label_video":"Guion de Video",
        "label_tech":"Ficha Técnica","label_email":"Campaña de Email","label_seo":"SEO & Web Copy",
        "label_photo":"Recomendaciones de Fotografía","extra_details":"Detalles Adicionales",
        "interface_lang":"Idioma de Interfaz","logout":"Cerrar Sesión","acc_settings":"Cuenta",
        "update_pw":"Actualizar Contraseña","new_pw":"Nueva Contraseña","btn_update":"Actualizar Ahora",
        "danger_zone":"Zona de Peligro","delete_confirm":"Quiero eliminar mi cuenta permanentemente.",
        "btn_delete":"Eliminar Cuenta","pw_min_err":"Mínimo 6 caracteres requeridos.",
        "delete_email_sent":"Email de confirmación enviado! Revisa tu bandeja.",
        "delete_email_fail":"Error al enviar email. Verifique la configuración SMTP.",
    },
    "Deutsch": {
        "title":"SarSa AI | Immobilien-Intelligenz-Plattform",
        "service_desc":"All-in-One Visuelle Objektintelligenz & Globale Verkaufsautomatisierung",
        "subtitle":"Verwandeln Sie Fotos sofort in Premium-Exposés, Social-Media-Kits, Videoskripte, Datenblätter, E-Mail-Kampagnen und SEO-Texte.",
        "settings":"Konfiguration","target_lang":"Erstellen in…","prop_type":"Objekttyp",
        "price":"Marktpreis","location":"Standort","tone":"Marketingstrategie",
        "tones":["Standard-Profi","Ultra-Luxus","Investitionsfokus","Modern-Minimalistisch","Familienleben","Ferienmiete","Gewerbe"],
        "ph_prop":"Z.B. 3-Zimmer-Wohnung, Luxusvilla…","ph_price":"Z.B. 850.000€ oder 2.000€/Monat…",
        "ph_loc":"Z.B. Berlin oder Hamburg…","bedrooms":"Schlafzimmer","bathrooms":"Badezimmer",
        "area":"Fläche","year_built":"Baujahr","ph_beds":"Z.B. 3","ph_baths":"Z.B. 2",
        "ph_area":"Z.B. 185 m²","ph_year":"Z.B. 2022","furnishing":"Möblierung",
        "furnishing_opts":["Nicht angegeben","Vollmöbliert","Teilmöbliert","Unmöbliert"],
        "target_audience":"Zielgruppe",
        "audience_opts":["Allgemeiner Markt","Luxuskäufer","Investoren & ROI","Expats & Internationale","Erstkäufer","Ferienmarkt","Gewerbemieter"],
        "custom_inst":"Notizen & Besonderheiten","custom_inst_ph":"Z.B. Privatpool, Panoramasicht, Smart-Home…",
        "btn":"AUSGEWÄHLTE ASSETS ERSTELLEN","upload_label":"Fotos hier hochladen",
        "result":"Executive-Vorschau","loading":"Ihr Marketing-Ökosystem wird erstellt…",
        "empty":"Warte auf Bilder. Laden Sie Fotos hoch und füllen Sie die Details aus.",
        "download":"Abschnitt Exportieren (TXT)","save_btn":"Speichern","saved_msg":"Gespeichert!",
        "error":"Fehler:","clear_btn":"Zurücksetzen","select_sections":"Bereiche wählen",
        "tab_main":"Premium-Exposé","tab_social":"Social Media Kit","tab_video":"Videoskripte",
        "tab_tech":"Tech-Details","tab_email":"E-Mail-Kampagne","tab_seo":"SEO & Webtext","tab_photo":"Foto-Guide",
        "label_main":"Verkaufstext","label_social":"Social-Media-Content","label_video":"Videoskript",
        "label_tech":"Technische Daten","label_email":"E-Mail-Kampagne","label_seo":"SEO & Webtext",
        "label_photo":"Fotografie-Empfehlungen","extra_details":"Weitere Details",
        "interface_lang":"Oberfläche Sprache","logout":"Abmelden","acc_settings":"Kontoeinstellungen",
        "update_pw":"Passwort ändern","new_pw":"Neues Passwort","btn_update":"Jetzt aktualisieren",
        "danger_zone":"Gefahrenzone","delete_confirm":"Ich möchte mein Konto dauerhaft löschen.",
        "btn_delete":"Konto löschen","pw_min_err":"Mindestens 6 Zeichen erforderlich.",
        "delete_email_sent":"Bestätigungs-E-Mail gesendet! Überprüfen Sie Ihren Posteingang.",
        "delete_email_fail":"E-Mail konnte nicht gesendet werden. SMTP-Einstellungen prüfen.",
    },
    "Français": {
        "title":"SarSa AI | Plateforme d'Intelligence Immobilière",
        "service_desc":"Intelligence Visuelle Immobilière et Automatisation des Ventes Globales",
        "subtitle":"Transformez vos photos en annonces premium, kits réseaux sociaux, scripts vidéo, fiches techniques, campagnes email et copy SEO instantanément.",
        "settings":"Configuration","target_lang":"Rédiger en…","prop_type":"Type de Bien",
        "price":"Prix du Marché","location":"Localisation","tone":"Stratégie Marketing",
        "tones":["Standard Pro","Ultra-Luxe","Focus Investissement","Minimaliste Moderne","Vie de Famille","Location Saisonnière","Commercial"],
        "ph_prop":"Ex: Appartement T4, Villa de Luxe…","ph_price":"Ex: 850.000€ ou 1.500€/mois…",
        "ph_loc":"Ex: Paris, Côte d'Azur ou Lyon…","bedrooms":"Chambres","bathrooms":"Salles de Bain",
        "area":"Surface","year_built":"Année de Construction","ph_beds":"Ex: 3","ph_baths":"Ex: 2",
        "ph_area":"Ex: 185 m²","ph_year":"Ex: 2022","furnishing":"Ameublement",
        "furnishing_opts":["Non spécifié","Entièrement Meublé","Semi-Meublé","Non Meublé"],
        "target_audience":"Audience Cible",
        "audience_opts":["Marché Général","Acheteurs de Luxe","Investisseurs & ROI","Expatriés & Internationaux","Primo-Accédants","Marché Vacances","Locataires Commerciaux"],
        "custom_inst":"Notes Spéciales & Points Forts","custom_inst_ph":"Ex: Piscine privée, vue panoramique, domotique…",
        "btn":"GÉNÉRER LES ACTIFS SÉLECTIONNÉS","upload_label":"Déposer les Photos Ici",
        "result":"Aperçu Exécutif","loading":"Préparation de votre écosystème marketing…",
        "empty":"En attente d'images. Déposez des photos et remplissez les détails à gauche.",
        "download":"Exporter Section (TXT)","save_btn":"Enregistrer","saved_msg":"Enregistré !",
        "error":"Erreur:","clear_btn":"Réinitialiser","select_sections":"Sélectionner les sections",
        "tab_main":"Annonce Premium","tab_social":"Kit Réseaux Sociaux","tab_video":"Scripts Vidéo",
        "tab_tech":"Spécifications","tab_email":"Campagne Email","tab_seo":"SEO & Web Copy","tab_photo":"Guide Photo",
        "label_main":"Texte de Vente","label_social":"Contenu Social","label_video":"Script Vidéo",
        "label_tech":"Détails Techniques","label_email":"Campagne Email","label_seo":"SEO & Web Copy",
        "label_photo":"Recommandations Photo","extra_details":"Détails Supplémentaires",
        "interface_lang":"Langue Interface","logout":"Déconnexion","acc_settings":"Paramètres",
        "update_pw":"Changer MDP","new_pw":"Nouveau MDP","btn_update":"Mettre à jour",
        "danger_zone":"Zone de Danger","delete_confirm":"Supprimer définitivement mon compte.",
        "btn_delete":"Supprimer le compte","pw_min_err":"6 caractères minimum.",
        "delete_email_sent":"Email de confirmation envoyé ! Vérifiez votre boîte.",
        "delete_email_fail":"Échec d'envoi. Vérifiez les paramètres SMTP.",
    },
    "Português": {
        "title":"SarSa AI | Plataforma de Inteligência Imobiliária",
        "service_desc":"Inteligência Visual Imobiliária e Automação de Vendas Globais",
        "subtitle":"Transforme fotos em anúncios premium, kits de redes sociais, roteiros de vídeo, fichas técnicas, campanhas de email e copy SEO instantaneamente.",
        "settings":"Configuração","target_lang":"Escrever em…","prop_type":"Tipo de Imóvel",
        "price":"Preço de Mercado","location":"Localização","tone":"Estratégia de Marketing",
        "tones":["Profissional Padrão","Ultra-Luxo","Foco em Investimento","Minimalista Moderno","Vida Familiar","Aluguel de Temporada","Comercial"],
        "ph_prop":"Ex: Apartamento T3, Moradia de Luxo…","ph_price":"Ex: 500.000€ ou 1.500€/mês…",
        "ph_loc":"Ex: Lisboa, Algarve ou Porto…","bedrooms":"Quartos","bathrooms":"Banheiros",
        "area":"Área","year_built":"Ano de Construção","ph_beds":"Ex: 3","ph_baths":"Ex: 2",
        "ph_area":"Ex: 185 m²","ph_year":"Ex: 2022","furnishing":"Mobiliário",
        "furnishing_opts":["Não especificado","Completamente Mobilado","Semi-Mobilado","Sem Mobília"],
        "target_audience":"Público-Alvo",
        "audience_opts":["Mercado Geral","Compradores de Luxo","Investidores & ROI","Expats e Internacionais","Primeiros Compradores","Mercado de Férias","Inquilinos Comerciais"],
        "custom_inst":"Notas Especiais e Destaques","custom_inst_ph":"Ex: Piscina privativa, vista panorâmica, casa inteligente…",
        "btn":"GERAR ATIVOS SELECIONADOS","upload_label":"Enviar Fotos do Imóvel",
        "result":"Pré-visualização Executiva","loading":"Preparando seu ecossistema de marketing…",
        "empty":"Aaguardando imagens. Envie fotos e preencha os detalhes à esquerda.",
        "download":"Exportar Secção (TXT)","save_btn":"Salvar","saved_msg":"Salvo!",
        "error":"Erro:","clear_btn":"Limpar","select_sections":"Selecionar Seções",
        "tab_main":"Anúncio Premium","tab_social":"Kit Redes Sociais","tab_video":"Roteiros de Vídeo",
        "tab_tech":"Especificações","tab_email":"Campanha de Email","tab_seo":"SEO & Web Copy","tab_photo":"Guia de Fotos",
        "label_main":"Texto de Vendas","label_social":"Conteúdo Social","label_video":"Roteiro de Vídeo",
        "label_tech":"Especificações Técnicas","label_email":"Campanha Email","label_seo":"SEO & Web Copy",
        "label_photo":"Recomendações de Fotografia","extra_details":"Detalhes Adicionais",
        "interface_lang":"Idioma Interface","logout":"Sair","acc_settings":"Configurações",
        "update_pw":"Alterar Senha","new_pw":"Nova Senha","btn_update":"Atualizar Agora",
        "danger_zone":"Zona de Perigo","delete_confirm":"Quero excluir minha conta permanentemente.",
        "btn_delete":"Excluir Conta","pw_min_err":"Mínimo de 6 caracteres.",
        "delete_email_sent":"Email de confirmação enviado! Verifique sua caixa de entrada.",
        "delete_email_fail":"Falha ao enviar email. Verifique as configurações SMTP.",
    },
    "日本語": {
        "title":"SarSa AI | 不動産インテリジェンス・プラットフォーム",
        "service_desc":"オールインワン視覚的物件インテリジェンス＆グローバル販売自動化",
        "subtitle":"物件写真をプレミアム広告、SNSキット、動画台本、技術仕様書、メールキャンペーン、SEOコピーに瞬時に変換します。",
        "settings":"設定","target_lang":"作成言語…","prop_type":"物件種別",
        "price":"市場価格","location":"所在地","tone":"マーケティング戦略",
        "tones":["標準プロ","ウルトラ・ラグジュアリー","投資重視","モダン・ミニマリスト","ファミリー向け","バケーションレンタル","商業用"],
        "ph_prop":"例: 3LDKマンション、高級別荘…","ph_price":"例: 8500万円 または 月20万円…",
        "ph_loc":"例: 東京都港区、大阪、ドバイ…","bedrooms":"寝室数","bathrooms":"浴室数",
        "area":"面積","year_built":"建築年","ph_beds":"例: 3","ph_baths":"例: 2",
        "ph_area":"例: 185 m²","ph_year":"例: 2022","furnishing":"家具",
        "furnishing_opts":["未指定","フル家具付き","一部家具付き","家具なし"],
        "target_audience":"ターゲット層",
        "audience_opts":["一般市場","富裕層バイヤー","投資家 & ROI重視","海外居住者","初めての購入者","休暇・別荘市場","商業テナント"],
        "custom_inst":"特記事項 ＆ アピールポイント","custom_inst_ph":"例: プライベートプール、パノラマビュー、スマートホーム…",
        "btn":"選択した資産を生成","upload_label":"ここに物件写真をアップロード",
        "result":"エグゼクティブ・プレビュー","loading":"プレミアム・マーケティング・エコシステムを構築中…",
        "empty":"分析用の画像を待機中。写真をアップロードし、左側に詳細を入力してください。",
        "download":"セクションを書き出し (TXT)","save_btn":"変更を保存","saved_msg":"保存完了！",
        "error":"エラー:","clear_btn":"フォームをリセット","select_sections":"生成するセクションを選択",
        "tab_main":"プレミアム広告","tab_social":"SNSキット","tab_video":"動画台本",
        "tab_tech":"技術仕様","tab_email":"メールキャンペーン","tab_seo":"SEO ＆ Webコピー","tab_photo":"写真ガイド",
        "label_main":"セールスコピー","label_social":"SNSコンテンツ","label_video":"動画シナリオ",
        "label_tech":"技術詳細","label_email":"メールキャンペーン","label_seo":"SEOテキスト",
        "label_photo":"撮影のアドバイス","extra_details":"物件詳細情報",
        "interface_lang":"インターフェース言語","logout":"ログアウト","acc_settings":"アカウント設定",
        "update_pw":"パスワード変更","new_pw":"新しいパスワード","btn_update":"今すぐ更新",
        "danger_zone":"危険区域","delete_confirm":"アカウントを完全に削除します。",
        "btn_delete":"アカウント削除","pw_min_err":"6文字以上必要です。",
        "delete_email_sent":"確認メールを送信しました！受信トレイを確認してください。",
        "delete_email_fail":"メールの送信に失敗しました。SMTP設定を確認してください。",
    },
    "简体中文": {
        "title":"SarSa AI | 房地产智能平台",
        "service_desc":"全方位房产视觉智能与全球销售自动化",
        "subtitle":"立即将房产照片转化为优质房源描述、社交媒体包、视频脚本、技术规格、邮件营销和 SEO 文案。",
        "settings":"配置","target_lang":"编写语言…","prop_type":"房产类型",
        "price":"市场价格","location":"地点","tone":"营销策略",
        "tones":["标准专业","顶级豪宅","投资价值","现代简约","家庭生活","度假租赁","商业办公"],
        "ph_prop":"例如：3室1厅公寓、豪华别墅…","ph_price":"例如：$850,000 或 $2,000/月…",
        "ph_loc":"例如：上海浦东新区、北京或伦敦…","bedrooms":"卧室","bathrooms":"卫生间",
        "area":"面积","year_built":"建造年份","ph_beds":"例如：3","ph_baths":"例如：2",
        "ph_area":"例如：185 平方米","ph_year":"例如：2022","furnishing":"装修情况",
        "furnishing_opts":["未指定","精装修（含家具）","简装修","毛坯房"],
        "target_audience":"目标受众",
        "audience_opts":["大众市场","豪宅买家","投资者 & 投资回报","外籍人士","首次购房者","度假市场","商业租客"],
        "custom_inst":"特别备注与亮点","custom_inst_ph":"例如：私人泳池、全景海景、智能家居…",
        "btn":"生成所选资产","upload_label":"在此上传房产照片",
        "result":"高级预览","loading":"正在打造您的专属营销生态系统…",
        "empty":"等待照片进行专业分析。请上传照片并在左侧填写详细信息。",
        "download":"导出此部分 (TXT)","save_btn":"保存更改","saved_msg":"已保存！",
        "error":"错误：","clear_btn":"重置表单","select_sections":"选择要生成的章节",
        "tab_main":"优质房源","tab_social":"社媒包","tab_video":"视频脚本",
        "tab_tech":"技术规格","tab_email":"邮件营销","tab_seo":"SEO 网页文案","tab_photo":"拍摄指南",
        "label_main":"销售文案","label_social":"社媒内容","label_video":"视频脚本",
        "label_tech":"技术规格","label_email":"邮件营销","label_seo":"SEO 文案",
        "label_photo":"摄影建议","extra_details":"额外房产细节",
        "interface_lang":"界面语言","logout":"退出登录","acc_settings":"账户设置",
        "update_pw":"更改密码","new_pw":"新密码","btn_update":"立即更新",
        "danger_zone":"危险区域","delete_confirm":"我确认要永久删除我的账户。",
        "btn_delete":"删除账户","pw_min_err":"密码至少需要6位。",
        "delete_email_sent":"确认邮件已发送！请检查您的收件箱。",
        "delete_email_fail":"发送邮件失败。请检查SMTP设置。",
    },
    "العربية": {
        "title":"SarSa AI | منصة الذكاء العقاري",
        "service_desc":"الذكاء البصري المتكامل للعقارات وأتمتة المبيعات العالمية",
        "subtitle":"حول صور العقارات فوراً إلى إعلانات مميزة، حقائب تواصل اجتماعي، سيناريوهات فيديو، مواصفات فنية، حملات بريدية ونصوص SEO.",
        "settings":"الإعدادات","target_lang":"لغة الكتابة…","prop_type":"نوع العقار",
        "price":"سعر السوق","location":"الموقع","tone":"استراتيجية التسويق",
        "tones":["احترافي قياسي","فخامة فائقة","تركيز استثماري","عصري بسيط","حياة عائلية","تأجير سياحي","تجاري"],
        "ph_prop":"مثال: شقة 3+1، فيلا فاخرة…","ph_price":"مثال: 850,000$ أو 2,500$ شهرياً…",
        "ph_loc":"مثال: دبي مارينا، الرياض، القاهرة…","bedrooms":"غرف النوم","bathrooms":"الحمامات",
        "area":"المساحة","year_built":"سنة البناء","ph_beds":"مثال: 3","ph_baths":"مثال: 2",
        "ph_area":"مثال: 185 م²","ph_year":"مثال: 2022","furnishing":"حالة التأثيث",
        "furnishing_opts":["غير محدد","مفروش بالكامل","مفروش جزئياً","غير مفروش"],
        "target_audience":"الجمهور المستهدف",
        "audience_opts":["السوق العام","مشتري الفخامة","المستثمرون","المغتربون","مشتري لأول مرة","سوق العطلات","مستأجر تجاري"],
        "custom_inst":"ملاحظات خاصة ومميزات","custom_inst_ph":"مثال: مسبح خاص، إطلالة بانورامية، منزل ذكي…",
        "btn":"إنشاء الأصول المختارة","upload_label":"ضع صور العقار هنا",
        "result":"معاينة تنفيذية","loading":"جاري تجهيز منظومتك التسويقية الفاخرة…",
        "empty":"في انتظار الصور لبدء التحليل المهني. ارفع الصور واملأ التفاصيل على اليسار.",
        "download":"تصدير القسم (TXT)","save_btn":"حفظ التغييرات","saved_msg":"تم الحفظ!",
        "error":"خطأ:","clear_btn":"إعادة تعيين","select_sections":"اختر الأقسام المراد إنشاؤها",
        "tab_main":"الإعلان الرئيسي","tab_social":"حقيبة التواصل","tab_video":"سيناريو الفيديو",
        "tab_tech":"المواصفات الفنية","tab_email":"حملة البريد","tab_seo":"نصوص الويب وSEO","tab_photo":"دليل التصوير",
        "label_main":"نص المبيعات","label_social":"محتوى التواصل","label_video":"سيناريو الفيديو",
        "label_tech":"المواصفات الفنية","label_email":"حملة البريد الإلكتروني","label_seo":"نص SEO",
        "label_photo":"توصيات التصوير","extra_details":"تفاصيل العقار الإضافية",
        "interface_lang":"لغة الواجهة","logout":"تسجيل الخروج","acc_settings":"إعدادات الحساب",
        "update_pw":"تحديث كلمة السر","new_pw":"كلمة سر جديدة","btn_update":"تحديث الآن",
        "danger_zone":"منطقة خطر","delete_confirm":"أريد حذف حسابي نهائياً.",
        "btn_delete":"حذف الحساب","pw_min_err":"يجب أن تكون 6 خانات على الأقل.",
        "delete_email_sent":"تم إرسال بريد التأكيد! تحقق من صندوق الوارد.",
        "delete_email_fail":"فشل إرسال البريد. تحقق من إعدادات SMTP.",
    },
}

# ─── SHARED AUTH CSS ──────────────────────────────────────────────────────────
_AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="st-"]{ font-family:'Plus Jakarta Sans',sans-serif !important; }
.stApp{ background:linear-gradient(135deg,#f0f4f8 0%,#e8edf5 100%) !important; }
#MainMenu,footer,div[data-testid="stDecoration"]{ display:none !important; }
.block-container{
    max-width:540px !important; margin:2rem auto !important;
    background:white; border-radius:24px; padding:2.5rem !important;
    box-shadow:0 20px 60px rgba(0,0,0,0.08); border:1px solid #e2e8f0;
}
.stButton>button{
    background:#0f172a !important; color:white !important;
    border-radius:12px !important; padding:14px 24px !important;
    font-weight:700 !important; font-size:0.95rem !important; width:100% !important;
    border:none !important; transition:all 0.25s ease !important;
    box-shadow:0 4px 15px rgba(15,23,42,0.25) !important;
}
.stButton>button:hover{
    background:#1e293b !important; transform:translateY(-2px) !important;
    box-shadow:0 8px 25px rgba(15,23,42,0.35) !important;
}
</style>"""

# ─── LANGUAGE HELPERS ─────────────────────────────────────────────────────────
def _at(key, fb=""):
    return auth_texts.get(st.session_state.auth_lang, auth_texts["English"]).get(key, fb)

def _ut(key, fb=""):
    return ui_languages.get(st.session_state.auth_lang, ui_languages["English"]).get(key, fb)

def _lang_sel(widget_key):
    langs = list(auth_texts.keys())
    idx   = langs.index(st.session_state.auth_lang) if st.session_state.auth_lang in langs else 0
    sel   = st.selectbox("🌐 Select Language / Dil Seçin", langs, index=idx, key=widget_key)
    if sel != st.session_state.auth_lang:
        st.session_state.auth_lang = sel
        if cookie_manager:
            cookie_manager.set("sarsa_auth_lang", sel, expires_at=datetime.now() + timedelta(days=365))
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE A — EMAIL CONFIRMED (KAYIT SONRASI ŞIK ONAY EKRANI)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.show_email_confirmed:
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)
    _lang_sel("lk_confirmed")

    st.markdown(f"""
    <div style="text-align:center;padding:1.5rem 0 2rem;">
        <div style="font-size:5rem;line-height:1;margin-bottom:1rem;
                    filter:drop-shadow(0 4px 16px rgba(34,197,94,0.4));">✅</div>
        <h1 style="color:#0f172a;font-weight:800;font-size:2rem;margin:0 0 0.8rem;">
            {_at("confirmed_title","✅ Email Verified Successfully!")}
        </h1>
        <p style="color:#475569;font-size:1.05rem;line-height:1.75;margin:0 0 0.4rem;">
            {_at("confirmed_msg","Your account has been confirmed and is ready to use.")}
        </p>
        <p style="color:#94a3b8;font-size:0.9rem;">
            {_at("confirmed_sub","Click the button below to go to the login page.")}
        </p>
    </div>
    <hr style="border:none;border-top:1px solid #f1f5f9;margin:0 0 1.8rem;">
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,3,1])
    with c2:
        if st.button(_at("confirmed_btn","🔑 Go to Login"), use_container_width=True):
            st.session_state.show_email_confirmed = False
            with st.spinner("Yönlendiriliyor..."):
                time.sleep(1)
            st.rerun()

    st.markdown("""<p style="text-align:center;color:#cbd5e1;font-size:0.8rem;margin-top:1.5rem;">
        SarSa AI | Real Estate Intelligence</p>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE B — SET NEW PASSWORD (ŞİFRE SIFIRLAMA LİNKİNDEN GELEN ŞIK EKRAN)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.recovery_mode:
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)
    _lang_sel("lk_recovery")

    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0 1.5rem;">
        <div style="font-size:3.5rem;margin-bottom:0.6rem;">🔒</div>
        <h1 style="color:#0f172a;font-weight:800;font-size:1.8rem;margin:0;">
            {_at("pw_reset_title","Set Your New Password")}
        </h1>
        <p style="color:#64748b;margin-top:0.6rem;font-size:0.97rem;line-height:1.6;">
            {_at("pw_reset_desc","Enter a new password for your account.")}
        </p>
    </div>
    <hr style="border:none;border-top:1px solid #f1f5f9;margin:0 0 1.5rem;">
    """, unsafe_allow_html=True)

    with st.form("recovery_form"):
        new_pw_val = st.text_input(
            _at("new_pw_label","New Password"),
            type="password", placeholder="••••••••"
        )
        cs, cc = st.columns(2)
        with cs: do_save   = st.form_submit_button(_at("pw_reset_btn","✅ Save Password & Login"), use_container_width=True)
        with cc: do_cancel = st.form_submit_button(_at("pw_reset_cancel","❌ Cancel"),              use_container_width=True)

        if do_cancel:
            st.session_state.recovery_mode = False
            st.session_state.is_logged_in  = False
            st.rerun()

        if do_save:
            if len(new_pw_val) < 6:
                st.error(_at("pw_reset_min_err","❌ Password must be at least 6 characters."))
            else:
                try:
                    if st.session_state.access_token:
                        supabase.auth.set_session(
                            st.session_state.access_token,
                            st.session_state.refresh_token)
                    supabase.auth.update_user({"password": new_pw_val})
                    st.success(_at("pw_reset_success","✅ Password updated! Logging you in…"))
                    
                    st.session_state.recovery_mode = False
                    st.session_state.is_logged_in  = True
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating password: {e}")
    st.stop()

# ─── AUTH STATUS ──────────────────────────────────────────────────────────────
def get_status():
    if st.session_state.is_logged_in:
        return "paid", st.session_state.user_email
    try:
        if st.session_state.access_token:
            supabase.auth.set_session(
                st.session_state.access_token, st.session_state.refresh_token)
        ur = supabase.auth.get_user()
        if not ur or not ur.user: return "logged_out", None
        if not ur.user.email_confirmed_at: return "unverified", ur.user.email
        st.session_state.is_logged_in = True
        st.session_state.user_email   = ur.user.email
        return "paid", ur.user.email
    except Exception:
        return "logged_out", None

auth_status, user_email = get_status()

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="st-"]{ font-family:'Plus Jakarta Sans',sans-serif !important; }
.stApp{ background-color:#f0f4f8 !important; }
div[data-testid="stInputInstructions"],#MainMenu,footer,
div[data-testid="stDecoration"]{ display:none !important; }
.block-container{
    background:white; padding:2.5rem 3rem !important; border-radius:20px;
    box-shadow:0 10px 40px rgba(0,0,0,0.06); margin-top:1.5rem; border:1px solid #e2e8f0; }
h1{ color:#0f172a !important; font-weight:800 !important; text-align:center; }
[data-testid="stSidebar"]{ background:#ffffff !important; border-right:1px solid #e2e8f0 !important; }
[data-testid="stSidebar"] label{ font-size:0.74rem !important; font-weight:700 !important;
    color:#64748b !important; text-transform:uppercase !important; letter-spacing:0.7px !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea{
    border-radius:8px !important; border:1.5px solid #e2e8f0 !important;
    background:#f8fafc !important; font-size:0.875rem !important; }
.stButton>button{
    background:#0f172a !important; color:white !important;
    border-radius:12px !important; padding:14px 24px !important;
    font-weight:700 !important; font-size:0.95rem !important; width:100% !important;
    border:none !important; transition:all 0.25s ease !important;
    box-shadow:0 4px 15px rgba(15,23,42,0.3) !important; }
.stButton>button:hover{
    background:#1e293b !important;
    box-shadow:0 8px 25px rgba(15,23,42,0.4) !important; transform:translateY(-1px) !important; }
.stTabs [aria-selected="true"]{
    background-color:#0f172a !important; color:white !important; border-radius:8px 8px 0 0 !important; }
</style>""", unsafe_allow_html=True)

@st.cache_data
def load_logo(p):
    return Image.open(p) if os.path.exists(p) else None

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN / REGISTER PAGE
# ══════════════════════════════════════════════════════════════════════════════
if auth_status != "paid":
    langs = list(auth_texts.keys())
    sel   = st.selectbox(
        "🌐 Select Language / Dil Seçin", langs,
        index=langs.index(st.session_state.auth_lang) if st.session_state.auth_lang in langs else 0,
        key="login_lang")
    if sel != st.session_state.auth_lang:
        st.session_state.auth_lang = sel
        if cookie_manager:
            cookie_manager.set("sarsa_auth_lang", sel, expires_at=datetime.now() + timedelta(days=365))
        st.rerun()
    at = auth_texts[st.session_state.auth_lang]

    cl, ct = st.columns([1, 6])
    with cl:
        logo = load_logo("SarSa_Logo_Transparent.png")
        if logo: st.image(logo, use_container_width=True)
    with ct:
        st.markdown(f"<h1 style='text-align:left;margin-top:0;'>{at['welcome_title']}</h1>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.1rem;color:#475569;font-weight:500;margin-bottom:2rem;'>"
                    f"{at['welcome_desc']}</p>", unsafe_allow_html=True)

    st.markdown(f"<h3 style='text-align:center;color:#0f172a;margin-bottom:1.5rem;'>"
                f"{at['login_prompt']}</h3>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        f"🔑 {at['login']}", f"📝 {at['register']}", f"❓ {at['forgot_pw']}"])

    with tab1:
        with st.form("login_form"):
            em = st.text_input(at["email"])
            pw = st.text_input(at["password"], type="password")
            if st.form_submit_button(at["btn_login"]):
                try:
                    r = supabase.auth.sign_in_with_password({"email": em, "password": pw})
                    if r.session:
                        st.session_state.access_token  = r.session.access_token
                        st.session_state.refresh_token = r.session.refresh_token
                        save_auth_cookies(r.session.access_token, r.session.refresh_token)
                    st.session_state.is_logged_in = True
                    st.session_state.user_email   = r.user.email
                    st.rerun()
                except Exception as ex:
                    msg = str(ex)
                    if "Email not confirmed" in msg: st.error(f"{at['verify_msg']} {em}")
                    elif "Invalid login credentials" in msg: st.error(f"❌ {at['error_login']}")
                    else: st.error(msg)

    with tab2:
        with st.form("register_form"):
            er = st.text_input(at["email"])
            pr = st.text_input(at["password"] + " (Min 6)", type="password")
            if st.form_submit_button(at["btn_reg"]):
                try:
                    supabase.auth.sign_up({
                        "email": er, "password": pr,
                        "options": {"email_redirect_to": "https://sarsa-ai-estateintelligence.streamlit.app/"}
                    })
                    st.success(f"✅ {at['success_reg']}")
                except Exception as ex:
                    msg = str(ex)
                    if "User already registered" in msg: st.error("This email is already registered.")
                    else: st.error(f"Error: {ex}")

    with tab3:
        with st.form("forgot_form"):
            er2 = st.text_input(at["email"], placeholder="your@email.com")
            if st.form_submit_button(at["btn_reset"]):
                er2 = er2.strip()
                if not er2 or "@" not in er2:
                    st.error(at["reset_invalid_email"])
                else:
                    with st.spinner("Checking…"):
                        exists = is_email_registered(er2)
                    if not exists:
                        st.error(at["reset_not_found"])
                    else:
                        try:
                            supabase.auth.reset_password_for_email(
                                er2,
                                {"redirect_to": "https://sarsa-ai-estateintelligence.streamlit.app/"})
                            st.success(f"✅ {at['reset_success']}")
                        except Exception as e:
                            st.error(f"Error: {e}")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# AI + SIDEBAR (ANA UYGULAMA)
# ══════════════════════════════════════════════════════════════════════════════
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

with st.sidebar:
    logo = load_logo("SarSa_Logo_Transparent.png")
    if logo: st.image(logo, use_container_width=True)
    else:
        st.markdown("<div style='text-align:center;padding:.8rem 0 .5rem;'>"
                    "<span style='font-size:1.8rem;font-weight:800;color:#0f172a;'>SarSa</span>"
                    "<span style='font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#3b82f6,#8b5cf6);"
                    "-webkit-background-clip:text;-webkit-text-fill-color:transparent;'> AI</span></div>",
                    unsafe_allow_html=True)
    st.divider()

    all_ui  = list(ui_languages.keys())
    cur_idx = all_ui.index(st.session_state.auth_lang) if st.session_state.auth_lang in all_ui else 0
    sel_ui  = st.selectbox(f"🌐 {_ut('interface_lang','Interface Language')}",
                           all_ui, index=cur_idx, key="sb_lang")
    if sel_ui != st.session_state.auth_lang:
        st.session_state.auth_lang = sel_ui
        if cookie_manager:
            cookie_manager.set("sarsa_auth_lang", sel_ui, expires_at=datetime.now() + timedelta(days=365))
        st.rerun()
    t = ui_languages[st.session_state.auth_lang]

    with st.expander(f"⚙️ {t['acc_settings']}"):
        st.write(st.session_state.user_email)
        st.subheader(t["update_pw"])
        new_pw_sb = st.text_input(t["new_pw"], type="password", key="sb_pw")
        if st.button(t["btn_update"], key="sb_upd"):
            if len(new_pw_sb) < 6: st.warning(t["pw_min_err"])
            else:
                try:
                    if st.session_state.access_token:
                        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
                    supabase.auth.update_user({"password": new_pw_sb})
                    st.success(t["saved_msg"])
                except Exception as e: st.error(f"{t['error']} {e}")
        st.divider()
        st.subheader(t["danger_zone"])
        chk_del = st.checkbox(t["delete_confirm"])
        if st.button(f"❌ {t['btn_delete']}", type="primary", use_container_width=True):
            if chk_del:
                try:
                    if st.session_state.access_token:
                        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
                    ur = supabase.auth.get_user()
                    if ur and ur.user:
                        ct_tok = str(uuid.uuid4()); ca_tok = str(uuid.uuid4())
                        exp = (datetime.now(timezone.utc)+timedelta(hours=24)).isoformat()
                        supabase.table("pending_deletions").insert({
                            "user_id":ur.user.id,"user_email":ur.user.email,
                            "confirm_token":ct_tok,"cancel_token":ca_tok,"expires_at":exp
                        }).execute()
                        ok, err = send_delete_confirmation_email(ur.user.email, ct_tok, ca_tok)
                        if ok: st.success(t["delete_email_sent"])
                        else:  st.error(f"{t['delete_email_fail']} — {err}")
                    else: st.error("Could not retrieve user. Please log out and log back in.")
                except Exception as e: st.error(f"{t['error']} {e}")
            else: st.warning("Please tick the confirmation checkbox first.")

    if st.button(f"🚪 {t['logout']}", use_container_width=True):
        with st.spinner("Çıkış yapılıyor..."):
            supabase.auth.sign_out()
            for k in ["is_logged_in","user_email","access_token","refresh_token"]:
                st.session_state[k] = False if k=="is_logged_in" else None
            clear_auth_cookies()
            time.sleep(1)
        st.rerun()

    st.markdown("---")
    st.header(t["settings"])
    st.session_state.target_lang_input = st.text_input(f"✍️ {t['target_lang']}", value=st.session_state.target_lang_input)
    st.session_state.prop_type = st.text_input(t["prop_type"], value=st.session_state.prop_type, placeholder=t["ph_prop"])
    st.session_state.price     = st.text_input(t["price"],     value=st.session_state.price,     placeholder=t["ph_price"])
    st.session_state.location  = st.text_input(t["location"],  value=st.session_state.location,  placeholder=t["ph_loc"])
    tone_idx = t["tones"].index(st.session_state.tone) if st.session_state.tone in t["tones"] else 0
    st.session_state.tone         = st.selectbox(t["tone"], t["tones"], index=tone_idx)
    st.session_state.audience_idx = st.selectbox(t["target_audience"], range(len(t["audience_opts"])),
        index=st.session_state.audience_idx, format_func=lambda x: t["audience_opts"][x])
    with st.expander(f"➕ {t['extra_details']}"):
        st.session_state.bedrooms       = st.text_input(t["bedrooms"],   value=st.session_state.bedrooms,   placeholder=t["ph_beds"])
        st.session_state.bathrooms      = st.text_input(t["bathrooms"],  value=st.session_state.bathrooms,  placeholder=t["ph_baths"])
        st.session_state.area_size      = st.text_input(t["area"],       value=st.session_state.area_size,  placeholder=t["ph_area"])
        st.session_state.year_built     = st.text_input(t["year_built"], value=st.session_state.year_built, placeholder=t["ph_year"])
        st.session_state.furnishing_idx = st.selectbox(t["furnishing"], range(len(t["furnishing_opts"])),
            index=st.session_state.furnishing_idx, format_func=lambda x: t["furnishing_opts"][x])
    st.session_state.custom_inst = st.text_area(f"📝 {t['custom_inst']}", value=st.session_state.custom_inst,
        placeholder=t["custom_inst_ph"], height=100)
    st.markdown("---")
    st.subheader(t["select_sections"])
    sec_opts = {t["tab_main"]:"main", t["tab_social"]:"social", t["tab_video"]:"video",
                t["tab_tech"]:"tech", t["tab_email"]:"email", t["tab_seo"]:"seo", t["tab_photo"]:"photo"}
    st.session_state.selected_sections = st.multiselect(
        "Sections:", options=list(sec_opts.keys()),
        default=list(sec_opts.keys()), label_visibility="collapsed")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"<h1 style='text-align:center;'>🏢 {t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;color:#64748b;font-size:1.1rem;margin-bottom:2rem;'>"
            f"{t.get('subtitle',t['service_desc'])}</p>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(f"📸 {t['upload_label']}",
    type=["jpg","png","webp","jpeg"], accept_multiple_files=True)

if uploaded_files:
    imgs = [Image.open(f) for f in uploaded_files]
    cols = st.columns(min(len(imgs),4))
    for i, img in enumerate(imgs):
        with cols[i%4]: st.image(img, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(f"🚀 {t.get('btn','GENERATE SELECTED ASSETS')}", use_container_width=True):
        if not st.session_state.selected_sections:
            st.warning("Please select at least one section from the sidebar.")
        else:
            with st.spinner(t.get("loading","Crafting your premium marketing ecosystem…")):
                st.success("Request received! Generating content for selected sections…")
            tabs = st.tabs(st.session_state.selected_sections)
            for idx, sec in enumerate(st.session_state.selected_sections):
                with tabs[idx]:
                    st.subheader(sec)
                    st.write(f"AI-generated content for '{sec}' will appear here.")
                    st.button(f"📥 {t['download']} – {sec}", key=f"dl_{idx}")
else:
    st.markdown(f"""
    <div style='text-align:center;padding:3rem;background:#f8fafc;border-radius:12px;
                border:2px dashed #cbd5e1;margin-top:2rem;'>
      <h3 style='color:#475569;'>🏘️ {t.get("result","Executive Preview")}</h3>
      <p style='color:#94a3b8;'>{t["empty"]}</p>
      <div style="display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:1.4rem;">
        {"".join(f"<span style='background:#f1f5f9;color:#475569;font-size:.73rem;font-weight:600;padding:5px 12px;border-radius:20px;border:1px solid #e2e8f0;'>{lb}</span>" for lb in [f"📝 {t['tab_main']}",f"📱 {t['tab_social']}",f"🎬 {t['tab_video']}",f"⚙️ {t['tab_tech']}",f"✉️ {t['tab_email']}",f"🔍 {t['tab_seo']}",f"📸 {t.get('tab_photo','Photo Guide')}"])}
      </div>
    </div>""", unsafe_allow_html=True)
