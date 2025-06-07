'''Methods to interact with the sqlite database used for the passwords.
'''

import sqlite3

def initialize_db(db_path="passwords.db"):
    '''Creates a new database for the passwords if one does not already exist.
    
    Fields:
    - id: id of the record
    - account_name: name of the online account that this record corresponds to
    - pepper: the "complex portion" or generated portion of the password
    - stem_password: hint for what the stem of the whole password is
    - bit_offset: offset of the hash of the account_name to generate the pepper with
    - created_at: when the current password was created
    '''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            account_name TEXT NOT NULL UNIQUE,
            pepper BLOB NOT NULL,
            stem_password TEXT,
            bit_offset INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_password(account_name, pepper, stem_password, bit_offset, db_path="passwords.db"):
    '''Inserts a new password into the database.'''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO passwords (account_name, pepper, stem_password, bit_offset)
        VALUES (?, ?, ?, ?)
    ''', (account_name, pepper, stem_password, bit_offset))
    conn.commit()
    conn.close()

def update_password(account_name, new_pepper, new_stem, db_path="passwords.db"):
    '''Updates the password for a given record.'''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE passwords
        SET pepper = ?, stem_password = ?, created_at = CURRENT_TIMESTAMP
        WHERE account_name = ?
    ''', (new_pepper, new_stem, account_name))

    conn.commit()
    conn.close()

def get_password(account_name, db_path="passwords.db"):
    '''Retrieves password from a database.

       ## Args:
       - account_name: str - the account that you want to obtain the pw for
       - db_path: str - defaults to passwords.db. The database path with your pwds
       
       ## Returns:
       - tuple(str, str): First str is the hex representation of the "pepper" or tail
                          of your pw. The second is the stem_password hint.
    '''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT pepper, stem_password FROM passwords
        WHERE account_name = ?
    ''', (account_name,))

    result = cursor.fetchone()
    conn.close()

    return (result[0].hex() if result else "Not Found", result[1])

def delete_account(account_name: str, db_path: str="passwords.db"):
    '''Deletes a record from the database where account_name matches the given argument.'''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM passwords WHERE account_name = ?", (account_name,))
    conn.commit()

    if cursor.rowcount == 0:
        raise ValueError(f"No record found with account_name = '{account_name}'")

    print(f"Deleted account '{account_name}' from database.")
    conn.close()

def get_accounts(n: str, db_path: str="passwords.db"):
    '''Lists all account names registered in the database at db_path'''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if n:
        cursor.execute(
            'SELECT account_name FROM passwords WHERE account_name LIKE ?',
            (n + '%',)
        )
    else:
        cursor.execute(
            'SELECT account_name FROM passwords'
        )
    
    result = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return result

