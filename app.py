import streamlit as st
from PIL import Image
import google.generativeai as genai
import os, re
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────────────
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(
    page_title="SarSa AI · Real Estate Intelligence",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def load_logo(p):
    return Image.open(p) if os.path.exists(p) else None

# ── LANGUAGE STRINGS ─────────────────────────────────────────────────────────
LANGS = {
"English": dict(
  config_head="Property Details", write_in="Output Language", write_ph="e.g. English, French…",
  prop_type="Property Type", prop_ph="e.g. Luxury Villa, 3-Bed Apartment…",
  price="Asking Price", price_ph="e.g. $850,000 or €2,400/mo",
  location="Location", loc_ph="e.g. Downtown Miami, FL",
  beds="Beds", baths="Baths", sqm="Size m²", year="Year Built",
  parking="Parking", amenities="Key Features", amenities_ph="Pool, gym, sea view, smart home…",
  strategy="Marketing Strategy",
  strategies=["⭐ Standard Pro","💎 Ultra-Luxury","📈 Investment Focus",
               "🏡 Family Comfort","🎨 Modern Minimalist",
               "🏖️ Vacation Rental","🏗️ New Development","🏢 Commercial"],
  notes="Extra Notes", notes_ph="Renovated kitchen, near metro, no pets…",
  agent_head="Agent Profile",
  agent_name="Your Name", agent_name_ph="Sarah Johnson",
  agent_co="Agency / Company", agent_co_ph="Luxe Realty Group",
  agent_phone="Phone", agent_phone_ph="+1 305 000 0000",
  agent_email="Email", agent_email_ph="sarah@luxerealty.com",
  upload="📸   Drop property photos here  ·  JPG · PNG · WEBP",
  gen_btn="✦  GENERATE COMPLETE MARKETING PACKAGE",
  regen_btn="↺  Regenerate",
  loading_steps=["🔍 Analyzing photos with AI…",
                 "✍️ Writing premium listing copy…",
                 "📱 Building social media kit…",
                 "🎬 Scripting cinematic video…",
                 "⚙️ Compiling technical specs…",
                 "📧 Drafting email templates…",
                 "🔍 Building SEO pack…",
                 "✅ Finalizing your package…"],
  save="💾  Save to History", saved_ok="✅  Saved!",
  dl_all="⬇  Download All (.txt)", dl_tab="⬇  Download", copy="⎘  Copy", copied="✅ Copied!",
  empty_title="Your Marketing Package Appears Here",
  empty_sub="Upload property photos · Fill in the details · Hit Generate",
  tab_listing="📝 Listing", tab_social="📱 Social Media", tab_video="🎬 Video Script",
  tab_specs="⚙️ Tech Specs", tab_email="📧 Email Kit", tab_seo="🔍 SEO Pack",
  tab_tools="🛠️ Agent Tools", tab_history="📁 History",
  tools_head="AI Power Tools for Real Estate Agents",
  tools_sub="One click — get a professional deliverable instantly.",
  tool_run="Generate →", tool_clear="✕  Clear", tool_dl="⬇  Download",
  hist_empty="No saved listings yet — generate and save your first one.",
  hist_load="Load →", hist_del="Delete", hist_dl="Download",
  words="words", chars="chars",
  compliance_ok="✅ Fair housing check — no issues detected",
  compliance_warn="⚠️ Review flagged terms: ",
  unsaved="● Unsaved changes", all_saved="✔ All saved",
  photo_label="Photo", error_prefix="⚠️ Error: ",
),
"Türkçe": dict(
  config_head="Mülk Bilgileri", write_in="Çıktı Dili", write_ph="örn. Türkçe, İngilizce…",
  prop_type="Mülk Tipi", prop_ph="örn. Lüks Villa, 3+1 Daire…",
  price="Fiyat", price_ph="örn. 5.000.000₺ veya $2.500/ay",
  location="Konum", loc_ph="örn. Beşiktaş, İstanbul",
  beds="Yatak", baths="Banyo", sqm="Alan m²", year="Yapım Yılı",
  parking="Otopark", amenities="Özellikler", amenities_ph="Havuz, spor salonu, deniz manzarası…",
  strategy="Pazarlama Stratejisi",
  strategies=["⭐ Standart Pro","💎 Ultra-Lüks","📈 Yatırım Odaklı",
               "🏡 Aile Konforu","🎨 Modern Minimalist",
               "🏖️ Tatil Kiralaması","🏗️ Yeni Proje","🏢 Ticari"],
  notes="Ek Notlar", notes_ph="Tadilatlı mutfak, metroya yakın…",
  agent_head="Temsilci Profili",
  agent_name="Adınız", agent_name_ph="Ayşe Kaya",
  agent_co="Acente / Şirket", agent_co_ph="Lüks Emlak A.Ş.",
  agent_phone="Telefon", agent_phone_ph="+90 532 000 0000",
  agent_email="E-posta", agent_email_ph="ayse@luksemalik.com",
  upload="📸   Mülk fotoğraflarını buraya sürükleyin  ·  JPG · PNG · WEBP",
  gen_btn="✦  TAM PAZARLAMA PAKETİ OLUŞTUR",
  regen_btn="↺  Yeniden Oluştur",
  loading_steps=["🔍 Fotoğraflar analiz ediliyor…","✍️ Premium ilan metni yazılıyor…",
                 "📱 Sosyal medya kiti oluşturuluyor…","🎬 Video senaryosu yazılıyor…",
                 "⚙️ Teknik özellikler derleniyor…","📧 E-posta şablonları hazırlanıyor…",
                 "🔍 SEO paketi oluşturuluyor…","✅ Paketiniz tamamlanıyor…"],
  save="💾  Geçmişe Kaydet", saved_ok="✅  Kaydedildi!",
  dl_all="⬇  Tümünü İndir (.txt)", dl_tab="⬇  İndir", copy="⎘  Kopyala", copied="✅ Kopyalandı!",
  empty_title="Pazarlama Paketiniz Burada Görünecek",
  empty_sub="Fotoğraf yükleyin · Bilgileri doldurun · Oluştur'a basın",
  tab_listing="📝 İlan", tab_social="📱 Sosyal Medya", tab_video="🎬 Video Senaryosu",
  tab_specs="⚙️ Teknik", tab_email="📧 E-posta Kiti", tab_seo="🔍 SEO Paketi",
  tab_tools="🛠️ Ajan Araçları", tab_history="📁 Geçmiş",
  tools_head="Gayrimenkul Uzmanları İçin AI Güç Araçları",
  tools_sub="Tek tıkla profesyonel çıktı alın.",
  tool_run="Oluştur →", tool_clear="✕  Temizle", tool_dl="⬇  İndir",
  hist_empty="Henüz kayıtlı ilan yok — ilk ilanınızı oluşturun ve kaydedin.",
  hist_load="Yükle →", hist_del="Sil", hist_dl="İndir",
  words="kelime", chars="karakter",
  compliance_ok="✅ Adil konut kontrolü — sorun tespit edilmedi",
  compliance_warn="⚠️ İşaretlenen terimleri inceleyin: ",
  unsaved="● Kaydedilmemiş değişiklikler", all_saved="✔ Tümü kaydedildi",
  photo_label="Fotoğraf", error_prefix="⚠️ Hata: ",
),
"Español": dict(
  config_head="Detalles de la Propiedad", write_in="Idioma de Salida", write_ph="ej. Español, Inglés…",
  prop_type="Tipo de Propiedad", prop_ph="ej. Villa de Lujo, Piso 3 hab…",
  price="Precio", price_ph="ej. $850,000 o €2,400/mes",
  location="Ubicación", loc_ph="ej. Centro de Madrid",
  beds="Hab.", baths="Baños", sqm="m²", year="Año",
  parking="Garaje", amenities="Características", amenities_ph="Piscina, gimnasio, vistas al mar…",
  strategy="Estrategia de Marketing",
  strategies=["⭐ Estándar Pro","💎 Ultra-Lujo","📈 Inversión",
               "🏡 Confort Familiar","🎨 Minimalista Moderno",
               "🏖️ Alquiler Vacacional","🏗️ Nueva Construcción","🏢 Comercial"],
  notes="Notas Extra", notes_ph="Cocina reformada, cerca del metro…",
  agent_head="Perfil del Agente",
  agent_name="Tu Nombre", agent_name_ph="Carlos García",
  agent_co="Agencia / Empresa", agent_co_ph="Luxe Realty Group",
  agent_phone="Teléfono", agent_phone_ph="+34 600 000 000",
  agent_email="Email", agent_email_ph="carlos@luxerealty.es",
  upload="📸   Arrastra fotos de la propiedad aquí  ·  JPG · PNG · WEBP",
  gen_btn="✦  GENERAR PAQUETE COMPLETO DE MARKETING",
  regen_btn="↺  Regenerar",
  loading_steps=["🔍 Analizando fotos con IA…","✍️ Redactando anuncio premium…",
                 "📱 Creando kit de redes sociales…","🎬 Escribiendo guión de vídeo…",
                 "⚙️ Compilando especificaciones…","📧 Redactando plantillas de email…",
                 "🔍 Construyendo pack SEO…","✅ Finalizando tu paquete…"],
  save="💾  Guardar", saved_ok="✅  ¡Guardado!",
  dl_all="⬇  Descargar Todo (.txt)", dl_tab="⬇  Descargar", copy="⎘  Copiar", copied="✅ ¡Copiado!",
  empty_title="Tu Paquete de Marketing Aparecerá Aquí",
  empty_sub="Sube fotos · Rellena los detalles · Pulsa Generar",
  tab_listing="📝 Anuncio", tab_social="📱 Redes Sociales", tab_video="🎬 Guión Vídeo",
  tab_specs="⚙️ Especificaciones", tab_email="📧 Kit Email", tab_seo="🔍 Pack SEO",
  tab_tools="🛠️ Herramientas", tab_history="📁 Historial",
  tools_head="Herramientas IA para Agentes Inmobiliarios",
  tools_sub="Un clic — entregable profesional al instante.",
  tool_run="Generar →", tool_clear="✕  Limpiar", tool_dl="⬇  Descargar",
  hist_empty="Aún no hay listados guardados.",
  hist_load="Cargar →", hist_del="Eliminar", hist_dl="Descargar",
  words="palabras", chars="caracteres",
  compliance_ok="✅ Vivienda justa — sin problemas detectados",
  compliance_warn="⚠️ Revise los términos marcados: ",
  unsaved="● Cambios sin guardar", all_saved="✔ Todo guardado",
  photo_label="Foto", error_prefix="⚠️ Error: ",
),
"Deutsch": dict(
  config_head="Objektdetails", write_in="Ausgabesprache", write_ph="z.B. Deutsch, Englisch…",
  prop_type="Objekttyp", prop_ph="z.B. Luxusvilla, 3-Zi-Wohnung…",
  price="Preis", price_ph="z.B. 850.000€ oder 2.400€/Mo",
  location="Standort", loc_ph="z.B. München Innenstadt",
  beds="Zimmer", baths="Bad", sqm="m²", year="Baujahr",
  parking="Stellplatz", amenities="Merkmale", amenities_ph="Pool, Gym, Meerblick…",
  strategy="Marketingstrategie",
  strategies=["⭐ Standard-Profi","💎 Ultra-Luxus","📈 Investment",
               "🏡 Familienwohnen","🎨 Modern-Minimalistisch",
               "🏖️ Ferienmiete","🏗️ Neubau","🏢 Gewerbe"],
  notes="Notizen", notes_ph="Renovierte Küche, U-Bahn-Nähe…",
  agent_head="Makler-Profil",
  agent_name="Ihr Name", agent_name_ph="Thomas Müller",
  agent_co="Agentur / Firma", agent_co_ph="Luxe Realty GmbH",
  agent_phone="Telefon", agent_phone_ph="+49 89 000 0000",
  agent_email="E-Mail", agent_email_ph="thomas@luxerealty.de",
  upload="📸   Objektfotos hier ablegen  ·  JPG · PNG · WEBP",
  gen_btn="✦  KOMPLETTES MARKETING-PAKET ERSTELLEN",
  regen_btn="↺  Neu erstellen",
  loading_steps=["🔍 Fotos werden analysiert…","✍️ Premium-Exposé wird erstellt…",
                 "📱 Social-Media-Kit wird aufgebaut…","🎬 Videoskript wird verfasst…",
                 "⚙️ Technische Daten werden zusammengestellt…",
                 "📧 E-Mail-Vorlagen werden erstellt…",
                 "🔍 SEO-Paket wird aufgebaut…","✅ Ihr Paket wird fertiggestellt…"],
  save="💾  Im Verlauf speichern", saved_ok="✅  Gespeichert!",
  dl_all="⬇  Alles herunterladen (.txt)", dl_tab="⬇  Herunterladen", copy="⎘  Kopieren", copied="✅ Kopiert!",
  empty_title="Ihr Marketing-Paket erscheint hier",
  empty_sub="Fotos hochladen · Details ausfüllen · Erstellen klicken",
  tab_listing="📝 Exposé", tab_social="📱 Social Media", tab_video="🎬 Videoskript",
  tab_specs="⚙️ Technik", tab_email="📧 E-Mail-Kit", tab_seo="🔍 SEO-Paket",
  tab_tools="🛠️ Makler-Tools", tab_history="📁 Verlauf",
  tools_head="KI-Tools für Immobilienmakler",
  tools_sub="Ein Klick — sofort ein professionelles Ergebnis.",
  tool_run="Erstellen →", tool_clear="✕  Löschen", tool_dl="⬇  Herunterladen",
  hist_empty="Noch keine gespeicherten Objekte.",
  hist_load="Laden →", hist_del="Löschen", hist_dl="Herunterladen",
  words="Wörter", chars="Zeichen",
  compliance_ok="✅ Fairness-Prüfung — keine Probleme erkannt",
  compliance_warn="⚠️ Markierte Begriffe prüfen: ",
  unsaved="● Ungespeicherte Änderungen", all_saved="✔ Alles gespeichert",
  photo_label="Foto", error_prefix="⚠️ Fehler: ",
),
"Français": dict(
  config_head="Détails du Bien", write_in="Langue de Sortie", write_ph="ex. Français, Anglais…",
  prop_type="Type de Bien", prop_ph="ex. Villa de Luxe, Apt 3 pièces…",
  price="Prix", price_ph="ex. 850 000€ ou 2 400€/mois",
  location="Localisation", loc_ph="ex. Paris 16ème",
  beds="Ch.", baths="SDB", sqm="m²", year="Année",
  parking="Parking", amenities="Équipements", amenities_ph="Piscine, salle de sport, vue mer…",
  strategy="Stratégie Marketing",
  strategies=["⭐ Standard Pro","💎 Ultra-Luxe","📈 Investissement",
               "🏡 Confort Familial","🎨 Minimaliste Moderne",
               "🏖️ Location Vacances","🏗️ Nouvelle Construction","🏢 Commercial"],
  notes="Notes", notes_ph="Cuisine rénovée, proche métro…",
  agent_head="Profil Agent",
  agent_name="Votre Nom", agent_name_ph="Marie Dupont",
  agent_co="Agence / Société", agent_co_ph="Luxe Realty France",
  agent_phone="Téléphone", agent_phone_ph="+33 6 00 00 00 00",
  agent_email="Email", agent_email_ph="marie@luxerealty.fr",
  upload="📸   Déposez les photos ici  ·  JPG · PNG · WEBP",
  gen_btn="✦  GÉNÉRER LE PACK MARKETING COMPLET",
  regen_btn="↺  Régénérer",
  loading_steps=["🔍 Analyse des photos par l'IA…","✍️ Rédaction de l'annonce premium…",
                 "📱 Création du kit réseaux sociaux…","🎬 Écriture du script vidéo…",
                 "⚙️ Compilation des spécifications…","📧 Rédaction des emails…",
                 "🔍 Construction du pack SEO…","✅ Finalisation de votre pack…"],
  save="💾  Sauvegarder", saved_ok="✅  Sauvegardé!",
  dl_all="⬇  Tout télécharger (.txt)", dl_tab="⬇  Télécharger", copy="⎘  Copier", copied="✅ Copié!",
  empty_title="Votre Pack Marketing Apparaît Ici",
  empty_sub="Chargez des photos · Remplissez les détails · Cliquez sur Générer",
  tab_listing="📝 Annonce", tab_social="📱 Réseaux Sociaux", tab_video="🎬 Script Vidéo",
  tab_specs="⚙️ Spécifications", tab_email="📧 Kit Email", tab_seo="🔍 Pack SEO",
  tab_tools="🛠️ Outils Agent", tab_history="📁 Historique",
  tools_head="Outils IA pour Agents Immobiliers",
  tools_sub="Un clic — résultat professionnel instantané.",
  tool_run="Générer →", tool_clear="✕  Effacer", tool_dl="⬇  Télécharger",
  hist_empty="Aucun bien sauvegardé pour l'instant.",
  hist_load="Charger →", hist_del="Supprimer", hist_dl="Télécharger",
  words="mots", chars="caractères",
  compliance_ok="✅ Logement équitable — aucun problème détecté",
  compliance_warn="⚠️ Termes à vérifier : ",
  unsaved="● Modifications non enregistrées", all_saved="✔ Tout enregistré",
  photo_label="Photo", error_prefix="⚠️ Erreur : ",
),
"Português": dict(
  config_head="Detalhes do Imóvel", write_in="Idioma de Saída", write_ph="ex. Português, Inglês…",
  prop_type="Tipo de Imóvel", prop_ph="ex. Villa de Luxo, Apt T3…",
  price="Preço", price_ph="ex. 850.000€ ou 2.400€/mês",
  location="Localização", loc_ph="ex. Lisboa, Chiado",
  beds="Quartos", baths="WC", sqm="m²", year="Ano",
  parking="Garagem", amenities="Características", amenities_ph="Piscina, ginásio, vista mar…",
  strategy="Estratégia de Marketing",
  strategies=["⭐ Profissional Padrão","💎 Ultra-Luxo","📈 Investimento",
               "🏡 Conforto Familiar","🎨 Minimalista Moderno",
               "🏖️ Aluguer de Férias","🏗️ Nova Construção","🏢 Comercial"],
  notes="Notas", notes_ph="Cozinha renovada, perto do metro…",
  agent_head="Perfil do Agente",
  agent_name="O Seu Nome", agent_name_ph="Ana Silva",
  agent_co="Agência / Empresa", agent_co_ph="Luxe Realty Portugal",
  agent_phone="Telefone", agent_phone_ph="+351 91 000 0000",
  agent_email="Email", agent_email_ph="ana@luxerealty.pt",
  upload="📸   Arraste fotos do imóvel aqui  ·  JPG · PNG · WEBP",
  gen_btn="✦  GERAR PACOTE COMPLETO DE MARKETING",
  regen_btn="↺  Regenerar",
  loading_steps=["🔍 Analisando fotos com IA…","✍️ Redigindo anúncio premium…",
                 "📱 Criando kit de redes sociais…","🎬 Escrevendo guião de vídeo…",
                 "⚙️ Compilando especificações…","📧 Redigindo templates de email…",
                 "🔍 Construindo pack SEO…","✅ Finalizando o seu pacote…"],
  save="💾  Guardar", saved_ok="✅  Guardado!",
  dl_all="⬇  Descarregar Tudo (.txt)", dl_tab="⬇  Descarregar", copy="⎘  Copiar", copied="✅ Copiado!",
  empty_title="O Seu Pacote de Marketing Aparece Aqui",
  empty_sub="Carregue fotos · Preencha os detalhes · Clique em Gerar",
  tab_listing="📝 Anúncio", tab_social="📱 Redes Sociais", tab_video="🎬 Guião Vídeo",
  tab_specs="⚙️ Especificações", tab_email="📧 Kit Email", tab_seo="🔍 Pack SEO",
  tab_tools="🛠️ Ferramentas Agente", tab_history="📁 Histórico",
  tools_head="Ferramentas IA para Agentes Imobiliários",
  tools_sub="Um clique — resultado profissional instantâneo.",
  tool_run="Gerar →", tool_clear="✕  Limpar", tool_dl="⬇  Descarregar",
  hist_empty="Ainda sem imóveis guardados.",
  hist_load="Carregar →", hist_del="Apagar", hist_dl="Descarregar",
  words="palavras", chars="caracteres",
  compliance_ok="✅ Habitação justa — sem problemas detetados",
  compliance_warn="⚠️ Reveja os termos assinalados: ",
  unsaved="● Alterações não guardadas", all_saved="✔ Tudo guardado",
  photo_label="Foto", error_prefix="⚠️ Erro: ",
),
"日本語": dict(
  config_head="物件詳細", write_in="出力言語", write_ph="例: 日本語、英語…",
  prop_type="物件種別", prop_ph="例: 高級別荘、3LDKマンション…",
  price="価格", price_ph="例: 5,000万円 または 月20万円",
  location="所在地", loc_ph="例: 東京都港区",
  beds="寝室", baths="浴室", sqm="㎡", year="築年",
  parking="駐車場", amenities="設備・特徴", amenities_ph="プール、ジム、海景…",
  strategy="マーケティング戦略",
  strategies=["⭐ スタンダードプロ","💎 ウルトラ高級","📈 投資向け",
               "🏡 ファミリー向け","🎨 モダンミニマル",
               "🏖️ バケーションレンタル","🏗️ 新築物件","🏢 商業用"],
  notes="備考", notes_ph="リノベ済みキッチン、駅近…",
  agent_head="エージェントプロフィール",
  agent_name="お名前", agent_name_ph="田中 太郎",
  agent_co="会社・代理店", agent_co_ph="ラックスリアルティ",
  agent_phone="電話", agent_phone_ph="+81 3 0000 0000",
  agent_email="メール", agent_email_ph="tanaka@luxerealty.jp",
  upload="📸   物件写真をここにドロップ  ·  JPG · PNG · WEBP",
  gen_btn="✦  完全なマーケティングパッケージを生成",
  regen_btn="↺  再生成",
  loading_steps=["🔍 AIで写真を分析中…","✍️ プレミアム広告を作成中…",
                 "📱 SNSキットを構築中…","🎬 映像台本を執筆中…",
                 "⚙️ 技術仕様を整理中…","📧 メールテンプレートを作成中…",
                 "🔍 SEOパックを構築中…","✅ パッケージを仕上げ中…"],
  save="💾  履歴に保存", saved_ok="✅  保存しました！",
  dl_all="⬇  全てダウンロード (.txt)", dl_tab="⬇  ダウンロード", copy="⎘  コピー", copied="✅ コピー完了！",
  empty_title="マーケティングパッケージはここに表示されます",
  empty_sub="写真をアップロード · 詳細を入力 · 生成ボタンを押す",
  tab_listing="📝 物件広告", tab_social="📱 SNSキット", tab_video="🎬 映像台本",
  tab_specs="⚙️ 技術仕様", tab_email="📧 メールキット", tab_seo="🔍 SEOパック",
  tab_tools="🛠️ エージェントツール", tab_history="📁 履歴",
  tools_head="AIエージェントツール",
  tools_sub="ワンクリックでプロ品質の成果物を即座に。",
  tool_run="生成 →", tool_clear="✕  クリア", tool_dl="⬇  ダウンロード",
  hist_empty="まだ保存された物件がありません。",
  hist_load="読込 →", hist_del="削除", hist_dl="ダウンロード",
  words="語", chars="文字",
  compliance_ok="✅ 公正住宅 — 問題は検出されませんでした",
  compliance_warn="⚠️ 確認が必要な用語: ",
  unsaved="● 未保存の変更", all_saved="✔ 全て保存済み",
  photo_label="写真", error_prefix="⚠️ エラー: ",
),
"中文 (简体)": dict(
  config_head="房产详情", write_in="输出语言", write_ph="如 中文、英文…",
  prop_type="房产类型", prop_ph="如 豪华别墅、3室2厅…",
  price="价格", price_ph="如 $850,000 或 $2,400/月",
  location="地点", loc_ph="如 上海市浦东新区",
  beds="卧室", baths="浴室", sqm="㎡", year="建造年份",
  parking="车位", amenities="主要特征", amenities_ph="泳池、健身房、海景…",
  strategy="营销策略",
  strategies=["⭐ 标准专业","💎 顶奢豪宅","📈 投资潜力",
               "🏡 家庭舒适","🎨 现代简约",
               "🏖️ 度假租赁","🏗️ 新开发","🏢 商业"],
  notes="备注", notes_ph="翻新厨房，靠近地铁…",
  agent_head="经纪人资料",
  agent_name="您的姓名", agent_name_ph="张伟",
  agent_co="中介 / 公司", agent_co_ph="豪华地产集团",
  agent_phone="电话", agent_phone_ph="+86 138 0000 0000",
  agent_email="邮箱", agent_email_ph="zhang@luxerealty.cn",
  upload="📸   将房产照片拖放到此处  ·  JPG · PNG · WEBP",
  gen_btn="✦  生成完整营销套餐",
  regen_btn="↺  重新生成",
  loading_steps=["🔍 AI正在分析照片…","✍️ 正在撰写优质房源描述…",
                 "📱 正在构建社交媒体套件…","🎬 正在编写视频脚本…",
                 "⚙️ 正在整理技术规格…","📧 正在起草邮件模板…",
                 "🔍 正在构建SEO套件…","✅ 正在完成您的套餐…"],
  save="💾  保存到历史", saved_ok="✅  已保存！",
  dl_all="⬇  下载全部 (.txt)", dl_tab="⬇  下载", copy="⎘  复制", copied="✅ 已复制！",
  empty_title="您的营销套餐将显示在这里",
  empty_sub="上传房产照片 · 填写详情 · 点击生成",
  tab_listing="📝 房源", tab_social="📱 社交媒体", tab_video="🎬 视频脚本",
  tab_specs="⚙️ 技术规格", tab_email="📧 邮件套件", tab_seo="🔍 SEO套件",
  tab_tools="🛠️ 经纪人工具", tab_history="📁 历史",
  tools_head="AI经纪人工具",
  tools_sub="一键获得专业成果。",
  tool_run="生成 →", tool_clear="✕  清除", tool_dl="⬇  下载",
  hist_empty="还没有保存的房源。",
  hist_load="加载 →", hist_del="删除", hist_dl="下载",
  words="词", chars="字符",
  compliance_ok="✅ 公平住房 — 未检测到问题",
  compliance_warn="⚠️ 请检查标记的词语: ",
  unsaved="● 未保存的更改", all_saved="✔ 全部已保存",
  photo_label="照片", error_prefix="⚠️ 错误: ",
),
"العربية": dict(
  config_head="تفاصيل العقار", write_in="لغة المحتوى", write_ph="مثال: العربية، الإنجليزية…",
  prop_type="نوع العقار", prop_ph="مثال: فيلا فاخرة، شقة 3 غرف…",
  price="السعر", price_ph="مثال: $850,000 أو $2,400/شهر",
  location="الموقع", loc_ph="مثال: دبي، وسط المدينة",
  beds="غرف", baths="حمامات", sqm="م²", year="سنة البناء",
  parking="موقف", amenities="المميزات", amenities_ph="مسبح، صالة رياضية، إطلالة بحرية…",
  strategy="استراتيجية التسويق",
  strategies=["⭐ احترافي قياسي","💎 فخامة فائقة","📈 استثماري",
               "🏡 راحة عائلية","🎨 عصري بسيط",
               "🏖️ إيجار عطلات","🏗️ مشروع جديد","🏢 تجاري"],
  notes="ملاحظات", notes_ph="مطبخ مجدد، قرب المترو…",
  agent_head="ملف الوكيل",
  agent_name="اسمك", agent_name_ph="محمد الأحمد",
  agent_co="الوكالة / الشركة", agent_co_ph="مجموعة لوكس العقارية",
  agent_phone="الهاتف", agent_phone_ph="+971 50 000 0000",
  agent_email="البريد الإلكتروني", agent_email_ph="m.ahmed@luxerealty.ae",
  upload="📸   اسحب صور العقار وأفلتها هنا  ·  JPG · PNG · WEBP",
  gen_btn="✦  إنشاء حزمة تسويقية متكاملة",
  regen_btn="↺  إعادة الإنشاء",
  loading_steps=["🔍 تحليل الصور بالذكاء الاصطناعي…","✍️ كتابة وصف عقاري متميز…",
                 "📱 بناء مجموعة التواصل الاجتماعي…","🎬 كتابة سيناريو الفيديو…",
                 "⚙️ تجميع المواصفات التقنية…","📧 صياغة قوالب البريد الإلكتروني…",
                 "🔍 بناء حزمة SEO…","✅ الانتهاء من حزمتك…"],
  save="💾  حفظ في السجل", saved_ok="✅  تم الحفظ!",
  dl_all="⬇  تحميل الكل (.txt)", dl_tab="⬇  تحميل", copy="⎘  نسخ", copied="✅ تم النسخ!",
  empty_title="ستظهر حزمتك التسويقية هنا",
  empty_sub="ارفع الصور · أدخل التفاصيل · اضغط إنشاء",
  tab_listing="📝 الإعلان", tab_social="📱 التواصل الاجتماعي", tab_video="🎬 سيناريو الفيديو",
  tab_specs="⚙️ المواصفات", tab_email="📧 مجموعة البريد", tab_seo="🔍 حزمة SEO",
  tab_tools="🛠️ أدوات الوكيل", tab_history="📁 السجل",
  tools_head="أدوات الوكيل بالذكاء الاصطناعي",
  tools_sub="نقرة واحدة — نتيجة احترافية فورية.",
  tool_run="إنشاء ←", tool_clear="✕  مسح", tool_dl="⬇  تحميل",
  hist_empty="لا توجد عقارات محفوظة بعد.",
  hist_load="تحميل ←", hist_del="حذف", hist_dl="تحميل",
  words="كلمة", chars="حرف",
  compliance_ok="✅ الإسكان العادل — لم يتم الكشف عن مشاكل",
  compliance_warn="⚠️ راجع المصطلحات المميزة: ",
  unsaved="● تغييرات غير محفوظة", all_saved="✔ تم الحفظ",
  photo_label="صورة", error_prefix="⚠️ خطأ: ",
),
}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
_defaults = dict(
    page="generate", output_raw="",
    s1="", s2="", s3="", s4="", s5="", s6="",
    tool_out="", tool_title="", dirty=False, history=[],
    write_in="English", prop_type="", price="", location="",
    beds="", baths="", sqm="", year_built="", parking="", amenities="",
    strategy_idx=0, notes="",
    agent_name="", agent_co="", agent_phone="", agent_email="",
)
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ───────────────────────────────────────────────────────────────────
FAIR_HOUSING_TERMS = [
    "adults only","no children","christian neighborhood","white neighborhood",
    "english speaking only","families only","perfect for couples","exclusive community",
]

def flag_fair_housing(text):
    tl = text.lower()
    return [t for t in FAIR_HOUSING_TERMS if t in tl]

def extract_section(raw, n):
    m = re.search(rf"##\s*SECTION_{n}.*?(?=##\s*SECTION_|\Z)", raw, re.DOTALL | re.IGNORECASE)
    if not m: return ""
    lines = m.group(0).strip().splitlines()
    return "\n".join(lines[1:]).strip()

def wc(text):
    return len(text.split()) if text else 0, len(text) if text else 0

def agent_ctx():
    parts = []
    if st.session_state.agent_name:  parts.append(f"Agent: {st.session_state.agent_name}")
    if st.session_state.agent_co:    parts.append(f"Agency: {st.session_state.agent_co}")
    if st.session_state.agent_phone: parts.append(f"Phone: {st.session_state.agent_phone}")
    if st.session_state.agent_email: parts.append(f"Email: {st.session_state.agent_email}")
    return " | ".join(parts) if parts else "Agent details not provided"

def prop_ctx():
    return f"""Property Type : {st.session_state.prop_type or 'Residential Property'}
Location      : {st.session_state.location or 'Undisclosed'}
Price         : {st.session_state.price or 'Price on Request'}
Bedrooms      : {st.session_state.beds or 'N/A'}
Bathrooms     : {st.session_state.baths or 'N/A'}
Size          : {st.session_state.sqm or 'N/A'} m²
Year Built    : {st.session_state.year_built or 'N/A'}
Parking       : {st.session_state.parking or 'N/A'}
Key Features  : {st.session_state.amenities or 'To be confirmed'}
Special Notes : {st.session_state.notes or 'None'}
{agent_ctx()}""".strip()

def save_history():
    entry = dict(
        id=str(datetime.now().timestamp()),
        date=datetime.now().strftime("%d %b %Y · %H:%M"),
        prop=st.session_state.prop_type or "Property",
        loc=st.session_state.location or "—",
        price=st.session_state.price or "—",
        **{f"s{i}": st.session_state[f"s{i}"] for i in range(1,7)}
    )
    st.session_state.history.insert(0, entry)
    if len(st.session_state.history) > 30:
        st.session_state.history = st.session_state.history[:30]

def build_main_prompt(lang, strategy):
    return f"""You are SarSa AI — the world's most advanced real estate marketing intelligence system.
You combine expertise of a luxury copywriter, social media director, cinematographer, SEO specialist, and real estate consultant.

PROPERTY INFORMATION:
{prop_ctx()}
MARKETING STRATEGY: {strategy}
OUTPUT LANGUAGE: {lang} — write ALL content in this language.

Study every uploaded photo carefully. Note architecture, finishes, light, views, room quality, outdoor spaces.

Produce a COMPLETE marketing package. Use EXACTLY these markers — do NOT skip any:

## SECTION_1 — PRIME LISTING COPY
Write a compelling, conversion-optimised property listing (450–650 words):
• Powerful ALL-CAPS headline (max 12 words)
• Emotional opening paragraph — paint a lifestyle picture
• Feature paragraphs (living spaces, kitchen/baths, outdoor/amenities)
• Location & neighbourhood highlights
• Investment/lifestyle value proposition
• Strong call-to-action with agent contact

## SECTION_2 — SOCIAL MEDIA KIT
Five platform-optimised posts:

📸 INSTAGRAM:
[Engaging caption, storytelling, emojis, 2200 chars max]
[25 targeted hashtags: property + location + lifestyle]

👥 FACEBOOK:
[Community-focused, conversational, 200–300 words, price + key features]

💼 LINKEDIN:
[Professional investment angle, market insight, 150–200 words]

🐦 X / TWITTER:
[Punchy, curiosity-driving, max 280 chars, 3–5 hashtags]

📱 WHATSAPP BROADCAST:
[Short, key details, price, contact — max 160 chars]

## SECTION_3 — CINEMATIC VIDEO SCRIPT
Full 60–90 second property video script:
• OPENING TITLE CARD text
• Scene-by-scene (6–8 scenes): camera direction + voiceover
• MUSIC SUGGESTION
• CLOSING TITLE CARD with agent contact
• YouTube description (150 words) + tags

## SECTION_4 — TECHNICAL SPECIFICATIONS
Professional data sheet:
• Property Specifications Table (all numeric data)
• Room-by-Room breakdown (from photos)
• Features & Amenities checklist (✓ / —)
• Building Information
• Energy & Utilities notes
• Legal Status placeholder
• Viewing & Contact Information

## SECTION_5 — EMAIL TEMPLATES
Three ready-to-send emails:

EMAIL 1 — NEW LISTING ANNOUNCEMENT
Subject: [compelling subject line]
[Full body 150–200 words + agent signature]

EMAIL 2 — BUYER FOLLOW-UP (post-viewing)
Subject: [follow-up subject line]
[Full body 120–150 words, address buyer concerns + agent signature]

EMAIL 3 — PRICE REDUCTION / SPECIAL OPPORTUNITY
Subject: [urgent subject line]
[Full body 100–130 words, urgency without pressure + agent signature]

## SECTION_6 — SEO & DIGITAL MARKETING PACK
• 20 SEO Keywords (short + long tail, ranked by priority)
• 3 Meta Descriptions (155 chars each, with CTA)
• Google Ads: 3 Headlines (max 30 chars) + 2 Descriptions (max 90 chars)
• 30 Instagram Hashtags by category: #Property(10) #Location(10) #Lifestyle(10)
• 10 YouTube Tags
• 5 Pinterest Board name suggestions
• Ideal posting schedule (best day + time per platform)

Write everything in {lang}. Be specific — reference actual photo details. Never use generic filler."""


# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=Playfair+Display:wght@700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="st-"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none !important; }
div[data-testid="stInputInstructions"] { display: none !important; }
span[data-testid="stIconMaterial"] { display: none !important; }

/* ── App background ── */
.stApp { background: #F5F3EE !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #18181B !important;
    border-right: 1px solid #27272A !important;
    min-width: 300px !important;
    max-width: 300px !important;
}
section[data-testid="stSidebar"] > div {
    padding: 1.25rem 1.1rem 2rem !important;
}

/* Sidebar text */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #A1A1AA !important;
}
section[data-testid="stSidebar"] label {
    color: #71717A !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* Sidebar inputs */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    background: #27272A !important;
    border: 1px solid #3F3F46 !important;
    border-radius: 7px !important;
    color: #E4E4E7 !important;
    font-size: 0.85rem !important;
    font-family: 'DM Sans', sans-serif !important;
}
section[data-testid="stSidebar"] input:focus,
section[data-testid="stSidebar"] textarea:focus {
    border-color: #C8A96A !important;
    box-shadow: 0 0 0 2px rgba(200,169,106,0.2) !important;
    outline: none !important;
}
section[data-testid="stSidebar"] input::placeholder,
section[data-testid="stSidebar"] textarea::placeholder {
    color: #52525B !important;
}

/* Sidebar select */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #27272A !important;
    border: 1px solid #3F3F46 !important;
    border-radius: 7px !important;
    color: #E4E4E7 !important;
    font-size: 0.85rem !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #71717A !important; }
[data-baseweb="popover"] { background: #27272A !important; border: 1px solid #3F3F46 !important; }
[role="listbox"] li { color: #E4E4E7 !important; font-size: 0.85rem !important; }
[role="listbox"] li:hover { background: #3F3F46 !important; }
[role="option"][aria-selected="true"] { background: #C8A96A !important; color: #18181B !important; }

/* Sidebar section headers */
.sb-head {
    color: #71717A !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 1rem 0 0.5rem !important;
    border-top: 1px solid #27272A !important;
    margin-top: 0.75rem !important;
}
.sb-head:first-child { border-top: none !important; padding-top: 0 !important; margin-top: 0 !important; }

/* ── Main container ── */
.block-container {
    background: transparent !important;
    padding: 1.75rem 2.25rem 4rem !important;
    max-width: 1240px !important;
}

/* ── Page header ── */
.pg-head { margin-bottom: 1.75rem; padding-bottom: 1.25rem; border-bottom: 1.5px solid #E2DDD5; }
.pg-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem; font-weight: 800;
    color: #18181B; line-height: 1.1; margin-bottom: 0.3rem;
}
.pg-title em { color: #C8A96A; font-style: normal; }
.pg-sub { font-size: 0.9rem; color: #71717A; font-weight: 400; }

/* ── Navigation pills ── */
.nav-wrap { display: flex; gap: 6px; margin-bottom: 1.5rem; }
.nav-pill {
    padding: 6px 16px; border-radius: 20px; font-size: 0.82rem; font-weight: 600;
    cursor: pointer; border: 1.5px solid #E2DDD5; background: #fff; color: #71717A;
    transition: all 0.15s; white-space: nowrap;
}
.nav-pill:hover { border-color: #C8A96A; color: #18181B; }
.nav-pill.active { background: #18181B; color: #fff; border-color: #18181B; }

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 2px dashed #D4CEC4 !important;
    border-radius: 14px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: #C8A96A !important; }
[data-testid="stFileUploader"] label {
    color: #71717A !important;
    font-size: 0.9rem !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    font-weight: 500 !important;
}
[data-testid="stFileUploader"] section { padding: 1.25rem !important; }

/* ── Generate button ── */
.gen-wrap button {
    background: #18181B !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.9rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.15) !important;
}
.gen-wrap button:hover {
    background: #C8A96A !important;
    box-shadow: 0 4px 16px rgba(200,169,106,0.4) !important;
    transform: translateY(-1px) !important;
    color: #18181B !important;
}

/* ── Regular buttons ── */
.stButton > button {
    background: #FFFFFF !important;
    color: #18181B !important;
    border: 1.5px solid #E2DDD5 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 0.42rem 0.9rem !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #F5F0E8 !important;
    border-color: #C8A96A !important;
}
.stButton > button:active { transform: scale(0.98) !important; }

/* ── Download buttons ── */
.stDownloadButton > button {
    background: #FFFFFF !important;
    color: #18181B !important;
    border: 1.5px solid #E2DDD5 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 0.42rem 0.9rem !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stDownloadButton > button:hover {
    background: #F5F0E8 !important;
    border-color: #C8A96A !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1.5px solid #E2DDD5 !important;
    gap: 2px !important;
    flex-wrap: wrap !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 7px !important;
    color: #71717A !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    padding: 6px 14px !important;
    border: none !important;
    white-space: nowrap !important;
    transition: all 0.15s !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #18181B !important; background: #F5F0E8 !important; }
.stTabs [aria-selected="true"] {
    background: #18181B !important;
    color: #FFFFFF !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1rem !important; }

/* ── Text areas ── */
.stTextArea textarea {
    background: #FFFFFF !important;
    border: 1.5px solid #E2DDD5 !important;
    border-radius: 10px !important;
    color: #18181B !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.7 !important;
    padding: 1rem !important;
    resize: vertical !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextArea textarea:focus {
    border-color: #C8A96A !important;
    box-shadow: 0 0 0 3px rgba(200,169,106,0.15) !important;
    outline: none !important;
}
.stTextArea label { display: none !important; }

/* ── Alerts / info ── */
.stAlert {
    border-radius: 8px !important;
    font-size: 0.87rem !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Progress bar ── */
.stProgress > div > div { background: #C8A96A !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #C8A96A !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F5F3EE; }
::-webkit-scrollbar-thumb { background: #C8A96A; border-radius: 3px; }

/* ── Custom components ── */
.wc-row {
    display: flex; gap: 8px; align-items: center; margin: 6px 0 10px;
}
.wc-chip {
    background: #F0EBE0; color: #71717A;
    font-size: 0.73rem; font-weight: 600; padding: 3px 10px;
    border-radius: 20px; font-family: 'DM Sans', sans-serif;
}
.ok-chip {
    display: inline-block;
    background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0;
    border-radius: 20px; padding: 3px 12px; font-size: 0.75rem; font-weight: 600;
    margin: 4px 0 8px;
}
.warn-chip {
    display: inline-block;
    background: #FFFBEB; color: #92400E; border: 1px solid #FCD34D;
    border-radius: 20px; padding: 3px 12px; font-size: 0.75rem; font-weight: 600;
    margin: 4px 0 8px;
}
.status-dot { display: inline-flex; align-items: center; gap: 5px; font-size: 0.78rem; font-weight: 600; }
.dot-dirty { color: #D97706; }
.dot-clean { color: #059669; }
.output-bar {
    display: flex; justify-content: space-between; align-items: flex-start;
    margin-bottom: 1.25rem; padding-bottom: 1.1rem;
    border-bottom: 1.5px solid #E2DDD5; gap: 1rem; flex-wrap: wrap;
}
.output-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.65rem; color: #18181B; font-weight: 800;
}
.tool-card {
    background: #FFFFFF; border: 1.5px solid #E2DDD5;
    border-radius: 12px; padding: 1.1rem 1.2rem; margin-bottom: 0.7rem;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.tool-card:hover { border-color: #C8A96A; box-shadow: 0 2px 10px rgba(200,169,106,0.18); }
.tn { font-weight: 700; color: #18181B; font-size: 0.92rem; margin-bottom: 3px; }
.td { color: #A1A1AA; font-size: 0.8rem; line-height: 1.4; }
.empty-box {
    background: #FFFFFF; border: 2px dashed #D4CEC4;
    border-radius: 18px; padding: 4rem 2rem; text-align: center; margin-top: 0.5rem;
}
.empty-icon { font-size: 3.5rem; margin-bottom: 1rem; }
.empty-t {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem; color: #18181B; margin-bottom: 0.5rem; font-weight: 700;
}
.empty-s { color: #A1A1AA; font-size: 0.9rem; }
.hist-card {
    background: #FFFFFF; border: 1.5px solid #E2DDD5;
    border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.7rem;
}
.ht { font-weight: 700; color: #18181B; font-size: 0.95rem; }
.hm { color: #A1A1AA; font-size: 0.78rem; margin-top: 2px; }

/* ── Logo ── */
.logo-block { padding: 0.25rem 0 1rem; }
.logo-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem; color: #FFFFFF; font-weight: 800; line-height: 1;
}
.logo-sub { font-size: 0.63rem; color: #52525B; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    logo = load_logo("SarSa_Logo_Transparent.png")
    if logo:
        st.image(logo, use_container_width=True)
    else:
        st.markdown("""
        <div class='logo-block'>
            <div class='logo-name'>SarSa AI</div>
            <div class='logo-sub'>Real Estate Intelligence</div>
        </div>""", unsafe_allow_html=True)

    ui_lang = st.selectbox("🌐 Language", list(LANGS.keys()), index=0, key="ui_lang_sel")
    T = LANGS[ui_lang]

    # ── Nav ──
    st.markdown("<div class='sb-head'>Navigation</div>", unsafe_allow_html=True)
    nav_items = [("generate","📝  Generate"), ("tools","🛠️  Tools"), ("history","📁  History")]
    for pid, plbl in nav_items:
        if st.button(plbl, key=f"nav_{pid}", use_container_width=True):
            st.session_state.page = pid
            st.rerun()

    # ── Property ──
    st.markdown(f"<div class='sb-head'>{T['config_head']}</div>", unsafe_allow_html=True)
    st.session_state.write_in     = st.text_input(T["write_in"],    value=st.session_state.write_in,     placeholder=T["write_ph"])
    st.session_state.prop_type    = st.text_input(T["prop_type"],   value=st.session_state.prop_type,    placeholder=T["prop_ph"])
    st.session_state.price        = st.text_input(T["price"],       value=st.session_state.price,        placeholder=T["price_ph"])
    st.session_state.location     = st.text_input(T["location"],    value=st.session_state.location,     placeholder=T["loc_ph"])
    c1, c2 = st.columns(2)
    with c1: st.session_state.beds       = st.text_input(T["beds"],  value=st.session_state.beds,       placeholder="3")
    with c2: st.session_state.baths      = st.text_input(T["baths"], value=st.session_state.baths,      placeholder="2")
    c3, c4 = st.columns(2)
    with c3: st.session_state.sqm        = st.text_input(T["sqm"],   value=st.session_state.sqm,        placeholder="120")
    with c4: st.session_state.year_built = st.text_input(T["year"],  value=st.session_state.year_built,  placeholder="2019")
    st.session_state.parking    = st.text_input(T["parking"],   value=st.session_state.parking,   placeholder="1")
    st.session_state.amenities  = st.text_input(T["amenities"], value=st.session_state.amenities, placeholder=T["amenities_ph"])
    strats = T["strategies"]
    sidx = st.session_state.strategy_idx if st.session_state.strategy_idx < len(strats) else 0
    chosen = st.selectbox(T["strategy"], strats, index=sidx)
    st.session_state.strategy_idx = strats.index(chosen)
    st.session_state.notes = st.text_area(T["notes"], value=st.session_state.notes, placeholder=T["notes_ph"], height=70)

    # ── Agent ──
    st.markdown(f"<div class='sb-head'>{T['agent_head']}</div>", unsafe_allow_html=True)
    st.session_state.agent_name  = st.text_input(T["agent_name"],  value=st.session_state.agent_name,  placeholder=T["agent_name_ph"])
    st.session_state.agent_co    = st.text_input(T["agent_co"],    value=st.session_state.agent_co,    placeholder=T["agent_co_ph"])
    st.session_state.agent_phone = st.text_input(T["agent_phone"], value=st.session_state.agent_phone, placeholder=T["agent_phone_ph"])
    st.session_state.agent_email = st.text_input(T["agent_email"], value=st.session_state.agent_email, placeholder=T["agent_email_ph"])


# ── PAGE: GENERATE ────────────────────────────────────────────────────────────
if st.session_state.page == "generate":

    st.markdown("""
    <div class='pg-head'>
        <div class='pg-title'>Property <em>Marketing Engine</em></div>
        <div class='pg-sub'>Upload photos · Fill in details · Get your complete professional marketing package in seconds</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        T["upload"], type=["jpg","jpeg","png","webp"],
        accept_multiple_files=True, label_visibility="visible"
    )

    if uploaded:
        images = [Image.open(f) for f in uploaded]
        n = min(len(images), 6)
        cols = st.columns(n)
        for i, img in enumerate(images):
            with cols[i % n]:
                st.image(img, use_container_width=True)
                st.markdown(
                    f"<p style='text-align:center;color:#A1A1AA;font-size:0.7rem;margin-top:2px;'>{T['photo_label']} {i+1}</p>",
                    unsafe_allow_html=True
                )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown("<div class='gen-wrap'>", unsafe_allow_html=True)
        do_gen = st.button(T["gen_btn"], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if do_gen:
            strategy = T["strategies"][st.session_state.strategy_idx]
            prompt   = build_main_prompt(st.session_state.write_in or "English", strategy)
            prog     = st.progress(0)
            status   = st.empty()
            steps    = T["loading_steps"]
            try:
                for i, step in enumerate(steps[:-1]):
                    status.info(step)
                    prog.progress(int((i + 1) / len(steps) * 88))
                status.info(steps[-1])
                response = model.generate_content([prompt] + images)
                raw = response.text
                st.session_state.output_raw = raw
                for n in range(1, 7):
                    st.session_state[f"s{n}"] = extract_section(raw, n)
                st.session_state.dirty = False
                prog.progress(100)
                status.success("✅  Package ready!")
            except Exception as e:
                status.error(f"{T['error_prefix']}{e}")
                prog.empty()

    else:
        if not st.session_state.output_raw:
            st.markdown(f"""
            <div class='empty-box'>
                <div class='empty-icon'>🏡</div>
                <div class='empty-t'>{T['empty_title']}</div>
                <div class='empty-s'>{T['empty_sub']}</div>
            </div>""", unsafe_allow_html=True)

    # ── OUTPUT ──
    if st.session_state.output_raw:
        st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

        # Action bar
        acol1, acol2, acol3, acol4 = st.columns([3, 1.1, 1.1, 1.2])
        with acol1:
            st.markdown("<div class='output-title'>Your Package</div>", unsafe_allow_html=True)
            if st.session_state.dirty:
                st.markdown(f"<span class='status-dot dot-dirty'>{T['unsaved']}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='status-dot dot-clean'>{T['all_saved']}</span>", unsafe_allow_html=True)
        with acol2:
            if st.button(T["save"], use_container_width=True):
                save_history()
                st.session_state.dirty = False
                st.success(T["saved_ok"])
        with acol3:
            if st.button(T["regen_btn"], use_container_width=True):
                for k in ["output_raw","s1","s2","s3","s4","s5","s6"]:
                    st.session_state[k] = ""
                st.rerun()
        with acol4:
            full = f"""SARSA AI — COMPLETE MARKETING PACKAGE
{'='*56}
Property : {st.session_state.prop_type}  |  {st.session_state.location}  |  {st.session_state.price}
Agent    : {agent_ctx()}
Date     : {datetime.now().strftime('%d %b %Y %H:%M')}
{'='*56}

📝 PRIME LISTING
{'─'*56}
{st.session_state.s1}

📱 SOCIAL MEDIA KIT
{'─'*56}
{st.session_state.s2}

🎬 VIDEO SCRIPT
{'─'*56}
{st.session_state.s3}

⚙️ TECHNICAL SPECIFICATIONS
{'─'*56}
{st.session_state.s4}

📧 EMAIL TEMPLATES
{'─'*56}
{st.session_state.s5}

🔍 SEO & DIGITAL MARKETING PACK
{'─'*56}
{st.session_state.s6}
"""
            st.download_button(T["dl_all"], data=full,
                               file_name=f"sarsa_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                               use_container_width=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # Tabs
        tabs = st.tabs([T["tab_listing"], T["tab_social"], T["tab_video"],
                        T["tab_specs"], T["tab_email"], T["tab_seo"]])
        tab_keys = ["s1","s2","s3","s4","s5","s6"]
        tab_files = ["listing","social_kit","video_script","tech_specs","email_kit","seo_pack"]

        for tab_obj, sk, fname, show_fhc in zip(
            tabs, tab_keys, tab_files,
            [True, False, False, False, False, False]
        ):
            with tab_obj:
                val = st.session_state.get(sk, "")
                new = st.text_area("", value=val, height=480, key=f"ta_{sk}")
                if new != val:
                    st.session_state[sk] = new
                    st.session_state.dirty = True

                w = len(new.split()) if new else 0
                c = len(new) if new else 0
                st.markdown(
                    f"<div class='wc-row'><span class='wc-chip'>📊 {w} {T['words']}</span>"
                    f"<span class='wc-chip'>✏️ {c} {T['chars']}</span></div>",
                    unsafe_allow_html=True
                )

                if show_fhc and new:
                    flags = flag_fair_housing(new)
                    if flags:
                        st.markdown(f"<div class='warn-chip'>{T['compliance_warn']}{', '.join(flags)}</div>",
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='ok-chip'>{T['compliance_ok']}</div>",
                                    unsafe_allow_html=True)

                bc1, bc2 = st.columns(2)
                with bc1:
                    st.download_button(
                        T["dl_tab"], data=new,
                        file_name=f"sarsa_{fname}_{datetime.now().strftime('%Y%m%d')}.txt",
                        key=f"dl_{sk}", use_container_width=True
                    )
                with bc2:
                    if new:
                        safe = new.replace("\\","\\\\").replace("`","\\`").replace("$","\\$")
                        copy_lbl = T["copy"].replace("'","&#39;")
                        copied_lbl = T["copied"].replace("'","&#39;")
                        st.markdown(f"""
                        <button onclick="navigator.clipboard.writeText(`{safe}`).then(()=>{{
                            this.textContent='{copied_lbl}';
                            setTimeout(()=>this.textContent='{copy_lbl}',2000)
                        }})" style="background:#fff;color:#18181B;border:1.5px solid #E2DDD5;
                            border-radius:8px;padding:0.42rem 0.9rem;font-size:0.82rem;
                            font-weight:600;cursor:pointer;width:100%;font-family:'DM Sans',sans-serif;
                            transition:all 0.15s;"
                            onmouseover="this.style.borderColor='#C8A96A';this.style.background='#F5F0E8'"
                            onmouseout="this.style.borderColor='#E2DDD5';this.style.background='#fff'"
                        >{copy_lbl}</button>""", unsafe_allow_html=True)


# ── PAGE: TOOLS ───────────────────────────────────────────────────────────────
elif st.session_state.page == "tools":

    st.markdown(f"""
    <div class='pg-head'>
        <div class='pg-title'>{T['tools_head']}</div>
        <div class='pg-sub'>{T['tools_sub']}</div>
    </div>""", unsafe_allow_html=True)

    TOOLS = [
      ("objection","💬 Objection Handler",
       "Master responses to the 10 toughest client objections",
       """You are the world's top real estate sales coach. Write a comprehensive OBJECTION HANDLING PLAYBOOK.
Agent: {name} | {co} | Market: {loc}
Cover these 10 objections using the FEEL-FELT-FOUND technique + confident closing line:
1. "Your commission is too high"  2. "I'll wait for the market to improve"
3. "I can sell it myself"  4. "Another agent offered a lower fee"
5. "The asking price is too high"  6. "I need to think about it"
7. "We're not in a rush"  8. "The property needs too much work"
9. "I'm already talking to another agent"  10. "I don't think AI can help sell my home"
For each: 3-line reframe + 1 confident closing line. Language: {lang}"""),

      ("cma","📊 CMA Report Template",
       "Professional comparative market analysis framework for seller presentations",
       """Write a professional COMPARATIVE MARKET ANALYSIS (CMA) REPORT.
Property: {prop} | Location: {loc} | Asking Price: {price}
Prepared by: {name} | {co}
Include: Executive Summary, Subject Property Overview, Market Conditions,
Comparable Sales Analysis (3 comp templates), Price Per m² Analysis,
Recommended Price Range + rationale, Marketing Strategy Recommendation,
Estimated Time to Sell, Agent Opinion of Value, Disclaimer.
Language: {lang}"""),

      ("cold_email","📧 Cold Outreach Emails",
       "Targeted emails to potential sellers, landlords and investors",
       """Write 3 cold outreach emails for real estate agent:
Agent: {name} | {co} | {phone} | {email}. Target area: {loc}. Property focus: {prop}.
EMAIL 1 — TO POTENTIAL SELLER: Subject + 150-word warm, value-first body.
EMAIL 2 — TO LANDLORD/INVESTOR: Subject + 150-word ROI-angle body.
EMAIL 3 — TO EXPIRED LISTING: Subject + 130-word empathy + fresh-approach body.
Each ends with professional signature. Language: {lang}"""),

      ("negotiation","🤝 Negotiation Scripts",
       "Word-for-word scripts to win price, terms and condition negotiations",
       """Write a COMPLETE NEGOTIATION SCRIPT for a seller's agent.
Property: {prop} at {loc} | Price: {price} | Agent: {name} | {co}
Script these 6 scenarios: 1. Responding to a lowball offer
2. Multiple offer situation  3. Buyer requests price reduction after inspection
4. Buyer requests seller pay closing costs  5. Buyer wants to extend closing date
6. Deal falling apart — last-chance script.
For each: Opening line + 3 talking points + Closing line + What NOT to say.
Language: {lang}"""),

      ("bio","👤 Agent Biography",
       "Three formats of your professional biography — micro, standard, and full",
       """Write 3 professional agent biographies.
Agent: {name} | Company: {co} | Market: {loc} | Contact: {phone} | {email}
VERSION 1 — MICRO (55 words): For Instagram, business card, email signature.
VERSION 2 — STANDARD (160 words): For website About page, property portals.
VERSION 3 — FULL BIOGRAPHY (320 words): For press releases, media kits, awards.
Include: expertise, market knowledge, client philosophy, personal touch.
First person V1, third person V2 & V3. Language: {lang}"""),

      ("openhouse","🏠 Open House Guide",
       "A complete event guide from arrival through to follow-up",
       """Write a complete OPEN HOUSE EVENT GUIDE.
Property: {prop} | Location: {loc} | Price: {price} | Beds: {beds} | Baths: {baths} | {sqm} m²
Agent: {name} | {co} | {phone}
Include: Pre-event checklist (10 tasks), Welcome script (45 sec), Room-by-room tour talking points (8 rooms),
Top 5 selling points to emphasize, 3 on-the-spot price objection responses,
Sign-in conversation opener, Closing conversation (gauge interest, ask for offer),
Same-day follow-up SMS (max 160 chars), Next-day follow-up email (subject + 120 words).
Language: {lang}"""),

      ("followup","📞 Follow-Up Sequence",
       "A 2-week multi-touchpoint follow-up system after every viewing",
       """Create a 2-WEEK POST-VIEWING FOLLOW-UP SEQUENCE.
Property: {prop} at {loc} | Price: {price} | Agent: {name} | {co} | {phone} | {email}
Day 0: SMS (max 160 chars) + WhatsApp message.
Day 1: Email — warm recap + highlights (150 words).
Day 3: Email — neighbourhood + lifestyle value (130 words).
Day 5: SMS — gentle check-in (max 120 chars).
Day 7: Email — market update / competing offers angle (120 words).
Day 10: Phone call script outline (2 minutes, 5 bullet points).
Day 14: Final email — last opportunity (100 words).
Tone: Helpful, never pushy. Language: {lang}"""),

      ("investment","💰 Investment Analysis",
       "Full ROI and rental yield analysis memo for investor-focused listings",
       """Write a professional INVESTMENT ANALYSIS MEMO.
Property: {prop} | Location: {loc} | Price: {price} | Size: {sqm} m² | Beds: {beds}
Prepared by: {name} | {co}
Include: Investment Summary, Purchase Cost Breakdown, Rental Income Potential (Airbnb vs long-term),
Gross Yield, Operating Expenses, NOI, Cap Rate, Cash-on-Cash Return (25% deposit),
5-Year Appreciation Projection (3 scenarios), Break-Even Timeline, Exit Strategy Options (3), Risk Factors (4).
Language: {lang}"""),

      ("checklist","✅ Transaction Checklists",
       "Complete step-by-step checklists for buyer and seller transactions",
       """Create COMPLETE REAL ESTATE TRANSACTION CHECKLISTS. Agent: {name} | {co}
PART 1 — SELLER CHECKLIST (35+ tasks, 6 phases: Pre-Listing, Active Listing, Offer & Negotiation, Under Contract, Pre-Closing, Closing Day).
PART 2 — BUYER CHECKLIST (32+ tasks, 6 phases: Pre-Search, Property Search, Making an Offer, Under Contract, Financing & Inspection, Closing & Moving In).
Each task: ☐ Task description | Responsible party | Notes. Language: {lang}"""),

      ("neighborhood","🗺️ Neighborhood Guide",
       "Detailed buyer's area guide that helps close deals faster",
       """Write a NEIGHBORHOOD GUIDE FOR BUYERS.
Area: {loc} | Property: {prop} | Price: {price} | Prepared by: {name} | {co}
Sections: Area Character & Vibe (2 paragraphs), Transport & Commuting, Schools & Education,
Dining/Shopping/Entertainment, Parks & Outdoor, Healthcare, Safety & Community,
Property Market Overview, What Locals Love (3 reasons), Future Development & Growth,
Agent's Recommendation. Add professional disclaimer. Language: {lang}"""),

      ("press","📰 Press Release",
       "Newsworthy press releases for high-value listings or agency news",
       """Write 2 professional press releases.
Agency: {co} | Agent: {name} | {phone} | {email} | Property: {prop} at {loc} | Price: {price} | Date: {date}
PRESS RELEASE 1 — PROPERTY LAUNCH: FOR IMMEDIATE RELEASE, punchy headline, dateline, opening para (who/what/where/when/why), 2 property paragraphs, agent quote, about agency boilerplate, media contact.
PRESS RELEASE 2 — MARKET UPDATE: Market conditions focus, expert commentary, agency positioning, CTA.
Both 350-400 words, AP style. Language: {lang}"""),

      ("mortgage","🏦 Buyer's Finance Guide",
       "A complete guide to mortgages, costs and financing for buyers",
       """Write a BUYER'S FINANCE & MORTGAGE GUIDE for the {loc} market. Prepared by: {name} | {co}
Include: Why Finance Planning Matters, How Much Can I Borrow (income multiples, DTI),
Deposit Requirements (% ranges, LTV), Types of Mortgages (pros/cons table),
Hidden Costs of Buying (% estimates), Step-by-Step Application Process (8 steps),
Common Reasons Applications Fail, First-Time Buyer Tips (5 tips),
Investor Financing (buy-to-let specifics), Glossary of 15 Key Finance Terms, Disclaimer.
Accessible, jargon-free. Language: {lang}"""),
    ]

    # Show tool output if available
    if st.session_state.tool_out:
        st.markdown(
            f"<div style='background:#FFFFFF;border:1.5px solid #E2DDD5;border-radius:12px;"
            f"padding:0.75rem 1rem;margin-bottom:1rem;font-weight:700;color:#18181B;'>"
            f"📄 {st.session_state.tool_title}</div>",
            unsafe_allow_html=True
        )
        edited = st.text_area("", value=st.session_state.tool_out, height=520, key="tool_ta")
        w = len(edited.split()) if edited else 0
        c = len(edited) if edited else 0
        st.markdown(
            f"<div class='wc-row'><span class='wc-chip'>📊 {w} {T['words']}</span>"
            f"<span class='wc-chip'>✏️ {c} {T['chars']}</span></div>",
            unsafe_allow_html=True
        )
        tc1, tc2 = st.columns(2)
        with tc1:
            st.download_button(
                T["tool_dl"], data=edited,
                file_name=f"sarsa_tool_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                use_container_width=True
            )
        with tc2:
            if st.button(T["tool_clear"], use_container_width=True):
                st.session_state.tool_out = ""
                st.session_state.tool_title = ""
                st.rerun()
        st.markdown("<hr style='margin:1.25rem 0;border-top:1.5px solid #E2DDD5;border:none;'>", unsafe_allow_html=True)

    # Tool grid
    for i in range(0, len(TOOLS), 2):
        row = st.columns(2)
        for j, col in enumerate(row):
            idx = i + j
            if idx >= len(TOOLS):
                break
            tid, tname, tdesc, tprompt = TOOLS[idx]
            with col:
                st.markdown(
                    f"<div class='tool-card'><div class='tn'>{tname}</div>"
                    f"<div class='td'>{tdesc}</div></div>",
                    unsafe_allow_html=True
                )
                if st.button(T["tool_run"], key=f"tool_{tid}", use_container_width=True):
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
                            phone=st.session_state.agent_phone or "your phone number",
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
                            st.error(f"{T['error_prefix']}{e}")


# ── PAGE: HISTORY ─────────────────────────────────────────────────────────────
elif st.session_state.page == "history":

    count = len(st.session_state.history)
    st.markdown(f"""
    <div class='pg-head'>
        <div class='pg-title'>{T['tab_history']}</div>
        <div class='pg-sub'>{count} saved listing{"s" if count != 1 else ""}</div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown(f"""
        <div class='empty-box'>
            <div class='empty-icon'>📁</div>
            <div class='empty-t'>{T['tab_history']}</div>
            <div class='empty-s'>{T['hist_empty']}</div>
        </div>""", unsafe_allow_html=True)
    else:
        for i, entry in enumerate(st.session_state.history):
            label = f"🏢  {entry['prop']}  ·  {entry['loc']}  ·  {entry['price']}  ·  {entry['date']}"
            with st.expander(label):
                htabs = st.tabs([T["tab_listing"], T["tab_social"], T["tab_video"], T["tab_specs"]])
                for ni, ht in enumerate(htabs):
                    with ht:
                        st.text_area("", value=entry.get(f"s{ni+1}",""), height=260, key=f"hs{ni+1}_{i}")

                hc1, hc2, hc3 = st.columns(3)
                with hc1:
                    if st.button(T["hist_load"], key=f"hl_{i}", use_container_width=True):
                        for n in range(1, 7):
                            st.session_state[f"s{n}"] = entry.get(f"s{n}", "")
                        st.session_state.output_raw = entry.get("s1", "")
                        st.session_state.page = "generate"
                        st.rerun()
                with hc2:
                    exp = "\n\n".join(entry.get(f"s{n}","") for n in range(1,7))
                    st.download_button(
                        T["hist_dl"], data=exp,
                        file_name=f"sarsa_hist_{entry['id'][:8]}.txt",
                        key=f"hd_{i}", use_container_width=True
                    )
                with hc3:
                    if st.button(T["hist_del"], key=f"hdel_{i}", use_container_width=True):
                        st.session_state.history.pop(i)
                        st.rerun()
