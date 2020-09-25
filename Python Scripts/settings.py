import os


PARENT_DIR =  os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
DATABASE_DIR = os.path.join(PARENT_DIR,'Database')

DB_PATH = DATABASE_DIR+'/Movie_Analyzer.db'