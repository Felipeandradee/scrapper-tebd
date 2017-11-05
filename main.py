import datetime

import populate
from models import db


populate.create_tables()

print(f'Script started at: {datetime.datetime.now()}')
with db.atomic() as transaction:

    try:
        populate.congress()
        populate.paper()
        populate.update_paper()

    except Exception as e:
        db.rollback()
        print('Error: ', e)

print(f'Script finished at: {datetime.datetime.now()}')
