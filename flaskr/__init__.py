import os
from flask import Flask

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flask.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config, silent=True)

    # Create the instance folder if not exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Import the method to initialize database
    from . import db
    db.init_app(app)

    # Import and register the Authentication blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # Import and register the Blog blueprint
    from . import blog
    app.register_blueprint(blog.bp) # Note Blog does not have url_prefix but Auth does
    app.add_url_rule('/', endpoint='index')

    return app