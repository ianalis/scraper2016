# scrapER2016

This script scrapes data from `pilipinaselectionresults2016.com`. It downloads the json file for each political division up to the level of precincts then saves them into a directory structure mirroring the levels of political divisions. It will not redownload an already existing json file so multiple invocations of the script won't download everything again. It also allows specifying a specific region to download to allow parallelization over regions. Note that `/` in the name of a political division is replaced by `_`.

## Dependencies

The script runs on Python with [cloudflare-scrape](https://github.com/Anorov/cloudflare-scrape) module installed.

## Invocation

This is a python script which can be invoked by

    python scraper.py

or

    ./scraper.py

if on a Ubuntu or Debian-based machine.

It also accepts the following parameters:

    --basedir BASEDIR, -b BASEDIR  directory where to store data (default: data)
    --region REGION, -r REGION     region from where to scrape data (default: all regions)
    --delay_min DELAY_MIN          minimum delay between downloads, in seconds (default: 1)
    --delay_max DELAY_MAX          maximum delay between downloads, in seconds (default: 3)

## Acknowledgement

I thank Aivin Solatorio for making me aware of the existence of the `cloudflare-scrape` module. I would have used Selenium, which is more cumbersome.
