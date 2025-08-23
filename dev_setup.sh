make docker/downv
make docker/up

sleep 2
#make db/upgrade revision="916737379902"
#make db/revision m="add config"
make db/upgrade

sleep 1

uv run etl/load_messages.py --csv etl/data/responses.csv

PSQL_DSN="postgresql://postgres:postgres@localhost:65432/postgres"
psql "${PSQL_DSN}" -c '
insert into message.message_group_choice
   (snowflake_id, group_id, weight, created_by)
values
   (126029177722765313, 5, 2, 0),
   (126029177722765313, 4, 3, 0);
'