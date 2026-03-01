from models import db
from sqlalchemy import text


class CommonService:
    @staticmethod
    def get_option(table_name, column_name):
        sql = text(f'SELECT DISTINCT `{column_name}` FROM `{table_name}` WHERE `{column_name}` IS NOT NULL AND `{column_name}` != ""')
        result = db.session.execute(sql)
        return [row[0] for row in result]

    @staticmethod
    def group(table_name, column_name):
        sql = text(f'SELECT `{column_name}` as name, COUNT(*) as value FROM `{table_name}` GROUP BY `{column_name}`')
        result = db.session.execute(sql)
        return [dict(row._mapping) for row in result]

    @staticmethod
    def value(table_name, x_column, y_column):
        sql = text(f'SELECT `{x_column}` as name, SUM(`{y_column}`) as value FROM `{table_name}` GROUP BY `{x_column}`')
        result = db.session.execute(sql)
        return [dict(row._mapping) for row in result]

    @staticmethod
    def cal(table_name, column_name):
        sql = text(f'SELECT SUM(`{column_name}`) as total, AVG(`{column_name}`) as average FROM `{table_name}`')
        result = db.session.execute(sql).fetchone()
        return {'total': float(result[0] or 0), 'average': float(result[1] or 0)}
