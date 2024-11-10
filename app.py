import datetime
import time
import googlemaps
import polyline
import boto3
import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
GOOGLE_API = os.getenv("GOOGLE_API")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
bot_id = os.getenv("bot_id")
bot_alias_id = os.getenv("bot_alias_id")

bot_client = boto3.client(
    'lexv2-runtime', region_name="us-east-1", 
    aws_access_key_id=AWS_ACCESS_KEY, 
    aws_secret_access_key=AWS_SECRET_KEY
)
gmaps = googlemaps.Client(key=GOOGLE_API)

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/api/message", methods=["POST"])
def post_message():
    time.sleep(1)
    json = request.get_json()

    try:
        response = bot_client.recognize_text(
            botId=bot_id,
            botAliasId=bot_alias_id,
            localeId="en_US",
            sessionId=json.get("session"),
            text=json.get("message")
        )
        if response.get("ResponseMetadata").get("HTTPStatusCode") == 200:
            if len(response.get("messages")):
                message = response.get("messages")[0].get("content")
                if message[0] == "*":
                    origin, destination = message[1:].split("//")
                    path = walking_route(origin, destination)
                    return {
                        "path":path
                    }
                return {
                    "message": message
                }
        return {
            "message":"Oops, I didn't understood, can you try an other prompt?"
        }
    except Exception as e:
        print(e)
        return {
            "message":"Oops, I didn't understood, can you try an other prompt?"
        }

HALLS = {
    "capen": "Capen Hall",
    "davis": "Davis Hall",
    "greiner": "Greiner Hall",
    "baird": "Baird Hall",
    "slee": "Slee Hall",
    "clemens": "Clemens Hall",
    "baldy": "Baldy Hall",
    "norton": "Norton Hall",
    "obrian": "O'Brian Hall",
    "park": "Park Hall",
    "knox": "Knox Hall",
    "talbert": "Talbert Hall",
    "hoschstetter": "Hochstetter Hall",
    "cooke": "Cooke Hall",
    "fronczak": "Fronczak Hall",
    "ketter": "Ketter Hall",
    "jarvis": "Jarvis Hall",
    "furnas": "Furnas Hall",
    "bell": "Bell Hall",
    "roosevelt": "Roosevelt Hall",
    "lehman": "Lehman Hall",
    "clinton": "Clinton Hall",
    "dewey": "Dewey Hall",
    "bonner": "Bonner Hall",
    "governor": "Governor Residence Halls",
    "lockwood": "Lockwood Library",
    "silverman": "Silverman Library",
}

def check_hall_place(place):
    place_list = place.split(' ')
    if len(place_list) == 1 and HALLS.get(place.lower()):
        place = HALLS.get(place.lower())
    return place



def walking_route(origin, destination):
    now = datetime.datetime.now()
    origin = check_hall_place(origin)
    destination = check_hall_place(destination)
    directions_result = gmaps.directions(
        f'{origin}, University at Buffalo, Buffalo, NY',
        f'{destination}, University at Buffalo, Buffalo, NY',
        mode="walking",
        departure_time=now
    )
    if len(directions_result):
        decoded_poly = directions_result[0].get("overview_polyline").get("points")
        decoded_poly = polyline.decode(decoded_poly)
        new_poly = []
        for line in decoded_poly:
            new_poly.append([line[1], line[0]])
        return new_poly
    return False

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)