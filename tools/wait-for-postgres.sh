#!/bin/sh
set -e

DB_HOSTNAME=${CONDITIONAL_DB_HOSTNAME:-postgres.csh.rit.edu}
DB_USER=${CONDITIONAL_DB_USER:-conditional}
export PGPASSWORD=${CONDITIONAL_DB_PASSWORD}

until psql -h "${DB_HOSTNAME}" -U ${DB_USER} -c '\l' > /dev/null 2>&1; do
  >&2 echo "⧖ Postgres is unavailable, waiting..."
  sleep 1
done

>&2 echo "✔ Postgres is available, starting application."
exec $@
