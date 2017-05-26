import sys, getopt

from src.bitifier import Bitifier

def main(argv):
    # Start all modules and servers
    print('Initializing...')

    accounts = []

    try:
        opts, args = getopt.getopt(argv, 'ha:', ['accounts='])
    except getopt.GetoptError:
        print('usage: __init__.py -a <comma_seperated_accounts>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('usage: __init__.py -a <comma_seperated_accounts>')
            sys.exit()
        elif opt in ('-a', '--btc_usr'):
            accounts = arg.split(',')

    bot = Bitifier(accounts)

if __name__ == '__main__':
    main(sys.argv[1:])
