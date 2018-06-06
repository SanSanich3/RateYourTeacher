import pymysql


class DataBase:
    def __init__(self, database, host, user, password):
        self.connection = pymysql.connect(user=user, password=password,
                                          host=host,
                                          database=database,
                                          charset='utf8')

    def execute_select(self, sql):
        cursor = self.connection.cursor()
        cursor.execute(sql)

        attributes = cursor.description
        fetch = cursor.fetchall()

        answer = [{} for _ in range(len(fetch))]
        for indexOfItem in range(len(fetch)):
            for indexOfAttr in range(len(attributes)):
                answer[indexOfItem][attributes[indexOfAttr][0]] = \
                    fetch[indexOfItem][indexOfAttr]
        return answer

    def execute_update_and_create(self, sql):
        cursor = self.connection.cursor()
        answer = True
        try:
            cursor.execute(sql)
            self.connection.commit()
        except pymysql.err.Error:
            answer = False
        return answer

    def get_all_from(self, table_name):
        cursor = self.connection.cursor()
        sql = "SELECT * FROM " + table_name
        cursor.execute(sql)

        attributes = cursor.description
        fetch = cursor.fetchall()

        answer = [{} for _ in range(len(fetch))]
        for indexOfItem in range(len(fetch)):
            for indexOfAttr in range(len(attributes)):
                answer[indexOfItem][attributes[indexOfAttr][0]] = \
                    fetch[indexOfItem][indexOfAttr]

        return answer
