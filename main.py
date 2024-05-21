import redis
import time
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
            return 'no'
    else:
        os.system('cls')
        print(f'{username} does not exist')
        time.sleep(1)
        return 'no'
    
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
        redis_client.set(f'chat:msgId:{username}',0)
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
                    if login() !='no':
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
    cursor = 0
    searched_user=str(input('Inserisci il nome da cercare: '))
    os.system('cls')
    cursor, keys = redis_client.scan(cursor=cursor, match=f'user:name:{searched_user}*', count=10)
    list_of_users=[]
    # funzione per stampare gli user trovati e poi aggiungerne 1 alla propria lista contatti
    for key in keys:
        key=key.split(':')
        list_of_users.append(f'{key[2]}')
    # Eliminazione Utenti gia presenti nella lista conatti
    user_contacts = redis_client.zrange(f'user:contacts:{username}', 0, -1)
    unique_elements = [user for user in list_of_users if user not in user_contacts and user != username]
    #
    if len(unique_elements)>0:
        for index, user in enumerate(unique_elements, 1):
            print(f'-{index}: {user}')
        print('-0: Exit')
        return unique_elements
    else:
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
        print('No user found\nComeback to menu')
        time.sleep(1)

        
if __name__=='__main__':
    redis_client=start_client()
    ping_status = redis_client.ping()
    print("Ping successful:", ping_status)
    username=first_page()
    if username!=False:
        list_of_contacts=[]
        while True:
            os.system('cls')
            try:
                choice=int(input('-1: Cerca utente\n-2: Visualizza contatti\n-0: Esci\n'))
                os.system('cls')
                if choice==1:
                    add_contacts()
                elif choice==2:
                    # Stampa di tutti i contatti in ordine di Score (il timeStamp dell'ultimo messaggio)
                    contacts=redis_client.zrangebyscore(f'user:contacts:{username}','-inf', '+inf')
                    for contact in contacts:
                        list_of_contacts.append(f'{contact}')
                    if len(list_of_contacts)>0:
                        for index in range(len(list_of_contacts)):
                            print(f'-{index+1}: {list_of_contacts[index]}')
                        print('-0: Exit\n'+'-'*20)   
                        contact_choice=int(input('Seleziona un contatto: '))-1 # Il fatto del -1 è perchè a schermo viene stampato con un +1 per una questione estetica
                        print('-'*20)
                        
                        if contact_choice!=-1:
                            while True:  
                                os.system('cls')
                                chat_choice=int(input(f'-1: Chat\n-2: Chat a tempo\n-3: Cancella Contatto\n-0: Exit\n'))
                                os.system('cls')
                                if chat_choice==1:
                                    while True:
                                        # Fase di Chat manca la visualizzazione dei messagi precedenti
                                        msg=str(input('     '*50+'Type: QuitChat\nScrivi: '))
                                        if msg !='QuitChat':
                                            timestamp = int(time.time() * 1000)
                                            msg_id=redis_client.get(f'chat:msgId:{username}')
                                            redis_client.zadd(f'chat:{username}:{list_of_contacts[contact_choice]}',{f'{msg_id}:{msg}':timestamp}) #chive il time stamp del messaggio
                                            redis_client.zadd(f'user:contacts:{list_of_contacts[contact_choice]}',{username: timestamp})
                                            redis_client.incr(f'chat:msgId:{username}')
                                        else:
                                            break
                                elif chat_choice==2:
                                    pass
                                elif chat_choice==3:
                                    os.system('cls')
                                    confirm=int(input('Se elimini il contatto verranno cancellati anche i messaggi\n-1: continua\n-0: Exit'))
                                    if confirm==1:
                                        redis_client.zrem(f'user:contacts:{username}',f'{list_of_contacts[contact_choice]}' )
                                        redis_client.zrem(f'user:contacts:{list_of_contacts[contact_choice]}',{username})
                                        redis_client.delete(f'chat:{username}:{list_of_contacts[contact_choice]}')
                                        redis_client.delete(f'chat:{list_of_contacts[contact_choice]}:{username}')

                                elif chat_choice==0:
                                    break
                        else:
                            print('-'*20)
                            print('fatti degli amici')  
                elif choice==0:
                    break
                else:
                    raise ValueError
            except ValueError as ve:
                print('Azione impossibile')
            except Exception as error:
                print(error)   
    else:
        print('close')