'''Main python files that executes the script for the password manager.
Parses arguments provided via command line.
'''

import argparse
import getpass
import os
from dotenv import load_dotenv
from random import random, choice

from crypto_handler import *
import db_utils

load_dotenv()

password = getpass.getpass("Enter your master password: ")

salt = os.getenv("MASTER_SALT")
stored_hash = os.getenv("MASTER_PASSWORD")
if not salt or not stored_hash:
    raise EnvironmentError("MASTER_SALT or MASTER_PASSWORD not set in environment.")

combined = (password + salt).encode()
password_hash = sha256(combined).hexdigest()

if password_hash != os.getenv("MASTER_PASSWORD"):
    raise Exception("Incorrect password.")

if __name__ == "__main__":
    # create database if it doesn't already exist
    db_utils.initialize_db()
    # parser to go through options for generation or retrieval
    parser = argparse.ArgumentParser(
        prog="Password Manager",
        description="Creates and retrieves passwords."
        )
    group = parser.add_mutually_exclusive_group()
    # add arguments
    parser.add_argument(
        "accountname",
        help="The account to generate/retrieve password for.",
        )
    group.add_argument(
        "-g", "--generate",
        action="store_true",
        help="Generate and store a new password for the given account"
    )
    group.add_argument(
        "-r", "--retrieve",
        action="store_true",
        help="Retrieve the randomly generated portion or \'pepper\' of the password."
    )
    group.add_argument(
        "-f", "--forgot",
        action="store_true",
        help="Flag for when a password is forgotten."
    )
    group.add_argument(
        "-d", "--delete",
        action="store_true",
        help="Delete a password."
    )

    # attached to accountname = '*'
    parser.add_argument(
        "--startswith",
        nargs='?',
        default='',
        help="Optional arg for listing all accounts that start with the given str"
    )

    # TODO: implement argument handling
    args = parser.parse_args()

    # Default to retrieve if no flags are specified
    if not args.accountname == '*' and not args.generate and not args.retrieve and not args.forgot and not args.delete:
        args.retrieve = True

    # Perform behavior
    if args.accountname == '*':
        # list all account names
        for name in db_utils.get_accounts(args.startswith):
          print(name)
    elif args.generate:
        # randomly generate bit offset
        offset = int(round(245*random()))
        pepper_hash = hash(args.accountname)
        pass_hash = hash(password)
        db_utils.insert_password(
            args.accountname,
            xor(pepper_hash, pass_hash, offset),
            choice((os.getenv("HINT1"), os.getenv("HINT2"))),
            offset
        )
        query = db_utils.get_password(args.accountname)
        print(args.accountname, query[0][-6:], query[1])
    elif args.retrieve:
        query = db_utils.get_password(args.accountname)
        print(args.accountname, query[0][-6:], query[1])
    elif args.forgot:
        answer = input("Would you like to generate a new password? y/n\n")
        if answer == 'y':
            offset = int(round(245*random()))
            pepper_hash = hash(args.accountname)
            pass_hash = hash(password)
            db_utils.update_password(
                args.accountname,
                xor(pepper_hash, pass_hash, offset),
                choice((os.getenv("HINT1"), os.getenv("HINT2")))
            )
            print("Updated. Please log in to see new password.")
        else:
            print("Input not \'y\'. Exiting.")
    elif args.delete:
        db_utils.delete_account(args.accountname)
    else:
        raise Exception("Something went wrong.")
