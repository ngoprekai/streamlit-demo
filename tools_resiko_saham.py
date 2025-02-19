import time
import streamlit as st
import yfinance as yf
import numpy as np
from datetime import datetime

st.warning(
    "DISCLAIMER : Tools ini hanya 'membantu' Anda, bukan menjadi 'dasar' atau 'alasan utama' Anda untuk memilih saham yang Anda inginkan. Tools di situs ini tidak dimaksudkan sebagai nasihat keuangan, investasi, atau perdagangan. Investasi saham melibatkan risiko, termasuk kehilangan modal. Penggunaan teknologi Artificial Intelligence dalam investasi saham juga memiliki risikonya tersendiri dan tidak ada jaminan bahwa teknologi ini akan membantu Anda menghasilkan keuntungan yang pasti.",
    icon="⚠️")
st.warning(
    "DISCLAIMER : Anda bertanggung jawab penuh atas keputusan investasi Anda sendiri. Kami tidak bertanggung jawab atas kerugian atau kerusakan yang mungkin timbul dari penggunaan tools yang disediakan di situs ini. Anda harus melakukan analisa Anda sendiri terlebih dahulu dan mengevaluasi informasi sebelum Anda mengambil tindakan apapun berdasarkan tools yang dibagikan di situs ini.",
    icon="⚠️")

st.title("Tools Analisa & Prediksi Harga Saham")

ticker1 = st.text_input(
        "Ticker saham (pakai '.JK' di akhir ticker untuk saham Indonesia)",
        "ASSA.JK",
        placeholder='Masukkan ticker saham disini, misalnya ASSA.JK').upper()
data1 = yf.Ticker(ticker1).history(period="1y")
stck_pct1 = data1["Close"].pct_change()
rets1 = stck_pct1.dropna()

st.button("Analisa")
    
if not ticker1:
    st.warning("Masukkan ticker saham yang Anda inginkan. Gunakan '.JK' di akhir ticker untuk saham Indonesia. Misal, BBRI.JK",
        icon="⚠️")
elif "USD" in ticker1:
    st.warning("Tools ini hanya menerima input data saham saja jadi tolong masukkan ticker saham Anda",
        icon="⚠️")
elif "IDR" in ticker1:
    st.warning("Tools ini hanya menerima input data saham saja jadi tolong masukkan ticker saham Anda",
        icon="⚠️")
else:
    if data1.empty:
        st.warning(
            "Data dari ticker saham ini tidak ditemukan. Gunakan '.JK' dibelakang ticker saham untuk saham Indonesia. Misal BBCA.JK",
            icon="⚠️")
    else:
        st.subheader("Analisa Grafik Return Harga Saham")
        st.line_chart(rets1, x_label="Tanggal", y_label="Return Harga Saham")

        if stck_pct1.max() > 0:
            st.write(
                "Return harga saham tertinggi dalam 1 tahun terakhir : :green[%.2f]%%"
                % (stck_pct1.max() * 100))
        else:
            st.write(
                "Return harga saham tertinggi dalam 1 tahun terakhir : :red[%.2f]%%"
                % (stck_pct1.max() * 100))

        if stck_pct1.min() > 0:
            st.write(
                "Return harga saham terendah dalam 1 tahun terakhir : :green[%.2f]%%"
                % (stck_pct1.min() * 100))
        else:
            st.write(
                "Return harga saham terendah dalam 1 tahun terakhir : :red[%.2f]%%"
                % (stck_pct1.min() * 100))

        if stck_pct1.mean() > 0:
            st.write(
                "Rata - rata return harga saham dalam 1 tahun terakhir : :green[%.2f]%%"
                % (stck_pct1.mean() * 100))
        else:
            st.write(
                "Rata - rata return harga saham dalam 1 tahun terakhir : :red[%.2f]%%"
                % (stck_pct1.mean() * 100))

        st.write(
            "Return harga saham dalam 1 tahun terakhir naik dan turun sebesar : :blue[%.2f]%% dari rata - rata return harga sahamnya"
            % (stck_pct1.std() * 100))

    st.subheader("Prediksi Harga Saham")

    if data1.empty:
        st.warning("Tidak ada data yang ditemukan", icon="⚠️")
    else:
        years = st.slider("Tentukan jumlah tahun yang kalian inginkan", 1, 10,
                         10)
        years_pick = years * 365
        dt = 1 / years_pick
        mu = rets1.mean()
        sigma = rets1.std()

        msg = st.toast('Memuat data...')
        time.sleep(1)

        def stock_monte_carlo(start_price, years_pick, mu, sigma):

            price = np.zeros(years_pick)
            price[0] = start_price
            shock = np.zeros(years_pick)
            drift = np.zeros(years_pick)

            for x in range(1, years_pick):

                shock[x] = np.random.normal(loc=mu * dt,
                                            scale=sigma * np.sqrt(dt))
                drift[x] = mu * dt
                price[x] = price[x - 1] + (price[x - 1] * (drift[x] +
                                                           (shock[x] * 5)))

            return price

        start_price = data1['Close'][-1]
        runs = 1000
        simulations = np.zeros(runs)
        np.set_printoptions(threshold=5)

        for run in range(runs):
            simulations[run] = stock_monte_carlo(start_price, years_pick, mu,
                                                 sigma)[years_pick - 1]

        q = np.percentile(simulations, 1)
        max_price = simulations.max()

        kurs = yf.Ticker("USDIDR=X").history(period="1y")
        kurs_sekarang = kurs['Close'][-1]

        def kerugian(multiple):
            nilai_kerugian = (start_price - q) * multiple
            harga_kerugian = start_price - nilai_kerugian
            persen_kerugian = (nilai_kerugian / start_price) * 100
            if ticker1.endswith('.JK'):
                if harga_kerugian < 0 :
                    st.subheader(":red[Resiko kerugian] yang bisa Anda alami adalah :red[modal investasi Anda hilang / habis] karena harga saham menyentuh :red[dibawah 0]")
                else:
                    st.write(
                        "Jika Anda membeli saham :blue[%s]" %(ticker1), "di harga sekarang yaitu :blue[Rp%.0f]." %(start_price), "Maka kemungkinan :red[resiko kerugian tertinggi] yang bisa Anda alami dalam",
                        years, "tahun kedepan untuk :blue[1 lot] nya adalah sebesar :red[-Rp%.0f]." % (nilai_kerugian * 100), "Kerugian tersebut diprediksi menyentuh harga :red[Rp%.0f]" % (harga_kerugian),
                        "yaitu sebesar :red[-%.2f]%%" %(persen_kerugian)   
                    )
                    col1, col2 = st.columns(2)
                    col1.metric("Predicted Highest Loss Value", "-Rp%.0f"%(nilai_kerugian*100), "-%.2f%%"%(persen_kerugian))
                    col2.metric("Predicted Highest Loss Price", "%.0f"%(harga_kerugian), "-%.2f%%"%(persen_kerugian))
            else:
                if harga_kerugian < 0:
                    st.subheader(":red[Resiko kerugian] yang bisa Anda alami adalah :red[modal investasi Anda hilang / habis] karena harga saham menyentuh :red[dibawah 0]")
                else:
                    st.write(
                        "Jika Anda membeli saham :blue[%s]" %(ticker1), "di harga sekarang yaitu :blue[Rp%.0f]." %(start_price), "Maka kemungkinan :red[resiko kerugian tertinggi] yang bisa Anda alami dalam",
                        years, "tahun kedepan untuk :blue[1 lembar] nya adalah sebesar :red[-Rp%.0f]." % (nilai_kerugian * kurs_sekarang), "Kerugian tersebut diprediksi menyentuh harga :red[Rp%.0f]" % (harga_kerugian),
                        "yaitu sebesar :red[-%.2f]%%" %(persen_kerugian), " (kurs: :blue[Rp%.0f])" %(kurs_sekarang)
                    )
                    col1, col2 = st.columns(2)
                    col1.metric("Predicted Highest Loss Value", "-Rp%.0f"%(nilai_kerugian*kurs_sekarang), "-%.2f%%"%(persen_kerugian))
                    col2.metric("Predicted Highest Loss Price", "%.0f"%(harga_kerugian), "-%.2f%%"%(persen_kerugian))

        def keuntungan(multiple):
            nilai_keuntungan = (max_price - start_price) * multiple
            harga_keuntungan = start_price + nilai_keuntungan
            persen_keuntungan = (nilai_keuntungan / start_price) * 100
            if ticker1.endswith('.JK'):
                st.write(
                    "Jika Anda membeli saham :blue[%s]" %(ticker1), "di harga sekarang yaitu :blue[Rp%.0f]." %(start_price), "Maka kemungkinan :green[keuntungan tertinggi] yang bisa Anda dapatkan dalam",
                    years, "tahun kedepan untuk :blue[1 lot] nya adalah sebesar :green[Rp%.0f]." % (nilai_keuntungan * 100), "Keuntungan tersebut diprediksi menyentuh harga :green[Rp%.0f]" % (harga_keuntungan),
                    "yaitu sebesar :green[%.2f]%%" %(persen_keuntungan)
                )
                col1, col2 = st.columns(2)
                col1.metric("Predicted Highest Gain Value", "Rp%.0f"%(nilai_keuntungan*100), "%.2f%%"%(persen_keuntungan))
                col2.metric("Predicted Highest Gain Price", "%.0f"%(harga_keuntungan), "%.2f%%"%(persen_keuntungan))
            else:
                st.write( 
                    "Jika Anda membeli saham :blue[%s]" %(ticker1), "di harga sekarang yaitu :blue[Rp%.0f]." %(start_price), "Maka kemungkinan :green[keuntungan tertinggi] yang bisa Anda dapatkan dalam",
                    years, "tahun kedepan untuk :blue[1 lembar] nya adalah sebesar :green[Rp%.0f]." % (nilai_keuntungan * kurs_sekarang), "Kerugian tersebut diprediksi menyentuh harga :green[Rp%.0f]" % (harga_keuntungan),
                    "yaitu sebesar :green[%.2f]%%" %(persen_keuntungan), " (kurs: :blue[Rp%.0f])" %(kurs_sekarang)
                )
                col1, col2 = st.columns(2)
                col1.metric("Predicted Highest Gain Value", "Rp%.0f"%(nilai_keuntungan*kurs_sekarang), "%.2f%%"%(persen_keuntungan))
                col2.metric("Predicted Highest Gain Price", "%.0f"%(harga_keuntungan), "%.2f%%"%(persen_keuntungan))
        
        if 0 < years <= 3:
            msg.toast('Memproses data...')
            time.sleep(1)
            kerugian(4)
            keuntungan(4)
            msg.toast('Data berhasil diubah', icon = "🎉")
        elif 3 < years <= 6:
            msg.toast('Memproses data...')
            time.sleep(1)
            kerugian(8)
            keuntungan(8)
            msg.toast('Data berhasil diubah', icon = "🎉")
        elif 6 < years <= 10:
            msg.toast('Memproses data...')
            time.sleep(1)
            kerugian(12)
            keuntungan(12)
            msg.toast('Data berhasil diubah', icon = "🎉")

st.warning(
    "DISCLAIMER : Tools ini hanya 'membantu' Anda, bukan menjadi 'dasar' atau 'alasan utama' Anda untuk memilih saham yang Anda inginkan. Tools di situs ini tidak dimaksudkan sebagai nasihat keuangan, investasi, atau perdagangan. Investasi saham melibatkan risiko, termasuk kehilangan modal. Penggunaan teknologi Artificial Intelligence dalam investasi saham juga memiliki risikonya tersendiri dan tidak ada jaminan bahwa teknologi ini akan membantu Anda menghasilkan keuntungan yang pasti.",
    icon="⚠️")
st.warning(
    "DISCLAIMER : Anda bertanggung jawab penuh atas keputusan investasi Anda sendiri. Kami tidak bertanggung jawab atas kerugian atau kerusakan yang mungkin timbul dari penggunaan tools yang disediakan di situs ini. Anda harus melakukan analisa Anda sendiri terlebih dahulu dan mengevaluasi informasi sebelum Anda mengambil tindakan apapun berdasarkan tools yang dibagikan di situs ini.",
    icon="⚠️")
