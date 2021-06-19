import argparse
import sys

from tqdm import tqdm

from msorm import models


def init(*args):
    if len(args) >= 1:
        parser = argparse.ArgumentParser(description='Argparse Test script')

        parser.add_argument("-ip", help="ip address")
        parser.add_argument("-db", help="database name")
        parser.add_argument("-u", help="username")
        parser.add_argument("-p", help="password")
        parser.add_argument("-f", help="file name", default="models.py")
        args_ = parser.parse_args(list(args))
        models.init(args_.ip, args_.db, args_.u, args_.p)
        file_name = args_.f
        ip, database, username, password = args_.ip, args_.db, args_.u, args_.p

    else:
        print("Welcome to msorm database initializer")
        while 1:
            ip = input("Please enter the database ip address: ")
            database = input("Please enter the database name: ")
            username = input("Please enter the username: ")
            password = input("Please enter the password: ")
            file_name = input("Please enter the output file name[Default: models.py]: ")
            file_name = file_name if file_name != "" else "models.py"
            print(
                f"database ip: {ip}\ndatabase name: {database}\n database username: {username}\n password: {password}")
            answer = input("Are all values are valid?[Y/n]: ")
            if answer.lower() == 'n':
                print("Please re-enter required fields!")
                continue
            else:
                break
        models.init(ip, database, username, password)
    intend = "    "
    models_py = \
        f"""from msorm import models
from msorm.models import Field
models.init("{ip}", "{database}", "{username}", "{password}")
"""
    crsr = models.connection.cursor()
    table_names = [x[2] for x in crsr.tables(tableType='TABLE')]
    table_names.remove("sysdiagrams")
    tables = {k: {} for k in table_names}
    table_scores = {}
    for table in tqdm(table_names):
        table_scores[table] = 0
        primarykey = False
        for row in crsr.columns(table=table):
            if row.type_name == "int identity":
                primarykey = True
                type_name = "primaryKey"
            else:
                type_name = row.type_name

            is_nullable = True if row.is_nullable == "YES" else False
            __primaryKey__ = False

            tables[table][row.column_name] = f"Field.{type_name}(null={is_nullable})"
        if not primarykey:
            tables[table]["__primaryKey__"] = __primaryKey__


        for fk in crsr.foreignKeys(table=table):
            table_scores[table]+=1
            pk_column_name = fk.pkcolumn_name
            fk_table_name = fk.fktable_name
            tables[fk_table_name][pk_column_name] = f"Field.foreignKey(model={fk.pktable_name},name='{pk_column_name}')"
    table_scores = [[k,v] for k,v in table_scores.items()]
    table_scores.sort(key=lambda x: x[1],reverse=True)
    table_scores = [t[0] for t in table_scores]
    tables = {k:tables[k] for k in table_scores}

    for last_table, fields in tables.items():
        models_py += f"\n\nclass {last_table}(models.Model):"
        for field, val in fields.items():
            if field == "__primaryKey__" and val == False:
                models_py += f"\n{intend}{field} = False"
                continue
            models_py += f"\n{intend}{field} = {val}"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(models_py)
    # with open("secrets2.json", "w") as fi:
    #     json.dump(tables,fi,indent=2)


processes = {"init": init}
if __name__ == '__main__':
    args = sys.argv[1:]
    processes.get(args.pop(0))(*args)
