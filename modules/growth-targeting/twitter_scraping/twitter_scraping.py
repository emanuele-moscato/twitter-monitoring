import pickle
from configparser import ConfigParser
from babylon.data.twitter import api
import pandas as pd
import json


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
        credentials_path = '../.secret/credentials.ini',
        twitter_ids_dict_path='../data/companies_twitter_ids.json'):
        self.data_path = data_path
        self.twitter_ids_dict_path = twitter_ids_dict_path
        self.credentials_path = credentials_path
        self.tweets_df = pd.DataFrame()
        self.logger = logger
        self.twitter_ids_dict = None
    
    def load_tweets(self):
        with open(self.data_path, 'rb') as f:
            self.tweets_df = pickle.load(f)
    
    
    def save_tweets(self):
        if not self.tweets_df.empty:
            with open(self.data_path, 'wb') as f:
                pickle.dump(self.tweets_df, f)
        else:
            print("Can't save tweets: no tweets loaded")
    
    
    def get_twitter_ids(self):
        with open(self.twitter_ids_dict_path, 'r') as f:
            self.twitter_ids_dict = json.load(f)
            
            
    def save_twitter_ids(self):
        if self.twitter_ids_dict:
            with open(self.twitter_ids_dict_path, 'w') as f:
                json.dump(self.twitter_ids_dict, f)
        else:
            print("Can't save Twitter ids: no Twitter IDs loaded")
    
    
    def add_handle(self, new_handle):
        self.get_twitter_ids()
        
        print(self.twitter_ids_dict)
        
        if not new_handle in self.twitter_ids_dict.keys():
            try:
                new_twitter_id = self.get_session().user_id(new_handle)
            
                self.twitter_ids_dict.update(
                    {new_handle: new_twitter_id}
                )
                
                self.save_twitter_ids()
                
                return "Handle '{}' is now monitored".format(new_handle)
            except Exception as e:
                print(e)
                
                return "Couldn't add handle '{}'".format(new_handle)
        else:
            return "Handle '{}' already monitored".format(new_handle)
            
            
    def delete_handle(self, handle, delete_tweets=False):
        self.get_twitter_ids()
        
        if handle in list(self.twitter_ids_dict.keys()):
            del self.twitter_ids_dict[handle]
            self.save_twitter_ids()
            
            return "Deleted handle: {}".format(handle)
        else:
            return "Handle '{}' not monitored".format(handle)
            
            
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
            self.tweets_df['created_at'] = pd.to_datetime(
                self.tweets_df['created_at'])

            self.logger.info("Saving tweets...")
            self.save_tweets()
        except Exception:
            self.logger.info("Error fetching tweets", exc_info=True)


class TweetsFilter(object):
    def __init__(self, tweets_df):
        self.tweets_df = tweets_df
        
    
    def filter_by_company(self, tweets_df, companies_list):
        for company in companies_list:
            if company not in self.tweets_df['twitter_handle'].unique():
                print((f"Warning: '{company}' is not among the followed "
                    "Twitter handles (and this IS case sensitive)"))
        
        return tweets_df[
            tweets_df['twitter_handle'].isin(companies_list)]
    
    
    def filter_by_date(self, tweets_df, dates_range):
        return tweets_df[
            (tweets_df['created_at']>dates_range[0]) &
            (tweets_df['created_at']<dates_range[1])
        ]
    
    
    def filter_by_keyword(self, tweets_df, keywords_list):
        """
        Filters tweets dataframe by keyword: only tweets containing one or more
        keywords in their text field are returned (it's an OR).
        """
        filtered_tweets_df = pd.DataFrame(columns=tweets_df.columns)

        for keyword in keywords_list:
            filtered_tweets_df = filtered_tweets_df.append(
                tweets_df[tweets_df['text'].str.contains(keyword)]
            )
        
        return filtered_tweets_df
    
    
    def filter_tweets(self, companies_list=[], dates_range=[],
        keywords_list=[], reindex=False):
        filtered_tweets_df = self.tweets_df.copy()

        if companies_list:
            filtered_tweets_df = self.filter_by_company(filtered_tweets_df,
                companies_list)
            
        if dates_range:
            filtered_tweets_df = self.filter_by_date(filtered_tweets_df,
                dates_range)
        
        if keywords_list:
            filtered_tweets_df = self.filter_by_keyword(filtered_tweets_df,
                keywords_list)
        
        filtered_tweets_df = filtered_tweets_df.sort_values(by='created_at',
            ascending=False)
        
        if reindex:
            filtered_tweets_df = filtered_tweets_df.reset_index().drop(
                'index', axis=1)
        
        return filtered_tweets_df