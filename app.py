import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman - Harus dipanggil paling awal
st.set_page_config(page_title="Dashboard Level Stres Siswa", layout="wide", page_icon="🎓")

# 1. Memuat Data
@st.cache_data
def load_data():
    df = pd.read_csv('StressLevelDataset_Updated.csv')
    return df

df = load_data()

# 2. Desain Sidebar (Filter)
st.sidebar.header("Filter Data")

# Filter Gender
gender_options = ["All", "M", "F"]
selected_gender = st.sidebar.selectbox("Gender", gender_options)

# Filter Age Range
min_age, max_age = int(df['age'].min()), int(df['age'].max())
age_range = st.sidebar.slider("Rentang Umur (15-24)", min_value=min_age, max_value=max_age, value=(min_age, max_age))

# Filter Education Level
st.sidebar.markdown("Tingkat Pendidikan")
hs_checked = st.sidebar.checkbox("HS", value=True)
u_checked = st.sidebar.checkbox("U", value=True)

# Footer di Sidebar
st.sidebar.markdown("---")
st.sidebar.caption("Created with Streamlit | Data Source:\n Kaggle Dataset")

# 3. Menerapkan Filter pada DataFrame
filtered_df = df.copy()

if selected_gender != "All":
    filtered_df = filtered_df[filtered_df['sex'] == selected_gender]

filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]

edu_filter = []
if hs_checked: edu_filter.append("HS")
if u_checked: edu_filter.append("U")
filtered_df = filtered_df[filtered_df['education'].isin(edu_filter)]

# 4. Bagian Utama (Main Content)
st.title("🎓 Dashboard Level Stres Siswa (Umur 15-24)")
st.markdown("Dashboard interaktif yang menganalisis data demografik, faktor akademik, dan indikator stres dari siswa dan mahasiswa (usia 15-24 tahun).")

# Jika data kosong setelah difilter
if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
else:
    # --- Baris Atas: Key Metrics ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Responden", f"{len(filtered_df):,}")
        st.caption(f"Total {(len(filtered_df)/len(df))*100:.1f}%")

    with col2:
        most_common_stress_val = filtered_df['stress_level'].mode()[0]
        stress_mapping = {0: "Ringan (Low)", 1: "Sedang (Medium)", 2: "Tinggi (High)"}
        stress_label = stress_mapping.get(most_common_stress_val, str(most_common_stress_val))
        st.metric("Mayoritas Tingkat Stres", stress_label)

    with col3:
        if 'mental_health_history' in filtered_df.columns:
            mental_health_issues = filtered_df[filtered_df['mental_health_history'] == 1]
            if not mental_health_issues.empty:
                vul_gender = mental_health_issues['sex'].mode()[0]
                vul_age = mental_health_issues['age'].mode()[0]
                gender_label = "Perempuan" if vul_gender == 'F' else "Laki-laki"
                st.metric("Memiliki Riwayat Kesehatan Mental", f"{gender_label} (Usia {vul_age})")
            else:
                 st.metric("Memiliki Riwayat Kesehatan Mental", "N/A")
        else:
            st.metric("Kelompok Rentan", "N/A")

    st.markdown("---")

    # --- Baris Kedua: Visualisasi Demografi & Akademik ---
    st.markdown("##### Faktor Beban Belajar dan Kualitas Tidur berdasarkan Kelompok Usia")
    col_chart1, col_chart2, col_chart3 = st.columns([2, 1, 1])

    with col_chart1:
        age_grouped = filtered_df.groupby('age')[['study_load', 'sleep_quality']].mean().reset_index()
        age_melted = age_grouped.melt(id_vars='age', value_vars=['study_load', 'sleep_quality'], 
                                      var_name='Faktor', value_name='Rata-rata Rating')
        age_melted['Faktor'] = age_melted['Faktor'].map({'study_load': 'Study Load', 'sleep_quality': 'Sleep Quality'})
        
        fig1 = px.bar(age_melted, x='age', y='Rata-rata Rating', color='Faktor', barmode='group',
                      labels={'age': 'Age', 'Rata-rata Rating': 'Average Rating'},
                      color_discrete_map={'Study Load': '#D9534F', 'Sleep Quality': '#337AB7'}) 
        fig1.update_layout(xaxis=dict(tickmode='linear', tick0=15, dtick=1), margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        st.caption("Distribusi Jenis Kelamin")
        gender_counts = filtered_df['sex'].value_counts().reset_index()
        gender_counts.columns = ['sex', 'count']
        fig2 = px.pie(gender_counts, values='count', names='sex', hole=0.5,
                      color='sex', color_discrete_map={'M': '#337AB7', 'F': '#D9534F'})
        fig2.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=True, legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=0.9))
        st.plotly_chart(fig2, use_container_width=True)

    with col_chart3:
        st.caption("Tingkat Pendidikan")
        edu_counts = filtered_df['education'].value_counts().reset_index()
        edu_counts.columns = ['education', 'count']
        edu_counts['education'] = edu_counts['education'].map({'HS': 'High School (HS)', 'U': 'University (U)'})
        fig3 = px.pie(edu_counts, values='count', names='education', hole=0.5,
                      color='education', color_discrete_map={'High School (HS)': '#F0AD4E', 'University (U)': '#5CB85C'}) 
        fig3.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=True, legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=0.9))
        st.plotly_chart(fig3, use_container_width=True)

    # --- Baris Ketiga: Heatmaps ---
    st.markdown("##### Analisis Lanjutan: Kesehatan Mental & Korelasi Faktor")
    
    # Membagi baris ketiga menjadi dua kolom yang sama besar
    col_heat1, col_heat2 = st.columns(2)

    with col_heat1:
        st.caption("Riwayat Kesehatan Mental vs Beban Belajar")
        if 'mental_health_history' in filtered_df.columns and 'study_load' in filtered_df.columns:
            pivot_df = pd.crosstab(filtered_df['mental_health_history'], filtered_df['study_load'])
            pivot_df.index = pivot_df.index.map({0: 'Tidak Pernah', 1: 'Pernah'})
            
            fig_heat = px.imshow(pivot_df, 
                                 labels=dict(x="Study Load", y="History", color="Jumlah"),
                                 x=[f"Level {i}" for i in pivot_df.columns], 
                                 y=pivot_df.index,
                                 color_continuous_scale="YlOrRd", 
                                 aspect="auto") 
            fig_heat.update_layout(margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False) 
            fig_heat.update_xaxes(tickvals=[0, len(pivot_df.columns)//2, len(pivot_df.columns)-1], 
                                  ticktext=["Sangat Ringan", "Sedang", "Berat"])
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Kolom 'mental_health_history' atau 'study_load' tidak ditemukan.")

    with col_heat2:
        st.caption("Correlation Heatmap")
        
        # Mengecualikan kolom yang diminta
        cols_to_exclude = ['age', 'sex', 'education']
        
        # Mengambil variabel numerik dan menghapus kolom yang dikecualikan
        numeric_df = filtered_df.select_dtypes(include=['number'])
        cols_to_drop = [c for c in cols_to_exclude if c in numeric_df.columns]
        corr_data = numeric_df.drop(columns=cols_to_drop)
        
        if not corr_data.empty:
            # Menghitung korelasi Pearson
            corr_matrix = corr_data.corr()
            
            # Membuat heatmap korelasi menggunakan skala warna Red-Blue (RdBu_r)
            fig_corr = px.imshow(corr_matrix, 
                                 color_continuous_scale="RdBu_r", 
                                 zmin=-1, zmax=1, # Rentang korelasi standar: -1 (negatif) sampai 1 (positif)
                                 aspect="auto",
                                 labels=dict(color="Korelasi"))
            
            # Layout adjustment agar muat di kolom
            fig_corr.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Tidak cukup data numerik untuk menghitung korelasi.")

    # --- Baris Bawah: Dataset Preview ---
    st.markdown("##### Preview Dataset")
    cols_to_show = ['age', 'sex', 'education', 'study_load', 'sleep_quality', 'stress_level', 'mental_health_history']
    remaining_cols = [c for c in filtered_df.columns if c not in cols_to_show]
    display_df = filtered_df[cols_to_show + remaining_cols]
    
    st.dataframe(display_df, use_container_width=True)
