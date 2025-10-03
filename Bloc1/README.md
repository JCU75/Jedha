# Project Kayak 
![Kayak](https://upload.wikimedia.org/wikipedia/commons/c/cb/Kayak_Logo.svg)

## 📌 Context
Kayak is a global travel search engine that helpss ussers plan tripss at the best price.

User research revealed that:
* <strong>70% of users </strong> want more information about their destination(weather, hotels, etc.). 
* Users tend to <strong>trust content only if it comes from a recognized brand</strong> such as Kayak

To address this, Kayak's marketing team wants to build an application recommending the <strong>best destination and hotels, based on real data :</strong>
* <strong>Weather conditions</strong>
* <strong>Hotels information</strong>

## 🎯 Project Goals
The project objectives were:
* Scrape data from destinations 
* Get weather data from each destination 
* Get hotels' info about each destination
* Store all the information above in a data lake
* Extract, transform and load cleaned data from your datalake to a data warehouse

## 🖼️ Scope
Marketing team wants to focus first on the best cities to travel to in France. According <a href="https://one-week-in.com/35-cities-to-visit-in-france/" target="_blank">One Week In.com</a> here are the top-35 cities to visit in France: 

```python 
["Mont Saint Michel","St Malo","Bayeux","Le Havre","Rouen",
"Paris","Amiens","Lille","Strasbourg","Chateau du Haut Koenigsbourg",
"Colmar","Eguisheim","Besancon","Dijon","Annecy",
"Grenoble","Lyon","Gorges du Verdon","Bormes les Mimosas","Cassis",
"Marseille","Aix en Provence","Avignon","Uzes","Nimes",
"Aigues Mortes","Saintes Maries de la mer","Collioure","Carcassonne","Ariege",
"Toulouse","Montauban","Biarritz","Bayonne","La Rochelle"]
```
Here we will determine the list of cities where the weather will be the most pleasant within the next 6 days by selecting where the sky is clear.

### Clone the repository:
```
git clone https://github.com/JCU75/Jedha.git
```
### Go to the project folder:
```
Bloc1/
```

## 🔗 Links
[Weather map](): Interactive 6 day forecast for 5 selected cities, focus on "clear sky" days
[Hotels map](): Top 20 hotels displayed for each city with location and rating

## Built With
<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg" alt="Python logo" height="80"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/38/Jupyter_logo.svg" alt="Jupyter logo" height="80"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/ed/Pandas_logo.svg" alt="pandas logo" height="80"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/0/05/Scikit_learn_logo_small.svg" alt="scikit learn logo" height="80"/>
  <img src="https://www.outsystems.com/Forge_CW/_image.aspx/Q8LvY--6WakOw9afDCuuGT3CEgwOzbDoRlWhBQfGYec=/nominatim-2023-01-04%2000-00-00-2025-03-14%2009-24-06" alt="nominatim logo" height="80" >
  <img src="https://assets.zabbix.com/img/brands/openweather.jpg" alt="openweather logo" height="80">
  <img src="https://miro.medium.com/v2/resize:fit:870/0*jOtewuDO3QM9lKyw" alt="AWS S3 logo" height="80" >
  <img src="https://cdn.prod.website-files.com/601064f495f4b4967f921aa9/635884ad45bd4b4723f4bc39_202210-rds-logo.png" alt="AWS RDS logo" height="80">
  <img src="https://upload.wikimedia.org/wikipedia/fr/1/16/Scrapy_logo.png" alt="scrapy logo" height="80"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/8/8a/Plotly-logo.png" alt="plotly logo" height="80"/>
</p>


## Authors

[Jean-claude Ung](https://github.com/JCU75)