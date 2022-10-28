# DynamoDB-Flask-Blog
### Run via flask --app DynamoDB-Flask-Blog run from outside the directory.  
Table contains Partition Key as PK and Sort Key as SK.  
For Users the Partition Key is USER#*username* and Sort Key is #METADATA#*username*  
For Posts the Partition Key is USER#*username* and Sort Key is POST#*username*#*timestamp* (timestamp in isoformat)
The rest are non primary keys.
