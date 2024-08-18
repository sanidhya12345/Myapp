class Config:
    SECRET_KEY='san123'
    MYSQL_USER='root'
    MYSQL_HOST='localhost'
    MYSQL_PASSWORD=''
    MYSQL_CURSORCLASS='DictCursor'
    MYSQL_DB='authentication'
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'varshneysanidhya@gmail.com'
    MAIL_PASSWORD = 'nisd uciv ajif sppw'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = 'varshneysanidhya@gmail.com'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SESSION_PERMANENT=False