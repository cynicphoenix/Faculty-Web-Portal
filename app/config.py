# Before running:
# setx FLASK_CONFIG "development"
# setx FLASK_APP "run.py"

class Config(object):
    """common configs"""
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}