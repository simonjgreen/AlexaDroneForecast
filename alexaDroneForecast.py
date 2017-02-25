import urllib2
import json
import os
import datetime
import time

# Set environment variables in Lambda function for DARKSKY_API_KEY and GOOGLEMAPS_API_KEY
DARKSKY_API_KEY=os.environ['DARKSKY_API_KEY']
GOOGLEMAPS_API_KEY=os.environ['GOOGLEMAPS_API_KEY']

DARKSKY_API_BASE="https://api.darksky.net/forecast/"
GOOGLEMAPS_API_BASE="https://maps.googleapis.com/maps/api/"

# Acceptable flying conditions
acceptable = {}
acceptable["temperature"] = 5
acceptable["wind"] = 20         #in knots
acceptable["precipitationPercentage"] = 50

def lambda_handler(event, context):
    if (event['session']['application']['applicationId'] !=
        "amzn1.ask.skill.7b9ed983-663d-4686-bed3-efd207d64e46"):
        raise ValueError("Invalid Application ID")

    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetForecast":
        return get_forecast(intent)
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."

def get_forecast(intent):
    session_attributes = {}
    card_title = "Drone forecast"
    speech_output = "I'm not quite sure what you are asking for. " \
                    "Please try again."
    reprompt_text = speech_output
    should_end_session = False

    now = int(time.time())

    if "value" in intent ["slots"]["Date"]:
        date = amazon_date_to_unixtime(intent["slots"]["Date"]["value"])
    else:
        date = now

    if "value" in intent["slots"]["Location"]:
        location = intent["slots"]["Location"]["value"].title()
    else:
        location = "Tadley"

    coords = get_coordinates(location)

    darkskycall = DARKSKY_API_BASE + DARKSKY_API_KEY + "/" + coords
    print("Calling: " + darkskycall)
    response = urllib2.urlopen(darkskycall)
    fullforecast = json.load(response)

    maxForCurrent = now + (60 * 60 * 6)
    maxForDaily = now + (60 * 60 * 24 * 8)
    dateIsFuture = False
    if date < maxForCurrent:
        print("Using current weather")
        forecast = fullforecast["currently"]
    elif date > maxForDaily:
        print("Requested date out of bounds")
        speech_output = "Sorry, I can't go that far ahead"
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    else:
        print("Future day chosen")
        dailyforecasts = fullforecast["daily"]["data"]
        closestForecastIdx, closestForecastTime = min(enumerate(dailyforecasts), key=lambda x:abs(x[1]['time']-date))
        print(closestForecastIdx)
        print(closestForecastTime)
        forecast = fullforecast["daily"]["data"][closestForecastIdx]
        dateIsFuture = True

    card_title = "Drone forecast for " + location

    currentlysummary = forecast["summary"]
    summary = forecast["summary"]

    if dateIsFuture == True:
        farenheitTemperature = (forecast["temperatureMin"] + forecast["temperatureMax"]) / 2
    else:
        farenheitTemperature = forecast["temperature"]

    temperature = int(farenheit_to_celsius(farenheitTemperature))
    farenheitDewpoint = forecast["dewPoint"]
    dewpoint = int(farenheit_to_celsius(farenheitDewpoint))
    windBearing = forecast["windBearing"]
    windSpeedMPH = forecast["windSpeed"]
    windSpeedKts = int(windSpeedMPH * 0.869)
    precipitationProb = forecast["precipProbability"]
    precipitationPercentage = int(precipitationProb * 100)
    precipitationType = forecast["precipType"]

    acceptableConditions = is_acceptable(temperature,windSpeedKts,precipitationPercentage)
    if acceptableConditions == True:
        conditionsText = "appear to be favourable"
    else:
        conditionsText = "appear to not be favourable"

    speech_output = "Conditions for flying " + conditionsText + ". " \
        + "The weather in " + location + " will be " + summary + ". " \
        + "Wind from <say-as interpret-as=\"spell-out\">" + str(windBearing) \
        + "</say-as> degrees at <say-as interpret-as=\"spell-out\">" + str(windSpeedKts) + "</say-as> knots. " \
        + "Temperature <say-as interpret-as=\"spell-out\">" + str(temperature) + "</say-as> celsius, " \
        + "dewpoint <say-as interpret-as=\"spell-out\">" + str(dewpoint) + "</say-as> celsius. " \
        + "There is a " + str(precipitationPercentage) + " percent chance of " + precipitationType + "."

    reprompt_text = speech_output

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def is_acceptable(temperature,windSpeedKts,precipitationPercentage):
    if temperature < acceptable["temperature"]:
        return False
    elif windSpeedKts > acceptable["wind"]:
        return False
    elif precipitationPercentage > acceptable["precipitationPercentage"]:
        return False
    else:
        return True

def farenheit_to_celsius(farenheit):
    celsius = (farenheit - 32) * 5/9
    return celsius

def amazon_date_to_unixtime(amazondate):
    date = datetime.datetime.strptime(amazondate, '%Y-%m-%d')
    return int(time.mktime(date.timetuple()))

def get_coordinates(location):
    googlemapscall = GOOGLEMAPS_API_BASE + "geocode/json?address=" + location + "&key=" + GOOGLEMAPS_API_KEY
    print("Calling: " + googlemapscall)
    response = urllib2.urlopen(googlemapscall)
    geocode = json.load(response)
    lat = str(geocode["results"][0]["geometry"]["location"]["lat"])
    lng = str(geocode["results"][0]["geometry"]["location"]["lng"])
    coords = lat + "," + lng
    return coords

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
