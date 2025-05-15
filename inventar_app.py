import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="Tägliches Stimmungs-Inventar", layout="centered")
st.title("Tägliches Selbstbeurteilungs-Inventar")

name = st.text_input("Name")
datum = st.date_input("Datum")

# --- ASRM (Manie) ---
st.header("Manische Symptome (ASRM modifiziert)")
asrm_questions = [
    ("Stimmung", [
        "1 - Nicht mehr als sonst",
        "2 - Einmal kurz besser gelaunt als sonst",
        "3 - Öfters besser gelaunt als sonst",
        "4 - Meistens sehr gut gelaunt, auch ohne Anlass",
        "5 - Fast durchgehend euphorisch"
    ]),
    ("Selbstvertrauen", [
        "1 - Wie üblich",
        "2 - Kurzzeitig überdurchschnittlich selbstsicher",
        "3 - Häufig sehr selbstsicher",
        "4 - Meistens überzeugt, alles zu schaffen",
        "5 - Überzeugt, unbesiegbar zu sein"
    ]),
    ("Schlafbedürfnis", [
        "1 - Normales Schlafbedürfnis",
        "2 - Etwas weniger Schlaf, aber wach",
        "3 - Deutlich weniger Schlaf, aber trotzdem fit",
        "4 - Sehr wenig oder kein Schlaf, aber ohne Müdigkeit",
        "5 - Kein Schlaf nötig, voller Energie"
    ]),
    ("Sprachverhalten", [
        "1 - Wie üblich",
        "2 - Etwas gesprächiger als sonst",
        "3 - Mehr geredet als gewöhnlich",
        "4 - Sehr redselig",
        "5 - Dauerhaftes Reden"
    ]),
    ("Aktivitätsniveau", [
        "1 - Normales Aktivitätsniveau",
        "2 - Kurzzeitig aktiver",
        "3 - Häufig besonders aktiv",
        "4 - Fast ständig in Bewegung",
        "5 - Dauerhaft aktiv"
    ])
]
asrm_values = []
asrm_answers = []
for i, (question, options) in enumerate(asrm_questions):
    answer = st.radio(f"{i+1}. {question}", options, key=f"asrm_{i}")
    asrm_answers.append(answer)
    asrm_values.append(int(answer.split(" ")[0]))
asrm_sum = sum(asrm_values)

# --- BDI-II (Depression) ---
st.header("Depressive Symptome (BDI-II modifiziert)")
bdi_questions = [
    ("Traurigkeit", [
        "0 - Ich war heute nicht traurig.",
        "1 - Ich war einen Teil des Tages traurig.",
        "2 - Ich war den ganzen Tag über traurig.",
        "3 - Ich war so traurig, dass ich es kaum ertragen konnte."
    ]),
    ("Pessimismus", [
        "0 - Ich hatte heute Hoffnung für die Zukunft.",
        "1 - Ich war eher entmutigt als sonst.",
        "2 - Ich hatte wenig Hoffnung, dass sich etwas verbessern wird.",
        "3 - Ich sah keine Zukunft für mich."
    ]),
    ("Gefühl des Versagens", [
        "0 - Ich hatte kein Gefühl des Versagens.",
        "1 - Ich habe mich in manchen Dingen als gescheitert empfunden.",
        "2 - Ich habe viele Misserfolge gesehen.",
        "3 - Ich fühlte mich heute als kompletter Versager."
    ]),
    ("Verlust von Freude", [
        "0 - Ich konnte mich heute an Dingen erfreuen.",
        "1 - Freude war vermindert.",
        "2 - Ich empfand kaum noch Freude.",
        "3 - Ich konnte mich an nichts erfreuen."
    ]),
    ("Schuldgefühle", [
        "0 - Keine Schuldgefühle.",
        "1 - Ich fühlte mich wegen mancher Dinge schuldig.",
        "2 - Ich hatte stark ausgeprägte Schuldgefühle.",
        "3 - Ich fühlte mich durchgehend schuldig."
    ]),
    ("Gefühl bestraft zu werden", [
        "0 - Ich fühlte mich nicht bestraft.",
        "1 - Ich hatte das Gefühl, ich könnte bestraft werden.",
        "2 - Ich erwartete Bestrafung.",
        "3 - Ich hatte das Gefühl, ich werde bestraft."
    ]),
    ("Selbstabwertung", [
        "0 - Ich hatte ein normales Selbstwertgefühl.",
        "1 - Ich hatte weniger Selbstvertrauen als sonst.",
        "2 - Ich war enttäuscht von mir.",
        "3 - Ich mochte mich selbst nicht."
    ]),
    ("Selbstkritik", [
        "0 - Keine besondere Selbstkritik.",
        "1 - Ich war kritischer als sonst.",
        "2 - Ich machte mir viele Vorwürfe.",
        "3 - Ich gab mir für alles die Schuld."
    ]),
    ("Suizidgedanken", [
        "0 - Keine Gedanken an Selbsttötung.",
        "1 - Gedanken daran, aber ohne Absicht.",
        "2 - Ich hätte heute sterben wollen.",
        "3 - Ich hätte mich umgebracht, wenn ich gekonnt hätte."
    ]),
    ("Weinen", [
        "0 - Ich habe heute nicht geweint.",
        "1 - Ich war nah am Weinen.",
        "2 - Ich habe über vieles geweint.",
        "3 - Ich konnte nicht weinen, obwohl ich wollte."
    ]),
    ("Unruhe/Agitiertheit", [
        "0 - Keine auffällige Unruhe.",
        "1 - Ich war etwas unruhiger als sonst.",
        "2 - Ich konnte kaum still sitzen.",
        "3 - Ich musste ständig in Bewegung sein."
    ]),
    ("Interessenverlust", [
        "0 - Ich interessierte mich für Aktivitäten.",
        "1 - Mein Interesse war etwas reduziert.",
        "2 - Ich hatte kaum Interesse an irgendetwas.",
        "3 - Ich konnte mich für nichts mehr interessieren."
    ]),
    ("Entscheidungsschwierigkeiten", [
        "0 - Ich konnte Entscheidungen normal treffen.",
        "1 - Es fiel mir heute etwas schwerer.",
        "2 - Es fiel mir deutlich schwerer.",
        "3 - Ich konnte heute keine Entscheidungen treffen."
    ]),
    ("Wertlosigkeitsgefühl", [
        "0 - Ich hatte ein normales Selbstwertgefühl.",
        "1 - Ich fühlte mich weniger wertvoll.",
        "2 - Ich fühlte mich anderen unterlegen.",
        "3 - Ich fühlte mich völlig wertlos."
    ]),
    ("Energieverlust", [
        "0 - Ich hatte normale Energie.",
        "1 - Ich fühlte mich etwas erschöpft.",
        "2 - Ich konnte nicht viel machen.",
        "3 - Ich war zu erschöpft für fast alles."
    ]),
    ("Schlafveränderung", [
        "0 - Kein Unterschied",
        "1 - Etwas mehr Schlaf",
        "2 - Etwas weniger Schlaf",
        "3 - Deutlich mehr Schlaf",
        "4 - Deutlich weniger Schlaf",
        "5 - Ich schlief fast den ganzen Tag",
        "6 - Ich wachte 1-2 Stunden zu früh auf"
    ]),
    ("Reizbarkeit", [
        "0 - Keine gesteigerte Reizbarkeit",
        "1 - Ich war leicht reizbar",
        "2 - Ich war sehr gereizt",
        "3 - Ich war durchgehend gereizt"
    ]),
    ("Appetitveränderung", [
        "0 - Keine Veränderung",
        "1 - Etwas weniger Appetit",
        "2 - Etwas mehr Appetit",
        "3 - Deutlich weniger Appetit",
        "4 - Deutlich mehr Appetit",
        "5 - Kein Appetit",
        "6 - Ständiger Heißhunger"
    ]),
    ("Konzentrationsprobleme", [
        "0 - Konzentration war normal",
        "1 - Konzentration war leicht erschwert",
        "2 - Ich konnte mich kaum länger konzentrieren",
        "3 - Ich konnte mich gar nicht konzentrieren"
    ]),
    ("Müdigkeit/Erschöpfung", [
        "0 - Keine besondere Müdigkeit",
        "1 - Ich wurde schneller müde",
        "2 - Ich konnte vieles nicht tun",
        "3 - Ich war für fast alles zu müde"
    ]),
    ("Libidoverlust", [
        "0 - Keine Veränderung",
        "1 - Weniger Interesse",
        "2 - Stark vermindertes Interesse",
        "3 - Vollständiger Verlust des Interesses"
    ])
]

bdi_values = []
bdi_answers = []
for i, (question, options) in enumerate(bdi_questions):
    answer = st.radio(f"{i+1}. {question}", options, key=f"bdi_{i}")
    bdi_answers.append(answer)
    bdi_values.append(int(answer.split(" ")[0]))
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
    pdf.cell(0, 10, "Tägliches Selbstbeurteilungs-Inventar", ln=True, align="C")
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