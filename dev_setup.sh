make docker/downv
make docker/up

sleep 2
#make db/upgrade revision="916737379902"
#make db/revision m="add config"
make db/upgrade

sleep 1

uv run --env-file=.env etl/load_messages.py --csv etl/data/responses.csv

PSQL_DSN="postgresql://postgres:postgres@localhost:65432/postgres"
psql "${PSQL_DSN}" -c '
select 1
'