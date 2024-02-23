# nba_model
Scrapes lines from PrizePicks, load and clean the corresponding player data, and finally predict using model. The model was trained using every game log played by each of the top 150 scorers in each of the last 9 seasons (150 players x 82 games x 9 seasons = 110,700 rows of data).

How to run:

Without scraping new data and using the saved SVM model:
1. Run PRIZEPICKS_NBA_SCRAPER.py (Replace the file path in the beginning with the file path your downloads go to)
2. Run process_lines.py
3. Run generate_prediction.py
4. Predictions for todas's NBA players points compared to their PrizePicks lines will be stored in the predictions_<timestamp>.csv

With scraping new data using the NBA API endpoint and building model fresh:
1. Run stat_scrape_v2.py
2. Run build_model.py
3. Follow same 4 steps listed above
