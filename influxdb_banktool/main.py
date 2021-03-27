#!/usr/bin/env python

from datetime import date, datetime, timedelta

from fints.client import FinTS3PinTanClient
from fints.utils import minimal_interactive_cli_bootstrap
from influxdb import InfluxDBClient

from influxdb_banktool.cache import cache_read, cache_write
from influxdb_banktool.settings import config
from influxdb_banktool.utils import parse_influxdb_timestamp


def main():
    client = InfluxDBClient(*config["influxdb_config"])

    # Original config was just a single dictionary, supporting a single bank
    # account. This allows to have a list of those dicts instead and check more
    # than one bank account
    if config["fints_config"] is dict:
        bank_configs = [config["fints_config"]]
    else:
        bank_configs = config["fints_config"]

    for bank_config in bank_configs:
        f = init_fints(bank_config)
        accounts = f.get_sepa_accounts()
        for account in accounts:
            since = calculate_account_timeframe(client, account.iban)

            transactions = get_transactions(f, account, start=since)
            if len(transactions) > 0:
                balances = get_balance_by_date(transactions)
            else:
                b = f.get_balance(account)
                balances = {b.date: b.amount.amount}
            write_balances_to_influxdb(account.iban, client, balances)

            holdings = f.get_holdings(account)
            write_holdings_to_influxdb(account.iban, client, holdings)

        deconstruct_fints(bank_config, f)


def init_fints(account_config):
    data = cache_read(account_config)
    fints = FinTS3PinTanClient(**account_config, from_data=data)
    minimal_interactive_cli_bootstrap(fints)
    # Since PSD2, a TAN might be needed for dialog initialization. Let's check if there is one required
    if fints.init_tan_response:
        print("A TAN is required", fints.init_tan_response.challenge)
        tan = input("Please enter TAN:")
        fints.send_tan(fints.init_tan_response, tan)

    return fints


def deconstruct_fints(account_config, fints):
    data = fints.deconstruct(including_private=True)
    cache_write(account_config, data)


def get_accounts(fints):
    accounts = fints.get_sepa_accounts()


def calculate_account_timeframe(client, account_id):
    query = f"SELECT LAST(int_value) FROM balance WHERE account='{account_id}'"

    try:
        rs = next(client.query(query).get_points())
        since = parse_influxdb_timestamp(rs["time"]) - timedelta(days=2)
    except (StopIteration, KeyError):
        since = date.today() - timedelta(days=30)

    return since


def get_transactions(fints, account, start, end=date.today()):
    statement = fints.get_transactions(account, start, end)

    return statement


def get_balance_by_date(data):
    opening = data[0].transactions.data["final_opening_balance"].amount.amount

    balance_by_date = {}
    intermediate_balance = opening

    for transaction in data:
        intermediate_balance += transaction.data["amount"].amount
        balance_by_date[transaction.data["date"]] = intermediate_balance

    return balance_by_date


def write_balances_to_influxdb(account_id, client, data):
    for key, value in data.items():
        json_body = [
            {
                "measurement": "balance",
                "tags": {"account": account_id},
                "time": datetime(key.year, key.month, key.day),
                "fields": {"int_value": round(value), "float_value": float(value)},
            }
        ]

        client.write_points(json_body)


def write_holdings_to_influxdb(account_id, client, data):
    for holding in data:
        json_body = [
            {
                "measurement": "holdings",
                "tags": {
                    "account": account_id,
                    "ISIN": holding.ISIN,
                    "name": holding.name,
                    "currency": holding.value_symbol,
                },
                "time": datetime(
                    holding.valuation_date.year,
                    holding.valuation_date.month,
                    holding.valuation_date.day,
                ),
                "fields": {
                    "total_value": float(holding.total_value),
                    "pieces": float(holding.pieces),
                    "market_value": float(holding.market_value),
                },
            }
        ]

        client.write_points(json_body)


if __name__ == "__main__":
    main()
