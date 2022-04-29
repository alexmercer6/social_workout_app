import os
import psycopg2

DB_URL = os.environ.get("DATABASE_URL", "dbname=grow_app")

# Run a SQL SELECT query and return all rows of results
# Example:
# results = sql_fetch('SELECT * FROM food WHERE id = %s', [id])
def sql_fetch(query, parameters=[]):
  conn = psycopg2.connect(DB_URL)
  cur = conn.cursor()
  cur.execute(query, parameters)
  results = cur.fetchall()
  conn.close()
  return results

# Run a SQL INSERT/UPDATE/DELETE query and do a commit.
# Example:
# sql_write('INSERT INTO food (name, price) VALUES (%s, %s)', [name, price])
def sql_write(query, parameters=[]):
  conn = psycopg2.connect(DB_URL)
  cur = conn.cursor()
  cur.execute(query, parameters)
  conn.commit()
  conn.close()