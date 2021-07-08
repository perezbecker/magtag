import time
import terminalio
import displayio
import adafruit_imageload
from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag
from secrets import secrets


from adafruit_datetime import datetime, timedelta
#from calendar import mdays

# --| USER CONFIG |--------------------------
METRIC = True  # set to True for metric units
# -------------------------------------------

# ----------------------------
# Define various assets
# ----------------------------
BACKGROUND_BMP = "/bmps/weather_bg.bmp"
ICONS_LARGE_FILE = "/bmps/weather_icons_70px.bmp"
ICONS_SMALL_FILE = "/bmps/weather_icons_20px.bmp"
ICON_MAP = ("01", "02", "03", "04", "09", "10", "11", "13", "50")
#DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
DAYS = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")
'''
MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
'''
MONTHS = (
    "Januar",
    "Februar",
    "Maerz",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
)

mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

magtag = MagTag()

# ----------------------------
# Backgrounnd bitmap
# ----------------------------
magtag.graphics.set_background(BACKGROUND_BMP)

# ----------------------------
# Weather icons sprite sheet
# ----------------------------
icons_large_bmp, icons_large_pal = adafruit_imageload.load(ICONS_LARGE_FILE)
icons_small_bmp, icons_small_pal = adafruit_imageload.load(ICONS_SMALL_FILE)

# /////////////////////////////////////////////////////////////////////////


def get_data_source_url(api="onecall", location=None):
    """Build and return the URL for the OpenWeather API."""
    if api.upper() == "FORECAST5":
        URL = "https://api.openweathermap.org/data/2.5/forecast?"
        URL += "q=" + location
    elif api.upper() == "ONECALL":
        URL = "https://api.openweathermap.org/data/2.5/onecall?exclude=minutely,hourly,alerts"
        URL += "&lat={}".format(location[0])
        URL += "&lon={}".format(location[1])
    else:
        raise ValueError("Unknown API type: " + api)

    return URL + "&appid=" + secrets["openweather_token"]


def get_latlon():
    """Use the Forecast5 API to determine lat/lon for given city."""
    magtag.url = get_data_source_url(api="forecast5", location=secrets["openweather_location"])
    magtag.json_path = ["city"]
    raw_data = magtag.fetch()
    return raw_data["coord"]["lat"], raw_data["coord"]["lon"]


def get_forecast(location):
    """Use OneCall API to fetch forecast and timezone data."""
    resp = magtag.network.fetch(get_data_source_url(api="onecall", location=location))
    json_data = resp.json()
    return json_data["daily"], json_data["current"]["dt"], json_data["timezone_offset"]


def make_banner(x=0, y=0):
    """Make a single future forecast info banner group."""
    day_of_week = label.Label(terminalio.FONT, text="DAY", color=0x000000)
    day_of_week.anchor_point = (0, 0.5)
    day_of_week.anchored_position = (0, 10)

    icon = displayio.TileGrid(
        icons_small_bmp,
        pixel_shader=icons_small_pal,
        x=25,
        y=0,
        width=1,
        height=1,
        tile_width=20,
        tile_height=20,
    )

    day_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
    day_temp.anchor_point = (0, 0.5)
    day_temp.anchored_position = (50, 10)

    group = displayio.Group(max_size=3, x=x, y=y)
    group.append(day_of_week)
    group.append(icon)
    group.append(day_temp)

    return group


def temperature_text(tempK):
    if METRIC:
        return "{:3.0f}C".format(tempK - 273.15)
    else:
        return "{:3.0f}F".format(32.0 + 1.8 * (tempK - 273.15))


def wind_text(speedms):
    if METRIC:
        return "{:3.0f}m/s".format(speedms)
    else:
        return "{:3.0f}mph".format(2.23694 * speedms)


def update_banner(banner, data):
    """Update supplied forecast banner with supplied data."""
    banner[0].text = DAYS[time.localtime(data["dt"]).tm_wday][:3].upper()
    banner[1][0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    banner[2].text = temperature_text(data["temp"]["day"])


def update_today(data, tz_offset=0):
    """Update today info banner."""
    date = time.localtime(data["dt"])
    sunrise = time.localtime(data["sunrise"] + tz_offset)
    sunset = time.localtime(data["sunset"] + tz_offset)

    today_weekday.text = "{},".format(DAYS[date.tm_wday].upper())

    today_date.text = "{} {} {}".format(
        date.tm_mday,
        MONTHS[date.tm_mon - 1].upper(),
        date.tm_year
    )
    today_icon[0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    today_morn_temp.text = temperature_text(data["temp"]["morn"])
    today_day_temp.text = temperature_text(data["temp"]["day"])
    today_night_temp.text = temperature_text(data["temp"]["night"])
    today_humidity.text = "{:3d}%".format(data["humidity"])
    today_wind.text = wind_text(data["wind_speed"])
    today_sunrise.text = "{:02d}:{:02d}".format(sunrise.tm_hour, sunrise.tm_min)
    today_sunset.text = "{:02d}:{:02d}".format(sunset.tm_hour, sunset.tm_min)
    today_1st_sweep.text = secrets["FirstSweep"].split(",")[0]+": {:02d}".format(days_until_street_sweep(datetime(int(date.tm_year),int(date.tm_mon),int(date.tm_mday)),int(secrets["FirstSweep"].split(",")[1]),int(secrets["FirstSweep"].split(",")[2])))
    today_2nd_sweep.text = secrets["SecondSweep"].split(",")[0]+": {:02d}".format(days_until_street_sweep(datetime(int(date.tm_year),int(date.tm_mon),int(date.tm_mday)),int(secrets["SecondSweep"].split(",")[1]),int(secrets["SecondSweep"].split(",")[2])))

def go_to_sleep(current_time):
    """Enter deep sleep for time needed."""
    # compute current time offset in seconds
    hour, minutes, seconds = time.localtime(current_time)[3:6]
    seconds_since_midnight = 60 * (hour * 60 + minutes) + seconds
    # wake up 15 minutes after midnite
    seconds_to_sleep = (24 * 60 * 60 - seconds_since_midnight) + 15 * 60
    print(
        "Sleeping for {} hours, {} minutes".format(
            seconds_to_sleep // 3600, (seconds_to_sleep // 60) % 60
        )
    )
    magtag.exit_and_deep_sleep(seconds_to_sleep)

# DPB Functions

def days_until_street_sweep(the_date,nth_week,week_day):
    temp = the_date.replace(day=1)
    adj = (week_day - temp.weekday()) % 7
    temp += timedelta(days=adj)
    temp += timedelta(weeks=nth_week-1)
    firstOption = (temp - the_date).days
    if(firstOption >= 0):
        return firstOption
    else:
        new_date_temp=the_date.replace(day=1)
        new_date=new_date_temp + timedelta(mdays[new_date_temp.month])
        temp2 = new_date.replace(day=1)
        adj2 = (week_day - temp2.weekday()) % 7
        temp2 += timedelta(days=adj2)
        temp2 += timedelta(weeks=nth_week-1)
        secondOption = (temp2 - the_date).days
        return secondOption


# ===========
# U I
# ===========
today_weekday = label.Label(terminalio.FONT, text="?" * 5, color=0x000000)
today_weekday.anchor_point = (0, 0)
today_weekday.anchored_position = (15, 13)

today_date = label.Label(terminalio.FONT, text="?" * 5, color=0x000000)
today_date.anchor_point = (0, 0)
today_date.anchored_position = (15, 24)

#city_name = label.Label(
#    terminalio.FONT, text=secrets["openweather_location"], color=0x000000
#)
#city_name.anchor_point = (0, 0)
#city_name.anchored_position = (15, 24)

today_icon = displayio.TileGrid(
    icons_large_bmp,
    pixel_shader=icons_small_pal,
    x=10,
    y=40,
    width=1,
    height=1,
    tile_width=70,
    tile_height=70,
)

today_1st_sweep = label.Label(terminalio.FONT, text="1st Fri: 31", color=0x000000)
today_1st_sweep.anchor_point = (0.5, 0)
today_1st_sweep.anchored_position = (155, 13)

today_2nd_sweep = label.Label(terminalio.FONT, text="2nd Mon: 31", color=0x000000)
today_2nd_sweep.anchor_point = (0.5, 0)
today_2nd_sweep.anchored_position = (155, 24)

today_morn_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_morn_temp.anchor_point = (0.5, 0)
today_morn_temp.anchored_position = (118, 59)

today_day_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_day_temp.anchor_point = (0.5, 0)
today_day_temp.anchored_position = (149, 59)

today_night_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_night_temp.anchor_point = (0.5, 0)
today_night_temp.anchored_position = (180, 59)

today_humidity = label.Label(terminalio.FONT, text="100%", color=0x000000)
today_humidity.anchor_point = (0, 0.5)
today_humidity.anchored_position = (105, 95)

today_wind = label.Label(terminalio.FONT, text="99m/s", color=0x000000)
today_wind.anchor_point = (0, 0.5)
today_wind.anchored_position = (155, 95)

today_sunrise = label.Label(terminalio.FONT, text="12:12 PM", color=0x000000)
today_sunrise.anchor_point = (0, 0.5)
today_sunrise.anchored_position = (45, 117)

today_sunset = label.Label(terminalio.FONT, text="12:12 PM", color=0x000000)
today_sunset.anchor_point = (0, 0.5)
today_sunset.anchored_position = (130, 117)

today_banner = displayio.Group(max_size=10)
today_banner.append(today_weekday)
today_banner.append(today_date)
#today_banner.append(city_name)
today_banner.append(today_icon)
today_banner.append(today_morn_temp)
today_banner.append(today_day_temp)
today_banner.append(today_night_temp)
today_banner.append(today_humidity)
today_banner.append(today_wind)
today_banner.append(today_sunrise)
today_banner.append(today_sunset)
today_banner.append(today_1st_sweep)
today_banner.append(today_2nd_sweep)

future_banners = [
    make_banner(x=210, y=18),
    make_banner(x=210, y=39),
    make_banner(x=210, y=60),
    make_banner(x=210, y=81),
    make_banner(x=210, y=102),
]

magtag.splash.append(today_banner)
for future_banner in future_banners:
    magtag.splash.append(future_banner)

# ===========
#  M A I N
# ===========
print("Getting Lat/Lon...")
latlon = get_latlon()
print(secrets["openweather_location"])
print(latlon)

print("Fetching forecast...")
forecast_data, utc_time, local_tz_offset = get_forecast(latlon)

print("Updating...")
update_today(forecast_data[0], local_tz_offset)
for day, forecast in enumerate(forecast_data[1:6]):
    update_banner(future_banners[day], forecast)

print("Refreshing...")
time.sleep(magtag.display.time_to_refresh + 1)
magtag.display.refresh()
time.sleep(magtag.display.time_to_refresh + 1)

print("Sleeping...")
go_to_sleep(utc_time + local_tz_offset)
#  entire code will run again after deep sleep cycle
#  similar to hitting the reset button

