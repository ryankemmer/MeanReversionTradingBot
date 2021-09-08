from tda import auth, client
from tda.orders.equities import equity_buy_market, equity_sell_market
from tda.orders.common import Duration, Session
from webdriver_manager.chrome import ChromeDriverManager
import yfinance as yf
import datetime as dt
from datetime import datetime
import pandas as pd
import numpy as np
from statistics import mean
from statistics import stdev
import json
import schedule
import time
# from external python file
from auth_params import ACCT_NUMBER, API_KEY, CALLBACK_URL

# GLOBAL VARIABLES
STOCK = 'VOO'
TIME_PERIOD = 20  # lookback period for bollinger bands calculation


def auth_func():

    token_path = 'token.pickle'
    try:
        c = auth.client_from_token_file(token_path, API_KEY)
    except FileNotFoundError:
        from selenium import webdriver
        with webdriver.Chrome(ChromeDriverManager().install()) as driver:
            c = auth.client_from_login_flow(
                driver, API_KEY, CALLBACK_URL, token_path)

    return c

# function to calculate moving averages
# prices - pandas df
# time_period - int, specifies lookback period


def get_MovingAverage(prices, time_period):

    prices = prices[-time_period:]
    ma = mean(prices)
    return ma

# function to calculate bollinger bands
# prices - pandas df
# time_period - int, specifies lookback period


def get_BBands(prices, time_period):

    prices = prices[-time_period:]
    print(prices)
    ma = get_MovingAverage(prices, time_period)
    std = stdev(prices)
    bup = ma + 2*std
    bdown = ma - 2*std
    return bup, bdown

# function to retrive previous closing prices
# c - user authentication token
# end - datetime of current time


def get_prices(c, end):

    # fetch price history using tda-api
    r = c.get_price_history(STOCK,
                            period_type=client.Client.PriceHistory.PeriodType.DAY,
                            period=client.Client.PriceHistory.Period.THREE_DAYS,
                            frequency_type=client.Client.PriceHistory.FrequencyType.MINUTE,
                            frequency=client.Client.PriceHistory.Frequency.EVERY_THIRTY_MINUTES,
                            end_datetime=end,
                            need_extended_hours_data=False
                            )

    assert r.status_code == 200, r.raise_for_status()

    # parse json and get candles data
    y = r.json()
    y = y["candles"]
    y = json.dumps(y)
    df = pd.read_json(y)
    # drop last row
    df = df[:-1]

    return df

# function to retrive current price of stock


def get_cur_price(c):

    r = c.get_quote(STOCK)
    assert r.status_code == 200, r.raise_for_status()

    y = r.json()
    price = y[STOCK]["lastPrice"]

    return price

# get useful account info


def get_account(c):

    r = c.get_account(ACCT_NUMBER)
    assert r.status_code == 200, r.raise_for_status()

    y = r.json()

    balance = y['securitiesAccount']['currentBalances']['cashAvailableForTrading']
    roundtrips = y['securitiesAccount']['roundTrips']

    return balance, roundtrips

# see if we currently have a position


def get_position(c):

    r = c.get_account(ACCT_NUMBER, fields=c.Account.Fields.POSITIONS)
    assert r.status_code == 200, r.raise_for_status()

    y = r.json()

    if "positions" in y["securitiesAccount"]:
        return True
    else:
        return False

# place an order


def place_order(c, order_type, shares):

    if order_type == 'buy':
        order_spec = equity_buy_market(STOCK, shares).set_session(
            Session.NORMAL).set_duration(Duration.DAY).build()
        c.place_order(ACCT_NUMBER, order_spec)

    if order_type == 'sell':
        order_spec = equity_sell_market(STOCK, shares).set_session(
            Session.NORMAL).set_duration(Duration.DAY).build()
        c.place_order(ACCT_NUMBER, order_spec)


def get_action():

    c = auth_func()
    now = datetime.now()
    print(now)

    try:
        # get current position
        position = get_position(c)
        print('HAS POSITION: ' + str(position))

        df = get_prices(c, now)
        bup, bdown = get_BBands(df.close, TIME_PERIOD)

        # get current price
        price = get_cur_price(c)

        # get account balance
        balance, roundtrips = get_account(c)

        print("Current balance " + str(balance))
        print("Current price " + str(price))
        print("High Band " + str(bup))
        print("Low Band " + str(bdown))

        # check if roundtrips is less than 2
        action = "nothing"
        if roundtrips < 2:

            if price < bdown:
                if position == False:
                    place_order(c, 'buy', 1)
                    action = "buy"
                    print("Bought")

            if price > bup:
                if position == True:
                    place_order(c, 'sell', 1)
                    action = "sell"
                    print("Sold")

    except:
        print('Auth Error')
        price = "ERR"
        bup = "ERR"
        bdown = "ERR"
        action = "ERR"


def get_action():

    c = auth_func()
    now = datetime.now()
    print(now)

    try:
        # get current position
        position = get_position(c)
        print('HAS POSITION: ' + str(position))

        df = get_prices(c, now)
        bup, bdown = get_BBands(df.close, TIME_PERIOD)

        # get current price
        price = get_cur_price(c)

        # get account balance
        balance, roundtrips = get_account(c)

        print("Current balance " + str(balance))
        print("Current price " + str(price))
        print("High Band " + str(bup))
        print("Low Band " + str(bdown))

        # check if roundtrips is less than 2
        if roundtrips < 2:

            if price < bdown:
                if position == False:
                    place_order(c, 'buy', 1)
                    print("Bought")

            if price > bup:
                if position == True:
                    place_order(c, 'sell', 1)
                    print("Sold")

    except:
        print('Auth Error')
        price = "ERR"
        bup = "ERR"
        bdown = "ERR"
        action = "ERR"


def main():

    schedule.every().day.at("07:00").do(get_action)
    schedule.every().day.at("07:30").do(get_action)
    schedule.every().day.at("08:00").do(get_action)
    schedule.every().day.at("08:30").do(get_action)
    schedule.every().day.at("09:00").do(get_action)
    schedule.every().day.at("09:30").do(get_action)
    schedule.every().day.at("10:00").do(get_action)
    schedule.every().day.at("10:30").do(get_action)
    schedule.every().day.at("11:00").do(get_action)
    schedule.every().day.at("11:30").do(get_action)
    schedule.every().day.at("12:00").do(get_action)
    schedule.every().day.at("12:30").do(get_action)
    schedule.every().day.at("13:00").do(get_action)

    while True:
        schedule.run_pending()
        time.sleep(1)


main()
