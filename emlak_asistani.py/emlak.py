# ==============================================================================
# HBG İNŞAAT & GAYRİMENKUL ERP & AI ASİSTANI
# 
# Bu dosyanın adı: emlak.py
# Çalıştırmak için terminale yazılacak komut:
# streamlit run emlak.py
# ==============================================================================

import os
from datetime import date
import pandas as pd
import base64
# pyrefly: ignore [missing-import]
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
# pyrefly: ignore [missing-import]
import google.generativeai as genai

# --- YARDIMCI FORMAT FONKSİYONLARI ---
def format_tl(deger):
    """
    Sayıları Türk Lirası formatında, her 3 basamakta bir nokta olacak şekilde biçimlendirir.
    Örnek: 20000000 -> 20.000.000 ₺
    """
    try:
        val = float(deger)
        formatted = f"{val:,.0f}".replace(",", ".")
        return f"{formatted} ₺"
    except Exception:
        return "0 ₺"

def format_sayi(deger):
    """Her 3 rakamda bir nokta koyar (₺ işareti olmadan). Örn: 20.000.000"""
    try:
        val = float(deger)
        return f"{val:,.0f}".replace(",", ".")
    except Exception:
        return "0"

def parse_tutar(deger):
    """Metin içindeki tüm noktaları/harfleri temizleyip tam sayıya çevirir."""
    temiz = "".join(c for c in str(deger) if c.isdigit())
    return int(temiz) if temiz else 0


# --- 1. OTOMATİK SECRETS & API KEY YÖNETİMİ (ARKA PLAN) ---
streamlit_dir = ".streamlit"
secrets_file = os.path.join(streamlit_dir, "secrets.toml")

def get_current_api_key():
    if st.session_state.get("user_gemini_key"):
        k = st.session_state["user_gemini_key"].strip()
        if k and not k.startswith("AQ.") and k != "BURAYA_API_KEYINIZI_YAZIN":
            return k

    if os.getenv("GEMINI_API_KEY"):
        k = os.getenv("GEMINI_API_KEY").strip()
        if k and not k.startswith("AQ.") and k != "BURAYA_API_KEYINIZI_YAZIN":
            return k

    try:
        if "GEMINI_API_KEY" in st.secrets:
            k = st.secrets["GEMINI_API_KEY"].strip()
            if k and not k.startswith("AQ.") and k != "BURAYA_API_KEYINIZI_YAZIN":
                return k
    except Exception:
        pass
    
    return None


# --- 2. GOOGLE GEMINI MODEL YÜKLEME VE BAĞLANTI ---
def initialize_gemini_model():
    api_key = get_current_api_key()
    if not api_key:
        return None, "Geçerli bir API Key girilmedi."

    try:
        genai.configure(api_key=api_key)

        model_candidates = [
            "gemini-1.5-flash",
            "models/gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]

        selected_model = None
        for model_name in model_candidates:
            try:
                m = genai.GenerativeModel(model_name)
                selected_model = m
                break
            except Exception:
                continue

        if selected_model is None:
            selected_model = genai.GenerativeModel("gemini-1.5-flash")

        return selected_model, None
    except Exception as e:
        return None, str(e)


# --- 3. AKILLI YERLEŞİK İLAN VE ŞANTİYE MOTORU (HBG İNŞAAT & GAYRİMENKUL) ---
def generate_pro_listing(konum, ozellik_maddeleri, fiyat_str, hedef_kitle, ekstra_not="", ilan_turu="SATILIK", lokasyon_maddeleri=None):
    fiyat_num = parse_tutar(fiyat_str)
    fiyat_tl = format_tl(fiyat_num)
    
    if ilan_turu == "KİRALIK":
        baslik = f"💎 HBG İNŞAAT & GAYRİMENKUL'DEN {konum.upper()} MERKEZİNDE {fiyat_tl} KİRALIK FIRSAT PORTFÖY!"
        fiyat_etiketi = f"💰 **Kira Bedeli:** {fiyat_tl}"
        durum_metni = f"**{hedef_kitle.lower()}** arayan müşterilerimiz için özel olarak KİRALIK olarak sunulmuştur."
        ek_kosul = "🔑 **Kira Koşulu:** Düzenli gelirli / kurumsal kiracı önceliklidir."
    else:
        baslik = f"💎 HBG İNŞAAT & GAYRİMENKUL'DEN {konum.upper()} MERKEZİNDE {fiyat_tl} SATILIK FIRSAT PORTFÖY!"
        fiyat_etiketi = f"💰 **Satış Fiyatı:** {fiyat_tl}"
        durum_metni = f"**{hedef_kitle.lower()}** arayan müşterilerimiz için özel olarak SATILIĞA sunulmuştur."
        ek_kosul = "🔑 **Teslim Durumu:** Hemen Taşınmaya Hazır / Boş"

    maddeler_metin = "\n".join([f"• {m}" for m in ozellik_maddeleri])
    if ekstra_not:
        maddeler_metin += f"\n• **Özel Not / Detay:** {ekstra_not}"

    if lokasyon_maddeleri:
        lokasyon_metin = "\n".join([f"* {l}" for l in lokasyon_maddeleri])
    else:
        lokasyon_metin = """* **Ulaşım:** Toplu taşıma ağlarına, ana arterlere ve metro/bağlantı yollarına yürüme mesafesinde.
* **Sosyal Yaşam:** Çevresinde seçkin eğitim kurumları, hastaneler, AVM'ler, kafeler ve sosyal donatı alanları mevcuttur.
* **Yatırım & Yaşam Değeri:** Bölgenin hızla artan değer grafiği ve seçkin çevre profiliyle konforlu ve güvenli bir yaşam sunar.
* **Yapı & İnşaat Kalitesi:** HBG İnşaat standartlarında; güncel deprem yönetmeliğine tam uyumlu, 1. sınıf işçilik ve A kalite malzeme kullanılarak tamamlanmıştır."""

    taslak = f"""### 🏷️ İLAN BAŞLIĞI:
**{baslik}**

---

### 📌 İLAN AÇIKLAMASI:

**HBG İNŞAAT & GAYRİMENKUL Güvencesi ve Ayrıcalığıyla;**

{konum} bölgesinin en prestijli, değer kazanan ve merkezi lokasyonunda yer alan gayrimenkulümüz, {durum_metni}

#### 🏡 GAYRİMENKULÜN ÖNE ÇIKAN ÖZELLİKLERİ:
{maddeler_metin}

#### 📍 LOKASYON & ÇEVRE AVANTAJLARI:
{lokasyon_metin}

---
{fiyat_etiketi}  
📑 **Tapu / Kontrat Durumu:** Resmi Sözleşmeli / Kat Mülkiyetli  
{ek_kosul}  

📞 **Detaylı sunum, yerinde keşif ve randevu için lütfen bizimle iletişime geçiniz.**  
**HBG İNŞAAT & GAYRİMENKUL**
"""
    return taslak


# --- 4. SAYFA DÜZENİ VE GENEL AYARLAR ---
st.set_page_config(
    page_title="HBG İNŞAAT & GAYRİMENKUL",
    layout="wide",
    page_icon="🏢"
)

# --- GÖZ YORMAYAN KOYU TEMA & YÜKSEK OKUNAKLILIKLI BUTONLAR CSS ---
st.markdown("""
<style>
/* ─── GENEL ARKA PLAN (GÖZ YORMAYAN KOYU / ANTRASİT TONLAR) ── */
.stApp {
    background-color: #111827 !important; /* Koyu antrasit-gece mavisi */
    color: #F3F4F6 !important;
}

/* ─── SOL SIDEBAR ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #0A0F1D !important; /* Çok koyu asil gece mavisi */
    border-right: 1px solid #1F2937 !important;
}
[data-testid="stSidebar"] h3 {
    color: #F9FAFB !important;
    font-weight: 700 !important;
    text-align: center !important;
    padding-bottom: 8px !important;
    margin-bottom: 18px !important;
    border-bottom: 1px solid #374151 !important;
    font-size: 1.15rem !important;
}

/* ─── SIDEBAR BUTONLARI (NET, GÖZ ALICI VE ÇOK OKUNAKLI) ──── */
/* Aktif Seçili Buton: Canlı Altın/Sarı zemin üzerine Koyu Siyah Net Yazı */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #F59E0B !important; /* Canlı ve net Amber/Altın */
    color: #000000 !important; /* Tam siyah, maksimum kontrast */
    border: 2px solid #FBBF24 !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    width: 100% !important;
    margin-bottom: 10px !important;
    box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3) !important;
    letter-spacing: 0.5px !important;
}

/* Pasif Buton: Koyu zemin üzerine Net Beyaz Yazı ve İnce Çerçeve */
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: #1F2937 !important;
    color: #F9FAFB !important; /* Parlak net beyaz */
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    width: 100% !important;
    margin-bottom: 10px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: #374151 !important;
    color: #FBBF24 !important;
    border-color: #FBBF24 !important;
}

/* ─── BAŞLIKLAR & METİNLER ───────────────────────────────── */
h1, h2 {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}
h3, h4 {
    color: #E5E7EB !important;
    font-weight: 700 !important;
}
.stApp p, .stApp label, .stApp span {
    color: #D1D5DB !important;
}

/* ─── METRİK KARTLARI (İNŞAAT Aİ İÇİN) ───────────────────── */
[data-testid="stMetric"] {
    background: #1F2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
    padding: 12px !important;
}
[data-testid="stMetricLabel"] {
    color: #9CA3AF !important;
}
[data-testid="stMetricValue"] {
    color: #F9FAFB !important;
}

/* ─── SATILIK / KİRALIK SEÇİM BUTONLARI ─────────────────── */
.stButton > button[kind="primary"] {
    background-color: #2563EB !important; /* Canlı Mavi */
    color: #FFFFFF !important;
    border: 1px solid #3B82F6 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}
.stButton > button[kind="secondary"] {
    background-color: #1F2937 !important;
    color: #D1D5DB !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* ─── BİLGİ KUTUCUĞU (ÜRETİLEN İLAN TASLAĞI BÖLÜMÜ) ──────── */
[data-testid="stAlert"] {
    background-color: #1E293B !important;
    color: #E2E8F0 !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}
[data-testid="stAlert"] * {
    color: #E2E8F0 !important;
}

/* ─── GİRDİ ALANLARI (INPUT & SELECTBOX) ─────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background-color: #1F2937 !important;
    border: 1.5px solid #374151 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #F59E0B !important;
}

/* Number input (+ / -) butonları */
.stNumberInput button {
    background-color: #374151 !important;
    color: #FFFFFF !important;
    border: none !important;
}

/* ─── MULTISELECT ETİKETLERİ ────────────────────────────── */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: #DC2626 !important;
    color: #FFFFFF !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
    color: #FFFFFF !important;
}

/* ─── BÖLÜM ÇİZGİLERİ ───────────────────────────────────── */
hr {
    border-color: #374151 !important;
}

/* ─── BELİRGİN VE ŞIK SEKME BAŞLIKLARI (stTabs) ──────────── */
[data-testid="stTabs"] {
    margin-top: 10px !important;
    margin-bottom: 20px !important;
}

/* Sekme çubuğunun zemin şeridi */
[data-testid="stTabs"] [role="tablist"] {
    background-color: #0B132B !important; /* Çok koyu lacivert zemin */
    padding: 6px 10px !important;
    border-radius: 12px !important;
    border: 1.5px solid #1E293B !important;
    display: flex !important;
    align-items: center !important;
    gap: 4px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
}

/* Tüm sekme butonları */
[data-testid="stTabs"] button[role="tab"] {
    position: relative !important;
    background-color: transparent !important;
    color: #94A3B8 !important; /* Okunaklı gri-mavi */
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    border: 1.5px solid transparent !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}

/* ─── SEKMELER ARASINDAKİ AYIRICI DİKEY ÇUBUK ────────────── */
[data-testid="stTabs"] button[role="tab"]:not(:last-child)::after {
    content: "" !important;
    position: absolute !important;
    right: -3px !important;
    top: 25% !important;
    height: 50% !important;
    width: 2px !important;
    background: linear-gradient(180deg, transparent, #334155, transparent) !important;
    pointer-events: none !important;
}

/* Sekme üzerine gelindiğinde (Hover & Mikro Animasyon) */
[data-testid="stTabs"] button[role="tab"]:hover {
    color: #F8FAFC !important;
    background-color: rgba(255, 255, 255, 0.06) !important;
    transform: translateY(-2px) !important; /* Yukarı hafif tatlı sıçrama */
}

/* AKTİF SEÇİLİ SEKME (Altın Kart & Canlı Animasyon) */
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #1E293B, #0F172A) !important;
    color: #F59E0B !important; /* Canlı Amber/Altın Sarısı */
    border: 1.5px solid #F59E0B !important;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.3) !important;
    transform: translateY(-2px) scale(1.02) !important; /* Belirgin büyüme ve yükselme */
}

/* Aktif sekmenin ayırıcı çubuğunu gizle */
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]::after {
    display: none !important;
}

/* Standart kırmızı alt çizgiyi gizle */
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Üst penceredeki inputlara anlık erişip klavyeden tuşa basıldığı anda noktalayan JavaScript
components.html("""
<script>
(function() {
    function formatWithDots(str) {
        let nums = str.replace(/\\D/g, '');
        if (!nums) return '';
        return nums.replace(/\\B(?=(\\d{3})+(?!\\d))/g, ".");
    }

    function setVal(elem, val) {
        let lastVal = elem.value;
        elem.value = val;
        let event = new Event('input', { bubbles: true });
        // React 16+ uyumluluğu için tracker
        let tracker = elem._valueTracker;
        if (tracker) {
            tracker.setValue(lastVal);
        }
        elem.dispatchEvent(event);
    }

    function attachMask() {
        try {
            let doc = window.parent.document;
            let inputs = doc.querySelectorAll('input[type="text"]');
            inputs.forEach(input => {
                let label = (input.getAttribute('aria-label') || '').toLowerCase();
                let isPrice = label.includes('fiyat') || label.includes('kira') || label.includes('bütçe') || label.includes('tutar');
                
                if (isPrice && !input.hasAttribute('data-live-mask')) {
                    input.setAttribute('data-live-mask', 'true');
                    
                    input.addEventListener('input', function(e) {
                        let cursor = this.selectionStart;
                        let oldLen = this.value.length;
                        let formatted = formatWithDots(this.value);
                        
                        if (this.value !== formatted && formatted !== '') {
                            setVal(this, formatted);
                            let newLen = formatted.length;
                            let newPos = cursor + (newLen - oldLen);
                            if (newPos >= 0) {
                                this.setSelectionRange(newPos, newPos);
                            }
                        }
                    });
                }
            });
        } catch(err) {}
    }

    setInterval(attachMask, 150);
})();
</script>
""", height=0, width=0)

# Oturum hafızasını (Session State) başlat
if "aktif_modul" not in st.session_state:
    st.session_state.aktif_modul = "EMLAK Aİ"

if "hedef_butce_str" not in st.session_state:
    st.session_state.hedef_butce_str = "20.000.000"

if "satilik_fiyat_str" not in st.session_state:
    st.session_state.satilik_fiyat_str = "18.500.000"

if "kiralik_fiyat_str" not in st.session_state:
    st.session_state.kiralik_fiyat_str = "65.000"

if "sablon_oda" not in st.session_state:
    st.session_state.sablon_oda = "3+1"

if "sablon_brut" not in st.session_state:
    st.session_state.sablon_brut = 145

if "sablon_net" not in st.session_state:
    st.session_state.sablon_net = 125

if "sablon_kat" not in st.session_state:
    st.session_state.sablon_kat = "Ara Kat"

if "sablon_yas" not in st.session_state:
    st.session_state.sablon_yas = "0 (Sıfır)"

if "sablon_isitma" not in st.session_state:
    st.session_state.sablon_isitma = "Yerden Isıtma"

if "df_harcamalar" not in st.session_state:
    st.session_state.df_harcamalar = pd.DataFrame([
        {"Tarih": "15.09.2026", "Kategori": "Hafriyat & Zemin", "Açıklama": "Temel kazısı ve hafriyat dökümü", "Tutar": 850000},
        {"Tarih": "20.09.2026", "Kategori": "Demir & Beton", "Açıklama": "50 Ton nervürlü inşaat demiri tedariği", "Tutar": 1450000},
        {"Tarih": "25.09.2026", "Kategori": "Demir & Beton", "Açıklama": "C35 Hazır beton dökümü (Temel 1. Etap)", "Tutar": 920000},
        {"Tarih": "28.09.2026", "Kategori": "Ruhsat & Harçlar", "Açıklama": "Belediye yapı denetim ve ruhsat harçları", "Tutar": 380000},
        {"Tarih": "02.10.2026", "Kategori": "Kaba İnşaat & İşçilik", "Açıklama": "Kalıpçı ve demirci taşeron 1. hakedişi", "Tutar": 650000}
    ])

if "manuel_harcanan" not in st.session_state:
    st.session_state.manuel_harcanan = 4250000


# --- SIDEBAR: DİKEY 2 BUTON (EMLAK Aİ ÜSTTE) ---
st.sidebar.markdown("### 🏢 Menü")

btn_emlak = st.sidebar.button(
    "🏡 EMLAK Aİ",
    use_container_width=True,
    type="primary" if st.session_state.aktif_modul == "EMLAK Aİ" else "secondary"
)
btn_insaat = st.sidebar.button(
    "🏗️ İNŞAAT Aİ",
    use_container_width=True,
    type="primary" if st.session_state.aktif_modul == "İNŞAAT Aİ" else "secondary"
)

if btn_emlak:
    st.session_state.aktif_modul = "EMLAK Aİ"
    st.rerun()
elif btn_insaat:
    st.session_state.aktif_modul = "İNŞAAT Aİ"
    st.rerun()

# --- ELEŞTİRİ 1 ÇÖZÜMÜ: SOL MENÜ BOŞLUĞUNU DOLDURAN KURUMSAL LOGO & BİLGİ KARTI ---
st.sidebar.markdown("---")

logo_b64 = ""
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg") if "__file__" in locals() else "logo.jpg"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as img_f:
        logo_b64 = base64.b64encode(img_f.read()).decode()

logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width: 105px; height: 105px; object-fit: contain; border-radius: 12px; margin-bottom: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.35);">' if logo_b64 else '<div style="font-size: 1.8rem; margin-bottom: 4px;">🏢💎</div>'

st.sidebar.markdown(f"""
<div style="
    background: rgba(31, 41, 55, 0.6);
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    margin-top: 15px;
">
    {logo_html}
    <div style="color: #F59E0B; font-weight: 800; font-size: 0.95rem; letter-spacing: 0.5px;">HBG İNŞAAT & GAYRİMENKUL</div>
    <div style="color: #9CA3AF; font-size: 0.75rem; margin-top: 4px;">Kurumsal ERP & AI Portföy Asistanı</div>
    <div style="
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid #10B981;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-top: 10px;
    ">● SİSTEM AKTİF (v2.0 PRO)</div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 1. MODÜL: EMLAK Aİ (HBG İNŞAAT & GAYRİMENKUL)
# ==============================================================================
if st.session_state.aktif_modul == "EMLAK Aİ":
    st.title("🏡 HBG İNŞAAT & GAYRİMENKUL - EMLAK Aİ")
    st.caption("Yapay Zeka Destekli Gayrimenkul İlan, Pazarlama ve Portföy Hazırlama Sistemi")

    c_e1, c_e2 = st.columns([1, 1], gap="medium")

    with c_e1:
        st.subheader("📝 Portföy Temel Bilgileri")

        if "ilan_turu" not in st.session_state:
            st.session_state.ilan_turu = "SATILIK"

        # KİRALIK / SATILIK BUTONLARI
        st.caption("İlan Kategorisi:")
        col_btn_sat, col_btn_kir = st.columns(2)
        if col_btn_sat.button(
            "🏷️ SATILIK",
            use_container_width=True,
            type="primary" if st.session_state.ilan_turu == "SATILIK" else "secondary"
        ):
            st.session_state.ilan_turu = "SATILIK"
            st.rerun()

        if col_btn_kir.button(
            "🔑 KİRALIK",
            use_container_width=True,
            type="primary" if st.session_state.ilan_turu == "KİRALIK" else "secondary"
        ):
            st.session_state.ilan_turu = "KİRALIK"
            st.rerun()

        konum = st.text_input(
            "📍 Portföy Konumu (Şehir / İlçe / Mahalle)",
            value="İstanbul / Kadıköy / Caddebostan",
            placeholder="Örn: İstanbul / Kadıköy / Fenerbahçe"
        )

        col_f1, col_f2 = st.columns(2)
        if st.session_state.ilan_turu == "SATILIK":
            girilen_satilik = col_f1.text_input(
                "💰 Satış Fiyatı (TL)",
                value=st.session_state.satilik_fiyat_str,
                help="Yazdığınızda otomatik olarak her 3 rakamda bir nokta koyulur."
            )
            satilik_sayi = parse_tutar(girilen_satilik)
            st.session_state.satilik_fiyat_str = format_sayi(satilik_sayi)
            fiyat_str = st.session_state.satilik_fiyat_str

            hedef_kitle = col_f2.selectbox(
                "🎯 Hedef Alıcı Kitlesi",
                ["Aile & Konfor Odaklı", "Yatırım & Yüksek Prim / Kira Getirili", "Lüks & Prestij Odaklı", "Kentsel Dönüşüm / Fırsat"]
            )
        else:
            girilen_kiralik = col_f1.text_input(
                "💰 Kira Bedeli (TL)",
                value=st.session_state.kiralik_fiyat_str,
                help="Yazdığınızda otomatik olarak her 3 rakamda bir nokta koyulur."
            )
            kiralik_sayi = parse_tutar(girilen_kiralik)
            st.session_state.kiralik_fiyat_str = format_sayi(kiralik_sayi)
            fiyat_str = st.session_state.kiralik_fiyat_str

            hedef_kitle = col_f2.selectbox(
                "🎯 Hedef Kiracı Kitlesi",
                ["Aile & Uzun Dönem", "Kurumsal Kiracı / Yönetici", "Memur / Çalışan", "Öğrenci & Bekar", "Yabancı"]
            )

        # --- ELEŞTİRİ 2 ÇÖZÜMÜ: KOMPAKT SEKMELİ FORM (SCROLL YÜKÜNÜ KALDIRIR) ---
        tab_ozellikler, tab_lokasyon, tab_fotolar = st.tabs([
            "🏠 Daire Özellikleri", 
            "📍 Lokasyon & Çevre", 
            "📸 Portföy Fotoğrafları & AI Görsel Analizi"
        ])

        with tab_ozellikler:
            # — Satır 1: 4 kolon yatay —
            oda_listesi = ["1+1", "2+1", "3+1", "4+1", "4+2", "5+1", "5+2", "Villa / Müstakil", "Dükkan / Mağaza", "Stüdyo (1+0)"]
            oda_idx = oda_listesi.index(st.session_state.sablon_oda) if st.session_state.sablon_oda in oda_listesi else 2

            col_oz1, col_oz2, col_oz3, col_oz4 = st.columns(4)
            oda_sayisi = col_oz1.selectbox(
                "🛏️ Oda",
                oda_listesi,
                index=oda_idx
            )
            brut_m2 = col_oz2.number_input("📐 Brüt m²", min_value=20, max_value=5000, value=st.session_state.sablon_brut, step=5)
            net_m2 = col_oz3.number_input("📏 Net m²", min_value=15, max_value=4000, value=st.session_state.sablon_net, step=5)
            
            yas_listesi = ["0 (Sıfır)", "1-5 Yaş", "6-10 Yaş", "11-15 Yaş", "16-20 Yaş", "21+ Yaş"]
            yas_idx = yas_listesi.index(st.session_state.sablon_yas) if st.session_state.sablon_yas in yas_listesi else 0
            bina_yasi = col_oz4.selectbox(
                "🏗️ Bina Yaşı",
                yas_listesi,
                index=yas_idx
            )

            # — Satır 2: Kolon genişlikleri (Banyo & Balkon daha geniş okunaklı) —
            kat_listesi = [
                "1. Kat", "2. Kat", "3. Kat", "4. Kat", "5. Kat",
                "6. Kat", "7. Kat", "8. Kat", "9. Kat", "10. Kat",
                "10+ Kat / Yüksek Kat", "Ara Kat", "Giriş Katı", "Bahçe Katı", 
                "En Üst Kat", "Çatı Dubleksi", "Bahçe Dubleksi", "Müstakil / Villa"
            ]
            kat_idx = kat_listesi.index(st.session_state.sablon_kat) if st.session_state.sablon_kat in kat_listesi else 11

            col_oz5, col_oz6, col_oz7, col_oz8 = st.columns([1, 1, 1, 1.4])
            bulundugu_kat = col_oz5.selectbox(
                "🏢 Kat",
                kat_listesi,
                index=kat_idx
            )
            
            isitma_listesi = ["Yerden Isıtma", "Doğalgaz (Kombi)", "Merkezi (Pay Ölçer)", "VRF / Klima"]
            isitma_idx = isitma_listesi.index(st.session_state.sablon_isitma) if st.session_state.sablon_isitma in isitma_listesi else 0
            isitma_tipi = col_oz6.selectbox(
                "🔥 Isıtma",
                isitma_listesi,
                index=isitma_idx
            )
            otopark_durumu = col_oz7.selectbox(
                "🚗 Otopark",
                ["Kapalı & Asansörlü", "Açık & Asansörlü", "Kapalı Otopark", "Açık Otopark", "Asansörlü", "Mevcut Değil"]
            )
            banyo_balkon = col_oz8.selectbox(
                "🚿 Banyo & Balkon",
                ["2 Banyo + Çift Balkon", "Ebeveyn Banyolu + Balkon", "1 Banyo + Balkon", "Geniş Teraslı", "1 Banyo"]
            )

            ekstra_donanimlar = st.multiselect(
                "✨ Ekstra Donanımlar & Seçenekler",
                [
                    "Deniz Manzaralı",
                    "Akıllı Ev Sistemi",
                    "7/24 Güvenlik & Kamera",
                    "Yüzme Havuzu & Fitness",
                    "Giyinme Odası",
                    "Site İçi Güvenlikli",
                    "Krediye Uygun",
                    "Kat Mülkiyetli / İskanlı"
                ],
                default=["Deniz Manzaralı", "Akıllı Ev Sistemi", "Krediye Uygun", "Kat Mülkiyetli / İskanlı"]
            )

        with tab_lokasyon:
            col_lok1, col_lok2 = st.columns(2)
            lok_ulasim = col_lok1.selectbox(
                "🚆 Toplu Taşıma & Ulaşım",
                [
                    "Metro / Metrobüse Yürüme Mesafesinde",
                    "Otobüs & Minibüs Duraklarına Yakın",
                    "Marmaray & YHT İstasyonuna Yakın",
                    "E-5 & TEM Bağlantı Yollarına Yakın",
                    "Sahil Yolu & Vapur İskelesine Yakın",
                    "Merkezi Ulaşım Ağı Üzerinde"
                ]
            )
            lok_saglik = col_lok2.selectbox(
                "🏥 Sağlık & Hastane",
                [
                    "Devlet & Şehir Hastanesine Yakın",
                    "Özel Hastane & Tıp Merkezine Yakın",
                    "Aile Sağlığı Merkezi & Eczanelere Yakın",
                    "Sağlık Kuruluşları Bölgesinde"
                ]
            )

            col_lok3, col_lok4 = st.columns(2)
            lok_egitim = col_lok3.selectbox(
                "🏫 Eğitim & Okullar",
                [
                    "Kolej & Özel Okullara Yürüme Mesafesinde",
                    "İlkokul / Ortaokul / Liseye Yakın",
                    "Üniversite Kampüsüne Yakın",
                    "Nezih Eğitim Vadisi İçerisinde"
                ]
            )
            lok_sosyal = col_lok4.selectbox(
                "🛍️ Alışveriş & Sosyal Yaşam",
                [
                    "AVM & Yaşam Merkezine Yürüme Mesafesinde",
                    "Zincir Marketler & Çarşı İçinde",
                    "Kafe, Restoran & Sahil Şeridinde",
                    "Park & Yeşil Alan Yanı"
                ]
            )

        # --- ELEŞTİRİ 4 ÇÖZÜMÜ: PORTFÖY FOTOĞRAFLARI YÜKLEME & GÖRSEL AI DESTEĞİ ---
        with tab_fotolar:
            st.caption("📸 Portföyün salon, mutfak, manzara veya bina fotoğraflarını yükleyin. Yapay zeka görselleri inceleyip ilana özel mimari detaylar ekler:")
            yuklenen_fotolar = st.file_uploader(
                "Daire / Bina Fotoğrafları Yükle (JPG, PNG)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
            if yuklenen_fotolar:
                foto_kolonlari = st.columns(min(len(yuklenen_fotolar), 3))
                for idx, f in enumerate(yuklenen_fotolar[:3]):
                    foto_kolonlari[idx].image(f, caption=f"Fotoğraf {idx+1}", use_container_width=True)

        st.markdown("---")
        ekstra_not = st.text_input(
            "📝 Varsa Özel Ekstra Notlar (Opsiyonel)",
            placeholder="Örn: Franke ankastre set, İtalyan granit tezgah, otomatik panjur..."
        )

        ilan_uret_btn = st.button("✨ Profesyonel İlan Metni Oluştur", use_container_width=True, type="primary")

    with c_e2:
        st.subheader("📋 Üretilen İlan Taslağı")
        if ilan_uret_btn:
            if konum:
                # Seçilen özellikleri tek tek derle
                ozellik_maddeleri = [
                    f"**Oda Sayısı:** {oda_sayisi}",
                    f"**Metrekare:** {brut_m2} m² Brüt / {net_m2} m² Net",
                    f"**Bulunduğu Kat:** {bulundugu_kat}",
                    f"**Bina Yaşı:** {bina_yasi}",
                    f"**Isıtma:** {isitma_tipi}",
                    f"**Otopark & Asansör:** {otopark_durumu}",
                    f"**Banyo & Balkon:** {banyo_balkon}"
                ]
                if ekstra_donanimlar:
                    ozellik_maddeleri.append(f"**Öne Çıkan Donanımlar:** {', '.join(ekstra_donanimlar)}")

                # Lokasyon maddeleri
                lokasyon_maddeleri = [
                    f"**Ulaşım:** {lok_ulasim}",
                    f"**Sağlık Kurumları:** {lok_saglik}",
                    f"**Eğitim & Okullar:** {lok_egitim}",
                    f"**Sosyal Yaşam & Alışveriş:** {lok_sosyal}"
                ]

                fiyat_sayi = parse_tutar(fiyat_str)
                formatli_fiyat = format_tl(fiyat_sayi)

                # Canlı Gemini Modelini Dene
                gemini_model, err = initialize_gemini_model()
                gemini_success = False

                if gemini_model:
                    with st.spinner("Gemini Yapay Zekası ile HBG İNŞAAT & GAYRİMENKUL ilanı ve fotoğraflar inceleniyor..."):
                        try:
                            maddeler_text = "\n".join(ozellik_maddeleri)
                            lokasyon_text = "\n".join(lokasyon_maddeleri)
                            prompt = (
                                f"Sen HBG İNŞAAT & GAYRİMENKUL firmasının kurucusu, profesyonel gayrimenkul danışmanı ve müteahhitisin. "
                                f"Aşağıdaki detaylı özelliklere ve varsa yüklenen fotoğraflara göre Sahibinden, Hepsiemlak ve Zingat için etkileyici, akıcı, "
                                f"profesyonel bir {st.session_state.ilan_turu} ilan başlığı ve detaylı açıklaması hazırla:\n\n"
                                f"Firma: HBG İNŞAAT & GAYRİMENKUL\n"
                                f"İlan Kategorisi: {st.session_state.ilan_turu}\n"
                                f"Konum: {konum}\n"
                                f"Fiyat: {formatli_fiyat}\n"
                                f"Hedef Kitle: {hedef_kitle}\n"
                                f"Gayrimenkul Özellikleri:\n{maddeler_text}\n"
                                f"Lokasyon ve Çevre Avantajları:\n{lokasyon_text}\n"
                                f"Ekstra Notlar: {ekstra_not}\n\n"
                                f"ÖNEMLİ KURAL: Fiyatın yanına veya başlığa ASLA '/AY', '/Ay' veya 'AY' yazma, sadece fiyatı ({formatli_fiyat}) belirt.\n"
                                f"Lütfen dikkat çekici başlık, madde madde avantajlar, lokasyon artıları, fotoğraflardaki estetik ve malzeme kalitesi vurgusu ve HBG İNŞAAT & GAYRİMENKUL imzalı çağrı cümlesi içersin."
                            )
                            
                            # Çoklu modlu içerik (Metin + Yüklenen Fotoğraflar)
                            ai_inputs = [prompt]
                            if yuklenen_fotolar:
                                for uf in yuklenen_fotolar[:2]: # İlk 2 fotoğrafı modele besle
                                    pil_img = Image.open(uf)
                                    ai_inputs.append(pil_img)

                            res = gemini_model.generate_content(ai_inputs)
                            st.success(f"✅ HBG İNŞAAT & GAYRİMENKUL {st.session_state.ilan_turu} İlan Taslağı Başarıyla Hazırlandı:")
                            final_metin = res.text
                            gemini_success = True
                        except Exception:
                            gemini_success = False
                
                # Yedek profesyonel şablon motoru
                if not gemini_success:
                    yedek_ilan = generate_pro_listing(
                        konum,
                        ozellik_maddeleri,
                        fiyat_str,
                        hedef_kitle,
                        ekstra_not,
                        ilan_turu=st.session_state.ilan_turu,
                        lokasyon_maddeleri=lokasyon_maddeleri
                    )
                    final_metin = yedek_ilan

                st.success(f"✅ HBG İNŞAAT & GAYRİMENKUL {st.session_state.ilan_turu} İlan Taslağı Başarıyla Hazırlandı:")
                st.markdown(final_metin)

                # 📋 TEK TIKLA KOPYALAMA ALANI (Sahibinden / Hepsiemlak için)
                st.markdown("---")
                st.subheader("📋 Sahibinden & Hepsiemlak İlan Metni (Tek Tıkla Kopyala)")
                st.caption("Aşağıdaki kutunun sağ üstündeki kopyalama butonuna basarak tam metni doğrudan panoya alabilirsiniz:")
                st.code(final_metin, language="markdown")

                # 💬 WHATSAPP HIZLI MÜŞTERİ SUNUM FORMATI (DOĞRUDAN AÇIK VE GÖRÜNÜR)
                st.markdown("---")
                st.subheader("📲 WhatsApp Müşteri Sunum Formatı (Kısa & Vurucu)")
                st.caption("Müşterilerinize tek tıkla WhatsApp'tan gönderebileceğiniz özet metin:")
                wp_mesaj = f"""💎 *HBG İNŞAAT & GAYRİMENKUL PORTFÖY PAYLAŞIMI*

📍 *Konum:* {konum}
💰 *Fiyat:* {formatli_fiyat} ({st.session_state.ilan_turu})
🏠 *Tip:* {oda_sayisi} | {brut_m2} m² Brüt ({net_m2} m² Net)
🏢 *Kat / Yaş:* {bulundugu_kat} | {bina_yasi}
🔥 *Isıtma:* {isitma_tipi} | {otopark_durumu}
📍 *Lokasyon:* {lok_ulasim} | {lok_saglik}

✨ Detaylı sunum, yerinde keşif ve randevu için lütfen bizimle iletişime geçiniz.
🏢 *HBG İNŞAAT & GAYRİMENKUL*"""
                st.code(wp_mesaj, language="markdown")
            else:
                st.warning("Lütfen portföy konumunu girin.")
        else:
            st.info("Soldaki formu doldurup **'✨ Profesyonel İlan Metni Oluştur'** butonuna tıklayın. HBG İNŞAAT & GAYRİMENKUL kurumsal standartlarında profesyonel ilan metniniz anında hazırlanacaktır.")


# ==============================================================================
# 2. MODÜL: İNŞAAT Aİ (HBG İNŞAAT & GAYRİMENKUL)
# ==============================================================================
elif st.session_state.aktif_modul == "İNŞAAT Aİ":
    st.title("🏗️ HBG İNŞAAT & GAYRİMENKUL - İNŞAAT Aİ")
    st.caption("Şantiye Yönetim, Maliyet Takip ve ERP Bütçe Kontrol Sistemi")

    # Üst Kontrol Satırı: Proje Adı, Şantiye Durumu ve HEDEF PROJE BÜTÇESİ (3 Rakamda Bir Noktalı)
    ust_col1, ust_col2, ust_col3 = st.columns([2, 1, 2])

    with ust_col1:
        proje_adi = st.text_input("📁 Proje Adı", value="HBG Kartal Rezidans & Konut Projesi")
    
    with ust_col2:
        proje_durumu = st.selectbox(
            "📌 Şantiye Durumu",
            ["Temel & Kaba İnşaat", "Hafriyat & Zemin", "İnce İşler & Tesisat", "Ruhsat & Proje", "İskan / Teslim"]
        )

    with ust_col3:
        # HEDEF PROJE BÜTÇESİ (Kutunun içinde her 3 rakamda bir nokta: Örn. 20.000.000)
        girilen_butce = st.text_input(
            "🎯 Hedef Proje Bütçesi (TL)",
            value=st.session_state.hedef_butce_str,
            help="Her 3 rakamda bir nokta ile gösterilir (Örn: 20.000.000). Rakamı dilediğiniz gibi değiştirebilirsiniz."
        )
        toplam_butce = parse_tutar(girilen_butce)
        st.session_state.hedef_butce_str = format_sayi(toplam_butce)

    st.markdown("---")

    # Harcama Hesabı
    col_opt1, col_opt2 = st.columns([1, 1])
    with col_opt1:
        harcama_hesap_turu = st.radio(
            "⚙️ Harcanan Tutar Kaynağı",
            ["📊 Tablodan Otomatik Topla", "✏️ Toplam Harcananı Elle Değiştir"],
            horizontal=True
        )

    with col_opt2:
        if harcama_hesap_turu == "✏️ Toplam Harcananı Elle Değiştir":
            manuel_input_str = st.text_input(
                "💸 Toplam Harcanan Tutar (TL)",
                value=format_sayi(st.session_state.manuel_harcanan),
                help="Her 3 rakamda bir nokta formatında doğrudan harcanan tutarı girin."
            )
            st.session_state.manuel_harcanan = parse_tutar(manuel_input_str)
            toplam_harcanan = st.session_state.manuel_harcanan
        else:
            if not st.session_state.df_harcamalar.empty and "Tutar" in st.session_state.df_harcamalar.columns:
                toplam_harcanan = int(st.session_state.df_harcamalar["Tutar"].fillna(0).sum())
            else:
                toplam_harcanan = 0

    kalan_para = toplam_butce - toplam_harcanan
    kullanim_orani = (toplam_harcanan / toplam_butce * 100) if toplam_butce > 0 else 0

    # 4 Kolonlu Metrik Kartları (Tümü Noktalı)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 Hedef Bütçe", format_tl(toplam_butce))
    m2.metric("💸 Toplam Harcanan", format_tl(toplam_harcanan))

    if kalan_para >= 0:
        m3.metric("💼 Kalan Net Bütçe", format_tl(kalan_para), delta=f"+{format_tl(kalan_para)} Güvenli", delta_color="normal")
    else:
        m3.metric("⚠️ Bütçe Aşımı", format_tl(abs(kalan_para)), delta=f"-{format_tl(abs(kalan_para))} Aşım", delta_color="inverse")

    m4.metric("📈 Harcama Payı", f"% {kullanim_orani:.1f}")

    # Bütçe İlerleme Çubuğu
    st.progress(min(max(kullanim_orani / 100.0, 0.0), 1.0))

    st.markdown("---")

    # İki Kolonlu Yerleşim: Gider Ekleme Formu & Kategori Özeti
    sol_k, sag_k = st.columns([1, 1], gap="medium")

    with sol_k:
        st.subheader("➕ Yeni Gider Kaydı Ekle")
        with st.form("yeni_gider_formu", clear_on_submit=True):
            f_tarih = st.date_input("İşlem Tarihi", value=date.today())
            f_kalem = st.selectbox(
                "Gider Kategorisi",
                [
                    "Demir & Beton",
                    "Hafriyat & Zemin",
                    "Kaba İnşaat & İşçilik",
                    "İnce İşler & Tesisat",
                    "Ruhsat & Harçlar",
                    "Arsa / Tapu Masrafı",
                    "Şantiye Genel Giderleri",
                    "Diğer"
                ]
            )
            f_aciklama = st.text_input("Harcama Açıklaması", placeholder="Örn: 40 Ton 14'lük Nervürlü Demir Alımı")
            f_tutar_str = st.text_input(
                "Harcama Tutarı (TL)",
                value="500.000",
                help="Her 3 rakamda bir nokta kullanabilirsiniz (Örn: 1.250.000)."
            )
            
            kaydet = st.form_submit_button("💾 Harcamayı Listeye Kaydet", use_container_width=True)
            if kaydet:
                f_tutar = parse_tutar(f_tutar_str)
                if f_tutar > 0:
                    yeni_satir = pd.DataFrame([{
                        "Tarih": f_tarih.strftime("%d.%m.%Y"),
                        "Kategori": f_kalem,
                        "Açıklama": f_aciklama if f_aciklama else f"{f_kalem} Harcaması",
                        "Tutar": int(f_tutar)
                    }])
                    st.session_state.df_harcamalar = pd.concat([st.session_state.df_harcamalar, yeni_satir], ignore_index=True)
                    st.success(f"✅ {format_tl(f_tutar)} tutarındaki gider başarıyla eklendi!")
                    st.rerun()
                else:
                    st.warning("⚠️ Lütfen 0'dan büyük bir tutar girin.")

    with sag_k:
        st.subheader("📊 Kategori Dağılımı")
        if not st.session_state.df_harcamalar.empty and "Tutar" in st.session_state.df_harcamalar.columns and st.session_state.df_harcamalar["Tutar"].sum() > 0:
            grup = st.session_state.df_harcamalar.groupby("Kategori")["Tutar"].sum().reset_index()
            grup["Tutar (₺)"] = grup["Tutar"].apply(format_tl)
            grup["Pay (%)"] = grup["Tutar"].apply(lambda x: f"% {(x / toplam_harcanan * 100):.1f}" if toplam_harcanan > 0 else "% 0")
            
            st.dataframe(
                grup[["Kategori", "Tutar (₺)", "Pay (%)"]].rename(columns={"Kategori": "Gider Kategorisi"}),
                use_container_width=True,
                hide_index=True
            )
            st.bar_chart(st.session_state.df_harcamalar.groupby("Kategori")["Tutar"].sum(), color="#1f77b4")
        else:
            st.info("Henüz harcama kaydı eklenmedi.")

    st.markdown("---")

    # DÜZENLENEBİLİR VE NOKTALI BASİT HARCAMA TABLOSU
    st.subheader("📋 Harcama Listesi (Canlı Düzenlenebilir)")
    st.caption("💡 Tablodaki herhangi bir kutucuğa çift tıklayarak rakamları doğrudan değiştirebilir, silebilir veya yeni satır ekleyebilirsiniz.")

    if not st.session_state.df_harcamalar.empty:
        duzenlenen_df = st.data_editor(
            st.session_state.df_harcamalar,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Tarih": st.column_config.TextColumn("Tarih"),
                "Kategori": st.column_config.SelectboxColumn(
                    "Kategori",
                    options=[
                        "Demir & Beton",
                        "Hafriyat & Zemin",
                        "Kaba İnşaat & İşçilik",
                        "İnce İşler & Tesisat",
                        "Ruhsat & Harçlar",
                        "Arsa / Tapu Masrafı",
                        "Şantiye Genel Giderleri",
                        "Diğer"
                    ],
                    required=True
                ),
                "Açıklama": st.column_config.TextColumn("Açıklama"),
                "Tutar": st.column_config.NumberColumn(
                    "Tutar (TL)",
                    format="%d",
                    step=10000
                )
            },
            key="insaat_tablo_editor"
        )

        if not duzenlenen_df.equals(st.session_state.df_harcamalar):
            st.session_state.df_harcamalar = duzenlenen_df
            st.rerun()

        # En Anlaşılır Noktalı Özet Tablosu & Kategori Filtresi
        st.markdown("#### 🔍 Noktalı Net Tablo Özeti")
        
        # 5. KATEGORİYE GÖRE HIZLI FİLTRELEME
        mevcut_kategoriler = ["Tümü"] + list(st.session_state.df_harcamalar["Kategori"].unique()) if not st.session_state.df_harcamalar.empty else ["Tümü"]
        secilen_filtre = st.selectbox("📂 Tabloyu Kategoriye Göre Filtrele:", mevcut_kategoriler, index=0)

        df_gosterim = st.session_state.df_harcamalar
        if secilen_filtre != "Tümü":
            df_gosterim = df_gosterim[df_gosterim["Kategori"] == secilen_filtre]

        tablo_ozet = []
        for idx, row in df_gosterim.reset_index(drop=True).iterrows():
            t_val = row.get("Tutar", 0)
            pay_val = (t_val / toplam_harcanan * 100) if toplam_harcanan > 0 else 0
            tablo_ozet.append({
                "Sıra": idx + 1,
                "Tarih": row.get("Tarih", "-"),
                "Kategori": row.get("Kategori", "-"),
                "Açıklama": row.get("Açıklama", "-"),
                "Net Tutar (TL)": format_tl(t_val),
                "Bütçe Payı": f"% {pay_val:.1f}"
            })
        
        df_net = pd.DataFrame(tablo_ozet)
        st.dataframe(df_net, use_container_width=True, hide_index=True)

        col_b1, col_b2, col_b3 = st.columns([2, 1, 1])
        col_b1.caption(f"📌 Toplam **{len(tablo_ozet)}** adet kayıt. Harcanan: **{format_tl(toplam_harcanan)}**")
        
        if col_b2.button("🗑️ Tümünü Sıfırla", use_container_width=True):
            st.session_state.df_harcamalar = pd.DataFrame(columns=["Tarih", "Kategori", "Açıklama", "Tutar"])
            st.session_state.manuel_harcanan = 0
            st.rerun()

        csv_bytes = df_net.to_csv(index=False).encode('utf-8-sig')
        col_b3.download_button(
            "📥 CSV İndir",
            data=csv_bytes,
            file_name=f"insaat_giderleri_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.warning("Tabloda henüz kayıt yok.")
        if st.button("📋 Örnek Şantiye Verilerini Yükle"):
            st.session_state.df_harcamalar = pd.DataFrame([
                {"Tarih": "15.09.2026", "Kategori": "Hafriyat & Zemin", "Açıklama": "Temel kazısı ve hafriyat dökümü", "Tutar": 850000},
                {"Tarih": "20.09.2026", "Kategori": "Demir & Beton", "Açıklama": "50 Ton nervürlü inşaat demiri tedariği", "Tutar": 1450000},
                {"Tarih": "25.09.2026", "Kategori": "Demir & Beton", "Açıklama": "C35 Hazır beton dökümü (Temel 1. Etap)", "Tutar": 920000},
                {"Tarih": "28.09.2026", "Kategori": "Ruhsat & Harçlar", "Açıklama": "Belediye yapı denetim ve ruhsat harçları", "Tutar": 380000},
                {"Tarih": "02.10.2026", "Kategori": "Kaba İnşaat & İşçilik", "Açıklama": "Kalıpçı ve demirci taşeron 1. hakedişi", "Tutar": 650000}
            ])
            st.rerun()

    # Şantiye Şefi & Malzeme Danışmanı
    st.markdown("---")
    st.subheader("🔍 Yapay Zeka Şantiye Şefi & Malzeme Danışmanı")
    soru = st.text_input("Şantiye, malzeme, maliyet veya teknik bir konu sorun (Örn: C35 beton priz süresi, demir metraj hesabı)")
    if st.button("🔍 Teknik Analiz Yap", use_container_width=True):
        if soru:
            gemini_model, err = initialize_gemini_model()
            if gemini_model:
                with st.spinner("HBG İnşaat & Gayrimenkul teknik analiz yapılıyor..."):
                    try:
                        p = f"Bir inşaat mühendisi, şantiye şefi ve gayrimenkul uzmanı olarak detaylı ve profesyonel yanıtla. Soru: {soru}"
                        res = gemini_model.generate_content(p)
                        st.success("Analiz Sonucu:")
                        st.write(res.text)
                    except Exception as e:
                        st.warning(f"⚠️ Canlı AI Hatası: {e}")
            else:
                st.info("💡 Yapay zeka teknik analizi için arka planda geçerli bir Gemini API anahtarı gereklidir.")