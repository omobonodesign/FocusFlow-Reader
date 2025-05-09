# Assistente Lettura Podcast 🎙️

Applicazione web semplice e intuitiva, costruita con Streamlit, per assistere gli storyteller nella lettura di testi e script per podcast. Questa applicazione **non utilizza Large Language Models (LLM) o servizi AI esterni**, ma si basa su parsing di testo locale e interazioni UI.

L'ispirazione per il formato delle annotazioni gestite dall'app (es. `[Pausa]`, `[alzando il tono]`) proviene da script di podcast dettagliati come quello di "Ada Blackjack: La Regina del Ghiaccio".

## ✨ Funzionalità Principali

* **Caricamento File Markdown**: Permette di caricare script in formato `.md` (o `.txt`).
* **Modalità Lettura Focalizzata**:
    * Visualizza il testo un segmento (paragrafo) alla volta per minimizzare distrazioni.
    * Navigazione semplice tra segmenti ("Prossimo", "Precedente").
    * Indicatore di progresso (es. "Segmento X di Y").
* **Personalizzazione dell'Interfaccia**:
    * Regolazione della dimensione del font del testo principale per una leggibilità ottimale.
* **Gestione Annotazioni**:
    * Riconosce e stilizza automaticamente le annotazioni presenti nel testo Markdown (es. `[Pausa]`, `[Suono di vento...]`), rendendole visivamente distinte (in corsivo) senza alterare il contenuto originale.
* **Stima del Tempo di Lettura**:
    * Calcola una stima del tempo di lettura totale basata sul numero di parole (escludendo le annotazioni) e una velocità di lettura (PPM) personalizzabile dall'utente.

## 🛠️ Tecnologie Utilizzate

* **Python 3**
* **Streamlit**: Per la creazione dell'interfaccia web interattiva.
* Librerie Python standard (principalmente `re` per le espressioni regolari e `math`).

## 🚀 Come Utilizzare l'Applicazione Deployata

Puoi accedere e utilizzare l'applicazione direttamente online tramite Streamlit Community Cloud:

➡️ **[Link alla tua App Streamlit Deployata - Sostituisci questo testo con il tuo URL effettivo una volta deployata]**

Semplicemente:
1.  Apri il link.
2.  Utilizza la sidebar per caricare il tuo file di script Markdown.
3.  Regola la dimensione del font se necessario.
4.  Utilizza i bottoni "Prossimo" e "Precedente" per navigare attraverso lo script nella modalità di lettura focalizzata.
5.  Consulta la stima del tempo di lettura nella sidebar.

## 📁 Struttura dei File nel Repository

* `podcast_reader_app.py`: Il codice sorgente Python principale dell'applicazione Streamlit.
* `requirements.txt`: Elenca le dipendenze Python necessarie per eseguire l'applicazione (principalmente `streamlit`).
* `README.md`: Questo file, che fornisce informazioni sul progetto.

## 💻 (Opzionale) Come Eseguire Localmente

Se desideri eseguire l'applicazione sul tuo computer locale:

1.  **Clona il repository (o scarica i file):**
    ```bash
    git clone [https://github.com/TUO_USERNAME/NOME_DEL_TUO_REPOSITORY.git](https://github.com/TUO_USERNAME/NOME_DEL_TUO_REPOSITORY.git)
    cd NOME_DEL_TUO_REPOSITORY
    ```
    (Sostituisci `TUO_USERNAME` e `NOME_DEL_TUO_REPOSITORY` con i tuoi dettagli)

2.  **Crea un ambiente virtuale (consigliato):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Su Windows: venv\Scripts\activate
    ```

3.  **Installa le dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Esegui l'applicazione Streamlit:**
    ```bash
    streamlit run podcast_reader_app.py
    ```
    L'applicazione dovrebbe aprirsi automaticamente nel tuo browser web predefinito.

---

Speriamo che questa applicazione ti sia utile!
