'''Short term pipeline'''

from extract_short import extract
from transform_short import get_connection
from load_short import upsert_plants


def lambda_handler(event, context):
    '''Lambda handler'''
    try:
        data = extract()
    except Exception as err:
        return {"statusCode": 400, 'body': f"Failure. Could not extract data, {err}"}
    with get_connection() as conn:
        try:
            conn_cursor = conn.cursor()
            upsert_plants(conn_cursor, data)
            conn_cursor.commit()
            conn_cursor.close()
        except Exception as err:
            return {"statusCode": 400, 'body': f"Failure: {err}"}
    return {'statusCode': 200, "body": "Success."}


if __name__ == "__main__":
    ...
