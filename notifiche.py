import redis
import time

# Connessione al server Redis
r = redis.StrictRedis(
        host='redis-12921.c135.eu-central-1-1.ec2.redns.redis-cloud.com', 
        port=12921,
        username='marmellata',
        password='c5Mmg!&AmVqg9dvX#9GF',
        decode_responses=True,
        ssl=False
    )

def ricevi_notifiche(utente):
    # Sottoscrizione al canale delle notifiche per l'utente specificato
    p = r.pubsub()
    p.subscribe(f'chat:*:{utente}')

    # controllo se iltype è diverso da None
    # Ricezione delle notifiche
    for message in p.listen():
        # Elaborazione del messaggio ricevuto
        if message['type'] == 'message':
            print(f"Notifica ricevuta per l'utente {utente}: {message['data']}")

def invia_notifica(utente, messaggio):
    # Invio della notifica al canale dell'utente specificato
    r.publish(utente, messaggio)

if __name__=='__main__':
    # Esempio di utilizzo
    utente = 'utente1'
    messaggio = 'Hai ricevuto un nuovo messaggio'

    # Invio della notifica
    invia_notifica(utente, messaggio)

    # Simulazione di un utente che riceve la notifica mentre è offline
    time.sleep(5)

    # Ricezione delle notifiche per l'utente
    ricevi_notifiche(utente)