import requests, json, mplcursors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tkinter as tk
import streamlit as st
from tkinter import messagebox, ttk
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Create a global session, but save it in Streamlit's memory so it doesn't get erased!
if "api_session" not in st.session_state:
    st.session_state.api_session = requests.Session()

# NEW: Create a list to store multiple graphs so they don't disappear
if "graphs" not in st.session_state:
    st.session_state.graphs = []


session = st.session_state.api_session

def login(user_email, user_password):
    headers = { #we need this so the page believes we are accessing thorugh a navigator and we can actually get the hidden token that generates every time you log in
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://app.wip29.com/login",
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8"
    }

    session.headers.update(headers)

    login_url = "https://app.wip29.com/login"

    first_response = session.get(login_url)

    soup = BeautifulSoup(first_response.text, 'html.parser') #parse web 

    token_element = soup.find('input', {'name': '_token'}) #find hidden token

    print(f"{login_url}")

    

    if token_element:
        live_token = token_element.get('value')


        login_data = {
            "_token": live_token,
            "email": user_email,
            "password": user_password
        }

        login_response = session.post(login_url, data=login_data)

        print(f"{login_response}, {login_response.url}")

        if login_response.status_code == 200 and login_response.url != login_url:
            return True

    return False


            
def executar_script(string_show_name, string_year, string_elapsed_time):


    taquilla_url = "https://app.wip29.com/taquilla" #get to different url inside the web

    taquilla_response = session.get(taquilla_url)

    print(f"next URL: {taquilla_response.url}") # DEBUG LINE 1

    today = datetime.today().strftime('%Y-%m-%d') #because url changes with date, we fetch today's date to avoid hardcoding the url and get it right always

    hidden_url = f"https://app.wip29.com/ticketing/dashboard?mode=session&start={today}&end={today}" #trigger different part to show up. In this case, this triggers the API to show the data we want
    
    print(f"this is the hidden url: {hidden_url}\n")
    print(f"\nthis is the class of elapsed_time {type(elapsed_time)} and from string_elapsed_time {type(string_elapsed_time)} shows {string_elapsed_time}")
    
    #session_response = session.get(hidden_url)

    #data = session_response.json() #because this hidden url triggers an API, the output we get is json so we read it differently

    today = date.today()


    
    year_1 = (int(espectacle_any)+1)
    year_2 = year_1
    month_1 = today.month
    month_2 = today.month

    my_date = date(year_1, today.month, today.day)

    

    start_of_week = my_date - timedelta(days=my_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    if start_of_week.day >= 24:
        month_1 = today.month -1

        if month_1 == 0:
            month_1 = 12
            year_1 = year_1 -1

    if end_of_week.day <= 5:
        month_2 = today.month +1

        if month_2 == 13:
            month_2 = 1
            year_2 = year_1 +1


    week_1_url = f"https://app.wip29.com/ticketing/dashboard?mode=session&start={start_of_week.year}-{start_of_week.month:02d}-{start_of_week.day:02d}&end={end_of_week.year}-{end_of_week.month:02d}-{end_of_week.day:02d}"

    #session_2_response = session.get(week_1_url)

    #data_2 = session_2_response.json() #because this hidden url triggers an API, the output we get is json so we read it differently


    print(f"\nthis is the week url: {week_1_url}")

    #llista_activitats = data_2['activities']

    

    print("\n\nData for the requested time periods")

    if start_of_week.day >= 24:
        month_1 = today.month -1

    if month_1 == 0:
        month_1 = 12
        year_1 = year_1 -1

    if end_of_week.day <= 5:
        month_2 = today.month +1

    if month_2 == 13:
        month_2 = 1
        year_2 = year_1 +1
    
    


    llista_peticions = []
    
    current_monday = my_date - timedelta(days = my_date.weekday())
    last_week_monday = current_monday - timedelta(weeks = 1)

    new_start_of_week = last_week_monday - timedelta(weeks = 52)
    new_end_of_week = new_start_of_week + timedelta(days = 6)

    start_of_month = date(int(my_date.year) -1, my_date.month, my_date.day - (int(my_date.day) -1))
    end_of_month = start_of_month.replace(month = int(start_of_month.month + 1)) - timedelta(days = 1)



    #string_show_name = entrada_espectacle.get()
    #string_elapsed_time = elapsed_time.get()

    if string_elapsed_time == "Setmanes":
        divisio_any = 53
    elif string_elapsed_time == "Mesos":
        divisio_any = 13
    elif string_elapsed_time == "Avui":
        divisio_any = 1


    for i in range(divisio_any):
        
        if string_elapsed_time == "Setmanes":
            analysed_url = f"https://app.wip29.com/ticketing/dashboard?mode=session&start={new_start_of_week.year}-{new_start_of_week.month:02d}-{new_start_of_week.day:02d}&end={new_end_of_week.year}-{new_end_of_week.month:02d}-{new_end_of_week.day:02d}"

            llista_peticions.append((new_start_of_week, analysed_url))

            if i == 0:
                #first_date = new_start_of_week
                #first_date = first_date.strftime("%d-%m-%Y")
                first_date = new_start_of_week.strftime("%d-%m-%Y")

            new_start_of_week = new_start_of_week + timedelta(days=7)
            new_end_of_week = new_end_of_week + timedelta(days=7)

        elif string_elapsed_time == "Mesos":
            analysed_url = f"https://app.wip29.com/ticketing/dashboard?mode=session&start={start_of_month.year}-{start_of_month.month:02d}-{start_of_month.day:02d}&end={end_of_month.year}-{end_of_month.month:02d}-{end_of_month.day:02d}"

            llista_peticions.append((start_of_month, analysed_url))

            if i == 0:
                #first_date = start_of_month
                #first_date = first_date.strftime("%m-%Y")
                first_date = start_of_month.strftime("%d-%m-%Y")

            start_of_month = end_of_month + timedelta(days = 1)

            data_salt = start_of_month + timedelta(days = 31)
            end_of_month = data_salt.replace(day = 1) - timedelta(days = 1)

        elif string_elapsed_time == "Avui":
            today_past = today.replace(year = espectacle_any)
            analysed_url = f"https://app.wip29.com/ticketing/dashboard?mode=session&start={today_past}&end={today_past}"
            first_date = today_past.strftime("%d-%m-%Y")

        

    def descarregar_setmana(peticio):
        data_inici, url = peticio

        resposta = session.get(url, stream=True)

        try: 
            return data_inici, url, resposta.json()

        except requests.exceptions.JSONDecodeError:
            # If it fails, print the actual server response to your terminal for debugging
            print(f"\n--- ERROR DE JSON ---")
            print(f"URL: {url}")
            print(f"Codi d'estat (Status): {resposta.status_code}")
            print(f"Resposta del servidor (Primers 200 caràcters):\n{resposta.text[:200]}\n")
            
            # Return empty data so the rest of the application doesn't crash
            return data_inici, url, {'activities': []}
    
    dades_descarregades = []

    with ThreadPoolExecutor(max_workers = 13) as executor:
        resultats = executor.map(descarregar_setmana, llista_peticions)

        dades_descarregades = list(resultats)

    dades_descarregades.sort(key = lambda x: x[0])

    dates_grafic = []
    recaptacions_grafic = []

    for data_inici, analysed_url, data_json in dades_descarregades:
        llista_activitats = data_json.get('activities', [])

        for espectacle in llista_activitats:
            
            if espectacle['activity'].startswith(string_show_name):
                funcions = espectacle['shows']
                espectadors_pagament = espectacle['tickets']
                invitacions = espectacle['invitation']
                total_entrades = int(espectadors_pagament) + int(invitacions)
            
                recaptacio = espectacle['amount']
                recaptacio_america = f"{recaptacio:,.2f}"
                recaptacio_formatejat = recaptacio_america.replace(',', 'X').replace('.', ',').replace('X', '.')
        
                comissions = espectacle['commission']
                comissions_america = f"{comissions:,.2f}"
                comissions_formatejat = comissions_america.replace(',', 'X').replace('.', ',').replace('X', '.')
                
                total = float(recaptacio) + float(comissions)
                total_america = f"{total:,.2f}"
                total_formatejat = total_america.replace(',', 'X').replace('.', ',').replace('X', '.')
                
                print(f"{analysed_url}")
                print(f"Any: {data_inici.year} / Mes: {data_inici.month:02d} / Dia: {data_inici.day:02d}")
                print(f"Espectacle: {string_show_name} | Funcions: {funcions} | Espectadors de pagament: {espectadors_pagament} | Total entrades: {total_entrades} | Total: {total_formatejat}€")

                dates_grafic.append(data_inici)
                recaptacions_grafic.append(recaptacio)

                break



    # Make the figure slightly larger so the labels fit nicely
    fig = Figure(figsize=(10, 6)) 
    ax = fig.add_subplot(111)

    barres = ax.bar(dates_grafic, recaptacions_grafic, color='skyblue')

    ax.set_title(f"Gràfic recaptació {string_show_name} des de {first_date}")
    ax.set_xlabel("Dates")
    ax.set_ylabel("Recaptació (€)")

    # Make the Y-axis slightly taller than the highest bar so text doesn't get cut off
    if recaptacions_grafic:
        ax.set_ylim(bottom=0, top=max(recaptacions_grafic) * 1.15) 

    # --- NEW: Write the values on top of each bar ---
    for barra in barres:
        alçada = barra.get_height()
        
        if alçada > 0: # Only write the text if the bar actually has a value
            # Format the number to Catalan/European standard
            text_america = f"{alçada:,.2f}"
            text_catala = text_america.replace(',', 'X').replace('.', ',').replace('X', '.')

            int_text_america = f"{alçada:,.0f}"
            int_text_catala = int_text_america.replace(',', '.')
            
            # Place the text
            ax.text(
                barra.get_x() + barra.get_width() / 2, # X coordinate: Center of the bar
                alçada,                                # Y coordinate: Top of the bar
                f"{int_text_catala}€",                     # The text to display
                ha='center',                           # Align center horizontally
                va='bottom',                           # Align just above the bar
                fontsize=9,                            # Make text slightly smaller
                rotation=45                            # Rotate it so nearby bars don't overlap
            )

    fig.autofmt_xdate(rotation=45, ha='right')

    # Hand the figure back to the main app instead of drawing it here
    return fig

    



# ==========================================
# 2. DESIGN THE ACTUAL WINDOW
# ==========================================
# Create the main window
st.set_page_config(page_title = "Panell de Control - Teatreneu")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if not st.session_state.logged_in:
    st.title("Inici de sessió")

    with st.form("login_form"):
        email = st.text_input("E-mail")

        password = st.text_input("Password", type="password")

        boto_login = st.form_submit_button("Iniciar sessió")

        if (boto_login):
            
            is_success = login(email, password)

            if is_success:
                # Here you will run your actual requests.Session() login logic.
                # If the status_code == 200, set the state to True:
                st.session_state.logged_in = True
                st.rerun() # This instantly refreshes the page to show the dashboard
            else:
                # Tell the user if they typed it wrong!
                st.error("Error d'autenticació. Comprova el teu correu i contrassenya.")

else:
    st.title("Analítica de Taquilla")
    
    # 1. Show Selection
    opcions_espectacles = [
        "Impro Show",
        "Los Hijos",
        "Nacido al revés", 
        "Érase una vez en los 80",
        "Viejóvenes", 
        "Cleptómago - Magia con Shado",
        "VIVENDO A TODO GASS", 
        "Monologos&vermut",
        "Magia Kids",
        "Magia a la carta", 
        "Inexplicable",
        "La llibreria màgica"
    ]
    # st.selectbox replaces ttk.Combobox
    entrada_espectacle = st.selectbox(
        "Quin espectacle vols analitzar?", 
        options=opcions_espectacles,
        index=0 # Sets "Impro Show" as the default
    )
    
    # 2. Year Selection
    opcions_anys = ["2026", "2025", "2024", "2023", "2022", "2021"]
    espectacle_any = st.selectbox("Any d'inici", options=opcions_anys)
    
    # 3. Time Period Selection
    opcions_temps = ["Avui", "Setmanes", "Mesos"]
    elapsed_time = st.selectbox("Període de temps", options=opcions_temps)
    
    # 4. Run Button
    boto_generar = st.button("Generar Gràfic")
    
    if boto_generar:
        with st.spinner(f"S'està executant l'script per a: **{entrada_espectacle}** (Any: {espectacle_any}, Període: {elapsed_time})..."):
            # 1. Run the script and catch the returned graph
            nou_grafic = executar_script(entrada_espectacle, espectacle_any, elapsed_time)
            
            # 2. If it successfully made a graph, add it to our memory list
            if nou_grafic is not None:
                st.session_state.graphs.insert(0, nou_grafic)


    # 3. Draw EVERY graph currently stored in memory
    # We use enumerate() to get both the index number (i) and the graph itself
    for i, grafic_guardat in enumerate(st.session_state.graphs):
        st.pyplot(grafic_guardat)

        # Create columns to put the delete button nicely on the right side
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2: #Center the button
            if st.button ("🗑️ Eliminar aquest gràfic", key=f"delete_{i}"):
                st.session_state.graphs.pop(i) # Remove this specific graph from the memory list
                st.rerun() # Instantly refresh the page to make it disappear
        st.divider() # Adds a nice visual line between charts

    # 4. Add a button to clear the screen if things get too cluttered
    if len(st.session_state.graphs) > 0:
        if st.button("Esborrar tots els gràfics", type="primary"):
            st.session_state.graphs = [] # Empty the list
            st.rerun() # Refresh the page
