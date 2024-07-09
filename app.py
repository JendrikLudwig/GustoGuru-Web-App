from flask import Flask, render_template, jsonify, request
import uuid
import sqlite3
import threading
import json
import asyncio
from groq import Groq 
from python.chefkoch_rezepte import findClosestMatch 
from python.util import start_background_task
from python.search_ing import finde_passende_zutaten
from python.sql import getUser, insertUser, insertRecipe, getRecipe
from python.generate import queryCustomModel, queryLlama3

### Setup

# groqcloud tunnel link for connecting to google collab
COLAB_LINK = "https://f5f9-34-16-141-167.ngrok-free.app/"

# FlaskApp Setup
app = Flask(__name__, 
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

# Database Connection 
connection = sqlite3.connect("gustoguro.db", check_same_thread=False)

# Llama3 API Connection
client = Groq(
    api_key="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"
)

# GET "/" - Index
@app.route("/", methods = ["GET"])
def index():
    return render_template("index.html")

# GET "/rec/<parameter>" - Erhalte Wortvervollständigunsvorschläge für Zutaten
@app.route("/rec/<parameter>", methods = ["GET"])
def return_recommendation(parameter):
    data = {
        "words": finde_passende_zutaten(parameter, k=5)
    }
    return jsonify(data)

# GET "/p/<parameter>" - Öffne Rezeptseite mit ID
@app.route("/p/<parameter>", methods = ["GET"])
def recipe_page(parameter):
    # Daten  aus Datenbank ziehen über "parameter  "
    data = getRecipe(parameter, connection)
    print(type(data[1]))
    return render_template("recipe.html", elements=json.loads(data[1]), anleitung=json.loads(data[1])["anleitung"], anleitung_ck=json.loads(data[1])["anleitungCk"])

# GET "/d/<parameter>" - Erhalte Rezeptdaten mit ID
@app.route("/d/<parameter>", methods = ["GET"])
def recipe_data(parameter):
    data = getRecipe(parameter, connection)
    # Daten  aus Datenbank ziehen über "parameter"

    return jsonify(data)

# POST "/generate" - Generiere Rezept aus Zutaten. 
@app.route("/generate", methods = ["POST"])
def generate():
    if request.is_json:
        data = request.get_json()  
        rezepept_uuid = str(uuid.uuid4())
        
        # Rezept Struktur Anlegen.
        recipe_data = {
            "uuid":rezepept_uuid,
            "zutaten": data["ing"],
            "anleitung": {},
            "anleitungCk": {}
        }
        
        # Start der asynchronen Funktion im Hintergrund
        loop = asyncio.new_event_loop()
        threading.Thread(target=start_background_task, args=(loop, generateInstructions(rezepept_uuid, data["ing"], data["llama3"]))).start()


        #Struktur speichern und nutzer objekt zurücl geben
        insertRecipe(rezepept_uuid, json.dumps(recipe_data), connection)

        return jsonify({'uuid': recipe_data["uuid"]}), 200
    else:
        return jsonify({'error': 'Request must be JSON'}), 400
    
# POST "/newuser" - Neue Nutzer UUID anlegen (Wird aktuell nicht mehr genutzt. Diente in erster Linie zur Rezeptzuweisung)
@app.route("/newuser", methods=["POST"])
def newUser():
    user_uuid = str(uuid.uuid4())
    while True:
        if (len(getUser(user_uuid, connection)) == 0):
            break
        user_uuid = str(uuid.uuid4())

    insertUser(user_uuid, connection)
    return jsonify({
        "uuid":user_uuid
    })


# Co-Routine um die generiereung der Rezepte anzufragen.
async def generateInstructions(rezepept_uuid, data, llama3):
     # Rezept Struktur Anlegen und parallel generierung anfragen.
    anleitung = {}
    if(llama3):
        anleitung = queryLlama3(",".join(data), client)
    else:
        anleitung = queryCustomModel(",".join(data), COLAB_LINK)
    anleitungCk = findClosestMatch(",".join(data))

    recipe_data = {
            "uuid":rezepept_uuid,
            "zutaten": data,
            "anleitung": anleitung,
            "anleitungCk": anleitungCk
    }

    #Struktur speichern und nutzer objekt zurücl geben
    insertRecipe(rezepept_uuid, json.dumps(recipe_data), connection)


if __name__ == "__main__":
    app.run(debug=True)