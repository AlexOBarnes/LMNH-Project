source .env
sqlcmd -S $HOST,$DB_PORT -U $DB_USER -P $DB_PW -d $DB_NAME -i schema.sql
sqlcmd -S $HOST,$DB_PORT -U $DB_USER -P $DB_PW -d $DB_NAME -i seed_data.sql
python seed_plant_data.py