import psycopg2

def single_insert(elephantsql_client, insert_req):
    """ Execute a single INSERT request """
    cur = elephantsql_client.cursor()
    try:
        cur.execute(insert_req)
        elephantsql_client.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        elephantsql_client.rollback()
        cur.close()
        return 1
    cur.close()