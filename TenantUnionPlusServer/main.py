from server import *
import os

if __name__ =="__main__":
    os.system("export FLASK_APP=server.py")
    os.system("export FLASK_DEBUG=true")
    os.system("flask initdb")
    os.system("flask run")
    while(True):
        os.system("flask update")
        time.sleep(3600)
