import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from handcalcs.decorator import handcalc
import handcalcs
from math import pi, sqrt, ceil, sin,cos, degrees, radians,atan


with st.sidebar:
    # INFORMASI PROYEK
    st.markdown("# INFORMASI PROYEK")
    project = st.text_input("Nama Proyek",
                            value="-")
    document_code = st.text_input("Kode Dokumen",
                                  help="Apabila tidak ada inputkan tanda - ",
                                  value="-")
    date = st.date_input("Tanggal Dibuat",
                         help="Masukan Tanggal")
    struktur = st.text_input("Struktur",
                             help="Masukan Type Struktur",
                             value="-")
    st.markdown("# PARAMETER")
    # INPUT PARAMETER
    beban_hidup = st.number_input("Beban Hidup untuk Tekanan Tanah Surcharge, $q_{ll}$ **(kN/m2)**",
                                  value=9)
    wall_width = st.number_input("Lebar Dinding, $B_{wall}$ **(m)**",
                                 value=16.5)
    wall_height = st.number_input("Tinggi Dinding, $H_{wall}$ **(m)**",
                                  value=2.75)
    wall_length = st.number_input("Panjang Wingwall, $L_{wall}$ **(m)**",
                                  value=2)
    soil_density = st.number_input("Berat Jenis Tanah, $\gamma_{soil}$ **(kN/m3)**",
                                   value=18)    
    shear_angle = st.number_input("Sudut Geser Antara Urukan dan Dinding, $\delta$ **(deg)**",
                                  help="Lihat Tabel 6",
                                  value=24)
    angle_of_the_backfill_to_the_horizontal_line = st.number_input("Sudut Pada Dinding Belakang Terhadap Garis Horizontal, $\\beta$ dan $i$ **(deg)**",
                                                                   help="Lihat Gambar 1",
                                                                   value=0)
    sudut_kemiringa_dinding_kepala_jembatan_terhadap_bidang_vertikal=st.number_input("Kemiringan Dinding Kepala Jembatan Terhadap Bidang Vertikal, $\\beta_a$ **(deg)**",
                                                                                     help="Lihat Gambar 2",
                                                                                     value=0)
    shear_angle_between_the_backfill_and_the_wall = st.number_input("Sudut Pada Urukan Terhadap Garis Horizontal, $\\theta$ **(deg)**",
                                                                    help="Lihat Gambar 1",
                                                                    value=90)
    effective_shear_angle_of_the_soil = st.number_input("Sudut Geser Efektif Tanah, $\phi_f$ **(deg)**",
                                                        value=30)
    koefisien_percepatan_vertical = st.number_input("Koefisien Percepatan Vertical",
                                                    help="Umumnya diambil =0",
                                                    value=0)
    percepatan_puncak_di_permukaan = st.number_input("Perepatan Puncan di Permukaan, $A_s$",
                                                     value=0.31
                                                      )
    # SLIDER PER KETINGGIN
    st.markdown("# INTERPOLASI BEBAN")
    interpolasi_per_ketinggian = st.number_input("Munculkan Beban Pada Ketinggian ?",
                                                 value=0.1)
# PARAMETER UNTUK ANALISIS
q_ll = beban_hidup
B_wall = wall_width
H_wall = wall_height
L_wall = wall_length
gamma_soil = soil_density
delta = radians(shear_angle)
beta = radians(angle_of_the_backfill_to_the_horizontal_line)
i = radians(angle_of_the_backfill_to_the_horizontal_line)
beta_a = radians(sudut_kemiringa_dinding_kepala_jembatan_terhadap_bidang_vertikal)
theta = radians(shear_angle_between_the_backfill_and_the_wall)
phi_f = radians(effective_shear_angle_of_the_soil)
A_s = percepatan_puncak_di_permukaan
k_v = koefisien_percepatan_vertical


@handcalc(override="long",precision=2)
def gamma_koefisien_tanah_aktif():
    Gamma = (1+sqrt((sin(phi_f+delta)*sin(phi_f-beta))/(sin(theta-delta)*sin(phi_f+beta))))**2
    return Gamma
Gamma_latex,Gamma=gamma_koefisien_tanah_aktif()

@handcalc(override="long",precision=2)
def koefisien_tanah_aktif():
    k_a = sin(theta+phi_f)**2/(Gamma*((sin(theta)**2))*sin(theta-delta))
    return k_a
k_a_latex,k_a=koefisien_tanah_aktif()

@handcalc(override="long",precision=2)
def tekanan_tanah_aktif():
    P_a = k_a*gamma_soil*H_wall*B_wall
    return P_a
P_a_latex,P_a=tekanan_tanah_aktif()

@handcalc(override="long",precision=2)
def tekanan_tanah_surcharge():
    P_s = k_a*q_ll*B_wall
    return P_s
P_s_latex,P_s=tekanan_tanah_surcharge()

@handcalc(override="long",precision=2)
def koefisien_perceptan_horizontal():
    k_h = 0.5*A_s
    return k_h
k_h_latex,k_h=koefisien_perceptan_horizontal()

@handcalc(override="long",precision=2)
def theta_gempa():
    theta_eq = (atan(k_h/(1-k_v)))
    return theta_eq
theta_eq_latex,theta_eq=theta_gempa()


@handcalc(override="long",precision=2)
def tekanan_tanah_gempa():
    k_ae = cos(phi_f-theta_eq-beta_a)**2/(cos(theta_eq)*cos(beta_a)**2*cos(delta+theta_eq+beta_a))*(1+sqrt((sin(phi_f+delta)*sin(phi_f-theta_eq-i))/(cos(beta_a+delta+theta_eq)*cos(i-beta_a))))**-2
    return k_ae
k_ae_latex,k_ae =tekanan_tanah_gempa()

@handcalc(override="long",precision=2)
def tekanan_tanah_gempa():
    P_ae = (1/2)*gamma_soil*H_wall**2*(1-k_v)*k_ae*B_wall
    return P_ae
P_ae_latex,P_ae = tekanan_tanah_gempa()

def linear_interpolation(x0, y0, x1, y1, x):
    """
    Melakukan interpolasi linier antara dua titik (x0, y0) dan (x1, y1) untuk menemukan nilai y pada x.
    
    Args:
    x0 (float): Nilai x dari titik pertama.
    y0 (float): Nilai y dari titik pertama.
    x1 (float): Nilai x dari titik kedua.
    y1 (float): Nilai y dari titik kedua.
    x (float): Nilai x yang ingin diinterpolasi.
    
    Returns:
    float: Nilai y yang diinterpolasi pada x.
    """
    if x0 == x1:
        raise ValueError("x0 dan x1 tidak boleh sama (mencegah pembagian dengan nol)")
    
    # Rumus interpolasi linier
    y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return y

# MARKDOWN
MD_PARAMETER = f"""
- Beban hidup, $q_{{ll}} = {q_ll} \ kN/m^{{2}}$
- Lebar dinding, $B_{{wall}} = {B_wall} \ m$
- Tinggi dinding, $H_{{wall}} = {H_wall} \ m$
- Panjang timbunan, $L_{{wall}} = {L_wall} \ m$
- Berat jenis tanah, $\gamma_{{soil}} = {gamma_soil} \ kN/m^{{2}}$
- Sudut geser antara urukan dan dinding, $\delta = {round(delta,ndigits=3)} \ rad$
- Sudut pada urukan terhadap garis horizontal, $\\beta = {round(beta,ndigits=3)} \ rad$
- Sudut kemiringan timbunan, $i = {round(i,ndigits=3)} \ rad$
- Kemiringan dinding kepala jembatan terhadap bidang vertikal, $\\beta_a = {round(beta_a,ndigits=3)} \ rad$
- Sudut pada dinding belakang terhadap garis horizontal, $\\theta = {round(theta,ndigits=3)} \ rad$
- Sudut geser efektif tanah, $\phi_f = {round(phi_f,ndigits=3)} \ rad$
- Percepatan puncak di Permukaan, $A_s = {round(A_s,ndigits=3)}$
- Koefisien percepatan vertical, $k_v = {k_v}$ 
"""

# HALAMAN WEB
st.title("TIA Engineering")
st.subheader("Aplikasi Analisis Tekanan Tanah Lateral Pada Dinding Penahan Tanah / Abutmen")
st.markdown("Analisis dihitung berdasarkan Peraturan/Code dan Referensi Sebagai Berikut :")
st.markdown("""
            - **SNI 1725:2016** tentang Pembebanan Untuk Jembatan
            - **SNI 2833:2016** tentang Perencanaan Jembatan Terhadap Beban Gempa
            """)
st.markdown("Perhitungan beban yang dilakukan hanya menganalisis beban sebagai brikut:")
st.markdown("""
            - **Tekanan Tanah Aktif, $P_a$**
            - **Tekanan Tanah Akibat Shurcharge, $P_s$**
            - **Tekanan Tanah Akibat Gempa, $P_{ae}$**
            """)
st.divider()
st.markdown("# Informasi Proyek")
col_C1,col_C2=st.columns(2)
with col_C1:
    st.markdown(f"**Proyek : {project}**")
    st.markdown(f"**Struktur : {struktur}**")
with col_C2:
    st.markdown(f"**Kode Dokumen : {document_code}**")
    st.markdown(f"**Tanggal : {date}**")

st.markdown("# Parameter")
col_A1,col_A2=st.columns(2)
with col_A1:
    st.image('notasi_perhitungan_tekanan_tanah_coulomb.png',
            caption="Gambar 1 : Notasi untuk perhitungan tekanan tanah aktif Coulomb")
with col_A2:
    st.image('notasi_perhitungan_tekanan_tanah_gempa.png',
            caption="Gambar 2 : Diagram keseimbangan aya pada dinding penahan tanah/kepala jembatan")
st.image('tabel_sudud_geser_tanah.png',
            caption="Gambar 3 : Tabel sudut geser tanah")
st.markdown(MD_PARAMETER)
st.markdown("# Tekanan Tanah Aktif, $P_a$")
st.markdown("## Koefisien Tekanan Tanah Aktif, $k_a$")
st.markdown("Nilai-nilai untuk koefisien tekanan tanah lateral aktif dapat diambil sebagai berikut:")
st.latex(k_a_latex)
st.markdown("Dengan:")
st.latex(Gamma_latex)
st.markdown("## Beban Tekanan Tanah Lateral")
st.markdown("Tekanan tanah lateral harus diasumsikan linier sebanding dengan kedalaman tanah sebagai berikut :")
st.latex(P_a_latex)
st.markdown(f"Dari hasil analisis di dapat nilai tekanan tanah lateral aktif adalah ${round(P_a,ndigits=3)} kN/m$ di bawah ini di tampilkan diagram beban tekanan tanah lateral aktif $P_a$ dalam variasi ketinggian dinding")

x_tinggi_wall=np.arange(0,1.1,0.1)*H_wall
y_P_a=linear_interpolation(0,P_a,H_wall,0,x_tinggi_wall)

df_tekanan_tanah_aktif=pd.DataFrame({
    "Tinggi Wall (m)":x_tinggi_wall,
    "Tekanan Tanah (kN/m)":y_P_a
    },index=None)

fig_1 = px.area(df_tekanan_tanah_aktif,
              x="Tekanan Tanah (kN/m)",
              y="Tinggi Wall (m)",
              range_x=[0,P_a],
              range_y=[0,H_wall],
              markers=True,
              )
#fig.update_layout(
    #xaxis = dict(range=[0,P_a]),
    #yaxis = dict(range=[0,H_wall]),
#)
st.plotly_chart(fig_1,theme="streamlit",use_container_width=True)

P_a_inter=linear_interpolation(0,P_a,H_wall,0,interpolasi_per_ketinggian)
st.markdown(f"Untuk beban $P_a$ pada ketinggian {interpolasi_per_ketinggian} m adalah sebesar = ${round(P_a_inter)} kN/m$")

st.markdown("# Tekanan Tanah Surcharge, $P_s$")
st.markdown("Tekanan tanah lateral akibat beban diatas dihitung dengan persamaan berikut:")
st.latex(P_s_latex)
st.markdown(f"Dari hasil analisis di dapat nilai tekanan tanah lateral akibat beban diatasnya adalah ${round(P_s,ndigits=3)} kN/m$ $P_{{ae}}$ di aplikasikan merata setinggi dinding")

st.markdown("# Tekanan Tanah Aktif akibat Gempa, $P_{ae}$")
st.markdown("""Kondisi kesetimbangan gaya di belakang kepala jembatan dapat dilihat pada Gambar 2.
            Formula gaya tekan tanah akibat pengaruh gempa $P_{ae}$ yaitu sebagai berikut :""")
st.latex(P_ae_latex)
st.markdown("dengan nilai koefisien tekanan aktif seismik $k_{ae}$ adalah")
st.latex(k_ae_latex)
st.markdown("Dimana nilai, $\theta_{eq}$ dan $k_h$ adaleh sebagai berikut:")
col_B1,col_B2=st.columns(2)
with col_B1:
    st.latex(theta_eq_latex)
with col_B2:
    st.latex(k_h_latex)
st.markdown(f"Dari hasil analisis di dapat nilai tekanan tanah lateral akibat gempa adalah ${round(P_ae,ndigits=3)} kN/m$ di bawah ini di tampilkan diagram beban tekanan tanah lateral aktif $P_{{ae}}$ dalam variasi ketinggian dinding")

y_P_ae=linear_interpolation(0,P_ae,H_wall,0,x_tinggi_wall)
df_tekanan_tanah_gempa=pd.DataFrame({
    "Tinggi Wall (m)":x_tinggi_wall,
    "Tekanan Tanah Akibat Gempa (kN/m)":y_P_ae
    },index=None)
fig_2 = px.area(df_tekanan_tanah_gempa,
              x="Tekanan Tanah Akibat Gempa (kN/m)",
              y="Tinggi Wall (m)",
              range_x=[P_ae,0],
              range_y=[0,H_wall],
              markers=True,
              )
#fig.update_layout(
    #xaxis = dict(range=[0,P_a]),
    #yaxis = dict(range=[0,H_wall]),
#)
st.plotly_chart(fig_2,theme="streamlit",use_container_width=True)
P_ae_inter=linear_interpolation(P_ae,0,H_wall,0,interpolasi_per_ketinggian)
st.markdown(f"Untuk beban $P_a$ pada ketinggian {interpolasi_per_ketinggian} m adalah sebesar = ${round(P_ae_inter)} kN/m$")