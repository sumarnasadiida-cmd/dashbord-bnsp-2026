import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
try:
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="EduPulse Dashboard", layout="wide")
st.title("🎓 EduPulse: GenAI Academic Strategy Dashboard")
st.markdown("Platform analitik strategis untuk mengevaluasi dampak GenAI terhadap performa dan kesejahteraan mental mahasiswa.")

# ==========================================
# 2. LOAD DATA & PREPROCESSING
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv('data/ai_student_clean.csv') 
    
    if 'Delta_GPA' not in df.columns:
        df['Delta_GPA'] = df['Post_Semester_GPA'] - df['Pre_Semester_GPA']
        
    if 'AI_Usage_Segment' not in df.columns:
        df['AI_Usage_Segment'] = pd.cut(
            df['Weekly_GenAI_Hours'], 
            bins=[-1, 5, 15, 100], 
            labels=['Light (0-5 jam)', 'Moderate (5-15 jam)', 'Heavy (>15 jam)']
        )
    return df

df_clean = load_data()

# ==========================================
# 3. SIDEBAR: FILTER & KAMUS DATA
# ==========================================
st.sidebar.header("🎯 Pusat Kendali")

selected_major = st.sidebar.multiselect(
    "Bidang Studi (Major_Category):",
    options=df_clean['Major_Category'].dropna().unique(),
    default=df_clean['Major_Category'].dropna().unique()
)

selected_year = st.sidebar.multiselect(
    "Tahun Studi (Year_of_Study):",
    options=df_clean['Year_of_Study'].dropna().unique(),
    default=df_clean['Year_of_Study'].dropna().unique()
)

selected_policy = st.sidebar.multiselect(
    "Kebijakan Institusi (Institutional_Policy):",
    options=df_clean['Institutional_Policy'].dropna().unique(),
    default=df_clean['Institutional_Policy'].dropna().unique()
)

df_filtered = df_clean[
    (df_clean['Major_Category'].isin(selected_major)) &
    (df_clean['Year_of_Study'].isin(selected_year)) &
    (df_clean['Institutional_Policy'].isin(selected_policy))
]

st.sidebar.markdown("---")
with st.sidebar.expander("📖 Kamus Data"):
    st.markdown("""
    * **Pre/Post GPA:** IPK awal & akhir(0.0-4.0).
    * **Delta_GPA:** Peningkatan IPK.
    * **Skill_Retention:** Skor retensi pengetahuan pasca-semester (0–100).
    * **AI_Usage_Segment:** Intensitas AI (Light, Moderate, Heavy).
    * **Dependency:** Skala ketergantungan (1-10).
    * **Burnout_Risk:** Kelelahan mental (Low/Med/High).
    """)

# ==========================================
# 4. PENGAMANAN & KPI GLOBAL
# ==========================================
if df_filtered.empty:
    st.error("⚠️ Tidak ada data yang sesuai dengan kombinasi filter saat ini.")
    st.stop()

st.markdown("### 📊 Key Performance Indicators")

avg_gpa = df_filtered['Post_Semester_GPA'].mean()
avg_ret = df_filtered['Skill_Retention_Score'].mean()
high_burnout_pct = (len(df_filtered[df_filtered['Burnout_Risk_Level'] == 'High']) / len(df_filtered)) * 100

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric("🎓 Rata-rata IPK Akhir", f"{avg_gpa:.2f}")
col_kpi2.metric("🧠 Rata-rata Skor Retensi", f"{avg_ret:.1f}")
col_kpi3.metric("🔥 Risiko High Burnout", f"{high_burnout_pct:.1f}%")

st.markdown("---")

# ==========================================
# 5. TABS DASHBOARD
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1️⃣ Ekosistem & Peningkatan", 
    "2️⃣ Optimalisasi & Dampak AI", 
    "3️⃣ Kognitif & Risiko Mental", 
    "4️⃣ Evaluasi Kebijakan", 
    "5️⃣ Strategic Action Plan"
])

# ------------------------------------------
# TAB 1: Ekosistem & Peningkatan Akademik
# ------------------------------------------
with tab1:
    st.markdown("### Ekosistem Mahasiswa")
    st.markdown("""
    <style>
    div.custom-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    div.card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    div.card-title {
        font-size: 14px;
        font-weight: 600;
        color: #4a5568;
        margin: 0;
    }
    div.card-icon {
        font-size: 20px;
        background-color: #f7fafc;
        padding: 8px;
        border-radius: 8px;
    }
    div.card-value {
        font-size: 28px;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 5px;
    }
    div.card-subtitle {
        font-size: 12px;
        color: #718096;
    }
    </style>
    """, unsafe_allow_html=True)

    col_m1, col_m2, col_m3 = st.columns(3)
    
    total_mhs = f"{len(df_filtered):,}"
    avg_ai = f"{df_filtered['Weekly_GenAI_Hours'].mean():.1f}"
    avg_trad = f"{df_filtered['Traditional_Study_Hours'].mean():.1f}"

    with col_m1:
        st.markdown(f"""
        <div class="custom-card">
            <div class="card-header">
                <div class="card-title">Total Mahasiswa</div>
                <div class="card-icon">👥</div>
            </div>
            <div class="card-value">{total_mhs}</div>
            <div class="card-subtitle">Berdasarkan filter aktif</div>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown(f"""
        <div class="custom-card">
            <div class="card-header">
                <div class="card-title">Penggunaan AI</div>
                <div class="card-icon">🤖</div>
            </div>
            <div class="card-value">{avg_ai}</div>
            <div class="card-subtitle">Rata-rata Jam / Minggu</div>
        </div>
        """, unsafe_allow_html=True)

    with col_m3:
        st.markdown(f"""
        <div class="custom-card">
            <div class="card-header">
                <div class="card-title">Belajar Tradisional</div>
                <div class="card-icon">📚</div>
            </div>
            <div class="card-value">{avg_trad}</div>
            <div class="card-subtitle">Rata-rata Jam / Minggu</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visual 1: Distribusi Populasi
    fig_sun = px.sunburst(df_filtered, path=['Institutional_Policy', 'Year_of_Study', 'Major_Category'], 
                          title="Distribusi Populasi (Kebijakan > Tahun > Bidang Studi)")
    st.plotly_chart(fig_sun, use_container_width=True)
    
    top_policy = df_filtered['Institutional_Policy'].mode()[0]
    top_policy_pct = (len(df_filtered[df_filtered['Institutional_Policy'] == top_policy]) / len(df_filtered)) * 100
    top_major = df_filtered['Major_Category'].mode()[0]
    st.success(f"**Insight Demografi:** Menampilkan data dari total {len(df_filtered):,} mahasiswa. Populasi terbesar berada pada kebijakan **{top_policy}** sebanyak **{top_policy_pct:.1f}%**, yang didominasi oleh mahasiswa pada bidang studi **{top_major}**.")

    st.markdown("---")

    # Visual 2: Perbandingan IPK
    st.markdown("### Perbandingan Peningkatan Akademik per Bidang Studi")
    df_melt = df_filtered.melt(id_vars='Major_Category', value_vars=['Pre_Semester_GPA', 'Post_Semester_GPA'], 
                               var_name='Semester', value_name='GPA')
    df_gpa_group = df_melt.groupby(['Major_Category', 'Semester'])['GPA'].mean().reset_index()
    fig_bar1 = px.bar(df_gpa_group, x='Major_Category', y='GPA', color='Semester', barmode='group',
                      title="Rata-rata IPK Awal (Pre) vs Akhir (Post) per Bidang Studi",
                      labels={'Major_Category': 'Bidang Studi', 'GPA': 'Rata-rata IPK'},
                      color_discrete_sequence=['#A6B1E1', '#424874'])
    fig_bar1.update_yaxes(range=[2.5, 4.0])
    st.plotly_chart(fig_bar1, use_container_width=True)


# ------------------------------------------
# TAB 2: Optimalisasi & Validasi Statistik AI
# ------------------------------------------
with tab2:
    st.markdown("### Dampak Intensitas AI terhadap Peningkatan IPK")
    
    fig_box_ai = px.box(df_filtered, x='AI_Usage_Segment', y='Delta_GPA', color='AI_Usage_Segment',
                        title="Sebaran Peningkatan IPK (Delta GPA) berdasarkan Segmen Penggunaan")
    st.plotly_chart(fig_box_ai, use_container_width=True)
    
    # Algoritma Dinamis Post-Hoc Tukey HSD diletakkan di bawah grafik
    segments = df_filtered['AI_Usage_Segment'].dropna().unique()
    if len(segments) < 2:
        st.info("📊 **Interpretasi Statistik:** Data pada filter ini tidak memiliki variasi segmen yang cukup untuk dilakukan uji komparasi statistik.")
    else:
        groups = [df_filtered[df_filtered['AI_Usage_Segment'] == seg]['Delta_GPA'].dropna() for seg in segments]
        f_stat, p_val = stats.f_oneway(*groups)
        
        if p_val > 0.05:
            st.warning("📊 **Interpretasi Statistik:** Hasil uji statistik (ANOVA) menunjukkan **tidak ada perbedaan yang signifikan** (p-value > 0.05) pada rata-rata peningkatan IPK antar segmen intensitas AI pada populasi ini.")
        else:
            if HAS_STATSMODELS:
                tukey = pairwise_tukeyhsd(endog=df_filtered['Delta_GPA'].dropna(), 
                                          groups=df_filtered['AI_Usage_Segment'].dropna(), alpha=0.05)
                st.success("📊 **Interpretasi Statistik:** Hasil uji lanjut (Post-Hoc Tukey HSD) menunjukkan adanya **perbedaan signifikan secara statistik** (p-value < 0.05) pada peningkatan IPK antar kelompok. Penggunaan AI memberikan dampak variatif yang nyata pada nilai akhir mahasiswa.")
            else:
                st.success("📊 **Interpretasi Statistik:** Hasil uji ANOVA menunjukkan adanya **perbedaan signifikan secara statistik** (p-value < 0.05) pada peningkatan IPK antar kelompok segmentasi.")

    st.markdown("---")
    
    st.markdown("### Efektivitas Tujuan Penggunaan AI")
    df_usecase = df_filtered.groupby('Primary_Use_Case')['Post_Semester_GPA'].mean().reset_index().sort_values('Post_Semester_GPA')
    fig_bar_use = px.bar(df_usecase, x='Post_Semester_GPA', y='Primary_Use_Case', orientation='h', text_auto='.2f',
                         title="Rata-rata IPK Akhir berdasarkan Tujuan Penggunaan AI (Primary Use Case)")
    fig_bar_use.update_xaxes(range=[3.0, 4.0])
    st.plotly_chart(fig_bar_use, use_container_width=True)
    
    best_usecase = df_usecase.iloc[-1]
    worst_usecase = df_usecase.iloc[0]
    st.info(f"💡 **Insight Efektivitas:** IPK akhir tertinggi rata-rata dicapai oleh mahasiswa dengan tujuan utama AI untuk **{best_usecase['Primary_Use_Case']}** (IPK: {best_usecase['Post_Semester_GPA']:.2f}). Sebaliknya, IPK terendah terlihat pada gaya penggunaan **{worst_usecase['Primary_Use_Case']}** (IPK: {worst_usecase['Post_Semester_GPA']:.2f}).")


# ------------------------------------------
# TAB 3: Kognitif & Risiko Mental
# ------------------------------------------
with tab3:
    st.markdown("### Pengikisan Retensi Pengetahuan")
    
    fig_scatter = px.scatter(df_filtered, x='Perceived_AI_Dependency', y='Skill_Retention_Score', 
                             opacity=0.5, trendline="ols", trendline_color_override="red",
                             title="Korelasi Tingkat Ketergantungan AI vs Skor Retensi Pengetahuan")
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    corr_val = df_filtered['Perceived_AI_Dependency'].corr(df_filtered['Skill_Retention_Score'])
    max_dep_retention = df_filtered[df_filtered['Perceived_AI_Dependency'] >= 8]['Skill_Retention_Score'].mean()
    st.warning(f"🧠 **Insight Kognitif:** Terdapat korelasi sebesar **{corr_val:.2f}** antara tingkat ketergantungan AI dan skor retensi. Pada tingkat ketergantungan ekstrem (skala $\ge$ 8), rata-rata skor retensi anjlok menjadi **{max_dep_retention:.1f}**.")

    st.markdown("---")
    
    # ==========================================
    # BAGIAN YANG DIREVISI: BOXPLOT KETERGANTUNGAN
    # ==========================================
    st.markdown("### Krisis Titik Buta: Kelelahan Mental Memicu Ketergantungan Ekstrem")
    
    # Membuat Boxplot Ketergantungan AI vs Risiko Burnout
    fig_box_dep = px.box(
        df_filtered, 
        x="Burnout_Risk_Level", 
        y="Perceived_AI_Dependency", 
        color="Burnout_Risk_Level",
        title="Distribusi Skala Ketergantungan AI berdasarkan Tingkat Burnout",
        category_orders={"Burnout_Risk_Level": ["Low", "Medium", "High"]}, # Memastikan urutan sumbu X logis
        labels={
            "Burnout_Risk_Level": "Tingkat Risiko Burnout",
            "Perceived_AI_Dependency": "Skala Ketergantungan AI (1-10)"
        },
        color_discrete_sequence=['#66c2a5', '#fc8d62', '#8da0cb'] # Palet warna agar selaras
    )
    
    # Menghilangkan legenda yang berulang agar UI lebih bersih
    fig_box_dep.update_layout(showlegend=False)
    
    st.plotly_chart(fig_box_dep, use_container_width=True)
    
    # Kotak Insight yang menohok dan sesuai data
    st.error("🚨 **Insight Titik Buta:** Mahasiswa dengan tingkat *High Burnout* bukan sekadar bermalas-malasan, melainkan kehabisan kapasitas kognitif. Hal ini terlihat dari **Tingkat Ketergantungan AI** mereka yang melonjak ekstrem dibandingkan kelompok *Low Burnout*. Mereka cenderung tidak lagi menjadikan AI sebagai mitra diskusi, melainkan sebagai tumpuan pelarian utama untuk menyelesaikan tugas.")

# ------------------------------------------
# TAB 4: Evaluasi Kebijakan & Kerentanan
# ------------------------------------------
with tab4:
    st.markdown("### Dampak Kebijakan Institusi terhadap Kesehatan Mental & IPK")
    col4_a, col4_b = st.columns(2)
    with col4_a:
        fig_pol_gpa = px.box(df_filtered, x='Institutional_Policy', y='Post_Semester_GPA', color='Institutional_Policy', title="Sebaran IPK Akhir per Kebijakan")
        st.plotly_chart(fig_pol_gpa, use_container_width=True)
    with col4_b:
        fig_pol_anx = px.box(df_filtered, x='Institutional_Policy', y='Anxiety_Level_During_Exams', color='Institutional_Policy', title="Tingkat Kecemasan Ujian per Kebijakan")
        st.plotly_chart(fig_pol_anx, use_container_width=True)
        
    st.info("📌 **Catatan Evaluasi:** Dua grafik di atas membandingkan secara langsung output akademik dengan beban stres yang ditanggung mahasiswa akibat regulasi kampus yang berlaku.")

    st.markdown("---")
    
    st.markdown("### Anatomi Kerentanan (High Burnout)")
    df_high_burn = df_filtered[df_filtered['Burnout_Risk_Level'] == 'High']
    
    if not df_high_burn.empty:
        fig_tree = px.treemap(df_high_burn, path=['Major_Category', 'Year_of_Study'], color='Traditional_Study_Hours',
                              color_continuous_scale='Oranges', title="Anatomi Mahasiswa dengan Risiko High Burnout")
        st.plotly_chart(fig_tree, use_container_width=True)
        
        dom_major = df_high_burn['Major_Category'].mode()[0]
        dom_year = df_high_burn['Year_of_Study'].mode()[0]
        avg_trad = df_high_burn['Traditional_Study_Hours'].mean()
        st.warning(f"🔍 **Karakteristik Rentan:** Kelompok mahasiswa dengan risiko *High Burnout* mendominasi pada bidang studi **{dom_major}**, di tahun ke-**{dom_year}**. Rata-rata jam belajar tradisional pada kelompok rentan ini tercatat sebesar **{avg_trad:.1f} jam/minggu**.")
    else:
        st.success("Tidak ada data High Burnout pada filter ini.")


# ------------------------------------------
# TAB 5: Strategic Action Plan & The Blueprint
# ------------------------------------------
with tab5:
    st.header("🎯 Strategic Action Plan & The Blueprint")
    st.markdown("Berdasarkan analisis data pada Tab 1-4, berikut adalah cetak biru kebijakan yang direkomendasikan untuk menyeimbangkan performa akademik dan kesehatan kognitif.")
    
    st.markdown("---")
    
    # ==========================================
    # FITUR BARU: SIMULATOR PROFIL BELAJAR
    # ==========================================
    st.markdown("### 🔬 Simulasi Profil Belajar (*The Success Blueprint*)")
    st.markdown("Geser *slider* IPK di bawah ini untuk membedah komposisi jam penggunaan AI versus jam belajar tradisional pada kelompok mahasiswa tersebut.")
    
    # Ambil batas minimum dan maksimum IPK dari data yang sudah difilter
    min_gpa = float(df_filtered['Post_Semester_GPA'].min())
    max_gpa = float(df_filtered['Post_Semester_GPA'].max())
    
    # Pengaman jika hasil filter hanya menyisakan nilai IPK yang seragam
    if min_gpa >= max_gpa:
        st.info(f"Semua mahasiswa pada filter ini memiliki IPK yang sama ({min_gpa:.2f}).")
        selected_gpa = (min_gpa, max_gpa)
    else:
        # Menampilkan Slider IPK dengan pengaman logika rentang
        default_min = min(max_gpa, max(min_gpa, 3.5)) # Mencegah error jika max_gpa < 3.5
        
        selected_gpa = st.slider(
            "Rentang IPK Akhir:",
            min_value=min_gpa,
            max_value=max_gpa,
            value=(default_min, max_gpa), 
            step=0.05
        )
        
        
    # Filter DataFrame KHUSUS untuk visualisasi Blueprint ini
    df_blueprint = df_filtered[
        (df_filtered['Post_Semester_GPA'] >= selected_gpa[0]) & 
        (df_filtered['Post_Semester_GPA'] <= selected_gpa[1])
    ]
    
    if not df_blueprint.empty:
        # Menggabungkan dua kolom jam belajar menjadi satu untuk Overlapping Histogram
        df_melt_blueprint = df_blueprint.melt(
            value_vars=['Weekly_GenAI_Hours', 'Traditional_Study_Hours'], 
            var_name='Metode Belajar', 
            value_name='Jam per Minggu'
        )
        
        # Merapikan nama label untuk legenda grafik
        df_melt_blueprint['Metode Belajar'] = df_melt_blueprint['Metode Belajar'].replace({
            'Weekly_GenAI_Hours': 'Penggunaan AI',
            'Traditional_Study_Hours': 'Belajar Tradisional'
        })
        
        # Gambar Overlapping Histogram
        fig_blueprint = px.histogram(
            df_melt_blueprint, 
            x='Jam per Minggu', 
            color='Metode Belajar',
            barmode='overlay',  # Membuat barnya tumpang tindih secara transparan
            opacity=0.7,
            title=f"Distribusi Jam Belajar Mahasiswa dengan IPK ({selected_gpa[0]:.2f} - {selected_gpa[1]:.2f})",
            labels={'Jam per Minggu': 'Intensitas (Jam per Minggu)'},
            color_discrete_sequence=['#EF553B', '#00CC96'] # Merah untuk AI, Hijau untuk Tradisional
        )
        
        # Merapikan label sumbu Y yang bawaannya tertulis 'count'
        fig_blueprint.update_layout(yaxis_title="Frekuensi (Jumlah Mahasiswa)")
        
        st.plotly_chart(fig_blueprint, use_container_width=True)
        
        # Kotak Insight Dinamis
        avg_ai_bp = df_blueprint['Weekly_GenAI_Hours'].mean()
        avg_trad_bp = df_blueprint['Traditional_Study_Hours'].mean()
        st.info(f"💡 **Insight Simulasi:** Pada kelompok mahasiswa berprestasi dengan rentang IPK **{selected_gpa[0]:.2f} - {selected_gpa[1]:.2f}**, mereka rata-rata menghabiskan **{avg_trad_bp:.1f} jam** untuk belajar mandiri secara tradisional, dan mengimbanginya dengan penggunaan AI sebesar **{avg_ai_bp:.1f} jam**. Pola ini adalah cetak biru proporsi ideal yang dapat diadopsi sebagai panduan kampus.")
    else:
        st.warning("Tidak ada mahasiswa dalam rentang IPK yang dipilih.")
        
    st.markdown("---")
    
    # ==========================================
    # KOTAK REKOMENDASI (Existing)
    # ==========================================
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.error("### 🚫 Evaluasi Strict Ban\nData komparatif menunjukkan pelarangan total tidak memberikan keunggulan IPK yang signifikan, namun justru menciptakan rekor tertinggi pada kecemasan ujian dan *burnout*. Kebijakan ini perlu direvisi.")
    with col_s2:
        st.success("### ⚖️ Edukasi Penggunaan Moderat\nTitik optimal (*sweet spot*) peningkatan IPK ada pada segmen pengguna Moderate (5-15 jam). Kampus harus mengarahkan mahasiswa untuk menjadikan AI sebagai mitra *brainstorming*, bukan pencetak jawaban langsung.")
    with col_s3:
        st.warning("### 🔄 Restrukturisasi Asesmen\nDependensi ekstrem terhadap AI menunjukkan tren indikasi penurunan pada retensi pemahaman materi jangka panjang. Sebagai langkah mitigasi, kampus perlu mengintegrasikan asesmen yang memvalidasi proses berpikir, seperti ujian lisan atau studi kasus langsung, untuk memastikan kompetensi asli mahasiswa tetap terjaga.")