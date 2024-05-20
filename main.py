import redis
import time
def start_client():
    redis_client = redis.StrictRedis(
        host='redis-12921.c135.eu-central-1-1.ec2.redns.redis-cloud.com', 
        port=12921,
        username='marmellata',
        password='c5Mmg!&AmVqg9dvX#9GF',
        decode_responses=True,
        ssl=False
    )
    return redis_client

def firts_step():
    while True:
        try:
            print('-'*20)
            choice=int(input('-1: Login\n-2: Sign in\n-3: Exit\n'))
            print('-'*20)
            if choice==1:
                username=str(input('Insert username: ')).lower()
                check=redis_client.get(f'user:name:{username}')
                if username == check:
                    psw=str(input('Insert password: '))
                    checkPsw=redis_client.get(f'user:psw:{username}')
                    if psw == checkPsw:
                        print('log OK')
                        return username
                    else:
                        print('password NO')
                else:
                    print('user NO')
            elif choice==2:
                username=str(input('Insert username: ')).lower()
                if redis_client.get(f'user:name:{username}')!=None:
                    print('username già preso')
                else:
                    psw=str(input('Insert password: '))
                    redis_client.set(f'user:name:{username}',username)
                    redis_client.set(f'user:psw:{username}',psw)
                    redis_client.set(f'chat:msgId:{username}',0)
                    print('account cretated')
            elif choice == 3:
                return False
            else:
                print('azione impossibile')
        except TypeError as typeError:       
            print('inserisci correttante')                  
        except Exception as error:
            print(error)
            
def add_contacts(list_of_user, keys):
    #funzione per stampare gli user trovati e poi aggiungerne 1 alla propria lista contatti
    for key in keys:
        key=key.split(':')
        list_of_user.append(f'{key[2]}')
    if len(list_of_user)>0:
        for index in range(len(list_of_user)):
            print(f'-{index+1}: {list_of_user[index]}')
        print('-0: Exit')
        selected_user=int(input('Quale user vuoi selezionare: '))-1
        if selected_user!=-1:
            redis_client.zadd(f'user:contacts:{first}',{list_of_user[selected_user]:0})
            redis_client.zadd(f'user:contacts:{list_of_user[selected_user]}',{first:0})
        else:
            print('Exit')
    else:
        print('No user found')
    
if __name__=='__main__':
    redis_client=start_client()
    ping_status = redis_client.ping()
    print("Ping successful:", ping_status)
    first=firts_step()
    if first!=False:
        cursor = 0
        list_of_user=[]
        list_of_contacts=[]
        while True:
            try:
                choice=int(input('-1: Cerca utente\n-2: Visualizza contatti\n-0: Esci\n'))
                if choice==1:
                    searched_user=str(input('Inserisci il nome da cercare: '))
                    cursor, keys = redis_client.scan(cursor=cursor, match=f'user:name:{searched_user}*', count=10)
                    add_contacts(list_of_user, keys)
                    list_of_user=[]
                elif choice==2:
                    # Stampa di tutti i contatti in ordine di Score (il timeStamp dell'ultimo messaggio)
                    contacts=redis_client.zrangebyscore(f'user:contacts:{first}','-inf', '+inf')
                    print('-'*20)
                    for contact in contacts:
                        list_of_contacts.append(f'{contact}')
                    if len(list_of_contacts)>0:
                        for index in range(len(list_of_contacts)):
                            print(f'-{index+1}: {list_of_contacts[index]}')
                        print('-0: Exit')   
                        contact_choice=int(input('Seleziona un contatto: '))-1 # Il fatto del -1 è perchè a schermo viene stampato con un +1 per una questione estetica
                        print('-'*20)
                        
                        if contact_choice!=-1:
                            while True:  
                                chat_choice=int(input(f'-1: Chat\n-2: Chat a tempo\n-3: Cancella Contatto\n-0: Exit\n'))
                                if chat_choice==1:
                                    while True:
                                        # Fase di Chat manca la visualizzazione dei messagi precedenti
                                        msg=str(input('     '*50+'Type: QuitChat\nScrivi: '))
                                        if msg !='QuitChat':
                                            timestamp = int(time.time() * 1000)
                                            msg_id=redis_client.get(f'chat:msgId:{first}')
                                            redis_client.zadd(f'chat:{first}:{list_of_contacts[contact_choice]}',{f'{msg_id}:{msg}':timestamp}) #chive il time stamp del messaggio
                                            redis_client.zadd(f'user:contacts:{list_of_contacts[contact_choice]}',{first: timestamp})
                                            redis_client.incr(f'chat:msgId:{first}')
                                        else:
                                            break
                                elif chat_choice==2:
                                    pass
                                elif chat_choice==3:
                                    pass
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