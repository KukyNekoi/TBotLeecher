#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'KuKy_NeKoi'
from TwitterAPI import TwitterAPI
import sqlite3
import urllib
import os
import logging
import sys
import time
logging.captureWarnings(True)

CONSUMER_KEY = 'YOUR CONSUMER KEY'
CONSUMER_SECRET = 'YOUR CONSUMER SECRET'
ACCESS_TOKEN_KEY = 'YOUR ACCESS TOKEN KEY'
ACCESS_TOKEN_SECRET = 'YOUR ACCES TOKEN SECRET'

proxy_url = None  # Example: 'https://USERNAME:PASSWORD@PROXYSERVER:PORT'

api = TwitterAPI(CONSUMER_KEY,
                 CONSUMER_SECRET,
                 ACCESS_TOKEN_KEY,
                 ACCESS_TOKEN_SECRET,
                 auth_type='oAuth2',
                 proxy_url=proxy_url)

conn = sqlite3.connect('tbot_database.db')

def leech_user(username, count):
    user = get_user_info(username)
    current_id = user["last_retrieved"]
    max_id = current_id
    request = api.request('statuses/user_timeline', {'count': count,'since_id':current_id,'screen_name': username})

    for item in request:
        if  int(item["id"]) > current_id:
            if 'entities' in item:
                if 'media' in item["entities"]:
                    for media in item["entities"]["media"]:
                        download_media(username, str(media["media_url"]))
            if 'extended_entities' in item:
                if 'media' in item["extended_entities"]:
                    for media in item["extended_entities"]["media"]:
                        if media["type"] == "video":
                            videos = media["video_info"]["variants"]
                            bitrate = 0
                            link = ""
                            print "."
                            for video in videos:
                                if(video["content_type"] == "video/mp4"):
                                    if(video["bitrate"] > bitrate):
                                        link = video["url"]
                                        bitrate = video["bitrate"]
                                        print link
                            download_video(username,str(item["id"]),link)
            if int(item["id"]) > max_id:
                max_id = int(item["id"])
                update_user_id(username, max_id)

def leech_hashtag(hashtag, count):
    hashtag = get_hashtag_info(hashtag)
    current_id = hashtag["last_retrieved"]
    max_id = current_id
    request = api.request('search/tweets', {'q': hashtag["hashtag"],'count': count,'since_id':current_id, 'result_type':'recent'})
    print "request done"
    for item in request:
        if  int(item["id"]) > current_id:
            
            if 'entities' in item:
                if 'media' in item["entities"]:
                    for media in item["entities"]["media"]:
                        download_media(hashtag["hashtag"], str(media["media_url"]))
            if 'extended_entities' in item:
                if 'media' in item["extended_entities"]:
                    for media in item["extended_entities"]["media"]:
                        if media["type"] == "video":
                            videos = media["video_info"]["variants"]
                            bitrate = 0
                            link = ""
                            print "."
                            for video in videos:
                                if(video["content_type"] == "video/mp4"):
                                    if(video["bitrate"] > bitrate):
                                        link = video["url"]
                                        bitrate = video["bitrate"]
                                        print link
                            download_video(hashtag["hashtag"],str(item["id"]),link)
            if int(item["id"]) > max_id:
                max_id = int(item["id"])
                update_hashtag_id(hashtag["hashtag"], max_id)


def download_media(username, url):
    if not os.path.exists(username):
        os.makedirs(username)

    ind=url.rfind('/')
    filename = username + "/" + url[ind+1:]
    try:
        os.remove(filename)
    except OSError:
        pass
    if get_setting("destination") != None:
        f = open(get_setting("destination") + filename,'wb')
    else:
        f = open(filename,'wb')
    f.write(urllib.urlopen(url + ":large").read())
    f.close()
#    sys.stdout.write('.')
    #print ("Downloading:  "  + url)
    #print ("destination:  "  + filename)

def download_video(username,filename, url):
    print "filename: " + filename
    if not os.path.exists(username):
        os.makedirs(username)
    try:
        filename = username + "/" + filename + ".mp4"
        os.remove(filename)
    except OSError:
        pass
    if get_setting("destination") != None:
        f = open(get_setting("destination") + filename,'wb')
    else:
        f = open(filename,'wb')
    f.write(urllib.urlopen(url).read())
    f.close()


def get_leeched_users():
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    ret_val = []
    for user in c.fetchall():
        t = {}
        t["username"] = user[0]
        t["enabled"] = user[1]
        t["last_retrieved"] = user[2]
        ret_val.append(t)
    return ret_val

def get_leeched_hashtags():
    c = conn.cursor()
    c.execute("SELECT * FROM hashtags")
    ret_val = []
    for user in c.fetchall():
        t = {}
        t["hashtag"] = user[0]
        t["enabled"] = user[1]
        t["last_retrieved"] = user[2]
        ret_val.append(t)
    return ret_val



def get_user_info(username):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username='"+username+"'")
    ret_val = []
    for user in c.fetchall():
        t = {}
        t["username"] = user[0]
        t["enabled"] = user[1]
        t["last_retrieved"] = user[2]
        ret_val.append(t)
    return ret_val[0]

def get_hashtag_info(hashtag):
    c = conn.cursor()
    c.execute("SELECT * FROM hashtags WHERE hashtag='"+hashtag+"'")
    ret_val = []
    for hashtag in c.fetchall():
        t = {}
        t["hashtag"] = hashtag[0]
        t["enabled"] = hashtag[1]
        t["last_retrieved"] = hashtag[2]
        ret_val.append(t)
    return ret_val[0]


def get_setting(setting):
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE name='"+setting+"'")
    c.fetchall()[0]

def exists_user(username):
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username='"+username+"'")
    if len(c.fetchall()) > 0:
        return True
    return False


def update_user_id(username, id):
    c = conn.cursor()
    c.execute("UPDATE users SET last_retrieved='"+str(id)+"' WHERE username='"+username+"'")
    conn.commit()



def update_hashtag_id(hashtag, id):
    c = conn.cursor()
    c.execute("UPDATE hashtags SET last_retrieved='"+str(id)+"' WHERE hashtag='"+hashtag+"'")
    conn.commit()

def update_destination(destination):
    c = conn.cursor()
    c.execute("UPDATE settings SET value='"+str(destination)+"' WHERE name='destination'")
    conn.commit()

def add_user(username):
    if not exists_user(username):
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES ('"+username+"',1,1)")
        conn.commit()

def add_hashtag(hashtag):
    if not exists_user(hashtag):
        c = conn.cursor()
        c.execute("INSERT INTO hashtags VALUES ('"+hashtag+"',1,1)")
        conn.commit()

def remove_user(username):
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username='"+username+"'")
    conn.commit()

def remove_hashtag(hashtag):
    c = conn.cursor()
    c.execute("DELETE FROM hashtags WHERE hashtag='"+hashtag+"'")
    conn.commit()


def remove_all_users():
    c = conn.cursor()
    c.execute("DELETE FROM users")
    conn.commit()

def remove_all_hashtags():
    c = conn.cursor()
    c.execute("DELETE FROM hashtags")
    conn.commit()

def execute_update():
    
    for hashtag in  get_leeched_hashtags():
        print("Hashtag: " + hashtag["hashtag"] + ", Enabled: " + str(hashtag["enabled"]) + ", LAST: " + str(hashtag["last_retrieved"]))
        number_of_tweets = len(get_leeched_hashtags())
        # leech_user(hashtag["hashtag"], 200/number_of_tweets)
        leech_hashtag(hashtag["hashtag"], 200)

    for users in  get_leeched_users():
        print("User: " + users["username"] + ", Enabled: " + str(users["enabled"]) + ", LAST: " + str(users["last_retrieved"]))
        number_of_tweets = len(get_leeched_users())
        # leech_user(users["username"], 200/number_of_tweets)
        leech_user(users["username"], 200)


def parse_command(command):

    ind=command.rfind(' ')
    instruction = command[:ind]
    suffix = command[ind+1:]
    if command == "list":
        print "Current users:"
        for user in get_leeched_users():
            print ("\t"+ user["username"])

        print "Current hashtags:"
        for user in get_leeched_hashtags():
            print ("\t"+ user["hashtag"])

    elif instruction == "add_user":
        add_user(suffix)
        print "User added. List of current users:"
        for user in get_leeched_users():
            print ("\t"+ user["username"])

    elif instruction == "add_hashtag":
        add_hashtag(suffix)
        print "hashtag added. List of current hashtags:"
        for hashtag in get_leeched_hashtags():
            print ("\t"+ hashtag["hashtag"])

    elif instruction == "remove":
        if suffix == "all":
            remove_all_users()
            remove_all_hashtags()
        else:
            remove_user(suffix)
            remove_hashtag(suffix)
        print "User(s) removed. List of current users:"
        for user in get_leeched_users():
            print ("\t"+ user["username"])

            
    elif command == "leech":
        print "Starting leeching process"
        execute_update()
        print "Leeching process finished."

    elif command == "daemon":
        print "Starting leeching process in daemon mode"
        while(True):
            execute_update()
            time.sleep(5*50)
        print "Leeching process finished."

    elif command == "set":
        idx = suffix.rfind(' ')
        operation = suffix[0:idx]
        argument = suffix[idx+1:]
        if operation == "destination":
            update_destination(argument)
        else:
            print "ERROR: Variable not recognized."
    elif command == "quit":
        print "Bye bee~"
        quit()
    else:
        print "ERROR: COMMAND NOT RECOGNIZED OR INCOMPLETE!"



def init_db():
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    if(len(c.fetchall()) < 1):
        c.execute('''CREATE TABLE users
             (username text, enabled number, last_retrieved number )''')
        c.execute('''CREATE TABLE hashtags
             (hashtag text, enabled number, last_retrieved number )''')
        conn.commit()
        c.execute('''CREATE TABLE settings
             (name text, value text)''')
        conn.commit()
        c.execute("INSERT INTO settings VALUES ('destination','')")
        conn.commit()

init_db()

while True:
    parse_command(raw_input("> "))
