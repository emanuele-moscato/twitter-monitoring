import pickle
from configparser import ConfigParser
from babylon.data.twitter import api
import pandas as pd


def print_rate_limits(session):
    rate_limit_status = session._session.rate_limit_status()
    
    for key in rate_limit_status['resources'].keys():
        for endpoint in rate_limit_status['resources'][key].keys():
            limit = rate_limit_status['resources'][key][endpoint]['limit']
            remaining = rate_limit_status['resources'][key][endpoint]['remaining']
            
            if limit!=remaining:
                print(endpoint)
                print(rate_limit_status['resources'][key][endpoint])
                

def get_users_ids(session, twitter_handles_list, twitter_ids_dict, n_users=None):
    if not n_users:
        n_users = len(twitter_handles_list)
        
    print(f"Fetching {n_users} ids")
    
    for i in range(n_users):
        twitter_handle = twitter_handles_list[i]
        
        print(f"Fetching id: @{twitter_handle}")
        
        try:
            twitter_id = session.user_id(twitter_handle)
            
            twitter_ids_dict.update(
                {twitter_handle: twitter_id}
            )
        except Exception as e:
            print(e)
            

def fetch_tweets(session, twitter_ids_dict, tweets_df):
    for twitter_handle in list(twitter_ids_dict.keys()):
        try:
            since_id = int(tweets_df[
                tweets_df['twitter_handle']==twitter_handle
            ]['twitter_id'].max())
        except Exception as e:
            since_id = None
        
        print(f"Fetching tweets: {twitter_handle}")
        print(f"since_id={since_id}")

        try:
            tweets = session.tweets(
                twitter_ids_dict[twitter_handle], since_id=since_id
            )
        
            for tweet in tweets:
                tweet.as_dict['twitter_handle'] = twitter_handle
                tweets_df = tweets_df.append(tweet.as_dict, ignore_index=True)
        except Exception as e:
            print("Error:", e)
            
    return tweets_df
    
    
class TwitterScraper(object):
    def __init__(self, logger, data_path='../data/tweets_df.pkl',
        credentials_path = '../.secret/credentials.ini'):
        self.data_path = data_path
        self.credentials_path = credentials_path
        self.tweets_df = pd.DataFrame()
        self.logger = logger
    
    def load_tweets(self):
        if self.tweets_df.empty:
            with open(self.data_path, 'rb') as f:
                self.tweets_df = pickle.load(f)
        else:
            pass
    
    
    def save_tweets(self):
        if not self.tweets_df.empty:
            with open(self.data_path, 'wb') as f:
                pickle.dump(self.tweets_df, f)
        else:
            print("Can't save tweets: no tweets loaded")
            
            
    def get_session(self):
        cp = ConfigParser()
        cp.read(self.credentials_path)
        
        try:
            session = api.Session(
                consumer_key = cp['emas_twitter_credentials']['consumer_key'],
                consumer_secret = cp['emas_twitter_credentials']['consumer_secret'],
                access_token = cp['emas_twitter_credentials']['access_token'],
                access_token_secret = cp['emas_twitter_credentials']['access_token_secret']
            )
        except:
            session = api.Session(
                consumer_key = cp['twitter_credentials']['consumer_key'],
                consumer_secret = cp['twitter_credentials']['consumer_secret'],
                access_token = cp['twitter_credentials']['access_token'],
                access_token_secret = cp['twitter_credentials']['access_token_secret']
            )
        return session
    
    
    def fetch_tweets(self, session, twitter_ids_dict):
        try:
            self.logger.info("Loading tweets...")
            self.load_tweets()
            
            # Do stuff
            self.logger.info("Fetching tweets...")
            for twitter_handle in list(twitter_ids_dict.keys()):
                try:
                    since_id = int(self.tweets_df[
                        self.tweets_df['twitter_handle']==twitter_handle
                    ]['twitter_id'].max())
                except Exception as e:
                    since_id = None
                
                print(f"Fetching tweets: {twitter_handle}")
                print(f"since_id={since_id}")
        
                try:
                    tweets = session.tweets(
                        twitter_ids_dict[twitter_handle], since_id=since_id
                    )
                
                    for tweet in tweets:
                        tweet.as_dict['twitter_handle'] = twitter_handle
                        self.tweets_df = self.tweets_df.append(
                            tweet.as_dict, ignore_index=True)
                except Exception as e:
                    print(e)
            
            self.logger.info("Saving tweets...")
            self.save_tweets()
        except Exception:
            self.logger.info("Error fetching tweets", exc_info=True)


class TweetsFilter(object):
    def __init__(self, tweets_df):
        self.tweets_df = tweets_df