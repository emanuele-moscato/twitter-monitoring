import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import json


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


def tweets_are_updating(tweets_updating_flag_path):
    with open(tweets_updating_flag_path, 'r') as f:
        tweets_updating_flag = json.load(f)
    
    return tweets_updating_flag['is_updating']


def toggle_tweets_updating(tweets_updating_flag_path):
    """
    Inverts inverts the value of the tweets updating flag (a json file in the 
    workspace).
    """
    if tweets_are_updating(tweets_updating_flag_path):
        with open(tweets_updating_flag_path, 'w') as f:
            json.dump({"is_updating": False}, f)
    elif not tweets_are_updating(tweets_updating_flag_path):
        with open(tweets_updating_flag_path, 'w') as f:
            json.dump({"is_updating": True}, f)
    else:
        print("Error: updating tweets toggle is inconsistent.")
        
        
def generate_handles_summary(tweets_filter, handles_list):
    filtered_df = tweets_filter.filter_tweets(companies_list=handles_list)
    
    handles_summary_df = pd.concat(
        [filtered_df.groupby(by='twitter_handle').size(),
        filtered_df.groupby('twitter_handle')['created_at'].max()],
        axis=1
    ).reset_index().rename({0: 'n_tweets'}, axis=1)
    
    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in handles_summary_df.columns])] +

        # Body
        [
            html.Tr([
            html.Td(str(handles_summary_df.iloc[i][col])) for col in 
            handles_summary_df.columns]) for i in range(len(handles_summary_df))
        ],
        style={'display': 'inline-block',}
    )
    
    subselect_dropdown = dcc.Dropdown(
        id='subselect-handles-dropdown',
        options=handles_present(tweets_filter),
        placeholder="Select handles...",
        multi=True
    )
    
    return [
        # html.H3("Summary by Twitter handle"),
        # subselect_dropdown,
        table
    ]