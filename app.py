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
import streamlit.components.v1 as components  # \u2190 FIX: needed for JS hash redirect

# \u2500\u2500\u2500 PAGE CONFIG (En \u00fcstte olmal\u0131) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
st.set_page_config(page_title="SarSa AI | Real Estate Intelligence", page_icon="\ud83c\udfe2", layout="wide")

# \u2500\u2500\u2500 HASH FRAGMENT \u2192 QUERY PARAM REDIRECT \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# Supabase reset-password AND signup-confirm emails use implicit flow and put
# tokens in the URL *hash* (#access_token=...&type=recovery|signup).
# Streamlit cannot read URL fragments server-side, so we inject a tiny JS
# snippet that detects the fragment and immediately redirects to the same URL
# using normal query params (?...) instead.
# The page then reloads and Python can read the tokens via st.query_params.
components.html("""
<script>
(function() {
    var hash = window.location.hash;
    if (hash && hash.length > 1) {
        var params = new URLSearchParams(hash.substring(1));
        var type = params.get('type');
        var hasToken = params.get('access_token');
        if (hasToken || type === 'recovery' || type === 'signup') {
            window.location.replace(window.location.pathname + '?' + params.toString());
        }
    }
})();
</script>
""", height=0)

# \u2500\u2500\u2500 SUPABASE CONFIGURATION \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
SUPABASE_URL: str = st.secrets["SUPABASE_URL"]
SUPABASE_KEY: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# \u2500\u2500\u2500 SESSION STATE INITIALIZATION \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
if 'auth_lang' not in st.session_state: st.session_state.auth_lang = "English"
if 'is_logged_in' not in st.session_state: st.session_state.is_logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'recovery_mode' not in st.session_state: st.session_state.recovery_mode = False
if 'access_token' not in st.session_state: st.session_state.access_token = None
if 'refresh_token' not in st.session_state: st.session_state.refresh_token = None
# \u2190 NEW: flag shown after email verification link is clicked
if 'email_verified' not in st.session_state: st.session_state.email_verified = False

for key_name, val in [
    ("uretilen_ilan", ""), ("prop_type", ""), ("price", ""),
    ("location", ""), ("tone", ""), ("custom_inst", ""),
    ("target_lang_input", "English"), ("bedrooms", ""),
    ("bathrooms", ""), ("area_size", ""), ("year_built", ""),
    ("furnishing_idx", 0), ("audience_idx", 0), ("selected_sections", [])
]:
    if key_name not in st.session_state:
        st.session_state[key_name] = val

# \u2500\u2500\u2500 PERSISTENT SESSION RESTORE (prevents logout on page refresh) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
if st.session_state.access_token and not st.session_state.is_logged_in:
    try:
        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
        _check = supabase.auth.get_user()
        if _check and _check.user:
            st.session_state.is_logged_in = True
            st.session_state.user_email = _check.user.email
    except Exception:
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.is_logged_in = False

# \u2500\u2500\u2500 EMAIL HELPER \u2014 Delete Confirmation \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
def send_delete_confirmation_email(to_email: str, confirm_token: str, cancel_token: str):
    """Returns (True, '') on success or (False, error_message) on failure."""
    app_url = "https://sarsa-ai-estateintelligence.streamlit.app/"
    confirm_url = f"{app_url}?action=confirm_delete&token={confirm_token}"
    cancel_url  = f"{app_url}?action=cancel_delete&token={cancel_token}"

    html_body = f"""
    <div style="font-family: 'Arial', sans-serif; max-width: 620px; margin: 0 auto; padding: 30px; background: #f8fafc; border-radius: 16px;">
      <div style="background: white; border-radius: 12px; padding: 36px; box-shadow: 0 4px 20px rgba(0,0,0,0.07);">
        <div style="text-align:center; margin-bottom: 28px;">
          <h2 style="color: #0f172a; font-size: 22px; margin: 0;">Warning Account Deletion Request</h2>
          <p style="color: #64748b; margin-top: 8px; font-size: 14px;">SarSa AI | Real Estate Intelligence</p>
        </div>
        <p style="color: #334155; font-size: 16px; line-height: 1.6;">
          We received a request to <strong>permanently delete</strong> the SarSa AI account associated with:<br>
          <strong style="color:#0f172a;">{to_email}</strong>
        </p>
        <p style="color: #ef4444; font-size: 15px; font-weight: 600;">This action is irreversible. All your data will be permanently removed.</p>
        <div style="text-align: center; margin: 32px 0;">
          <a href="{confirm_url}"
             style="background-color: #dc2626; color: white; padding: 14px 32px; border-radius: 10px;
                    text-decoration: none; font-weight: 700; font-size: 16px; display: inline-block; margin-bottom: 14px;">
            Yes, Delete My Account
          </a><br>
          <a href="{cancel_url}"
             style="background-color: #0f172a; color: white; padding: 14px 32px; border-radius: 10px;
                    text-decoration: none; font-weight: 700; font-size: 16px; display: inline-block;">
            Cancel - Keep My Account Safe
          </a>
        </div>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
        <p style="color: #94a3b8; font-size: 13px; text-align: center;">
          This link expires in <strong>24 hours</strong>.<br>
          If you did not request this, simply ignore this email - your account is completely safe.
        </p>
      </div>
    </div>
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "SarSa AI - Confirm Account Deletion"
        msg["From"]    = st.secrets["SMTP_USER"]
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html"))

        smtp_host = st.secrets.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(st.secrets.get("SMTP_PORT", 587))
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(st.secrets["SMTP_USER"], st.secrets["SMTP_PASS"])
            server.sendmail(st.secrets["SMTP_USER"], to_email, msg.as_string())
        return True, ""
    except Exception as smtp_err:
        return False, str(smtp_err)

# \u2500\u2500\u2500 QUERY PARAM HANDLERS \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
query_params = st.query_params

# \u2500\u2500 Handle: Account Deletion Confirmation \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
if "action" in query_params and query_params.get("action") == "confirm_delete":
    token = query_params.get("token", "")
    try:
        result = supabase.table("pending_deletions").select("*").eq("confirm_token", token).execute()
        if result.data:
            record = result.data[0]
            expires_str = record.get("expires_at", "")
            expires_at  = datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
            now_utc     = datetime.now(timezone.utc)
            if now_utc < expires_at:
                try:
                    svc = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"])
                    svc.auth.admin.delete_user(record["user_id"])
                except Exception as del_e:
                    st.error(f"Deletion error: {del_e}")
                    st.stop()
                supabase.table("pending_deletions").delete().eq("confirm_token", token).execute()
                for _k in ["is_logged_in", "user_email", "access_token", "refresh_token"]:
                    st.session_state[_k] = None if _k != "is_logged_in" else False
                st.query_params.clear()
                st.markdown("""
                <div style='text-align:center; padding:5rem 2rem;'>
                  <div style='font-size:5rem; margin-bottom:1rem;'>\ud83d\udc4b</div>
                  <h1 style='color:#0f172a; font-weight:800;'>Account Deleted</h1>
                  <p style='color:#475569; font-size:1.15rem; margin-top:1rem; line-height:1.7;'>
                    Your SarSa AI account has been <strong>permanently deleted</strong>.<br>
                    All your data has been removed from our systems.
                  </p>
                  <p style='color:#94a3b8; margin-top:2rem; font-size:0.95rem;'>You have been logged out.</p>
                  <hr style='border:none; border-top:1px solid #e2e8f0; margin:2.5rem auto; max-width:400px;'>
                  <p style='color:#cbd5e1; font-size:0.85rem;'>Thank you for using SarSa AI.</p>
                </div>
                """, unsafe_allow_html=True)
                st.stop()
            else:
                st.error("This confirmation link has expired (24h limit). Please request a new deletion from Account Settings.")
        else:
            st.error("Invalid or already used link.")
    except Exception as e:
        st.error(f"Error during account deletion: {e}")
    st.stop()

# \u2500\u2500 Handle: Account Deletion Cancel \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
if "action" in query_params and query_params.get("action") == "cancel_delete":
    token = query_params.get("token", "")
    try:
        supabase.table("pending_deletions").delete().eq("cancel_token", token).execute()
    except Exception:
        pass
    st.query_params.clear()
    st.success("Account deletion cancelled. Your account is completely safe!")
    import time; time.sleep(2)
    st.rerun()

# \u2500\u2500\u2500 TEXT