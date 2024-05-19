import redis

def start_client():
    redis_client = redis.StrictRedis(
        host='redis-12921.c135.eu-central-1-1.ec2.redns.redis-cloud.com', 
        port=12921,
        username='marmellata',
        password='c5Mmg!&AmVqg9dvX#9GF',
        ssl=False
    )
    return redis_client
def firts_step(redis_client):
    while True:
        try:
            choice=int(input('-1: Login\n-2: Sign in\n-3: Exit\n'))
            if choice==1:
                username=str(input('Insert username: ')).lower()
                check=redis_client.get(f'user:name:{username}').decode('utf-8') #con i get di redis vengono salvati come byte string e hanno bisogno di un decode
                if username == check:
                    psw=str(input('Insert password: '))
                    checkPsw=redis_client.get(f'user:psw:{username}').decode('utf-8')
                    if psw == checkPsw:
                        print('log OK')
                        return True
                        
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
                    print('account cretated')
            elif choice == 3:
                return False
            else:
                print('azione impossibile')
        except TypeError as typeError:       
            print('inserisci correttante')                  
        except Exception as error:
            print(error)
if __name__=='__main__':
    redis_client=start_client()
    ping_status = redis_client.ping()
    print("Ping successful:", ping_status)
    first=firts_step(redis_client)
    if first==True:
        cursor = 0
        while True:
            try:
                choice=int(input('-1: Cerca utente\n-2: Visualizza contatti\n-3 esci\n'))
                if choice==1:
                    searched_user=input('Inserisci il nome da cercare: ')
                    cursor, keys = redis_client.scan(cursor=cursor, match=f'user:name:{searched_user}*', count=10)
                    for key in keys:
                        key=key.decode('utf-8').split(':')
                        print(f'-Username: {key[2]}')
                    
            except Exception as error:
                print(error)   
    else:
        print('close')