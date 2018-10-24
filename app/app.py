from flask import Flask, send_from_directory
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, Event
import pandas as pd
from app_components.app_components import handles_present, generate_table
from twitter_scraping.twitter_scraping import TwitterScraper, TweetsFilter
import daiquiri
import logging
import os.path as path
import sys


LOGS_DIR = '../logs/'

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

twitter_scraper = TwitterScraper(logger)
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
                    html.P("Manage tweets here"),
                ],
                style={'text-align':"center"}
            )
        ])
    ])
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