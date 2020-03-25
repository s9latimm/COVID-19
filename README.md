# COVID-19-GeoPlot

A tool to visualize up-to-date case data published by the [ECDC](https://www.ecdc.europa.eu).

Please note that daily numbers only include yesterday (today's cases will appear tomorrow) and request may not work until current data is uploaded.

### Usage

``` 
  -h, --help            show this help message and exit
  -c <str>, --column <str>
                        one of ['cases', 'deaths']
  -C <list<str>>, --country <list<str>>
                        comma separated list of GeoIDs (e.g. "DE,US")
  -s, --show            show plot instead of saving
  -d <datetime>, --date <datetime>
                        date (yyyy-mm-dd)
  -L, --list            list available GeoIDs and exit
  -l, --log             logarithmic scale
```

### Examples

Logarithmic plot of cases from all regions:

![plots/covid-19-world-cases-log-2020-03-25.svg](plots/covid-19-world-cases-log-2020-03-25.svg?sanitize=true)

Linear plot of cases from Germany:

![plots/covid-19-de-cases-2020-03-25.svg](plots/covid-19-de-cases-2020-03-25.svg?sanitize=true)
