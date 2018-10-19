from twitter_scraping.twitter_scraping import TwitterScraper
import json
import logging
import daiquiri
import sys
import os.path as path


IDS_PATH = '../data/companies_twitter_ids.json'
LOGS_DIR = '../logs/'


daiquiri.setup(
    level=logging.INFO,
    outputs=(
        daiquiri.output.Stream(sys.stdout),
        daiquiri.output.File(
            path.join(LOGS_DIR, 'update_tweets.log'),
            formatter=daiquiri.formatter.TEXT_FORMATTER
        )
    )
)


def main(logger):
    # Load companies IDs
    with open( IDS_PATH, 'r') as f:
        twitter_ids_dict = json.load(f)
    
    # Instantiate scraper
    scraper = TwitterScraper(logger)
    
    # Scrape Twitter
    scraper.load_tweets()
    n_tweets = scraper.tweets_df.shape[0]
    
    scraper.fetch_tweets(scraper.get_session(), twitter_ids_dict)
    
    print(f"{scraper.tweets_df.shape[0]-n_tweets} new tweets fetched")


if __name__=='__main__':
    logger = daiquiri.getLogger(__name__)
    
    try:
        logger.info("Executing main routine...")
        main(logger)
        logger.info("Tweets fetched")
    except Exception:
        logger.info("Error executing main routine", exc_info=True)