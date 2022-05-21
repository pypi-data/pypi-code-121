from qplay_cli.api_clients.user_api import UserAPIClient
import click
import getpass

@click.group()
def user():
    pass

@user.command()
def signup():
    print("Enter your username:")
    username = input()
    
    print("Enter email address:")
    email = input()
    
    print("Enter your name:")
    name = input()
    
    p = getpass.getpass()
    
    response = UserAPIClient().signup(username, name, email, p)
    print(response['message'])
    
    print("Enter verification code")
    code = input()
    response = UserAPIClient().confirm_signup(username, name, code)
    print(response['message'])
    
    UserAPIClient().signin(username, p)
    
 
@user.command() 
def signin():
    print("Enter your username:")
    username = input()
    
    password = getpass.getpass()
    UserAPIClient().signin(username, password)
    print("Sign in sucessfull")