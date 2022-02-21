import psycopg2

def drop_table(elephantsql_client, command):
    '''Drops table included in the input command'''
    cur = elephantsql_client.cursor()
    try:
        cur.execute(command)
        elephantsql_client.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        elephantsql_client.rollback()
        cur.close()
        return 1

    cur.close()