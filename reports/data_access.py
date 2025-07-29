# Enthält die DataAccess-Klasse für abstrahierte Datenabfragen 
# Basierend auf der Table-Klasse, die alle Rohdaten und Vorverarbeitung enthält

import pandas as pd
from reports import table   # custom Modul mit vorverarbeiteten Tabellen


class DataAccess :
    # Servicebezogene Labels
    LBL_FRIENDLY_STAFF = 'friendly_staff'
    LBL_SLOW_SERVICE = 'slow_service'
    LBL_RUDE_STAFF = 'rude_staff'
    LBL_PROFESSIONAL_SERVICE = 'professional_service'
    LBL_UNPROFESSIONAL_SERVICE = 'unprofessional_service'

    # Lebensmittelqualität
    LBL_DELICIOUS_FOOD = 'delicious_food'
    LBL_POOR_TASTE = 'poor_taste'
    LBL_OVERCOOKED = 'overcooked'
    LBL_FRESH_INGREDIENTS = 'fresh_ingredients'
    LBL_LOW_QUALITY_INGREDIENTS = 'low_quality_ingredients'

    # Hygiene
    LBL_UNHYGIENIC = 'unhygienic'
    LBL_SPOILED = 'spoiled'

    # Atmosphäre & Sauberkeit
    LBL_CLEANLINESS = 'cleanliness'
    LBL_DIRTY = 'dirty'
    LBL_NOISY_ENVIRONMENT = 'noisy_environment'
    LBL_COZY_ATMOSPHERE = 'cozy_atmosphere'

    #  Preis-Leistung
    LBL_GOOD_VALUE = 'good_value'
    LBL_OVERPRICED = 'overpriced'

    #  Allgemeine Stimmung
    LBL_POSITIVE = 'positive'
    LBL_NEGATIVE = 'negative'

    def __init__(self, table:table.Table):
        # Die Table-Klasse wird übergeben und gespeichert
        self.table = table
        self.table.review_label["stars"] = self.table.review_label["stars"].astype("category")
        #Sammelliste aller verfügbaren Labels
        self.LABELS = [
            self.LBL_FRIENDLY_STAFF,
            self.LBL_SLOW_SERVICE,
            self.LBL_RUDE_STAFF,
            self.LBL_PROFESSIONAL_SERVICE,
            self.LBL_UNPROFESSIONAL_SERVICE   ,
            self.LBL_DELICIOUS_FOOD,
            self.LBL_POOR_TASTE,
            self.LBL_OVERCOOKED,
            self.LBL_FRESH_INGREDIENTS,
            self.LBL_LOW_QUALITY_INGREDIENTS    ,
            self.LBL_UNHYGIENIC,
            self.LBL_SPOILED,
            self.LBL_CLEANLINESS,
            self.LBL_DIRTY,
            self.LBL_NOISY_ENVIRONMENT,
            self.LBL_COZY_ATMOSPHERE,
            self.LBL_GOOD_VALUE,
            self.LBL_OVERPRICED,
            self.LBL_POSITIVE,
            self.LBL_NEGATIVE
            ]
        
        
    #Durchschnittliche Sterne pro Jahr in einem Zeitraum berechnen
    def average_star_per_year(self, _from:int , _to:int ):
        filtered=self.table.reviews[(self.table.reviews['year']>=_from) & (self.table.reviews['year']<=_to)]
        avg_stars=filtered.groupby('year')['stars'].mean().reset_index()
        return avg_stars
    
    
     
    def word_clouds_per_star(self, star:int):
        #Gibt die vorberechnete WordCloud pro Sternbewertung zurück
        result=self.table.word_clouds[star-1]  
        return result      


    
    def cities(self):
        #Liste aller einzigartigen Städte mit verfügbaren Businesses
        result=self.table.business['city'].unique().tolist()
        return result

    def all_businesses(self):
        #Liste aller einzigartigen Business-Namen
        result = self.table.business[["name"]].drop_duplicates("name")
        return result

    #Gibt Businesses nach optionaler Stadt, und Namensfilterung zurück, mind. Sternenbewertung muss passen
    def businesses(self, city:list[str], star:int, names:list[str]):
        if city:
            result = self.table.business[self.table.business['city'].isin(city)]
        else:
            result = self.table.business
        
        if len(names) > 0:
            result = result[result['name'].isin(names)]
            
        result = result[["business_id","name", 'latitude','longitude','stars','review_count']]
        result = result[result['stars'].astype(int)>=star]
        
        return result
            
       #Gibt die Top_N Businesses zurück     
    def top_businesses(self, top:int, labels:list[str], cities:list[str]):
        
        if len(labels) == 0:
            raise 'labels can not be empty'
        
        d = self.table
        
        tdf = d.business_labels
        if len(cities) != 0:    
            tdf = d.business_labels[d.business_labels['city'].isin(cities)]  
                      
         # Punkte berechnen durch Summierung der ausgewählten Labels   
        tdf["score"] = tdf[labels].sum(axis=1)
        tdf=tdf.merge(d.business[['business_id','name']], on= 'business_id')
        
        return tdf.sort_values('score',ascending=False).head(top)


#Analyse: Von den Reviews mit base_label, wie viele enthalten zusätzlich first oder second
    def performance_by_preis(self, base_label:str, first_label:str, second_label:str):
        d = self.table

        #  Nur relevante Labels auswählen
        tdf = d.review_label[
            d.review_label["label"].isin([base_label, first_label, second_label])
        ]

        #  Nur review_ids behalten, die das base_label enthalten
        base_ids = set(
            tdf[tdf["label"] == base_label]["review_id"].unique()
        )

        #  Nur Reviews mit base_label berücksichtigen
        tdf = tdf[tdf["review_id"].isin(base_ids)]

        #  Zähle, wie viele davon jeweils auch first/second enthalten
        count_first = tdf[tdf["label"] == first_label]["review_id"].nunique()
        count_second = tdf[tdf["label"] == second_label]["review_id"].nunique()

        total = len(tdf)
        first_percent = round((count_first / total) * 100) if total > 0 else 0
        second_percent = 100 - first_percent if total > 0 else 0

        return (total, count_first, count_second)
    
    
#Gibt an, wie häufig ein bestimmtes Label bei 1 bis 5 Sternen vorkommt
    def performance_by_star(self, base_label:str):
        d = self.table
        
        tdf = d.review_label[(d.review_label['label']==base_label)]
       
        counts = [0,0,0,0,0]
        
        total = len(tdf)
       
        for star in range(1,6):
            c = len(tdf[tdf["stars"] == star])
            counts[star-1] = c 
       
        return (total, counts)
    
    #Anzahl der Labels pro Jahr
    def reviews_label_per_year(self, from_year:int, to_year:int):
        d = self.table
        
        df = d.review_label[(d.review_label['year'] >= from_year) & (d.review_label['year'] <= to_year)]

        # Gruppieren nach Jahr und Label
        df_grouped = df.groupby(['year', 'label']).size().reset_index(name='count')
        return df_grouped
        
    
    #Anzahl der Reviews pro Jahr (gesamt)
    def reviews_anzahl_per_year(self, from_year:int, to_year:int):
        d = self.table
        
        result = []
        
        for year in range(from_year,to_year+1,1):
            c = d.review_label[(d.review_label['year'] == year)]['review_id'].nunique()
            result.append({"year":year, "count":c})

        return pd.DataFrame(result)