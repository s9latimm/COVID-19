#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2020 Lauritz Timm
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
import xlrd
import datetime
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os
import pprint

COLUMNS = {'cases': 4, 'deaths': 5}
URL = 'https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--column', metavar='<str>', type=str, default='cases',
                        help=f'one of {[i for i in COLUMNS.keys()]}')
    parser.add_argument('-C', '--country', metavar='<list<str>>', type=str, default='*',
                        help=f'comma separated list of GeoIDs (e.g. "DE,US")')
    parser.add_argument('-s', '--show', default=False, action='store_true', help='show plot instead of saving')
    parser.add_argument('-L', '--list', default=False, action='store_true', help='list available GeoIDs')
    parser.add_argument('-l', '--log', default=False, action='store_true', help='logarithmic scale')
    args = parser.parse_args()
    today = datetime.date.today().strftime('%Y-%m-%d')
    cnt = requests.get(f'{URL}-{today}.xlsx').content
    table = xlrd.open_workbook(file_contents=cnt).sheet_by_index(0)
    countries = dict()
    for row in table.get_rows():
        countries[row[7].value.strip()] = row[6].value.replace('_', ' ').strip()
    countries['*'] = 'World'
    del countries['GeoId']
    if args.list:
        pprint.PrettyPrinter(indent=2).pprint(countries)
        return 0
    if args.column not in COLUMNS.keys():
        parser.error(f'column must be one of {[i for i in COLUMNS.keys()]}')
    idx = COLUMNS[args.column]
    country = sorted({i.strip() for i in args.country.strip().split(',')})
    for c in country:
        if c not in countries.keys():
            parser.error(f'no data for {c}')
    if '*' in country:
        country = {'WORLD'}
    raw = dict()
    for row in table.get_rows():
        try:
            if 'WORLD' in country or row[7].value.strip() in country:
                key = int(row[0].value)
                if key in raw.keys():
                    raw[key] += int(row[idx].value)
                else:
                    raw[key] = int(row[idx].value)
        except ValueError:
            continue
    if not raw:
        parser.error('no data')
    data = [(0, 0, datetime.date.today())]
    for i in range(min({i for i in raw.keys() if raw[i] > 0}), max(raw.keys()) + 1):
        if i in raw.keys():
            data.append(
                (raw[i], data[-1][1] + raw[i], datetime.datetime(*xlrd.xldate_as_tuple(i, 0)).strftime('%Y-%m-%d')))
        else:
            data.append((0, data[-1][1], datetime.datetime(*xlrd.xldate_as_tuple(i, 0)).strftime('%Y-%m-%d')))
    fig, ax1 = plt.subplots()
    color = 'tab:blue'
    ax2 = ax1.twinx()
    ax2.plot([i[2] for i in data[1:]], [i[1] for i in data[1:]], 'o-', color=color)
    ax2.set_ylabel(args.column, color=color)
    if args.log:
        ax2.set_yscale('log')
    else:
        ax2.set_ylim(bottom=0)
    ax2.tick_params(axis='y', labelcolor=color)
    color = 'tab:red'
    ax1.bar([i[2] for i in data[1:]], [i[0] for i in data[1:]], color=color)
    ax1.set_ylabel(f'new {args.column} per day', color=color)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', labelrotation=90)
    ax1.set_title(f'COVID-19 {" ".join(country)} ({data[1][2]} → {data[-1][2]})')
    fig.set_size_inches(20, 10, forward=True)
    fig.tight_layout()
    if args.show:
        plt.show()
    else:
        file = f'plots/covid-19-{"-".join(country)}-{args.column}{"-log" if args.log else ""}-{today}.png'.lower()
        print(f'saving {os.path.abspath(file)}')
        plt.savefig(file)
    plt.close()
    return 0


if __name__ == '__main__':
    exit(main())
