import os
class Config(object):
    DEBUG=False
    

    basedir=os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI='postgres://nnghtdwydhzhyp:4d11ec365e83a2eb48ec8a204d51273dcd4612e70e3a314fde7b4de1b964b68a@ec2-52-201-55-4.compute-1.amazonaws.com:5432/dae4mu7can1gs9'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    CORS_HEADERS='Content-Type'
    MAIL_SERVER='imap.gmail.com'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME='magaranub@gmail.com'
    MAIL_PASSWORD='*******'
    ALLOWED_PICTURE_EXTENSION=['JPEG',"JPG"]
    SECRET='secret'
    ALLOWED_IMAGE_EXTENSION=['DOCX','PDF']


    



class Production(Config):
    pass

class Development(Config):
    DEBUG=False
    basedir=os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI='postgresql+psycopg2://flasktest:*******@flasktest.cd7q5lzal6jr.us-east-1.rds.amazonaws.com:5432/flasktest'
