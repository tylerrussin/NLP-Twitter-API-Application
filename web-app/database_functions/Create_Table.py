import psycopg2

def create_table(elephantsql_client, command):
    '''Creating table with given input command'''    
    try:
        # A "cursor", a structure to iterate over db records to perform queries
        cur = elephantsql_client.cursor()

        # Execute commands in order
        cur.execute(command)

        # Close communication with the PostgreSQL database server
        cur.close()

        # Commit the changes
        elephantsql_client.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)