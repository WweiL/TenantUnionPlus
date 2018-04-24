from server import *
import os

if __name__ =="__main__":
    os.system("EXPORT FLASK_APP=server.py")
    os.system("EXPORT FLASK_DEBUG=true")
    # os.system("flask initdb")
    os.system("flask run")
    while(True):
        os.system("flask initdb")
        time.sleep(3600)
