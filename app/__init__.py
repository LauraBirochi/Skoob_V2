import os
from flask import Flask
from .database import db
from .routes import bp
from .routes_livro import bp_livro
from flask_migrate import Migrate  # <-- import

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")
    
    app = Flask(
        __name__, 
        template_folder=template_dir, 
        static_folder=static_dir, 
        instance_relative_config=True
    )
     
    app.config.from_pyfile("config.py")
    app.config['SECRET_KEY'] = os.urandom(24)
    db.init_app(app)
    
    # Inicializa o migrate
    migrate = Migrate(app, db)

    # Registrar blueprints
    app.register_blueprint(bp)
    app.register_blueprint(bp_livro)
    
    return app
