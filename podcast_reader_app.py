import streamlit as st
import re
import math

# --- Costanti ---
DEFAULT_WPM = 150
# Espressione regolare per identificare le annotazioni racchiuse tra parentesi quadre.
ANNOTATION_REGEX = r"(\[.*?\])"
MIN_FONT_SIZE_PX = 10
MAX_FONT_SIZE_PX = 60
DEFAULT_FONT_SIZE_PX = 20

# Chiavi per st.session_state
SESSION_STATE_INITIALIZED = "session_state_initialized"
RAW_TEXT = "raw_text"
SEGMENTS = "segments"
CURRENT_SEGMENT_INDEX = "current_segment_index"
FONT_SIZE_PX = "font_size_px"
USER_WPM = "user_wpm"
UPLOADED_FILE_NAME = "uploaded_file_name"

# Nuove chiavi per la personalizzazione del tema
READING_BOX_BG_COLOR = "reading_box_bg_color"
READING_BOX_TEXT_COLOR = "reading_box_text_color"
LAST_SELECTED_PRESET_NAME = "last_selected_preset_name"

THEME_PRESETS = {
    "Luminoso (Default)": {"bg": "#F9F9F9", "text": "#333333"},
    "Scuro Intenso": {"bg": "#222222", "text": "#E0E0E0"},
    "Seppia Classico": {"bg": "#F4E9D8", "text": "#5B4636"},
    "Notturno Freddo": {"bg": "#001F3F", "text": "#DDDDDD"},
    "Verde Foresta": {"bg": "#2E3E35", "text": "#E8E8E0"},
    "Carta Pergamena": {"bg": "#FCF5E5", "text": "#5D4037"},
}
# Il primo preset della lista sarà il default iniziale
DEFAULT_PRESET_NAME = list(THEME_PRESETS.keys())[0]

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

        # Inizializzazione stati per il tema del box di lettura
        default_colors = THEME_PRESETS[DEFAULT_PRESET_NAME]
        st.session_state[READING_BOX_BG_COLOR] = default_colors["bg"]
        st.session_state[READING_BOX_TEXT_COLOR] = default_colors["text"]
        st.session_state[LAST_SELECTED_PRESET_NAME] = DEFAULT_PRESET_NAME
        
        st.session_state[SESSION_STATE_INITIALIZED] = True
    
    # Fallback per assicurare che i valori del tema esistano
    # Utile se si aggiungono preset o si modifica il codice dopo la prima inizializzazione
    if READING_BOX_BG_COLOR not in st.session_state:
        default_colors = THEME_PRESETS[DEFAULT_PRESET_NAME]
        st.session_state[READING_BOX_BG_COLOR] = default_colors["bg"]
    if READING_BOX_TEXT_COLOR not in st.session_state:
        default_colors = THEME_PRESETS[DEFAULT_PRESET_NAME]
        st.session_state[READING_BOX_TEXT_COLOR] = default_colors["text"]
    if LAST_SELECTED_PRESET_NAME not in st.session_state:
        st.session_state[LAST_SELECTED_PRESET_NAME] = DEFAULT_PRESET_NAME


def parse_and_style_annotations(text_segment: str) -> str:
    """
    Identifica le annotazioni nel formato [esempio] e le stilizza in corsivo per la visualizzazione Markdown.
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
        if uploaded_file.name != st.session_state.get(UPLOADED_FILE_NAME): # Processa solo se è un nuovo file
            try:
                raw_text_bytes = uploaded_file.read()
                raw_text = raw_text_bytes.decode("utf-8")
                st.session_state[RAW_TEXT] = raw_text
                segments = [seg.strip() for seg in raw_text.split('\n\n') if seg.strip()]
                st.session_state[SEGMENTS] = segments
                st.session_state[CURRENT_SEGMENT_INDEX] = 0
                st.session_state[UPLOADED_FILE_NAME] = uploaded_file.name
                st.success(f"File '{uploaded_file.name}' caricato e processato!")
                return True
            except Exception as e:
                st.error(f"Errore durante la lettura o processamento del file: {e}")
                st.session_state[RAW_TEXT] = None
                st.session_state[SEGMENTS] = []
                st.session_state[UPLOADED_FILE_NAME] = None
                return False
        return True # File già caricato e non cambiato
    return False

# --- Funzioni di Visualizzazione Streamlit ---

def display_sidebar_tools():
    """Visualizza i controlli e gli strumenti nella sidebar."""
    st.sidebar.header("🛠️ Strumenti e Opzioni")

    # 1. Caricamento File
    st.sidebar.subheader("📄 Carica Testo")
    uploaded_file = st.sidebar.file_uploader(
        "Seleziona un file Markdown (.md)",
        type=["md", "txt"]
    )
    file_processed_successfully = load_and_process_file(uploaded_file)

    # 2. Configurazione Dimensione Font
    st.sidebar.subheader("🔡 Dimensione Font")
    st.session_state[FONT_SIZE_PX] = st.sidebar.slider(
        "Dimensione del font (px)",
        min_value=MIN_FONT_SIZE_PX,
        max_value=MAX_FONT_SIZE_PX,
        value=st.session_state.get(FONT_SIZE_PX, DEFAULT_FONT_SIZE_PX),
        step=1
    )

    # 3. Personalizzazione Tema Lettura
    st.sidebar.subheader("🎨 Tema Box Lettura")
    preset_options_list = list(THEME_PRESETS.keys())
    
    try:
        # Tenta di trovare l'indice del preset memorizzato nello stato
        # Questo assicura che il selectbox mostri il preset corretto all'avvio o dopo un refresh
        # se LAST_SELECTED_PRESET_NAME è ancora un nome di preset valido.
        current_preset_index = preset_options_list.index(st.session_state[LAST_SELECTED_PRESET_NAME])
    except ValueError:
        # Se LAST_SELECTED_PRESET_NAME non è più un preset valido (es. rimosso da THEME_PRESETS),
        # o se lo stato è corrotto, fai un fallback al primo preset della lista.
        current_preset_index = 0
        st.session_state[LAST_SELECTED_PRESET_NAME] = preset_options_list[current_preset_index]
        # Applica i colori di questo preset di fallback
        fallback_colors = THEME_PRESETS[st.session_state[LAST_SELECTED_PRESET_NAME]]
        st.session_state[READING_BOX_BG_COLOR] = fallback_colors["bg"]
        st.session_state[READING_BOX_TEXT_COLOR] = fallback_colors["text"]

    selected_preset_name_sidebar = st.sidebar.selectbox(
        "Scegli un tema predefinito:",
        options=preset_options_list,
        index=current_preset_index,
        key="theme_preset_selector_widget"
    )

    # Se l'utente sceglie un nuovo preset dal selectbox, applicalo
    if st.session_state[LAST_SELECTED_PRESET_NAME] != selected_preset_name_sidebar:
        chosen_colors = THEME_PRESETS[selected_preset_name_sidebar]
        st.session_state[READING_BOX_BG_COLOR] = chosen_colors["bg"]
        st.session_state[READING_BOX_TEXT_COLOR] = chosen_colors["text"]
        st.session_state[LAST_SELECTED_PRESET_NAME] = selected_preset_name_sidebar
        st.rerun() # Ricarica per applicare immediatamente e aggiornare i color picker

    # Color pickers per personalizzazione
    custom_bg_color = st.sidebar.color_picker(
        "Colore Sfondo Personalizzato:",
        value=st.session_state[READING_BOX_BG_COLOR],
        key="bg_color_picker_widget"
    )
    custom_text_color = st.sidebar.color_picker(
        "Colore Testo Personalizzato:",
        value=st.session_state[READING_BOX_TEXT_COLOR],
        key="text_color_picker_widget"
    )

    # Se i color picker vengono modificati, aggiorna lo stato
    if custom_bg_color != st.session_state[READING_BOX_BG_COLOR]:
        st.session_state[READING_BOX_BG_COLOR] = custom_bg_color
        st.rerun() # Ricarica per vedere l'effetto nel box di lettura
    if custom_text_color != st.session_state[READING_BOX_TEXT_COLOR]:
        st.session_state[READING_BOX_TEXT_COLOR] = custom_text_color
        st.rerun() # Ricarica per vedere l'effetto nel box di lettura
    
    st.sidebar.caption("Modificando i colori qui sopra, crei un tema personalizzato per il box di lettura.")

    # 4. Stima del Tempo di Lettura
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
    elif file_processed_successfully: # File caricato ma potrebbe essere vuoto
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

    # Navigazione
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

        # Recupera i colori correnti dallo stato della sessione
        bg_color = st.session_state.get(READING_BOX_BG_COLOR, THEME_PRESETS[DEFAULT_PRESET_NAME]["bg"])
        text_color = st.session_state.get(READING_BOX_TEXT_COLOR, THEME_PRESETS[DEFAULT_PRESET_NAME]["text"])
        
        # Colore del bordo fisso per semplicità, potrebbe essere personalizzato ulteriormente
        border_color = "#DDDDDD" 

        container_style = (
            f"font-size: {font_size}px; "
            f"border: 1px solid {border_color}; "
            f"padding: 20px; "
            f"border-radius: 5px; "
            f"background-color: {bg_color}; "
            f"min-height: 200px; "
            f"color: {text_color};"
        )
        st.markdown(f"<div style='{container_style}'>{styled_segment_text}</div>", unsafe_allow_html=True)
    else:
        st.warning("Indice del segmento non valido. Prova a ricaricare il file.")

# --- Applicazione Principale ---
def main():
    """Funzione principale per eseguire l'applicazione Streamlit."""
    st.set_page_config(page_title="Assistente Lettura Podcast", layout="wide")
    st.title("🎙️ Assistente Lettura Podcast")
    st.caption("Carica il tuo script Markdown e leggi con focus, segmento per segmento. (Senza LLM/AI)")

    initialize_session_state() # Assicura che lo stato sia inizializzato
    display_sidebar_tools()
    display_focused_reading_view()

if __name__ == "__main__":
    main()
