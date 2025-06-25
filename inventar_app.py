import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os
from typing import List, Tuple, Dict

# --- KONFIGURATION & TEXTE ---

st.set_page_config(page_title="Selbstbeurteilungsbogen", layout="centered")

def make_ascii(text: str) -> str:
    """Konvertiert Umlaute und Sonderzeichen für den PDF-Export."""
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
        "“": '"', "”": '"', "„": '"', "’": "'", "‘": "'",
        "–": "-", "—": "-", "…": "...", "°": " Grad "
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# Die Fragenlisten sind jetzt Konstanten
ASRM_ITEMS = [
    ("Stimmung", ["Ich fuehle mich nicht anders als sonst.", "Ich bin gelegentlich besser gelaunt oder gereizter als sonst.", "Ich bin haeufig deutlich besser gelaunt oder gereizt, kann es aber kontrollieren.", "Ich bin die meiste Zeit ungewoehnlich gehoben/gereizt, kann es kaum kontrollieren.", "Ich bin fast staendig euphorisch oder stark gereizt."]),
    ("Hyperfokus/Spezialinteresse", ["Mein Interesse an meinen Themen ist wie ueblich.", "Ich beschaeftige mich gelegentlich intensiver mit einem Thema als sonst.", "Ich fokussiere haeufig sehr stark auf ein Thema, verliere dabei aber nicht die Kontrolle.", "Ich bin die meiste Zeit so auf ein Thema fokussiert, dass anderes vernachlaessigt wird.", "Ich bin fast ununterbrochen extrem fixiert und kann kaum abschalten."]),
    ("Schlafbeduerfnis", ["Mein Schlafbeduerfnis ist wie sonst.", "Ich brauche gelegentlich weniger Schlaf als sonst.", "Ich brauche haeufig weniger Schlaf, fuehle mich aber nicht muede.", "Ich schlafe kaum und bin trotzdem leistungsfaehig.", "Ich brauche kaum oder gar keinen Schlaf."]),
    ("Gedankenfluss", ["Meine Gedanken sind ruhig wie ueblich.", "Gelegentlich habe ich mehr Ideen oder Gedanken als sonst.", "Ich habe haeufig viele Gedanken auf einmal, kann sie aber ordnen.", "Ich habe die meiste Zeit viele rasende Gedanken, die mich antreiben.", "Meine Gedanken rasen pausenlos, ich kann sie kaum steuern."]),
    ("Kommunikation", ["Ich spreche wie ueblich.", "Ich spreche gelegentlich mehr oder intensiver als sonst, meist ueber Spezialthemen.", "Ich spreche haeufig viel oder ausufernd ueber meine Themen.", "Ich rede die meiste Zeit sehr viel, vor allem monothematisch.", "Ich rede fast ununterbrochen, kann kaum gestoppt werden."]),
    ("Ordnungs-/Strukturdrang", ["Mein Beduerfnis nach Ordnung und Struktur ist wie ueblich.", "Ich habe gelegentlich das Gefuehl, mehr Kontrolle oder Ordnung zu brauchen.", "Ich richte haeufig Listen, Plaene, Rituale ein, um mich zu beruhigen.", "Ich muss die meiste Zeit alles strukturieren, fuehle mich sonst unruhig.", "Mein Ordnungsdrang bestimmt fast durchgehend mein Verhalten."]),
    ("Risikoreiches Verhalten", ["Kein risikoreiches Verhalten.", "Gelegentlich risikoreicher als sonst, ohne grosse Folgen.", "Haeufig risikoreiche Entscheidungen, kann sie meist noch kontrollieren.", "Die meiste Zeit handle ich impulsiv/riskant, trotz moeglicher negativer Folgen.", "Fast staendig impulsive, riskante Handlungen ohne Ruecksicht auf Konsequenzen."]),
    ("Gefuehl besonderer Faehigkeiten/Bedeutung", ["Kein besonderes Gefuehl.", "Gelegentlich fuehle ich mich besonders talentiert/bedeutend.", "Haeufig habe ich das Gefuehl, besonders viel zu koennen.", "Die meiste Zeit bin ich ueberzeugt, aussergewoehnlich begabt zu sein.", "Ich bin fast staendig voellig sicher, besondere Faehigkeiten oder eine besondere Mission zu haben."]),
    ("Selbstvertrauen/Selbstueberschaetzung", ["Mein Selbstvertrauen ist wie sonst.", "Gelegentlich mehr Selbstvertrauen als ueblich.", "Haeufig sehr selbstsicher, traue mir viel zu.", "Die meiste Zeit ueberschaetze ich meine Faehigkeiten deutlich.", "Ich fuehle mich fast immer absolut sicher, alles zu koennen - keine Zweifel, kein Zoegern."]),
    ("Misstrauen/Paranoide Gedanken", ["Ich habe kein Misstrauen, fuehle mich nicht bedroht.", "Gelegentlich denke ich, dass andere ueber mich reden oder mich beobachten.", "Haeufig bin ich misstrauisch, glaube, dass man mir schaden will.", "Die meiste Zeit bin ich ueberzeugt, dass ich ueberwacht/verfolgt werde.", "Ich bin voellig sicher, dass ich verfolgt, bedroht oder kontrolliert werde."]),
    ("Wahnideen", ["Meine Gedanken sind realistisch und nachvollziehbar.", "Gelegentlich glaube ich an Dinge, die anderen seltsam erscheinen koennten.", "Haeufig habe ich feste Ueberzeugungen, die anderen merkwuerdig vorkommen.", "Die meiste Zeit glaube ich an Dinge, die andere nicht nachvollziehen koennen.", "Ich bin voellig ueberzeugt von sonderbaren oder 'unwirklichen' Ueberzeugungen."]),
    ("Stimmenhoeren/Halluzinationen", ["Ich hoere keine Stimmen oder Geraeusche, die nicht da sind.", "Gelegentlich habe ich das Gefuehl, meinen Namen zu hoeren oder dass jemand spricht, obwohl niemand da ist.", "Haeufig hoere ich Stimmen/Geraeusche, bin mir aber unsicher, ob sie real sind.", "Die meiste Zeit hoere ich Stimmen/Geraeusche, die andere nicht wahrnehmen.", "Ich hoere fast staendig Stimmen oder Geraeusche, die mir etwas sagen, befehlen oder mich kommentieren."]),
    ("Veraenderte Wahrnehmung", ["Meine Wahrnehmung ist wie ueblich.", "Gelegentlich erscheinen mir Geraeusche, Farben oder Licht anders als sonst.", "Haeufig wirken meine Umgebung oder mein Koerper veraendert oder fremd.", "Die meiste Zeit fuehle ich mich 'unwirklich' oder nehme Dinge ganz anders wahr als sonst.", "Meine Wahrnehmung ist durchgehend voellig veraendert (alles wirkt fremd, bedrohlich oder verzerrt)."]),
    ("Beeinflussungs- oder Kontrollgefuehle", ["Ich habe die volle Kontrolle ueber meine Gedanken und Handlungen.", "Gelegentlich habe ich das Gefuehl, dass meine Gedanken von aussen beeinflusst werden.", "Haeufig denke ich, dass meine Gedanken oder Handlungen von anderen gesteuert werden.", "Die meiste Zeit bin ich ueberzeugt, dass andere meine Gedanken lesen oder kontrollieren koennen.", "Ich habe staendig das Gefuehl, komplett fremdgesteuert zu sein."]),
    ("Selbstverletzendes Verhalten", ["Ich habe keinerlei Impuls, mich selbst zu schlagen, zu stossen oder anders zu verletzen.", "Gelegentlich habe ich das Beduerfnis, mich selbst zu verletzen, kann es aber kontrollieren.", "Haeufig kommt der Impuls, mich zu verletzen - ich widerstehe manchmal, manchmal nicht.", "Die meiste Zeit kann ich den Drang, mich zu verletzen, kaum kontrollieren, und es kommt regelmaessig zu solchen Handlungen.", "Ich verletze mich fast staendig durch Schlagen, Stossen, Beissen, Kratzen oder aehnliche Impulse, ohne Kontrolle darueber."]),
]
BDI_ITEMS = [
    ("Traurigkeit/Leere", ["Ich fuehle mich nicht traurig oder leer.", "Ich bin gelegentlich traurig oder leer.", "Ich bin haeufig traurig oder leer.", "Ich bin die meiste Zeit traurig oder leer.", "Ich bin fast durchgehend traurig oder voellig leer."]),
    ("Verlust von Freude", ["Ich habe an allem Freude wie sonst.", "Ich habe gelegentlich weniger Freude als sonst.", "Ich empfinde haeufig weniger Freude, auch an Lieblingsaktivitaeten.", "Ich kann die meiste Zeit keine Freude mehr empfinden.", "Ich kann ueberhaupt keine Freude mehr empfinden."]),
    ("Verlust Hyperfokus/Spezialinteresse", ["Mein Interesse an meinen Themen ist wie ueblich.", "Ich habe gelegentlich weniger Lust, mich damit zu beschaeftigen.", "Ich habe haeufig wenig Lust, kann mich nur schwer motivieren.", "Ich kann mich die meiste Zeit nicht mehr dafuer begeistern.", "Ich kann mich ueberhaupt nicht mehr fuer meine Interessen motivieren."]),
    ("Selbstwertgefuehl", ["Ich habe ein normales Selbstwertgefuehl.", "Gelegentlich habe ich Selbstzweifel.", "Haeufig fuehle ich mich unsicher oder minderwertig.", "Ich habe die meiste Zeit ein geringes Selbstwertgefuehl.", "Ich fuehle mich fast durchgehend wertlos und ungenuegend."]),
    ("Schuld-/Versagensgefuehle", ["Ich mache mir keine besonderen Vorwuerfe.", "Gelegentlich mache ich mir mehr Gedanken ueber Fehler.", "Haeufig fuehle ich mich schuldig oder als Versager.", "Die meiste Zeit habe ich starke Schuld- oder Versagensgefuehle.", "Ich fuehle mich staendig vollkommen schuldig/als Versager."]),
    ("Wertlosigkeitsgefuehl", ["Ich empfinde mich als wertvoll wie sonst.", "Gelegentlich habe ich Gedanken, wertlos zu sein.", "Haeufig habe ich das Gefuehl, anderen nichts wert zu sein.", "Die meiste Zeit fuehle ich mich wertlos.", "Ich fuehle mich staendig voellig wertlos."]),
    ("Selbstkritik", ["Ich bin nicht selbstkritischer als sonst.", "Ich kritisiere mich gelegentlich mehr als sonst.", "Haeufig mache ich mir starke Vorwuerfe oder kritisiere mich.", "Die meiste Zeit bewerte ich mich sehr negativ.", "Ich mache mich staendig selbst fertig."]),
    ("Suizidgedanken", ["Ich habe keine Gedanken daran, mir das Leben zu nehmen.", "Gelegentlich kommen solche Gedanken auf, verschwinden aber schnell.", "Haeufig denke ich daran, aber ohne konkrete Absicht.", "Ich habe die meiste Zeit Gedanken an Suizid und gelegentlich Plaene.", "Ich habe starke Suizidgedanken und/oder Plaene."]),
    ("Selbstverletzendes Verhalten", ["Ich habe keinerlei Impuls, mich selbst zu schlagen, zu stossen oder anders zu verletzen.", "Gelegentlich habe ich das Beduerfnis, mich selbst zu verletzen, kann es aber kontrollieren.", "Haeufig kommt der Impuls, mich zu verletzen - ich widerstehe manchmal, manchmal nicht.", "Die meiste Zeit kann ich den Drang, mich zu verletzen, kaum kontrollieren, und es kommt regelmaessig zu solchen Handlungen.", "Ich verletze mich fast staendig durch Schlagen, Stossen, Beissen, Kratzen oder aehnliche Impulse, ohne Kontrolle darueber."]),
    ("Weinen", ["Ich weine nicht mehr als sonst.", "Ich weine gelegentlich mehr.", "Ich muss haeufiger und leichter weinen.", "Ich weine die meiste Zeit oder kann das Weinen nicht kontrollieren.", "Ich habe den ganzen Tag ueber das Beduerfnis zu weinen."]),
    ("Unruhe/Agitiertheit", ["Ich bin so ruhig wie sonst.", "Gelegentlich bin ich innerlich unruhig.", "Haeufig bin ich angespannt oder kann nicht stillsitzen.", "Ich bin die meiste Zeit sehr unruhig oder 'aufgedreht'.", "Ich bin fast staendig getrieben, kann kaum zur Ruhe kommen."]),
    ("Entscheidungsschwierigkeiten", ["Ich kann Entscheidungen treffen wie immer.", "Gelegentlich faellt es mir schwerer als sonst.", "Haeufig brauche ich laenger, bin unsicher.", "Ich kann die meiste Zeit kaum Entscheidungen treffen.", "Ich kann mich fast nie entscheiden, selbst bei Kleinigkeiten."]),
    ("Antrieb/Energieverlust", ["Ich habe normale Energie.", "Ich fuehle mich gelegentlich weniger energiegeladen.", "Haeufig bin ich muede/erschoepft.", "Die meiste Zeit bin ich sehr antriebslos.", "Ich habe praktisch keine Energie mehr."]),
    ("Schlaf", ["Ich schlafe wie gewohnt.", "Gelegentlich schlafe ich schlechter oder mehr als sonst.", "Haeufig habe ich Ein- oder Durchschlafprobleme/Schlafe zu viel.", "Die meiste Zeit kann ich kaum schlafen oder nur mit Muehe.", "Ich schlafe fast gar nicht mehr oder nur extrem viel."]),
    ("Appetitveraenderungen", ["Mein Appetit ist wie ueblich.", "Gelegentlich esse ich weniger oder mehr als sonst.", "Haeufig habe ich wenig/zu viel Appetit.", "Die meiste Zeit habe ich kaum/uebermaessigen Appetit.", "Ich esse fast nichts/fast staendig, ohne Hunger/Saettigungsgefuehl."]),
    ("Konzentration", ["Ich kann mich wie gewohnt konzentrieren.", "Gelegentlich bin ich unkonzentriert.", "Haeufig habe ich Schwierigkeiten, bei der Sache zu bleiben.", "Die meiste Zeit kann ich mich kaum konzentrieren.", "Ich kann mich praktisch gar nicht mehr konzentrieren."]),
    ("Muedigkeit/Erschoepfung", ["Ich bin wie gewohnt wach/fit.", "Ich bin gelegentlich mueder als sonst.", "Haeufig bin ich sehr muede/erschoepft.", "Die meiste Zeit fuehle ich mich erschoepft und schlapp.", "Ich bin praktisch immer voellig erschoepft."]),
    ("Libidoverlust", ["Mein sexuelles Interesse ist wie immer.", "Gelegentlich habe ich weniger Interesse.", "Haeufig ist mein sexuelles Interesse stark vermindert.", "Die meiste Zeit habe ich gar kein sexuelles Interesse.", "Ich habe keinerlei sexuelles Interesse mehr."]),
]
PSYCHOTIC_ASRM_INDICES = list(range(9, 15))
PSYCHOTIC_BDI_INDICES = [7, 8]

# --- LOGIK- & BERECHNUNGSFUNKTIONEN ---

def create_questionnaire_section(title: str, items: List[Tuple[str, List[str]]], key_prefix: str) -> Tuple[List[str], List[int], int]:
    """Erstellt einen Abschnitt mit Radio-Buttons für einen Fragebogen und gibt Antworten und Score zurück."""
    st.header(title)
    answers, values = [], []
    for i, (question, options) in enumerate(items):
        answer = st.radio(f"{i+1}. {question}", options, key=f"{key_prefix}_{i}")
        answers.append(answer)
        values.append(options.index(answer))
    return answers, values, sum(values)

def interpret_asrm(score: int) -> str:
    if score <= 8: return "Normbereich (0–8)"
    if score <= 17: return "Subklinisch/leichte Hypomanie (9–17)"
    if score <= 24: return "Hypomanie (18–24)"
    if score <= 35: return "Manie (25–35)"
    return "Schwere Manie/Psychose (>35)"

def interpret_bdi(score: int) -> str:
    if score <= 13: return "Keine/minimale Depression (0–13)"
    if score <= 23: return "Leichte Depression (14–23)"
    if score <= 34: return "Moderate Depression (24–34)"
    if score <= 47: return "Schwere Depression (35–47)"
    return "Sehr schwere Depression (>47)"

def check_psychotic_flag(asrm_values: List[int], bdi_values: List[int]) -> bool:
    """Prüft, ob psychotische oder suizidale Symptome auffällig sind."""
    psychotic_asrm = any(asrm_values[i] >= 2 for i in PSYCHOTIC_ASRM_INDICES)
    psychotic_bdi = any(bdi_values[i] >= 2 for i in PSYCHOTIC_BDI_INDICES)
    return psychotic_asrm or psychotic_bdi

# --- VISUALISIERUNGS- & EXPORTFUNKTIONEN ---

def plot_mood_matrix(asrm_score: int, bdi_score: int) -> plt.Figure:
    """Erstellt die Stimmungs-Matrix als Matplotlib-Figur mit farbigen Zonen."""
    fig, ax = plt.subplots(figsize=(8, 6.5))
    
    # Dynamische Achsenlimits, damit der Punkt immer sichtbar ist
    max_x = max(60, asrm_score + 10)
    max_y = max(75, bdi_score + 10)
    ax.set_xlim(-2, max_x)
    ax.set_ylim(-2, max_y)
    
    ax.set_xlabel("Manie/Psychose Score")
    ax.set_ylabel("Depression Score")

    # Schwellenwerte
    manic_thresh = 18
    depressive_thresh = 24

    # Zonen mit ax.fill definieren (x-Koordinaten, y-Koordinaten der Ecken)
    # Mischzustand (oben rechts)
    ax.fill([manic_thresh, max_x, max_x, manic_thresh], [depressive_thresh, depressive_thresh, max_y, max_y], 
            '#FADBD8', alpha=0.6, label='Mischzustand')
    # Depressiv (oben links)
    ax.fill([-2, manic_thresh, manic_thresh, -2], [depressive_thresh, depressive_thresh, max_y, max_y], 
            '#D6EAF8', alpha=0.6, label='Depressiv')
    # (Hypo)Manisch (unten rechts)
    ax.fill([manic_thresh, max_x, max_x, manic_thresh], [-2, -2, depressive_thresh, depressive_thresh], 
            '#FEF9E7', alpha=0.6, label='(Hypo)Manisch')
    # Euthym (unten links)
    ax.fill([-2, manic_thresh, manic_thresh, -2], [-2, -2, depressive_thresh, depressive_thresh], 
            '#E8F8F5', alpha=0.6, label='Euthym/Stabil')

    # Punkt für den aktuellen Score zeichnen
    ax.plot(asrm_score, bdi_score, "o", color="#e74c3c", markersize=14, markeredgecolor="white", markeredgewidth=2, label="Aktueller Wert")
    ax.text(asrm_score, bdi_score, f"{asrm_score}/{bdi_score}", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    
    ax.legend(loc="upper left")
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    return fig

def generate_pdf_bytes(name: str, datum, asrm_items, asrm_answers, asrm_sum, asrm_text, bdi_items, bdi_answers, bdi_sum, bdi_text, fig: plt.Figure) -> bytes:
    """Erstellt den gesamten Bericht als PDF und gibt die Bytes zurück."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, make_ascii("Selbstbeurteilungsbogen Tagesmonitoring"), ln=True, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, make_ascii(f"Name: {name}"), ln=True)
    pdf.cell(0, 8, make_ascii(f"Datum: {datum}"), ln=True)
    pdf.ln(5)

    def write_section(title, items, answers, total_score, interpretation):
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, make_ascii(title), ln=True)
        pdf.set_font("Arial", size=9)
        for i, (q, _) in enumerate(items):
            pdf.multi_cell(0, 5, make_ascii(f"{i+1}. {q}: {answers[i]}"))
        pdf.set_font("Arial", style="B", size=10)
        pdf.cell(0, 8, make_ascii(f"Gesamtpunktzahl: {total_score}"), ln=True)
        pdf.multi_cell(0, 5, make_ascii(f"Interpretation: {interpretation}"))
        pdf.ln(5)

    write_section("Manie/Psychose-Inventar", asrm_items, asrm_answers, asrm_sum, asrm_text)
    write_section("Depressions-Inventar", bdi_items, bdi_answers, bdi_sum, bdi_text)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight', dpi=150)
        grafik_path = tmpfile.name
    
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, make_ascii("Visuelle Auswertung: Stimmungs-Matrix"), ln=True)
    pdf.image(grafik_path, x=10, w=pdf.w - 20)
    os.remove(grafik_path)

    return pdf.output(dest='S').encode('latin-1')

# --- STREAMLIT HAUPTANWENDUNG ---

def main():
    st.title("Selbstbeurteilungsbogen – Tagesmonitoring")
    name = st.text_input("Name", help="Optional, für den PDF-Export.")
    datum = st.date_input("Datum")

    asrm_answers, asrm_values, asrm_sum = create_questionnaire_section("Manisch-psychotische Symptome", ASRM_ITEMS, "asrm")
    bdi_answers, bdi_values, bdi_sum = create_questionnaire_section("Depressive Symptome", BDI_ITEMS, "bdi")

    asrm_text = interpret_asrm(asrm_sum)
    bdi_text = interpret_bdi(bdi_sum)
    is_psychotic = check_psychotic_flag(asrm_values, bdi_values)

    st.subheader("Zusammenfassende Auswertung")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Manie/Psychose Score", value=f"{asrm_sum} / {len(ASRM_ITEMS)*4}", help=asrm_text)
    with col2:
        st.metric(label="Depressions Score", value=f"{bdi_sum} / {len(BDI_ITEMS)*4}", help=bdi_text)

    if is_psychotic:
        st.error("🚨 **Achtung:** Es wurden auffällige Werte bei psychotischen, selbstverletzenden oder suizidalen Symptomen angegeben. Bitte klären Sie dies ärztlich ab!")

    st.subheader("Visuelle Einordnung in der Stimmungs-Matrix")
    mood_matrix_fig = plot_mood_matrix(asrm_sum, bdi_sum)
    st.pyplot(mood_matrix_fig)
    with st.expander("Interpretation der Matrix"):
        st.caption("""
        **Was es zeigt:** Ihre aktuellen Scores für manische und depressive Symptome in einem zweidimensionalen Raum.
        
        **Warum es wichtig ist:** Die Position Ihres Punktes visualisiert Ihren Zustand:
        - **Unten rechts (gelb):** (Hypo)manische Symptome dominieren.
        - **Oben links (blau):** Depressive Symptome dominieren.
        - **Oben rechts (rot):** Ein "Mischzustand", bei dem gleichzeitig signifikante manische und depressive Symptome vorliegen.
        - **Unten links (grün):** Euthymer oder unauffälliger Bereich.
        """)

    st.subheader("Bericht als PDF exportieren")
    if st.button("PDF generieren"):
        pdf_bytes = generate_pdf_bytes(name, datum, ASRM_ITEMS, asrm_answers, asrm_sum, asrm_text, BDI_ITEMS, bdi_answers, bdi_sum, bdi_text, mood_matrix_fig)
        st.download_button(
            label="PDF jetzt herunterladen",
            data=pdf_bytes,
            file_name=f"Selbstbeurteilungsbogen_{name}_{datum}.pdf",
            mime="application/pdf"
        )

if __name__ == '__main__':
    main()