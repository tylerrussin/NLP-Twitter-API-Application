import psycopg2

def sql_command(elephantsql_client, command):
    '''Exacutes general commands'''
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