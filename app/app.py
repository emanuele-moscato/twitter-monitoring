from flask import Flask, send_from_directory
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, Event
import pandas as pd
from app_components.app_components import handles_monitored, generate_table, \
    tweets_are_updating, toggle_tweets_updating, generate_handles_summary
from twitter_scraping.twitter_scraping import TwitterScraper, TweetsFilter
import daiquiri
import logging
import os.path as path
import sys
import json
from time import sleep


LOGS_DIR = '../logs/'
IDS_PATH = '../data/companies_twitter_ids.json'

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
        dcc.Tab(id='select-tweets-tab', label='Select tweets',
            value='select-tweets-tab', children=[
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
                                        options=handles_monitored(
                                            twitter_scraper),
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
        dcc.Tab(id='manage-tweets-tab', label='Manage tweets',
            value='manage-tweets-tab', children=[
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
                    html.Div(className='row', children=[
                            html.Div(className='six columns', children=[
                                html.H3("Summary by Twitter handle"),
                                html.Div(children=[
                                    dcc.Dropdown(
                                        id='subselect-handles-dropdown',
                                        options=handles_monitored(
                                            twitter_scraper),
                                        placeholder="Select handles",
                                        multi=True,
                                    )],
                                    style={
                                        'width': '30%',
                                        'display': 'inline-block'
                                    }
                                ),
                                html.Div(id='handles-summary-container')
                            ]),
                            html.Div(className='six columns', children=[
                                html.H3("Add handle"),
                                dcc.Input(id='add-handle-input',
                                    style={'marginRight': '10px'}
                                ),
                                html.Button('Add', id='add-handle-button',
                                    style={'marginLeft': '10px'}
                                ),
                                html.Div(id='new-handle-div')
                            ]),
                            html.Div(className='six columns', children=[
                                html.H3("Delete handle"),
                                dcc.Input('delete-handle-input',
                                    placeholder='Handle...',
                                    style={
                                        'marginRight': '10px'
                                    }),
                                dcc.Checklist(id='delete-tweets-check',
                                    options=[
                                        {'label': 'Delete tweets',
                                            'value': 'dt'}
                                    ],
                                    values=[],
                                    style={'display': 'inline-block'}
                                ),
                                html.Button('Delete', id='delete-handle-button',
                                    style={
                                        'marginLeft': '10px'
                                    }),
                                dcc.Checklist(id='delete-check',
                                    options=[
                                        {'label': 'Sure?', 'value': 'y'}
                                    ],
                                    values=[],
                                    style={
                                        'display': 'inline-block',
                                        'marginLeft': '10px'
                                    }
                                ),
                                html.Div(id='delete-handle-div',
                                    style={'marginTop': '10px'}
                                )],
                                style = {'marginTop': '20px'}
                            )
                        ])
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
    toggle_tweets_updating()
    
    # Update tweets
    twitter_scraper.get_twitter_ids()
    twitter_scraper.fetch_tweets(twitter_scraper.get_session(),
        twitter_scraper.twitter_ids_dict)
    
    toggle_tweets_updating()
    
    return None


@app.callback(
    Output('tweets-updating-container', 'children'),
    [Input('tweets-updating-interval', 'n_intervals')],
    [State('update-tweets-button', 'n_clicks')])
def tweets_updating_signal(n_intervals, n_clicks):
    if tweets_are_updating():
        return html.P("Tweets updating...")
    elif not tweets_are_updating():
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
    if tweets_are_updating():
        return {'display': 'none'}
    else:
        return {'display': 'inline-block', 'marginTop': '10px'}
        
        
@app.callback(
    Output('handles-summary-container', 'children'),
    [Input('subselect-handles-dropdown', 'value'),
    Input('tweets-updating-interval', 'n_intervals')])
def show_handles_summary(value, n_intervals):
    if not tweets_are_updating():
        twitter_scraper.load_tweets()
        tweets_filter.tweets_df = twitter_scraper.tweets_df
        
        return generate_handles_summary(twitter_scraper, tweets_filter, value)
    else:
        pass
    
    
@app.callback(
    Output('new-handle-div', 'children'),
    [],
    [State('add-handle-input', 'value')],
    [Event('add-handle-button', 'click')],
)
def add_handle(new_handle):
    return html.P(twitter_scraper.add_handle(new_handle),
        style={'marginTop': '10px'})
    
    
@app.callback(
    Output('companies-dropdown', 'options'),
    [Input('tweets-updating-interval', 'n_intervals')])
def update_companies_filter_options(n_intervals):
    return handles_monitored(twitter_scraper)


@app.callback(
    Output('subselect-handles-dropdown', 'options'),
    [Input('tweets-updating-interval', 'n_intervals')])
def update_subselect_handles_options(n_intervals):
    return handles_monitored(twitter_scraper)
    
    
@app.callback(
    Output('delete-handle-div', 'children'),
    [],
    [State('delete-check', 'values'),
    State('delete-tweets-check', 'values'),
    State('delete-handle-input', 'value')],
    [Event('delete-handle-button', 'click')])
def delete_handle(sure_checks, delete_tweets_checks, handle):
    if 'y' in sure_checks:
        print(f"Deleting handle {handle}")
        
        if 'dt' in delete_tweets_checks:
            return html.P(twitter_scraper.delete_handle(handle,
                delete_tweets=True))
        
        return html.P(twitter_scraper.delete_handle(handle))
    else:
        return html.P(f"Please confirm you want to delete handle '{handle}'")

        
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