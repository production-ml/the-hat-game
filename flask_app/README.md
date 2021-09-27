[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

The code in this folder is build upon a docker image example taken from an excellent comprehensive guide about Docker https://docker-curriculum.com

Procfile - this one is required for app to deploy on heroku. Read the following for more details: https://devcenter.heroku.com/articles/procfile

To deploy this folder only to the heroku git repo use `git subtree push --prefix flask-app heroku master`. If you are in `heroku` branch, then just `git push heroku master`.
