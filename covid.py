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
import matplotlib.pyplot as plt
import xlrd
import requests

COLUMNS = {'cases': 4, 'deaths': 5}
URL = 'https://www.ecdc.europa.eu/sites/default/files/documents/' \
      'COVID-19-geographic-disbtribution-worldwide'


class GeoPlot:
    """Visualize up-to-date case data published by the ECDC."""

    def __init__(self):
        self.args = None
        self.ids = None

    def parse_args(self, args):
        """Parse options."""
        parser = argparse.ArgumentParser()

        def column_ty(value):
            try:
                COLUMNS[value]
            except KeyError as err:
                raise argparse.ArgumentTypeError(
                    f'{err.__class__.__name__}: {err}')
            return value

        parser.add_argument('-c',
                            '--column',
                            metavar='<str>',
                            type=column_ty,
                            default='cases',
                            help=f'one of {list(COLUMNS.keys())}')
        parser.add_argument(
            '-C',
            '--country',
            metavar='<list<str>>',
            type=str,
            default='*',
            help=f'comma separated list of GeoIDs (e.g. "DE,US")')

        def base_ty(value):
            try:
                math.log(1, int(value))
            except (ValueError, ZeroDivisionError) as err:
                raise argparse.ArgumentTypeError(
                    f'{err.__class__.__name__}: {err}')
            return int(value)

        parser.add_argument('-b',
                            '--base',
                            metavar='<int>',
                            type=base_ty,
                            default=10,
                            help=f'logarithm base')
        parser.add_argument('-S',
                            '--suffix',
                            metavar='<str>',
                            type=str,
                            default='',
                            help=f'use suffix in filename instead of date')
        parser.add_argument('-s',
                            '--show',
                            default=False,
                            action='store_true',
                            help='show plot instead of saving')
        parser.add_argument('-d',
                            '--diff',
                            default=False,
                            action='store_true',
                            help='plot differentiation')

        def date_ty(value):
            try:
                return datetime.datetime.strptime(value, '%Y-%m-%d')
            except ValueError as err:
                raise argparse.ArgumentTypeError(
                    f'{err.__class__.__name__}: {err}')

        parser.add_argument('-D',
                            '--date',
                            metavar='<datetime>',
                            type=date_ty,
                            default=datetime.date.today(),
                            help=f'date (yyyy-mm-dd)')
        parser.add_argument('-L',
                            '--list',
                            default=False,
                            action='store_true',
                            help='list available GeoIDs and exit')
        parser.add_argument('-l',
                            '--log',
                            required='--base' in args or '-b' in args,
                            default=False,
                            action='store_true',
                            help='logarithmic scale')
        self.args = parser.parse_args(args)

    @staticmethod
    def error(msg):
        """Print message and exit."""
        print(f'[ERROR] {msg}')
        sys.exit(1)

    def poll(self):
        """Get raw data from ECDC server."""
        url = f'{URL}-{self.args.date.strftime("%Y-%m-%d")}.xlsx'
        try:
            print(f'[GET] {url}')
            req = requests.get(url)
            if req.status_code != 200:
                self.error(req.status_code)
            return req.content
        except requests.exceptions.RequestException as err:
            self.error(f'{err.__class__.__name__}: {err}')

    @staticmethod
    def get_regions(table):
        """Collect available GeoIDs."""
        regions = {
            i[7].value.strip(): i[6].value.replace('_', ' ').strip()
            for i in list(table.get_rows())[1:]
        }
        regions['*'] = 'World'
        return regions

    def log(self, number):
        """Calculate logarithm."""
        return math.log(max(number, 1), self.args.base)

    def get_data(self, table):
        """Extract data from table."""
        raw = dict()
        idx = COLUMNS[self.args.column]
        for row in list(table.get_rows())[1:]:
            try:
                if 'WORLD' in self.ids or row[7].value.strip() in self.ids:
                    key = int(row[0].value)
                    if key in raw.keys():
                        raw[key] += int(row[idx].value)
                    else:
                        raw[key] = int(row[idx].value)
            except ValueError as err:
                self.error(f'{err.__class__.__name__}: {err}')
        assert raw
        data = [(0, 0, 0, self.args.date)]
        for i in range(
                min({i for i in raw if i > 0 and raw[i] > 0}) - 1,
                max(raw.keys()) + 1):
            if i in raw.keys():
                val = data[-1][1] + raw[i]
                data.append(
                    (raw[i], val if not self.args.log else max(val, 1),
                     (self.log(val) -
                      self.log(data[-1][1]) if self.args.log else val -
                      data[-1][1]),
                     datetime.datetime(*xlrd.xldate_as_tuple(i, 0)).strftime(
                         '%Y-%m-%d')))
            else:
                data.append(
                    (0,
                     data[-1][1] if not self.args.log else max(data[-1][1], 1),
                     0, datetime.datetime(*xlrd.xldate_as_tuple(i, 0)).strftime(
                         '%Y-%m-%d')))
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
            f'COVID-19 {" ".join(self.ids)}{f" LOG{self.args.base}" if self.args.log else ""}'
            f'{" DIFF" if self.args.diff else ""} ({data[0][3]} → {data[-1][3]})'
        )
        ax2 = ax1.twinx()
        ax2.margins(x=.01, y=.01)
        ax2.plot([i[3] for i in data], [i[1] for i in data],
                 'o-',
                 color='tab:blue')
        ax2.set_ylabel(self.args.column, color='tab:blue')
        if self.args.log:
            ax2.set_yscale('log', basey=self.args.base)
        ax2.tick_params(axis='y', labelcolor='tab:blue')

        fig.set_size_inches(20, 10, forward=True)
        fig.tight_layout()
        if self.args.show:
            print('[SHOW]')
            plt.show()
        else:
            os.makedirs('plots', exist_ok=True)
            suffix = self.args.date.strftime(
                '%Y-%m-%d') if not self.args.suffix else self.args.suffix
            file = f'plots/covid-19-{"-".join(self.ids)}-{self.args.column}' \
                   f'{f"-log{self.args.base}" if self.args.log else ""}' \
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
        self.parse_args(sys.argv[1:])
        table = xlrd.open_workbook(file_contents=self.poll()).sheet_by_index(0)
        regions = self.get_regions(table)
        if self.args.list:
            _ = [print(f'[INFO] \'{i[0]}\': {i[1]}') for i in regions.items()]
        else:
            self.ids = sorted(
                {i.strip() for i in self.args.country.strip().split(',')})
            _ = [
                print(f'[INFO] \'{i}\': {regions[i]}')
                if i in regions.keys() else self.error(f'KeyError: \'{i}\'')
                for i in self.ids
            ]
            if '*' in self.ids:
                self.ids = {'WORLD'}
            self.plot(self.get_data(table))
        print('[EXIT]')
        return 0


if __name__ == '__main__':
    sys.exit(GeoPlot().main())
