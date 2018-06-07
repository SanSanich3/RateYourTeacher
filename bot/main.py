from settings import *
from Time import Lecture
from DataBase import DataBase
from RateYourTeacherBot import RateYourTeacherBot

db = DataBase("rate_your_teacher", HOST, DATABASE_USER, DATABASE_USER_PASSWORD)
lecture = Lecture()
bot = RateYourTeacherBot(TOKEN, db, lecture)
bot.run()

