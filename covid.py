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

# -*- coding: utf-8 -*-
"""COVID-19-GeoPlot"""

import os
import sys
import math
import signal
import argparse
import datetime
from datetime import timedelta
import pprint
import matplotlib.pyplot as plt
import xlrd
import requests

COLUMNS = {'cases': 4, 'deaths': 5}
URL = 'https://www.ecdc.europa.eu/sites/default/files/documents/' \
      'COVID-19-geographic-disbtribution-worldwide'


class GeoPlot:
    """Visualize up-to-date case data published by the ECDC."""

    def __init__(self):
        self.date = None
        self.parser = argparse.ArgumentParser()
        self.args = None
        self.countries = None

    def poll(self):
        """Get raw sheet from ECDC server."""
        rep = 0
        while True:
            url = f'{URL}-{self.date.strftime("%Y-%m-%d")}.xlsx'
            try:
                req = requests.get(url)
            except requests.exceptions.ConnectionError as err:
                self.parser.error(err)
            print(f'[GET] {url} {req.status_code}')
            if req.status_code == 200:
                break
            if rep > 3:
                self.parser.error('could not get dataset')
            elif rep == 3:
                self.date = datetime.date.today()
            else:
                self.date -= timedelta(days=1)
            rep += 1
        return req.content

    def parse_args(self):
        """Parse options."""
        self.parser.add_argument('-c',
                                 '--column',
                                 metavar='<str>',
                                 type=str,
                                 default='cases',
                                 help=f'one of {list(COLUMNS.keys())}')
        self.parser.add_argument(
            '-C',
            '--country',
            metavar='<list<str>>',
            type=str,
            default='*',
            help=f'comma separated list of GeoIDs (e.g. "DE,US")')
        self.parser.add_argument('-S',
                                 '--suffix',
                                 metavar='<str>',
                                 type=str,
                                 default='',
                                 help=f'use suffix in filename instead of date')
        self.parser.add_argument('-s',
                                 '--show',
                                 default=False,
                                 action='store_true',
                                 help='show plot instead of saving')
        self.parser.add_argument('-d',
                                 '--diff',
                                 default=False,
                                 action='store_true',
                                 help='plot differentiation')
        self.parser.add_argument(
            '-D',
            '--date',
            metavar='<datetime>',
            type=str,
            default=datetime.date.today().strftime('%Y-%m-%d'),
            help=f'date (yyyy-mm-dd)')
        self.parser.add_argument('-L',
                                 '--list',
                                 default=False,
                                 action='store_true',
                                 help='list available GeoIDs and exit')
        self.parser.add_argument('-l',
                                 '--log',
                                 default=False,
                                 action='store_true',
                                 help='logarithmic scale')
        self.args = self.parser.parse_args()

    @staticmethod
    def get_regions(table):
        """Collect all available GeoIDs."""
        countries = dict()
        skip = True
        for row in table.get_rows():
            if skip:
                skip = False
                continue
            countries[row[7].value.strip()] = row[6].value.replace('_',
                                                                   ' ').strip()
        countries['*'] = 'World'
        return countries

    @staticmethod
    def log(number):
        """Calculate logarithm base 10."""
        return math.log10(number) if number > 0 else 0

    def get_data(self, table):
        """Extract data from table."""
        raw = dict()
        idx = COLUMNS[self.args.column]
        skip = True
        for row in table.get_rows():
            if skip:
                skip = False
                continue
            try:
                if 'WORLD' in self.countries or row[7].value.strip(
                ) in self.countries:
                    key = int(row[0].value)
                    if key in raw.keys():
                        raw[key] += int(row[idx].value)
                    else:
                        raw[key] = int(row[idx].value)
            except ValueError:
                continue
        if not raw:
            self.parser.error('no data')
        data = [(0, 0, 0, self.date)]
        for i in range(min({i for i in raw if raw[i] > 0}),
                       max(raw.keys()) + 1):
            if i in raw.keys():
                val = data[-1][1] + raw[i]
                diff = self.log(val) - self.log(
                    data[-1][1]) if self.args.log else val - data[-1][1]
                data.append(
                    (raw[i], val, diff,
                     datetime.datetime(*xlrd.xldate_as_tuple(i, 0)).strftime(
                         '%Y-%m-%d')))
            else:
                data.append(
                    (0, data[-1][1], 0,
                     datetime.datetime(*xlrd.xldate_as_tuple(i, 0)).strftime(
                         '%Y-%m-%d')))
        if self.args.log:
            data[1] = (data[1][0], data[1][1], 0, data[1][3])
        return data[1:]

    @staticmethod
    def handler(*_):
        """Handle SIGINT and SIGKILL."""
        print('[ABORT]')
        sys.exit(0)

    def plot(self, data):
        """Show or save plot of data."""
        fig, ax1 = plt.subplots()
        ax1.margins(x=.01, y=.01)
        ax1.spines['top'].set_visible(False)
        if self.args.diff:
            ax1.plot([i[3] for i in data], [i[2] for i in data],
                     '-',
                     color='tab:red')
            ax1.set_ylabel(f'differentiation', color='tab:red')
        else:
            ax1.bar([i[3] for i in data], [i[0] for i in data], color='tab:red')
            ax1.set_ylabel(f'new {self.args.column} per day', color='tab:red')
        ax1.tick_params(axis='y', labelcolor='tab:red')
        ax1.tick_params(axis='x', labelrotation=90)
        ax1.set_title(
            f'COVID-19 {" ".join(self.countries)}{" LOG" if self.args.log else ""}'
            f'{" DIFF" if self.args.diff else ""} ({data[1][3]} → {data[-1][3]})'
        )
        ax2 = ax1.twinx()
        ax2.margins(x=.01, y=.01)
        ax2.plot([i[3] for i in data], [i[1] for i in data],
                 'o-',
                 color='tab:blue')
        ax2.set_ylabel(self.args.column, color='tab:blue')
        if self.args.log:
            ax2.set_yscale('log')
        ax2.tick_params(axis='y', labelcolor='tab:blue')
        fig.set_size_inches(20, 10, forward=True)
        fig.tight_layout()
        if self.args.show:
            plt.show()
        else:
            suffix = self.date.strftime(
                "%Y-%m-%d") if not self.args.suffix else self.args.suffix
            file = f'plots/covid-19-{"-".join(self.countries)}-{self.args.column}' \
                   f'{"-log" if self.args.log else ""}' \
                   f'{"-diff" if self.args.diff else ""}' \
                   f'-{suffix}' \
                   f'.svg'.lower()
            print(f'[SAVE] {os.path.abspath(file)}')
            plt.savefig(file)
        print('[CLOSE]')
        plt.close()

    def main(self):
        """Entry point."""
        signal.signal(signal.SIGINT, self.handler)
        signal.signal(signal.SIGTERM, self.handler)
        self.parse_args()
        try:
            self.date = datetime.datetime.strptime(self.args.date, '%Y-%m-%d')
        except ValueError as err:
            self.parser.error(err)
        table = xlrd.open_workbook(file_contents=self.poll()).sheet_by_index(0)
        if self.args.list:
            pprint.PrettyPrinter(indent=2).pprint(self.get_regions(table))
            return 0
        if self.args.column not in COLUMNS.keys():
            self.parser.error(f'column must be one of {list(COLUMNS)}')
        self.countries = sorted(
            {i.strip() for i in self.args.country.strip().split(',')})
        regions = self.get_regions(table)
        for country in self.countries:
            if country not in regions.keys():
                self.parser.error(f'no data for {country}')
        if '*' in self.countries:
            self.countries = {'WORLD'}
        self.plot(self.get_data(table))
        return 0


if __name__ == '__main__':
    sys.exit(GeoPlot().main())
