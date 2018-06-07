import csv
from Cist import Cist
from DataBase import DataBase
from settings import *

db = DataBase("rate_your_teacher", HOST, DATABASE_USER, DATABASE_USER_PASSWORD)


group_full_name = "КН-ПЗПІ-16-4"
group_id = Cist.get_group_id(group_full_name)

print(group_full_name, group_id)
insert_group_sql = """
INSERT INTO rate_your_teacher.Group(group_id, group_full_name)
VALUES (%i, '%s')
""" % (group_id, group_full_name)
result = db.execute_update_and_create(insert_group_sql)
print("add group: ", result)

f = open("groups/" + group_full_name + ".csv", "r")
csv_f = csv.reader(f, delimiter=',')
for student in csv_f:
    insert_student_sql = """
    INSERT INTO rate_your_teacher.Student(student_full_name, student_avg_mark,
                                                                      student_tg_username, group_id) 
    VALUES ('%s', %f, '%s', %i)
    """ % (student[0], float(student[1]), student[2], group_id)
    result = db.execute_update_and_create(insert_student_sql)
    print(student, result)
