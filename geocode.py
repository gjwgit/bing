import requests
import sys
import os
import argparse

from mlhub.utils import get_private


def geocode(address, key, nhood=False, max=1, url=None):
    """Generate potential latitude and longitude coordinates.

    Arguments
    ---------

    address (str) The address to look up.

    key (str) The bing maps key.

    nhood (bool) Whether to include the neighbourhood.

    max (int) The maximum number of matches.

    url (str) Whether to return a URL string: None, Google, Bing, OSM.

    Return
    ------

    string The matched information, comma separated:
      lat:long,bbox,confidence,type,code,address
    OR
    string A URL ready to be used within a browser.
    """

    result = []

    # Bing Maps API endpoint for Australian addresses.

    API_URL = (
        "http://dev.virtualearth.net/REST/v1/Locations?culture=" +
        f"en-AU&query={address}&inclnb={nhood}&include=" +
        f"queryParse&maxResults={max}&userRegion=AU&key=" +
        f"{key}")

    # Get JSON response from Bing Maps API.

    response = requests.get(API_URL).json()

    # If the estimatedTotal is 1 or more than 1

    if response["resourceSets"][0]['estimatedTotal'] > 0:

        locations = response["resourceSets"][0]["resources"]

        loc = ""

        for item in locations:
            latitude = item["point"]["coordinates"][0]
            longitude = item["point"]["coordinates"][1]
            bbox = ":".join(map(str, item["bbox"]))
            address = f'{item["address"]["formattedAddress"]}, '
            address += f'{item["address"]["countryRegion"]}'
            confidence = item["confidence"]
            etype = item["entityType"]
            code = ":".join(item["matchCodes"])

            if url:
                if url == "bing":
                    loc = "https://bing.com/maps"
                    loc += f"?cp={latitude}~{longitude}&lvl=12&style=b"
                elif url == "google":
                    loc = "https://maps.google.com/"
                    loc += f"?q={latitude},{longitude}"
                else:
                    loc = "http://www.openstreetmap.org/"
                    loc += f"?mlat={latitude}&mlon={longitude}&zoom=12"
            else:
                loc = f'{latitude}:{longitude},{bbox},'
                loc += f"{confidence},{etype},{code},{address}"

            result.append(loc)

    else:
        print("No locations identified from the provided address.")
        sys.exit(1)

    return result


if __name__ == "__main__":

    # Private file stores the Bing Maps key required by the geocoding
    # function.

    PRIVATE_FILE = "private.json"
    path = os.path.join(os.getcwd(), PRIVATE_FILE)

    private_dic = get_private(path, "bing")

    # Read Bing Maps key from the private file for authentication
    # through Bing Maps API.

    if "key" in private_dic:
        BING_MAPS_KEY = private_dic["key"]
    else:
        print(f"There is no key in '{PRIVATE_FILE}'.\n" +
              "Please run 'ml configure bing' to enter your key.",
              file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Bing Maps')

    parser.add_argument(
        'address',
        type=str,
        nargs='*',
        help='location to geocode')

    parser.add_argument(
        '--neighbourhood', '-n',
        help='include neighbourhood of the address.')

    parser.add_argument(
        '--max', '-m',
        type=int,
        default=5,
        help='maximun number of locations to return (1-20)')

    parser.add_argument(
        '--url', '-u',
        action="store_true",
        help='return map URL (Open Street Map)')

    parser.add_argument(
        '--osm', '-o',
        action="store_true",
        help='return Open Street Map map URL')

    parser.add_argument(
        '--bing', '-b',
        action="store_true",
        help='return Bing map URL')

    parser.add_argument(
        '--google', '-g',
        action="store_true",
        help='return Google map URL')

    args = parser.parse_args()

    address = " ".join(args.address)
    nhood = 1 if args.neighbourhood else 0
    max = args.max
    url = "osm" if args.osm or args.url else "bing" if args.bing else \
        "google" if args.google else None

    try:
        result = geocode(address, BING_MAPS_KEY, nhood, max, url)
        print("\n".join(result))

    except Exception as e:
        print(f"The bing map key is invalid: {e}" +
              "\nRun 'ml configure bing' to update the key.",
              file=sys.stderr)
        sys.exit(1)
