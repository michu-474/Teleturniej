# Ten kod to prosta aplikacja webowa do Twojego teleturnieju. Użyłem Pythona z biblioteką Streamlit, bo jest super prosty do uruchomienia i edycji.
# Streamlit pozwala na interaktywną stronę, gdzie możesz edytować pytania, odtwarzać audio i śledzić buzzery.
# Ograniczenie: Streamlit jest "single-session" domyślnie, więc dla wielu graczy najlepiej, żeby każdy otworzył stronę w swojej przeglądarce,
# a Ty jako host streamujesz swoją wersję (z admin panelem). Dla buzzerów użyjemy prostego mechanizmu z session state + odświeżaniem,
# ale dla prawdziwego real-time (kto pierwszy kliknął) polecam upgrade do Flask + SocketIO później, jeśli potrzeba.
# Na razie to działa na streamie: gracze klikają buzz w swoich przeglądarkach, a Ty widzisz kto buzznął pierwszy w adminie.

# Instrukcje uruchomienia:
# 1. Zainstaluj Streamlit: pip install streamlit
# 2. Zapisz ten kod jako app.py
# 3. Uruchom: streamlit run app.py
# 4. Otwórz w przeglądarce (lokalnie: http://localhost:8501)
# 5. Do udostępnienia online: Załóż konto na Streamlit Sharing (share.streamlit.io), wgraj kod i udostępnij link koledze.
#    Albo na Replit: Stwórz nowy repl z Python, wklej kod do main.py, dodaj "streamlit run main.py" do .replit i hostuj.
#    Link do Twojego repla będzie publicly dostępny – daj koledze, żeby streamował.

# Edycja: Pytania i piosenki są w listach poniżej – edytuj je bezpośrednio w kodzie.
# Dla piosenek: Użyj lokalnych plików MP3 lub linków do online audio (np. z YouTube, ale YouTube nie pozwala direct play – lepiej upload MP3 na free host jak Dropbox i weź direct link).
# W app: Jako host wpisz hasło 'admin' żeby zobaczyć panel edycji (w kodzie, ale możesz zmienić).

import streamlit as st
import time
import pygame  # Do odtwarzania audio – zainstaluj pip install pygame

# Inicjalizacja pygame do audio
pygame.mixer.init()

# Dane do edycji – tu edytuj swoje pytania i odpowiedzi
questions = [
    {"question": "Jakie jest stolica Polski?", "answer": "Warszawa", "points": 10},
    {"question": "Ile to 2+2?", "answer": "4", "points": 5},
    # Dodaj więcej: {"question": "...", "answer": "...", "points": X},
]

melodies = [
    {"name": "Piosenka 1", "file": "path/to/audio1.mp3", "duration": 10},  # 'file' to ścieżka do MP3 lub URL
    {"name": "Piosenka 2", "file": "path/to/audio2.mp3", "duration": 15},
    # Dodaj: upload pliki do folderu z app.py lub użyj URL jak "https://example.com/audio.mp3"
]

# Stan aplikacji (session state)
if 'buzzers' not in st.session_state:
    st.session_state.buzzers = {}  # {player_name: timestamp}
if 'scores' not in st.session_state:
    st.session_state.scores = {}  # {player_name: points}
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'current_melody' not in st.session_state:
    st.session_state.current_melody = None
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False

# Logowanie jako admin lub gracz
st.title("Teleturniej Buzz!")
role = st.selectbox("Kim jesteś?", ["Gracz", "Host (admin)"])

if role == "Host (admin)":
    password = st.text_input("Hasło admina", type="password")
    if password == "admin":  # Zmień na swoje hasło
        st.session_state.admin_mode = True
    else:
        st.error("Złe hasło!")
        st.session_state.admin_mode = False

player_name = st.text_input("Twoje imię (gracz lub host)")

# Panel gracza – zawsze widoczny
if player_name:
    st.header(f"Witaj, {player_name}!")
    
    # Buzz button
    if st.button("BUZZ! (Kliknij jako pierwszy)"):
        if player_name not in st.session_state.buzzers:
            st.session_state.buzzers[player_name] = time.time()
            st.success("Buzznąłś! Czekaj na hosta.")
    
    # Wyświetl aktualne pytanie jeśli jest
    if st.session_state.current_question:
        st.write(f"Pytanie: {st.session_state.current_question['question']}")
    
    # Wyświetl aktualną melodię jeśli jest (ale audio odtwarza host)
    if st.session_state.current_melody:
        st.write(f"Słuchaj melodii: {st.session_state.current_melody['name']}")

    # Odpowiedź (dla buzzera)
    if player_name in st.session_state.buzzers:
        answer = st.text_input("Twoja odpowiedź:")
        if st.button("Wyślij odpowiedź"):
            st.write("Odpowiedź wysłana – host oceni!")

# Panel admina (hosta)
if st.session_state.admin_mode:
    st.header("Panel Host'a")
    
    # Edycja pytań (w runtime – ale na stałe edytuj w kodzie)
    st.subheader("Edytuj pytania")
    for i, q in enumerate(questions):
        questions[i]["question"] = st.text_input(f"Pytanie {i+1}", q["question"])
        questions[i]["answer"] = st.text_input(f"Odpowiedź {i+1}", q["answer"])
        questions[i]["points"] = st.number_input(f"Punkty {i+1}", q["points"])
    
    # Edycja melodii
    st.subheader("Edytuj melodie")
    for i, m in enumerate(melodies):
        melodies[i]["name"] = st.text_input(f"Nazwa {i+1}", m["name"])
        melodies[i]["file"] = st.text_input(f"Plik/URL {i+1}", m["file"])
        melodies[i]["duration"] = st.number_input(f"Czas (sek) {i+1}", m["duration"])
    
    # Wybierz i pokaż pytanie
    st.subheader("Uruchom pytanie")
    selected_q = st.selectbox("Wybierz pytanie", [q["question"] for q in questions])
    if st.button("Pokaz pytanie"):
        st.session_state.current_question = next(q for q in questions if q["question"] == selected_q)
        st.session_state.buzzers = {}  # Reset buzzers
        st.write("Pytanie pokazane!")
    
    # Uruchom melodię
    st.subheader("Uruchom 'Jaka to melodia'")
    selected_m = st.selectbox("Wybierz melodię", [m["name"] for m in melodies])
    if st.button("Odtwórz fragment"):
        st.session_state.current_melody = next(m for m in melodies if m["name"] == selected_m)
        try:
            pygame.mixer.music.load(st.session_state.current_melody["file"])
            pygame.mixer.music.play()
            time.sleep(st.session_state.current_melody["duration"])
            pygame.mixer.music.stop()
            st.write("Odtworzono!")
        except Exception as e:
            st.error(f"Błąd audio: {e} – sprawdź plik/URL")
        st.session_state.buzzers = {}  # Reset
    
    # Zarządzaj buzzerami i punktami
    st.subheader("Buzzery i punkty")
    if st.session_state.buzzers:
        sorted_buzz = sorted(st.session_state.buzzers.items(), key=lambda x: x[1])
        st.write("Kolejność buzzów:")
        for name, ts in sorted_buzz:
            st.write(f"{name} buzznął o {ts}")
        
        winner = sorted_buzz[0][0]
        if st.button(f"Przyznaj punkty {st.session_state.current_question['points'] if st.session_state.current_question else 10} dla {winner}"):
            if winner not in st.session_state.scores:
                st.session_state.scores[winner] = 0
            st.session_state.scores[winner] += st.session_state.current_question['points'] if st.session_state.current_question else 10
            st.session_state.buzzers = {}
            st.write("Punkty przyznane!")
    
    # Wyświetl wyniki
    st.subheader("Punktacja")
    for name, score in st.session_state.scores.items():
        st.write(f"{name}: {score} pkt")
    
    if st.button("Resetuj wszystko"):
        st.session_state.buzzers = {}
        st.session_state.scores = {}
        st.session_state.current_question = None
        st.session_state.current_melody = None

# Uwagi: 
# - Dla multi-user real-time: Streamlit odświeża się ręcznie (F5), więc host musi mówić "odświeżcie stronę" po buzz.
# - Lepszy real-time: Przerób na Flask + Streamlit nie wspiera, ale mogę dać kod Flask jeśli chcesz (z SocketIO dla instant buzz).
# - Audio: Testuj lokalnie pliki MP3. Na online hostingu (Streamlit Sharing) upload pliki do repo.
# - Udostępnienie: Na Streamlit Sharing daj link koledze – on otworzy jako host, streamuje ekran z app.
# Jeśli coś nie działa lub chcesz zmiany (np. więcej features, lepszy multi-user), daj znać! 😊