from re import U
import boto3
from pathlib import Path
import json
import click
from flask import g
from botocore.exceptions import ClientError
from .entities import User, Post
from datetime import datetime

# This function reads json file and return its values
# to be used for getting values of TableName, Attributes, etc
def jsonifie(p):
    with p.open('r') as f:
        fi = f.read()
    file = json.loads(fi)
    return [*file.values()]

# Add to Posts in user
# def updatePostUser(user, type):
#     dc = boto3.client('dynamodb', endpoint_url='http://localhost:8000')

#     if type == 'Add':
#         response = dc.update_item(
#         TableName="Users",
#         Key={'Username': {'S': user}},
#         AttributeUpdates={
#             "Posts": {
#                 'Value': {'N': "1"},
#                 'Action': 'ADD'
#             }},
#         ReturnValues = 'ALL_NEW'
#         )
#         return response["Attributes"]

#     if type == 'Sub':
#         response = dc.update_item(
#         TableName="Users",
#         Key={'Username': {'S': user}},
#         AttributeUpdates={
#             "Posts": {
#                 'Value': {'N': "-1"},
#                 'Action': 'ADD'
#             }}
#         )

def updatePost(user, time, t, b, filename = ''):
    dc = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
    time = time.replace(" ", "T")
    if filename != '':
        response = dc.update_item(
        TableName="BlogTable",
        Key={'PK': {'S': "USER#" + user}, 'SK': {'S': "POST#" + user+ '#'+ time}},
        AttributeUpdates={
            "title": {
                'Value': {'S': t},
                'Action': 'PUT'
            },
            "body": {
                'Value': {'S': b},
                'Action': 'PUT'
            },
            "image": {
                'Value': {'S': filename},
                'Action': 'PUT'
            }}
        )
    else:
        response = dc.update_item(
        TableName="BlogTable",
        Key={'PK': {'S': "USER#" + user}, 'SK': {'S': "POST#" + user+ '#'+ time}},
        AttributeUpdates={
            "title": {
                'Value': {'S': t},
                'Action': 'PUT'
            },
            "body": {
                'Value': {'S': b},
                'Action': 'PUT'
            }
            }
        )
    print(response)


def postDelete(user, time):
    dc = boto3.client("dynamodb", endpoint_url = 'http://localhost:8000')
    time = time.replace(" ", "T")
    resp = dc.delete_item(
            TableName="BlogTable",
            Key={"PK": {"S": "USER#" + user}, "SK": {"S": "POST#" + user + "#" + time}},
            ReturnValues="ALL_OLD"
    )
    # g.posts = updatePostUser(resp['Attributes']['Username']['S'], 'Sub')
    return resp


# This function returns a dictionary called item
# which is sent to the register function
def user_item(u, p):
    item = {
        'PK': {'S': 'USER#' + u},
        'SK': {'S': '#METADATA#' + u},
        'username':{'S': u},
        'password': {'S': p},
        'posts': {'N': "0"}
    }
    return item


def post_item(t, b, user, image):
    tm = datetime.now().isoformat("T", "seconds")
    post = {
        'PK': {'S': 'USER#' + user},
        'SK': {'S': 'POST#' + user + '#'+ tm},
        'username': {'S': user},
        'timestamp': {'S': tm},
        'title': {'S': t},
        'body': {'S': b},
        'image': {'S': image}
    }
    return post

def getPost(user, time):
    dc = boto3.client('dynamodb', endpoint_url="http://localhost:8000")
    time = time.replace(" ", "T")
    print()
    response = dc.get_item(
        TableName="BlogTable",
        Key={"PK": {"S": "USER#" + user}, "SK": {"S": "POST#" + user + "#" + time}},
    )
    if response["Item"]:
        post = Post(response["Item"])

        post.time = datetime.fromisoformat(post.timestamp)
    
    return post

# Function to get all posts from DB
def get_posts_db():
    dc = boto3.client("dynamodb", endpoint_url = 'http://localhost:8000')
    response = dc.scan(TableName = 'BlogTable')
    posts = []
    for res in response["Items"]:
        if res.get('SK').get('S').startswith("POST#"):
            post = Post(res)
            post.time = datetime.fromisoformat(post.timestamp)
            posts.append(post)
    
    return posts


# Initializes DB i.e. delete and make new table
def init_db():

    dc = boto3.client("dynamodb", endpoint_url = 'http://localhost:8000')
    
    # Delete table Users
    try:
        dc.delete_table(TableName = 'BlogTable')
    except Exception as err:
        print("Blog Table doesn't exist")
    else:
        print("Deleted Blog Table")

    # Using Users.json file to create Users table
    p = Path(__file__).with_name('Table.json')
    val = jsonifie(p)
    dc.create_table(
        TableName = val[0], 
        AttributeDefinitions = val[1],
        KeySchema = val[2],
        GlobalSecondaryIndexes= val[3],
        ProvisionedThroughput = val[4]
    )



# Checking if User exists and input data
def regis(user, ps):

    dc = boto3.client("dynamodb", endpoint_url = 'http://localhost:8000')
    
    # Create dictionary for all items and put into DB
    item = user_item(user, ps)
    try:
        response = dc.put_item(
            TableName="BlogTable",
            Item=item,
            ConditionExpression="attribute_not_exists(username)",
        )
        return response
    # If condition fails, it goes into except block
    # and returns ConditionalCheckFailedException
    # which is to be checked in the place where function 
    # is called
    except ClientError as e:  
        if e.response['Error']['Code']=='ConditionalCheckFailedException':  
            return e.response['Error']['Code']




def logindb(user):

    dc = boto3.client("dynamodb", endpoint_url = 'http://localhost:8000')
    try:
        response = dc.get_item(
            TableName="BlogTable",
            Key={"PK": {"S": 'USER#' + user}, "SK": {'S': '#METADATA#' + user}}
        )
        blogger = User(response['Item'])
        return blogger
    except KeyError as e:
            return "UserNotFoundException"



def createPost (title, body, user, image = ""):
    dc = boto3.client("dynamodb", endpoint_url = 'http://localhost:8000')
    pos = post_item(title, body, user, image)
    resp = dc.put_item(
            TableName="BlogTable",
            Item=pos
    )
    return resp

# Command line init-db inititalizes from this
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.cli.add_command(init_db_command)
