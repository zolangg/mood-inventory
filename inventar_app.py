import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="Mehrmals tägliches Selbstbeurteilungs-Inventar", layout="centered")
st.title("Mehrmals tägliches Selbstbeurteilungs-Inventar")

name = st.text_input("Name")
datum = st.date_input("Datum")

# === 14-Item ASRM (Manie/Mischzustand) ===

st.header("Manische und psychotische Symptome (14-Item ASRM, mehrmals täglich)")

asrm14_items = [
    ("Reizbarkeit", [
        "Ich war nicht gereizt.",
        "Ich war gelegentlich gereizt.",
        "Ich war häufiger gereizt, konnte es aber gut kontrollieren.",
        "Ich war die meiste Zeit gereizt und hatte Mühe, es zu kontrollieren.",
        "Ich war durchgehend extrem gereizt."
    ]),
    ("Glücksgefühl / gehobene Stimmung", [
        "Ich war nicht fröhlicher oder besser gelaunt als sonst.",
        "Ich war gelegentlich fröhlicher oder besser gelaunt als sonst.",
        "Ich war häufiger fröhlicher oder besser gelaunt als sonst.",
        "Ich war die meiste Zeit fröhlicher oder besser gelaunt als sonst.",
        "Ich war die ganze Zeit über außergewöhnlich fröhlich oder besser gelaunt."
    ]),
    ("Stimmungswechsel", [
        "Meine Stimmung war stabil.",
        "Meine Stimmung hat sich gelegentlich von fröhlich zu traurig oder gereizt verändert.",
        "Meine Stimmung hat sich häufiger von fröhlich zu traurig oder gereizt verändert.",
        "Meine Stimmung hat sich die meiste Zeit rasch verändert.",
        "Meine Stimmung hat sich ständig und abrupt verändert."
    ]),
    ("Selbstvertrauen", [
        "Mein Selbstvertrauen war wie üblich.",
        "Ich war gelegentlich selbstsicherer als sonst.",
        "Ich war häufiger deutlich selbstsicherer als sonst.",
        "Ich war die meiste Zeit sehr selbstsicher.",
        "Ich war durchgehend extrem selbstsicher."
    ]),
    ("Gefühl besonderer Fähigkeiten", [
        "Ich hatte nicht das Gefühl, besondere Fähigkeiten oder Kenntnisse zu haben.",
        "Ich hatte gelegentlich das Gefühl, besondere Fähigkeiten oder Kenntnisse zu haben, die andere nicht haben.",
        "Ich hatte häufiger das Gefühl, besondere Fähigkeiten oder Kenntnisse zu haben, die andere nicht haben.",
        "Ich hatte die meiste Zeit das Gefühl, besondere Fähigkeiten oder Kenntnisse zu haben.",
        "Ich war überzeugt, außergewöhnliche Fähigkeiten oder Kenntnisse zu haben, die anderen fehlen."
    ]),
    ("Schlafbedürfnis", [
        "Mein Schlafbedürfnis war wie sonst.",
        "Ich brauchte gelegentlich weniger Schlaf als sonst.",
        "Ich brauchte häufiger weniger Schlaf als sonst.",
        "Ich brauchte die meiste Zeit weniger Schlaf als sonst.",
        "Ich war durchgehend ohne Schlaf oder brauchte keinen Schlaf und fühlte mich trotzdem nicht müde."
    ]),
    ("Rededrang", [
        "Ich habe nicht mehr als sonst geredet.",
        "Ich habe gelegentlich mehr als sonst geredet.",
        "Ich habe häufiger mehr als sonst geredet.",
        "Ich habe die meiste Zeit mehr als sonst geredet.",
        "Ich habe ständig und ohne Unterbrechung geredet."
    ]),
    ("Gedankenrasen", [
        "Meine Gedanken waren ruhig und geordnet.",
        "Meine Gedanken waren gelegentlich schneller oder sprunghafter als sonst.",
        "Meine Gedanken waren häufiger schnell oder sprunghaft, aber ich konnte sie kontrollieren.",
        "Meine Gedanken waren die meiste Zeit rasend und schwer zu kontrollieren.",
        "Meine Gedanken waren ständig rasend und kaum zu kontrollieren."
    ]),
    ("Ablenkbarkeit", [
        "Ich war nicht abgelenkt durch meine Umgebung.",
        "Ich war gelegentlich abgelenkt durch Ereignisse oder Dinge um mich herum.",
        "Ich war häufiger abgelenkt durch Ereignisse oder Dinge um mich herum.",
        "Ich war die meiste Zeit abgelenkt durch Ereignisse oder Dinge um mich herum.",
        "Ich war ständig abgelenkt und konnte mich auf nichts konzentrieren."
    ]),
    ("Aktivitätsniveau", [
        "Ich war nicht aktiver als sonst.",
        "Ich war gelegentlich aktiver als sonst.",
        "Ich war häufiger aktiver als sonst.",
        "Ich war die meiste Zeit aktiver als sonst.",
        "Ich war nahezu pausenlos in Bewegung oder sehr aktiv."
    ]),
    ("Risikoverhalten / unüberlegte Handlungen", [
        "Ich habe keine Aktivitäten ausgeübt, die für mich oder andere negative Folgen hatten.",
        "Ich habe gelegentlich Dinge getan, die zu negativen Folgen geführt haben (z. B. impulsive Einkäufe, riskantes Verhalten).",
        "Ich habe häufiger solche Dinge getan.",
        "Ich habe die meiste Zeit solche Aktivitäten ausgeübt.",
        "Ich habe wiederholt Dinge getan, die zu gravierenden Problemen geführt haben und das Gefühl gehabt, die Kontrolle zu verlieren."
    ]),
    # Psychotische Items ab hier
    ("Stimmenhören", [
        "Ich habe keine Stimmen oder Geräusche gehört, die andere nicht gehört haben.",
        "Ich habe gelegentlich Stimmen oder Geräusche gehört, die andere nicht gehört haben.",
        "Ich habe häufiger Stimmen oder Geräusche gehört, die andere nicht gehört haben.",
        "Ich habe die meiste Zeit solche Stimmen oder Geräusche gehört.",
        "Ich habe fast ständig Stimmen oder Geräusche gehört, die andere nicht hören konnten."
    ]),
    ("Halluzinationen (z. B. Visionen, Dinge sehen)", [
        "Ich habe keine Dinge gesehen, die andere nicht sehen konnten.",
        "Ich habe gelegentlich Dinge gesehen, die andere nicht sehen konnten.",
        "Ich habe häufiger Dinge gesehen, die andere nicht sehen konnten.",
        "Ich habe die meiste Zeit Dinge gesehen, die anderen verborgen waren.",
        "Ich habe fast ständig Dinge gesehen, die andere nicht sehen konnten."
    ]),
    ("Ungewöhnliche / paranoide Gedanken", [
        "Ich hatte keine ungewöhnlichen oder belastenden Gedanken (wie: verfolgt zu werden, beeinflusst zu werden, oder dass andere über mich reden).",
        "Ich hatte gelegentlich solche Gedanken.",
        "Ich hatte häufiger solche Gedanken.",
        "Ich hatte die meiste Zeit belastende und störende Gedanken.",
        "Ich wurde die ganze Zeit von solchen Gedanken gequält, die meinen Alltag beeinträchtigt haben."
    ])
]

asrm14_values = []
asrm14_answers = []
for i, (question, options) in enumerate(asrm14_items):
    answer = st.radio(f"{i+1}. {question}", options, key=f"asrm14_{i}")
    asrm14_answers.append(answer)
    asrm14_values.append(options.index(answer))

asrm14_sum = sum(asrm14_values)

# Psychotische Items (12-14)
psychosis_scores = asrm14_values[11:14]
psychosis_alert = any([x >= 1 for x in psychosis_scores])  # schon ab 1 Punkt auffällig

# === BDI-II (mehrmals tägliche Befragung, Kurzfassung) ===

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

# === Auswertung & Anzeige ===

st.subheader("Auswertung")

def interpret_asrm14(score, psychosis_scores):
    message = ""
    if score < 15:
        message += "Keine oder nur minimale manische Symptome."
    elif score < 18:
        message += "Milde manische Symptome."
    elif score < 25:
        message += "Hypomanische Tendenz (Frühwarnzeichen)."
    else:
        message += "Klinisch relevante Manie! Dringende Rücksprache empfohlen."
    if any([x >= 1 for x in psychosis_scores]):
        message += " \n**Achtung:** Psychotische Symptome vorhanden! Bitte umgehend ärztliche Abklärung erwägen."
    return message

def interpret_bdi(score):
    if score <= 13:
        return "Minimale depressive Symptome"
    elif score <= 19:
        return "Leichte Symptome"
    elif score <= 28:
        return "Mäßige Symptome"
    else:
        return "Schwere Symptome"

asrm14_text = interpret_asrm14(asrm14_sum, psychosis_scores)
bdi_text = interpret_bdi(bdi_sum)

st.write(f"**14-Item ASRM Gesamtpunktzahl:** {asrm14_sum} von 56")
st.markdown(f"- **ASRM-Interpretation:** {asrm14_text}")
st.write(f"**BDI-II Gesamtpunktzahl:** {bdi_sum}")
st.markdown(f"- **BDI-II-Interpretation:** {bdi_text}")

# === Quadrantengrafik ===
st.subheader("Mischzustandsmatrix (ASRM vs. BDI)")
fig, ax = plt.subplots(figsize=(6, 4))
ax.set_xlim(0, 56)
ax.set_ylim(0, 63)
ax.set_xlabel("14-Item ASRM (Manie/Mischzustand)")
ax.set_ylabel("BDI-II (Depression)")
ax.axvline(18, color="grey", linestyle="--", alpha=0.7, label="Cutoff Hypomanie")
ax.axvline(25, color="red", linestyle="--", alpha=0.5, label="Cutoff Manie")
ax.axhline(19, color="grey", linestyle="--", alpha=0.7)
ax.scatter(asrm14_sum, bdi_sum, s=150, color="red")
ax.text(5, 60, "Depressiv", fontsize=10)
ax.text(35, 5, "Manisch", fontsize=10)
ax.text(35, 55, "Mischzustand", fontsize=10)
ax.text(5, 5, "Unauffällig", fontsize=10)
st.pyplot(fig)

# === PDF-Export ===
st.subheader("PDF Export")
if st.button("PDF erstellen und herunterladen"):
    # Grafik speichern
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        grafik_path = tmpfile.name

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, "Mehrmals tägliches Selbstbeurteilungs-Inventar (14-Item ASRM & BDI-II)", ln=True, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Datum: {datum}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "14-Item ASRM:", ln=True)
    pdf.set_font("Arial", size=10)
    for i, (q, _) in enumerate(asrm14_items):
        pdf.multi_cell(0, 8, f"{i + 1}. {q}: {asrm14_answers[i]}")
    pdf.cell(0, 10, f"Gesamtpunktzahl ASRM: {asrm14_sum}", ln=True)
    pdf.multi_cell(0, 10, f"ASRM-Interpretation: {asrm14_text}")
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "BDI-II:", ln=True)
    pdf.set_font("Arial", size=10)
    for i, (q, _) in enumerate(bdi_questions):
        pdf.multi_cell(0, 8, f"{i + 1}. {q}: {bdi_answers[i]}")
    pdf.cell(0, 10, f"Gesamtpunktzahl BDI-II: {bdi_sum}", ln=True)
    pdf.multi_cell(0, 10, f"BDI-II-Interpretation: {bdi_text}")
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "Mischzustandsmatrix:", ln=True)

    # Grafik einfügen (der Y-Wert wird nach der aktuellen Position im PDF bestimmt)
    y_now = pdf.get_y()
    pdf.image(grafik_path, x=10, y=y_now, w=pdf.w - 20)
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