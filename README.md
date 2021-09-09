# Moodial Back-end

Backend for mood-tracking app. Flask application connecting to an instance of MongoDB. Created by Sean Lawless with some minor updates by myself. Re-hosting in repo for purpose of continuation of completed work by a future student.

## File Structure

app

> \_\_init\_\_.py  
> app.py  
> config.py _(For MongoDB connection)_

static

> images  
> graphs

requirements.txt  
README.md

_(For Heroku hosting)_  
wsgi.py  
Procfile

## Install and Run:

1. Install all requirements located in requirements.txt
   `pip install -r requirements.txt`

2. run app.py, this should launch a webserver at localhost:5000
   `py app/app.py`

3. Use browser of choice to visit localhost:5000

4. Swagger UI will show all available endpoints

5. User must be created in order to access protected endpoints ( shown with a lock in swagger )

6. To create a user do the following:
   1. Click /register endpoint
   2. Send required details in body. Username, email, password ( test user is 'david' password is 'abc123' )
   3. Go to log in and fill in required details in body.
   4. Send request and copy the JWT token returned
7. On localhost:5000, on upper right hand side there is a button "Authorize". Click it

8. Follow the details on the pop up window to include JWT. Must be prefixed with 'Bearer' e.g)
   `Bearer <JWT>`

## Configure database

By default the app is configured to point to a shared MongoDB instance for testing purposes. This is not to be used in a production environment.

If you wish to use your own database, use [Atlas](https://docs.atlas.mongodb.com/getting-started/) to deploy a cluster and update your local app/config.py with the given connection string as shown [here](https://stackoverflow.com/a/66270640).

```
MONGO_DBNAME = "<db_name>"
MONGO_URI = "mongodb+srv://<username>:<password>@<cluster_name>.mongodb.net/<db_name>?retryWrites=true&w=majority"
```
