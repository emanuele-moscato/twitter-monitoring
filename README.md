# Twitter monitoring tools

A package plus a Plotly Dash app to help monitor latest tweets from selected users on Twitter.

## Requirements
First install the custom included package,
```
cd /modules/growth-targeting
pip install .
```

Additional packages that should be installed (from pyPI) by the above are
* Tweepy
* Daiquiri
* Dash
* dash_html_components
* dash_core_components

To manually install these,
```
pip install -r requirements.txt
```

## To do
* Create a tab to:
    * See the list of users whose tweets we want to monitor
    * Add users to the list