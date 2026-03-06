import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
from datetime import datetime
import sys

sys.path.insert(0, os.path.dirname(__file__))
from shared import (
    CSS, LANGS, init_state, render_sidebar,
    extract_section, flag_fh, wc, save_to_history,
    build_prompt, prop_str, agent_str,
)

# ─────────────────────────────────────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────────────────────────────────────
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(
    page_title="SarSa AI · Real Estate Intelligence",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_state()
st.markdown(CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — renders and returns active language dict
# ─────────────────────────────────────────────────────────────────────────────
T = render_sidebar(LANGS["English"])

# ─────────────────────────────────────────────────────────────────────────────
# COPY-TO-CLIPBOARD HELPER
# ─────────────────────────────────────────────────────────────────────────────
def copy_button(text: str, copy_lbl: str, copied_lbl: str, key: str):
    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$").replace("'", "\\'")
    cl = copy_lbl.replace("'", "\\'")
    cd = copied_lbl.replace("'", "\\'")
    st.markdown(f"""
    <button class='copy-btn' id='cb_{key}'
      onclick="navigator.clipboard.writeText(`{safe}`).then(()=>{{
        var b=document.getElementById('cb_{key}');
        b.textContent='{cd}';
        setTimeout(()=>b.textContent='{cl}',2000);
      }})"
    >{cl}</button>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION RENDERER (shared by all output tabs)
# ─────────────────────────────────────────────────────────────────────────────
def render_output_section(sk: str, fname: str, show_fhc: bool = False):
    val = st.session_state.get(sk, "")
    new = st.text_area("", value=val, height=500, key=f"ta_{sk}")
    if new != val:
        st.session_state[sk] = new
        st.session_state.dirty = True

    w, c = wc(new)
    st.markdown(
        f"<div class='wc-row'>"
        f"<span class='wc-chip'>📊 {w} {T['words']}</span>"
        f"<span class='wc-chip'>✏️ {c} {T['chars']}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if show_fhc and new:
        flags = flag_fh(new)
        if flags:
            st.markdown(
                f"<div class='comp-warn'>{T['comp_warn']}{', '.join(flags)}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"<div class='comp-ok'>{T['comp_ok']}</div>", unsafe_allow_html=True)

    bc1, bc2 = st.columns(2)
    with bc1:
        st.download_button(
            T["dl_section"], data=new,
            file_name=f"sarsa_{fname}_{datetime.now().strftime('%Y%m%d')}.txt",
            key=f"dl_{sk}", use_container_width=True,
        )
    with bc2:
        copy_button(new, T["copy_btn"], T["copied_btn"], sk)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: GENERATE
# ═══════════════════════════════════════════════════════════════════════════════
def page_generate():
    # Welcome hero (shown before first generation)
    if not st.session_state.output_raw and not st.session_state.get("_shown_welcome"):
        st.markdown(f"""
        <div class='welcome-hero'>
          <div class='tag'>✦ AI-Powered Real Estate Marketing</div>
          <div class='display-title' style='margin-bottom:0.75rem;'>
            The Professional <span class='gold'>Marketing Engine</span><br>for Real Estate Agents
          </div>
          <p style='color:var(--text2);font-size:1rem;max-width:600px;margin:0 auto 1.5rem;line-height:1.6;'>
            Upload property photos. Fill in details. Get a complete professional marketing package — listing copy, social media kit, video script, technical specs, email templates, and SEO pack — in seconds.
          </p>
          <div class='feature-row'>
            <span class='feature-chip'>📝 Listing Copy</span>
            <span class='feature-chip'>📱 Social Media Kit</span>
            <span class='feature-chip'>🎬 Video Script</span>
            <span class='feature-chip'>⚙️ Tech Specs</span>
            <span class='feature-chip'>📧 Email Templates</span>
            <span class='feature-chip'>🔍 SEO Pack</span>
            <span class='feature-chip'>🌍 9 Languages</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── UPLOAD ──
    uploaded = st.file_uploader(
        T["upload_label"],
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        label_visibility="visible",
    )

    if uploaded:
        images = [Image.open(f) for f in uploaded]
        n = min(len(images), 6)
        cols = st.columns(n)
        for i, img in enumerate(images):
            with cols[i % n]:
                st.image(img, use_container_width=True)
                st.markdown(
                    f"<p style='text-align:center;color:var(--text3);font-size:0.7rem;"
                    f"margin-top:3px;font-family:Lato,sans-serif;'>"
                    f"{T['photo']} {i+1}</p>",
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown("<div class='btn-primary'>", unsafe_allow_html=True)
        do_gen = st.button(T["gen_btn"], use_container_width=True, key="do_gen_btn")
        st.markdown("</div>", unsafe_allow_html=True)

        if do_gen:
            st.session_state["_shown_welcome"] = True
            strategy = T["strategies"][st.session_state.strategy_idx]
            prompt   = build_prompt(st.session_state.write_in or "English", strategy)
            prog     = st.progress(0)
            status   = st.empty()
            steps    = T["loading"]
            try:
                for i, step in enumerate(steps[:-1]):
                    status.info(step)
                    prog.progress(int((i + 1) / len(steps) * 88))
                status.info(steps[-1])
                resp = model.generate_content([prompt] + images)
                raw  = resp.text
                st.session_state.output_raw = raw
                for n in range(1, 7):
                    st.session_state[f"s{n}"] = extract_section(raw, n)
                st.session_state.dirty = False
                prog.progress(100)
                status.success("✅  Package ready!")
            except Exception as e:
                status.error(f"{T['err']}{e}")
                prog.empty()

    elif not st.session_state.output_raw:
        st.markdown(f"""
        <div class='empty-state'>
          <div class='empty-icon'>🏡</div>
          <div class='empty-title'>{T['empty_title']}</div>
          <div class='empty-sub'>{T['empty_sub']}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── OUTPUT ──
    if st.session_state.output_raw:
        st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)

        # Action bar
        ac1, ac2, ac3, ac4, ac5 = st.columns([3.5, 1.1, 1.1, 1.1, 1.2])

        with ac1:
            st.markdown("<div class='output-title'>Your Package</div>", unsafe_allow_html=True)
            if st.session_state.dirty:
                st.markdown(f"<span class='status-dirty'>● {T['unsaved']}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='status-saved'>✓ {T['all_saved']}</span>", unsafe_allow_html=True)

        with ac2:
            if st.button(T["save_btn"], use_container_width=True, key="save_hist"):
                save_to_history()
                st.session_state.dirty = False
                st.success(T["saved_ok"])

        with ac3:
            if st.button(T["regen_btn"], use_container_width=True, key="regen_btn"):
                for k in ["output_raw","s1","s2","s3","s4","s5","s6"]:
                    st.session_state[k] = ""
                st.session_state.dirty = False
                st.rerun()

        with ac4:
            # Build full download
            full = f"""SARSA AI — COMPLETE MARKETING PACKAGE
{'='*60}
{prop_str()}
Generated: {datetime.now().strftime('%d %b %Y %H:%M')}
{'='*60}

{'─'*60}
LISTING COPY
{'─'*60}
{st.session_state.s1}

{'─'*60}
SOCIAL MEDIA KIT
{'─'*60}
{st.session_state.s2}

{'─'*60}
VIDEO SCRIPT
{'─'*60}
{st.session_state.s3}

{'─'*60}
TECHNICAL SPECIFICATIONS
{'─'*60}
{st.session_state.s4}

{'─'*60}
EMAIL TEMPLATES
{'─'*60}
{st.session_state.s5}

{'─'*60}
SEO & DIGITAL MARKETING PACK
{'─'*60}
{st.session_state.s6}
"""
            st.download_button(
                T["dl_all"], data=full,
                file_name=f"sarsa_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                use_container_width=True, key="dl_all_btn",
            )

        with ac5:
            copy_button(
                "\n\n".join(st.session_state.get(f"s{i}","") for i in range(1,7)),
                T["copy_btn"], T["copied_btn"], "all"
            )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # ── TABS ──
        tabs = st.tabs([
            T["tab1"], T["tab2"], T["tab3"],
            T["tab4"], T["tab5"], T["tab6"],
        ])
        tab_meta = [
            ("s1", "listing",       True),
            ("s2", "social_kit",    False),
            ("s3", "video_script",  False),
            ("s4", "tech_specs",    False),
            ("s5", "email_kit",     False),
            ("s6", "seo_pack",      False),
        ]
        for tab_obj, (sk, fname, fhc) in zip(tabs, tab_meta):
            with tab_obj:
                render_output_section(sk, fname, show_fhc=fhc)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: AGENT TOOLS
# ═══════════════════════════════════════════════════════════════════════════════
TOOLS = [
    ("objection", "💬 Objection Handler",
     "Master the 10 toughest seller/buyer objections with FEEL-FELT-FOUND",
     """You are the world's premier real estate sales coach.
Write a COMPLETE OBJECTION HANDLING PLAYBOOK for:
Agent: {name} | Agency: {co} | Market: {loc}

Handle EXACTLY these 10 objections using FEEL-FELT-FOUND technique + closing line:
1. "Your commission is too high"
2. "I'll wait for the market to improve"
3. "I can sell it myself (FSBO)"
4. "Another agent offered a lower fee"
5. "The asking price is too high"
6. "I need more time to think"
7. "We're not in a rush to sell"
8. "The property needs too much work"
9. "I'm already talking to another agent"
10. "I want to try selling privately first"

For each objection:
- FEEL (empathise — 1 sentence)
- FELT (normalise — 1 sentence)
- FOUND (reframe/solution — 2 sentences)
- CLOSING LINE (confident, one sentence)

Format: bold the objection, then the 4 elements. Clear, professional, conversational.
Language: {lang}"""),

    ("cma", "📊 CMA Report Template",
     "Professional comparative market analysis ready for seller presentations",
     """Write a professional COMPARATIVE MARKET ANALYSIS REPORT.
Property: {prop} at {loc} | Price: {price}
Prepared by: {name} | {co}

Sections:
1. EXECUTIVE SUMMARY (3 sentences)
2. SUBJECT PROPERTY PROFILE (use all provided data)
3. CURRENT MARKET CONDITIONS (trends, DOM, absorption rate, buyer demand)
4. COMPARABLE SALES — 3 templates with fields: Address, Size, Beds/Baths, Sale Date, Price, Price/m², Days on Market, Similarity Score
5. PRICE ANALYSIS (price per m², range recommendation with reasoning)
6. RECOMMENDED LISTING PRICE (range + justification)
7. DAYS ON MARKET FORECAST (conservative / likely / optimistic)
8. RECOMMENDED MARKETING STRATEGY (top 5 tactics for this property)
9. AGENT OPINION OF VALUE (professional assessment paragraph)
10. DISCLAIMER

Professional, data-driven, client-ready. Language: {lang}"""),

    ("cold_email", "📧 Cold Outreach Emails",
     "Three targeted prospecting emails for sellers, landlords, and expired listings",
     """Write 3 high-converting cold outreach emails.
Agent: {name} | {co} | {phone} | {email} | Target area: {loc}

EMAIL 1 — POTENTIAL SELLER (homeowner not yet on market)
Subject: [Curiosity-driven, personalised subject line]
Body: 150 words. Warm, value-first, no pressure.
Signature block.

EMAIL 2 — LANDLORD / INVESTOR
Subject: [ROI-focused subject line]
Body: 150 words. Market data angle, portfolio opportunity.
Signature block.

EMAIL 3 — EXPIRED LISTING (previously listed, didn't sell)
Subject: [Empathy-first subject line]
Body: 130 words. Acknowledge frustration, fresh approach, proven results.
Signature block.

Each: professional, personable, clear CTA, no spam triggers.
Language: {lang}"""),

    ("negotiation", "🤝 Negotiation Scripts",
     "Word-for-word scripts for every negotiation scenario agents face",
     """Write a COMPLETE REAL ESTATE NEGOTIATION SCRIPT PLAYBOOK.
Property: {prop} at {loc} | Price: {price} | Agent: {name} | {co}

Script EXACTLY these 6 scenarios (word-for-word, as agent speaking):

1. LOWBALL OFFER — counter without insulting buyer
2. MULTIPLE OFFERS — create urgency, manage fairly
3. POST-INSPECTION PRICE REDUCTION REQUEST
4. BUYER REQUESTS SELLER PAYS CLOSING COSTS
5. REQUEST TO EXTEND CLOSING DATE
6. DEAL IS FALLING APART — save the transaction

For each:
• OPENING LINE (de-escalate, empathise)
• AGENT'S CORE POSITION (3 bullet points)
• COUNTER PROPOSAL (specific, confident)
• WHAT NOT TO SAY (2 mistakes)
• CLOSING LINE

Language: {lang}"""),

    ("bio", "👤 Agent Biography",
     "Three professional bios — micro (55 words), standard (160 words), full (320 words)",
     """Write 3 professional real estate agent biographies.
Agent: {name} | Agency: {co} | Market: {loc} | Phone: {phone} | Email: {email}

VERSION 1 — MICRO BIO (55 words maximum)
For: Instagram bio, business card, email signature
Style: First person, punchy, unique value proposition

VERSION 2 — STANDARD BIO (160 words)
For: Website about page, property portals, LinkedIn
Style: Third person, expertise + results + philosophy

VERSION 3 — FULL BIOGRAPHY (320 words)
For: Press releases, media kits, award submissions
Style: Third person, narrative arc, career highlights, client philosophy, personal element, market expertise
Include a placeholder section for awards/achievements.

Tone: Authoritative yet personable. Real and specific.
Language: {lang}"""),

    ("openhouse", "🏠 Open House Event Guide",
     "Complete event guide from pre-show prep to same-day follow-up",
     """Write a COMPLETE OPEN HOUSE EVENT GUIDE.
Property: {prop} at {loc} | Price: {price} | {beds} beds | {baths} baths | {sqm} m²
Agent: {name} | {co} | {phone}

Include:
1. PRE-EVENT CHECKLIST (12 preparation tasks with timeframes)
2. WELCOME SCRIPT (door greeting, 45-second version and 2-minute version)
3. PROPERTY TOUR — room-by-room talking points (8 rooms/areas)
4. TOP 6 SELLING POINTS to memorise and emphasise
5. PRICE OBJECTION RESPONSES (4 on-the-spot responses)
6. SIGN-IN CONVERSATION OPENER (get details naturally)
7. INTEREST GAUGING QUESTIONS (5 qualifying questions)
8. OFFER CONVERSATION (how to move from interest to offer)
9. SAME-DAY FOLLOW-UP SMS (max 155 chars, send within 2 hours)
10. SAME-DAY FOLLOW-UP WHATSAPP (slightly longer, warmer)
11. NEXT-DAY EMAIL (Subject + 130-word body)

Language: {lang}"""),

    ("followup", "📞 Follow-Up Sequence",
     "14-day multi-channel follow-up system with every message written",
     """Create a COMPLETE 14-DAY POST-VIEWING FOLLOW-UP SEQUENCE.
Property: {prop} at {loc} | Price: {price}
Agent: {name} | {co} | {phone} | {email}

Write EVERY message in full:

Day 0 (same day, 2 hours after viewing):
• SMS (155 chars max)
• WhatsApp (200 chars, slightly warmer)

Day 1:
• Email — Subject + 150-word warm recap + agent signature

Day 3:
• Email — Subject + 130-word neighbourhood guide highlights + signature

Day 5:
• SMS — Gentle check-in (120 chars max)

Day 7:
• Email — Subject + 120-word market update + competing interest angle + signature

Day 10:
• Phone call outline (2-min script, 6 bullet points)

Day 14:
• Email — Subject + 100-word final opportunity message + signature

Tone: Warm, professional, helpful — never pushy or desperate.
Language: {lang}"""),

    ("investment", "💰 Investment Analysis Memo",
     "Full ROI, yield, and cash flow analysis for investor-focused properties",
     """Write a comprehensive REAL ESTATE INVESTMENT ANALYSIS MEMO.
Property: {prop} at {loc} | Purchase Price: {price} | Size: {sqm} m² | Beds: {beds}
Prepared by: {name} | {co}

Include:
1. INVESTMENT SNAPSHOT (3-bullet executive summary)
2. ACQUISITION COSTS (purchase price + agent fees + legal + taxes — use typical % estimates)
3. RENTAL INCOME PROJECTIONS
   — Short-term rental (Airbnb/VRBO): nightly rate estimate, occupancy rate, monthly gross
   — Long-term rental: monthly rent estimate, annual gross
4. GROSS RENTAL YIELD (both scenarios)
5. OPERATING EXPENSES (management, maintenance, insurance, vacancy allowance)
6. NET OPERATING INCOME (NOI) for both scenarios
7. CAP RATE analysis and interpretation
8. CASH-ON-CASH RETURN (assuming 25% deposit, 75% mortgage)
9. 5-YEAR CAPITAL APPRECIATION
   — Conservative (-5% / 0% / +3%)
   — Base case (market average)
   — Optimistic (+5% annual)
10. BREAK-EVEN TIMELINE
11. EXIT STRATEGY OPTIONS (3 options with pros/cons)
12. KEY RISK FACTORS (5 risks with mitigation)
13. INVESTMENT VERDICT (professional recommendation)
14. DISCLAIMER

Use tables where appropriate. Professional investment memo format.
Language: {lang}"""),

    ("checklist", "✅ Transaction Checklists",
     "Complete step-by-step transaction checklists for buyers and sellers",
     """Create COMPREHENSIVE REAL ESTATE TRANSACTION CHECKLISTS.
Agent: {name} | {co}

PART 1 — SELLER TRANSACTION CHECKLIST
Minimum 36 tasks. Group into 6 phases:
Phase 1: Pre-Listing Preparation (8 tasks)
Phase 2: Active Listing (8 tasks)
Phase 3: Offer & Negotiation (6 tasks)
Phase 4: Under Contract (6 tasks)
Phase 5: Pre-Closing (5 tasks)
Phase 6: Closing Day & After (5 tasks)

PART 2 — BUYER TRANSACTION CHECKLIST
Minimum 33 tasks. Group into 6 phases:
Phase 1: Pre-Search Preparation (6 tasks)
Phase 2: Property Search (6 tasks)
Phase 3: Making an Offer (6 tasks)
Phase 4: Under Contract (5 tasks)
Phase 5: Financing & Inspection (5 tasks)
Phase 6: Closing & Moving In (5 tasks)

Format: ☐ [Task] | Owner | Notes field
Language: {lang}"""),

    ("neighborhood", "🗺️ Neighbourhood Guide",
     "Comprehensive buyer's area guide that overcomes location hesitation",
     """Write a COMPREHENSIVE NEIGHBOURHOOD GUIDE FOR BUYERS.
Area: {loc} | Property: {prop} | Price: {price}
Prepared by: {name} | {co}

10 sections:
1. AREA CHARACTER & IDENTITY (2 paragraphs — honest, specific, compelling)
2. TRANSPORT & COMMUTING (distances to main hubs, all transport modes, commute times)
3. SCHOOLS & EDUCATION (all levels, Ofsted/rating placeholder, catchment note)
4. DINING, SHOPPING & ENTERTAINMENT (10+ specific recommendations by type)
5. PARKS, SPORT & OUTDOOR LIFESTYLE (green spaces, recreation, gym culture)
6. HEALTHCARE & ESSENTIAL SERVICES (GP, hospital, pharmacies)
7. SAFETY & COMMUNITY FEEL (honest, balanced assessment)
8. PROPERTY MARKET OVERVIEW (price trends, recent activity, buyer competition)
9. 5 REASONS LOCALS LOVE THIS AREA (genuine, specific, compelling)
10. FUTURE GROWTH & DEVELOPMENT PROSPECTS (regeneration, infrastructure, investment)

AGENT'S RECOMMENDATION (3 sentences — personal, professional endorsement)
DISCLAIMER (standard professional disclaimer)

Informative, honest, genuinely useful. Language: {lang}"""),

    ("press", "📰 Press Releases",
     "Two professional press releases — property launch and market update",
     """Write 2 AP-style press releases.
Agency: {co} | Agent: {name} | {phone} | {email}
Property: {prop} at {loc} | Price: {price} | Date: {date}

PRESS RELEASE 1 — LUXURY PROPERTY LAUNCH
Structure:
• FOR IMMEDIATE RELEASE
• HEADLINE (max 12 words, news-style)
• SUBHEADING (max 20 words, key hook)
• DATELINE + City, Date
• Lead paragraph (who, what, where, when, why)
• Property description (2 paragraphs, vivid, specific)
• Market context paragraph
• Agent quote (2–3 sentences in quotation marks)
• About [Agency Name] — boilerplate (60 words)
• ###
• Media Contact block (full details)

PRESS RELEASE 2 — MARKET UPDATE / AGENCY NEWS
• Same structure, focus on market conditions or agency milestone
• Include relevant statistics (use placeholders where needed)
• Executive quote

Both: 380–420 words. Clean AP style. Professional.
Language: {lang}"""),

    ("mortgage", "🏦 Buyer's Finance Guide",
     "Complete guide to mortgages, financing options, and hidden costs",
     """Write a COMPREHENSIVE BUYER'S FINANCE & MORTGAGE GUIDE for the {loc} market.
Prepared by: {name} | {co}

12 sections:
1. WHY FINANCE PLANNING IS CRITICAL (importance, timing, common mistakes)
2. HOW MUCH CAN YOU BORROW? (income multiples, DTI ratio, affordability calculators)
3. DEPOSIT REQUIREMENTS (typical percentages, LTV bands, impact on rate)
4. TYPES OF MORTGAGES — comparison table:
   Fixed Rate | Variable/Tracker | Interest-Only | Repayment
   (Pros, Cons, Best For, Typical Rate Type)
5. COMPLETE COST OF BUYING (all fees as % estimates: stamp duty/transfer tax, legal, survey, agent, mortgage arrangement, removal)
6. STEP-BY-STEP APPLICATION PROCESS (8 steps with timeframes)
7. COMMON REJECTION REASONS (8 reasons + how to avoid each)
8. FIRST-TIME BUYER ADVANTAGES (schemes, tax relief, tips)
9. INVESTOR MORTGAGE SPECIFICS (buy-to-let rules, yield requirements, tax implications)
10. REMORTGAGING STRATEGY (when to remortgage, how to find best deal)
11. GLOSSARY OF KEY TERMS (18 terms, plain English definitions)
12. NEXT STEPS & DISCLAIMER

Accessible, jargon-free, genuinely useful.
Language: {lang}"""),
]


def page_tools():
    st.markdown(f"""
    <div class='page-header'>
      <div class='section-title'>{T['tools_title']}</div>
      <div class='section-sub'>{T['tools_sub']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Show existing tool output at top
    if st.session_state.tool_out:
        st.markdown(
            f"<div class='glass-card' style='margin-bottom:1.25rem;'>"
            f"<div style='font-family:Syne,sans-serif;font-weight:700;color:var(--gold);"
            f"font-size:0.95rem;margin-bottom:0.75rem;'>📄 {st.session_state.tool_title}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        edited = st.text_area("", value=st.session_state.tool_out, height=540, key="tool_ta_main")
        w, c = wc(edited)
        st.markdown(
            f"<div class='wc-row'>"
            f"<span class='wc-chip'>📊 {w} {T['words']}</span>"
            f"<span class='wc-chip'>✏️ {c} {T['chars']}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        tc1, tc2, tc3 = st.columns(3)
        with tc1:
            st.download_button(
                T["dl_tool"], data=edited,
                file_name=f"sarsa_tool_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                use_container_width=True, key="tool_dl_btn",
            )
        with tc2:
            copy_button(edited, T["copy_btn"], T["copied_btn"], "tool_out")
        with tc3:
            if st.button(T["clear_tool"], use_container_width=True, key="tool_clear_btn"):
                st.session_state.tool_out = ""
                st.session_state.tool_title = ""
                st.rerun()

        st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)

    # Tool grid
    for i in range(0, len(TOOLS), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(TOOLS):
                break
            tid, tname, tdesc, tprompt = TOOLS[idx]
            with col:
                st.markdown(
                    f"<div class='tool-card'>"
                    f"<div class='tool-name'>{tname}</div>"
                    f"<div class='tool-desc'>{tdesc}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if st.button(T["run_tool"], key=f"tool_run_{tid}", use_container_width=True):
                    with st.spinner(f"✨ {tname}…"):
                        filled = tprompt.format(
                            name=st.session_state.agent_name   or "the agent",
                            co=st.session_state.agent_co       or "the agency",
                            loc=st.session_state.location      or "the local market",
                            prop=st.session_state.prop_type    or "residential property",
                            price=st.session_state.price       or "market price",
                            beds=st.session_state.beds         or "N/A",
                            baths=st.session_state.baths       or "N/A",
                            sqm=st.session_state.sqm           or "N/A",
                            phone=st.session_state.agent_phone or "your phone",
                            email=st.session_state.agent_email or "your email",
                            lang=st.session_state.write_in     or "English",
                            date=datetime.now().strftime("%B %d, %Y"),
                        )
                        try:
                            r = model.generate_content(filled)
                            st.session_state.tool_out   = r.text
                            st.session_state.tool_title = tname
                            st.rerun()
                        except Exception as e:
                            st.error(f"{T['err']}{e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
def page_history():
    hist = st.session_state.get("history", [])
    st.markdown(f"""
    <div class='page-header'>
      <div class='section-title'>{T['hist_title']}</div>
      <div class='section-sub'>{len(hist)} saved listing{"s" if len(hist) != 1 else ""}</div>
    </div>
    """, unsafe_allow_html=True)

    if not hist:
        st.markdown(f"""
        <div class='empty-state'>
          <div class='empty-icon'>📁</div>
          <div class='empty-title'>{T['hist_title']}</div>
          <div class='empty-sub'>{T['hist_empty']}</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for i, entry in enumerate(hist):
        label = f"🏢  {entry['prop']}  ·  {entry['loc']}  ·  {entry['price']}  ·  {entry['date']}"
        with st.expander(label, expanded=(i == 0)):
            htabs = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"]])
            for ni, ht in enumerate(htabs):
                with ht:
                    v = entry.get(f"s{ni+1}", "")
                    st.text_area("", value=v, height=280, key=f"hs{ni+1}_{i}", disabled=True)

            hc1, hc2, hc3 = st.columns(3)
            with hc1:
                if st.button(T["load_btn"], key=f"hl_{i}", use_container_width=True):
                    for n in range(1, 7):
                        st.session_state[f"s{n}"] = entry.get(f"s{n}", "")
                    st.session_state.output_raw = entry.get("s1", "dummy")
                    st.session_state.dirty = False
                    st.session_state.page = "generate"
                    st.rerun()
            with hc2:
                exp_data = "\n\n".join(entry.get(f"s{n}", "") for n in range(1, 7))
                st.download_button(
                    T["dl_section"], data=exp_data,
                    file_name=f"sarsa_hist_{entry['id'][:8]}.txt",
                    key=f"hd_{i}", use_container_width=True,
                )
            with hc3:
                if st.button(T["del_btn"], key=f"hdel_{i}", use_container_width=True):
                    st.session_state.history.pop(i)
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
page = st.session_state.get("page", "generate")

if page == "generate":
    page_generate()
elif page == "tools":
    page_tools()
elif page == "history":
    page_history()
else:
    page_generate()
