from peewee import SqliteDatabase

# 数据库配置，本地版直接用sqlite存本地即可
# database configuration, use sqlite for local version
def config_database(address):
    db = SqliteDatabase(f'{address}.db')
    return db

database = None
