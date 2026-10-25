"""
seed.py - fills caddy_lite database with a pretend school
-- when ran from the terminal it wipes existing data, so it can be re ran
"""

import getpass # type a password without it showing up on the screen
import psycopg # lets python talk to postgres
from werkzeug.security import generate_password_hash # turns passwords into a hash so we don't store them in plain text

# demo account for testing and logging in later
DEMO_PASSWORD = "password123"

# -------------------------------------------------------------------------
# Helper functions: each one inserts a row and gives back its new id.
#
# %s marks a "placeholder". psycopg slots the values in safely for us.
# NEVER build SQL by gluing strings together (e.g. f"... VALUES ('{name}')"),
# because a malicious value could change the SQL itself. That attack is
# called SQL injection, and placeholders prevent it.
#
# RETURNING id tells PostgreSQL to send back the id it just generated,
# so we can use it when linking rows together.
# ---------------------------------------------------------------------------

def add_class(cur, name): 
    cur.execute("INSERT INTO classes (name) VALUES (%s) RETURNING id",
    (name,), # values must be a tuple, so we add a comma to make it one
    )
    return cur.fetchone()[0] # fetchone() gets the returned row; [0] is its first column (id)

def add_user(cur, name, email, password, role):
    cur.execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s) RETURNING id",
        (name, email, generate_password_hash(DEMO_PASSWORD), role),
    )
    return cur.fetchone()[0]

def add_messages(cur, class_id, author_id, title, body, has_consent=False):
    cur.execute(
        "INSERT INTO messages (class_id, author_id, title, body, has_consent) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (class_id, author_id, title, body, has_consent),
    )
    return cur.fetchone()[0]

# ----------------- Main Script ---------------- #

#Ask for POSTgreSQL password when the script runs, instead of writing within code - to prevent saving in files or Ghub
db_password = getpass("PostgreSQL password: ")

# 'with' opens the connection and closes it automatically at the end.
# If everything succeeds, all changes are saved together ("committed").
# If anything fails, everything is undone ("rolled back"), so you never
# end up with a half-filled database.
with psycopg.connect(
    host="localhost",
    dbname="caddy_lite",
    user="postgres",
    password=db_password,
) as conn:

    # cursor - an object with send SWL commands and fetches results
    with conn.cursor() as cur:
    # --- Clear out old data -------------------------------------------
    # TRUNCATE empties tables quickly.
    # RESTART IDENTITY resets the id counters back to 1.
    # CASCADE also empties every table that points at these
    # (parent_child, messages, message_reads, consent_replies). 
        
        cur.execute("TRUNCATE users, classes, children RESTART IDENTITY CASCADE")

        # Classes
        reception = add_class(cur, "Reception")
        year3 = add_class(cur, "Year 3")

        # Staff
        mrs_patel = add_user(cur, "Mrs Patel", "mrs.patel@school.test", "staff")
        mr_jones = add_user(cur, "Mr Jones", "jones@school.test", "staff")

        # Parents
        sarah = add_user(cur, "Sarah Evans", "sarah@parent.test", "parent")
        tom = add_user(cur, "Tom Evans", "tom@parent.test", "parent")
        aisha = add_user(cur, "Aisha Khan", "aisha@parent.test", "parent")
        gareth = add_user(cur, "Gareth Smith", "gareth@parent.test", "parent")

        # Children 
        lily = add_child(cur, "Lily", year3)
        noah = add_child(cur, "Noah", reception)
        zara = add_child(cur, "Zara", year3)
        osian = add_child(cur, "Osian", reception)
        megan = add_child(cur, "Megan", year3)

        # Link parents to children
                # --- Link parents to children --------------------------------------
        # This deliberately includes the tricky cases your app must handle:
        #   - Lily has TWO parents (Sarah and Tom)
        #   - Sarah and Tom have TWO children in DIFFERENT classes (Lily and Noah)
        #   - Gareth has two children in different classes (Osian and Megan)
        # executemany() runs the same SQL once for each pair in the list.

        cur.executemany(
            "INSERT INTO parent_child (parent_id, child_id) VALUES (%s, %s)",
            [
                (sarah, lily), (tom, lily),
                (sarah, noah), (tom, noah),
                (aisha, zara),
                (gareth, osian), (gareth, megan),
            ],
        )
