import redis
import time
import datetime
import os

def start_client():
    """_summary_
    Returns:
        object redis
    """
    redis_client = redis.StrictRedis(
        host='redis-12921.c135.eu-central-1-1.ec2.redns.redis-cloud.com', 
        port=12921,
        username='marmellata',
        password='c5Mmg!&AmVqg9dvX#9GF',
        decode_responses=True,
        ssl=False
    )
    return redis_client

def login():
    """
    login
    """
    username=str(input('Insert username: ')).lower().strip()
    check=redis_client.get(f'user:name:{username}')
    if username == check:
        psw=str(input('Insert password: ')).strip()
        checkPsw=redis_client.get(f'user:psw:{username}')
        if psw == checkPsw:
            os.system('cls')
            print('log OK')
            time.sleep(1)
            return username
        else:
            os.system('cls')
            print('password is incorrect')
            time.sleep(1)
    else:
        os.system('cls')
        print(f'{username} does not exist')
        time.sleep(1)
        return False
            
def sign_up():
    """
    Registrazione utente con la creazione delle chiavi:
    - user:name:{username} -> nome utente
    - user:psw:{username} -> password utente
    - chat:msgId:{username}-> id per rendere univoci i messaggi inviati
    """
    username=str(input('Insert username: ')).lower().strip()
    if redis_client.get(f'user:name:{username}')!=None:
        os.system('cls')
        print(f'{username} already taken')
        time.sleep(1)
    else:
        psw=str(input('Insert password: '))
        redis_client.set(f'user:name:{username}',username)
        redis_client.set(f'user:psw:{username}',psw)
        #s.add('set', username)
        assegnamento_utente_bit(username)
        print('account cretated')
        time.sleep(1)    

def first_page():
    while True:
        try:
            os.system('cls')
            choice=int(input('-1: Login\n-2: Sign up\n-0: Exit\n'))
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
            print('inserisci correttante')                  
        except Exception as error:
            print(error)
            
def stamp_user():
    cursor=0
    searched_user=str(input('Inserisci il nome da cercare: ')).lower().strip()
    os.system('cls')
    list_of_users=[]
    # funzione per stampare gli user trovati e poi aggiungerne 1 alla propria lista contatti
    cursor, keys = redis_client.scan(cursor=cursor, match=f'user:name:{searched_user}*', count=100)
    if not keys:
        print(f"No users found matching '{searched_user}'.")
        return []
    for key in keys:
        key_parts = key.split(':')
        if len(key_parts) > 2:
            list_of_users.append(key_parts[2])
        
    # Eliminazione Utenti gia presenti nella lista conatti
    user_contacts = redis_client.zrange(f'user:contacts:{username}', 0, -1)
    unique_elements = [user for user in list_of_users if user not in user_contacts and user != username]
    list_of_users=[]
    if len(unique_elements)>0:
        for index, user in enumerate(unique_elements, 1):
            print(f'-{index}: {user}')
        print('-0: Exit')
        user_contacts=[]
        return unique_elements
    else:
        user_contacts=[]
        return []

def add_contacts():
    list_of_user=stamp_user()
    # Aggiunta di un user alla lista contatti
    if len(list_of_user)!=0:
        selected_user=int(input('Quale user vuoi selezionare: '))-1
        if selected_user!=-1:
            redis_client.zadd(f'user:contacts:{username}',{list_of_user[selected_user]:0})
            redis_client.zadd(f'user:contacts:{list_of_user[selected_user]}',{username:0})
        else:
            print('Exit')
    else:
        time.sleep(1)

def delete_user_form_contacts(contact_choice):
    os.system('cls')
    confirm=int(input('Se elimini il contatto verranno cancellati anche i messaggi\n-1: continua\n-0: Exit\n'))
    match confirm:
        case 1:
            contacts1 = f'user:contacts:{username}'
            contacts2 = f'user:contacts:{list_of_contacts[contact_choice]}'
            
            chat1 = f'chat:{username}:{list_of_contacts[contact_choice]}'
            chat2 = f'chat:{list_of_contacts[contact_choice]}:{username}'
            
            if redis_client.zrem(contacts1, list_of_contacts[contact_choice]) and redis_client.zrem(contacts2, username):
                print('Eliminazione dei contatti riuscita.')
            if redis_client.delete(chat1) and redis_client.delete(chat2):
                print('Eliminazione delle chat riuscita.')
        case 0:
            print('Operazione annullata.')
        case _:
            raise TypeError("Input non valido.")

def chatChoice_page(contact_choice, contacts):
    # Il fatto del -1 è perchè a schermo viene stampato con un +1 per una questione estetica   
    if contact_choice!=-1:
        print(redis_client.getbit('non_disturbare', redis_client.hget('user:bit', list_of_contacts[contact_choice])))
        print(type(redis_client.getbit('non_disturbare', redis_client.hget('user:bit', list_of_contacts[contact_choice]))))
        while True:
            os.system('cls')
            chat_choice=int(input(f'<{contacts[contact_choice]}>\n-1: Chat\n-2: Chat a tempo\n-3: Cancella Contatto\n-0: Exit\n'))
            os.system('cls')
            match chat_choice:
                case 1:
                    while True:
                        #stampa dei messaggi precedenti della chat

                        if redis_client.exists(f'chat:{username}:{contacts[contact_choice]}'):
                            cursor = 0
                            chat_list = redis_client.zscan(cursor = cursor, name=f'chat:{username}:{contacts[contact_choice]}')
                            chat_list = chat_list[1]
                            print(chat_list)
                            for chat in chat_list:
                                chat = chat[0].split(':')
                                print(f'{chat[1]}-{chat[2]}')

                        #  manca la visualizzazione dei messagi precedenti e la live chat
                        msg=str(input('   '*50+'Type: QuitChat\nScrivi: '))
                        if msg !='QuitChat':
                            timestamp = int(time.time() * 1000)
                            msg_id=redis_client.get(f'chat:msgId:{username}')
                            # chat:<mittente>:<destinatario>->zset member= <timestamp>:msf score=timestamp
                            # from timestamp int to date format -> datetime.datetime.fromtimestamp(timestamp_s).strftime('%d-%m-%Y %H:%M')
                            redis_client.zadd(f'chat:{username}:{contacts[contact_choice]}',{f'{timestamp}:inviato>:{msg}':timestamp})
                            redis_client.zadd(f'chat:{contacts[contact_choice]}:{username}', {f'{timestamp}:ricevuto<:{msg}':timestamp})
                        elif msg !='QuitChat' or redis_client.getbit('user:dnd',redis_client.hget('user:bit', list_of_contacts[contact_choice]))==1:
                            print("Errore, l'utente selezionato è in modalità non disturbare. Non è pertanto raggiungibile fino a quando la modalità non disturbare sarà disattivata")
                            time.sleep(3)
                            break
                        else:
                            break
                case 2:
                    # Chat a tempo
                    pass
                case 3:
                    delete_user_form_contacts(contact_choice)
                    break
                case 0:
                    break
    
def stamp_contacts():
    # Stampa di tutti i contatti in ordine di Score (il timeStamp dell'ultimo messaggio)
    contacts=redis_client.zrangebyscore(f'user:contacts:{username}','-inf', '+inf')

    if len(contacts)!=0:
        for index, contact in enumerate(contacts):
            print(f'-{index+1}: {contact}')
        print('-0: Exit\n')
        contact_choice=int(input('Seleziona un contatto: '))
        contact_choice -= 1
        chatChoice_page(contact_choice, contacts)
    else:
        os.system('cls')
        print('fatti degli amici')
        time.sleep(0.5)  

def do_not_disturb(user, choice):
    bit = redis_client.hget('user:bit', user)
    if choice==1 and redis_client.getbit('user:dnd', bit)!=0:
        redis_client.setbit('user:dnd', bit, 0)
    elif choice==2 and redis_client.getbit('user:dnd', bit)!=1:
        redis_client.setbit('user:dnd', bit, 1)

def assegnamento_utente_bit(username):
    bit = redis_client.get('user:indice_bitmap')
    redis_client.hset('user:bit', username, bit)
    redis_client.incr('user:indice_bitmap')
            
if __name__=='__main__':
    redis_client=start_client()
    ping_status = redis_client.ping()
        
    print("Ping successful:", ping_status)
    if not redis_client.exists('user:dnd'):
        redis_client.setbit('user:dnd', 0, 0)
    if not redis_client.exists('user:indice_bitmap'):
        redis_client.set('user:indice_bitmap', 0)
    username=first_page()
    if username!=False:
        list_of_contacts=[]
        while True:
            try:
                os.system('cls')
                choice=int(input(f'<{username}>\n-1: Cerca utente\n-2: Visualizza contatti\n-3: Modalità non disturbare\n-0: Esci\n'))
                os.system('cls')
                match choice:
                    case 1:
                        add_contacts()
                    case 2:  
                        stamp_contacts()
                        list_of_contacts=[]            
                    case 3:
                        while True:
                            try:
                                choice_dnd=int(input("-1: Disattiva la modalità non disturbare\n-2: Attiva la modalità non disturbare\n-0: Esci\n"))
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
                    case 0:
                        break
                    case _:
                        raise ValueError
            except ValueError as ve:
                print('Azione impossibile')
            except Exception as error:
                print(error)   
    else:
        print('close')