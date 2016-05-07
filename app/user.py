from pymongo import MongoClient
from bson import objectid
from bson.objectid import ObjectId
import _mysql
import config

'''
Defaults to using a test user
'''

username = ""
user_id = -1
run_id = -1

client = MongoClient()
mongodb = client.socrates

db = _mysql.connect(host=config.CREDS["mysql"]["host"], user=config.CREDS["mysql"]["user"], passwd=config.CREDS["mysql"]["password"], db=config.CREDS["mysql"]["database"])

def authenticate(u, p):
    global username, user_id
    e_user = db.escape_string(u)
    e_password = db.escape_string(p)
    q = "SELECT * FROM user WHERE username='%s' and password=SHA1('%s')" % (e_user, e_password)
    db.query(q)
    r = db.store_result()
    if r.num_rows() > 0:
        row = r.fetch_row()[0]
        user_id = row[2] #TODO fetch as a dictionary using a different mysql wrapper
        username = e_user
        return True
    else:
        return False

def register(u, p):
    e_user = db.escape_string(u)
    e_password = db.escape_string(p)
    #check if user already exists
    q = "SELECT * FROM user WHERE username='%s'" % e_user
    db.query(q)
    r = db.store_result()
    if r.num_rows() > 0:
        return False

    q = "INSERT INTO user (username, password) VALUES ('%s', SHA1('%s'))" % (e_user, e_password)
    db.query(q)
    return True

def getWorkingSet(working_set_id):
    working_set = mongodb.working_set.find_one({"_id" : ObjectId(working_set_id)})
    del working_set['_id']
    return working_set

def getWorkingSets():
    working_sets = list(mongodb.working_set.find({"user_id" : user_id}))
    for i in xrange(len(working_sets)):
        working_set_id = working_sets[i]['_id']
        del working_sets[i]['_id']
        working_sets[i]['working_set_id'] = str(working_set_id)
    return working_sets

#returns the insert id
def addWorkingSet(working_set):
    working_set['user_id'] = user_id
    insert_id = mongodb.working_set.insert_one(working_set).inserted_id
    del working_set['_id']
    return insert_id

def removeWorkingSet(working_set_id):
    mongodb.working_set.remove({"_id" : ObjectId(working_set_id)});

def updateWorkingSet(working_set_id, working_set):
    working_set["_id"] = ObjectId(working_set_id)
    mongodb.working_set.save(working_set)
    del working_set['_id']

def renameWorkingSet(working_set_id, new_name):
    working_set = getWorkingSet(working_set_id)
    working_set["working_set_name"] = new_name
    working_set["_id"] = ObjectId(working_set_id)
    mongodb.working_set.save(working_set)
    del working_set['_id']

def log_run(typ,mod,fn):
    global user_id, run_id
    q = "INSERT INTO run_log (`type`, `module`, `function`, `user_id`, `time`) VALUES ('%s', '%s', '%s', %d, NOW())" % (typ, mod, fn, int(user_id))
    db.query(q)
    run_id = db.insert_id()

#log any general activity (login, logout, etc.)
def log_activity(name, value):
    global user_id, run_id
    q = "INSERT INTO activity_log (`name`, `value`, `time`, `user_id`, `run_id`) VALUES('%s', '%s', NOW(), %d, %d)" % (name, value, int(user_id), run_id)
    db.query(q)

''' Sets to using default user '''
def setDefault():
    #first check if test user is in database
    if not authenticate("test", "test"):
        register("test", "test")
    authenticate("test", "test")