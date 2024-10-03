'''Short term pipeline'''

from load_short import load


def lambda_handler(event, context):
    '''Lambda handler'''
    try:
        load()
    except Exception as err:
        return {"statusCode": 400, 'body': f"Failure. Could not extract data, {err}"}
    return {'statusCode': 200, "body": "Success."}


if __name__ == "__main__":
    ...
