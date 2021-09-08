# MeanReversionTradingBot

A basic trading bot in Python using Mean Reversion.

The strategy will buy and sell 1 share of VOO depending on Bollinger Bands.

Full tutorial on medium:
https://ryankemmer.medium.com/

## Getting started

1. Clone this repository

```
git clone git@github.com:ryankemmer/MeanReversionTradingBot.git
```

2. Change current directory to the repo folder

```
cd MeanReversionTradingBot
```

3. Within the folder, create a file called "auth_params.py, that specifies your TDA API KEY, account number, and callback url like so.

```python
API_KEY =  <Your API Key> + '@AMER.OAUTHAP'
ACCT_NUMBER = <Your TDA Account Number>
CALLBACK_URL = <Your Callback URL>

```

4. Update the scheduler to run during market hours in your time zone.

5. Start running the code

```python
python main.py
```
