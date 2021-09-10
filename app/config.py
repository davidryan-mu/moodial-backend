import os, sys, getopt
is_prod = os.environ.get('IS_HEROKU')

MONGO_DBNAME = None
MONGO_URI = None
SECRET_KEY = None
JWT_SECRET_KEY = None

# Use Heroku env vars, else use command line args
if is_prod:
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME')
    MONGO_URI = os.environ.get('MONGO_URI')

    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

else:
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:j:d:u:', ['secret_key=', 'jwt_secret_key=', 'db_name=', 'mongo_uri='])

    except getopt.GetoptError as err:
        print('Error parsing command line agruments:')
        print(err)

    for opt, arg in opts:
        if opt in ['-s', '--secret_key']:
            SECRET_KEY = arg
            
        elif opt in ['-j', '--jwt_secret_key']:
            JWT_SECRET_KEY = arg

        elif opt in ['-d', '--db_name']:
            MONGO_DBNAME = arg

        elif opt in ['-u', '--mongo_uri']:
            MONGO_URI = arg


vars = {
    'secret key': SECRET_KEY,
    'jwt secret key': JWT_SECRET_KEY,
    'database name': MONGO_DBNAME,
    'MongoDB URI': MONGO_URI
}

for key, value in vars.items():
    if value == None:
        print('🤔 Missing ' + key + ' from arguments')
        sys.exit()

DEBUG = True