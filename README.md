# TenantUnionPlus
Web project for CS411. Helps students find ideal apartment.

# To start:
0. Setup venv
1. Goto TenantUnionPlus
2. run
    `pip install -r requirements.txt`
3. run the following:
    `pip install --editable .`
4. Goto TenantUnionPlus/TenantUnionPlusServer
5. run
    `export FLASK_APP=server.py`
    `export FLASK_DEBUG=true` // don't do this when launching the website to public.
    `flask run`
    `flask initdb`
