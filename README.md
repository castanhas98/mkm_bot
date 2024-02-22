# mkm_bot

A cardmarket.com bot to help updating card stock prices.
LIMITATION: to 300 foil and 300 non-foil cards.

## Installation

## Using the bot

## To Do
- Enrich status email (start/end time, number of cards processed)


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
