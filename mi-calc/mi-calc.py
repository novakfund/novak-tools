import sqlite3
import pandas


companyValue = 0  # define initial company value


class DatabaseConnection:
    def __init__(self, host):
        self.connection = None
        self.host = host

    def __enter__(self):
        self.connection = sqlite3.connect(self.host)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb:
            self.connection.close()
        else:
            self.connection.commit()
            self.connection.close()


# import csv into db
def load_database():
    with DatabaseConnection('data.db') as connection:
        df = pandas.read_csv('members.csv', encoding='utf-8')
        df.to_sql('memberdb', connection, if_exists='append', index=False)


load_database()  # comment out after initial load


def update_mi(mi, name):
    with DatabaseConnection('data.db') as connection:
        cursor = connection.cursor()

        cursor.execute('UPDATE memberdb SET mi=? WHERE name=?', (mi, name))


def read_all_database():
    with DatabaseConnection('data.db') as connection:
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM memberdb')
        memberdata = cursor.fetchall()

    for member in memberdata:
        print(member)


with DatabaseConnection('data.db') as connection:
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM memberdb')

    memberdata = cursor.fetchall()


for row in memberdata:
    name = row[0]
    mi = float(row[1])
    investment = float(row[2])

    if mi == 0:
        print(f"detecting {name} as new investor... adjusting {name}'s membership interest.")

        pi_value = investment / companyValue
        mi = ((mi + .75 * pi_value) / (1 + pi_value))

        update_mi(mi, name)

        stoppername = name
        companyValue = companyValue + investment

        print(f"{name}'s membership interest is now {mi}. Proceeding to adjust everyone else's membership interest...")

        update_mi(mi, name)

        with DatabaseConnection('data.db') as connection:
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM memberdb')

            memberdata = cursor.fetchall()

        for x in memberdata:
            name = x[0]
            mi = float(x[1])
            investment = float(x[2])

            if name != stoppername and mi != 0:

                mi = mi / (1 + pi_value)
                update_mi(mi, name)
                print(f"{name}'s membership interest has been adjusted, and it is now {mi}")

            else:
                pass
    else:
        pass


print(f"Printing final member information...")
read_all_database()
