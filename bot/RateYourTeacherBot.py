import requests
import time
import messages
import Time
from Cist import Cist
from Bot import Bot


class RateYourTeacherBot(Bot):

    def __init__(self, token, database):
        super().__init__('https://api.telegram.org/bot',
                         token,
                         update_frequency=1)
        self.db = database

    def default_command(self, info):
        message = messages.default_command
        self.send_message(info['chat']['id'], message)

    def on_start_command(self, info):
        """
        Активация учетной записи студента
        """
        print("Start command")
        print("Username: ", info['chat']['username'])
        print("Input text", info['text'])

        username = info['chat']['username']
        commands = info['text'].split(" ")
        if len(commands) > 1:
            username = commands[1]
        select_student = """
        SELECT * FROM Student WHERE student_tg_username = '%s'
        """ % username
        result = self.db.execute_select(select_student)
        if len(result) == 0:
            print("No student with such username")
            message = messages.no_such_username
            self.send_message(info['chat']['id'], message)
            return

        result = result[0]
        if result['student_chat_id'] != -1:
            print("Already exist")
            message = messages.already_active
            self.send_message(info['chat']['id'], message)
        else:
            print("Activation")
            activate_student = """
            UPDATE Student
            SET student_chat_id = %i
            WHERE student_id = %i
            """ % (int(info['chat']['id']), int(result['student_id']))
            is_activate = self.db.execute_update_and_create(activate_student)
            if is_activate:
                self.send_message(info['chat']['id'], messages.activation_success)
            else:
                self.send_message(info['chat']['id'], messages.activation_error)

    def on_vote_command(self, info):
        self.send_message(info['chat']['id'], messages.vote_command)

    def handle_current_lecture(self, lecture, teacher, subject, group_id):
        """
        Очень важно! Если у вас по расписанию сейчас две пары (например англ => 2 группы)
        голосовать можно то за последнюю добовленную, потому что у каждого студента записан номер
        последнего голосования в котором он участвовал(-ует)
        """
        select_teacher = """
        SELECT * FROM Teacher
        WHERE teacher_id = %i
        """ % int(teacher['id'])
        find_teacher = self.db.execute_select(select_teacher)
        if len(find_teacher) == 0:
            insert_teacher = """
            INSERT INTO Teacher(teacher_full_name, teacher_short_name, teacher_id) 
            VALUES ('%s', '%s', %i)
            """ % (teacher['full_name'],  teacher['short_name'], int(teacher['id']))
            result = self.db.execute_update_and_create(insert_teacher)
            if not result:
                print("WARNING, TEACHER NOT INSERTED")
                return

        message = messages.vote_request % (teacher['short_name'], subject['brief'])

        print("Create new vote")
        insert_vote = """
        INSERT INTO Vote( group_id, teacher_id, vote_mark_sum, 
        vote_num_of_participants, vote_start_time)
        VALUES (%i, %i, %i, %i, %i)
        """ % (group_id, int(teacher['id']), 0, 0, int(time.time()))
        result = self.db.execute_update_and_create(insert_vote)
        if not result:
            print("WARNING, VOTE NOT INSERTED")

        select_students = """
        SELECT * FROM Student
        WHERE group_id = %i
        """ % int(group_id)
        students = self.db.execute_select(select_students)
        for student in students:
            if student['student_chat_id'] != -1:
                response = self.send_message(student['student_chat_id'], message)
                if requests is not None:
                    response_json = response.json()
                    vote_message_id = int(response_json['result']['message_id'])
                    update_student = """
                    UPDATE Student
                    SET student_last_vote_id = LAST_INSERT_ID(), student_vote_message_id = %i
                    WHERE student_id = %i
                    """ % (vote_message_id, int(student['student_id']))
                    result = self.db.execute_update_and_create(update_student)
                    print("Result of adding voting to student: ", result)

    def check(self, lecture):
        if lecture.is_ended():
            select_groups = """
            SELECT * FROM rate_your_teacher.Group
            """
            groups = self.db.execute_select(select_groups)
            for group in groups:
                Cist.handle_current_lectures(int(group['group_id']), lecture.current_num,
                                             self.handle_current_lecture)

            lecture.next()

    def on_message_received(self, info):
        if 'reply_to_message' in info:
            print("Voting")
            print("Username: ", info['chat']['username'])
            print("Chat id: ", info['chat']['id'])
            print("Reply message id: ", info['reply_to_message']['message_id'])
            print("Text: ", info['text'])

            select_student = """
            SELECT * FROM Student WHERE student_chat_id = %i
            """ % int(info['chat']['id'])
            student = self.db.execute_select(select_student)

            if len(student) == 0:
                self.send_message(info['chat']['id'], messages.voting_no_such_username)
                return
            student = student[0]

            if student['student_vote_message_id'] != info['reply_to_message']['message_id']:
                self.send_message(info['chat']['id'], messages.voting_not_correct_vote_m_id)
                return

            select_vote = """
            SELECT * FROM Vote WHERE vote_id = %i
            """ % int(student['student_last_vote_id'])
            vote = self.db.execute_select(select_vote)[0]

            if int(time.time()) - int(vote['vote_start_time']) > Time.SEC_IN_15_MIN:
                self.send_message(info['chat']['id'], messages.voting_late)
                return

            try:
                student_mark = int(info['text'].split(" ")[0])
            except ValueError:
                self.send_message(info['chat']['id'], messages.voting_nan)
                return

            if student_mark > 10:
                student_mark = 10
            elif student_mark < 0:
                student_mark = 0

            update_vote = """
            UPDATE Vote
            SET vote_mark_sum = vote_mark_sum + %i, 
            vote_num_of_participants = vote_num_of_participants + 1
            WHERE vote_id = %i
            """ % (student_mark, int(student['student_last_vote_id']))

            result = self.db.execute_update_and_create(update_vote)
            if not result:
                print("WARNING, VOTE NOT UPDATED")
            update_student = """
            UPDATE Student
            SET student_vote_message_id = -1, student_last_vote_id = -1
            WHERE student_id = %i
            """ % int(student['student_id'])
            result = self.db.execute_update_and_create(update_student)
            if not result:
                print("WARNING, STUDENT NOT UPDATED")
            self.send_message(info['chat']['id'],
                              messages.voting_successful
                              % vote['teacher_id'])

        else:
            self.send_message(info['chat']['id'], messages.default_message)
