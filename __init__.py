from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)

    # Set configurations from config.py needed
    # for setting up sessions
    app.config.from_pyfile('config.py')

    @app.route('/hello')
    def hello():
        return "This is the main page"

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app