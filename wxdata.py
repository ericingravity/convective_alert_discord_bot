import json, pgeocode, requests
from urllib.request import urlopen
from tinydb import TinyDB, Query, where


db_file = "wxdata.json"


def add_user(user, zip, threshold=1):
    if not user or not zip:
        return

    dictionary = {
        "user": user,
        "zip": zip,
        "threshold": threshold,
        "alerted": "No"
    }

    db = TinyDB(db_file)
    db.insert(dictionary)


def remove_user(user):
    if not user:
        return

    db = TinyDB(db_file)
    db.remove(where('user') == user)
    query = Query()
    removed = db.search(query.user == user)

    if not removed:
        return False
    else:
        return True


def user_exists(user):
    if not user:
        return False

    db = TinyDB(db_file)
    query = Query()
    user_exists = db.search(query.user == user)

    if not user_exists:
        return False
    else:
        return True


def get_lat_lon_by_zip(zip):
    nomi = pgeocode.Nominatim('us')
    coords = {
        "latitude": nomi.query_postal_code(zip).latitude,
        "longitude": nomi.query_postal_code(zip).longitude
    }

    return coords


def get_convective_outlook(lat, lon, day=1):
    url = r"http://mesonet.agron.iastate.edu/json/spcoutlook.py"

    # check if site is up
    response_code = requests.get(url)
    if response_code.status_code != 200:

        outlook_dict = {
            "number": 6,
            "text": "Unknown"
        }

        return outlook_dict

    pluggable_lat = "&lat=" + lat
    pluggable_lon = "?lon=" + lon
    pluggable_day = "&day=" + str(day)
    post_url = "&time=now&cat=CATEGORICAL"
    whole_url = url + pluggable_lon + pluggable_lat + pluggable_day + post_url

    # get the outlook
    data = urlopen(whole_url).read()
    output = json.loads(data)

    if "threshold" in str(output):
        outlook = str(output['outlook']['threshold'])
    else:
        outlook = "NONE"

    # beautify the outlook
    if outlook == "NONE":
        outlook_dict = {
            "number": -1,
            "text": "None"
            }

    elif outlook == "TSTM":
        outlook_dict = {
            "number": 0,
            "text": "Thunderstorm"
        }

    elif outlook == "MRGL":
        outlook_dict = {
            "number": 1,
            "text": "Marginal"
        }

    elif outlook == "SLGT":
        outlook_dict = {
            "number": 2,
            "text": "Slight"
        }

    elif outlook == "ENH":
        outlook_dict = {
            "number": 3,
            "text": "Enhanced"
        }

    elif outlook == "MDT":
        outlook_dict = {
            "number": 4,
            "text": "Moderate"
        }

    elif outlook == "HIGH":
        outlook_dict = {
            "number": 5,
            "text": "High"
        }

    else:
        outlook_dict = {
            "number": 6,
            "text": "Unknown"
        }

    # and return
    return outlook_dict


def background_weather():
    db = TinyDB(db_file)
    query = Query()

    msg_list = []

    for item in db:
        # if alerted, skip
        alerted = item['alerted']
        if alerted == "Yes":
            continue

        userid = item['user']
        zip = item['zip']
        threshold = item['threshold']

        latlon = get_lat_lon_by_zip(zip)
        lat = str(latlon['latitude'])
        lon = str(latlon['longitude'])

        outlook = get_convective_outlook(lat, lon)
        outlook_number = outlook['number']
        outlook_text = outlook['text']

        if outlook_number >= threshold:
            db.update({'alerted': 'Yes'}, query.user == userid)
            msg = "<@!" + userid + ">  `[" + str(outlook_number) + ":" + outlook_text + "] risk for your area today.`"
            msg_list.append(msg)

    return msg_list


def clear_alerted():
    db = TinyDB(db_file)
    db.update({'alerted': 'No'})
