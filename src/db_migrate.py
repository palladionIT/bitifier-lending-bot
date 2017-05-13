from playhouse.migrate import *
from .databaseconnector import DatabaseConnector

def migrate_v1(db):
    migrator = SqliteMigrator(db)

    table_name = 'ExchangeTrades'

    # amount_src = DecimalField(max_digits=15, decimal_places=8)
    amount_trg = DecimalField(max_digits=15, decimal_places=8, null=True)
    extrema_time = IntegerField(null=True)
    min_sell_margin = DecimalField(max_digits=15, decimal_places=8, null=True)

    migrate(
        migrator.rename_column(table_name, 'amount_src', 'amount_src'),

        migrator.add_column(table_name, 'amount_trg', amount_trg),
        migrator.add_column(table_name, 'extrema_time', extrema_time),
        migrator.add_column(table_name, 'min_sell_margin', min_sell_margin)
    )

def migrate_v2(db):
    migrator = SqliteMigrator(db)

    table_name = 'ExchangeTrades'

    migrate(
        migrator.rename_column(table_name, 'amount_trg', 'rate')
    )