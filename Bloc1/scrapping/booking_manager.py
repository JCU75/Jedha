import os
import subprocess
import pandas as pd
import time
import sys
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class BookingScrapingManager:
    """Manager for Booking.com scraping with automatic retry"""
    
    def __init__(self, cities, max_retries=3, min_hotels=5):
        self.cities = cities
        self.max_retries = max_retries
        self.min_hotels = min_hotels
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_folder = os.path.join(self.script_dir, "data")
        self.scraper_script = os.path.join(self.script_dir, "booking_spyder.py")
        
    def check_file_quality(self, city):
        """Checks if a city's CSV file is valid and contains enough data"""
        csv_file = os.path.join(self.data_folder, f"{city}.csv")
        
        if not os.path.exists(csv_file):
            return False, "Fichier manquant"
        
        try:
            df = pd.read_csv(csv_file)
            hotel_count = len(df)
            
            if hotel_count == 0:
                return False, "Fichier vide"
            elif hotel_count < self.min_hotels:
                return False, f"Données insuffisantes ({hotel_count} hôtels < {self.min_hotels})"
            else:
                return True, f"OK ({hotel_count} hôtels)"
                
        except Exception as e:
            return False, f"Erreur lecture: {e}"
    
    def get_missing_cities(self):
        """Returns the list of cities that need to be scraped"""
        missing_cities = []
        
        print("\n🔍 Vérification des fichiers...")
        for city in self.cities:
            is_valid, message = self.check_file_quality(city)
            
            if is_valid:
                print(f"{city}: {message}")
            else:
                print(f"{city}: {message}")
                missing_cities.append(city)
                
                # Delete the faulty file if it exists
                csv_file = os.path.join(self.data_folder, f"{city}.csv")
                if os.path.exists(csv_file):
                    os.remove(csv_file)
                    print(f"Suppression de {city}.csv défaillant")
        
        return missing_cities
    
    def run_scraping(self, cities_to_scrape):
        """Runs the scraping script for the specified cities"""
        if not cities_to_scrape:
            return True
            
        print(f"\nLancement du scraping pour: {cities_to_scrape}")
        
        try:
            # Build the command to run the scraping script
            cities_str = ','.join(cities_to_scrape)
            command = [sys.executable, self.scraper_script, cities_str]
            
            print(f"Commande: {' '.join(command)}")
            
            # Run the script in a new process
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=1800)  # 30 min timeout
            
            if result.returncode == 0:
                print("Scraping terminé avec succès")
                print(result.stdout)
                return True
            else:
                print(f"❌ Erreur lors du scraping (code: {result.returncode})")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("Timeout: le scraping a pris trop de temps")
            return False
        except Exception as e:
            print(f"Erreur lors du lancement du scraping: {e}")
            return False
    
    def run_with_retry(self):
        """Main method with automatic retry management"""
        print(f"Démarrage du scraping avec retry pour: {self.cities}")
        print(f"Configuration: max_retries={self.max_retries}, min_hotels={self.min_hotels}")
        
        for attempt in range(self.max_retries):
            print(f"\n{'='*50}")
            print(f"TENTATIVE {attempt + 1}/{self.max_retries}")
            print(f"{'='*50}")
            
            # Check which cities need to be scraped
            missing_cities = self.get_missing_cities()
            
            if not missing_cities:
                print("\nTous les fichiers sont présents et complets !")
                self.print_final_summary()
                return True
            
            print(f"\nVilles à scraper: {missing_cities}")
            
            # Start scraping for missing cities
            success = self.run_scraping(missing_cities)
            
            if not success:
                print(f"Échec du scraping lors de la tentative {attempt + 1}")
                
            # If this is not the last attempt, wait before trying again.
            if attempt < self.max_retries - 1:
                wait_time = 15 + (attempt * 5)  # Progressive waiting: 15s, 20s, 25s...
                print(f"Attente de {wait_time} secondes avant la prochaine tentative...")
                time.sleep(wait_time)
        
        # Final summary after all attempts
        final_missing = self.get_missing_cities()
        if final_missing:
            print(f"\nÉchec après {self.max_retries} tentatives")
            print(f"Villes toujours problématiques: {final_missing}")
            print("Suggestions:")
            print("   - Vérifiez votre connexion internet")
            print("   - Booking.com peut avoir des protections anti-bot actives")
            print("   - Essayez de relancer plus tard")
            return False
        else:
            print("\n🎉 Succès ! Tous les fichiers ont été créés !")
            self.print_final_summary()
            return True
    
    def print_final_summary(self):
        """Displays a final summary of the created files"""
        print("\n RÉSUMÉ FINAL")
        print("="*50)
        
        total_hotels = 0
        for city in self.cities:
            csv_file = os.path.join(self.data_folder, f"{city}.csv")
            if os.path.exists(csv_file):
                try:
                    df = pd.read_csv(csv_file)
                    hotel_count = len(df)
                    total_hotels += hotel_count
                    print(f"{city}.csv: {hotel_count} hôtels")
                except:
                    print(f"{city}.csv: erreur de lecture")
        
        print(f"\nTotal: {total_hotels} hôtels dans {len(self.cities)} villes")
        print(f"Dossier: {self.data_folder}")

    def merge_city_files(self, output_file="all_cities.csv"):
        """Merges all city CSV files into one global file"""
        print("\nFusion des fichiers CSV...")

        all_data = []
        for city in self.cities:
            csv_file = os.path.join(self.data_folder, f"{city}.csv")
            if os.path.exists(csv_file):
                try:
                    df = pd.read_csv(csv_file)
                    all_data.append(df)
                    print(f"Ajout de {city}.csv ({len(df)} hôtels)")
                except Exception as e:
                    print(f"Erreur lecture {city}.csv: {e}")
            else:
                print(f"Fichier manquant: {city}.csv")

        if all_data:
            merged_df = pd.concat(all_data, ignore_index=True)
            output_path = os.path.join(self.data_folder, output_file)
            merged_df.to_csv(output_path, index=False, encoding="utf-8")
            print(f"\nFichier fusionné créé: {output_path} ({len(merged_df)} lignes)")
        else:
            print("Aucun fichier à fusionner")
    


def main():
    """Main function"""
    
    cities = ["Avignon", "Bormes-les-Mimosas", "Cassis", "Marseille", "Nîmes"]
    
   
    manager = BookingScrapingManager(
        cities=cities,
        max_retries=5,
        min_hotels=20 
    )
    
    # Start scraping with automatic retry
    success = manager.run_with_retry()
    
    if success:
        print("\nMission accomplie !")
        manager.merge_city_files(output_file="all_cities.csv")
    else:
        print("\nMission échouée, intervention manuelle requise")


if __name__ == "__main__":
    main()