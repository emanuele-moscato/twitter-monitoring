import dash_html_components as html
import json
import pandas as pd


TWEETS_UPDATING_FLAG_PATH = '../data/tweets_updating_flag.json'

tweets_cols = [
    'twitter_handle',
    'created_at',
    'text',
    'is_retweet',
    'retweet_count',
    'favorite_count'
]


def handles_present(tweets_filter):
    handles = list(tweets_filter.tweets_df['twitter_handle'].unique())
    
    return [{'label': handle, 'value': handle} for handle in handles]


def generate_table(dataframe):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in tweets_cols])] +

        # Body
        [html.Tr([
            html.Td(str(dataframe.iloc[i][col])) for col in tweets_cols
        ]) for i in range(len(dataframe))]
    )


def tweets_are_updating():
    with open(TWEETS_UPDATING_FLAG_PATH, 'r') as f:
        tweets_updating_flag = json.load(f)
    
    return tweets_updating_flag['is_updating']


def toggle_tweets_updating():
    """
    Inverts inverts the value of the tweets updating flag (a json file in the 
    workspace).
    """
    if tweets_are_updating():
        with open(TWEETS_UPDATING_FLAG_PATH, 'w') as f:
            json.dump({"is_updating": False}, f)
    elif not tweets_are_updating():
        with open(TWEETS_UPDATING_FLAG_PATH, 'w') as f:
            json.dump({"is_updating": True}, f)
    else:
        print("Error: updating tweets toggle is inconsistent.")


def generate_handles_summary(tweets_df):
    handles_summary_df = pd.concat(
        [tweets_df.groupby(by='twitter_handle').size(),
        tweets_df.groupby('twitter_handle')['created_at'].max()],
        axis=1
    ).reset_index().rename({0: 'n_tweets'}, axis=1)

    return handles_summary_df