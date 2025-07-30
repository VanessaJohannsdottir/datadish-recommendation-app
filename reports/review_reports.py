from reports import data_access
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


#zeigt Businesses auf einer interaktiven Karte mit Filtern
def business_on_map_section(db:data_access.DataAccess):
    
    st.subheader("Lokale finden: Karte der Restaurants & Cafés mit Sternefiltern")
    with st.expander("ℹ️ Was zeigt diese Karte?"): 
        st.write("""
        Auf dieser Karte sieht man **Businesses mit ihrer geografischen Lage**.  
        Es kann nach **Stadt**, **Name** und **Sternebewertung** gefiltert werden.

        ### 🔍 Hier sieht man:
        - Wo sich Restaurants, Cafés oder Bars befinden  
        - Welche davon besonders **gut bewertet** sind (nach Sternen)  
        - Welche besonders viele Bewertungen haben (größere Punkte)

         **Hinweis zur Filterlogik:**  
        Wenn z. B. **"ab 3 Sterne"** ausgewählt wird, werden **alle Businesses mit mindestens 3.0 Sternen angezeigt**.

        👉 Nutze die Filter unten, um gezielt nach Orten mit dem gewünschten Bewertungsniveau zu suchen.
        """)

    if "business_on_map_section_cities" not in st.session_state:
        cities = db.cities()
        all_business = db.all_businesses()
        st.session_state.business_on_map_section_cities = cities
        st.session_state.business_on_map_section_all_business = all_business
    else:
        cities = st.session_state.business_on_map_section_cities
        all_business = st.session_state.business_on_map_section_all_business
    
    selected_cities = st.multiselect("Wähle eine oder mehrere Städte", cities,["Philadelphia"])
    
    rangecol,_,topcol=st.columns([0.6,0.1, 0.3])
    with rangecol:
        selected_names = st.multiselect("Name des Lokals auswählene", all_business)
    with topcol:
        selected_star = st.selectbox("Ab welcher Bewertung?",[1,2,3,4,5])
    
    if (
        ("business_on_map_section_selected_cities" not in st.session_state or st.session_state.business_on_map_section_selected_cities!=selected_cities) 
        or ("business_on_map_section_selected_names" not in st.session_state or st.session_state.business_on_map_section_selected_names!=selected_names)
        or ("business_on_map_section_selected_star" not in st.session_state or st.session_state.business_on_map_section_selected_star!=selected_star)
    ):
        bs = db.businesses(selected_cities, selected_star, selected_names)
        st.session_state.business_on_map_section_data = bs
    
    if len(st.session_state.business_on_map_section_data)>1:
        st.metric(label="🔍 Gefundene Einträge", value=len(bs))

    
    # Karte mit Plotly
    fig = px.scatter_mapbox(
        st.session_state.business_on_map_section_data,
        lat="latitude",
        lon="longitude",
        hover_name="name",
        hover_data=["stars", "review_count"],
        color="stars",
        size="review_count",
        zoom=11,
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},dragmode="zoom")
    st.plotly_chart(fig, use_container_width=True, config={
    "scrollZoom": True  #  DAS ist der Schlüssel!
})


 #zeigt Top_N Businesses nach thematischer Auswahl (z. B. Sauberkeit, Service)  

def top_n_section(db: data_access.DataAccess):
    st.subheader(" Bewertungstrends entdecken: Wo lohnt sich ein Besuch _ und wo nicht?")

    cities = db.cities()
 

    top_topic_options = [
        {
            "topic":"👑 Top_Rating über alle Qualitätsmerkmale",
            "color":"Blues",
            "params":[db.LBL_DELICIOUS_FOOD,db.LBL_CLEANLINESS,db.LBL_FRIENDLY_STAFF,db.LBL_PROFESSIONAL_SERVICE,db.LBL_GOOD_VALUE,db.LBL_COZY_ATMOSPHERE,db.LBL_FRESH_INGREDIENTS,db.LBL_POSITIVE],
            "desc":"""
Hier sieht man Businesses, die in mehreren Bereichen besonders positiv auffallen – etwa:

- `delicious_food` (leckeres Essen)  
- `cleanliness` (Sauberkeit)  
- `friendly_staff` (freundliches Personal)  
- `professional_service` (professioneller Service)  
- `good_value` (gutes Preis-Leistungs-Verhältnis)  
- `cozy_atmosphere` (angenehme Atmosphäre)  
- `fresh_ingredients` (frische Zutaten)  
- `positive` (insgesamt positiver Eindruck)

🔍 Hilft dabei zu entdecken, **wer auf ganzer Linie überzeugt** – und welche Lokale eine Top-Performance zeigen. und bietet eine gute Orientierung für **Empfehlungen**


    
    """
        },
        {
            "topic":"🚨 warning for unhygienic businesses",
            "color":"Reds",
            "params":[db.LBL_UNHYGIENIC,db.LBL_SPOILED,db.LBL_DIRTY],
            "desc":"""
    Hier sieht man Businesses, bei denen besonders häufig **Hygienemängel** gemeldet wurden – etwa:

- `unhygienic` (unhygienisch)  
- `spoiled` (verdorbene Produkte)  
- `dirty` (schmutzige Bedingungen)

🔍 Hilft dabei zu erkennen, **wo potenzielle Gesundheitsrisiken bestehen**,  
wo es auffällige Mängel in **Sauberkeit oder Lebensmittelqualität** gibt –  
und bietet eine gute Orientierung für **Behörden**, **Verbraucherschutz** oder das **interne Qualitätsmanagement**.

    """
            
        },
        {
            "topic":"🌟 Top_Servicequalität",
            "color":"Greens",
            "params":[db.LBL_PROFESSIONAL_SERVICE,db.LBL_FRIENDLY_STAFF],
            "desc":"""
    Hier sieht man Businesses, bei denen Gäste besonders häufig **positives Feedback zum Service** gegeben haben – etwa:

- `friendly_staff` (freundliches Personal)  
- `professional_service` (professioneller Service)

🔍 Hilft dabei zu erkennen, **wo der Service besonders überzeugt**,  
wo Gäste besonders zufrieden sind und sich gut betreut fühlen.

    """
            
        },
        {
            "topic":"⚠️ Mängel im Service. Service mit Optimierungspotenzial erkennen",
            "color":"Oranges",
            "params":[db.LBL_SLOW_SERVICE,db.LBL_RUDE_STAFF, db.LBL_UNPROFESSIONAL_SERVICE],
            "desc":"""
    
    Hier sieht man Businesses, bei denen Gäste häufig **Serviceprobleme** melden – etwa:

    - `slow_service`  (langsamer Service)  
    - `rude_staff` (unhöfliches Personal ) 
    - `unprofessional_service` (unprofessionelles Verhalten)

    🔍  Hilft dabei zu erkennen, wo häufiger Servicebeschwerden auftreten, Schwachstellen im Kundenumgang schnell zu erkennen – und gezielt zu verbessern.
    """
        },
        {
            "topic":"‼️Warnsignale aus der Küche",
            "color":"OrRd",
            "params":[db.LBL_LOW_QUALITY_INGREDIENTS,db.LBL_POOR_TASTE, db.LBL_OVERCOOKED,db.LBL_UNHYGIENIC, db.LBL_SPOILED],
            "desc":"""
    Hier sieht man Businesses, bei denen Gäste häufig **Probleme mit der Speisequalität oder der Küchenhygiene** gemeldet haben – etwa:

- `low_quality_ingredients` (minderwertige Zutaten)  
- `poor_taste` (unangenehmer Geschmack)  
- `overcooked` (verkochte Speisen)  
- `unhygienic` (mangelnde Sauberkeit in der Küche)  
- `spoiled` (verdorbene Lebensmittel)

🔍 Hilft dabei zu erkennen, **wo es in der Küche ernsthafte Qualitäts- oder Hygienemängel gibt** –  
und bietet eine wertvolle Grundlage für  **Lebensmittelkontrollen** oder **Qualitätssicherung**.

    """
                
        },
        
        {
            "topic":" ⛔ Businesses mit negativer Gesamt-Performance",
            "color":"YlOrRd",
            "params":[db.LBL_POOR_TASTE,db.LBL_UNHYGIENIC,db.LBL_DIRTY,db.LBL_SPOILED,db.LBL_RUDE_STAFF,db.LBL_UNPROFESSIONAL_SERVICE, db.LBL_SLOW_SERVICE,db.LBL_OVERPRICED, db.LBL_LOW_QUALITY_INGREDIENTS,db.LBL_NEGATIVE],
            "desc":"""
Hier sieht man Businesses, bei denen **viele negative Merkmale gleichzeitig auftreten** – etwa:

- `poor_taste` (schlechter Geschmack)  
- `unhygienic` / dirty / spoiled (Hygieneprobleme)  
- `rude_staff` / unprofessional_service / slow_service (schlechter Service)  
- `overpriced` (überteuert)  
- `low_quality_ingredients` (schlechte Zutaten)  
- `negative` (allgemein schlechte Stimmung)

🔍 Hilft dabei zu erkennen, **wo die Gesamtbewertung besonders schlecht ausfällt** – und welche Lokale man aus Sicht der Gäste eher vermeiden sollte.

    """
        }
    ]
    selected_top_topic = st.selectbox("Datenanalyse nach Wunsch auswählen",[
        top_topic_options[0]["topic"],
        top_topic_options[1]["topic"],
        top_topic_options[2]["topic"],
        top_topic_options[3]["topic"],
        top_topic_options[4]["topic"],
        top_topic_options[5]["topic"],
        
    ])
    
    rangecol,_,topcol=st.columns([0.6,0.2, 0.2])
    with rangecol:
        selected_cities=st.multiselect("Wähle eine oder mehrere Städte",cities)
    with topcol:
        top_n = st.selectbox("Top",[5,10,15,20],1)
    
    
    item = {}
    for it in top_topic_options:
        if it["topic"] == selected_top_topic:
            item = it
            break
        
    with st.expander("ℹ️ Was zeigt dieses Diagramm? (Zum Aufklappen klicken)"):
        st.write(item['desc'])   
        
    Performer=db.top_businesses(top_n,item["params"],selected_cities)
    
    fig_Performer = px.bar(
        Performer,
        x='score',
        y='name',
        color='score',
        color_continuous_scale=item["color"],
        orientation='h',

        title=item["topic"],
        labels={'name': 'Business', 'score': 'Score'}
    )
    fig_Performer.update_layout(barmode='stack', yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_Performer, use_container_width=True)

#analysiert Korrelation von Preisempfinden mit Geschmack oder Stimmung
def Preis_Leistung(db: data_access.DataAccess):
    st.subheader(" Preis-Leistungs-Analyse: Geschmack & Stimmung vs. Kosten")
    with st.expander("ℹ️ Was zeigt dieses Diagramm?"):
        st.write("""
        In diesem Bubble-Diagramm sieht man die **Korrelation zwischen dem Preis-Leistungs-Verhältnis und dem Gästeerlebnis** – also wie gut Preis und Qualität aus Sicht der Gäste zusammenpassen.

        ### 🔍 Was wird kombiniert?
        - Geschmack (lecker vs. geschmacklos) **oder** Stimmung (positiv vs. negativ)  
        mit  
        - Preisempfinden (preiswert vs. überteuert)

        💬 Jede Blase zeigt eine Kombination wie:  
        -  Teuer aber lecker  
        -  Teuer & negativ  
        -  Preiswert & positiv  
        -  Billig aber geschmacklos  

        ➕ Je **größer die Blase**, desto häufiger kommt diese Kombination in den Bewertungen vor.

        👉 Hilft dabei zu erkennen, **wo sich der Preis lohnt – und wo eher nicht**.
        """)

    #  Auswahl via Filter 
    view_option = st.selectbox(
        "Welche Perspektive möchtest du sehen?",
        options=["Geschmack vs. Preis", "Stimmung vs. Preis"]
    )
    if ("view_option" not in st.session_state or st.session_state.view_option != view_option) :
        st.session_state.view_option = view_option
        
        if view_option == "Geschmack vs. Preis":
            #  Taste-Based Correlation
            (total, p1, p2) = db.performance_by_preis(db.LBL_DELICIOUS_FOOD, db.LBL_OVERPRICED, db.LBL_GOOD_VALUE)
            (total_poor, p1_poor, p2_poor) = db.performance_by_preis(db.LBL_POOR_TASTE, db.LBL_OVERPRICED, db.LBL_GOOD_VALUE)
             #  DataFrame Construction
            data = pd.DataFrame([
                # Geschmack vs Preis
                {"Typ": "Geschmack", "Qualität": "Lecker", "Preis": "Teuer", "Kombi": " Teuer aber lecker", "Anzahl": p1},
                {"Typ": "Geschmack", "Qualität": "Lecker", "Preis": "Preiswert", "Kombi": " Perfekt ausgewogen", "Anzahl": p2},
                {"Typ": "Geschmack", "Qualität": "Geschmacklos", "Preis": "Teuer", "Kombi": " Schlecht & teuer", "Anzahl": p1_poor},
                {"Typ": "Geschmack", "Qualität": "Geschmacklos", "Preis": "Preiswert", "Kombi": " Billig aber schlecht", "Anzahl": p2_poor}
            ])
        else:
            #  Sentiment-Based Correlation 
            (total_pos, p1_pos, p2_pos) = db.performance_by_preis(db.LBL_POSITIVE, db.LBL_OVERPRICED, db.LBL_GOOD_VALUE)
            (total_neg, p1_neg, p2_neg) = db.performance_by_preis(db.LBL_NEGATIVE, db.LBL_OVERPRICED, db.LBL_GOOD_VALUE)
            #  DataFrame Construction
            data = pd.DataFrame([
                # Stimmung vs Preis
                {"Typ": "Stimmung", "Qualität": "Positiv", "Preis": "Teuer", "Kombi": " Teuer aber positiv", "Anzahl": p1_pos},
                {"Typ": "Stimmung", "Qualität": "Positiv", "Preis": "Preiswert", "Kombi": " Preiswert & positiv", "Anzahl": p2_pos},
                {"Typ": "Stimmung", "Qualität": "Negativ", "Preis": "Teuer", "Kombi": " Teuer & negativ", "Anzahl": p1_neg},
                {"Typ": "Stimmung", "Qualität": "Negativ", "Preis": "Preiswert", "Kombi": " Billig aber negativ", "Anzahl": p2_neg}
            ])
            
            # Axis Mapping 
        qualitäts_map = {
            "Lecker": 1, "Geschmacklos": 0,
            "Positiv": 1, "Negativ": 0
        }
        preis_map = {"Preiswert": 0, "Teuer": 1}
        data["x"] = data["Preis"].map(preis_map)
        data["y"] = data["Qualität"].map(qualitäts_map)

        st.session_state.Preis_Leistung = data
        
    #  Bubble Chart
    fig = px.scatter(
        st.session_state.Preis_Leistung,
        x="x",
        y="y",
        size="Anzahl",
        color="Kombi",
        hover_name="Kombi",
        text="Kombi",
        size_max=80,
        color_discrete_sequence=["#88B39A", "#d68b83", "#f4c430", "#c94c4c"]
    )

    fig.update_layout(
        title=f" {view_option} – Bewertungskombinationen",
        xaxis=dict(title="Preiswahrnehmung", tickvals=[0, 1], ticktext=["Preiswert", "Teuer"]),
        yaxis=dict(
            title="Geschmack" if view_option == "Geschmack vs. Preis" else "Stimmung",
            tickvals=[0, 1],
            ticktext=["Geschmacklos", "Lecker"] if view_option == "Geschmack vs. Preis" else ["Negativ", "Positiv"]
        ),
        showlegend=False,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
    
    
    #analysiert, wie häufig ein bestimmtes Label mit 1–5 Sternen vorkommt (Donut-Chart)

def star(db:data_access.DataAccess):
    
    st.subheader("Wie Sternebewertungen mit Alle label zusammenhängen")
    with st.expander("ℹ️ Was zeigt dieses Diagramm?"):
        st.write("""
        In diesem Diagramm wird gezeigt, wie stark bestimmte Labels mit den Sternebewertungen zusammenhängen.

        ### 🔍 Was sieht man hier?
        - Zwei Donut_Diagramme, je nach Auswahl der Labels .
        - Die Verteilung zeigt, bei welchen **Sternebewertungen** (1–5) das gewählte Label **besonders häufig** vorkommt

        💬 Beispiele:
        - Kommt `dirty` häufiger bei 1–2 Sternen vor?
        - Wird `cleanliness` öfter mit 4–5 Sternen genannt?

        ➕ So lassen sich **positive oder negative Einflussfaktoren** auf die Gesamtbewertung schnell erkennen.
        
        Wenn ein Business z. B. mehr auf Sauberkeit achtet,kann die Sternebewertung deutlich verbessern.  
        """)

    
    selected_lbl = st.multiselect("Wähle Labels zur Analyse nach Sternen",db.LABELS,max_selections=2,default=[db.LBL_CLEANLINESS,db.LBL_DIRTY])
    
    farben = [
                "#F26C4F",   
                "#F68E5F",  
                "#F3CD74",   
                "#F6E8BE",  
                "#EAE7D1",  ] 
    
    fig = go.Figure()
    annotations = []
    for idx,lbl in enumerate(selected_lbl):
        total,counts = db.performance_by_star(lbl)

        if idx==0:
            fig.add_trace(go.Pie(
                labels=["1 star", "2 star", "3 star", "4 star", "5 star"],
                values=counts,
                name=lbl,
                hole=0.5,
                domain={'x': [0, 0.48]},
                marker=dict(colors=farben),
               
            ))
            annotations.append(dict(text=f"<b>{lbl}</b>", x=0.24, y=0.5, font_size=16, showarrow=False, xanchor='center', yanchor='middle' ))

        if idx == 1:
            fig.add_trace(go.Pie(
                labels=["1 star", "2 star", "3 star", "4 star", "5 star"],
                values=counts,
                name=lbl,
                hole=0.5,
                domain={'x': [0.52, 1.0]},
                marker=dict(colors=farben)
            ))
            annotations.append(dict(text=f"<b>{lbl}</b>", x=0.76, y=0.5, font_size=16, showarrow=False, xanchor='center', yanchor='middle'))
            
    fig.update_layout(
        title_text=" stern-Leistungs-Verhältnis",
        annotations=annotations
    )

    st.plotly_chart(fig, use_container_width=True)

    #zeigt häufige Wörter je Sternebewertung

def word_cloud_section(db: data_access.DataAccess):
    st.subheader("Häufig genannte Begriffe je Sternebewertung")
    with st.expander("ℹ️ Was zeigt diese Wortwolke?"):
        st.write("""
        Hier sieht man, **welche Begriffe in den Bewertungen am häufigsten vorkommen** – je nach Sternebewertung.

        ### 🔍 Vergleich 1 vs. 5 Sterne:
        -  **1 Stern**: Viele kritische Begriffe wie *never*, *rude* , *worst* oder *wait* – oft in Zusammenhang mit schlechtem Service.
        -  **5 Sterne**: Positive Wörter wie *great*, *delicious*, *friendly* oder *amazing* – Gäste loben Geschmack Service und Atmosphäre. 

        ➕ Die Wortwolken helfen dabei zu verstehen, **was gute vs. schlechte Erfahrungen aus Sicht der Gäste ausmacht**.
        """)

    star = st.slider("Sternebewertung auswählen",1,5,5)
    if "slider_star" not in st.session_state or st.session_state.slider_star != star:
        st.session_state.slider_star = star
        w_c=db.word_clouds_per_star(star)
        st.session_state.word_cloud_section = w_c
        
    st.subheader(f" {star}-Sterne Reviews")
    st.image(f"reports/wordcloud/{st.session_state.word_cloud_section}")
    
  
  #zeigt Trends der Labels über die Jahre  

def reviews_star_per_year_section(db: data_access.DataAccess):
    st.subheader(" Zeitreise: Wie sich Gästebewertungen über die Jahre verändert haben")
    with st.expander("ℹ️ Was zeigt dieses Diagramm?"):
        st.write("""
        Hier sieht man, wie sich die **Anzahl der vergebenen Labels pro Jahr** verändert hat.

        ### 🔍 Was kann man erkennen?
        - Wie oft bestimmte Labels wie *lecker*, *unhygienisch* oder *freundlich* vergeben wurden  
        -  Ein klarer Rückgang während der **Corona-Zeit (2020–2021)** – wahrscheinlich wegen weniger Besuche & Bewertungen  
        - **Trends im Laufe der Jahre**: Man erkennt deutlich, dass **positive Bewertungen insgesamt dominieren**  
        - Welche Themen (z. B. **Service**, **Geschmack**) besonders häufig genannt werden

        👉 Praktisch, um Entwicklungen und Veränderungen im Gästefeedback über die Zeit zu entdecken.
        """)

    # Streamlit_Slider für Jahresauswahl
    start_year, end_year = st.slider("Jahresbereich auswählen", 2005, 2022, (2005, 2022), step=1, key='part')

    if ("start_year" not in st.session_state or st.session_state.start_year != start_year) or ("end_year" not in st.session_state or st.session_state.end_year != end_year):
        st.session_state.start_year = start_year
        st.session_state.end_year = end_year
        
        # Hole die Daten mit Labels und die Gesamtanzahl pro Jahr
        df = db.reviews_label_per_year(start_year, end_year)
        total_df = db.reviews_anzahl_per_year(start_year, end_year)

        st.session_state.reviews_star_per_year_section_df = df
        st.session_state.reviews_star_per_year_section_total_df = total_df
        
    # Erstelle das gestapelte Balkendiagramm (Label_Verteilung)
    fig = px.bar(
        st.session_state.reviews_star_per_year_section_df,
        x="year",
        y="count",
        color="label",
        title="Label-Verteilung & Gesamtzahl Reviews pro Jahr",
        barmode="stack",
        height=600
    )

    # Füge die Liniendarstellung für die Gesamtanzahl der Reviews hinzu
    fig.add_trace(go.Scatter(
        x=st.session_state.reviews_star_per_year_section_total_df["year"],
        y=st.session_state.reviews_star_per_year_section_total_df["count"],
        mode="lines+markers",
        name="Gesamtanzahl Reviews",
        line=dict(color="black", width=3, dash="dash")  
    ))

    # Achsen_Layout anpassen
    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            tickangle=45
        )
    )

    # Diagramm anzeigen
    st.plotly_chart(fig)
