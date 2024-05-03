# mkm_bot

A cardmarket.com bot to help updating card stock prices.
LIMITATION: to 300 foil and 300 non-foil cards.

## Installation

```
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install -e .
```

## Using the bot

Be sure to create four files with the cardmarket username and password, as well as the email and password (you need to create some gmail API credentials, can follow the following tutorial https://mailtrap.io/blog/python-send-email-gmail/#:~:text=your%20Python%20script.-,How%20to%20send%20an%20email%20with%20Python%20via%20Gmail%20API%3F,-The%20Gmail%20API). These correspond to the `mkm_username`, `mkm_password`, `gmail_email`, and `gmail_password` files referenced in `mkm_bot/mkm_bot/xsd/mkm_bot.xml`.

To run, use the following command, substituting `/path/to/mkm_bot.xml` with the correct path to the config.
```
mkm-bot /path/to/mkm_bot.xml
```

Logs are placed by default in the `mkm_bot/.log` directory, but that can be changed in the config.


## Common Issues
- 21/Feb/2024: New chromium version, 122, was set to latest/candidate but not latest/release. Let's see how long it takes to fix. Error when launching `driver = uc.Chrome(...)`.
Error:
```
selenium.common.exceptions.WebDriverException: Message: unknown error: cannot connect to chrome at 127.0.0.1:42983
from session not created: This version of ChromeDriver only supports Chrome version 122
Current browser version is 121.0.6167.184
```
After a WebDriverException was caught (maybe nice to print the stack trace?)

For this, we can update the chrome version. Check https://snapcraft.io/chromium to see if a new candidate/stable release was made.
Can update using
```
sudo snap refresh chromium --candidate
```
Or maybe also with the following, for the stable instead of candidate.
```
sudo snap refresh chromium
```
