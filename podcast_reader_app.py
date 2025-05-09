import streamlit as st
import re
import math
from st_keyup import st_keyup # Importa la nuova libreria

# --- Costanti ---
DEFAULT_WPM = 150
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

READING_BOX_BG_COLOR = "reading_box_bg_color"
READING_BOX_TEXT_COLOR = "reading_box_text_color"
LAST_SELECTED_PRESET_NAME = "last_selected_preset_name"

FOCUS_MODE_ACTIVE = "focus_mode_active" # Nuova chiave per la modalità focus

THEME_PRESETS = {
    "Luminoso (Default)": {"bg": "#F9F9F9", "text": "#333333"},
    "Scuro Intenso": {"bg": "#222222", "text": "#E0E0E0"},
    "Seppia Classico": {"bg": "#F4E9D8", "text": "#5B4636"},
    "Notturno Freddo": {"bg": "#001F3F", "text": "#DDDDDD"},
    "Verde Foresta": {"bg": "#2E3E35", "text": "#E8E8E0"},
    "Carta Pergamena": {"bg": "#FCF5E5", "text": "#5D4037"},
}
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

        default_colors = THEME_PRESETS[DEFAULT_PRESET_NAME]
        st.session_state[READING_BOX_BG_COLOR] = default_colors["bg"]
        st.session_state[READING_BOX_TEXT_COLOR] = default_colors["text"]
        st.session_state[LAST_SELECTED_PRESET_NAME] = DEFAULT_PRESET_NAME
        
        st.session_state[FOCUS_MODE_ACTIVE] = False # Inizializza la modalità focus
        
        st.session_state[SESSION_STATE_INITIALIZED] = True
    
    # Fallback per assicurare che i valori del tema e focus mode esistano
    if READING_BOX_BG_COLOR not in st.session_state:
        default_colors = THEME_PRESETS[DEFAULT_PRESET_NAME]
        st.session_state[READING_BOX_BG_COLOR] = default_colors["bg"]
    if READING_BOX_TEXT_COLOR not in st.session_state:
        default_colors = THEME_PRESETS[DEFAULT_PRESET_NAME]
        st.session_state[READING_BOX_TEXT_COLOR] = default_colors["text"]
    if LAST_SELECTED_PRESET_NAME not in st.session_state:
        st.session_state[LAST_SELECTED_PRESET_NAME] = DEFAULT_PRESET_NAME
    if FOCUS_MODE_ACTIVE not in st.session_state:
        st.session_state[FOCUS_MODE_ACTIVE] = False


def parse_and_style_annotations(text_segment: str) -> str:
    return re.sub(ANNOTATION_REGEX, r'*\1*', text_segment)

def count_words_without_annotations(full_text: str) -> int:
    if not full_text: return 0
    text_cleaned = re.sub(ANNOTATION_REGEX, '', full_text)
    return len(text_cleaned.split())

def estimate_reading_time(word_count: int, wpm: int) -> str:
    if wpm <= 0: return "PPM deve essere maggiore di 0."
    if word_count == 0: return "Nessun testo da leggere."
    total_minutes_float = word_count / wpm
    total_minutes_int = int(total_minutes_float)
    total_seconds_int = math.ceil((total_minutes_float - total_minutes_int) * 60)
    if total_seconds_int == 60:
        total_minutes_int += 1
        total_seconds_int = 0
    if total_minutes_int == 0 and total_seconds_int == 0 and word_count > 0: return "Meno di 1 secondo."
    parts = []
    if total_minutes_int > 0: parts.append(f"{total_minutes_int} minut{'o' if total_minutes_int == 1 else 'i'}")
    if total_seconds_int > 0: parts.append(f"{total_seconds_int} second{'o' if total_seconds_int == 1 else 'i'}")
    return "Circa " + " e ".join(parts) if parts else "Tempo di lettura trascurabile."

def load_and_process_file(uploaded_file):
    if uploaded_file is not None and uploaded_file.name != st.session_state.get(UPLOADED_FILE_NAME):
        try:
            raw_text = uploaded_file.read().decode("utf-8")
            st.session_state[RAW_TEXT] = raw_text
            st.session_state[SEGMENTS] = [s.strip() for s in raw_text.split('\n\n') if s.strip()]
            st.session_state[CURRENT_SEGMENT_INDEX] = 0
            st.session_state[UPLOADED_FILE_NAME] = uploaded_file.name
            st.success(f"File '{uploaded_file.name}' caricato!")
            return True
        except Exception as e:
            st.error(f"Errore lettura file: {e}")
            # Reset relevant states on error
            st.session_state[RAW_TEXT] = None
            st.session_state[SEGMENTS] = []
            st.session_state[UPLOADED_FILE_NAME] = None
            return False
    elif uploaded_file is not None and uploaded_file.name == st.session_state.get(UPLOADED_FILE_NAME):
        return True # File già caricato, non fare nulla
    return False


# --- Gestione Input Tastiera ---
def handle_keyboard_input(key_pressed_value):
    if not key_pressed_value:
        return

    current_index = st.session_state.get(CURRENT_SEGMENT_INDEX, 0)
    total_segments = len(st.session_state.get(SEGMENTS, []))
    
    action_taken = False
    if key_pressed_value == 'ArrowLeft':
        if current_index > 0:
            st.session_state[CURRENT_SEGMENT_INDEX] -= 1
            action_taken = True
    elif key_pressed_value == 'ArrowRight':
        if total_segments > 0 and current_index < total_segments - 1:
            st.session_state[CURRENT_SEGMENT_INDEX] += 1
            action_taken = True
    elif key_pressed_value == 'Escape':
        if st.session_state.get(FOCUS_MODE_ACTIVE, False):
            st.session_state[FOCUS_MODE_ACTIVE] = False
            action_taken = True
            
    if action_taken:
        st.rerun()

# --- Funzioni di Styling per Modalità Focus ---
def apply_focus_mode_styling():
    """Applica CSS per nascondere elementi in modalità focus."""
    st.markdown("""
        <style>
            /* Nasconde la sidebar */
            div[data-testid="stSidebar"] {
                display: none !important;
            }
            /* Nasconde l'header di Streamlit (se si vuole un look ancora più pulito) */
            div[data-testid="stHeader"] {
                display: none !important;
            }
            /* Rimuove padding dal contenitore principale per massimizzare lo spazio */
            .main .block-container {
                padding-top: 1rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-bottom: 1rem !important;
            }
            /* Assicura che il titolo e il caption dell'app non siano visibili se non condizionati */
            /* Questo è più per sicurezza, la logica Python dovrebbe già nasconderli */
            h1, div[data-testid="stCaptionContainer"] {
                 /* visibility: hidden; se la logica python li nasconde già, non serve */
            }
        </style>
    """, unsafe_allow_html=True)

# --- Funzioni di Visualizzazione Streamlit ---

def display_sidebar_tools():
    """Visualizza i controlli e gli strumenti nella sidebar."""
    st.sidebar.header("🛠️ Strumenti e Opzioni")

    # 1. Caricamento File
    st.sidebar.subheader("📄 Carica Testo")
    uploaded_file = st.sidebar.file_uploader("Seleziona file Markdown (.md)", type=["md", "txt"])
    file_processed = load_and_process_file(uploaded_file)

    # 2. Configurazione Dimensione Font
    st.sidebar.subheader("🔡 Dimensione Font")
    st.session_state[FONT_SIZE_PX] = st.sidebar.slider(
        "Dimensione font (px)", MIN_FONT_SIZE_PX, MAX_FONT_SIZE_PX,
        st.session_state.get(FONT_SIZE_PX, DEFAULT_FONT_SIZE_PX), 1
    )

    # 3. Personalizzazione Tema Lettura
    st.sidebar.subheader("🎨 Tema Box Lettura")
    preset_list = list(THEME_PRESETS.keys())
    try:
        idx = preset_list.index(st.session_state[LAST_SELECTED_PRESET_NAME])
    except ValueError: # Fallback se il nome del preset salvato non è più valido
        idx = 0
        st.session_state[LAST_SELECTED_PRESET_NAME] = preset_list[idx]
        # Applica colori del preset di fallback
        fb_colors = THEME_PRESETS[preset_list[idx]]
        st.session_state[READING_BOX_BG_COLOR] = fb_colors["bg"]
        st.session_state[READING_BOX_TEXT_COLOR] = fb_colors["text"]


    selected_preset = st.sidebar.selectbox(
        "Preset Tema:", options=preset_list, index=idx, key="sb_theme_preset"
    )
    if st.session_state[LAST_SELECTED_PRESET_NAME] != selected_preset:
        colors = THEME_PRESETS[selected_preset]
        st.session_state[READING_BOX_BG_COLOR] = colors["bg"]
        st.session_state[READING_BOX_TEXT_COLOR] = colors["text"]
        st.session_state[LAST_SELECTED_PRESET_NAME] = selected_preset
        st.rerun()

    bg_c = st.sidebar.color_picker("Sfondo Box:", st.session_state[READING_BOX_BG_COLOR], key="cp_bg")
    txt_c = st.sidebar.color_picker("Testo Box:", st.session_state[READING_BOX_TEXT_COLOR], key="cp_txt")

    if bg_c != st.session_state[READING_BOX_BG_COLOR] or txt_c != st.session_state[READING_BOX_TEXT_COLOR]:
        st.session_state[READING_BOX_BG_COLOR] = bg_c
        st.session_state[READING_BOX_TEXT_COLOR] = txt_c
        # Potrebbe essere utile impostare LAST_SELECTED_PRESET_NAME a un valore "Personalizzato"
        # o semplicemente lasciare che il selectbox mostri l'ultimo preset scelto
        # e l'utente vede che i colori nei picker sono diversi.
        st.rerun()
    st.sidebar.caption("Modificando i colori, crei un tema personalizzato.")

    # 4. Stima del Tempo di Lettura
    st.sidebar.subheader("⏱️ Stima Tempo di Lettura")
    st.session_state[USER_WPM] = st.sidebar.number_input(
        "Velocità lettura (PPM)", 10, 500, st.session_state.get(USER_WPM, DEFAULT_WPM), 10
    )
    if st.session_state.get(RAW_TEXT):
        # with st.spinner("Calcolo parole..."): # Rimosso per ridurre "salti" UI
        word_count = count_words_without_annotations(st.session_state[RAW_TEXT])
        st.sidebar.write(f"Parole (no annotazioni): {word_count}")
        est_time = estimate_reading_time(word_count, st.session_state[USER_WPM])
        st.sidebar.info(est_time)
    elif file_processed and not st.session_state.get(RAW_TEXT):
         st.sidebar.info("File vuoto o non processabile.")
    else:
        st.sidebar.info("Carica un file per la stima.")

    # 5. Modalità Focus Toggle
    st.sidebar.divider()
    st.sidebar.subheader("👁️ Lettura Focalizzata")
    focus_mode_toggled = st.sidebar.toggle(
        "Attiva Modalità Senza Distrazioni",
        value=st.session_state.get(FOCUS_MODE_ACTIVE, False),
        key="toggle_focus_mode",
        help="Nasconde la sidebar e altri elementi. Premi 'Esc' per uscire."
    )
    if focus_mode_toggled != st.session_state.get(FOCUS_MODE_ACTIVE, False):
        st.session_state[FOCUS_MODE_ACTIVE] = focus_mode_toggled
        st.rerun()


def display_focused_reading_view():
    """Visualizza la modalità lettura focalizzata con navigazione."""
    if not st.session_state.get(FOCUS_MODE_ACTIVE, False): # Non mostrare header se non in focus
        st.header("📖 Modalità Lettura Focalizzata")

    segments = st.session_state.get(SEGMENTS, [])
    if not segments:
        if not st.session_state.get(FOCUS_MODE_ACTIVE, False): # Mostra solo se non in focus mode
            st.info("Nessun testo caricato. Carica un file Markdown dalla sidebar.")
        return

    current_index = st.session_state.get(CURRENT_SEGMENT_INDEX, 0)
    total_segments = len(segments)

    # Navigazione con bottoni
    # Riduci lo spazio se in modalità focus
    cols_spec = [1, 1, 1] if st.session_state.get(FOCUS_MODE_ACTIVE, False) else [1, 2, 1]
    col1, col_mid, col3 = st.columns(cols_spec)

    with col1:
        if st.button("⬅️ Precedente", use_container_width=True, key="btn_prev"):
            if current_index > 0:
                st.session_state[CURRENT_SEGMENT_INDEX] -= 1
                st.rerun()
    with col3:
        if st.button("Prossimo ➡️", use_container_width=True, key="btn_next"):
            if current_index < total_segments - 1:
                st.session_state[CURRENT_SEGMENT_INDEX] += 1
                st.rerun()

    # Indicatore di Progresso (centrato o nel mezzo)
    prog_text_align = "center" if st.session_state.get(FOCUS_MODE_ACTIVE, False) else "center" # o left se col_mid è più grande
    with col_mid:
        if total_segments > 0:
            st.markdown(f"<p style='text-align: {prog_text_align}; margin-top: 10px;'>Segmento {current_index + 1} di {total_segments}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='text-align: {prog_text_align}; margin-top: 10px;'>Nessun segmento</p>", unsafe_allow_html=True)


    if 0 <= current_index < total_segments:
        current_segment_text = segments[current_index]
        styled_segment_text = parse_and_style_annotations(current_segment_text)
        font_size = st.session_state.get(FONT_SIZE_PX, DEFAULT_FONT_SIZE_PX)

        bg_color = st.session_state.get(READING_BOX_BG_COLOR, THEME_PRESETS[DEFAULT_PRESET_NAME]["bg"])
        text_color = st.session_state.get(READING_BOX_TEXT_COLOR, THEME_PRESETS[DEFAULT_PRESET_NAME]["text"])
        border_color = "#DDDDDD" # Fisso per ora

        container_style = (
            f"font-size: {font_size}px; border: 1px solid {border_color}; padding: 20px; "
            f"border-radius: 5px; background-color: {bg_color}; min-height: 300px; " # Aumentato min-height
            f"color: {text_color}; overflow-y: auto; max-height: 70vh;" # Aggiunto scroll per segmenti lunghi
        )
        st.markdown(f"<div style='{container_style}'>{styled_segment_text}</div>", unsafe_allow_html=True)
    elif total_segments > 0 : # Indice non valido ma ci sono segmenti
        st.warning("Indice del segmento non valido. Prova a ricaricare il file.")

# --- Applicazione Principale ---
def main():
    st.set_page_config(page_title="Assistente Lettura Podcast", layout="wide", initial_sidebar_state="auto")
    initialize_session_state() # Assicura che lo stato sia inizializzato

    # Listener per i tasti freccia e Esc
    # Usiamo un label vuoto per renderlo meno invadente
    # La key è importante per la gestione dello stato del componente st_keyup
    key_pressed_value = st_keyup(
        label=" ", # Label minimale
        debounce_time_ms=150, 
        key_events=['ArrowLeft', 'ArrowRight', 'Escape'], 
        key="universal_keyup" # Una chiave unica per il listener
    )
    if key_pressed_value: # Solo se c'è un input valido
        handle_keyboard_input(key_pressed_value)

    if st.session_state.get(FOCUS_MODE_ACTIVE, False):
        apply_focus_mode_styling()
        # Non chiamare display_sidebar_tools()
        # Titolo e caption sono anche omessi in modalità focus
        display_focused_reading_view()
    else:
        st.title("🎙️ Assistente Lettura Podcast")
        st.caption("Carica il tuo script Markdown e leggi con focus, segmento per segmento.")
        display_sidebar_tools()
        display_focused_reading_view()

if __name__ == "__main__":
    main()
