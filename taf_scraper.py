import requests
from bs4 import BeautifulSoup


def scrape_airport_taf(icao_code):
    """
    TAF: Terminal Aerodrome Forecast
    # Read TAF from aviation weather
    # Input: Airport ICAO Code
    # Output: list of strings with TAF information
    """

    station_url = get_airport_url(icao_code)

    r = requests.get(station_url)

    soup = BeautifulSoup(r.content)

    # get elements within the 'awc_main_content' tag
    main_content = soup.find('div', attrs={'id': 'awc_main_content'})

    # get elements within the code tag
    code = main_content.find('code')

    # convert object to text and split into strings
    taf = code.text.split('\xa0')

    # remove blank rows
    taf = [x for x in taf if x != '']

    # strip leading and trailing characters
    taf = [x.strip() for x in taf]

    return taf


def get_airport_url(icao_code):
    """
    This function returns the correct url for a given airport
    # Input: Airport ICAO code
    # Output: URL to terminal aerodrome forecast
    """
    icao_code = icao_code.upper()

    base_url = 'https://www.aviationweather.gov/taf/data?ids=XXXX&format=raw&metars=off&layout=off'

    return base_url.replace('XXXX', icao_code)


taf = scrape_airport_taf('KORD')
