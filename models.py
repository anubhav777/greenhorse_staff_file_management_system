from app import db,ma
from datetime import date
class Signup(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(100))
    fullname=db.Column(db.String(100))
    address=db.Column(db.String(100))
    phone=db.Column(db.Integer)
    password=db.Column(db.String(100))
    usertype=db.Column(db.String(100))
    registertime=db.Column(db.String(100))
    is_verified=db.Column(db.String(100))
    picturepath=db.Column(db.String(100))
    questions=db.relationship('Question',backref='signup',lazy='dynamic')
    files=db.relationship('Filesdb',backref='filedb',lazy='dynamic')
    login=db.relationship('Logindb',backref='loguser',lazy='dynamic')

    def __init__(self,email,fullname,address,phone,password,usertype,registertime,is_verified,picturepath):
        self.email=email
        self.fullname=fullname
        self.address=address
        self.phone=phone
        self.password=password
        self.usertype=usertype
        self.registertime=registertime
        self.is_verified=is_verified
        self.picturepath=picturepath

class Question(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    status=db.Column(db.String(100))
    linkname=db.Column(db.String(100))
    date=db.Column(db.String(100))
    userid=db.Column(db.Integer,db.ForeignKey('signup.id'))

    def __init__(self,status,linkname,date,userid):
        self.status=status
        self.linkname=linkname
        self.date=date
        self.userid=userid
       
class Filesdb(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    filename=db.Column(db.String(100))
    url=db.Column(db.String(100))
    filepath=db.Column(db.String(100))
    status=db.Column(db.String(100))
    wordcount=db.Column(db.String(100))
    date=db.Column(db.String(100))
    userid=db.Column(db.Integer,db.ForeignKey('signup.id'))

    def __init__(self,filename,url,filepath,status,wordcount,date,userid):
        self.filename=filename
        self.url=url
        self.filepath=filepath
        self.status=status
        self.wordcount=wordcount
        self.date=date
        self.userid=userid


class Logindb(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    date=db.Column(db.Date,default=date.today())
    logged_in=db.Column(db.String(100))
    current_status=db.Column(db.Boolean,default=False)
    userid=db.Column(db.Integer,db.ForeignKey('signup.id'))

    def __init__(self,logged_in,current_status,userid):
        
        self.current_status=current_status
        self.logged_in=logged_in
        self.userid=userid

# class Miscallenous(db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     macaddress=db.Column()

class QuestionSchema(ma.Schema):
    class Meta:
        fields=('id','status','linkname','date','userid')
        
class SignupSchema(ma.Schema):
    class Meta:
        fields=('id','email','fullname','address','phone','password','usertype','registertime','is_verified','picturepath')

class FilesdbSchema(ma.Schema):
    class Meta:
        fields=('id','filename','url','filepath','status','wordcount','date','userid')

class LoginSchema(ma.Schema):
    class Meta:
        fields=('id','date','current_status','logged_in','userid')

signup_schema=SignupSchema()
signups_schema=SignupSchema(many=True)


question_schema=QuestionSchema()
questions_schema=QuestionSchema(many=True)

filesdb_schema=FilesdbSchema()
filesdbs_schema=FilesdbSchema(many=True)

login_schema=LoginSchema()
logins_schema=LoginSchema(many=True)
