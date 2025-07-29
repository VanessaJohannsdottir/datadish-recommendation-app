# Diese Klasse lädt und verarbeitet alle CSV-Dateien, bereitet WordClouds für jede Sternebewertung vor

import pandas as pd
from nltk.corpus import stopwords
from wordcloud import WordCloud

class Table:

    def __init__(self):

        # Einlesen aller relevanten CSV-Dateien
        self.reviews=pd.read_csv("data/reviews_no_txt.csv")
        self.business=pd.read_csv("data/business.csv")
        self.business_attributes=pd.read_csv("data/business_attributes.csv")
        self.business_hours=pd.read_csv("data/business_hours.csv")
        self.business_categories=pd.read_csv("data/business_categories.csv")
        self.review_label = pd.read_csv("data/review_label.csv")
        
        
        # Datum konvertieren & Jahr extrahieren
        self.reviews['date']=pd.to_datetime(self.reviews['date'])
        self.reviews['year']=self.reviews['date'].dt.year
        
        #Sternebewertung & Jahr zu den Labels hinzufügen
        self.review_label = self.review_label.merge(self.reviews[["review_id","stars","year"]], on="review_id")
        
        #Stopwörter kombinieren: Standard  + domänenspezifische + Zahlen
        self.stop_words=set(stopwords.words('english'))
        custom_stopwords = [
            "food", "mc donald", "order", "mcdonald", "place", "always", "one", "minute", "people", "go", "time",
            "told", "back", "give", "bad", "say", "even", "asked", "open", "got", "inside", "table", "like", 
            "something", "use", "took", "many", "us", "pay", "need", "person", "eat", "lot", "day", "ordered", 
            "restaurant", "make", "number", "sitting", "around", "last", "said", "get", "come", "says", "going", 
            "meal", "want", "ever", "though", "gave", "could", "would", "buy", "went", "seen", "hanging", "away", 
            "mcdonalds", "still", "austin", "lobby", "take", "know", "wanted", "th", "times", "minutes", "came", 
            "really", "also", "little", "menu", "chicken", "see", "every", "much", "server", "another", "bar", 
            "two", "way", "left", "drinks", "made", "hour", "night", "cheese", "sauce", "salad", "bit", "think", 
            "first", "lunch", "dinner", "drink", "pizza", "right", "check", "finally", "long", 
            "nothing", "fries", "burger", "stars", "side", "however", "beer", "fried", "new", "steak", "sandwich", 
            "bread", "ask", "water", "tables", "seated", "called", "walked", "since", "maybe", "sure", "put", 
            "shrimp", "can't", "everything", "good", "thing", "one"
            
            ]
        numbers = [f'{i}' for i in range(0,1000)]
        self.stop_words.update(custom_stopwords)
        self.stop_words.update(numbers)
        # WordClouds für jede Sternebewertung generieren (1–5 Sterne)
        self.word_clouds = []
        for i in range(1,6):
            self.word_clouds.append(f"wordcloud_star_{i}.png")
            
        # Label-Zusammenfassung pro Business vorbereiten
        self.business_labels = self._business_label()
        
    # WordCloud für eine bestimmte Sternebewertung erzeugen
    def _word_clouds_per_star(self,star:int):
        star_reviews=self.reviews[self.reviews["stars"]==star]['text'].tolist()
        all_reviews_text = " ".join(star_reviews)
        wordcloud = WordCloud(
            width=1000,
            height=500,
            background_color='white',
            stopwords=self.stop_words,
            collocations=False,
            max_words=40
        ).generate(all_reviews_text)
        path = f"wordcloud_star_{star}.png"
        wordcloud.to_file(path)
        return wordcloud
    
    
    #Struktur der df_pivot-Tabelle:
    #business_id	  city	         delicious_food	    cleanliness	   	friendly_staff ...
    #abcd1234	 	 New York	         3	               0	              2        ...
    
    
    #Erstellt eine Pivot_Tabelle mit Anzahl bestimmter Labels je Business
    def _business_label(self):
        # Labels mit Reviews verbinden
        df=pd.merge(self.review_label,self.reviews[['review_id', 'business_id']],on ='review_id')
        
        
        # Labels pivotieren --> Jede Zeile = ein Business, jede Spalte = ein Label mit Häufigkeit
        df_pivot=pd.crosstab(df['business_id'],df['label'])
        
        # Stadtinformationen hinzufügen
        df_pivot=df_pivot.merge(self.business[['business_id', 'city']].drop_duplicates(),on='business_id')
        return df_pivot