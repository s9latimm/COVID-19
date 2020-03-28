# COVID-19-GeoPlot

A tool to visualize up-to-date case data published by the [ECDC](https://www.ecdc.europa.eu).

Please note that daily numbers only include yesterday (today's cases will appear tomorrow) and request may not work until current data is uploaded.

### Usage

``` 
usage: covid.py [-h] [-c <str>] [-C <list<str>>] [-S <str>] [-s]
                [-d <datetime>] [-L] [-l]

optional arguments:
  -h, --help            show this help message and exit
  -c <str>, --column <str>
                        one of ['cases', 'deaths']
  -C <list<str>>, --country <list<str>>
                        comma separated list of GeoIDs (e.g. "DE,US")
  -S <str>, --suffix <str>
                        use suffix in filename instead of date
  -s, --show            show plot instead of saving
  -d <datetime>, --date <datetime>
                        date (yyyy-mm-dd)
  -L, --list            list available GeoIDs and exit
  -l, --log             logarithmic scale

```

### Examples

Logarithmic plot of worldwide cases:

![WORLD LOG](plots/covid-19-world-cases-log-example.svg?sanitize=true)

Linear and logarithmic plots of cases in Germany:

![DE LIN](plots/covid-19-de-cases-example.svg?sanitize=true)
![DE LOG](plots/covid-19-de-cases-log-example.svg?sanitize=true)

