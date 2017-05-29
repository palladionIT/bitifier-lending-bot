import sys, getopt

from src.bitifier import Bitifier

def main(argv):
    # Start all modules and servers
    print('Initializing...')

    accounts = []
    functionality = {'trading': False,
                 'funding': False}

    try:
        opts, args = getopt.getopt(argv, 'ha:tf', ['accounts='])
    except getopt.GetoptError:
        print('usage: __init__.py -a <comma_seperated_accounts> [-t, -f]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('usage: __init__.py -a <comma_seperated_accounts> [-t, -f]')
            sys.exit()
        elif opt in ('-a', '--btc_usr'):
            accounts = arg.split(',')
        elif opt in ('-t'):
            functionality['trading'] = True
        elif opt in ('-f'):
            functionality['funding'] = True

    bot = Bitifier(accounts, functionality)

if __name__ == '__main__':
    main(sys.argv[1:])
