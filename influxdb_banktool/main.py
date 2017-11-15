#!/usr/bin/env python

from datetime import date, datetime, timedelta

from fints.client import FinTS3PinTanClient
from influxdb import InfluxDBClient

from influxdb_banktool.settings import config


def main():
    transactions = get_transactions(start=date(2016, 8, 1))
    balances = get_balance_by_date(transactions)
    write_to_influxdb(balances)


def get_transactions(start=date.today()-timedelta(days=30), end=date.today()):
    fints = FinTS3PinTanClient(**config['fints_config'])
    accounts = fints.get_sepa_accounts()

    statement = fints.get_statement(accounts[0], start, end)
    return statement


def get_balance_by_date(data):
    opening = data[0].transactions.data['final_opening_balance'].amount.amount

    balance_by_date = {}
    intermediate_balance = opening

    for transaction in data:
        intermediate_balance += transaction.data['amount'].amount
        balance_by_date[transaction.data['date']] = intermediate_balance

    return balance_by_date


def write_to_influxdb(data):
    client = InfluxDBClient(*config['influxdb_config'])

    for key, value in data.items():
        json_body = [
            {
                "measurement": "balance",
                "tags": {
                    "account": "default"
                },
                "time": datetime(key.year, key.month, key.day),
                "fields": {
                    "int_value": round(value),
                    "float_value": float(value)
                }
            }
        ]

        client.write_points(json_body)


if __name__ == '__main__':
    main()
