import asyncio

# Funktion zum Starten einer asynchronen Aufgabe im Hintergrund
def start_background_task(loop, coro):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)