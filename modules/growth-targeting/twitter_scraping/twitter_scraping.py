import pickle
from configparser import ConfigParser
import tweepy
import pandas as pd
import json


def print_rate_limits(api):
    """
    Parameters
    ----------
        api: tweepy.API
    """
    rate_limit_status = api.rate_limit_status()
    
    for key in rate_limit_status['resources'].keys():
        for endpoint in rate_limit_status['resources'][key].keys():
            limit = rate_limit_status['resources'][key][endpoint]['limit']
            remaining = rate_limit_status['resources'][key][endpoint]['remaining']
            
            if limit!=remaining:
                print(endpoint)
                print(rate_limit_status['resources'][key][endpoint])
                

def get_users_ids(api, twitter_handles_list, twitter_ids_dict, n_users=None):
    """
    Parameters
    ----------
        api: tweepy.API
        twitter_handles_list: list
            List of Twitter handles (screen names)
        twitter_ids_dict: dict
            Dictionary to which to append the new {'handle': 'id'}
            key-value pairs
        n_users: int
            Maximum number of users of which to fetch the ids. Default: None
            (i.e. range(twitter_handles_list)).
    """
    if not n_users:
        n_users = len(twitter_handles_list)
        
    print(f"Fetching {n_users} ids")
    
    for i in range(n_users):
        twitter_handle = twitter_handles_list[i]
        
        print(f"Fetching id: @{twitter_handle}")
        
        try:
            twitter_id = api.get_user(twitter_handle).id
            
            twitter_ids_dict.update(
                {twitter_handle: twitter_id}
            )
        except Exception as e:
            print(e)
            

def fetch_tweets(api, twitter_ids_dict, tweets_df):
    """
    Download 200 tweets for all the users in twitter_ids_dict, starting
    chronologically from the last tweet for each user over. If no tweet from a
    particular user is present in the dataframe, then the the last 200 tweets are
    fetched.
    
    Parameters
    __________
        api: tweepy.API
        twitter_ids_dict: dict
        tweets_df: pandas.DataFrame
    
    Returns
    -------
        tweets_df: pandas.DataFrame
    """
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
            tweets = api.user_timeline(
                id=twitter_ids_dict[twitter_handle],
                tweet_mode='extended',
                count=200,
                since_id=since_id
            )
        
            for tweet in tweets:
                tweet_dict = {
                    'twitter_id': tweet.id,
                    'created_at': tweet.created_at,
                    'user_id': tweet.user.id_str,
                    'twitter_handle': twitter_handle,
                    'is_retweet': str(tweet.retweeted),
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count
                }
                try:
                    tweet_dict['text'] = tweet._json['retweeted_status']['full_text']
                except:
                    tweet_dict['text'] = tweet.full_text
                tweets_df = tweets_df.append(tweet_dict, ignore_index=True)
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
        
        if not new_handle in self.twitter_ids_dict.keys():
            try:
                new_twitter_id = self.get_tweepy_api().get_user(new_handle).id
            
                self.twitter_ids_dict.update(
                    {new_handle: new_twitter_id}
                )
                
                self.save_twitter_ids()
            except Exception as e:
                print(e)
        else:
            print("Handle already present")
            
            
    def get_tweepy_api(self):
        """
        Reads the Twitter credentials from file and returns a tweepy.API instance.
        """
        cp = ConfigParser()
        cp.read(self.credentials_path)
        
        try:
            auth = tweepy.OAuthHandler(
                cp['emas_twitter_credentials']['consumer_key'],
                cp['emas_twitter_credentials']['consumer_secret'])
            auth.set_access_token(
                cp['emas_twitter_credentials']['access_token'],
                cp['emas_twitter_credentials']['access_token_secret']
            )
            api = tweepy.API(auth_handler=auth)
        except:
            auth = tweepy.OAuthHandler(
                cp['twitter_credentials']['consumer_key'],
                cp['twitter_credentials']['consumer_secret'])
            auth.set_access_token(
                cp['twitter_credentials']['access_token'],
                cp['twitter_credentials']['access_token_secret']
            )
            api = tweepy.API(auth_handler=auth)
        return api
    
    
    def fetch_tweets(self, api, twitter_ids_dict):
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
                    tweets = api.user_timeline(
                        id=twitter_ids_dict[twitter_handle],
                        tweet_mode='extended',
                        count=200,
                        since_id=since_id
                    )
                
                    for tweet in tweets:
                        tweet_dict = {
                            'twitter_id': tweet.id,
                            'created_at': tweet.created_at,
                            'user_id': tweet.user.id_str,
                            'twitter_handle': twitter_handle,
                            'is_retweet': str(tweet.retweeted),
                            'retweet_count': tweet.retweet_count,
                            'favorite_count': tweet.favorite_count
                        }
                        try:
                            tweet_dict['text'] = tweet._json['retweeted_status']['full_text']
                        except:
                            try:
                                tweet_dict['text'] = tweet.full_text
                            except:
                                tweet_dict['text'] = tweet.text
                        self.tweets_df = self.tweets_df.append(tweet_dict,
                            ignore_index=True)
                except Exception as e:
                    print("Error:", e)

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