# Wriiten by Nishant Mittal aka nishantwrp
import click
import os
import configparser
import getpass
import requests
import platform

import shutil
from appdirs import *


@click.command()

@click.option('--info', 'action', flag_value='info',default = True,help="Displays Instructions For Using sublime-backup")
@click.option('--update', 'action', flag_value='update',help="Update The Sublime Snippets Connected With Your Account With Those In Your Computer")
@click.option('--get', 'action', flag_value='get',help="Downloads The Sublime Snippets In A Directory Snippets In The Present Working Directory")
@click.option('--logout', 'action', flag_value='logout',help="Logs Out The Current User")

def cli(action):
    """
    A simple command line tool to backup / sync your sublime snippets
    """

    # Snippets Directory
    snippets_folder = ""
    current_os = platform.system()

    if current_os == 'Linux':
        snippets_folder = os.path.join(os.path.expanduser("~"),'.config')
        snippets_folder = os.path.join(snippets_folder,'sublime-text-3')
        snippets_folder = os.path.join(snippets_folder,'Packages')
        snippets_folder = os.path.join(snippets_folder,'User')
    if current_os == 'Windows':
        snippets_folder = os.path.join(os.getenv('APPDATA'),"Sublime Text 3")
        snippets_folder = os.path.join(snippets_folder,'Packages')
        snippets_folder = os.path.join(snippets_folder,'User')
    if current_os == 'OS X':
        snippets_folder = os.path.join(os.path.expanduser("~"),'Library')
        snippets_folder = os.path.join(os.path.expanduser("~"),'Application Support')
        snippets_folder = os.path.join(snippets_folder,'Sublime Text 3')
        snippets_folder = os.path.join(snippets_folder,'Packages')
        snippets_folder = os.path.join(snippets_folder,'User')

    if os.path.isdir(snippets_folder):
        pass
    else:
        print("Could Not Find Sublime Snippets")
        return

    # Important Variables
    auth_token = ""
    logged = 'false'
    auth_username = ""


    # Find The Config Directory
    appname = "sublime-backup"
    appauthor = "nishantwrp"
    configfolder = user_data_dir(appname,appauthor)
    configfile = os.path.join(configfolder,'config.ini')

    # Create Or Access Config File
    config = configparser.ConfigParser()
    if os.path.exists(configfile):
        config.read(configfile)
        logged = config['auth']['logged']
        auth_username = config['auth']['username']
        auth_token = config['auth']['token']
    else:
        config['auth'] = {}
        config['auth']['logged'] = 'false'
        config['auth']['username'] = ""
        config['auth']['token'] = ""
        try:
            os.makedirs(configfolder)
        except:
            pass
        with open(configfile, 'w+') as config_file:
            config.write(config_file)

    # Connect To Backend
    print("Connecting To Server")
    r = requests.get('https://sublime-backup.herokuapp.com/connect/')
    print("Successfully Connected To Server")


    # Authentication
    msg = 0
    choice = ""
    while(logged == 'false'):
        if msg == 0:
            print("Do you have a sublime-backup account? (yes/no)")
            choice = input()
            msg = 1
        if choice == 'yes':
            print("Username: ",end = "")
            username = input()
            password = getpass.getpass(prompt='Password: ', stream=None)
            url = 'https://sublime-backup.herokuapp.com/auth/'
            data = {'username':username,'password':password}
            print("Checking Credentials")
            r = requests.post(url=url,data=data)
            if r.json()['message'] == 'invalid_credentials':
                print("Invalid Credentials. Please Try Again")
            elif r.json()['message'] == 'logged_in':
                config['auth']['username'] = username
                config['auth']['token'] = r.json()['token']
                config['auth']['logged'] = 'true'
                with open(configfile,'w+') as config_file:
                    config.write(config_file)
                logged = 'true'
                auth_token = r.json()['token']
                auth_username = r.json()['username']
        elif choice == 'no':
            print("Choose A Username: ",end = "")
            username = input()
            password = getpass.getpass(prompt='Choose A Password: ', stream=None)
            url = 'https://sublime-backup.herokuapp.com/auth/register/'
            data = {'username':username,'password':password}
            print("Creating Account")
            r = requests.post(url=url,data=data)
            if r.json()['message'] == 'username_already_exists':
                print("Username Already Exists. Please Try Again With A Different Username")
            elif r.json()['message'] == 'user_registered':
                config['auth']['username'] = username
                config['auth']['token'] = r.json()['token']
                config['auth']['logged'] = 'true'
                with open(configfile,'w+') as config_file:
                    config.write(config_file)
                logged = 'true'
                auth_token = r.json()['token']
                auth_username = r.json()['username']
                print("Account Created")
        else:
            print("Invalid Input")

    # Checking The Credentials
    print("Authenticating...")
    url = 'https://sublime-backup.herokuapp.com/connect/'
    headers = {'Authorization': 'Token ' + auth_token}
    r = requests.get(url=url,headers=headers)
    try:
        if r.json()['detail'] == 'Invalid token.':
            config['auth']['logged'] = 'false'
            with open(configfile,'w+') as config_file:
                config.write(config_file)
            print("Error Authenticating The User. Please Try Again")
            return
    except:
        pass
    print("Authenticated\n")
    print("User Connected: ",end="")
    print(auth_username,end="\n\n")

    # Different Functions

    if (action == 'info'):
        print("sublime-backup v0.1 \nsublime-backup is a basic command line tool that can be used to sync / backup your sublime snippets across Windows, Linux and MacOS.\n(c) 2019 Nishant Mittal\n")
        print("Instructions\n\n1. For uploading your snippets to the server run `sublime-backup --update`. This Will DELETE previously uploaded snippets to this account and replace them by the new sublime snippets currently present in your computer.\n\n2. To download the snippets connected with your account run `sublime-backup --get`. This will CREATE a directory snippets in the present working directory.The snippets are not directly downloaded to your sublime-text-3 folder in order to avoid loss of data\n\n3. To logout run `sublime-backup --logout`.\n\n4. To see the help menu run `sublime-backup --help`.")
    if action == 'logout':
        config['auth']['logged'] = 'false'
        config['auth']['username'] = ""
        config['auth']['token'] = ""
        with open(configfile,'w+') as config_file:
            config.write(config_file)
        print("Logged Out")
        return
    if (action == 'update'):
        # Delete The Previous Snippets
        print("Getting Previous Backup")
        url = 'https://sublime-backup.herokuapp.com/snippets/'
        headers = {'Authorization': 'Token ' + auth_token}
        r = requests.get(url=url,headers=headers)
        print("Removing Previous Backup")
        account_id = ''
        token = ''
        for obj in r.json():
            obj_url = "https://api.kloudless.com/v1/accounts/" + account_id + "/storage/files/" + obj['dropbox_id'] + "/?permanent=true"
            obj_headers = {
            'Authorization' : "Bearer " + token
            }
            obj_r = requests.delete(url=obj_url,headers=obj_headers)
        print("Almost There")
        url = 'https://sublime-backup.herokuapp.com/snippets/delete/'
        headers = {'Authorization': 'Token ' + auth_token}
        r = requests.get(url=url,headers=headers)
        if r.json()['message'] == 'snippets_deleted':
            print("Previous Backup Removed")
        # Upload New Snippets
        print("Backing Up Current Snippets")
        all_files =  os.listdir(snippets_folder)
        for obj in all_files:
            if obj.endswith('.sublime-snippet'):
                print("Uploading ",end="")
                print(obj)
                snippet_file = os.path.join(snippets_folder,obj)
                url = 'https://sublime-backup.herokuapp.com/snippets/upload/'
                headers = {'Authorization': 'Token ' + auth_token}
                files = {'snippet_file': open(snippet_file,'rb')}
                r = requests.post(url=url,headers=headers,files=files)
                if r.json()['message'] == 'snippet_uploaded':
                    print(obj,end="")
                    print(" successfully uploaded")
        print("Backup Complete")
    if action == 'get':
        # Download The Snippets
        download_folder = os.path.join(os.getcwd(),'sublime-backup-snippets')
        if os.path.isdir(download_folder):
            shutil.rmtree(download_folder)
        os.makedirs(download_folder)
        # API requests
        print("Downloading Snippets")
        url = 'https://sublime-backup.herokuapp.com/snippets/'
        headers = {'Authorization': 'Token ' + auth_token}
        r = requests.get(url=url,headers=headers)
        for obj in r.json():
            print("Downloading ",end="")
            print(obj['original_name'])
            file_path = os.path.join(download_folder,obj['original_name'])
            x = requests.get(obj['snippet_file'])
            with open(file_path,'wb') as f:
                f.write(x.content)
            print(obj['original_name'],end="")
            print(" successfully downloaded")
        print("Snippets Downloaded In ",end="")
        print(download_folder)





if __name__ == "__main__":
    cli()
