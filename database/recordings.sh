source .env
row_count=$(sqlcmd -S $HOST,$DB_PORT -U $DB_USER -P $DB_PW -d $DB_NAME -Q 'SET NOCOUNT ON; SELECT COUNT(*) FROM gamma.recordings;' -h -1 | xargs)
echo "Number of rows in recordings table: $row_count"