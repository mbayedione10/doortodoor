# doortodoor

# README #

This is the DoorToDoor App
we will build Delivery Application using Python 3 and Django
There will be three sides to this application and users must be connected to use it:
1- Customer can add product and view his Dashboard
2- Delivery man views today's product and modify status "doing", "done", "return"
3- Admin can add new users, use like a customer or delivery man, have all dashboard and manage

## How do I get set up? ##

####1. Create a python environment####

The environement setup process depends on your system. Do some research to find out how to do it on OS. For MAC you can use the following commands

#!bash
Create virtual environment
virtualenv myenv

Active this env
source myenv/bin/activate
```

####2. Clone the repo and move to the project folder####
```
#!bash
git clone *repo_url*
cd dkrexpress

```

####3. Install required python packages####
```
#!python
pip install -r requirements.txt

```

####4. Apply database migrations####
```
#!bash

python manage.py makemigrations
python manage.py migrate
```


####5. Run the app####
```
#!bash

./manage.py runserver

```
The api should now be running at http://127.0.0.1:8000/

## Troubleshooting ##
If there is any problem during the installation of the python package, just install each them one by one using `pip install` *package_name*. 
The most important packages are `django`, `django-allauth` and `django-crispy-forms`.

