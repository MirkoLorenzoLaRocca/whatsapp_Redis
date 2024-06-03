<img src="https://img.shields.io/badge/redis-CC0000.svg?&style=for-the-badge&logo=redis&logoColor=white"/><img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blu"/><img src="https://img.shields.io/badge/powershell-5391FE?style=for-the-badge&logo=powershell&logoColor=white"/>

# Whatsapp copy with Redis

WhatsApp Redis è un'applicazione Python che utilizza Redis come database per implementare un sistema di messaggistica con le seguenti funzionalità:

1. **Registrazione Utente**: Permette agli utenti di registrarsi e creare un profilo. 
2. **Chat Live:** Fornisce la possibilità di scambiare messaggi in tempo reale.
3. **Chat a Tempo:** Permette di inviare messaggi che si autodistruggono dopo un minuto.
4. **Modalità Non Disturbare:** Gli utenti possono attivare questa modalità per evitare di ricevere notifiche in tempo reale.
5. **Notifiche:** Invia notifiche per i messaggi ricevuti al di fuori della sessione attiva.

## Table of Contents

- [Whatsapp copy with Redis](#whatsapp-copy-with-redis)
    - [Table of Contents](#table-of-contents)
    - [Installazione](#installazione)
    - [Usage](#usage)

## Installazione

1. **Clone the repository**:
    ```bash
    git clone <https://github.com/MirkoLorenzoLaRocca/whatsapp_Redis.git>
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Installazione librerie**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **impostazione del redis cloud:**

   inserimento del proprio username, host, porta e password nella funzione _start_client( )_:

         redis_client = redis.StrictRedis(
              host='your_host',
              port= 'your_port',
              username='your_username',
              password='your_password',
              decode_responses=True,
              ssl=False
          )


2. **Run the main script to start the application:**
    ```bash
    python main.py
    ```
