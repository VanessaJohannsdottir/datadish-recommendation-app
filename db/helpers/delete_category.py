import sqlite3

def delete_category(db_path, category_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Vorhandene Einträge anzeigen
        cursor.execute("SELECT * FROM business_categories WHERE category = ?", (category_name,))
        rows = cursor.fetchall()

        if not rows:
            print(f"⚠️  Keine Einträge mit der Kategorie '{category_name}' gefunden.\n")
            return

        print(f"🔍 Gefundene Einträge mit Kategorie '{category_name}':")
        for row in rows:
            print(row)

        confirm = input(f"\n❓ Möchtest du alle Einträge mit der Kategorie '{category_name}' wirklich löschen? (ja/nein): ").lower()
        if confirm != 'ja':
            print("⏭️  Abbruch. Keine Daten wurden gelöscht.\n")
            return

        cursor.execute("DELETE FROM business_categories WHERE category = ?", (category_name,))
        conn.commit()

        print(f"✅ {cursor.rowcount} Eintrag/Einträge mit Kategorie '{category_name}' wurden gelöscht.\n")

    except sqlite3.Error as e:
        print("❌ Fehler beim Zugriff auf die Datenbank:", e)

    finally:
        if conn:
            conn.close()

def main():
    db_path = "../../yelp.db"
    print("🔄 Lösche Kategorien aus 'business_categories'. Tippe 'exit', um zu beenden.\n")

    while True:
        category_to_delete = input("🗑️  Welche Kategorie möchtest du löschen? ").strip()
        if category_to_delete.lower() in ["exit", ""]:
            print("👋 Vorgang beendet.")
            break

        delete_category(db_path, category_to_delete)

if __name__ == "__main__":
    main()
