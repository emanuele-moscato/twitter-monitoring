import dash_html_components as html


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