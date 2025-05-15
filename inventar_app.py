import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="Tägliches Stimmungs-Inventar", layout="centered")
st.title("Mehrmals tägliches Selbstbeurteilungs-Inventar")

name = st.text_input("Name")
datum = st.date_input("Datum")

# --- ASRM (Manie) ---

st.header("Manische Symptome (ASRM, mehrmals täglich)")

asrm_questions = [
    ("Stimmung", [
        "Ich war nicht besser gelaunt als gewöhnlich.",
        "Ich war kurzzeitig besser gelaunt als gewöhnlich.",
        "Ich war mehrmals besser gelaunt als gewöhnlich.",
        "Ich war über weite Strecken deutlich besser gelaunt, auch ohne besonderen Anlass.",
        "Ich war fast durchgehend außergewöhnlich euphorisch."
    ]),
    ("Selbstvertrauen", [
        "Mein Selbstvertrauen war wie gewohnt.",
        "Ich war kurzzeitig selbstsicherer als sonst.",
        "Ich war wiederholt deutlich selbstsicherer als sonst.",
        "Ich war die meiste Zeit überzeugt, alles schaffen zu können.",
        "Ich war fast durchgehend überzeugt, unbesiegbar zu sein."
    ]),
    ("Schlafbedürfnis", [
        "Mein Schlafbedürfnis war wie üblich.",
        "Ich fühlte mich mit etwas weniger Schlaf als sonst wach und ausgeruht.",
        "Ich brauchte deutlich weniger Schlaf und war dennoch fit.",
        "Ich hatte sehr wenig oder keinen Schlaf, aber keine Müdigkeit.",
        "Ich hatte das Gefühl, keinen Schlaf zu benötigen und war voller Energie."
    ]),
    ("Sprachverhalten", [
        "Ich habe wie gewöhnlich gesprochen.",
        "Ich war etwas gesprächiger als sonst.",
        "Ich habe deutlich mehr geredet als üblich.",
        "Ich war die meiste Zeit sehr redselig.",
        "Ich habe nahezu ununterbrochen gesprochen."
    ]),
    ("Aktivitätsniveau", [
        "Mein Aktivitätsniveau war wie üblich.",
        "Ich war kurzzeitig aktiver als sonst.",
        "Ich war häufig besonders aktiv.",
        "Ich war fast die gesamte Zeit in Bewegung.",
        "Ich war nahezu dauerhaft sehr aktiv."
    ])
]

asrm_values = []
asrm_answers = []
for i, (question, options) in enumerate(asrm_questions):
    answer = st.radio(f"{i+1}. {question}", options, key=f"asrm_{i}")
    asrm_answers.append(answer)
    asrm_values.append(options.index(answer) + 1)
asrm_sum = sum(asrm_values)

# --- BDI-II (Depression) ---

st.header("Depressive Symptome (BDI-II, mehrmals täglich)")

bdi_questions = [
    ("Traurigkeit", [
        "Ich war nicht traurig.",
        "Ich war zeitweise traurig.",
        "Ich war fast die ganze Zeit traurig.",
        "Ich war so traurig, dass ich es kaum ertragen konnte."
    ]),
    ("Pessimismus", [
        "Ich hatte Hoffnung für die nähere Zukunft.",
        "Ich war zwischenzeitlich entmutigt.",
        "Ich hatte wenig Hoffnung, dass sich etwas verbessert.",
        "Ich hatte keine Hoffnung für die nähere Zukunft."
    ]),
    ("Gefühl des Versagens", [
        "Ich hatte kein Gefühl des Versagens.",
        "Ich habe mich gelegentlich als gescheitert gefühlt.",
        "Ich habe mehrere Misserfolge wahrgenommen.",
        "Ich habe mich durchgehend als Versager gefühlt."
    ]),
    ("Verlust von Freude", [
        "Ich konnte mich an Dingen erfreuen.",
        "Meine Freude war zwischendurch vermindert.",
        "Ich konnte mich kaum noch freuen.",
        "Ich konnte mich an nichts erfreuen."
    ]),
    ("Schuldgefühle", [
        "Ich hatte keine Schuldgefühle.",
        "Ich fühlte mich wegen mancher Dinge schuldig.",
        "Ich hatte stark ausgeprägte Schuldgefühle.",
        "Ich fühlte mich durchgehend schuldig."
    ]),
    ("Gefühl bestraft zu werden", [
        "Ich hatte nicht das Gefühl, bestraft zu werden.",
        "Ich hatte zeitweise das Gefühl, ich könnte bestraft werden.",
        "Ich erwartete, bestraft zu werden.",
        "Ich war überzeugt, bestraft zu werden."
    ]),
    ("Selbstabwertung", [
        "Mein Selbstwertgefühl war wie gewohnt.",
        "Ich hatte gelegentlich weniger Selbstvertrauen.",
        "Ich war mit mir selbst unzufrieden.",
        "Ich mochte mich gar nicht."
    ]),
    ("Selbstkritik", [
        "Ich habe mich nicht besonders selbstkritisch gesehen.",
        "Ich war zeitweise kritischer mit mir als sonst.",
        "Ich machte mir viele Vorwürfe.",
        "Ich gab mir für alles die Schuld."
    ]),
    ("Suizidgedanken", [
        "Ich hatte keine Gedanken an Selbsttötung.",
        "Ich hatte gelegentlich Gedanken daran, aber keine Absicht.",
        "Ich hätte manchmal nicht mehr leben wollen.",
        "Ich hätte mich umgebracht, wenn ich gekonnt hätte."
    ]),
    ("Weinen", [
        "Ich habe nicht geweint.",
        "Ich war zeitweise den Tränen nahe.",
        "Ich habe viel geweint.",
        "Ich wollte weinen, konnte aber nicht."
    ]),
    ("Unruhe/Agitiertheit", [
        "Ich war nicht unruhiger als sonst.",
        "Ich war manchmal unruhiger als sonst.",
        "Ich konnte kaum stillsitzen.",
        "Ich musste die meiste Zeit in Bewegung sein."
    ]),
    ("Interessenverlust", [
        "Ich hatte Interesse an Aktivitäten.",
        "Mein Interesse war zwischenzeitlich reduziert.",
        "Ich hatte kaum Interesse an irgendetwas.",
        "Ich konnte mich für nichts interessieren."
    ]),
    ("Entscheidungsschwierigkeiten", [
        "Ich konnte Entscheidungen wie gewohnt treffen.",
        "Entscheidungen fielen mir zeitweise schwerer.",
        "Es fiel mir deutlich schwerer, mich zu entscheiden.",
        "Ich konnte keine Entscheidungen treffen."
    ]),
    ("Wertlosigkeitsgefühl", [
        "Mein Selbstwertgefühl war normal.",
        "Ich fühlte mich manchmal weniger wertvoll.",
        "Ich fühlte mich anderen unterlegen.",
        "Ich fühlte mich völlig wertlos."
    ]),
    ("Energieverlust", [
        "Ich hatte normale Energie.",
        "Ich fühlte mich zwischendurch etwas erschöpft.",
        "Ich konnte wenig machen.",
        "Ich war zu erschöpft, um etwas zu tun."
    ]),
    ("Schlafveränderung", [
        "Mein Schlaf war wie gewöhnlich.",
        "Ich habe etwas mehr geschlafen als sonst.",
        "Ich habe etwas weniger geschlafen als sonst.",
        "Ich habe deutlich mehr geschlafen als sonst.",
        "Ich habe deutlich weniger geschlafen als sonst.",
        "Ich habe fast durchgehend geschlafen.",
        "Ich bin ein bis zwei Stunden zu früh aufgewacht."
    ]),
    ("Reizbarkeit", [
        "Ich war nicht reizbarer als sonst.",
        "Ich war zeitweise leicht reizbar.",
        "Ich war oft sehr gereizt.",
        "Ich war die meiste Zeit durchgehend gereizt."
    ]),
    ("Appetitveränderung", [
        "Mein Appetit war wie gewohnt.",
        "Ich hatte zwischendurch weniger Appetit.",
        "Ich hatte zwischendurch mehr Appetit.",
        "Ich hatte deutlich weniger Appetit.",
        "Ich hatte deutlich mehr Appetit.",
        "Ich hatte gar keinen Appetit.",
        "Ich hatte ständig Heißhunger."
    ]),
    ("Konzentrationsprobleme", [
        "Meine Konzentration war wie gewohnt.",
        "Ich konnte mich zeitweise schlechter konzentrieren.",
        "Ich konnte mich kaum noch länger konzentrieren.",
        "Ich konnte mich gar nicht konzentrieren."
    ]),
    ("Müdigkeit/Erschöpfung", [
        "Ich war nicht müder als sonst.",
        "Ich wurde schneller müde.",
        "Ich konnte vieles nicht tun.",
        "Ich war für fast alles zu müde."
    ]),
    ("Libidoverlust", [
        "Mein sexuelles Interesse war wie gewöhnlich.",
        "Ich hatte zwischendurch weniger Interesse.",
        "Ich hatte deutlich weniger Interesse.",
        "Ich hatte kein sexuelles Interesse mehr."
    ])
]

bdi_values = []
bdi_answers = []
for i, (question, options) in enumerate(bdi_questions):
    answer = st.radio(f"{i+1}. {question}", options, key=f"bdi_{i}")
    bdi_answers.append(answer)
    bdi_values.append(options.index(answer))
bdi_sum = sum(bdi_values)

# --- Auswertung und Anzeige ---
st.subheader("Auswertung")
st.write(f"**ASRM (Manie):** {asrm_sum} Punkte")
st.write(f"**BDI-II (Depression):** {bdi_sum} Punkte")

def interpret_asrm(score):
    if score <= 5:
        return "Keine auffälligen Symptome"
    elif score < 11:
        return "Hinweise auf manische/hypomanische Tendenzen"
    else:
        return "Mögliche klinisch relevante Manieanzeichen"

def interpret_bdi(score):
    if score <= 13:
        return "Minimale depressive Symptome"
    elif score <= 19:
        return "Leichte Symptome"
    elif score <= 28:
        return "Mäßige Symptome"
    else:
        return "Schwere Symptome"

asrm_text = interpret_asrm(asrm_sum)
bdi_text = interpret_bdi(bdi_sum)

st.markdown(f"- **ASRM-Interpretation:** {asrm_text}")
st.markdown(f"- **BDI-II-Interpretation:** {bdi_text}")

# --- Quadrantengrafik: Mischzustandsmatrix ---
st.subheader("Mischzustandsmatrix (ASRM vs. BDI)")
fig, ax = plt.subplots(figsize=(6, 4))
ax.set_xlim(0, 25)
ax.set_ylim(0, 63)
ax.set_xlabel("ASRM (Manie)")
ax.set_ylabel("BDI-II (Depression)")
ax.axvline(11, color="grey", linestyle="--", alpha=0.7)
ax.axhline(19, color="grey", linestyle="--", alpha=0.7)
ax.scatter(asrm_sum, bdi_sum, s=150, color="red")
ax.text(3, 60, "Depressiv", fontsize=10)
ax.text(15, 3, "Manisch", fontsize=10)
ax.text(15, 55, "Mischzustand", fontsize=10)
ax.text(3, 5, "Unauffällig", fontsize=10)
st.pyplot(fig)

# --- PDF-Export ---
st.subheader("PDF Export")
if st.button("PDF erstellen und herunterladen"):
    # Grafik speichern
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        grafik_path = tmpfile.name

    # PDF erstellen
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, "Mehrmals tägliches Selbstbeurteilungs-Inventar", ln=True, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Datum: {datum}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "ASRM (Manie):", ln=True)
    pdf.set_font("Arial", size=10)
    for i, (q, _) in enumerate(asrm_questions):
        pdf.multi_cell(0, 8, f"{i+1}. {q}: {asrm_answers[i]}")
    pdf.cell(0, 10, f"Gesamtpunktzahl ASRM: {asrm_sum}", ln=True)
    pdf.cell(0, 10, f"ASRM-Interpretation: {asrm_text}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "BDI-II (Depression):", ln=True)
    pdf.set_font("Arial", size=10)
    for i, (q, _) in enumerate(bdi_questions):
        pdf.multi_cell(0, 8, f"{i+1}. {q}: {bdi_answers[i]}")
    pdf.cell(0, 10, f"Gesamtpunktzahl BDI-II: {bdi_sum}", ln=True)
    pdf.cell(0, 10, f"BDI-Interpretation: {bdi_text}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "Mischzustandsmatrix:", ln=True)
    # Grafik einfügen
    pdf.image(grafik_path, x=10, y=pdf.get_y(), w=pdf.w-20)
    os.remove(grafik_path)
    # Als Download bereitstellen
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
        with open(tmpfile.name, "rb") as f:
            st.download_button(
                label="PDF herunterladen",
                data=f.read(),
                file_name=f"Stimmungsinventar_{datum}.pdf",
                mime="application/pdf"
            )
        os.remove(tmpfile.name)