import redis
import time
import datetime
import os
from colorama import Fore, Back, init, Style

init(autoreset=True)


def start_client():
    """
    avvio e configurazione del client redis.
    :return: Redis client object
    """
    redis_client = redis.StrictRedis(
        host='redis-12921.c135.eu-central-1-1.ec2.redns.redis-cloud.com',
        port=12921,
        username='marmellata',
        password='c5Mmg!&AmVqg9dvX#9GF',
        decode_responses=True,
        ssl=False
    )
    if not redis_client.exists('user:dnd'):
        redis_client.setbit('user:dnd', 0, 0)
    if not redis_client.exists('user:indice_bitmap'):
        redis_client.set('user:indice_bitmap', 0)
    return redis_client


def login():
    """
    login
    """
    username = str(input('Inserisci username: ')).lower().strip()
    check = redis_client.get(f'user:name:{username}')
    if username == check:
        psw = str(input('Inserisci password: ')).strip()
        check_psw = redis_client.get(f'user:psw:{username}')
        if psw == check_psw:
            os.system('cls')
            print(f'Benvenuto/a, {username}!')
            time.sleep(1)
            return username
        else:
            os.system('cls')
            print('La password inserita non è corretta')
            time.sleep(1)
            return menu_accesso()
    else:
        os.system('cls')
        print(f'account {username} non trovato')
        time.sleep(1)
        return menu_accesso()


def sign_up():
    """
    Registrazione utente con la creazione delle chiavi:
    - user:name:{username} -> nome utente
    - user:psw:{username} -> password utente
    - chat:msgId:{username}-> id per rendere univoci i messaggi inviati
    """
    username = str(input('Inserisci username: ')).lower().strip()
    if redis_client.get(f'user:name:{username}') != None:
        os.system('cls')
        print(f'Username {username} non è disponibile')
        time.sleep(1)
    else:
        psw = str(input('Inserisci password: '))
        redis_client.set(f'user:name:{username}', username)
        redis_client.set(f'user:psw:{username}', psw)
        # s.add('set', username)
        assegnamento_utente_bit(username)
        print('Account creato correttamente')
        time.sleep(1)


def menu_accesso():
    while True:
        try:
            os.system('cls')
            choice = int(input(Fore.GREEN + '-1: Login\n-2: Sign up\n' + Fore.RED +
                               '-0: Esci\n' + Style.RESET_ALL))
            os.system('cls')
            match choice:
                case 1:
                    return login()
                case 2:
                    sign_up()
                case 0:
                    return False
                case _:
                    raise TypeError

        except TypeError:
            print('scelta non valida')
        except Exception as error:
            print(error)


def cerca_account():
    # ricerca degli utenti nel database di redis e visualizzazione a schermo
    searched_user = str(input('Inserisci il nome da cercare: ')).lower().strip()
    os.system('cls')
    list_of_users = []
    # funzione per stampare gli user trovati e poi aggiungerne 1 alla propria lista contatti
    keys = redis_client.scan(match=f'user:name:{searched_user}*', count=100)
    keys = keys[1]
    if not keys:
        print(f"Nessun utente '{searched_user}' trovato.")
        return []
    for key in keys:
        key_parts = key.split(':')
        list_of_users.append(key_parts[2])

    # Eliminazione Utenti gia presenti nella lista conatti
    user_contacts = redis_client.zrange(f'user:contacts:{username}', 0, -1)
    unique_elements = [user for user in list_of_users if user not in user_contacts and user != username]
    list_of_users = []
    if len(unique_elements) > 0:
        for index, user in enumerate(unique_elements, 1):
            print(f'-{index}: {user}')
        print(Fore.RED + '-0: Indietro' + Style.RESET_ALL)
        user_contacts = []
        return unique_elements
    else:
        user_contacts = []
        return []


def aggiungi_contatto():
    list_of_user = cerca_account()
    # Aggiunta di un user alla lista contatti
    if len(list_of_user) != 0:
        selected_user = int(input('Inserisci indice da aggiungere ai contatti: ')) - 1
        if selected_user != -1:
            redis_client.zadd(f'user:contacts:{username}', {list_of_user[selected_user]: 0})
            redis_client.zadd(f'user:contacts:{list_of_user[selected_user]}', {username: 0})
        else:
            print('Exit')
    else:
        time.sleep(1)


def elimina_contatto(contact_choice, contacts):
    os.system('cls')
    confirm = int(input('Se elimini il contatto verranno cancellati anche i messaggi\n' + Fore.RED +
                        '-1: continua\n' + Style.RESET_ALL +
                        '-0: Indietro\n'))
    match confirm:
        case 1:
            # salvo username e il contatto da eliminare in due variabili
            user_attivo = f'user:contacts:{username}'
            contatto_da_eliminare = f'user:contacts:{contacts[contact_choice]}'
            chat = f'chat:{":".join(sorted([username, contacts[contact_choice]]))}'

            if (redis_client.zrem(user_attivo, contacts[contact_choice])
                    and redis_client.zrem(contatto_da_eliminare, username)):
                print(Fore.GREEN + 'Eliminazione del contatto riuscita.')
            else:
                print(Fore.RED + "Errore nell'eliminazione del contatto")
            if redis_client.delete(chat):
                print(Fore.GREEN + 'Eliminazione della chat riuscita.')
            else:
                print(Fore.RED + "Errore nell'eliminazione della chat" + Style.RESET_ALL)
        case 0:
            print('Operazione annullata.')
        case _:
            raise TypeError("Input non valido.")


def convert_date(date):
    return datetime.datetime.fromtimestamp(int(date) / 10000).strftime('%d-%m-%Y %H:%M')


def crea_callback(username):
    def callback(message):
        data = message['data'].split(':')
        formatted_date = convert_date(data[0])
        check_username = data[1]
        msg = data[2]

        if check_username == username:
            formattato = (Fore.LIGHTGREEN_EX + '     ' * 8 + f'io>{msg}\n' + '     ' * 8 +
                          Style.RESET_ALL + f'{formatted_date}')
        else:
            formattato = f'{check_username}<{msg}\n  {formatted_date}'
        print(formattato)

    return callback


def visualizza_chat(contacts, contact_choice):
    key = [username, contacts[contact_choice]]
    key.sort()
    key = f'chat:{key[0]}:{key[1]}'
    # controllo se la chat esiste e stampa dei messaggi precedenti
    if redis_client.exists(key):
        chat_list = redis_client.zscan(name=key)
        chat_list = chat_list[1]
        for chat in chat_list:
            chat = chat[0].split(':')
            formatted_date = convert_date(chat[0])
            if chat[1] == username:
                print(
                    Fore.LIGHTGREEN_EX + '     ' * 8 + f'io>{chat[2]}\n' + '     ' * 8
                    +Style.RESET_ALL + f'  {formatted_date}')
            else:
                print(f'{contacts[contact_choice]}<{chat[2]}\n  {formatted_date}' + Style.RESET_ALL)

    # creazione chat live
    pubsub = redis_client.pubsub()
    pubsub.psubscribe(**{f'{key}': crea_callback(username)})
    thread = pubsub.run_in_thread(sleep_time=0.01)

    while True:
        # controllo se l'utente è in modalità non disturbare
        if redis_client.getbit('user:dnd',
                               redis_client.hget('user:bit', contacts[contact_choice])) == 1:
            print("Errore, l'utente selezionato è in modalità non disturbare."
                  " Non è pertanto raggiungibile fino a quando la modalità non disturbare "
                  "sarà disattivata")
            time.sleep(2)
            break

        # richiesta del messaggio da scrivere
        msg = str(input(Style.DIM + 'Scrivi' + Fore.RED + '(QuitChat per uscire): ' + Style.RESET_ALL))
        print("\033[A                             \033[A")

        if msg != 'QuitChat':

            timestamp = int(time.time() * 10000)
            # aggiunta messaggio db
            redis_client.zadd(key, {f'{timestamp}:{username}:{msg}': timestamp})
            redis_client.publish(f'{key}', f'{timestamp}:{username}:{msg}')
        else:
            break
    thread.stop()


def chatChoice_page(contact_choice, contacts):
    # Il fatto del -1 è perchè a schermo viene stampato con un +1 per una questione estetica   
    if contact_choice != -1:
        while True:
            os.system('cls')
            chat_choice = int(input(
                f'< {contacts[contact_choice].upper()} >\n'
                f'-1: Chat\n'
                f'-2: Chat a tempo\n'
                f'-3: Cancella Contatto\n' + Fore.RED +
                f'-0: Indietro\n' + Style.RESET_ALL))
            os.system('cls')
            match chat_choice:
                case 1:
                    visualizza_chat(contacts, contact_choice)
                case 2:
                    # Chat a tempo
                    pass
                case 3:
                    elimina_contatto(contact_choice, contacts)
                    break
                case 0:
                    break


def visualizza_contatti():
    # Stampa di tutti i contatti in ordine di Score (il timeStamp dell'ultimo messaggio)
    contacts = redis_client.zrangebyscore(f'user:contacts:{username}', '-inf', '+inf')

    if len(contacts) != 0:
        for index, contact in enumerate(contacts):
            print(f'-{index + 1}: {contact}')
        print('-0: Exit\n')
        contact_choice = int(input('Seleziona un contatto: '))
        contact_choice -= 1
        chatChoice_page(contact_choice, contacts)
    else:
        os.system('cls')
        print('fatti degli amici')
        time.sleep(0.5)


def do_not_disturb(user, choice):
    bit = redis_client.hget('user:bit', user)
    if choice == 1 and redis_client.getbit('user:dnd', bit) != 0:
        redis_client.setbit('user:dnd', bit, 0)
    elif choice == 2 and redis_client.getbit('user:dnd', bit) != 1:
        redis_client.setbit('user:dnd', bit, 1)


def assegnamento_utente_bit(username):
    bit = redis_client.get('user:indice_bitmap')
    redis_client.hset('user:bit', username, bit)
    redis_client.incr('user:indice_bitmap')


def menu_non_disturbare():
    while True:
        try:
            choice_dnd = int(
                input("-1: Disattiva la modalità non disturbare\n-2: Attiva la modalità non disturbare\n-0: Esci\n"))
            match choice_dnd:
                case 1:
                    do_not_disturb(username, choice_dnd)
                    print('Modalità non disturbare disattivata con successo')
                case 2:
                    do_not_disturb(username, choice_dnd)
                    print('Modalità non disturbare attivata con successo')
                case 0:
                    break
                case _:
                    print('Scelta non disponibile')
            break
        except ValueError as ve:
            print('Inserire un numero')
        except Exception as error:
            print(error)


def menu_principale(user):
    while True:
        try:
            os.system('cls')
            choice = int(input(
                f'< {user.upper()} >'
                f'\n-1: Cerca utente\n'
                f'-2: Visualizza contatti\n'
                f'-3: Modalità non disturbare\n' + Fore.RED +
                f'-0: Esci\n' + Style.RESET_ALL))
            os.system('cls')

            match choice:
                case 1:
                    aggiungi_contatto()
                case 2:
                    visualizza_contatti()
                case 3:
                    menu_non_disturbare()
                case 0:
                    return menu_accesso()
                case _:
                    raise ValueError
        except ValueError as ve:
            print('Azione impossibile')
        except Exception as error:
            print(error)
            break


if __name__ == '__main__':
    redis_client = start_client()
    ping_status = redis_client.ping()

    print("Ping successful:", ping_status)
    username = menu_accesso()
    if username != False:
        list_of_contacts = []
        menu_principale(username)
    else:
        print('close')
