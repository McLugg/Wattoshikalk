
import streamlit as st
import matplotlib.pyplot as plt

def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Passord", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Passord", type="password", on_change=password_entered, key="password")
        st.error("Feil passord")
        return False
    else:
        return True

def beregn_nedbetalingstid(
    total_kwh,
    investering_nok,
    spotpris_nok,
    nettleie_nok,
    egenforbruk_prosent,
    eksport_prosent,
    btc_eksportandel,
    btc_vekst_aar
):
    egenforbruk_kwh = total_kwh * egenforbruk_prosent
    eksport_kwh = total_kwh * eksport_prosent

    besparelse_forbruk = egenforbruk_kwh * (spotpris_nok + nettleie_nok)
    eksport_kontant = eksport_kwh * spotpris_nok * (1 - btc_eksportandel)
    eksport_btc = eksport_kwh * spotpris_nok * btc_eksportandel

    btc_beholdning = 0
    total_inntekt = 0
    kumulativ_inntekt = []

    for år in range(1, 51):
        # BTC lagres først
        btc_beholdning += eksport_btc
        btc_verdi = btc_beholdning * ((1 + btc_vekst_aar) ** år) if btc_eksportandel > 0 else 0

        total_inntekt = (besparelse_forbruk + eksport_kontant) * år + btc_verdi
        kumulativ_inntekt.append(total_inntekt)

        if total_inntekt >= investering_nok:
            return år, kumulativ_inntekt

    return None, kumulativ_inntekt

if check_password():
    st.title("Wattoshi vs Solcelle - Nedbetalingskalkulator")
    st.sidebar.header("Inputparametere")

    total_kwh = st.sidebar.number_input("Total årlig produksjon (kWh)", value=10000)
    investering_nok = st.sidebar.number_input("Investering (NOK)", value=120000)
    spotpris_nok = st.sidebar.number_input("Spotpris (NOK/kWh)", value=0.60)
    nettleie_nok = st.sidebar.number_input("Nettleie (NOK/kWh)", value=0.35)
    egenforbruk_prosent = st.sidebar.slider("Egenforbruk (%)", 0, 100, 70) / 100
    eksport_prosent = st.sidebar.slider("Eksport (%)", 0, 100, 30) / 100
    btc_eksportandel = st.sidebar.slider("Andel eksport lagret i BTC (%)", 0, 100, 50) / 100
    btc_vekst_aar = st.sidebar.slider("BTC verdiøkning (%/år)", 0, 50, 20) / 100

    if st.sidebar.button("Beregn nedbetalingstid"):
        nedbetaling, kumulativ_inntekt = beregn_nedbetalingstid(
            total_kwh,
            investering_nok,
            spotpris_nok,
            nettleie_nok,
            egenforbruk_prosent,
            eksport_prosent,
            btc_eksportandel,
            btc_vekst_aar
        )

        if nedbetaling:
            st.success(f"Nedbetalingstiden er {nedbetaling} år.")
        else:
            st.error("Investeringen nedbetales ikke innen 50 år.")

        fig, ax = plt.subplots()
        ax.plot(range(1, len(kumulativ_inntekt)+1), kumulativ_inntekt, label="Kumulativ inntekt")
        ax.axhline(y=investering_nok, color='r', linestyle='--', label="Investering")
        ax.set_xlabel("År")
        ax.set_ylabel("Verdi (NOK)")
        ax.set_title("Kumulativ Inntekt vs Investering")
        ax.legend()
        st.pyplot(fig)
