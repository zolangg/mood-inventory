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

st.set_page_config(page_title="Selbstbeurteilungsbogen", layout="centered")
st.title("Selbstbeurteilungsbogen – Tagesmonitoring")
name = st.text_input("Name")
datum = st.date_input("Datum")

# === Selbstbeurteilungsbogen für manische und psychotische Symptome ===
st.header("Selbstbeurteilungsbogen für manische und psychotische Symptome")

asrm_items = [
    ("Stimmung", [
        "Ich fuehle mich nicht anders als sonst.",
        "Ich bin gelegentlich besser gelaunt oder gereizter als sonst.",
        "Ich bin haeufig deutlich besser gelaunt oder gereizt, kann es aber kontrollieren.",
        "Ich bin die meiste Zeit ungewoehnlich gehoben/gereizt, kann es kaum kontrollieren.",
        "Ich bin fast staendig euphorisch oder stark gereizt."
    ]),
    ("Hyperfokus/Spezialinteresse", [
        "Mein Interesse an meinen Themen ist wie ueblich.",
        "Ich beschaeftige mich gelegentlich intensiver mit einem Thema als sonst.",
        "Ich fokussiere haeufig sehr stark auf ein Thema, verliere dabei aber nicht die Kontrolle.",
        "Ich bin die meiste Zeit so auf ein Thema fokussiert, dass anderes vernachlaessigt wird.",
        "Ich bin fast ununterbrochen extrem fixiert und kann kaum abschalten."
    ]),
    ("Schlafbeduerfnis", [
        "Mein Schlafbeduerfnis ist wie sonst.",
        "Ich brauche gelegentlich weniger Schlaf als sonst.",
        "Ich brauche haeufig weniger Schlaf, fuehle mich aber nicht muede.",
        "Ich schlafe kaum und bin trotzdem leistungsfaehig.",
        "Ich brauche kaum oder gar keinen Schlaf."
    ]),
    ("Gedankenfluss", [
        "Meine Gedanken sind ruhig wie ueblich.",
        "Gelegentlich habe ich mehr Ideen oder Gedanken als sonst.",
        "Ich habe haeufig viele Gedanken auf einmal, kann sie aber ordnen.",
        "Ich habe die meiste Zeit viele rasende Gedanken, die mich antreiben.",
        "Meine Gedanken rasen pausenlos, ich kann sie kaum steuern."
    ]),
    ("Kommunikation", [
        "Ich spreche wie ueblich.",
        "Ich spreche gelegentlich mehr oder intensiver als sonst, meist ueber Spezialthemen.",
        "Ich spreche haeufig viel oder ausufernd ueber meine Themen.",
        "Ich rede die meiste Zeit sehr viel, vor allem monothematisch.",
        "Ich rede fast ununterbrochen, kann kaum gestoppt werden."
    ]),
    ("Ordnungs-/Strukturdrang", [
        "Mein Beduerfnis nach Ordnung und Struktur ist wie ueblich.",
        "Ich habe gelegentlich das Gefuehl, mehr Kontrolle oder Ordnung zu brauchen.",
        "Ich richte haeufig Listen, Plaene, Rituale ein, um mich zu beruhigen.",
        "Ich muss die meiste Zeit alles strukturieren, fuehle mich sonst unruhig.",
        "Mein Ordnungsdrang bestimmt fast durchgehend mein Verhalten."
    ]),
    ("Risikoreiches Verhalten", [
        "Kein risikoreiches Verhalten.",
        "Gelegentlich risikoreicher als sonst, ohne grosse Folgen.",
        "Haeufig risikoreiche Entscheidungen, kann sie meist noch kontrollieren.",
        "Die meiste Zeit handle ich impulsiv/riskant, trotz moeglicher negativer Folgen.",
        "Fast staendig impulsive, riskante Handlungen ohne Ruecksicht auf Konsequenzen."
    ]),
    ("Gefuehl besonderer Faehigkeiten/Bedeutung", [
        "Kein besonderes Gefuehl.",
        "Gelegentlich fuehle ich mich besonders talentiert/bedeutend.",
        "Haeufig habe ich das Gefuehl, besonders viel zu koennen.",
        "Die meiste Zeit bin ich ueberzeugt, aussergewoehnlich begabt zu sein.",
        "Ich bin fast staendig voellig sicher, besondere Faehigkeiten oder eine besondere Mission zu haben."
    ]),
    ("Selbstvertrauen/Selbstueberschaetzung", [
        "Mein Selbstvertrauen ist wie sonst.",
        "Gelegentlich mehr Selbstvertrauen als ueblich.",
        "Haeufig sehr selbstsicher, traue mir viel zu.",
        "Die meiste Zeit ueberschaetze ich meine Faehigkeiten deutlich.",
        "Ich fuehle mich fast immer absolut sicher, alles zu koennen - keine Zweifel, kein Zoegern."
    ]),
    ("Misstrauen/Paranoide Gedanken", [
        "Ich habe kein Misstrauen, fuehle mich nicht bedroht.",
        "Gelegentlich denke ich, dass andere ueber mich reden oder mich beobachten.",
        "Haeufig bin ich misstrauisch, glaube, dass man mir schaden will.",
        "Die meiste Zeit bin ich ueberzeugt, dass ich ueberwacht/verfolgt werde.",
        "Ich bin voellig sicher, dass ich verfolgt, bedroht oder kontrolliert werde."
    ]),
    ("Wahnideen", [
        "Meine Gedanken sind realistisch und nachvollziehbar.",
        "Gelegentlich glaube ich an Dinge, die anderen seltsam erscheinen koennten.",
        "Haeufig habe ich feste Ueberzeugungen, die anderen merkwuerdig vorkommen.",
        "Die meiste Zeit glaube ich an Dinge, die andere nicht nachvollziehen koennen.",
        "Ich bin voellig ueberzeugt von sonderbaren oder 'unwirklichen' Ueberzeugungen."
    ]),
    ("Stimmenhoeren/Halluzinationen", [
        "Ich hoere keine Stimmen oder Geraeusche, die nicht da sind.",
        "Gelegentlich habe ich das Gefuehl, meinen Namen zu hoeren oder dass jemand spricht, obwohl niemand da ist.",
        "Haeufig hoere ich Stimmen/Geraeusche, bin mir aber unsicher, ob sie real sind.",
        "Die meiste Zeit hoere ich Stimmen/Geraeusche, die andere nicht wahrnehmen.",
        "Ich hoere fast staendig Stimmen oder Geraeusche, die mir etwas sagen, befehlen oder mich kommentieren."
    ]),
    ("Veraenderte Wahrnehmung", [
        "Meine Wahrnehmung ist wie ueblich.",
        "Gelegentlich erscheinen mir Geraeusche, Farben oder Licht anders als sonst.",
        "Haeufig wirken meine Umgebung oder mein Koerper veraendert oder fremd.",
        "Die meiste Zeit fuehle ich mich 'unwirklich' oder nehme Dinge ganz anders wahr als sonst.",
        "Meine Wahrnehmung ist durchgehend voellig veraendert (alles wirkt fremd, bedrohlich oder verzerrt)."
    ]),
    ("Beeinflussungs- oder Kontrollgefuehle", [
        "Ich habe die volle Kontrolle ueber meine Gedanken und Handlungen.",
        "Gelegentlich habe ich das Gefuehl, dass meine Gedanken von aussen beeinflusst werden.",
        "Haeufig denke ich, dass meine Gedanken oder Handlungen von anderen gesteuert werden.",
        "Die meiste Zeit bin ich ueberzeugt, dass andere meine Gedanken lesen oder kontrollieren koennen.",
        "Ich habe staendig das Gefuehl, komplett fremdgesteuert zu sein."
    ]),
    ("Selbstverletzendes Verhalten", [
        "Ich habe keinerlei Impuls, mich selbst zu schlagen, zu stossen oder anders zu verletzen.",
        "Gelegentlich habe ich das Beduerfnis, mich selbst zu verletzen, kann es aber kontrollieren.",
        "Haeufig kommt der Impuls, mich zu verletzen - ich widerstehe manchmal, manchmal nicht.",
        "Die meiste Zeit kann ich den Drang, mich zu verletzen, kaum kontrollieren, und es kommt regelmaessig zu solchen Handlungen.",
        "Ich verletze mich fast staendig durch Schlagen, Stossen, Beissen, Kratzen oder aehnliche Impulse, ohne Kontrolle darueber."
    ]),
]

asrm_answers = []
asrm_values = []
for i, (question, options) in enumerate(asrm_items):
    answer = st.radio(f"{i+1}. {question}", options, key=f"asrm_{i}")
    asrm_answers.append(answer)
    asrm_values.append(options.index(answer))
asrm_sum = sum(asrm_values)

# === Selbstbeurteilungsbogen für depressive Symptome ===
st.header("Selbstbeurteilungsbogen für depressive Symptome")

bdi_items = [
    ("Traurigkeit/Leere", [
        "Ich fuehle mich nicht traurig oder leer.",
        "Ich bin gelegentlich traurig oder leer.",
        "Ich bin haeufig traurig oder leer.",
        "Ich bin die meiste Zeit traurig oder leer.",
        "Ich bin fast durchgehend traurig oder voellig leer."
    ]),
    ("Verlust von Freude", [
        "Ich habe an allem Freude wie sonst.",
        "Ich habe gelegentlich weniger Freude als sonst.",
        "Ich empfinde haeufig weniger Freude, auch an Lieblingsaktivitaeten.",
        "Ich kann die meiste Zeit keine Freude mehr empfinden.",
        "Ich kann ueberhaupt keine Freude mehr empfinden."
    ]),
    ("Verlust Hyperfokus/Spezialinteresse", [
        "Mein Interesse an meinen Themen ist wie ueblich.",
        "Ich habe gelegentlich weniger Lust, mich damit zu beschaeftigen.",
        "Ich habe haeufig wenig Lust, kann mich nur schwer motivieren.",
        "Ich kann mich die meiste Zeit nicht mehr dafuer begeistern.",
        "Ich kann mich ueberhaupt nicht mehr fuer meine Interessen motivieren."
    ]),
    ("Selbstwertgefuehl", [
        "Ich habe ein normales Selbstwertgefuehl.",
        "Gelegentlich habe ich Selbstzweifel.",
        "Haeufig fuehle ich mich unsicher oder minderwertig.",
        "Ich habe die meiste Zeit ein geringes Selbstwertgefuehl.",
        "Ich fuehle mich fast durchgehend wertlos und ungenuegend."
    ]),
    ("Schuld-/Versagensgefuehle", [
        "Ich mache mir keine besonderen Vorwuerfe.",
        "Gelegentlich mache ich mir mehr Gedanken ueber Fehler.",
        "Haeufig fuehle ich mich schuldig oder als Versager.",
        "Die meiste Zeit habe ich starke Schuld- oder Versagensgefuehle.",
        "Ich fuehle mich staendig vollkommen schuldig/als Versager."
    ]),
    ("Wertlosigkeitsgefuehl", [
        "Ich empfinde mich als wertvoll wie sonst.",
        "Gelegentlich habe ich Gedanken, wertlos zu sein.",
        "Haeufig habe ich das Gefuehl, anderen nichts wert zu sein.",
        "Die meiste Zeit fuehle ich mich wertlos.",
        "Ich fuehle mich staendig voellig wertlos."
    ]),
    ("Selbstkritik", [
        "Ich bin nicht selbstkritischer als sonst.",
        "Ich kritisiere mich gelegentlich mehr als sonst.",
        "Haeufig mache ich mir starke Vorwuerfe oder kritisiere mich.",
        "Die meiste Zeit bewerte ich mich sehr negativ.",
        "Ich mache mich staendig selbst fertig."
    ]),
    ("Suizidgedanken", [
        "Ich habe keine Gedanken daran, mir das Leben zu nehmen.",
        "Gelegentlich kommen solche Gedanken auf, verschwinden aber schnell.",
        "Haeufig denke ich daran, aber ohne konkrete Absicht.",
        "Ich habe die meiste Zeit Gedanken an Suizid und gelegentlich Plaene.",
        "Ich habe starke Suizidgedanken und/oder Plaene."
    ]),
    ("Selbstverletzendes Verhalten", [
        "Ich habe keinerlei Impuls, mich selbst zu schlagen, zu stossen oder anders zu verletzen.",
        "Gelegentlich habe ich das Beduerfnis, mich selbst zu verletzen, kann es aber kontrollieren.",
        "Haeufig kommt der Impuls, mich zu verletzen - ich widerstehe manchmal, manchmal nicht.",
        "Die meiste Zeit kann ich den Drang, mich zu verletzen, kaum kontrollieren, und es kommt regelmaessig zu solchen Handlungen.",
        "Ich verletze mich fast staendig durch Schlagen, Stossen, Beissen, Kratzen oder aehnliche Impulse, ohne Kontrolle darueber."
    ]),
    ("Weinen", [
        "Ich weine nicht mehr als sonst.",
        "Ich weine gelegentlich mehr.",
        "Ich muss haeufiger und leichter weinen.",
        "Ich weine die meiste Zeit oder kann das Weinen nicht kontrollieren.",
        "Ich habe den ganzen Tag ueber das Beduerfnis zu weinen."
    ]),
    ("Unruhe/Agitiertheit", [
        "Ich bin so ruhig wie sonst.",
        "Gelegentlich bin ich innerlich unruhig.",
        "Haeufig bin ich angespannt oder kann nicht stillsitzen.",
        "Ich bin die meiste Zeit sehr unruhig oder 'aufgedreht'.",
        "Ich bin fast staendig getrieben, kann kaum zur Ruhe kommen."
    ]),
    ("Entscheidungsschwierigkeiten", [
        "Ich kann Entscheidungen treffen wie immer.",
        "Gelegentlich faellt es mir schwerer als sonst.",
        "Haeufig brauche ich laenger, bin unsicher.",
        "Ich kann die meiste Zeit kaum Entscheidungen treffen.",
        "Ich kann mich fast nie entscheiden, selbst bei Kleinigkeiten."
    ]),
    ("Antrieb/Energieverlust", [
        "Ich habe normale Energie.",
        "Ich fuehle mich gelegentlich weniger energiegeladen.",
        "Haeufig bin ich muede/erschoepft.",
        "Die meiste Zeit bin ich sehr antriebslos.",
        "Ich habe praktisch keine Energie mehr."
    ]),
    ("Schlaf", [
        "Ich schlafe wie gewohnt.",
        "Gelegentlich schlafe ich schlechter oder mehr als sonst.",
        "Haeufig habe ich Ein- oder Durchschlafprobleme/Schlafe zu viel.",
        "Die meiste Zeit kann ich kaum schlafen oder nur mit Muehe.",
        "Ich schlafe fast gar nicht mehr oder nur extrem viel."
    ]),
    ("Appetitveraenderungen", [
        "Mein Appetit ist wie ueblich.",
        "Gelegentlich esse ich weniger oder mehr als sonst.",
        "Haeufig habe ich wenig/zu viel Appetit.",
        "Die meiste Zeit habe ich kaum/uebermaessigen Appetit.",
        "Ich esse fast nichts/fast staendig, ohne Hunger/Saettigungsgefuehl."
    ]),
    ("Konzentration", [
        "Ich kann mich wie gewohnt konzentrieren.",
        "Gelegentlich bin ich unkonzentriert.",
        "Haeufig habe ich Schwierigkeiten, bei der Sache zu bleiben.",
        "Die meiste Zeit kann ich mich kaum konzentrieren.",
        "Ich kann mich praktisch gar nicht mehr konzentrieren."
    ]),
    ("Muedigkeit/Erschoepfung", [
        "Ich bin wie gewohnt wach/fit.",
        "Ich bin gelegentlich mueder als sonst.",
        "Haeufig bin ich sehr muede/erschoepft.",
        "Die meiste Zeit fuehle ich mich erschoepft und schlapp.",
        "Ich bin praktisch immer voellig erschoepft."
    ]),
    ("Libidoverlust", [
        "Mein sexuelles Interesse ist wie immer.",
        "Gelegentlich habe ich weniger Interesse.",
        "Haeufig ist mein sexuelles Interesse stark vermindert.",
        "Die meiste Zeit habe ich gar kein sexuelles Interesse.",
        "Ich habe keinerlei sexuelles Interesse mehr."
    ]),
]

bdi_answers = []
bdi_values = []
for i, (question, options) in enumerate(bdi_items):
    answer = st.radio(f"{i+1}. {question}", options, key=f"bdi_{i}")
    bdi_answers.append(answer)
    bdi_values.append(options.index(answer))
bdi_sum = sum(bdi_values)

# Psychotische Items markieren (wie gehabt)
psychotic_asrm_indices = list(range(9, 15))  # 10-15 (0-basiert)
psychotic_bdi_indices = [7, 8]               # Suizidgedanken, Selbstverletzung

psychotic_flag = any(asrm_values[i] >= 2 for i in psychotic_asrm_indices) or any(bdi_values[i] >= 2 for i in psychotic_bdi_indices)

# === Schwellenwerte-Auswertung ===
def interpret_asrm(score):
    if score <= 8:
        return "Normbereich (0–8)"
    elif score <= 17:
        return "Subklinisch/leichte Hypomanie (9–17)"
    elif score <= 24:
        return "Hypomanie (18–24)"
    elif score <= 35:
        return "Manie (25–35)"
    else:
        return "Schwere Manie/Psychose (>35)"

def interpret_bdi(score):
    if score <= 13:
        return "Keine/minimale Depression (0–13)"
    elif score <= 23:
        return "Leichte Depression (14–23)"
    elif score <= 34:
        return "Moderate Depression (24–34)"
    elif score <= 47:
        return "Schwere Depression (35–47)"
    else:
        return "Sehr schwere Depression (>47)"

asrm_text = interpret_asrm(asrm_sum)
bdi_text = interpret_bdi(bdi_sum)

st.subheader("Auswertung")
st.write(f"**Manie/Psychose Gesamtpunktzahl:** {asrm_sum} von 75")
st.write(f"**Depression Gesamtpunktzahl:** {bdi_sum} von 90")
st.markdown(f"- **Interpretation Manie/Psychose:**\n{asrm_text}")
st.markdown(f"- **Interpretation Depression:**\n{bdi_text}")
if psychotic_flag:
    st.error("Achtung: Es liegen auffällige psychotische oder suizidale Symptome vor! Bitte aerztlich abklaeren.")

# === Mood-Matrix (mit Range, Schwellenwerten, Score-Labels) ===
st.subheader("Stimmungs-Matrix (Manie/Psychose vs. Depression)")

fig, ax = plt.subplots(figsize=(8, 6))

ax.set_xlim(0, 75)
ax.set_ylim(0, 90)
ax.set_xlabel("Manie/Psychose Score (Selbstbeurteilungsbogen)")
ax.set_ylabel("Depression Score (Selbstbeurteilungsbogen)")

# Vertikale Schwellenlinien für Manie-Psychose
ax.axvline(8, color="#FFECB3", lw=1, linestyle="--", label="MPS: Normbereich 0-8")
ax.axvline(17, color="#FFE082", lw=1, linestyle="--", label="MPS: Leichte Hypomanie 9-17")
ax.axvline(24, color="#FFCC80", lw=1, linestyle="--", label="MPS: Hypomanie 18-24")
ax.axvline(24, color="#FFCC80", lw=1, linestyle="--", label="MPS: Manie 25-75")

# Horizontale Schwellenlinien für Depression
ax.axhline(13, color="#B3E5FC", lw=1, linestyle="--", label="DS: Normbereich 0-13")
ax.axhline(23, color="#81D4FA", lw=1, linestyle="--", label="DS: Leicht Depressiv 14-23")
ax.axhline(34, color="#4FC3F7", lw=1, linestyle="--", label="DS: Moderat Depressiv 24-34")
ax.axhline(34, color="#4FC3F7", lw=1, linestyle="--", label="DS: Schwer Depressiv 35-90")

# Bereichs-Beschriftungen (Farbe, Position, Größe)
ax.text(4, 85, "Depressiv", fontsize=11, color="#4FC3F7", weight="bold")
ax.text(48, 7, "Manisch", fontsize=11, color="#FFCC80", weight="bold")
ax.text(45, 85, "Mischzustand", fontsize=11, color="#be4d25", alpha=0.6, weight="bold")

# Punkt & Score-Label
ax.plot(asrm_sum, bdi_sum, "o", color="#333", markersize=14)
ax.text(asrm_sum, bdi_sum + 2.1, f"{asrm_sum}", ha="center", color="#333", fontsize=12, fontweight="bold")
ax.text(asrm_sum - 2, bdi_sum, f"{bdi_sum}", ha="right", va="center", color="#333", fontsize=11, fontweight="bold")

ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
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
    pdf.cell(0, 10, make_ascii("Selbstbeurteilungsbogen Tagesmonitoring"), ln=True, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, make_ascii(f"Name: {name}"), ln=True)
    pdf.cell(0, 10, make_ascii(f"Datum: {datum}"), ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, make_ascii("Manie/Psychose-Inventar:"), ln=True)
    pdf.set_font("Arial", size=10)
    for i, (q, _) in enumerate(asrm_items):
        pdf.multi_cell(0, 8, make_ascii(f"{i+1}. {q}: {asrm_answers[i]}"))
    pdf.cell(0, 10, make_ascii(f"Gesamtpunktzahl: {asrm_sum}"), ln=True)
    pdf.multi_cell(0, 10, make_ascii(f"Interpretation:\n{asrm_text}"))
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, make_ascii("Depressions-Inventar:"), ln=True)
    pdf.set_font("Arial", size=10)
    for i, (q, _) in enumerate(bdi_items):
        pdf.multi_cell(0, 8, make_ascii(f"{i+1}. {q}: {bdi_answers[i]}"))
    pdf.cell(0, 10, make_ascii(f"Gesamtpunktzahl: {bdi_sum}"), ln=True)
    pdf.multi_cell(0, 10, make_ascii(f"Interpretation:\n{bdi_text}"))
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, make_ascii("Stimmungs-Matrix:"), ln=True)
    y_now = pdf.get_y()
    pdf.image(grafik_path, x=10, y=y_now, w=pdf.w-20)
    os.remove(grafik_path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
        with open(tmpfile.name, "rb") as f:
            st.download_button(
                label="PDF herunterladen",
                data=f.read(),
                file_name=f"Selbstbeurteilungsbogen_{datum}.pdf",
                mime="application/pdf"
            )
        os.remove(tmpfile.name)
