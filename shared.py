"""
SarSa AI — Shared design system, language strings, helpers.
All pages import from here.
"""
import streamlit as st
from PIL import Image
import os, re
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────────
GOLD    = "#C9A84C"
DARK    = "#0F0F10"
SURFACE = "#18181B"
CARD    = "#1E1E22"
BORDER  = "#2A2A30"
TEXT    = "#F4F4F5"
MUTED   = "#71717A"
SUCCESS = "#22C55E"
WARN    = "#F59E0B"
ERROR   = "#EF4444"
BG      = "#0A0A0B"

# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE STRINGS
# ─────────────────────────────────────────────────────────────────────────────
LANGS = {
"English": dict(
  nav_generate="Generate", nav_tools="Agent Tools", nav_history="History",
  config_head="Property", agent_head="Agent Profile",
  write_in="Output Language", write_ph="English, French, Arabic…",
  prop_type="Property Type", prop_ph="Luxury Villa, 3-Bed Apt…",
  price="Price", price_ph="$850,000 or €2,400/mo",
  location="Location", loc_ph="Miami Beach, FL",
  beds="Beds", baths="Baths", sqm="m²", year="Year",
  parking="Parking", amenities="Features", amen_ph="Pool, gym, sea view…",
  strategy="Strategy",
  strategies=["⭐ Standard Pro","💎 Ultra-Luxury","📈 Investment",
               "🏡 Family Comfort","🎨 Modern Minimal",
               "🏖️ Vacation Rental","🏗️ New Development","🏢 Commercial"],
  notes="Notes", notes_ph="Renovated kitchen, metro nearby…",
  agent_name="Your Name", agent_ph="Sarah Johnson",
  agent_co="Agency", agent_co_ph="Luxe Realty Group",
  agent_phone="Phone", agent_phone_ph="+1 305 000 0000",
  agent_email="Email", agent_email_ph="sarah@luxerealty.com",
  upload_label="Drop property photos here — JPG, PNG, WEBP",
  gen_btn="GENERATE COMPLETE MARKETING PACKAGE",
  regen_btn="Regenerate",
  save_btn="Save to History",
  saved_ok="Saved!",
  dl_all="Download All",
  dl_section="Download",
  copy_btn="Copy",
  copied_btn="Copied!",
  tab1="Listing", tab2="Social", tab3="Video", tab4="Specs", tab5="Emails", tab6="SEO",
  tools_title="Agent Toolbox",
  tools_sub="One click. Professional output. Instantly.",
  run_tool="Generate →",
  clear_tool="Clear",
  dl_tool="Download",
  hist_title="Saved Listings",
  hist_empty="No saved listings yet.",
  load_btn="Load",
  del_btn="Delete",
  words="words", chars="chars",
  comp_ok="✓ Fair housing — no issues",
  comp_warn="⚠ Review: ",
  unsaved="Unsaved changes",
  all_saved="Saved",
  photo="Photo",
  err="Error: ",
  loading=["Analyzing photos…","Writing listing copy…","Building social kit…",
           "Scripting video…","Compiling specs…","Drafting emails…","Building SEO pack…","Finalizing…"],
  empty_title="Your marketing package will appear here",
  empty_sub="Upload photos · Fill in details · Hit Generate",
  welcome_title="The Professional Real Estate\nMarketing Platform",
  welcome_sub="Transform property photos into a complete professional marketing suite — listing copy, social media kit, video scripts, tech specs, emails, and SEO pack — in seconds.",
  welcome_cta="Start Generating →",
),
"Türkçe": dict(
  nav_generate="Oluştur", nav_tools="Araçlar", nav_history="Geçmiş",
  config_head="Mülk", agent_head="Temsilci Profili",
  write_in="Çıktı Dili", write_ph="Türkçe, İngilizce…",
  prop_type="Mülk Tipi", prop_ph="Lüks Villa, 3+1 Daire…",
  price="Fiyat", price_ph="5.000.000₺ veya $2.500/ay",
  location="Konum", loc_ph="Beşiktaş, İstanbul",
  beds="Yatak", baths="Banyo", sqm="m²", year="Yıl",
  parking="Otopark", amenities="Özellikler", amen_ph="Havuz, spor salonu…",
  strategy="Strateji",
  strategies=["⭐ Standart Pro","💎 Ultra-Lüks","📈 Yatırım",
               "🏡 Aile Konforu","🎨 Modern Minimal",
               "🏖️ Tatil Kiralaması","🏗️ Yeni Proje","🏢 Ticari"],
  notes="Notlar", notes_ph="Tadilatlı mutfak, metroya yakın…",
  agent_name="Adınız", agent_ph="Ayşe Kaya",
  agent_co="Acente", agent_co_ph="Lüks Emlak A.Ş.",
  agent_phone="Telefon", agent_phone_ph="+90 532 000 0000",
  agent_email="E-posta", agent_email_ph="ayse@luksemalik.com",
  upload_label="Fotoğrafları buraya bırakın — JPG, PNG, WEBP",
  gen_btn="TAM PAZARLAMA PAKETİ OLUŞTUR",
  regen_btn="Yeniden Oluştur",
  save_btn="Geçmişe Kaydet",
  saved_ok="Kaydedildi!",
  dl_all="Tümünü İndir",
  dl_section="İndir",
  copy_btn="Kopyala",
  copied_btn="Kopyalandı!",
  tab1="İlan", tab2="Sosyal", tab3="Video", tab4="Teknik", tab5="E-posta", tab6="SEO",
  tools_title="Ajan Araç Kutusu",
  tools_sub="Tek tıkla. Profesyonel sonuç. Anında.",
  run_tool="Oluştur →",
  clear_tool="Temizle",
  dl_tool="İndir",
  hist_title="Kayıtlı İlanlar",
  hist_empty="Henüz kayıtlı ilan yok.",
  load_btn="Yükle",
  del_btn="Sil",
  words="kelime", chars="karakter",
  comp_ok="✓ Adil konut — sorun yok",
  comp_warn="⚠ İnceleyin: ",
  unsaved="Kaydedilmemiş",
  all_saved="Kaydedildi",
  photo="Fotoğraf",
  err="Hata: ",
  loading=["Fotoğraflar analiz ediliyor…","İlan metni yazılıyor…","Sosyal medya kiti oluşturuluyor…",
           "Video senaryosu yazılıyor…","Teknik özellikler derleniyor…","E-postalar hazırlanıyor…","SEO paketi oluşturuluyor…","Tamamlanıyor…"],
  empty_title="Pazarlama paketiniz burada görünecek",
  empty_sub="Fotoğraf yükleyin · Bilgileri doldurun · Oluştur'a basın",
  welcome_title="Profesyonel Gayrimenkul\nPazarlama Platformu",
  welcome_sub="Mülk fotoğraflarını saniyeler içinde eksiksiz bir profesyonel pazarlama paketine dönüştürün.",
  welcome_cta="Oluşturmaya Başla →",
),
"Español": dict(
  nav_generate="Generar", nav_tools="Herramientas", nav_history="Historial",
  config_head="Propiedad", agent_head="Perfil Agente",
  write_in="Idioma Salida", write_ph="Español, Inglés…",
  prop_type="Tipo Propiedad", prop_ph="Villa Lujo, Piso 3 hab…",
  price="Precio", price_ph="$850,000 o €2,400/mes",
  location="Ubicación", loc_ph="Centro Madrid",
  beds="Hab.", baths="Baños", sqm="m²", year="Año",
  parking="Garaje", amenities="Características", amen_ph="Piscina, gym, vistas…",
  strategy="Estrategia",
  strategies=["⭐ Estándar Pro","💎 Ultra-Lujo","📈 Inversión",
               "🏡 Confort Familiar","🎨 Minimalista",
               "🏖️ Vacacional","🏗️ Nueva Construcción","🏢 Comercial"],
  notes="Notas", notes_ph="Cocina reformada, metro cerca…",
  agent_name="Nombre", agent_ph="Carlos García",
  agent_co="Agencia", agent_co_ph="Luxe Realty Group",
  agent_phone="Teléfono", agent_phone_ph="+34 600 000 000",
  agent_email="Email", agent_email_ph="carlos@luxerealty.es",
  upload_label="Arrastra fotos aquí — JPG, PNG, WEBP",
  gen_btn="GENERAR PAQUETE COMPLETO",
  regen_btn="Regenerar",
  save_btn="Guardar",
  saved_ok="¡Guardado!",
  dl_all="Descargar Todo",
  dl_section="Descargar",
  copy_btn="Copiar",
  copied_btn="¡Copiado!",
  tab1="Anuncio", tab2="Social", tab3="Vídeo", tab4="Specs", tab5="Emails", tab6="SEO",
  tools_title="Caja de Herramientas",
  tools_sub="Un clic. Resultado profesional. Instantáneo.",
  run_tool="Generar →",
  clear_tool="Limpiar",
  dl_tool="Descargar",
  hist_title="Listados Guardados",
  hist_empty="Aún no hay listados guardados.",
  load_btn="Cargar",
  del_btn="Eliminar",
  words="palabras", chars="caracteres",
  comp_ok="✓ Vivienda justa — sin problemas",
  comp_warn="⚠ Revisar: ",
  unsaved="Sin guardar",
  all_saved="Guardado",
  photo="Foto",
  err="Error: ",
  loading=["Analizando fotos…","Redactando anuncio…","Creando kit social…",
           "Escribiendo guión…","Compilando specs…","Redactando emails…","Pack SEO…","Finalizando…"],
  empty_title="Tu paquete aparecerá aquí",
  empty_sub="Sube fotos · Rellena detalles · Pulsa Generar",
  welcome_title="La Plataforma Profesional de\nMarketing Inmobiliario",
  welcome_sub="Convierte fotos en un paquete completo de marketing profesional en segundos.",
  welcome_cta="Empezar a Generar →",
),
"Deutsch": dict(
  nav_generate="Erstellen", nav_tools="Makler-Tools", nav_history="Verlauf",
  config_head="Objekt", agent_head="Makler-Profil",
  write_in="Ausgabesprache", write_ph="Deutsch, Englisch…",
  prop_type="Objekttyp", prop_ph="Luxusvilla, 3-Zi-Wohnung…",
  price="Preis", price_ph="850.000€ oder 2.400€/Mo",
  location="Standort", loc_ph="München Innenstadt",
  beds="Zimmer", baths="Bad", sqm="m²", year="Jahr",
  parking="Stellplatz", amenities="Merkmale", amen_ph="Pool, Gym, Meerblick…",
  strategy="Strategie",
  strategies=["⭐ Standard-Profi","💎 Ultra-Luxus","📈 Investment",
               "🏡 Familie","🎨 Modern-Minimal",
               "🏖️ Ferienmiete","🏗️ Neubau","🏢 Gewerbe"],
  notes="Notizen", notes_ph="Renovierte Küche, U-Bahn-Nähe…",
  agent_name="Ihr Name", agent_ph="Thomas Müller",
  agent_co="Agentur", agent_co_ph="Luxe Realty GmbH",
  agent_phone="Telefon", agent_phone_ph="+49 89 000 0000",
  agent_email="E-Mail", agent_email_ph="thomas@luxerealty.de",
  upload_label="Objektfotos hier ablegen — JPG, PNG, WEBP",
  gen_btn="KOMPLETTES MARKETING-PAKET ERSTELLEN",
  regen_btn="Neu erstellen",
  save_btn="Im Verlauf speichern",
  saved_ok="Gespeichert!",
  dl_all="Alles herunterladen",
  dl_section="Herunterladen",
  copy_btn="Kopieren",
  copied_btn="Kopiert!",
  tab1="Exposé", tab2="Social", tab3="Video", tab4="Technik", tab5="E-Mails", tab6="SEO",
  tools_title="Makler-Werkzeugkasten",
  tools_sub="Ein Klick. Professionelles Ergebnis. Sofort.",
  run_tool="Erstellen →",
  clear_tool="Löschen",
  dl_tool="Herunterladen",
  hist_title="Gespeicherte Objekte",
  hist_empty="Noch keine gespeicherten Objekte.",
  load_btn="Laden",
  del_btn="Löschen",
  words="Wörter", chars="Zeichen",
  comp_ok="✓ Fairness — keine Probleme",
  comp_warn="⚠ Prüfen: ",
  unsaved="Nicht gespeichert",
  all_saved="Gespeichert",
  photo="Foto",
  err="Fehler: ",
  loading=["Fotos analysieren…","Exposé schreiben…","Social-Kit aufbauen…",
           "Skript verfassen…","Daten kompilieren…","E-Mails erstellen…","SEO-Paket…","Abschluss…"],
  empty_title="Ihr Paket erscheint hier",
  empty_sub="Fotos hochladen · Details ausfüllen · Erstellen",
  welcome_title="Die Professionelle Immobilien-\nMarketing-Plattform",
  welcome_sub="Verwandeln Sie Fotos in Sekunden in ein komplettes professionelles Marketing-Paket.",
  welcome_cta="Jetzt starten →",
),
"Français": dict(
  nav_generate="Générer", nav_tools="Outils Agent", nav_history="Historique",
  config_head="Bien", agent_head="Profil Agent",
  write_in="Langue Sortie", write_ph="Français, Anglais…",
  prop_type="Type de Bien", prop_ph="Villa de Luxe, Apt T3…",
  price="Prix", price_ph="850 000€ ou 2 400€/mois",
  location="Localisation", loc_ph="Paris 16ème",
  beds="Ch.", baths="SDB", sqm="m²", year="Année",
  parking="Parking", amenities="Équipements", amen_ph="Piscine, sport, vue mer…",
  strategy="Stratégie",
  strategies=["⭐ Standard Pro","💎 Ultra-Luxe","📈 Investissement",
               "🏡 Familial","🎨 Minimaliste",
               "🏖️ Location Vacances","🏗️ Neuf","🏢 Commercial"],
  notes="Notes", notes_ph="Cuisine rénovée, métro proche…",
  agent_name="Votre Nom", agent_ph="Marie Dupont",
  agent_co="Agence", agent_co_ph="Luxe Realty France",
  agent_phone="Téléphone", agent_phone_ph="+33 6 00 00 00 00",
  agent_email="Email", agent_email_ph="marie@luxerealty.fr",
  upload_label="Déposez les photos ici — JPG, PNG, WEBP",
  gen_btn="GÉNÉRER LE PACK COMPLET",
  regen_btn="Régénérer",
  save_btn="Sauvegarder",
  saved_ok="Sauvegardé!",
  dl_all="Tout télécharger",
  dl_section="Télécharger",
  copy_btn="Copier",
  copied_btn="Copié!",
  tab1="Annonce", tab2="Social", tab3="Vidéo", tab4="Specs", tab5="Emails", tab6="SEO",
  tools_title="Boîte à Outils Agent",
  tools_sub="Un clic. Résultat professionnel. Instantané.",
  run_tool="Générer →",
  clear_tool="Effacer",
  dl_tool="Télécharger",
  hist_title="Biens Sauvegardés",
  hist_empty="Aucun bien sauvegardé.",
  load_btn="Charger",
  del_btn="Supprimer",
  words="mots", chars="caractères",
  comp_ok="✓ Logement équitable — OK",
  comp_warn="⚠ Vérifier: ",
  unsaved="Non enregistré",
  all_saved="Enregistré",
  photo="Photo",
  err="Erreur: ",
  loading=["Analyse des photos…","Rédaction annonce…","Kit réseaux sociaux…",
           "Script vidéo…","Compilation specs…","Emails…","Pack SEO…","Finalisation…"],
  empty_title="Votre pack apparaîtra ici",
  empty_sub="Chargez des photos · Remplissez les détails · Générez",
  welcome_title="La Plateforme Professionnelle\nde Marketing Immobilier",
  welcome_sub="Transformez des photos en pack marketing complet en quelques secondes.",
  welcome_cta="Commencer →",
),
"Português": dict(
  nav_generate="Gerar", nav_tools="Ferramentas", nav_history="Histórico",
  config_head="Imóvel", agent_head="Perfil Agente",
  write_in="Idioma Saída", write_ph="Português, Inglês…",
  prop_type="Tipo Imóvel", prop_ph="Villa Luxo, Apt T3…",
  price="Preço", price_ph="850.000€ ou 2.400€/mês",
  location="Localização", loc_ph="Lisboa, Chiado",
  beds="Quartos", baths="WC", sqm="m²", year="Ano",
  parking="Garagem", amenities="Características", amen_ph="Piscina, ginásio, vista mar…",
  strategy="Estratégia",
  strategies=["⭐ Profissional","💎 Ultra-Luxo","📈 Investimento",
               "🏡 Familiar","🎨 Minimalista",
               "🏖️ Férias","🏗️ Nova Construção","🏢 Comercial"],
  notes="Notas", notes_ph="Cozinha renovada, metro próximo…",
  agent_name="O Seu Nome", agent_ph="Ana Silva",
  agent_co="Agência", agent_co_ph="Luxe Realty Portugal",
  agent_phone="Telefone", agent_phone_ph="+351 91 000 0000",
  agent_email="Email", agent_email_ph="ana@luxerealty.pt",
  upload_label="Arraste fotos aqui — JPG, PNG, WEBP",
  gen_btn="GERAR PACOTE COMPLETO",
  regen_btn="Regenerar",
  save_btn="Guardar",
  saved_ok="Guardado!",
  dl_all="Descarregar Tudo",
  dl_section="Descarregar",
  copy_btn="Copiar",
  copied_btn="Copiado!",
  tab1="Anúncio", tab2="Social", tab3="Vídeo", tab4="Specs", tab5="Emails", tab6="SEO",
  tools_title="Caixa de Ferramentas",
  tools_sub="Um clique. Resultado profissional. Instantâneo.",
  run_tool="Gerar →",
  clear_tool="Limpar",
  dl_tool="Descarregar",
  hist_title="Imóveis Guardados",
  hist_empty="Ainda sem imóveis guardados.",
  load_btn="Carregar",
  del_btn="Apagar",
  words="palavras", chars="caracteres",
  comp_ok="✓ Habitação justa — sem problemas",
  comp_warn="⚠ Rever: ",
  unsaved="Não guardado",
  all_saved="Guardado",
  photo="Foto",
  err="Erro: ",
  loading=["Analisando fotos…","Redigindo anúncio…","Kit social…",
           "Guião vídeo…","Compilando specs…","Emails…","Pack SEO…","A finalizar…"],
  empty_title="O seu pacote aparecerá aqui",
  empty_sub="Carregue fotos · Preencha detalhes · Clique em Gerar",
  welcome_title="A Plataforma Profissional\nde Marketing Imobiliário",
  welcome_sub="Transforme fotos num pacote completo de marketing profissional em segundos.",
  welcome_cta="Começar →",
),
"日本語": dict(
  nav_generate="生成", nav_tools="エージェントツール", nav_history="履歴",
  config_head="物件", agent_head="エージェント",
  write_in="出力言語", write_ph="日本語、英語…",
  prop_type="物件種別", prop_ph="高級別荘、3LDK…",
  price="価格", price_ph="5,000万円 月20万円",
  location="所在地", loc_ph="東京都港区",
  beds="寝室", baths="浴室", sqm="㎡", year="築年",
  parking="駐車場", amenities="特徴", amen_ph="プール、ジム、海景…",
  strategy="戦略",
  strategies=["⭐ スタンダード","💎 高級","📈 投資","🏡 ファミリー",
               "🎨 ミニマル","🏖️ 別荘","🏗️ 新築","🏢 商業"],
  notes="備考", notes_ph="リノベ済み、駅近…",
  agent_name="お名前", agent_ph="田中太郎",
  agent_co="会社", agent_co_ph="ラックスリアルティ",
  agent_phone="電話", agent_phone_ph="+81 3 0000 0000",
  agent_email="メール", agent_email_ph="tanaka@luxerealty.jp",
  upload_label="写真をここにドロップ — JPG、PNG、WEBP",
  gen_btn="完全なマーケティングパッケージを生成",
  regen_btn="再生成",
  save_btn="履歴に保存",
  saved_ok="保存しました！",
  dl_all="全てダウンロード",
  dl_section="ダウンロード",
  copy_btn="コピー",
  copied_btn="コピー完了！",
  tab1="広告", tab2="SNS", tab3="動画", tab4="仕様", tab5="メール", tab6="SEO",
  tools_title="エージェントツールボックス",
  tools_sub="ワンクリックでプロ品質の成果物を。",
  run_tool="生成 →",
  clear_tool="クリア",
  dl_tool="ダウンロード",
  hist_title="保存済み物件",
  hist_empty="まだ保存された物件がありません。",
  load_btn="読込",
  del_btn="削除",
  words="語", chars="文字",
  comp_ok="✓ 公正住宅 — 問題なし",
  comp_warn="⚠ 要確認: ",
  unsaved="未保存",
  all_saved="保存済み",
  photo="写真",
  err="エラー: ",
  loading=["写真を分析中…","広告を作成中…","SNSキット構築中…",
           "動画台本を執筆中…","仕様を整理中…","メール作成中…","SEOパック構築中…","仕上げ中…"],
  empty_title="パッケージはここに表示されます",
  empty_sub="写真をアップロード · 詳細を入力 · 生成",
  welcome_title="プロフェッショナル不動産\nマーケティングプラットフォーム",
  welcome_sub="物件写真を秒単位で完全なプロのマーケティングパッケージに変換。",
  welcome_cta="生成を開始 →",
),
"中文 (简体)": dict(
  nav_generate="生成", nav_tools="经纪人工具", nav_history="历史",
  config_head="房产", agent_head="经纪人资料",
  write_in="输出语言", write_ph="中文、英文…",
  prop_type="房产类型", prop_ph="豪华别墅、3室2厅…",
  price="价格", price_ph="$850,000 或 $2,400/月",
  location="地点", loc_ph="上海市浦东新区",
  beds="卧室", baths="浴室", sqm="㎡", year="年份",
  parking="车位", amenities="特征", amen_ph="泳池、健身房、海景…",
  strategy="营销策略",
  strategies=["⭐ 标准专业","💎 顶奢","📈 投资","🏡 家庭",
               "🎨 简约","🏖️ 度假","🏗️ 新开发","🏢 商业"],
  notes="备注", notes_ph="翻新厨房，靠近地铁…",
  agent_name="姓名", agent_ph="张伟",
  agent_co="中介公司", agent_co_ph="豪华地产集团",
  agent_phone="电话", agent_phone_ph="+86 138 0000 0000",
  agent_email="邮箱", agent_email_ph="zhang@luxerealty.cn",
  upload_label="将房产照片拖放到此处 — JPG、PNG、WEBP",
  gen_btn="生成完整营销套餐",
  regen_btn="重新生成",
  save_btn="保存到历史",
  saved_ok="已保存！",
  dl_all="下载全部",
  dl_section="下载",
  copy_btn="复制",
  copied_btn="已复制！",
  tab1="房源", tab2="社交", tab3="视频", tab4="规格", tab5="邮件", tab6="SEO",
  tools_title="经纪人工具箱",
  tools_sub="一键即得专业成果。",
  run_tool="生成 →",
  clear_tool="清除",
  dl_tool="下载",
  hist_title="已保存房源",
  hist_empty="还没有保存的房源。",
  load_btn="加载",
  del_btn="删除",
  words="词", chars="字符",
  comp_ok="✓ 公平住房 — 无问题",
  comp_warn="⚠ 请检查: ",
  unsaved="未保存",
  all_saved="已保存",
  photo="照片",
  err="错误: ",
  loading=["正在分析照片…","正在撰写房源描述…","正在构建社交套件…",
           "正在编写视频脚本…","正在整理技术规格…","正在起草邮件…","正在构建SEO套件…","正在完成…"],
  empty_title="您的营销套餐将显示在这里",
  empty_sub="上传照片 · 填写详情 · 点击生成",
  welcome_title="专业房地产\n营销平台",
  welcome_sub="将房产照片在几秒钟内转化为完整的专业营销套餐。",
  welcome_cta="开始生成 →",
),
"العربية": dict(
  nav_generate="إنشاء", nav_tools="أدوات الوكيل", nav_history="السجل",
  config_head="العقار", agent_head="ملف الوكيل",
  write_in="لغة المحتوى", write_ph="العربية، الإنجليزية…",
  prop_type="نوع العقار", prop_ph="فيلا فاخرة، شقة 3 غرف…",
  price="السعر", price_ph="$850,000 أو $2,400/شهر",
  location="الموقع", loc_ph="دبي، وسط المدينة",
  beds="غرف", baths="حمامات", sqm="م²", year="السنة",
  parking="موقف", amenities="المميزات", amen_ph="مسبح، صالة، إطلالة بحرية…",
  strategy="الاستراتيجية",
  strategies=["⭐ احترافي","💎 فخامة فائقة","📈 استثماري","🏡 عائلي",
               "🎨 عصري بسيط","🏖️ عطلات","🏗️ مشروع جديد","🏢 تجاري"],
  notes="ملاحظات", notes_ph="مطبخ مجدد، قرب المترو…",
  agent_name="اسمك", agent_ph="محمد الأحمد",
  agent_co="الوكالة", agent_co_ph="مجموعة لوكس العقارية",
  agent_phone="الهاتف", agent_phone_ph="+971 50 000 0000",
  agent_email="البريد الإلكتروني", agent_email_ph="m@luxerealty.ae",
  upload_label="اسحب الصور وأفلتها هنا — JPG، PNG، WEBP",
  gen_btn="إنشاء حزمة تسويقية متكاملة",
  regen_btn="إعادة الإنشاء",
  save_btn="حفظ في السجل",
  saved_ok="تم الحفظ!",
  dl_all="تحميل الكل",
  dl_section="تحميل",
  copy_btn="نسخ",
  copied_btn="تم النسخ!",
  tab1="الإعلان", tab2="التواصل", tab3="الفيديو", tab4="المواصفات", tab5="البريد", tab6="SEO",
  tools_title="صندوق أدوات الوكيل",
  tools_sub="نقرة واحدة. نتيجة احترافية. فورية.",
  run_tool="إنشاء ←",
  clear_tool="مسح",
  dl_tool="تحميل",
  hist_title="العقارات المحفوظة",
  hist_empty="لا توجد عقارات محفوظة بعد.",
  load_btn="تحميل",
  del_btn="حذف",
  words="كلمة", chars="حرف",
  comp_ok="✓ الإسكان العادل — لا مشاكل",
  comp_warn="⚠ راجع: ",
  unsaved="غير محفوظ",
  all_saved="محفوظ",
  photo="صورة",
  err="خطأ: ",
  loading=["تحليل الصور…","كتابة الإعلان…","مجموعة التواصل الاجتماعي…",
           "سيناريو الفيديو…","تجميع المواصفات…","صياغة البريد…","حزمة SEO…","الانتهاء…"],
  empty_title="ستظهر حزمتك هنا",
  empty_sub="ارفع الصور · أدخل التفاصيل · اضغط إنشاء",
  welcome_title="المنصة الاحترافية\nللتسويق العقاري",
  welcome_sub="حوّل صور العقارات إلى حزمة تسويقية احترافية متكاملة في ثوانٍ.",
  welcome_cta="ابدأ الآن ←",
),
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
FAIR_HOUSING = [
    "adults only","no children","christian neighborhood","white neighborhood",
    "english speaking only","families only","gated for safety",
]

def flag_fh(text: str) -> list:
    tl = text.lower()
    return [t for t in FAIR_HOUSING if t in tl]

def extract_section(raw: str, n: int) -> str:
    m = re.search(rf"##\s*SECTION_{n}.*?(?=##\s*SECTION_|\Z)", raw, re.DOTALL|re.IGNORECASE)
    if not m:
        return ""
    lines = m.group(0).strip().splitlines()
    return "\n".join(lines[1:]).strip()

def wc(text: str):
    return len(text.split()), len(text)

def agent_str() -> str:
    parts = []
    if st.session_state.get("agent_name"):  parts.append(st.session_state.agent_name)
    if st.session_state.get("agent_co"):    parts.append(st.session_state.agent_co)
    if st.session_state.get("agent_phone"): parts.append(st.session_state.agent_phone)
    if st.session_state.get("agent_email"): parts.append(st.session_state.agent_email)
    return " | ".join(parts) if parts else "Agent details not provided"

def prop_str() -> str:
    ss = st.session_state
    return f"""Property: {ss.get('prop_type','Property')} | Location: {ss.get('location','Undisclosed')} | Price: {ss.get('price','POR')}
Beds: {ss.get('beds','N/A')} | Baths: {ss.get('baths','N/A')} | Size: {ss.get('sqm','N/A')} m² | Year: {ss.get('year_built','N/A')} | Parking: {ss.get('parking','N/A')}
Features: {ss.get('amenities','TBC')} | Notes: {ss.get('notes','None')}
Agent: {agent_str()}""".strip()

def save_to_history():
    ss = st.session_state
    entry = dict(
        id=str(datetime.now().timestamp()),
        date=datetime.now().strftime("%d %b %Y · %H:%M"),
        prop=ss.get("prop_type","Property"),
        loc=ss.get("location","—"),
        price=ss.get("price","—"),
        **{f"s{i}": ss.get(f"s{i}","") for i in range(1,7)},
    )
    if "history" not in ss:
        ss.history = []
    ss.history.insert(0, entry)
    if len(ss.history) > 50:
        ss.history = ss.history[:50]

def init_state():
    defaults = dict(
        page="generate", output_raw="",
        s1="",s2="",s3="",s4="",s5="",s6="",
        tool_out="", tool_title="", dirty=False, history=[],
        write_in="English", prop_type="", price="", location="",
        beds="", baths="", sqm="", year_built="", parking="", amenities="",
        strategy_idx=0, notes="",
        agent_name="", agent_co="", agent_phone="", agent_email="",
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# MASTER CSS — complete dark luxury design system
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
<style>
/* ═══════════════════════════════════════════════════
   FONTS
═══════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Lato:wght@300;400;700&display=swap');

/* ═══════════════════════════════════════════════════
   TOKENS
═══════════════════════════════════════════════════ */
:root {
  --gold:    #C9A84C;
  --gold-lt: #E8C97A;
  --dark:    #0A0A0B;
  --surface: #111114;
  --card:    #18181C;
  --card2:   #1E1E24;
  --border:  #2C2C35;
  --border2: #38383F;
  --text:    #F0F0F2;
  --text2:   #A0A0AB;
  --text3:   #606068;
  --green:   #22C55E;
  --amber:   #F59E0B;
  --red:     #EF4444;
  --radius:  10px;
  --radius-lg: 16px;
}

/* ═══════════════════════════════════════════════════
   RESET & BASE
═══════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  font-family: 'Lato', sans-serif !important;
  background: var(--dark) !important;
  color: var(--text) !important;
}

.stApp {
  background: var(--dark) !important;
  font-family: 'Lato', sans-serif !important;
}

/* ═══════════════════════════════════════════════════
   HIDE STREAMLIT CHROME
═══════════════════════════════════════════════════ */
#MainMenu, footer, header,
.stDeployButton,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
div[data-testid="stInputInstructions"],
span[data-testid="stIconMaterial"] {
  display: none !important;
  visibility: hidden !important;
}

/* ═══════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
  width: 290px !important;
  min-width: 290px !important;
}

section[data-testid="stSidebar"] > div {
  padding: 0 !important;
}

/* Sidebar scroll container */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding: 1.5rem 1.1rem 2rem !important;
  overflow-y: auto !important;
}

/* All sidebar text */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p {
  color: var(--text2) !important;
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.07em !important;
  text-transform: uppercase !important;
  font-family: 'Lato', sans-serif !important;
}

/* Sidebar inputs */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-size: 0.86rem !important;
  font-family: 'Lato', sans-serif !important;
  padding: 8px 12px !important;
  transition: border-color 0.2s !important;
}

section[data-testid="stSidebar"] input:focus,
section[data-testid="stSidebar"] textarea:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 2px rgba(201,168,76,0.18) !important;
  outline: none !important;
}

section[data-testid="stSidebar"] input::placeholder,
section[data-testid="stSidebar"] textarea::placeholder {
  color: var(--text3) !important;
}

/* Sidebar select */
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="select"] > div > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-size: 0.86rem !important;
  font-family: 'Lato', sans-serif !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] svg {
  fill: var(--text3) !important;
}

/* Dropdown portal */
[data-baseweb="popover"],
[data-baseweb="menu"] {
  background: var(--card2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important;
}

[role="option"], [role="listbox"] li {
  color: var(--text) !important;
  font-family: 'Lato', sans-serif !important;
  font-size: 0.87rem !important;
  padding: 8px 14px !important;
}

[role="option"]:hover { background: var(--border) !important; }
[role="option"][aria-selected="true"] {
  background: var(--gold) !important;
  color: var(--dark) !important;
}

/* Sidebar nav buttons */
.sb-nav-btn button {
  background: transparent !important;
  color: var(--text2) !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 9px 12px !important;
  font-size: 0.86rem !important;
  font-weight: 700 !important;
  font-family: 'Lato', sans-serif !important;
  text-align: left !important;
  width: 100% !important;
  letter-spacing: 0.02em !important;
  transition: all 0.15s !important;
}

.sb-nav-btn button:hover {
  background: var(--card2) !important;
  color: var(--text) !important;
}

.sb-nav-active button {
  background: var(--gold) !important;
  color: var(--dark) !important;
  font-weight: 700 !important;
}

.sb-nav-active button:hover {
  background: var(--gold-lt) !important;
  color: var(--dark) !important;
}

/* Sidebar section divider */
.sb-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1.1rem 0;
}

.sb-section {
  font-size: 0.65rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--text3) !important;
  margin: 1.2rem 0 0.6rem !important;
  font-family: 'Lato', sans-serif !important;
}

/* ═══════════════════════════════════════════════════
   MAIN CONTENT AREA
═══════════════════════════════════════════════════ */
.block-container {
  background: transparent !important;
  padding: 2rem 2.5rem 5rem !important;
  max-width: 1300px !important;
}

/* ═══════════════════════════════════════════════════
   TYPOGRAPHY
═══════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {
  font-family: 'Syne', sans-serif !important;
  color: var(--text) !important;
}

p, span, div, li {
  font-family: 'Lato', sans-serif !important;
  color: var(--text) !important;
}

.display-title {
  font-family: 'Syne', sans-serif;
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  color: var(--text);
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.display-title .gold { color: var(--gold); }

.section-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0.3rem;
}

.section-sub {
  font-size: 0.9rem;
  color: var(--text2);
  font-weight: 400;
}

/* ═══════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════ */

/* Primary generate button */
.btn-primary button {
  background: var(--gold) !important;
  color: var(--dark) !important;
  border: none !important;
  border-radius: var(--radius) !important;
  padding: 0.85rem 2rem !important;
  font-family: 'Syne', sans-serif !important;
  font-size: 0.88rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.08em !important;
  width: 100% !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 0 0 0 rgba(201,168,76,0) !important;
}

.btn-primary button:hover {
  background: var(--gold-lt) !important;
  box-shadow: 0 4px 20px rgba(201,168,76,0.35) !important;
  transform: translateY(-1px) !important;
}

.btn-primary button:active {
  transform: translateY(0) !important;
}

/* Secondary buttons */
.stButton > button {
  background: var(--card) !important;
  color: var(--text) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--radius) !important;
  font-family: 'Lato', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  padding: 0.48rem 1rem !important;
  cursor: pointer !important;
  transition: all 0.15s !important;
  letter-spacing: 0.01em !important;
}

.stButton > button:hover {
  background: var(--card2) !important;
  border-color: var(--gold) !important;
  color: var(--text) !important;
}

.stButton > button:active {
  transform: scale(0.98) !important;
}

/* Download buttons */
.stDownloadButton > button {
  background: var(--card) !important;
  color: var(--text) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--radius) !important;
  font-family: 'Lato', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  padding: 0.48rem 1rem !important;
  cursor: pointer !important;
  transition: all 0.15s !important;
}

.stDownloadButton > button:hover {
  background: var(--card2) !important;
  border-color: var(--gold) !important;
}

/* ═══════════════════════════════════════════════════
   FILE UPLOADER
═══════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
  background: var(--card) !important;
  border: 2px dashed var(--border2) !important;
  border-radius: var(--radius-lg) !important;
  transition: border-color 0.2s, background 0.2s !important;
}

[data-testid="stFileUploader"]:hover {
  border-color: var(--gold) !important;
  background: rgba(201,168,76,0.04) !important;
}

[data-testid="stFileUploader"] label {
  color: var(--text2) !important;
  font-size: 0.9rem !important;
  font-family: 'Lato', sans-serif !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  font-weight: 400 !important;
}

[data-testid="stFileUploader"] section {
  padding: 1.5rem !important;
}

[data-testid="stFileUploaderDropzone"] {
  border: none !important;
  background: transparent !important;
}

/* ═══════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  background: var(--card) !important;
  border-radius: var(--radius) !important;
  padding: 5px !important;
  border: 1px solid var(--border) !important;
  gap: 3px !important;
  flex-wrap: wrap !important;
}

.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: 7px !important;
  color: var(--text2) !important;
  font-family: 'Lato', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.81rem !important;
  padding: 7px 14px !important;
  border: none !important;
  white-space: nowrap !important;
  transition: all 0.15s !important;
  letter-spacing: 0.02em !important;
}

.stTabs [data-baseweb="tab"]:hover {
  background: var(--card2) !important;
  color: var(--text) !important;
}

.stTabs [aria-selected="true"] {
  background: var(--gold) !important;
  color: var(--dark) !important;
}

.stTabs [data-baseweb="tab-panel"] {
  padding-top: 1.25rem !important;
  background: transparent !important;
}

.stTabs [data-baseweb="tab-highlight"] {
  display: none !important;
}

/* ═══════════════════════════════════════════════════
   TEXT AREAS
═══════════════════════════════════════════════════ */
.stTextArea textarea {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: 'Lato', sans-serif !important;
  font-size: 0.9rem !important;
  line-height: 1.7 !important;
  padding: 1rem !important;
  resize: vertical !important;
  transition: border-color 0.15s !important;
  caret-color: var(--gold) !important;
}

.stTextArea textarea:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 3px rgba(201,168,76,0.12) !important;
  outline: none !important;
}

.stTextArea textarea::selection {
  background: rgba(201,168,76,0.25) !important;
}

.stTextArea label {
  display: none !important;
}

/* ═══════════════════════════════════════════════════
   TEXT INPUTS (main area)
═══════════════════════════════════════════════════ */
.stTextInput input {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: 'Lato', sans-serif !important;
  font-size: 0.88rem !important;
}

.stTextInput input:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important;
}

/* ═══════════════════════════════════════════════════
   PROGRESS & SPINNER
═══════════════════════════════════════════════════ */
.stProgress > div > div > div > div {
  background: linear-gradient(90deg, var(--gold), var(--gold-lt)) !important;
  border-radius: 99px !important;
}

.stProgress > div > div {
  background: var(--card) !important;
  border-radius: 99px !important;
  height: 6px !important;
}

.stSpinner > div {
  border-top-color: var(--gold) !important;
}

/* ═══════════════════════════════════════════════════
   ALERTS
═══════════════════════════════════════════════════ */
.stAlert {
  background: var(--card) !important;
  border-radius: var(--radius) !important;
  font-family: 'Lato', sans-serif !important;
  font-size: 0.87rem !important;
  border-left-width: 3px !important;
}

[data-testid="stAlertContentInfo"] { border-color: var(--gold) !important; }
[data-testid="stAlertContentSuccess"] { border-color: var(--green) !important; }
[data-testid="stAlertContentError"] { border-color: var(--red) !important; }

/* ═══════════════════════════════════════════════════
   SCROLLBAR
═══════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--dark); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold); }

/* ═══════════════════════════════════════════════════
   CUSTOM COMPONENTS
═══════════════════════════════════════════════════ */

/* Page header */
.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}

/* Cards */
.glass-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
}

.tool-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.4rem;
  margin-bottom: 0.75rem;
  transition: border-color 0.15s, background 0.15s;
  cursor: default;
}

.tool-card:hover {
  border-color: var(--gold);
  background: var(--card2);
}

.tool-name {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--text);
  margin-bottom: 4px;
}

.tool-desc {
  font-size: 0.82rem;
  color: var(--text2);
  line-height: 1.45;
}

/* Word count chips */
.wc-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin: 8px 0 12px;
  flex-wrap: wrap;
}

.wc-chip {
  background: var(--card2);
  color: var(--text2);
  font-size: 0.73rem;
  font-weight: 700;
  font-family: 'Lato', sans-serif;
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.03em;
}

/* Status chips */
.status-saved {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--green);
  font-family: 'Lato', sans-serif;
}

.status-dirty {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--amber);
  font-family: 'Lato', sans-serif;
}

/* Compliance */
.comp-ok {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(34,197,94,0.1);
  border: 1px solid rgba(34,197,94,0.3);
  color: var(--green);
  border-radius: 20px;
  padding: 4px 14px;
  font-size: 0.77rem;
  font-weight: 700;
  font-family: 'Lato', sans-serif;
  margin: 6px 0 12px;
}

.comp-warn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(245,158,11,0.1);
  border: 1px solid rgba(245,158,11,0.3);
  color: var(--amber);
  border-radius: 20px;
  padding: 4px 14px;
  font-size: 0.77rem;
  font-weight: 700;
  font-family: 'Lato', sans-serif;
  margin: 6px 0 12px;
}

/* Empty state */
.empty-state {
  background: var(--card);
  border: 1px dashed var(--border2);
  border-radius: var(--radius-lg);
  padding: 5rem 2rem;
  text-align: center;
  margin-top: 0.5rem;
}

.empty-icon { font-size: 3.5rem; margin-bottom: 1.25rem; }

.empty-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0.5rem;
}

.empty-sub {
  font-size: 0.9rem;
  color: var(--text2);
}

/* History card */
.hist-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.1rem 1.4rem;
  margin-bottom: 0.75rem;
  transition: border-color 0.15s;
}

.hist-card:hover { border-color: var(--border2); }
.hist-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.95rem; color: var(--text); }
.hist-meta { font-size: 0.79rem; color: var(--text2); margin-top: 3px; }

/* Output bar */
.output-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
  gap: 0.75rem;
}

.output-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text);
}

/* Photo grid */
.photo-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 1rem 0;
}

.photo-thumb {
  width: 120px;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--border);
}

/* Logo */
.logo-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0.25rem 0 1.25rem;
}

.logo-name {
  font-family: 'Syne', sans-serif;
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text);
}

.logo-name span { color: var(--gold); }

.logo-sub {
  font-size: 0.6rem;
  color: var(--text3);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-top: 1px;
  font-family: 'Lato', sans-serif;
}

/* Gold divider */
.gold-line {
  height: 1px;
  background: linear-gradient(90deg, var(--gold) 0%, transparent 100%);
  margin: 1.5rem 0;
  opacity: 0.4;
}

/* Landing / welcome */
.welcome-hero {
  background: linear-gradient(135deg, var(--card) 0%, var(--card2) 100%);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 3.5rem 2.5rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.welcome-hero::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at center, rgba(201,168,76,0.06) 0%, transparent 60%);
  pointer-events: none;
}

/* Tag badge */
.tag {
  display: inline-block;
  background: rgba(201,168,76,0.12);
  color: var(--gold);
  border: 1px solid rgba(201,168,76,0.3);
  border-radius: 20px;
  padding: 4px 14px;
  font-size: 0.75rem;
  font-weight: 700;
  font-family: 'Lato', sans-serif;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

/* Feature chips */
.feature-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 1.5rem;
}

.feature-chip {
  background: var(--card2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 14px;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text2);
  font-family: 'Lato', sans-serif;
}

/* Copy button inline */
.copy-btn {
  background: var(--card) !important;
  color: var(--text) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--radius) !important;
  padding: 0.48rem 1rem !important;
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  cursor: pointer !important;
  font-family: 'Lato', sans-serif !important;
  width: 100% !important;
  transition: all 0.15s !important;
}

.copy-btn:hover {
  background: var(--card2) !important;
  border-color: var(--gold) !important;
}

/* Expander */
.streamlit-expanderHeader {
  background: var(--card) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: 'Lato', sans-serif !important;
  font-weight: 700 !important;
  border: 1px solid var(--border) !important;
}

.streamlit-expanderContent {
  background: var(--card2) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--radius) var(--radius) !important;
}

details {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  overflow: hidden !important;
  margin-bottom: 0.6rem !important;
}

summary {
  background: var(--card) !important;
  color: var(--text) !important;
  font-family: 'Lato', sans-serif !important;
  font-weight: 700 !important;
  padding: 0.85rem 1.1rem !important;
  font-size: 0.88rem !important;
  cursor: pointer !important;
}

summary:hover { background: var(--card2) !important; }

/* Metric */
[data-testid="stMetric"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 1.1rem 1.25rem !important;
}

[data-testid="stMetricValue"] {
  font-family: 'Syne', sans-serif !important;
  color: var(--gold) !important;
  font-size: 1.8rem !important;
}

[data-testid="stMetricLabel"] {
  color: var(--text2) !important;
  font-size: 0.78rem !important;
  font-family: 'Lato', sans-serif !important;
}
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# PROMPT BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def build_prompt(lang: str, strategy: str) -> str:
    return f"""You are SarSa AI — the world's most advanced real estate marketing intelligence platform.
You combine a luxury copywriter, social media director, cinematographer, SEO strategist, and real estate consultant.

PROPERTY DATA:
{prop_str()}
MARKETING STRATEGY: {strategy}
WRITE ALL CONTENT IN: {lang}

Analyse every uploaded photo carefully — architecture, finishes, light quality, views, outdoor areas, room sizes.

Generate a COMPLETE 6-section marketing package. Use EXACTLY these markers, never skip any:

## SECTION_1 — PRIME LISTING COPY
450–650 words. Structure:
• ALL-CAPS headline (max 12 words, bold, compelling)
• Opening paragraph — paint a vivid lifestyle picture (3–4 sentences)
• Living spaces paragraph — reference what you see in photos
• Kitchen/bathrooms paragraph — specific details from photos
• Outdoor/amenities paragraph — lifestyle benefits
• Location & neighbourhood highlights (2–3 sentences)
• Investment/value proposition
• Closing CTA with agent contact details from the data above

## SECTION_2 — SOCIAL MEDIA KIT
Five platform posts:

📸 INSTAGRAM (caption 2000 chars max + 25 hashtags):
[Write full caption with emojis, storytelling, 3 clear sections]
[25 hashtags: 10 property, 8 location, 7 lifestyle]

👥 FACEBOOK (200–280 words):
[Community-focused, full details, conversational, price prominently shown]

💼 LINKEDIN (150–200 words):
[Investment angle, market insight, professional tone]

🐦 X/TWITTER (max 270 chars, 4 hashtags):
[Punchy opener + key stat + CTA]

📱 WHATSAPP BROADCAST (max 155 chars):
[Price + key feature + contact — ultra concise]

## SECTION_3 — CINEMATIC VIDEO SCRIPT
Full production script for a 60–90 second video:
• TITLE CARD (opening text overlay)
• 7 SCENES: each with [CAMERA: ...] [VOICEOVER: ...] [DURATION: ...]
• MUSIC DIRECTION: specific genre/mood suggestion
• CLOSING CARD with agent details
• YOUTUBE DESCRIPTION (150 words) + 10 tags

## SECTION_4 — TECHNICAL SPECIFICATIONS
Professional property data sheet:
• KEY SPECIFICATIONS (table format: feature | detail)
• ROOM-BY-ROOM breakdown from photos
• AMENITIES CHECKLIST (✓ present, — unknown)
• BUILDING & INFRASTRUCTURE notes
• LEGAL STATUS placeholder section
• CONTACT & VIEWING information

## SECTION_5 — EMAIL TEMPLATES
Three complete, ready-to-send emails:

📧 EMAIL 1 — JUST LISTED ANNOUNCEMENT
Subject: [Compelling subject line]
[150–200 word body + professional agent signature with all contact details]

📧 EMAIL 2 — POST-VIEWING FOLLOW-UP
Subject: [Warm follow-up subject]
[120–150 word body addressing viewing, next steps + signature]

📧 EMAIL 3 — PRICE REDUCTION / OPPORTUNITY ALERT
Subject: [Urgent but professional subject]
[110–130 word body, urgency without pressure + signature]

## SECTION_6 — SEO & DIGITAL MARKETING PACK
• 20 SEO KEYWORDS ranked (mix of short and long-tail)
• 3 META DESCRIPTIONS (155 chars each, include CTA)
• GOOGLE ADS: 3 Headlines (30 chars max each) + 2 Descriptions (90 chars max each)
• INSTAGRAM HASHTAGS by category: #Property(10) #Location(10) #Lifestyle(10)
• 10 YOUTUBE TAGS
• 5 PINTEREST BOARD NAME suggestions
• POSTING CALENDAR: best day + time for each platform

Write every word in {lang}. Be specific — reference real details from photos. Zero filler sentences."""


@st.cache_data
def load_logo(path: str):
    try:
        from PIL import Image
        import os
        return Image.open(path) if os.path.exists(path) else None
    except Exception:
        return None


def render_sidebar(T: dict):
    """Renders the full sidebar. Call from any page."""
    with st.sidebar:
        logo = load_logo("SarSa_Logo_Transparent.png")
        if logo:
            st.image(logo, use_container_width=True)
        else:
            st.markdown("""
            <div class='logo-wrap'>
              <div>
                <div class='logo-name'>Sar<span>Sa</span> AI</div>
                <div class='logo-sub'>Real Estate Intelligence</div>
              </div>
            </div>""", unsafe_allow_html=True)

        # Language
        langs = list(LANGS.keys())
        ui_lang = st.selectbox("🌐", langs, index=0, key="ui_lang_sel", label_visibility="collapsed")
        T_new = LANGS[ui_lang]

        st.markdown("<hr class='sb-divider'>", unsafe_allow_html=True)

        # Navigation
        st.markdown("<div class='sb-section'>Menu</div>", unsafe_allow_html=True)
        nav_items = [
            ("generate", f"▶  {T_new['nav_generate']}"),
            ("tools",    f"⚡  {T_new['nav_tools']}"),
            ("history",  f"📁  {T_new['nav_history']}"),
        ]
        for pid, plbl in nav_items:
            is_active = st.session_state.get("page") == pid
            cls = "sb-nav-active" if is_active else "sb-nav-btn"
            st.markdown(f"<div class='{cls}'>", unsafe_allow_html=True)
            if st.button(plbl, key=f"nav_{pid}", use_container_width=True):
                st.session_state.page = pid
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr class='sb-divider'>", unsafe_allow_html=True)

        # Property
        st.markdown(f"<div class='sb-section'>{T_new['config_head']}</div>", unsafe_allow_html=True)

        st.session_state.write_in = st.text_input(
            T_new["write_in"], value=st.session_state.write_in,
            placeholder=T_new["write_ph"], key="si_wi"
        )
        st.session_state.prop_type = st.text_input(
            T_new["prop_type"], value=st.session_state.prop_type,
            placeholder=T_new["prop_ph"], key="si_pt"
        )
        st.session_state.price = st.text_input(
            T_new["price"], value=st.session_state.price,
            placeholder=T_new["price_ph"], key="si_pr"
        )
        st.session_state.location = st.text_input(
            T_new["location"], value=st.session_state.location,
            placeholder=T_new["loc_ph"], key="si_lo"
        )

        c1, c2 = st.columns(2)
        with c1:
            st.session_state.beds = st.text_input(T_new["beds"], value=st.session_state.beds, placeholder="3", key="si_b")
        with c2:
            st.session_state.baths = st.text_input(T_new["baths"], value=st.session_state.baths, placeholder="2", key="si_ba")

        c3, c4 = st.columns(2)
        with c3:
            st.session_state.sqm = st.text_input(T_new["sqm"], value=st.session_state.sqm, placeholder="120", key="si_sq")
        with c4:
            st.session_state.year_built = st.text_input(T_new["year"], value=st.session_state.year_built, placeholder="2019", key="si_yr")

        st.session_state.parking = st.text_input(
            T_new["parking"], value=st.session_state.parking, placeholder="1", key="si_pk"
        )
        st.session_state.amenities = st.text_input(
            T_new["amenities"], value=st.session_state.amenities,
            placeholder=T_new["amen_ph"], key="si_am"
        )

        strats = T_new["strategies"]
        sidx = st.session_state.strategy_idx
        if sidx >= len(strats): sidx = 0
        chosen = st.selectbox(T_new["strategy"], strats, index=sidx, key="si_st")
        st.session_state.strategy_idx = strats.index(chosen)

        st.session_state.notes = st.text_area(
            T_new["notes"], value=st.session_state.notes,
            placeholder=T_new["notes_ph"], height=68, key="si_no"
        )

        st.markdown("<hr class='sb-divider'>", unsafe_allow_html=True)

        # Agent
        st.markdown(f"<div class='sb-section'>{T_new['agent_head']}</div>", unsafe_allow_html=True)
        st.session_state.agent_name  = st.text_input(T_new["agent_name"],  value=st.session_state.agent_name,  placeholder=T_new["agent_ph"],       key="si_an")
        st.session_state.agent_co    = st.text_input(T_new["agent_co"],    value=st.session_state.agent_co,    placeholder=T_new["agent_co_ph"],    key="si_ac")
        st.session_state.agent_phone = st.text_input(T_new["agent_phone"], value=st.session_state.agent_phone, placeholder=T_new["agent_phone_ph"], key="si_ap")
        st.session_state.agent_email = st.text_input(T_new["agent_email"], value=st.session_state.agent_email, placeholder=T_new["agent_email_ph"], key="si_ae")

        return T_new
