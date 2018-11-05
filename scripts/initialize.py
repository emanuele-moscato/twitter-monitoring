"""
TO DO:
*Create directory tree
*Create the minimal amount of files needed ({'handle':'id'} json and a pickled tweets dataframe, which could also be empty as long as the column headers are there)
"""

import os
import json
import pickle
import pandas as pd


DATA_DIR = '../data/'
LOGS_DIR = '../logs/'

TWEETS_COLS = [
    'twitter_handle',
    'created_at',
    'text',
    'is_retweet',
    'retweet_count',
    'favorite_count'
]


def main():
    # Create directories
    if not os.path.isdir(DATA_DIR):
        os.mkdir(DATA_DIR)
        
    if not os.path.isdir(os.path.join(DATA_DIR, 'data_tweepy/')):
        os.mkdir(os.path.join(DATA_DIR, 'data_tweepy/'))
        
    if not os.path.isdir(LOGS_DIR):
        os.mkdir(LOGS_DIR)
        
    if not os.path.isdir(os.path.join(LOGS_DIR, 'logs_tweepy/')):
        os.mkdir(os.path.join(LOGS_DIR, 'logs_tweepy/'))
    
    # Create (empty) files for Twitter handles-ids dictionary
    empty_handles_dict = {}
    
    ids_dict_path = os.path.join(DATA_DIR, 'companies_twitter_ids.json')
    ids_dict_tweepy_path = os.path.join(
        DATA_DIR, 'data_tweepy/', 'twitter_ids_dict.json')
    
    if not os.path.exists(ids_dict_path):
        with open(ids_dict_path, 'w') as f:
            json.dump(empty_handles_dict, f)
    
    if not os.path.exists(ids_dict_tweepy_path):
        with open(ids_dict_tweepy_path, 'w') as f:
            json.dump(empty_handles_dict, f)
        
    # Create (empty) files for tweets updating flag
    tweets_updating_flag = {'updating': False}
    
    updating_flag_path = os.path.join(DATA_DIR, 'tweets_updating_flag.json')
    updating_flag_path_tweepy = os.path.join(
        DATA_DIR, 'data_tweepy/', 'tweets_updating_flag.json')
    
    if not os.path.exists(updating_flag_path):
        with open(updating_flag_path, 'w') as f:
            json.dump(tweets_updating_flag, f)
        
    if not os.path.exists(updating_flag_path_tweepy):
        with open(updating_flag_path_tweepy, 'w') as f:
            json.dump(tweets_updating_flag, f)
    
    # Create (empty) dataframes for the tweets
    empty_tweets_df = pd.DataFrame(columns=TWEETS_COLS)
    
    tweets_df_path = os.path.join(DATA_DIR, 'tweets_df.pkl')
    tweets_df_path_tweepy = os.path.join(
        DATA_DIR, 'data_tweepy/', 'tweets_df.pkl')
    
    if not os.path.exists(tweets_df_path):
        with open(tweets_df_path, 'wb') as f:
            pickle.dump(empty_tweets_df, f)
        
    if not os.path.exists(tweets_df_path_tweepy):
        with open(tweets_df_path_tweepy, 'wb') as f:
            pickle.dump(empty_tweets_df, f)


if __name__=='__main__':
    main()