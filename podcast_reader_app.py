import streamlit as st
import re
import math

# --- Costanti ---
DEFAULT_WPM = 150
# Espressione regolare per identificare le annotazioni racchiuse tra parentesi quadre.
# \[ e \]: Corrispondono letteralmente alle parentesi quadre.
# .: Corrisponde a qualsiasi carattere (eccetto newline).
# *: Corrisponde al carattere precedente zero o più volte.
# ?: Rende il '*' non-greedy, significa che corrisponderà alla corrispondenza più breve possibile.
#    Essenziale per gestire correttamente multiple annotazioni su una riga, es. "[Nota1] testo [Nota2]".
# (): Racchiude il pattern in un gruppo di cattura, permettendo di riferirsi al testo matchato (es. con \1).
ANNOTATION_REGEX = r"(\[.*?\])"
MIN_FONT_SIZE_PX = 10
MAX_FONT_SIZE_PX = 60
DEFAULT_FONT_SIZE_PX = 20
SESSION_STATE_INITIALIZED = "session_state_initialized"
RAW_TEXT = "raw_text"
SEGMENTS = "segments"
CURRENT_SEGMENT_INDEX = "current_segment_index"
FONT_SIZE_PX = "font_size_px"
USER_WPM = "user_wpm"
UPLOADED_FILE_NAME = "uploaded_file_name"

# --- Funzioni di Utility ---

def initialize_session_state():
    """Inizializza le variabili di session_state se non sono già presenti."""
    if SESSION_STATE_INITIALIZED not in st.session_state:
        st.session_state[RAW_TEXT] = None
        st.session_state[SEGMENTS] = []
        st.session_state[CURRENT_SEGMENT_INDEX] = 0
        st.session_state[FONT_SIZE_PX] = DEFAULT_FONT_SIZE_PX
        st.session_state[USER_WPM] = DEFAULT_WPM
        st.session_state[UPLOADED_FILE_NAME] = None
        st.session_state[SESSION_STATE_INITIALIZED] = True

def parse_and_style_annotations(text_segment: str) -> str:
    """
    Identifica le annotazioni nel formato [esempio] e le stilizza in corsivo per la visualizzazione Markdown.
    Esempio: "Testo con [Pausa] e [Altra nota]" diventa "Testo con *[Pausa]* e *[Altra nota]*".
    """
    return re.sub(ANNOTATION_REGEX, r'*\1*', text_segment)

def count_words_without_annotations(full_text: str) -> int:
    """
    Conta le parole nel testo fornito, escludendo il contenuto delle annotazioni.
    """
    if not full_text:
        return 0
    text_cleaned = re.sub(ANNOTATION_REGEX, '', full_text)
    words = text_cleaned.split()
    return len(words)

def estimate_reading_time(word_count: int, wpm: int) -> str:
    """
    Calcola il tempo di lettura stimato e lo formatta in una stringa leggibile.
    """
    if wpm <= 0:
        return "PPM deve essere maggiore di 0."
    if word_count == 0:
        return "Nessun testo da leggere."

    total_minutes_float = word_count / wpm
    total_minutes_int = int(total_minutes_float)
    remaining_seconds_float = (total_minutes_float - total_minutes_int) * 60
    total_seconds_int = math.ceil(remaining_seconds_float)

    if total_seconds_int == 60:
        total_minutes_int += 1
        total_seconds_int = 0

    if total_minutes_int == 0 and total_seconds_int == 0 and word_count > 0:
        return "Meno di 1 secondo."

    time_str_parts = []
    if total_minutes_int > 0:
        time_str_parts.append(f"{total_minutes_int} minut{'o' if total_minutes_int == 1 else 'i'}")
    if total_seconds_int > 0:
        time_str_parts.append(f"{total_seconds_int} second{'o' if total_seconds_int == 1 else 'i'}")

    if not time_str_parts:
        return "Tempo di lettura trascurabile."

    return "Circa " + " e ".join(time_str_parts)

def load_and_process_file(uploaded_file):
    """
    Legge il file Markdown caricato, lo segmenta e aggiorna lo stato della sessione.
    """
    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.get(UPLOADED_FILE_NAME):
            try:
                raw_text_bytes = uploaded_file.read()
                raw_text = raw_text_bytes.decode("utf-8")
                st.session_state[RAW_TEXT] = raw_text
                segments = [seg.strip() for seg in raw_text.split('\n\n') if seg.strip()]
                st.session_state[SEGMENTS] = segments
                st.session_state[CURRENT_SEGMENT_INDEX] = 0
                st.session_state[UPLOADED_FILE_NAME] = uploaded_file.name
                st.success(f"File '{uploaded_file.name}' caricato e processato con successo!")
                return True
            except Exception as e:
                st.error(f"Errore durante la lettura o processamento del file: {e}")
                st.session_state[RAW_TEXT] = None
                st.session_state[SEGMENTS] = []
                st.session_state[UPLOADED_FILE_NAME] = None
                return False
        return True
    return False

# --- Funzioni di Visualizzazione Streamlit ---

def display_sidebar_tools():
    """Visualizza i controlli e gli strumenti nella sidebar."""
    st.sidebar.header("🛠️ Strumenti e Opzioni")

    st.sidebar.subheader("📄 Carica Testo")
    uploaded_file = st.sidebar.file_uploader(
        "Seleziona un file Markdown (.md)",
        type=["md", "txt"]
    )

    file_processed_successfully = load_and_process_file(uploaded_file)

    st.sidebar.subheader("🔡 Dimensione Font")
    st.session_state[FONT_SIZE_PX] = st.sidebar.slider(
        "Dimensione del font (px)",
        min_value=MIN_FONT_SIZE_PX,
        max_value=MAX_FONT_SIZE_PX,
        value=st.session_state.get(FONT_SIZE_PX, DEFAULT_FONT_SIZE_PX),
        step=1
    )

    st.sidebar.subheader("⏱️ Stima Tempo di Lettura")
    st.session_state[USER_WPM] = st.sidebar.number_input(
        "Velocità di lettura (parole al minuto)",
        min_value=10,
        max_value=500,
        value=st.session_state.get(USER_WPM, DEFAULT_WPM),
        step=10
    )

    if st.session_state.get(RAW_TEXT):
        with st.spinner("Calcolo parole..."):
            word_count = count_words_without_annotations(st.session_state[RAW_TEXT])
        st.sidebar.write(f"Numero totale di parole (escluse annotazioni): {word_count}")
        estimated_time_str = estimate_reading_time(word_count, st.session_state[USER_WPM])
        st.sidebar.info(estimated_time_str)
    elif file_processed_successfully:
         st.sidebar.info("Il file caricato è vuoto o non contiene testo processabile.")
    else:
        st.sidebar.info("Carica un file per stimare il tempo di lettura.")

def display_focused_reading_view():
    """Visualizza la modalità lettura focalizzata con navigazione."""
    st.header("📖 Modalità Lettura Focalizzata")

    segments = st.session_state.get(SEGMENTS, [])
    if not segments:
        st.info("Nessun testo caricato o il testo non contiene segmenti validi. Carica un file Markdown dalla sidebar.")
        return

    current_index = st.session_state.get(CURRENT_SEGMENT_INDEX, 0)
    total_segments = len(segments)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Precedente", use_container_width=True) and current_index > 0:
            st.session_state[CURRENT_SEGMENT_INDEX] -= 1
            st.rerun()

    with col3:
        if st.button("Prossimo ➡️", use_container_width=True) and current_index < total_segments - 1:
            st.session_state[CURRENT_SEGMENT_INDEX] += 1
            st.rerun()

    if 0 <= current_index < total_segments:
        with col2:
            st.markdown(f"<p style='text-align: center; margin-top: 10px;'>Segmento {current_index + 1} di {total_segments}</p>", unsafe_allow_html=True)

        current_segment_text = segments[current_index]
        styled_segment_text = parse_and_style_annotations(current_segment_text)
        font_size = st.session_state.get(FONT_SIZE_PX, DEFAULT_FONT_SIZE_PX)

        container_style = f"font-size: {font_size}px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; background-color: #f9f9f9; min-height: 200px;"
        st.markdown(f"<div style='{container_style}'>{styled_segment_text}</div>", unsafe_allow_html=True)
    else:
        st.warning("Indice del segmento non valido. Prova a ricaricare il file.")

# --- Applicazione Principale ---
def main():
    """Funzione principale per eseguire l'applicazione Streamlit."""
    st.set_page_config(page_title="Assistente Lettura Podcast", layout="wide")
    st.title("🎙️ Assistente Lettura Podcast")
    st.caption("Carica il tuo script Markdown e leggi con focus, segmento per segmento. (Senza LLM/AI)")

    initialize_session_state()
    display_sidebar_tools()
    display_focused_reading_view()

if __name__ == "__main__":
    main()
