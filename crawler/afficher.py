# HADA C POUR AFFICHER WSH KYN DLA BDD PSQ LE FICHIER CRAWLER.DB YJI EN BINAIRE 

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "crawler.db")

def afficher_urls():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    print("Contenu de la base de données :\n")
    for row in c.execute("SELECT * FROM visited_urls"):
        print(row)
    
    conn.close()

if __name__ == "__main__":
    afficher_urls()
