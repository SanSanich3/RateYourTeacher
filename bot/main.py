from settings import *
from DataBase import DataBase
from RateYourTeacherBot import RateYourTeacherBot

db = DataBase("rate_your_teacher", HOST, DATABASE_USER, DATABASE_USER_PASSWORD)
bot = RateYourTeacherBot(TOKEN, db)
bot.run()

