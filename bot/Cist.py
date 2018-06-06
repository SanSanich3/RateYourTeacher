import requests
import time
import Time


def where(arr, key, value):
    return list(filter(lambda x: x[key] == value, arr))


class Cist:
    URL = "http://cist.nure.ua/ias/app/tt/"

    @staticmethod
    def get_group_id(full_group_name):
        faculty_name, group_name = full_group_name.split('-', 1)
        direction_name = group_name.split('-', 1)[0]

        command = "P_API_GROUP_JSON"
        res = requests.get("http://cist.nure.ua/ias/app/tt/" + command)
        group_json = res.json()

        faculty = where(group_json["university"]["faculties"], "full_name", faculty_name)[0]
        direction = where(faculty["directions"], "full_name", direction_name)[0]
        group = where(direction["groups"], "name", group_name)[0]
        return int(group["id"])

    @staticmethod
    def handle_current_lectures(group_id, current_lecture_num, handle_func):
        # текущий день
        time_from = ((int(time.time()) + Time.SHIFT_FROM_GTM) // Time.SEC_IN_DAY) \
                    * Time.SEC_IN_DAY - Time.SHIFT_FROM_GTM
        time_to = time_from + Time.SEC_IN_DAY - 1
        print("Current time: ", time_from, time_to, int(time.time()))
        print("Current lecture num: ", current_lecture_num)
        # print(time_from, time_to, int(time.time()))
        # тестовый день - 5.06
        # time_from = 1528146000 # 5.06.2018 00:00:00 +3 (KIEV) это начало тек дня
        # time_to = 1528232400 - 1 # 6.06.2018 00:00:00 +3 (KIEV) конец - 1
        # TODO осторожно, debug, тут ставим номер лекции в ручную
        current_lecture_num = 3
        try:
            command = "P_API_EVENTS_GROUP_JSON"
            p = {'p_id_group': group_id, 'time_from': time_from, 'time_to': time_to}
            events_group_json = requests.get("http://cist.nure.ua/ias/app/tt/" + command,
                                             params=p).json()

            cur_lec = where(events_group_json['events'], 'number_pair', current_lecture_num)
            # print(cur_lec)
            for lecture in cur_lec:
                for teacher_id in lecture['teachers']:
                    teacher = where(events_group_json['teachers'], 'id', teacher_id)[0]
                    subject = where(events_group_json['subjects'], 'id', lecture['subject_id'])[0]
                    handle_func(lecture, teacher, subject, group_id)
                    # теперь мы проыеряем есть ли такой препод в бд (табличка Teacher)
                    # 1) если есть - отправляем всем студентам группы опрос о прошедшой паре
                    #    1.1) записываем группе время end_of_pair
                    # 2) если нет - добавлем препода в бд и идем во второй пункт
        except ValueError:
            print("No lectures for today")
