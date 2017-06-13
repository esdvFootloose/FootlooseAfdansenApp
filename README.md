# Footloose Afdansen Web App
This repo contains the source code for the Web App as used at the "afdansen" (dans exams) of E.S.D.V. Footloose.

This web app is meant to gather and process the grades from jury members. Pairs can be imported from a csv file and get 
fully automatically assigned backnumbers. Heats can be assigned in a drag and drop interface by staff.
Dancers can access the heat information to see when they are scheduled.

Jury members login into the system using phone or tablet and can input grades directly on a juryform. This form only shows
backnumbers instead of names.

Afterwards staff can gather the results, averages are automatically calculated and shown in a table.

## Technical details
The system is written in the [Python](https://www.python.org/) framework [Django](https://www.djangoproject.com/).
It is split in two parts: the index app which handles login and basic things and the afdansen app which handles the 
actual exam things.

The system is capable of parsing a csv file from a form on our website.
It is currently tailored for the form that Footloose uses, but the import function can easily be adjusted to other forms.

## Installation
### First time setup
In our setup everything is ran in a container so everything is in root folder and run as root user.
1. Install python 3, python pip, nginx(or other webserver), postgresql and redis
1. Clone the repo
1. Run ```pip install -r requirements.txt```
1. Generate your own secret key and captcha keys and put them in settings.py
1. Update settings.py with your settings for database and caching
1. Run ```python manage.py makemigrations afdansen index```
1. Run ```python manage.py migrate```
1. Run ```python manage.py createsuperuser```
1. Fill in superuser credentials of your choosing
1. Run ```python InitPopulate.py --mode {production/debug depending on your setting}```


### For development
* for development put --settings=FootlooseAfdansenApp.settings_development after each manage.py command

### For deployement
The following is based on systemd and is an example how to run in production. Other management systems is possible.
Check the systemd files for the commands that they execute to start the system.
1. Start and enable nginx(or other webserver) and redis servers. A sample ```nginx.conf``` is provided in deployement folder
1. Copy all systemd files from deployement folder to ```/etc/systemd/system/```
1. The following commands setup 4 http workers and 2 websockets. Adjust numbers if necesarry
  * systemctl enable httpworker@{1..4}.service
  * systemctl enable websocketworker@{1..2}.service
1. Start and enable httpworker.target, websocketworker.target and daphne