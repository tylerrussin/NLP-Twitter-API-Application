import psycopg2

def get_table(elephantsql_client, command):
    '''Returns a list of values from table'''
    cur = elephantsql_client.cursor()
    try:
        # Execute commands in order
        cur.execute(command)

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        elephantsql_client.rollback()
        cur.close()
        return 1

    # Create list of database values
    returned = []
    returned_list = cur.fetchall()
    for tup in returned_list:
        returned.append(tup[0])
    
    # Close communication with the PostgreSQL database server
    cur.close()

    return returned