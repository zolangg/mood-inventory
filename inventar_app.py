import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

def make_ascii(text):
    return (text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
                .replace("ß", "ss").replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue")
                .replace("“", '"').replace("”", '"').replace("„", '"')
                .replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-")
                .replace("…", "...").replace("°", " Grad "))
st.set_page_config(page_title="Mehrmals taegliches Selbstbeurteilungs-Inventar", layout="centered")
st.title("Mehrmals taegliches Selbstbeurteilungs-Inventar")

name = st.text_input("Name")
datum = st.date_input("Datum")

# === 14-Item ASRM (Manie/Mischzustand) ===

st.header("Manische und psychotische Symptome (14-Item ASRM, mehrmals taeglich)")

asrm14_items = [
    ("Reizbarkeit", [
        "Ich war nicht gereizt.",
        "Ich war gelegentlich gereizt.",
        "Ich war haeufiger gereizt, konnte es aber gut kontrollieren.",
        "Ich war die meiste Zeit gereizt und hatte Muehe, es zu kontrollieren.",
        "Ich war durchgehend extrem gereizt."
    ]),
    ("Gluecksgefuehl / gehobene Stimmung", [
        "Ich war nicht froehlicher oder besser gelaunt als sonst.",
        "Ich war gelegentlich froehlicher oder besser gelaunt als sonst.",
        "Ich war haeufiger froehlicher oder besser gelaunt als sonst.",
        "Ich war die meiste Zeit froehlicher oder besser gelaunt als sonst.",
        "Ich war die ganze Zeit ueber aussergewoehnlich froehlich oder besser gelaunt."
    ]),
    ("Stimmungswechsel", [
        "Meine Stimmung war stabil.",
        "Meine Stimmung hat sich gelegentlich von froehlich zu traurig oder gereizt veraendert.",
        "Meine Stimmung hat sich haeufiger von froehlich zu traurig oder gereizt veraendert.",
        "Meine Stimmung hat sich die meiste Zeit rasch veraendert.",
        "Meine Stimmung hat sich staendig und abrupt veraendert."
    ]),
    ("Selbstvertrauen", [
        "Mein Selbstvertrauen war wie ueblich.",
        "Ich war gelegentlich selbstsicherer als sonst.",
        "Ich war haeufiger deutlich selbstsicherer als sonst.",
        "Ich war die meiste Zeit sehr selbstsicher.",
        "Ich war durchgehend extrem selbstsicher."
    ]),
    ("Gefuehl besonderer Faehigkeiten", [
        "Ich hatte nicht das Gefuehl, besondere Faehigkeiten oder Kenntnisse zu haben.",
        "Ich hatte gelegentlich das Gefuehl, besondere Faehigkeiten oder Kenntnisse zu haben, die andere nicht haben.",
        "Ich hatte haeufiger das Gefuehl, besondere Faehigkeiten oder Kenntnisse zu haben, die andere nicht haben.",
        "Ich hatte die meiste Zeit das Gefuehl, besondere Faehigkeiten oder Kenntnisse zu haben.",
        "Ich war ueberzeugt, aussergewoehnliche Faehigkeiten oder Kenntnisse zu haben, die anderen fehlen."
    ]),
    ("Schlafbeduerfnis", [
        "Mein Schlafbeduerfnis war wie sonst.",
        "Ich brauchte gelegentlich weniger Schlaf als sonst.",
        "Ich brauchte haeufiger weniger Schlaf als sonst.",
        "Ich brauchte die meiste Zeit weniger Schlaf als sonst.",
        "Ich war durchgehend ohne Schlaf oder brauchte keinen Schlaf und fuehlte mich trotzdem nicht muede."
    ]),
    ("Rededrang", [
        "Ich habe nicht mehr als sonst geredet.",
        "Ich habe gelegentlich mehr als sonst geredet.",
        "Ich habe haeufiger mehr als sonst geredet.",
        "Ich habe die meiste Zeit mehr als sonst geredet.",
        "Ich habe staendig und ohne Unterbrechung geredet."
    ]),
    ("Gedankenrasen", [
        "Meine Gedanken waren ruhig und geordnet.",
        "Meine Gedanken waren gelegentlich schneller oder sprunghafter als sonst.",
        "Meine Gedanken waren haeufiger schnell oder sprunghaft, aber ich konnte sie kontrollieren.",
        "Meine Gedanken waren die meiste Zeit rasend und schwer zu kontrollieren.",
        "Meine Gedanken waren staendig rasend und kaum zu kontrollieren."
    ]),
    ("Ablenkbarkeit", [
        "Ich war nicht abgelenkt durch meine Umgebung.",
        "Ich war gelegentlich abgelenkt durch Ereignisse oder Dinge um mich herum.",
        "Ich war haeufiger abgelenkt durch Ereignisse oder Dinge um mich herum.",
        "Ich war die meiste Zeit abgelenkt durch Ereignisse oder Dinge um mich herum.",
        "Ich war staendig abgelenkt und konnte mich auf nichts konzentrieren."
    ]),
    ("Aktivitaetsniveau", [
        "Ich war nicht aktiver als sonst.",
        "Ich war gelegentlich aktiver als sonst.",
        "Ich war haeufiger aktiver als sonst.",
        "Ich war die meiste Zeit aktiver als sonst.",
        "Ich war nahezu pausenlos in Bewegung oder sehr aktiv."
    ]),
    ("Risikoverhalten / unueberlegte Handlungen", [
        "Ich habe keine Aktivitaeten ausgeuebt, die fuer mich oder andere negative Folgen hatten.",
        "Ich habe gelegentlich Dinge getan, die zu negativen Folgen gefuehrt haben (z.B. impulsive Einkaeufe, riskantes Verhalten).",
        "Ich habe haeufiger solche Dinge getan.",
        "Ich habe die meiste Zeit solche Aktivitaeten ausgeuebt.",
        "Ich habe wiederholt Dinge getan, die zu gravierenden Problemen gefuehrt haben und das Gefuehl gehabt, die Kontrolle zu verlieren."
    ]),
    ("Stimmenhoeren", [
        "Ich habe keine Stimmen oder Geraeusche gehoert, die andere nicht gehoert haben.",
        "Ich habe gelegentlich Stimmen oder Geraeusche gehoert, die andere nicht gehoert haben.",
        "Ich habe haeufiger Stimmen oder Geraeusche gehoert, die andere nicht gehoert haben.",
        "Ich habe die meiste Zeit solche Stimmen oder Geraeusche gehoert.",
        "Ich habe fast staendig Stimmen oder Geraeusche gehoert, die andere nicht hoeren konnten."
    ]),
    ("Halluzinationen (z.B. Visionen, Dinge sehen)", [
        "Ich habe keine Dinge gesehen, die andere nicht sehen konnten.",
        "Ich habe gelegentlich Dinge gesehen, die andere nicht sehen konnten.",
        "Ich habe haeufiger Dinge gesehen, die andere nicht sehen konnten.",
        "Ich habe die meiste Zeit Dinge gesehen, die anderen verborgen waren.",
        "Ich habe fast staendig Dinge gesehen, die andere nicht sehen konnten."
    ]),
    ("Ungewoehnliche / paranoide Gedanken", [
        "Ich hatte keine ungewoehnlichen oder belastenden Gedanken (wie: verfolgt zu werden, beeinflusst zu werden, oder dass andere ueber mich reden).",
        "Ich hatte gelegentlich solche Gedanken.",
        "Ich hatte haeufiger solche Gedanken.",
        "Ich hatte die meiste Zeit belastende und stoerende Gedanken.",
        "Ich wurde die ganze Zeit von solchen Gedanken gequaelt, die meinen Alltag beeintraechtigt haben."
    ])
]

asrm14_values = []
asrm14_answers = []
for i, (question, options) in enumerate(asrm14_items):
    answer = st.radio(f"{i+1}. {question}", options, key=f"asrm14_{i}")
    asrm14_answers.append(answer)
    asrm14_values.append(options.index(answer))

asrm14_sum = sum(asrm14_values)
psychosis_scores = asrm14_values[11:14]

asrm_core = sum(asrm14_values[:5])
asrm_total = asrm14_sum
# === BDI-II (ASCII-kompatibel, Kurzfassung) ===

st.header("Depressive Symptome (BDI-II, mehrmals taeglich)")

bdi_questions = [
    ("Traurigkeit", [
        "Ich war nicht traurig.",
        "Ich war zeitweise traurig.",
        "Ich war fast die ganze Zeit traurig.",
        "Ich war so traurig, dass ich es kaum ertragen konnte."
    ]),
    ("Pessimismus", [
        "Ich hatte Hoffnung fuer die naehere Zukunft.",
        "Ich war zwischenzeitlich entmutigt.",
        "Ich hatte wenig Hoffnung, dass sich etwas verbessert.",
        "Ich hatte keine Hoffnung fuer die naehere Zukunft."
    ]),
    ("Gefuehl des Versagens", [
        "Ich hatte kein Gefuehl des Versagens.",
        "Ich habe mich gelegentlich als gescheitert gefuehlt.",
        "Ich habe mehrere Misserfolge wahrgenommen.",
        "Ich habe mich durchgehend als Versager gefuehlt."
    ]),
    ("Verlust von Freude", [
        "Ich konnte mich an Dingen erfreuen.",
        "Meine Freude war zwischendurch vermindert.",
        "Ich konnte mich kaum noch freuen.",
        "Ich konnte mich an nichts erfreuen."
    ]),
    ("Schuldgefuehle", [
        "Ich hatte keine Schuldgefuehle.",
        "Ich fuehlte mich wegen mancher Dinge schuldig.",
        "Ich hatte stark ausgepraegte Schuldgefuehle.",
        "Ich fuehlte mich durchgehend schuldig."
    ]),
    ("Gefuehl bestraft zu werden", [
        "Ich hatte nicht das Gefuehl, bestraft zu werden.",
        "Ich hatte zeitweise das Gefuehl, ich koennte bestraft werden.",
        "Ich erwartete, bestraft zu werden.",
        "Ich war ueberzeugt, bestraft zu werden."
    ]),
    ("Selbstabwertung", [
        "Mein Selbstwertgefuehl war wie gewohnt.",
        "Ich hatte gelegentlich weniger Selbstvertrauen.",
        "Ich war mit mir selbst unzufrieden.",
        "Ich mochte mich gar nicht."
    ]),
    ("Selbstkritik", [
        "Ich habe mich nicht besonders selbstkritisch gesehen.",
        "Ich war zeitweise kritischer mit mir als sonst.",
        "Ich machte mir viele Vorwuerfe.",
        "Ich gab mir fuer alles die Schuld."
    ]),
    ("Suizidgedanken", [
        "Ich hatte keine Gedanken an Selbsttoetung.",
        "Ich hatte gelegentlich Gedanken daran, aber keine Absicht.",
        "Ich haette manchmal nicht mehr leben wollen.",
        "Ich haette mich umgebracht, wenn ich gekonnt haette."
    ]),
    ("Weinen", [
        "Ich habe nicht geweint.",
        "Ich war zeitweise den Traenen nahe.",
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
        "Ich hatte Interesse an Aktivitaeten.",
        "Mein Interesse war zwischenzeitlich reduziert.",
        "Ich hatte kaum Interesse an irgendetwas.",
        "Ich konnte mich fuer nichts interessieren."
    ]),
    ("Entscheidungsschwierigkeiten", [
        "Ich konnte Entscheidungen wie gewohnt treffen.",
        "Entscheidungen fielen mir zeitweise schwerer.",
        "Es fiel mir deutlich schwerer, mich zu entscheiden.",
        "Ich konnte keine Entscheidungen treffen."
    ]),
    ("Wertlosigkeitsgefuehl", [
        "Mein Selbstwertgefuehl war normal.",
        "Ich fuehlte mich manchmal weniger wertvoll.",
        "Ich fuehlte mich anderen unterlegen.",
        "Ich fuehlte mich voellig wertlos."
    ]),
    ("Energieverlust", [
        "Ich hatte normale Energie.",
        "Ich fuehlte mich zwischendurch etwas erschoepft.",
        "Ich konnte wenig machen.",
        "Ich war zu erschoepft, um etwas zu tun."
    ]),
    ("Schlafveraenderung", [
        "Mein Schlaf war wie gewoehnlich.",
        "Ich habe etwas mehr geschlafen als sonst.",
        "Ich habe etwas weniger geschlafen als sonst.",
        "Ich habe deutlich mehr geschlafen als sonst.",
        "Ich habe deutlich weniger geschlafen als sonst.",
        "Ich habe fast durchgehend geschlafen.",
        "Ich bin ein bis zwei Stunden zu frueh aufgewacht."
    ]),
    ("Reizbarkeit", [
        "Ich war nicht reizbarer als sonst.",
        "Ich war zeitweise leicht reizbar.",
        "Ich war oft sehr gereizt.",
        "Ich war die meiste Zeit durchgehend gereizt."
    ]),
    ("Appetitveraenderung", [
        "Mein Appetit war wie gewohnt.",
        "Ich hatte zwischendurch weniger Appetit.",
        "Ich hatte zwischendurch mehr Appetit.",
        "Ich hatte deutlich weniger Appetit.",
        "Ich hatte deutlich mehr Appetit.",
        "Ich hatte gar keinen Appetit.",
        "Ich hatte staendig Heisshunger."
    ]),
    ("Konzentrationsprobleme", [
        "Meine Konzentration war wie gewohnt.",
        "Ich konnte mich zeitweise schlechter konzentrieren.",
        "Ich konnte mich kaum noch laenger konzentrieren.",
        "Ich konnte mich gar nicht konzentrieren."
    ]),
    ("Muedigkeit/Erschoepfung", [
        "Ich war nicht mueder als sonst.",
        "Ich wurde schneller muede.",
        "Ich konnte vieles nicht tun.",
        "Ich war fuer fast alles zu muede."
    ]),
    ("Libidoverlust", [
        "Mein sexuelles Interesse war wie gewoehnlich.",
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

def interpret_asrm14(core, total, psychosis_scores):
    kerntext = ""
    gesamttext = ""
    if core < 6:
        kerntext = "Kern-ASRM: Unauffaellig (0-5)"
    elif core <= 12:
        kerntext = "Kern-ASRM: Auffaellig (6-12, Hypomanie/Manie)"
    else:
        kerntext = "Kern-ASRM: Schwere Manie (>12)"

    if total < 17:
        gesamttext = "Gesamt-ASRM: Unauffaellig (<17)"
    elif total <= 35:
        gesamttext = "Gesamt-ASRM: Auffaellig (17-35, Hypomanie/Manie)"
    else:
        gesamttext = "Gesamt-ASRM: Schwere Manie (>35)"
    warntext = ""
    if any([x >= 1 for x in psychosis_scores]):
        warntext = "\n**Achtung:** Psychotische Symptome vorhanden! Bitte aerztliche Abklaerung!"
    return f"{kerntext}\n{gesamttext}{warntext}"

def interpret_bdi(score):
    if score <= 13:
        return "Minimale depressive Symptome"
    elif score <= 19:
        return "Leichte Symptome"
    elif score <= 28:
        return "Maessige Symptome"
    else:
        return "Schwere Symptome"

asrm14_text = interpret_asrm14(asrm_core, asrm_total, psychosis_scores)
bdi_text = interpret_bdi(bdi_sum)

st.write(f"**Kern-ASRM (1-5) Punktzahl:** {asrm_core} von 20")
st.write(f"**Gesamt-ASRM (1-14) Punktzahl:** {asrm_total} von 56")
st.markdown(f"- **ASRM-Interpretation:**\n{asrm14_text}")
st.write(f"**BDI-II Gesamtpunktzahl:** {bdi_sum}")
st.markdown(f"- **BDI-II-Interpretation:** {bdi_text}")
# === Mood-Matrix (Range, zwei Punkte, schwarzer Strich, BDI-Schwellenwerte, Score-Labels) ===
st.subheader("Mischzustandsmatrix (ASRM vs. BDI)")

fig, ax = plt.subplots(figsize=(8, 6))

ax.set_xlim(0, 56)
ax.set_ylim(0, 63)
ax.set_xlabel("14-Item ASRM (Manie/Mischzustand)")
ax.set_ylabel("BDI-II (Depression)")

# ASRM Schwellen
ax.axvline(6, color="grey", linestyle="--", label="Cutoff Kern: 6")
ax.axvline(17, color="orange", linestyle="--", label="Cutoff Gesamt: 17")
ax.axvline(35, color="red", linestyle="--", label="Schwere Manie: 35")

# BDI-II Schwellenlinien und Labels
ax.axhline(14, color="#1976d2", linestyle=":", label="BDI: leicht (14)")
ax.axhline(20, color="#ffa726", linestyle=":", label="BDI: mäßig (20)")
ax.axhline(29, color="#d32f2f", linestyle=":", label="BDI: schwer (29)")
ax.text(57, 14, va="center", color="#1976d2", fontsize=10)
ax.text(57, 20, va="center", color="#ffa726", fontsize=10)
ax.text(57, 29, va="center", color="#d32f2f", fontsize=10)

# Quadranten-Labels
ax.text(5, 60, "Depressiv", fontsize=10)
ax.text(35, 5, "Manisch", fontsize=10)
ax.text(35, 60, "Mischzustand", fontsize=10)
ax.text(5, 5, "Unauffaellig", fontsize=10)

# Schwarzer Range-Strich zwischen beiden Punkten auf dem BDI-Wert
ax.plot([asrm_core, asrm_total], [bdi_sum, bdi_sum], color="black", linewidth=4, zorder=2)

# Linker Marker: Kern-ASRM
ax.plot(asrm_core, bdi_sum, "o", color="#1976d2", markersize=13, label="Kern-ASRM (1–5)", zorder=3)
ax.text(asrm_core, bdi_sum + 2.1, f"ASRM: {asrm_core}", ha="center", color="#1976d2", fontsize=12, fontweight="bold", zorder=4)
# Depressionsscore links neben dem Punkt
ax.text(asrm_core - 2, bdi_sum, f"BDI: {bdi_sum}", ha="right", va="center", color="#333", fontsize=11, fontweight="bold", zorder=5)

# Rechter Marker: Gesamt-ASRM
ax.plot(asrm_total, bdi_sum, "o", color="#b71c1c", markersize=13, label="Gesamt-ASRM (1–14)", zorder=3)
ax.text(asrm_total, bdi_sum + 2.1, f"{asrm_total}", ha="center", color="#b71c1c", fontsize=12, fontweight="bold", zorder=4)

ax.legend(loc="upper left", bbox_to_anchor=(1,1))
st.pyplot(fig)

# === PDF-Export ===
st.subheader("PDF Export")
if st.button("PDF erstellen und herunterladen"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        grafik_path = tmpfile.name

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, make_ascii("Mehrmals taegliches Selbstbeurteilungs-Inventar (14-Item ASRM & BDI-II)"), ln=True, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, make_ascii(f"Name: {name}"), ln=True)
    pdf.cell(0, 10, make_ascii(f"Datum: {datum}"), ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, make_ascii("14-Item ASRM:"), ln=True)
    pdf.set_font("Arial", size=10)
    for i, (q, _) in enumerate(asrm14_items):
        pdf.multi_cell(0, 8, make_ascii(f"{i+1}. {q}: {asrm14_answers[i]}"))
    pdf.cell(0, 10, make_ascii(f"Kern-ASRM (1-5): {asrm_core}"), ln=True)
    pdf.cell(0, 10, make_ascii(f"Gesamt-ASRM (1-14): {asrm_total}"), ln=True)
    pdf.multi_cell(0, 10, make_ascii(f"ASRM-Interpretation:\n{asrm14_text}"))
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, make_ascii("BDI-II:"), ln=True)
    pdf.set_font("Arial", size=10)
    for i, (q, _) in enumerate(bdi_questions):
        pdf.multi_cell(0, 8, make_ascii(f"{i+1}. {q}: {bdi_answers[i]}"))
    pdf.cell(0, 10, make_ascii(f"Gesamtpunktzahl BDI-II: {bdi_sum}"), ln=True)
    pdf.multi_cell(0, 10, make_ascii(f"BDI-II-Interpretation: {bdi_text}"))
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, make_ascii("Mood-Matrix:"), ln=True)
    y_now = pdf.get_y()
    pdf.image(grafik_path, x=10, y=y_now, w=pdf.w-20)
    os.remove(grafik_path)
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
