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

The examples below and the available Heroku deployment available [here](https://moodial-server.herokuapp.com/) use a shared MongoDB instance that is not to be used in production and is only for testing purposes. Feel free to use this database or create your own.

If you wish to use your own database, use [Atlas](https://docs.atlas.mongodb.com/getting-started/) to deploy a cluster and use the relevant [connection string](https://stackoverflow.com/a/66270640) and database name in the methods below.

### Local

To use the available MongoDB instance, run the following in the /api directory:
`py app/app.py --secret_key secretkey --jwt_secret_key jwtsecretkey --db_name moodialdb --mongo_uri mongodb+srv://user1:3dKskn44HalWYWPH@moodial-test.qhgwo.mongodb.net/moodialdb?retryWrites=true"&"w=majority`

To use your own MongoDB database, run the following in the /api directory and replace the variables or use strings provided by Atlas UI:
`py app/app.py --secret_key secretkey --jwt_secret_key jwtsecretkey -db <db_name> -uri mongodb+srv://<username>:<clustername>@<cluster>.mongodb.net/<db_name>?retryWrites=true"&"w=majority`

> Note: You may need to escape the ampersand ('&') in the connection string in your terminal by using `"&"`

### Heroku Deployment

The existing [Heroku deployment](https://moodial-server.herokuapp.com/) uses environment variables pointing at the aforementioned MongoDB instance.

You can deploy your own version of the server onto Heroku using this [guide](https://devcenter.heroku.com/articles/git).

When you have your server running on Heroku, you can set the needed environment variables using the Heroku cli:

```
heroku config:set IS_HEROKU=True
heroku config:set SECRET_KEY=secretkey
heroku config:set JWT_SECRET_KEY=jwtsecretkey
heroku config:set DBNAME=<db_name>
heroku config:set MONGO_URI=<connection_string>
```

> Note: You may need to escape the ampersand ('&') in the connection string in your terminal by using `^^^&`
