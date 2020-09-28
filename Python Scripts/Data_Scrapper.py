
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from sqlite3 import Error
import time

DB_PATH = '<path for sqlite3 dbfile>'
CHROME_DRIVER_PATH = '<path for Chrome Driver>'

def create_connection(db_file, delete_db=False):
    import os
    if delete_db and os.path.exists(db_file):
        os.remove(db_file)

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = 1")
    except Error as e:
        print(e)

    return conn

def insert_movie_master(conn, values):
    sql = ''' INSERT INTO MOVIE_MASTER(Movie_Name,Movie_RunTime,Movie_Rating,Movie_Votes_Count)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, values)
    return cur.lastrowid

def insert_movie_genre_mapper(conn, values):
    sql = ''' INSERT INTO MOVIE_GENRE_MAPPER(Movie_Name,Movie_Genre,ID)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, values)
    return cur.lastrowid

def insert_movie_genre_master(conn, values):
    sql = ''' INSERT INTO MOVIE_GENRE_MASTER(Genre,Genre_ID)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, values)
    return cur.lastrowid

def insert_movie_release_date(conn, values):
    sql = ''' INSERT INTO MOVIE_RELEASE_DATE(Movie_Name,Release_Date,PK)
              VALUES(?,DATE(?),?) '''
    cur = conn.cursor()
    cur.execute(sql, values)
    return cur.lastrowid

def insert_movie_no_release_date(conn, values):
    sql = ''' INSERT INTO MOVIE_RELEASE_DATE(Movie_Name,PK)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, values)
    return cur.lastrowid

def convert_date_format(day,month,year):
    if month[0:3].lower() == 'jan':
        mon = '01';
    elif month[0:3].lower() == 'feb':
        mon = '02';
    elif month[0:3].lower() == 'mar':
        mon = '03';
    elif month[0:3].lower() == 'apr':
        mon = '04';
    elif month[0:3].lower() == 'may':
        mon = '05';
    elif month[0:3].lower() == 'jun':
        mon = '06';
    elif month[0:3].lower() == 'jul':
        mon = '07';
    elif month[0:3].lower() == 'aug':
        mon = '08';
    elif month[0:3].lower() == 'sep':
        mon = '09';
    elif month[0:3].lower() == 'oct':
        mon = '10';
    elif month[0:3].lower() == 'nov':
        mon = '11';
    else:
        mon = '12';

    if int(day) < 10:
        day = '0' + day

    return year + '-' + mon + '-' + day

if __name__ == '__main__':
    Movie_Data = []
    Movie_Name = []
    Movie_RunTime = []
    Movie_Genre = []
    Movie_Rating = []
    Votes_Count = []
    Movie_Genre_Mapper = []
    Movie_genre_List = []
    Release_Date_List = []
    Movie_Release_Data = []

    driver = webdriver.Chrome(CHROME_DRIVER_PATH)
    driver.get("https://www.imdb.com/search/title/?title_type=feature&release_date=2019-01-01,2020-01-01")
    content = driver.page_source
    soup = BeautifulSoup(content,features="lxml")

    no_of_pages = 5

    for i in range(0,no_of_pages):
        for div in soup.findAll('div',href=False,attrs={'class':'lister-item-content'}):
            link_soup = ''
            link_content = ''
            h3 = div.find('h3',href=False,attrs={'class':'lister-item-header'})
            movie = h3.find('a',href=True)
            #print(movie['href'])
            Movie_Name.append(h3.find('a',href=True).text)

            #link = driver.find_element_by_link_text(movie)
            print('https://www.imdb.com'+movie['href'])
            driver.get('https://www.imdb.com'+movie['href'])

            link_content = driver.page_source
            link_soup = BeautifulSoup(link_content,"lxml")
            link_content_data = (link_soup.find_all('div',{'class' : 'subtext'}))
            Release_Date_Text = ''
            for data in link_content_data:
                if data.find('a',{'title' : 'See more release dates'}) is not None:
                    Release_Date_Text = data.find('a',{'title' : 'See more release dates'}).text.split('(')[0]
                    Release_Date_List.append(Release_Date_Text)

            print(Release_Date_Text)
            print(movie.text)
            #Release_Date_List.append(div.find('a',href=True,attrs={'title':'See more release dates'}).text)
            driver.back()

        for p in soup.findAll('span',href=False,attrs={'class':'runtime'}):
            Movie_RunTime.append(p.text)

        for p in soup.findAll('span',href=False,attrs={'class':'genre'}):
            Movie_Genre.append(p.text.strip().split(','))

        for div in soup.findAll('div',href=False,attrs={'class':'inline-block ratings-imdb-rating'}):
            Movie_Rating.append(float(div.find('strong').text))

        for p in soup.findAll('p',attrs={'class':'sort-num_votes-visible'}):
            #No_Of_Votes = p.find('span',attrs={'name':'nv'}).text
            Votes_Count.append(int(p.find('span',attrs={'name':'nv'}).text.replace(',','')))

        if i != no_of_pages:
            link = driver.find_element_by_link_text('Next »')
            link.click()
            time.sleep(3)
            content = driver.page_source
            soup = BeautifulSoup(content,features="lxml")

    for i in range(len(Movie_Name)):
        Movie_Data.append((Movie_Name[i],int(Movie_RunTime[i].replace('min','').strip()),Movie_Rating[i],Votes_Count[i]))
        if len(Release_Date_List[i].split()) == 3 :
            Release_Date = convert_date_format(Release_Date_List[i].split()[0].strip(),Release_Date_List[i].split()[1].strip(),Release_Date_List[i].split()[2].strip())
            Movie_Release_Data.append((Movie_Name[i],Release_Date))
        else:
            Movie_Release_Data.append((Movie_Name[i]))
        for j in range(len(Movie_Genre[i])):
            Movie_Genre_Mapper.append((Movie_Name[i],Movie_Genre[i][j].replace(' ','')))
            if Movie_Genre[i][j].replace(' ','') not in Movie_genre_List:
                Movie_genre_List.append(Movie_Genre[i][j].replace(' ',''))

    conn = create_connection(DB_PATH)
    count = 0
    with conn:
        for values in Movie_Data:
            insert_movie_master(conn,values)

        for values in Movie_Genre_Mapper:
            count += 1
            values = list(values)
            values.append(count)
            values = tuple(values)
            insert_movie_genre_mapper(conn,values)

        count = 0
        for values in Movie_genre_List:
            count += 1
            values = (values,count)
            #print(values)
            insert_movie_genre_master(conn,values)

        count = 0
        for values in Movie_Release_Data:
            count += 1
            values = list(values)
            values.append(count)
            values = tuple(values)
            if len(list(values)) == 3 :
                insert_movie_release_date(conn,values)
            else:
                insert_movie_no_release_date(conn,values)
