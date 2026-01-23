import argparse
import datetime
from run_auction import run_auction
from user_management import list_users, add_user, delete_user

def users(args):
    if args.command == 'list':
        list_users(args.username, args.card_id)
    elif args.command == 'add':
        add_user(args.username, args.card_id)
    elif args.command == 'delete':
        delete_user(args.username)

def auction(args):
    run_auction(args.auction_name, args.start_price, args.end_time, args.min_difference)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='server.py',
        description='Server for running auctions and managing user database',
    )

    subparsers = parser.add_subparsers(required=True)

    userManagement = subparsers.add_parser('users')
    userManagement.set_defaults(func=users)

    userManagement.add_argument('command', choices=['add', 'list', 'delete'])
    userManagement.add_argument('--username', '-n', default=None, type=str)
    userManagement.add_argument('--card_id', '-c', default=None, type=int)

    runAuction = subparsers.add_parser('auction')
    runAuction.set_defaults(func=auction)

    runAuction.add_argument('--auction_name', '-n', default=None, type=str)
    runAuction.add_argument('--start_price', '-p', default=None, type=float)
    runAuction.add_argument('--end_time', '-t', default=None, type=int)#lambda d: datetime.datetime.strptime(d, '%Y/%m/%d %I:%M'))
    runAuction.add_argument('--min_difference', '-d', default=None, type=float)

    args = parser.parse_args()
    args.func(args)
