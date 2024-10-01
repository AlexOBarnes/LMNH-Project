source .env
sqlcmd -S $HOST,$DB_PORT -U $DB_USER -P $DB_PW -d $DB_NAME -Q 'TRUNCATE TABLE gamma.recordings;'