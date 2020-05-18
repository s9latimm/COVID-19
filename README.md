# COVID-19-GeoPlot

A tool to visualize daily case data published by the [ECDC](https://www.ecdc.europa.eu/en/copyright).

Please note that daily numbers only include yesterday (today's cases will appear tomorrow) and request may not work until current data is uploaded.

### Usage

```
usage: covid.py [-h] [-c <str>] [-C <list<str>>] [-b <int>] [-S <str>] [-s]
                [-D <datetime>] [-L] [-l] [-d] [-x]

optional arguments:
  -h, --help            show this help message and exit
  -c <str>, --column <str>
                        one of ['cases', 'deaths']
  -C <list<str>>, --country <list<str>>
                        comma separated list of country codes (e.g. "DEU,USA")
  -b <int>, --base <int>
                        logarithm base
  -S <str>, --suffix <str>
                        use suffix in filename instead of date
  -s, --show            show plot instead of saving
  -D <datetime>, --date <datetime>
                        date (yyyy-mm-dd)
  -L, --list            list available country codes and exit
  -l, --log             logarithmic scale
  -d, --dark            dark background
  -x, --xkcd            xkcd style
```

### Examples (updated daily)

![WORLD](https://gitlab.com/s9latimm/covid-19-geoplot/-/jobs/artifacts/master/raw/plots/covid-19-world-cases-example.svg?job=deploy&sanitize=true)

![DE](https://gitlab.com/s9latimm/covid-19-geoplot/-/jobs/artifacts/master/raw/plots/covid-19-deu-cases-example.svg?job=deploy&sanitize=true)

![DE LOG2 DIFF](https://gitlab.com/s9latimm/covid-19-geoplot/-/jobs/artifacts/master/raw/plots/covid-19-deu-cases-log2-example.svg?job=deploy&sanitize=true)
