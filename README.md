#====================  
#    Door To Door  
#====================  

This is DoorToDoor App
we will build Delivery Application using Python 3 and Django  

There will be three sides to this application and users must be connected to use it:  

* 1- Customer can add, modify or delete product and view his Dashboard  
* 2- Delivery man views today's product and modify status "doing", "done", "return"  
* 3- Admin can use like a customer or delivery man, have all dashboard and manage  
* 4- Employe can view all dashboard

## How do I get set up?
* [Demo](#demo)
* [Install Python](#1.Python-environment)
* [Clone Project](#2.Clone-repositorie)
* [Install required python packages](#3.Install-Packages)
* [Database migrations](#4.Apply-database-migrations)
* [App User](#6.Manage-Users)
* [Test local](#5.Run-the-app)
* [Troubleshooting](#6.-Troubleshooting)
* [Contact Information ](#Contact-Information)


## Demo
View the application at [Door To Door App](http://104.236.104.196/)

## 1.Python environment

The environement setup process depends on your system. Do some research to find out how to do it on OS.  
For MAC you can use the following commands  
```
pip install virtualenv
```

Create virtual environment
```
python -m virtualenv myenv
```
Active this env

```
Mac: source myenv/bin/activate
Windows: myenv\Scripts\activate.bat

```

## 2.Clone repositorie
Clone the repo and move to the project folder
```
git clone *repo_url*
cd dkrexpress

```

## 3.Install Packages
```

pip install -r requirements.txt

```

## 4.Apply database migrations
```
python manage.py makemigrations
python manage.py migrate
```

## 5.Run the app
Let’s start the development server and explore it.

```
python manage.py runserver

```
The api should now be running at http://127.0.0.1:8000/


## 6.Manage Users
* Create an admin user  
First we’ll need to create a user who can login to the admin site. Run the following command:  

```
python manage.py createsuperuser
```
If the server is not running start it again by running:  
```
python manage.py runserver
```

Now, open a Web browser and go to admin on your local domain   
🚨 check `dkrexpress/dkrexpress/urls.py` to know URL of `admin.site.urls`  
You should see the admin’s login screen:  
<img src="https://docs.djangoproject.com/en/3.2/_images/admin01.png" align="center"
     alt="Size Limit logo by Anton Lovchikov">  
Now, try logging in with the superuser account you created in the previous step  
You should see the Django admin index page:  
 <img src="https://docs.djangoproject.com/en/3.2/_images/admin02.png" align="center"
     alt="Size Limit logo by Anton Lovchikov">  
     \
Users must be connected to use the app so tests need to have data: users with groups  
* Create Groups:  
Must have 4 groups:
| Groups Name |                             Description                                      |
|-------------|------------------------------------------------------------------------------|
| Admin       | Can use like Clients or Livreurs account,have all dashboard and manage them  |
| Clients     | Add, modify or delete product and view his Dashboard                         |
| Employes    | View all dashboard                                                           |
| Livreurs    | View today's product and modify status "doing", "done", "return"             |

* Create Users:
4 users mustt be create and associate it a group  
The groups this user belongs to. A user will get all permissions granted to each of their groups.  
Run tthe App again [like this](#5.Run-the-app) and Connect with users created

## 6. Troubleshooting 

If there is any problem during the installation of the python package, just install each them one by one using   
```
pip install *package_name*. 
```
The most important packages are `django`, `django-allauth` and `django-crispy-forms`.

## Contact Information 
@mbayedione10  
mbayedione10@gmail.com  

