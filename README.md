# Twitter monitoring tools

A package plus a Plotly Dash app to help monitor latest tweets from selected users on Twitter.

## Requirements
First navigate into the `scripts/` directory and run the `initialize.py` script,
```
cd scripts/
python initialize.py
```
This will create the directory structure and some emtpy data files that will be filled as Twitter handles to monitor are added and tweets are downloaded. Moreover, this will also create the hidden `.secret/` folder containing the `credentials.ini` file: open the file and write your Twitter app credentials (see [here](https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html) to see how to).

Second install the custom included package,
```
cd /modules/growth-targeting
pip install .
```

Additional packages that are installed (from pyPI) by the above are
* `tweepy`
* `daiquiri`
* `dash`
* `dash_html_components`
* `dash_core_components`

To manually install these, navigate to the `app/` directory and execute
```
pip install -r requirements.txt
```

## To do
* Create a tab to:
    * Add consistent logic between added/removed handles and what is shown in the table/selectable in the dropdowns.