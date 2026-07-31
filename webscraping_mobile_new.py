import requests, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from matplotlib.figure import Figure

import pandas as pd
import plotly.express as px


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



def obtenir_anys_seleccionats(y26, y25, y24, y23, y22):
    """Checks the boolean values of the checkboxes and returns a list of years."""
    anys = []
    if y26: anys.append("2026")
    if y25: anys.append("2025")
    if y24: anys.append("2024")
    if y23: anys.append("2023")
    if y22: anys.append("2022")
    
    # If they unchecked everything, default to the current year
    if not anys:
        anys.append(str(datetime.today().year))
        
    return anys


def executar_script(string_show_name, string_elapsed_time, show_recaptacio, show_espectadors_pagament, show_comissions, show_espectadors_convidats, anys_seleccionats):


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


    month_1 = today.month
    month_2 = today.month

    my_date = date(today.year, today.month, today.day)

    

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

    new_start_of_month = date(int(my_date.year) -1, 1, 1)
    new_end_of_month = new_start_of_month.replace(month = int(new_start_of_month.month + 1)) - timedelta(days = 1)



    #string_show_name = entrada_espectacle.get()
    #string_elapsed_time = elapsed_time.get()

    if string_elapsed_time == "Setmanes":
        divisio_any = 52
    elif string_elapsed_time == "Mesos":
        divisio_any = 12
    elif string_elapsed_time == "Avui":
        divisio_any = 1

  

    for any_str in anys_seleccionats:
        any_int = int(any_str)

        data_inici = date(any_int, 1, 1)
        
        if string_elapsed_time == "Setmanes":

            data_inici = data_inici - timedelta(days=data_inici.weekday())

            for i in range(divisio_any):
                data_fi = data_inici + timedelta(days=6)
                analysed_url = f"https://app.wip29.com/ticketing/dashboard?mode=session&start={data_inici.year}-{data_inici.month:02d}-{data_inici.day:02d}&end={data_fi.year}-{data_fi.month:02d}-{data_fi.day:02d}"

                llista_peticions.append((any_str, i, analysed_url))

                data_inici = data_inici + timedelta(days=7)

                ########

                if i == 1:
                    #first_date = new_start_of_week
                    #first_date = first_date.strftime("%d-%m-%Y")
                    first_date = new_start_of_week.strftime("%d-%m-%Y")

                new_start_of_week = new_start_of_week + timedelta(days=7)
                new_end_of_week = new_end_of_week + timedelta(days=7)

                option = 0

        elif string_elapsed_time == "Mesos":
            for i in range(divisio_any):
                data_salt = data_inici + timedelta(days = 31)
                new_end_of_month = data_salt.replace(day = 1) - timedelta(days = 1)

                analysed_url = f"https://app.wip29.com/ticketing/dashboard?mode=session&start={data_inici.year}-{data_inici.month:02d}-01&end={new_end_of_month.year}-{new_end_of_month.month:02d}-{new_end_of_month.day:02d}"

                llista_peticions.append((any_str, i, analysed_url))

                if i == 1:
                    #first_date = start_of_month
                    #first_date = first_date.strftime("%m-%Y")
                    first_date = data_inici.strftime("%d-%m-%Y")

                data_inici = new_end_of_month + timedelta(days = 1)

                data_salt = data_inici + timedelta(days = 31)
                new_end_of_month = data_salt.replace(day = 1) - timedelta(days = 1)

                option = 0

        elif string_elapsed_time == "Avui":
            #today_past = today.replace(year = espectacle_any)
            analysed_url = f"https://app.wip29.com/ticketing/dashboard?mode=session&start={today}&end={today}"
            first_date = today.strftime("%d-%m-%Y")

            llista_peticions.append((any_str, analysed_url))

            option = 1

        

    def descarregar_dades(peticio):
        any_str, index, url = peticio

        resposta = session.get(url, stream=True)

        try: 
            return any_str, index, url, resposta.json()

        except requests.exceptions.JSONDecodeError:
            # If it fails, print the actual server response to your terminal for debugging
            print(f"\n--- ERROR DE JSON ---")
            print(f"URL: {url}")
            print(f"Codi d'estat (Status): {resposta.status_code}")
            print(f"Resposta del servidor (Primers 200 caràcters):\n{resposta.text[:200]}\n")
            
            # Return empty data so the rest of the application doesn't crash
            return any_str, index, url, {'activities': []}
    
    dades_descarregades = []

    with ThreadPoolExecutor(max_workers = 13) as executor:
        dades_descarregades = list(executor.map(descarregar_dades, llista_peticions))

    # 4. Create our dictionaries and pre-fill them with zeros!
    # This ensures that if a show didn't play in February, February just stays at 0 instead of breaking the graph.
    recaptacions_per_any = {any_str: [0] * divisio_any for any_str in anys_seleccionats}
    espectadors_pagament_per_any = {any_str: [0] * divisio_any for any_str in anys_seleccionats}
    espectadors_convidats_per_any = {any_str: [0] * divisio_any for any_str in anys_seleccionats}
    comissions_per_any = {any_str: [0] * divisio_any for any_str in anys_seleccionats}

    dades_trobades = False # To check if the show actually exists in these years

    
        


    #dades_descarregades.sort(key = lambda x: x[0])

    #dates_grafic = []
    #recaptacions_grafic = []
    #espectadors_pagament_grafic = []
    #comissions_grafic = []
    
    for any_str, index, url, data_json in dades_descarregades:
        for espectacle in data_json.get('activities', []):
                
            if espectacle['activity'].startswith(string_show_name):
                dades_trobades = True

                funcions = espectacle['shows']
                espectadors_pagament = int(espectacle['tickets'])
                espectadors_convidats = int(espectacle['invitation'])
                total_entrades = espectadors_pagament + espectadors_convidats
            
                recaptacio = float(espectacle['amount'])
                recaptacio_america = f"{recaptacio:,.2f}"
                recaptacio_formatejat = recaptacio_america.replace(',', 'X').replace('.', ',').replace('X', '.')
        
                comissions = float(espectacle['commission'])
                comissions_america = f"{comissions:,.2f}"
                comissions_formatejat = comissions_america.replace(',', 'X').replace('.', ',').replace('X', '.')
                
                total = float(recaptacio) + float(comissions)
                total_america = f"{total:,.2f}"
                total_formatejat = total_america.replace(',', 'X').replace('.', ',').replace('X', '.')
                
                print(f"{analysed_url}")
                print(f"Any: {data_inici.year} / Mes: {data_inici.month:02d} / Dia: {data_inici.day:02d}")
                print(f"Espectacle: {string_show_name} | Funcions: {funcions} | Espectadors de pagament: {espectadors_pagament} | Espectadors convidats: {espectadors_convidats} | comissions: {comissions} | Total: {total_formatejat}€")

                if option == 1:
                    st.write(f"Any: {today.year} / Mes: {today.month:02d} / Dia: {today.day:02d}")
                    st.write(f"Espectacle: {string_show_name} | Funcions: {funcions} | Espectadors de pagament: {espectadors_pagament} | Total entrades: {total_entrades} | Comissions: {comissions} | Total: {total_formatejat}€")
                    st.divider()


                #dates_grafic.append(data_inici)
                #recaptacions_grafic.append(float(recaptacio))
                #espectadors_pagament_grafic.append(float(espectadors_pagament))
                #comissions_grafic.append(float(comissions))

                recaptacions_per_any[any_str][index] += recaptacio
                espectadors_pagament_per_any[any_str][index] += espectadors_pagament
                espectadors_convidats_per_any[any_str][index] += espectadors_convidats
                comissions_per_any[any_str][index] += comissions

                break

    # If the loop finished and we never found the show, tell the user!
    if not dades_trobades:
        st.warning(f"No s'han trobat dades de recaptació per a '{string_show_name}' en el període seleccionat.")
        return None


    if option == 0:
        figures_generades = [] #list to hold all graphs we are about to make

        #build recipe book based on what user checked
        graphs_to_draw = []

        colors_per_any = {
            "2026": "skyblue",
            "2025": "lightsalmon",
            "2024": "lightgreen",
            "2023": "plum",
            "2022": "khaki"
        }

        if show_recaptacio:
            graphs_to_draw.append({
                "titol": "Recaptació", 
                "dades_per_any": recaptacions_per_any,
                "color": colors_per_any,
                "symbol": "€"
            })

        if show_espectadors_pagament:
            graphs_to_draw.append({
                "titol": "Espectadors de pagament", 
                "dades_per_any": espectadors_pagament_per_any,
                "color": colors_per_any,
                "symbol": "👤€"
            })

        if show_comissions:
            graphs_to_draw.append({
                "titol": "Comissions", 
                "dades_per_any": comissions_per_any,
                "color": colors_per_any,
                "symbol": "€"
            })

        if show_espectadors_convidats:
            graphs_to_draw.append({
                "titol": "Espectadors amb invitació", 
                "dades_per_any": espectadors_convidats_per_any,
                "color": colors_per_any,
                "symbol": "👤"
            })

        for config in graphs_to_draw:
            # Make the figure slightly larger so the labels fit nicely
            #fig = Figure(figsize=(10, 6)) 
            #ax = fig.add_subplot(111)

            anys = sorted(list(config["dades_per_any"].keys()))
            num_anys = len(anys)

            # Figure out how many periods (bars) are in a single year 
            # (e.g., 12 months or 52 weeks)
            num_punts = len(config["dades_per_any"][anys[0]])

            # --- NEW: Smart X-axis Labels based on the time period ---
            if string_elapsed_time == "Mesos":
                noms_mesos = ["Gener", "Febrer", "Març", "Abril", "Maig", "Juny", 
                              "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"]
                # Grab exactly the number of months we need
                etiquetes_x = noms_mesos[:num_punts] 
                
            elif string_elapsed_time == "Setmanes":
                # Print "Setmana 1", "Setmana 2", etc.
                etiquetes_x = [f"Setmana {i+1}" for i in range(num_punts)]
                
            elif string_elapsed_time == "Avui":
                etiquetes_x = ["Avui"]
                
            else:
                etiquetes_x = [f"Període {i+1}" for i in range(num_punts)]


            dades_llista = []
            for any_label in anys:
                for i, valor in enumerate(config["dades_per_any"][any_label]):
                    dades_llista.append({
                        "Any": str(any_label),
                        "Període": etiquetes_x[i],
                        "Valor": valor
                    })

            df = pd.DataFrame(dades_llista)

            fig = px.bar(
                df,
                x="Període",
                y="Valor",
                color="Any",
                barmode="group",
                title=f"Gràfic {config['titol']} {string_show_name} Comparativa",
                text_auto='.2s'
            )

            fig.update_traces(
                #hovertemplate="<b>%{data.name}</b><br>Valor: %{y:,.2f}" + config["symbol"] + "<extra></extra>",
                hovertemplate="%{data.name} Valor: %{y:,.2f}" + config["symbol"] + "<extra></extra>",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Períodes",
                yaxis_title=f"{config['titol']} {config['symbol']}",
                legend_title="Anys",
                hovermode="x unified"
            )

            

            figures_generades.append(fig)

            # Hand the figure back to the main app instead of drawing it here
        return figures_generades
    
    else:
        return None
    



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
    st.subheader("Anys a representar")

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col1:
        year_26 = st.checkbox("2026", value=True)

    with col2:
        year_25 = st.checkbox("2025")

    with col3:
        year_24 = st.checkbox("2024")

    with col4:
        year_23 = st.checkbox("2023")

    with col5:
        year_22 = st.checkbox("2022")
        

    
    # 3. Time Period Selection
    opcions_temps = ["Mesos", "Setmanes", "Avui"]
    elapsed_time = st.selectbox("Període de temps", options=opcions_temps)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        graph_recaptació = st.checkbox("Recaptació", value=True)


    with col2:
        graph_espectadors_pagament = st.checkbox("Espectadors de pagament")
        graph_espectadors_convidats = st.checkbox("Espectadors amb invitació")


    with col3:
        graph_comissions = st.checkbox("Comissions")


    
    # 4. Run Button
    boto_generar = st.button("Generar Gràfic")
    
    if boto_generar:
        # 1. Call our new function to get the list of years (e.g., ['2026', '2024'])
        llista_anys = obtenir_anys_seleccionats(year_26, year_25, year_24, year_23, year_22)
        
        # 2. Join the list into a nice string for the spinner (e.g., "2026, 2024")
        text_anys = ", ".join(llista_anys)

        with st.spinner(f"S'està executant l'script per a: **{entrada_espectacle}** (Anys: {text_anys}, Període: {elapsed_time})..."):
            # 1. Run the script and catch the returned graph
            nous_graphs = executar_script(entrada_espectacle, elapsed_time, graph_recaptació, graph_espectadors_pagament, graph_espectadors_convidats, graph_comissions, llista_anys)


            # 2. Make sure it actually returned something
            if nous_graphs is not None:
                
                # --- THIS IS THE CRITICAL SAFETY NET ---
                # Check if Python gave us a LIST of graphs
                if isinstance(nous_graphs, list):
                    for graf in reversed(nous_graphs):
                        st.session_state.graphs.insert(0, graf)
                        
                # If Python gave us just ONE single graph
                else:
                    st.session_state.graphs.insert(0, nous_graphs)
            
            # 2. If it successfully made a graph, add it to our memory list
            #if nous_graphs:
                #for graf in reversed(nous_graphs):
                    #st.session_state.graphs.insert(0, graf)


    # 3. Draw EVERY graph currently stored in memory
    # We use enumerate() to get both the index number (i) and the graph itself
    for i, grafic_guardat in enumerate(st.session_state.graphs):
        st.plotly_chart(grafic_guardat, use_container_width=True)

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

    