from io import BytesIO
from DataBase import DataBase
from settings import *

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


class Teacher:
    @staticmethod
    def find_by_surname(database: DataBase, teacher_surname):
        select_teacher = """
        SELECT teacher_id FROM Teacher WHERE teacher_short_name LIKE '%s%%'
        """ % teacher_surname
        teacher = database.execute_select(select_teacher)
        if len(teacher) == 0:
            return None
        teacher = teacher[0]
        return int(teacher['teacher_id'])

    @staticmethod
    def get_base_info(database: DataBase, teacher_id):
        select_teacher = """
        SELECT * FROM Teacher WHERE teacher_id = %i
        """ % int(teacher_id)
        teacher = database.execute_select(select_teacher)
        if len(teacher) == 0:
            return None
        return teacher[0]

    @staticmethod
    def get_rating(database: DataBase, teacher_id):
        select_metrics = """
        SELECT SUM(vote_mark_sum) AS sum_mark, SUM(vote_num_of_participants) AS num_of_participants
        FROM Vote
        WHERE teacher_id = %i
        """ % int(teacher_id)
        metrics = database.execute_select(select_metrics)
        if len(metrics) == 0:
            return None
        metrics = metrics[0]
        try:
            avg_mark = int(metrics['sum_mark']) / int(metrics['num_of_participants'])
            return avg_mark
        except (ZeroDivisionError, TypeError):
            return 0

    @staticmethod
    def get_amount_of_bonus(database: DataBase, teacher_id):
        top = Teacher.get_top(database, n=None)
        sum_of_avg_mark = sum(map(lambda x: x['avg_mark'], top))
        teacher = list(filter(lambda x: int(x['teacher_id']) == teacher_id, top))
        if len(teacher) == 0:
            return 0
        teacher_avg_mark = teacher[0]['avg_mark']
        return int((teacher_avg_mark * BUDGET) / sum_of_avg_mark)

    @staticmethod
    def get_statistics(database: DataBase, teacher_id):
        select_metrics = """
        SELECT vote_mark_sum / GREATEST(vote_num_of_participants, 1) AS avg_mark, 
        vote_start_time
        FROM Vote
        WHERE teacher_id = %i
        """ % int(teacher_id)
        metrics = database.execute_select(select_metrics)
        return metrics

    @staticmethod
    def build_plot(metrics):
        x = [int(el['vote_start_time']) for el in metrics]
        y = [el['avg_mark'] for el in metrics]
        plt.style.use('ggplot')
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        axis.plot(x, y)
        axis.set_xlabel("время")
        axis.set_ylabel("оценка")
        axis.set_xticklabels([])
        canvas = FigureCanvas(fig)
        output = BytesIO()
        canvas.print_png(output)
        return output.getvalue()

    @staticmethod
    def get_top(database: DataBase, n=10):
        select_top = """
        SELECT SUM(vote_mark_sum) / GREATEST(SUM(vote_num_of_participants), 1) AS avg_mark,
        teacher_short_name, Teacher.teacher_id
        FROM Vote INNER JOIN Teacher ON Vote.teacher_id = Teacher.teacher_id
        GROUP BY Vote.teacher_id, teacher_short_name
        ORDER BY avg_mark DESC 
        """
        top = database.execute_select(select_top)
        return top[:n]

