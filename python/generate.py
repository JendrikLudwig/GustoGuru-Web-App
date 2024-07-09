from requests.exceptions import Timeout
import requests

def queryLlama3(ing, client):
    completion = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {
            "role": "user",
            "content": "Erstelle ein deutsches Rezept mit folgenden Zutaten: "+ing+". Gib nur die Anleitung als HTML an, nicht mehr. Schreibe ALLES auf Deutsch. Nutze keine Tabellen. Nutze nur folgende HTML tags: h2, h3, p, li. Erstelle eine nummerierte Auflistung für die Zubereitung. Nutze nur für die Zubereitung eine Liste, ansonsten nirgends."
        }
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
    )

    # Initialisiere einen leeren Puffer
    buffer = []

    # Empfange und speichere alle Chunks im Puffer
    for chunk in completion:
        buffer.append(chunk.choices[0].delta.content or "")

    # Verbinde alle Teile zu einem vollständigen String
    complete_content = ''.join(buffer)
    
    return complete_content    


def queryCustomModel(ing, link):
    url = link+"/generate"
    payload = {'prompt': 'Erstelle ein Rezept nur aus diesen Zutaten, nutze keine weiteren Zutaten und gib nur die Zubereitung (Response) zurück: '+ing}

    try:
        # Führe die POST-Anfrage aus mit Timeout von 10 Minuten (600 Sekunden)
        response = requests.post(url, json=payload, timeout=600)
        
        # Überprüfe die Antwort
        if response.status_code == 200:
            print('Anfrage erfolgreich abgeschlossen.')
            print(str(response.json()))
            return str(response.json()).replace("'",'"')
        else:
            print(f'Fehler: Statuscode {response.status_code}')
        
    except Timeout:
        print('Die Anfrage wurde abgebrochen, da die Zeitüberschreitung von 10 Minuten erreicht wurde.')

    except Exception as e:
        print(f'Fehler bei der Anfrage: {str(e)}')
