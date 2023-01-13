from typing import Dict, List, Tuple
from loguru import logger


def insert(table: str, column_values: Dict, cursor, conn):
    logger.info(f'inserting values into {table}: {column_values}')
    columns = ', '.join(column_values.keys())
    values = tuple(column_values.values())

    place = ['%s' for x in column_values.values()]

    placeholders = ", ".join(place)
    logger.info(f'{columns} {values} {place} {placeholders}')
    cursor.execute(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)


def fetchall(table: str, columns: List[str], cursor, conn) -> List[Tuple]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


# def delete(table: str, row_id: int,cursor, conn) -> None:
#     row_id = int(row_id)
#     cursor.execute(f"delete from {table} where id={row_id}")
