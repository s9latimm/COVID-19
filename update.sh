#!/bin/bash

git stash

./covid.py --log --suffix example
git add --force plots/covid-19-world-cases-log-example.svg

./covid.py --country DE --suffix example
git add --force plots/covid-19-de-cases-example.svg

./covid.py --country DE --log --suffix example
git add --force plots/covid-19-de-cases-log-example.svg

git commit -m "Update examples"

git push

git stash pop
