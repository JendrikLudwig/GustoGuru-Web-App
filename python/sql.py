
def getUser(id, connection):
    cursor = connection.cursor()
    sql = """
        SELECT * FROM USER
        WHERE id = "{0}"
    """.format(id)
    cursor.execute(sql)
    results = cursor.fetchall()
    return results


def insertUser(id, connection):
    cursor = connection.cursor()
    sql = """
        INSERT INTO USER
        VALUES ('{0}')
    """.format(id)
    cursor.execute(sql)
    connection.commit()


def insertRecipe(uuid, data, connection):
    cursor = connection.cursor()
    sql = """
        INSERT OR REPLACE INTO RECIPES (id, data)
        VALUES ('{0}', '{1}');
    """.format(uuid, data)
    cursor.execute(sql)
    connection.commit()


def getRecipe(id, connection):
    cursor = connection.cursor()
    sql = """
        SELECT * FROM RECIPES
        WHERE id = "{0}"
    """.format(id)
    cursor.execute(sql)
    results = cursor.fetchone()
    return results
