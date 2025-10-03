import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
import json
import urllib.parse
import random
import pandas as pd
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class BookingSpider(scrapy.Spider):
    name = "booking"
    
    def __init__(self, city, *args, **kwargs):
        super(BookingSpider, self).__init__(*args, **kwargs)
        self.city = city
        self.start_urls = [f"https://www.booking.com/searchresults.fr.html?ss={city}"]

    def parse(self, response):
        # Extract all hotel names and all hotel url
        hotel_names = response.xpath("//h3/a/div[1]/text()").getall()
        hotel_urls = response.xpath("//h3/a/@href").getall()

        for hotel_name, hotel_url in zip(hotel_names, hotel_urls):
            # Normalize URL
            url = response.urljoin(hotel_url)
            
            if url:
                yield scrapy.Request(
                    url=url, 
                    callback=self.parse_hotel_page, 
                    meta={
                        'name': hotel_name,
                        'url': url,
                        'city': self.city
                })     

    def parse_hotel_page(self, response):
        # Get data from meta
        hotel_name = response.meta["name"]
        url = response.meta["url"]

        # Get data from json
        json_block = response.xpath("//script[@type='application/ld+json']/text()").get()

        if json_block:
            try:
                data = json.loads(json_block)
                lat, lon = None, None

                if data.get("@type") == "Hotel":
                    if "hasMap" in data:
                        hotel_GPS_coordinates_URL_string = data["hasMap"]
                        parsed_url = urllib.parse.urlparse(hotel_GPS_coordinates_URL_string)     
                        query_params = urllib.parse.parse_qs(parsed_url.query)
                        center_string = query_params.get('center', [''])[0]

                        if center_string:
                           lat, lon = center_string.split(',') 

                    yield{
                        "city": response.meta["city"],
                        "hotel": hotel_name, 
                        "address": data.get("address", {}).get("streetAddress"),
                        "rating": data.get("aggregateRating", {}).get("ratingValue"),
                        "reviews": data.get("aggregateRating", {}).get("reviewCount"),
                        "url": data.get("url") or url,
                        "description": data.get("description"),
                        "latitude": lat,
                        "longitude": lon
                    }

            except json.JSONDecodeError:
                self.logger.warning(f"⚠️ JSON mal formé sur {url}")        


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

class RotateUserAgentMiddleware:
    def process_request(self, request, spider):
        user_agent = random.choice(USER_AGENTS)
        request.headers["User-Agent"] = user_agent

class CityCSVPipeline:
    """Custom pipeline to separate data by city into separate CSV files"""
    
    def __init__(self):
        self.files = {}
        self.data_folder = None
        
    def open_spider(self, spider):
        """Appelé au début du scraping - crée le dossier data"""
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_folder = os.path.join(script_dir, "data")
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        print(f"Dossier de données créé: {self.data_folder}")
    
    def process_item(self, item, spider):
        """Called for each scraped item - stores data by city"""
        city = item['city']
        
        if city not in self.files:
            self.files[city] = []
            print(f"Nouvelle ville détectée: {city}")
        
        self.files[city].append(dict(item))
        return item
    
    def close_spider(self, spider):
        """Called at the end of scraping - saves all CSV files"""
        print("\nSauvegarde des fichiers CSV...")
        
        for city, items in self.files.items():
            if items:
                filename = os.path.join(self.data_folder, f"{city}.csv")
                df = pd.DataFrame(items)
                df.to_csv(filename, index=False, encoding='utf-8')
                print(f"{city}.csv créé avec {len(items)} hôtels")
            else:
                print(f"Aucune donnée pour {city}")
        
        print("Tous les fichiers CSV ont été créés")


def run_spiders_for_cities(cities):
    """Starts scraping for the specified cities"""
    print(f"🕷️ Démarrage scraping pour: {cities}")
    
    process = CrawlerProcess(settings={
        'LOG_LEVEL': logging.DEBUG,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': random.uniform(2, 5),
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.5,
        'DOWNLOADER_MIDDLEWARES': {
            '__main__.RotateUserAgentMiddleware': 400,
        },
        'ITEM_PIPELINES': {
            '__main__.CityCSVPipeline': 300,
        }
    })
    
    for city in cities:
        print(f"🕷️ Ajout spider pour {city}")
        process.crawl(BookingSpider, city=city)
    
    print("🚀 Démarrage du scraping...")
    process.start()
    print("✅ Scraping terminé")


if __name__ == "__main__":
    # Retrieve cities from command line arguments
    if len(sys.argv) > 1:
        cities = sys.argv[1].split(',')
    else:
        cities = ["Montpellier", "Avignon"]
    
    run_spiders_for_cities(cities)