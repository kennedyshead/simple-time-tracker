import sqlite3

from tools.files import file_path

db = sqlite3.connect(file_path.joinpath('storage.db'))


def run_query(**kwargs):
    cursor = db.cursor()
    cursor.execute(kwargs['query'], kwargs.get('params', {}))
    db.commit()
    cursor.close()
