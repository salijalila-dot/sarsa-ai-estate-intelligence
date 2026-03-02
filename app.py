import streamlit as st 
from PIL import Image 
import google.generativeai as genai 
import os 

# --- AI YAPILANDIRMASI --- 
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"] 
genai.configure(api_key=GOOGLE_API_KEY) 
MODEL_NAME = 'gemini-2.5-flash'  
model = genai.GenerativeModel(MODEL_NAME) 

# --- SAYFA AYARLARI --- 
st.set_page_config(page_title="SarSa AI | Real Estate Analysis & Marketing Engine", page_icon="🏢", layout="wide") 

# --- HIZLANDIRICI --- 
@st.cache_data 
def load_logo(file_path): 
    if os.path.exists(file_path): return Image.open(file_path) 
    return None 

# --- GLOBAL DİL SİSTEMİ (PLACEHOLDER VE VARSAYILAN AYAR GÜNCELLEMESİ) --- 
ui_languages = { 
    "English": { 
        "title": "SarSa AI | Real Estate Analysis & Marketing Engine", 
        "service_desc": "All-in-One Visual Property Intelligence & Global Sales Automation", 
        "subtitle": "Transform property photos into premium listings, social media kits, cinematic video scripts, and technical data sheets instantly.",
        "settings": "⚙️ Configuration", "target_lang": "✍️ Write Listing In...", "prop_type": "Property Type", "price": "Market Price", "location": "Location", "tone": "Strategy",
        "tones": ["Standard Pro", "Ultra-Luxury", "Investment Potential", "Modern Minimalist", "Family Comfort"],
        "ph_prop": "E.g., 3+1 Apartment, Luxury Villa...", "ph_price": "E.g., $500,000 or £2,000/mo...", "ph_loc": "E.g., Manhattan, NY or London, UK...",
        "custom_inst": "📝 Special Notes", "custom_inst_ph": "E.g., High ceilings, near metro...", "btn": "🚀 GENERATE COMPLETE MARKETING ASSETS", "upload_label": "📸 Drop Property Photos Here",
        "result": "💎 Executive Preview", "loading": "Crafting your premium marketing ecosystem...", "empty": "Awaiting visuals to start professional analysis.", "download": "📥 Export TXT", "save_btn": "💾 Save Changes", "saved_msg": "✅ Saved!", "error": "Error:",
        "tab_main": "📝 Prime Listing", "tab_social": "📱 Social Media Kit", "tab_video": "🎬 Video Scripts", "tab_tech": "⚙️ Technical Specs", "label_main": "Sales Copy", "label_social": "Social Media Content", "label_video": "Video Script", "label_tech": "Technical Specifications"
    }, 
    "Türkçe": { 
        "title": "SarSa AI | Gayrimenkul Analiz ve Pazarlama Motoru", 
        "service_desc": "Hepsi Bir Arada Görsel Mülk Zekası ve Küresel Satış Otomasyonu", 
        "subtitle": "Mülk fotoğraflarını anında profesyonel ilanlara, sosyal medya kitlerine, sinematik video senaryolarına ve teknik şartnamelere dönüştürün.",
        "settings": "⚙️ Yapılandırma", "target_lang": "✍️ İlan Yazım Dili...", "prop_type": "Emlak Tipi", "price": "Pazar Fiyatı", "location": "Konum", "tone": "Strateji",
        "tones": ["Standart Profesyonel", "Ultra-Lüks", "Yatırım Potansiyeli", "Modern Minimalist", "Aile Konforu"],
        "ph_prop": "Örn: 3+1 Daire, Müstakil Villa...", "ph_price": "Örn: 5.000.000 TL veya $2.500/ay...", "ph_loc": "Örn: Beşiktaş, İstanbul...",
        "custom_inst": "📝 Özel Notlar", "custom_inst_ph": "Örn: Yüksek tavanlar, metroya yakın...", "btn": "🚀 TÜM PAZARLAMA VARLIKLARINI OLUŞTUR", "upload_label": "📸 Fotoğrafları Buraya Bırakın",
        "result": "💎 Yönetici Önizlemesi", "loading": "Premium pazarlama ekosisteminiz hazırlanıyor...", "empty": "Profesyonel analiz için görsel bekleniyor.", "download": "📥 TXT Olarak İndir", "save_btn": "💾 Kaydet", "saved_msg": "✅ Kaydedildi!", "error": "Hata:",
        "tab_main": "📝 Ana İlan", "tab_social": "📱 Sosyal Medya Kiti", "tab_video": "🎬 Video Senaryoları", "tab_tech": "⚙️ Teknik Özellikler", "label_main": "Satış Metni", "label_social": "Sosyal Medya", "label_video": "Video Script", "label_tech": "Teknik Detaylar"
    },
    "Español": { 
        "title": "SarSa AI | Motor de Marketing y Análisis Inmobiliario", 
        "service_desc": "Inteligencia Visual de Propiedades y Automatización de Ventas Globales", 
        "subtitle": "Convierta fotos en anuncios premium, kits de redes sociales, guiones de video y fichas técnicas al instante.",
        "settings": "⚙️ Configuración", "target_lang": "✍️ Escribir en...", "prop_type": "Tipo de Propiedad", "price": "Precio de Mercado", "location": "Ubicación", "tone": "Estrategia",
        "tones": ["Profesional Estándar", "Ultra-Lujo", "Potencial de Inversión", "Minimalista Moderno", "Confort Familiar"],
        "ph_prop": "Ej: Apartamento 3+1, Villa de Lujo...", "ph_price": "Ej: $500.000 o €1.500/mes...", "ph_loc": "Ej: Madrid, España...",
        "custom_inst": "📝 Notas Especiales", "custom_inst_ph": "Ej: Techos altos, cerca del metro...", "btn": "🚀 GENERAR ACTIVOS DE MARKETING COMPLETOS", "upload_label": "📸 Subir Fotos Aquí",
        "result": "💎 Vista Previa Ejecutiva", "loading": "Creando su ecosistema de marketing...", "empty": "Esperando imágenes para análisis profesional.", "download": "📥 Exportar TXT", "save_btn": "💾 Guardar Cambios", "saved_msg": "✅ ¡Guardado!", "error": "Error:",
        "tab_main": "📝 Anuncio Premium", "tab_social": "📱 Kit de Redes", "tab_video": "🎬 Guiones de Video", "tab_tech": "⚙️ Especificaciones", "label_main": "Texto de Ventas", "label_social": "Contenido Social", "label_video": "Guion de Video", "label_tech": "Ficha Técnica"
    },
    "Deutsch": { 
        "title": "SarSa AI | Immobilienanalyse & Marketing-Plattform", 
        "service_desc": "All-in-One Visuelle Objektintelligenz & Globale Verkaufsautomatisierung", 
        "subtitle": "Verwandeln Sie Fotos sofort in Premium-Exposés, Social-Media-Kits, Videoskripte und Datenblätter.",
        "settings": "⚙️ Konfiguration", "target_lang": "✍️ Erstellen in...", "prop_type": "Objekttyp", "price": "Marktpreis", "location": "Standort", "tone": "Strategie",
        "tones": ["Standard-Profi", "Ultra-Luxus", "Investitionspotenzial", "Modern-Minimalistisch", "Familienkomfort"],
        "ph_prop": "Z.B. 3-Zimmer-Wohnung, Luxusvilla...", "ph_price": "Z.B. 500.000€ oder 2.000€/Monat...", "ph_loc": "Z.B. Berlin, Deutschland...",
        "custom_inst": "📝 Notizen", "custom_inst_ph": "Z.B. Hohe Decken, U-Bahn-Nähe...", "btn": "🚀 KOMPLETTE MARKETING-ASSETS ERSTELLEN", "upload_label": "📸 Fotos hier hochladen",
        "result": "💎 Executive-Vorschau", "loading": "Ihr Marketing-Ökosystem wird erstellt...", "empty": "Warte auf Bilder für die Analyse.", "download": "📥 TXT Exportieren", "save_btn": "💾 Speichern", "saved_msg": "✅ Gespeichert!", "error": "Fehler:",
        "tab_main": "📝 Premium-Exposé", "tab_social": "📱 Social Media Kit", "tab_video": "🎬 Videoskripte", "tab_tech": "⚙️ Tech-Details", "label_main": "Verkaufstext", "label_social": "Social Media Content", "label_video": "Video-Skript", "label_tech": "Technische Daten"
    },
    "Français": { 
        "title": "SarSa AI | Moteur d'Analyse et de Marketing Immobilier", 
        "service_desc": "Intelligence Visuelle Immobilière et Automatisation des Ventes Globales", 
        "subtitle": "Transformez vos photos en annonces premium, kits réseaux sociaux, scripts vidéo et fiches techniques.",
        "settings": "⚙️ Configuration", "target_lang": "✍️ Rédiger en...", "prop_type": "Type de Bien", "price": "Prix du Marché", "location": "Localisation", "tone": "Stratégie",
        "tones": ["Standard Pro", "Ultra-Luxe", "Potentiel d'Investissement", "Minimaliste Moderne", "Confort Familiar"],
        "ph_prop": "Ex: Appartement T4, Villa de Luxe...", "ph_price": "Ex: 500.000€ ou 1.500€/mois...", "ph_loc": "Ex: Paris, France...",
        "custom_inst": "📝 Notes Spéciales", "custom_inst_ph": "Ex: Plafonds hauts, proche métro...", "btn": "🚀 GÉNÉRER LES ACTIFS MARKETING COMPLETS", "upload_label": "📸 Déposer les Photos Ici",
        "result": "💎 Aperçu Exécutif", "loading": "Préparation de votre écosystème marketing...", "empty": "En attente d'images pour analyse.", "download": "📥 Exporter TXT", "save_btn": "💾 Enregistrer", "saved_msg": "✅ Enregistré !", "error": "Erreur :",
        "tab_main": "📝 Annonce Premium", "tab_social": "📱 Kit Réseaux Sociaux", "tab_video": "🎬 Scripts Vidéo", "tab_tech": "⚙️ Spécifications", "label_main": "Texte de Vente", "label_social": "Contenu Social", "label_video": "Script Vidéo", "label_tech": "Détails Techniques"
    },
    "Português": { 
        "title": "SarSa AI | Motor de Marketing e Análise Imobiliária", 
        "service_desc": "Inteligência Visual Imobiliária e Automação de Vendas Globais", 
        "subtitle": "Transforme fotos em anúncios premium, kits de redes sociais, roteiros de vídeo e fichas técnicas.",
        "settings": "⚙️ Configuração", "target_lang": "✍️ Escrever em...", "prop_type": "Tipo de Imóvel", "price": "Preço de Mercado", "location": "Localização", "tone": "Estrategia",
        "tones": ["Profissional Padrão", "Ultra-Luxo", "Potencial de Investimento", "Minimalista Moderno", "Conforto Familiar"],
        "ph_prop": "Ex: Apartamento T3, Moradia de Luxo...", "ph_price": "Ex: 500.000€ ou 1.500€/mês...", "ph_loc": "Ex: Lisboa, Portugal...",
        "custom_inst": "📝 Notas Especiais", "custom_inst_ph": "Ex: Tetos altos, perto do metrô...", "btn": "🚀 GERAR ATIVOS DE MARKETING COMPLETOS", "upload_label": "📸 Enviar Fotos Aqui",
        "result": "💎 Pré-visualização Executiva", "loading": "Preparando seu ecossistema de marketing...", "empty": "Aguardando imagens para análise.", "download": "📥 Exportar TXT", "save_btn": "💾 Salvar Alterações", "saved_msg": "✅ Salvo!", "error": "Erro:",
        "tab_main": "📝 Anúncio Premium", "tab_social": "📱 Kit Redes Sociais", "tab_video": "🎬 Roteiros de Vídeo", "tab_tech": "⚙️ Detalhes", "label_main": "Texto de Vendas", "label_social": "Conteúdo Social", "label_video": "Script de Vídeo", "label_tech": "Especificações Técnicas"
    },
    "日本語": { 
        "title": "SarSa AI | 不動産分析＆マーケティングエンジン", 
        "service_desc": "オールインワン物件インテリジェンス＆グローバル販売自動化", 
        "subtitle": "物件写真をプレミアム広告、SNSキット、動画台本、技術仕様書に瞬時に変換。",
        "settings": "⚙️ 設定", "target_lang": "✍️ 作成言語...", "prop_type": "物件種別", "price": "市場価格", "location": "所在地", "tone": "戦略",
        "tones": ["スタンダードプロ", "ウルトララグジュアリー", "投資ポテンシャル", "モダンミニマリスト", "ファミリーコンフォート"],
        "ph_prop": "例：3LDKマンション、高級別荘...", "ph_price": "例：5000万円、月20万円...", "ph_loc": "例：東京都港区...",
        "custom_inst": "📝 特記事項", "custom_inst_ph": "例：高い天井、駅近...", "btn": "🚀 完全なマーケティング資産を生成", "upload_label": "📸 ここに写真をアップロード",
        "result": "💎 エグゼクティブプレビュー", "loading": "マーケティングエコシステムを構築中...", "empty": "分析用の画像を待機中。", "download": "📥 TXT出力", "save_btn": "💾 変更を保存", "saved_msg": "✅ 保存完了！", "error": "エラー:",
        "tab_main": "📝 プレミアム広告", "tab_social": "📱 SNSキット", "tab_video": "🎬 動画台本", "tab_tech": "⚙️ 技術仕様", "label_main": "セールスコピー", "label_social": "SNSコンテンツ", "label_video": "動画台本", "label_tech": "技術仕様"
    },
    "中文 (简体)": { 
        "title": "SarSa AI | 房地产分析与营销引擎", 
        "service_desc": "全方位房产视觉智能与全球销售自动化", 
        "subtitle": "立即将房产照片转化为优质房源描述、社交媒体包、电影级视频脚本和技术规格。",
        "settings": "⚙️ 配置", "target_lang": "✍️ 编写语言...", "prop_type": "房产类型", "price": "市场价格", "location": "地点", "tone": "策略",
        "tones": ["标准专业", "顶奢豪宅", "投资潜力", "现代简约", "家庭舒适"],
        "ph_prop": "例如：3居室公寓，豪华别墅...", "ph_price": "例如：$500,000 或 $2,000/月...", "ph_loc": "例如：上海市浦东新区...",
        "custom_inst": "📝 特别备注", "custom_inst_ph": "例如：挑高天花板，靠近地铁...", "btn": "🚀 生成完整营销资产", "upload_label": "📸 在此处上传照片",
        "result": "💎 高管预览", "loading": "正在打造您的营销生态系统...", "empty": "等待图像进行分析。", "download": "📥 导出 TXT", "save_btn": "💾 保存更改", "saved_msg": "✅ 已保存！", "error": "错误:",
        "tab_main": "📝 优质房源", "tab_social": "📱 社交媒体包", "tab_video": "🎬 视频脚本", "tab_tech": "⚙️ 技术细节", "label_main": "销售文案", "label_social": "社媒内容", "label_video": "视频脚本", "label_tech": "技术规格"
    },
    "العربية": { 
        "title": "SarSa AI | محرك تحليل وتسويق العقارات", 
        "service_desc": "ذكاء العقارات البصري المتكامل وأتمتة المبيعات العالمية", 
        "subtitle": "حوّل صور العقارات إلى إعلانات مميزة، باقات تواصل اجتماعي، سيناريوهات فيديو، ومواصفات فنية فوراً.",
        "settings": "⚙️ الإعدادات", "target_lang": "✍️ لغة الكتابة...", "prop_type": "نوع العقار", "price": "سعر السوق", "location": "الموقع", "tone": "الاستراتيجية",
        "tones": ["احترافي قياسي", "فخامة فائقة", "إمكانات استثمارية", "عصري بسيط", "راحة عائلية"],
        "ph_prop": "مثال: شقة 3+1، فيلا فاخرة...", "ph_price": "مثال: $500,000 أو $2,000 شهرياً...", "ph_loc": "مثال: دبي، الإمارات...",
        "custom_inst": "📝 ملاحظات خاصة", "custom_inst_ph": "مثال: أسقف عالية، بالقرب من المترو...", "btn": "🚀 إنشاء أصول تسويقية متكاملة", "upload_label": "📸 ضع الصور هنا",
        "result": "💎 معاينة تنفيذية", "loading": "جاري تجهيز منظومتك التسويقية الفاخرة...", "empty": "في انتظار الصور لبدء التحليل المهني.", "download": "📥 تصدير TXT", "save_btn": "💾 حفظ التغييرات", "saved_msg": "✅ تم الحفظ!", "error": "خطأ:",
        "tab_main": "📝 إعلان مميز", "tab_social": "📱 باقة التواصل", "tab_video": "🎬 سيناريوهات الفيديو", "tab_tech": "⚙️ تفاصيل", "label_main": "نص المبيعات", "label_social": "محتوى التواصل", "label_video": "سيناريو الفيديو", "label_tech": "المواصفات الفنية"
    }
} 

# --- SESSION STATE (TEMİZ BAŞLANGIÇ AYARLARI) --- 
# Başlangıç değerleri boş bırakıldı ki placeholder'lar görünsün.
for key, val in [("uretilen_ilan", ""), ("prop_type", ""), ("price", ""), ("location", ""), ("tone", ""), ("custom_inst", ""), ("target_lang_input", "English")]:
    if key not in st.session_state: st.session_state[key] = val

# --- CSS (STİL KORUNDU) --- 
st.markdown(""" 
    <style> 
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap'); 
        html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; } 
        .stApp { background-color: #f8fafc; } 
         
        div[data-testid="stInputInstructions"] { display: none !important; }

        .block-container { background: white; padding: 3rem !important; border-radius: 20px; box-shadow: 0 15px 45px rgba(0,0,0,0.04); margin-top: 2rem; border: 1px solid #e2e8f0; } 
        h1 { color: #0f172a !important; font-weight: 800 !important; text-align: center; } 
          
        button, [data-baseweb="tab"], [data-testid="stFileUploader"],  
        div[data-baseweb="select"], div[role="button"], .stSelectbox div { 
            cursor: pointer !important; 
        } 
         
        .stTextInput input, .stTextArea textarea { cursor: text !important; }

        span[data-testid="stIconMaterial"] { font-size: 0px !important; color: transparent !important; }
        span[data-testid="stIconMaterial"]::before { content: "⬅️" !important; font-size: 18px !important; color: #0f172a !important; visibility: visible !important; display: block !important; cursor: pointer !important; }

        .stButton>button { background: #0f172a; color: white !important; border-radius: 10px; padding: 14px; font-weight: 600; width: 100%; border: none; }
        .stButton>button:hover { background: #1e293b; box-shadow: 0 4px 12px rgba(0,0,0,0.1); } 
         
        .stTabs [aria-selected="true"] { background-color: #0f172a !important; color: white !important; border-radius: 8px 8px 0 0; }
    </style> 
""", unsafe_allow_html=True) 

# --- SIDEBAR --- 
with st.sidebar: 
    logo_img = load_logo("SarSa_Logo_Transparent.png") 
    if logo_img: st.image(logo_img, use_container_width=True) 
    else: st.markdown("<h2 style='text-align:center; color:#0f172a;'>SARSA AI</h2>", unsafe_allow_html=True) 
      
    current_ui_lang = st.selectbox("🌐 Interface Language", list(ui_languages.keys()), index=0)   
    t = ui_languages[current_ui_lang] 
      
    st.markdown("---") 
    st.header(t["settings"]) 
    st.session_state.target_lang_input = st.text_input(t["target_lang"], value=st.session_state.target_lang_input) 
    
    # Placeholder eklenen girişler:
    st.session_state.prop_type = st.text_input(t["prop_type"], value=st.session_state.prop_type, placeholder=t["ph_prop"]) 
    st.session_state.price = st.text_input(t["price"], value=st.session_state.price, placeholder=t["ph_price"]) 
    st.session_state.location = st.text_input(t["location"], value=st.session_state.location, placeholder=t["ph_loc"]) 
      
    # Varsayılan strateji artık listenin ilk elemanı olan "Standard Pro / Standart Profesyonel"
    current_tone_idx = t["tones"].index(st.session_state.tone) if st.session_state.tone in t["tones"] else 0
    st.session_state.tone = st.selectbox(t["tone"], t["tones"], index=current_tone_idx) 
    st.session_state.custom_inst = st.text_area(t["custom_inst"], value=st.session_state.custom_inst, placeholder=t["custom_inst_ph"]) 

# --- ANA EKRAN --- 
st.markdown(f"<h1>🏢 {t['title']}</h1>", unsafe_allow_html=True) 
st.markdown(f"<p style='text-align:center; color:#0f172a; font-weight:700; font-size:1.4rem; letter-spacing:0.5px; margin-bottom:5px;'>{t['service_desc']}</p>", unsafe_allow_html=True) 
st.markdown(f"<div style='text-align:center; color:#64748b; font-size:1.1rem; max-width:850px; margin: 0 auto 2rem auto; line-height:1.5;'>{t['subtitle']}</div>", unsafe_allow_html=True) 

uploaded_files = st.file_uploader(t["upload_label"], type=["jpg", "png", "webp", "jpeg"], accept_multiple_files=True) 

if uploaded_files: 
    cols = st.columns(4) 
    images_for_ai = [Image.open(f) for f in uploaded_files] 
    for i, img in enumerate(images_for_ai): 
        with cols[i % 4]: st.image(img, use_container_width=True) 

    if st.button(t["btn"]): 
        with st.spinner(t["loading"]): 
            # Boş bırakılan alanlar için AI'a yardımcı bilgi gönderimi
            p_type = st.session_state.prop_type if st.session_state.prop_type else "Property"
            p_loc = st.session_state.location if st.session_state.location else "undisclosed location"
            
            expert_prompt = (f"Role: Senior Architect & Global Real Estate Strategist for SarSa AI. "
                             f"Target Language: {st.session_state.target_lang_input}. "
                             f"Property: {p_type} at {p_loc}. "
                             f"Strategy: {st.session_state.tone}. "
                             f"Structure: Split response using ## SECTION_1 (Main Listing), ## SECTION_2 (Social Media Kit - Captions & Hashtags), ## SECTION_3 (Cinematic Video Script), ## SECTION_4 (Technical Specifications).")
            try: 
                response = model.generate_content([expert_prompt] + images_for_ai) 
                st.session_state.uretilen_ilan = response.text 
            except Exception as e: 
                st.error(f"{t['error']} {e}") 

    if st.session_state.uretilen_ilan: 
        st.markdown("---") 
        st.subheader(t["result"]) 
        raw_text = st.session_state.uretilen_ilan 
        parts = raw_text.split("##") 
        sec1, sec2, sec3, sec4 = "", "", "", "" 
        for p in parts: 
            if "SECTION_1" in p: sec1 = p.replace("SECTION_1", "").split(":", 1)[-1].strip() 
            elif "SECTION_2" in p: sec2 = p.replace("SECTION_2", "").split(":", 1)[-1].strip() 
            elif "SECTION_3" in p: sec3 = p.replace("SECTION_3", "").split(":", 1)[-1].strip() 
            elif "SECTION_4" in p: sec4 = p.replace("SECTION_4", "").split(":", 1)[-1].strip() 

        tab1, tab2, tab3, tab4 = st.tabs([t["tab_main"], t["tab_social"], t["tab_video"], t["tab_tech"]]) 
         
        with tab1: res_ana = st.text_area(t["label_main"], value=sec1 if sec1 else raw_text, height=400, key="txt_ana") 
        with tab2: res_sosyal = st.text_area(t["label_social"], value=sec2, height=400, key="txt_sosyal") 
        with tab3: res_video = st.text_area(t["label_video"], value=sec3, height=400, key="txt_video") 
        with tab4: res_teknik = st.text_area(t["label_tech"], value=sec4, height=400, key="txt_teknik") 
          
        c1, c2 = st.columns(2) 
        with c1: 
            if st.button(t["save_btn"]): 
                st.session_state.uretilen_ilan = f"## SECTION_1\n{res_ana}\n\n## SECTION_2\n{res_sosyal}\n\n## SECTION_3\n{res_video}\n\n## SECTION_4\n{res_teknik}"
                st.success(t["saved_msg"]) 
        with c2: 
            st.download_button(t["download"], data=st.session_state.uretilen_ilan, file_name="sarsa_ai_export.txt") 
else: 
    st.info(t["empty"])
