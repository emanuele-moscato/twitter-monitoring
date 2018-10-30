from flask import Flask, send_from_directory
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, Event
import pandas as pd
from app_components.app_components import handles_present, generate_table, \
    tweets_are_updating, toggle_tweets_updating, generate_handles_summary
from twitter_scraping.twitter_scraping import TwitterScraper, TweetsFilter
import daiquiri
import logging
import os.path as path
import sys
import json
from time import sleep


LOGS_DIR = '../logs/logs_tweepy/'
IDS_PATH = '../data/data_tweepy/twitter_ids_dict.json'
TWEETS_UPDATING_FLAG_PATH = '../data/data_tweepy/tweets_updating_flag.json'

daiquiri.setup(
    level=logging.INFO,
    outputs=(
        daiquiri.output.Stream(sys.stdout),
        daiquiri.output.File(
            path.join(LOGS_DIR, 'app.log'),
            formatter=daiquiri.formatter.TEXT_FORMATTER
        )
    )
)
logger = daiquiri.getLogger(__name__)


server = Flask('Dashboard', static_url_path='')

app = dash.Dash(server=server)

@server.route('/static/style.css')
def serve_stylesheet():
    return server.send_static_file('style.css')

app.css.append_css({
    'external_url': '/static/style.css'
})
    
@server.route('/favicon.ico')
def favicon():
    return server.send_static_file('400x400SML-01.png')
    
app.scripts.config.serve_locally = True

app.config['suppress_callback_exceptions']=True

twitter_scraper = TwitterScraper(
    logger,
    data_path='../data/data_tweepy/tweets_df.pkl',
    credentials_path='../.secret/credentials.ini',
    twitter_ids_dict_path=IDS_PATH
)
twitter_scraper.load_tweets()

tweets_filter = TweetsFilter(twitter_scraper.tweets_df)

app.layout = html.Div(children=[
    html.H1("The Growth targeting tool", style={'text-align': 'center'}),
    dcc.Tabs(id='tabs', children=[
        dcc.Tab(label='Select tweets', children=[
            html.Div(
                children=[
                    html.Button('Test!', id='test-button',
                        style={'marginBottom': '10px'}),
                    html.Div(id='test-div'),
                    html.Div(id='companies-list-div'),
                    html.Div(
                        id='options-container',
                        children=[
                            html.Div(
                                id='dates-range-container',
                                children=[
                                    dcc.DatePickerRange(
                                        id='date-picker-range',
                                        end_date=pd.to_datetime(
                                            pd.Timestamp.now()),
                                        start_date_placeholder_text=("Select a "
                                            "date!")
                                    )
                                ],
                                style={
                                    'text-align': 'center',
                                    'marginBottom': '5px'
                                }
                            ),
                            html.Div(
                                id='companies-container',
                                children=[
                                    dcc.Dropdown(
                                        id='companies-dropdown',
                                        options=handles_present(tweets_filter),
                                        placeholder="Companies...",
                                        multi=True
                                    )
                                ],
                                style={
                                    'display': 'inline-block',
                                    'width': '20%'
                                }
                            ),
                            html.Div(
                                id='keywords-container',
                                children=[
                                    dcc.Dropdown(
                                        id='keywords-dropdown',
                                        options=[
                                            {'label': 'New York City',
                                                'value': 'NYC'},
                                            {'label': 'Montreal',
                                                'value': 'MTL'},
                                            {'label': 'San Francisco',
                                                'value': 'SF'}
                                        ],
                                        placeholder="Keywords...",
                                        multi=True
                                    )
                                ],
                                style={
                                    'display': 'inline-block',
                                    'width': '20%'
                                }
                            )
                        ]
                    ),
                    html.Div(
                        id='tweets-container',
                        style={
                            'width': '80%',
                            'display': 'inline-block',
                            'text-align': 'center'
                        }
                    )
                ],
                style={'text-align':"center", 'marginTop': '10px'}
            )
        ]),
        dcc.Tab(label='Manage tweets', children=[
            html.Div(
                children=[
                    html.Button("Update tweets", id='update-tweets-button',
                        style={'marginTop': '10px'}),
                        dcc.Interval(
                            id='tweets-updating-interval',
                            interval=1000,
                            n_intervals=0
                        ),
                        html.Div(id='tweets-updating-container',
                            style={'marginTop': '10px'}),
                        html.H3("Summary by Twitter handle"),
                        html.Div(children=[
                            dcc.Dropdown(
                                id='subselect-handles-dropdown',
                                options=handles_present(tweets_filter),
                                placeholder="Select handles",
                                multi=True,
                            )],
                            style={'width': '20%', 'display': 'inline-block'}
                        ),
                        html.Div(id='handles-summary-container')
                ],
                style={'text-align':"center"}
            )
        ])
    ]),
    html.Div(id='hidden-div', style={'display': 'none'})
])


@app.callback(
    Output('tweets-container', 'children'),
    [Input('companies-dropdown', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')])
def filter_by_companies(companies_list, start_date, end_date):
    twitter_scraper.load_tweets()

    tweets_filter.tweets_df = twitter_scraper.tweets_df
    
    if start_date and end_date:
        dates_range = [start_date, end_date]
    else:
        dates_range = []
    
    if companies_list or dates_range:
        return generate_table(
            tweets_filter.filter_tweets(companies_list=companies_list,
                dates_range=dates_range))
    else:
        return None


@app.callback(
    Output('hidden-div', 'children'),
    events=[Event('update-tweets-button', 'click')])
def update_tweets():
    toggle_tweets_updating(TWEETS_UPDATING_FLAG_PATH)
    
    # Update tweets
    twitter_scraper.get_twitter_ids()
    twitter_scraper.fetch_tweets(twitter_scraper.get_tweepy_api(),
        twitter_scraper.twitter_ids_dict)
    
    toggle_tweets_updating(TWEETS_UPDATING_FLAG_PATH)
    
    tweets_filter.tweets_df = twitter_scraper.tweets_df
    
    return None


@app.callback(
    Output('tweets-updating-container', 'children'),
    [Input('tweets-updating-interval', 'n_intervals')],
    [State('update-tweets-button', 'n_clicks')])
def tweets_updating_signal(n_intervals, n_clicks):
    if tweets_are_updating(TWEETS_UPDATING_FLAG_PATH):
        return html.P("Tweets updating...")
    elif not tweets_are_updating(TWEETS_UPDATING_FLAG_PATH):
        if not n_clicks:
            return None
        else:
            return html.P("Tweets updated")
    else:
        return html.P("Error: inconsistent tweets updating toggle!")


@app.callback(
    Output('update-tweets-button', 'style'),
    [Input('tweets-updating-interval', 'n_intervals')])
def toggle_update_button(n_intervals):
    if tweets_are_updating(TWEETS_UPDATING_FLAG_PATH):
        return {'display': 'none'}
    else:
        return {'display': 'inline-block', 'marginTop': '10px'}
    
        
@app.callback(
    Output('handles-summary-container', 'children'),
    [Input('subselect-handles-dropdown', 'value')])
def show_handles_summary(value):
    twitter_scraper.load_tweets()
    tweets_filter.tweets_df = twitter_scraper.tweets_df
    
    return generate_handles_summary(tweets_filter, value)
        
        
@app.callback(
    Output('companies-list-div', 'children'),
    [Input('companies-dropdown', 'value')])
def show_companies(companies_list):
    if companies_list:
        return html.P(f"{str(companies_list)}")
    else:
        return None
        
        
@app.callback(
    Output('test-div', 'children'),
    [Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')])
def show_dates(start_date, end_date):
    if start_date and end_date:
        dates_range = [start_date, end_date]
        return html.P(f"{str(dates_range)}")
    else:
        pass


"""@app.callback(
    Output('test-div', 'children'),
    events=[Event('test-button', 'click')])
def test_button():
    return html.P("Bella!")"""


if __name__=='__main__':
    app.server.run(debug=True, port=8888, processes=True)