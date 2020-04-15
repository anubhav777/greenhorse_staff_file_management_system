from flask import Flask, request, jsonify,send_file,Response,send_from_directory,render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from werkzeug.security import generate_password_hash,check_password_hash
import jwt
import datetime
from datetime import date
from functools import wraps
import docx2txt
from flask_cors import CORS
import boto3
import magic
from flask_cors import CORS,cross_origin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail,Message
from collections import Counter
import socket
from getmac import get_mac_address
app= Flask(__name__)
CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'
db=SQLAlchemy(app)
ma=Marshmallow(app)
upload_folder="./uploads"
CORS(app)
s3=boto3.client('s3')

basedir=os.path.abspath(os.path.dirname(__file__))

app.config.from_object('config.Development')
print(app.config['MAIL_SERVER'])
# m = magic.from_file('./Users/2.jpg', mime=True)

# print(m)

# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'db.sqlite')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
# app.config['MAIL_SERVER']='imap.gmail.com'
# app.config['MAIL_PORT']=587
# app.config['MAIL_USE_TLS']=True
# app.config['MAIL_USERNAME']='magaranub@gmail.com'
# app.config['MAIL_PASSWORD']='jimmy_@$'
# app.config['ALLOWED_PICTURE_EXTENSION']=['JPEG',"JPG"]
mail=Mail(app)

key='secret'
# app.config['SECRET']='secret'
app.config['ALLOWED_DATE']=[]
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

def token(f):
    @wraps(f)
    def decoratoe(*args,**kwargs):
        token=None

        if 'x-access-token' in request.headers:
            token=request.headers['x-access-token']
        
        if not token:
            return'token not validate'

        try:
            userid=jwt.decode(token,key)
            
            new_user=Signup.query.filter_by(id=userid['id']).first()

            currentuser=new_user.id
            
        
        except :
            return 'token not valid'
        
        return f(currentuser,*args,**kwargs)
    return decoratoe

newarr=[]
def time():
    new_time=datetime.datetime.now()
    current_time=new_time.strftime("%H:%M")
    today=date.today()
    registered_time=str(current_time)+" "+str(today)
    return registered_time

def time_only():
    new_time=datetime.datetime.now()
    current_time=new_time.strftime("%H:%M")
    return str(current_time)
# print(time_only())
def weekly():
    newdate=date.today()
    week_ago=newdate - datetime.timedelta(days=7)
    count=0
    
    while (count <=7):
        new_week=newdate - datetime.timedelta(days=count)
        formatted_date=new_week.strftime('%Y-%m-%d')
       
        app.config['ALLOWED_DATE'].append(formatted_date)
        
        count+=1
    return 'hi'

def generate_token(user_email,expiry_time=300):
    s=Serializer(app.config['SECRET'],expiry_time)
    new_user=Signup.query.filter_by(email=user_email).first()
    if not new_user:
        return False
    print(new_user.id)
    token=s.dumps({'user_id':new_user.id}).decode('UTF-8')
    return token

def send_email(token,email,condition):
    msg=None
    if condition == 'verification':
        msg=Message('Account Verification',sender='noreply@demo.com',recipients=[email])
        msg.body=f''' to verify your account please click the link below
        http://localhost:3000/verifier?tk={token}
        
        '''
    
    else:
        msg=Message('Password Reset Settings',sender='noreply@demo.com',recipients=[email])
        msg.body=f''' to reset your password please visit the link below
        http://localhost:3000/confirm?tk={token}
        If you have not requested please leave as it is
        '''
    mail.send(msg)
def token_decoder(token):
    s=Serializer(app.config['SECRET'])
    uid=None
    try:
        uid=s.loads(token)['user_id']
        print(uid)
    except:
        return False
    return uid
# tok=generate_token('genjilama007@gmail.com')
# print(type(token_decoder(tok)))

def makefolder(fgh):
    path="./%s"%fgh
    if not os.path.exists(path):
        os.mkdir(fgh)
        return(path)
    else:
            print('path already created')
            return (path)
app.config['ALLOWED_IMAGE_EXTENSION']=['DOCX','PDF']
def allowed_image(file):
 
    filename=str(file)
    print(filename)
    
    if not "." in filename:
        print(1)
        return False
    
    ext=filename.rsplit(".",1)[1]

    if ext.upper() in app.config['ALLOWED_IMAGE_EXTENSION']:
        return True
    else:
        print(2)
        return False

def file_checker(filename,filetype):
    file_check=None
    if filetype == "document":
        file_check=Filesdb.query.filter_by(filename=filename).first()
        print('document')
    elif filetype == "picture":
        new_filename=f"Users/{filename}"
        file_check=Signup.query.filter_by(picturepath=new_filename).first()
    
    if not file_check:
        return True
    else:
        return False
def profile_checker(path_name):
    new_path=Signup.query.filter_by(picturepath=path_name).first()
    path_split=path_name.split("/",2)
    print(path_split[1])
    new_filename=str(path_split[1])

    if new_path:
        return False
    if not "." in new_filename:
        return False
    new_split=new_filename.rsplit(".",2)
    file_check=new_split[1]
    print(file_check)
    if file_check.upper() in app.config['ALLOWED_PICTURE_EXTENSION']:
        return True
    else:
        return False


def upload_file(file_name, bucket):
    object_name = file_name
    print(object_name)
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)

    return response 
def user_mac(new_ip=''):
    new_mac=get_mac_address(ip=new_ip)
    return new_mac
def ip_adress():
    inet_ip=None
    new_socket=socket.gethostname()
    new_ip=socket.gethostbyname_ex(new_socket)
    all_ip=new_ip[2]
    if len(all_ip) > 1:
        inet_ip=all_ip[(len(all_ip)-1)]
    else:
        inet_ip=all_ip
    mac_ad=user_mac(inet_ip)
    print(mac_ad)
    return mac_ad

print(ip_adress())
@app.route('/signup',methods=['POST'])
def register():
    # print(request.json)
    email=request.form['email']
    fullname=request.form['fullname']
    address=request.form['address']
    phone=request.form['phone']
    new_password=request.form['password']
    usertype=request.form['usertype']
    hash_password=generate_password_hash(new_password,method='sha256')
    password=hash_password
    registertime=time()
    is_verified='False'
    filepath=request.files['file']
    filename=filepath.filename
    picturepath=f"Users/{filename}"
    print(email,picturepath)
    path=makefolder('Users')
    print(path)
    validator=Signup.query.filter_by(email=email).first()

    if validator:
        return ({'status':'This email has already been registered'})
    if not profile_checker(picturepath):
        return({'status':'the pictiure seems to be in wrong format or seems to have been uploaded'})
    filepath.save(os.path.join(path,filename))
    upload_file(picturepath,'greenhorse')
    new_data=Signup(email,fullname,address,phone,password,usertype,registertime,is_verified,picturepath)
    db.session.add(new_data)
    db.session.commit()

    # return signup_schema.jsonify(new_data)
    return({'hi':'hi'})

@app.route('/getuser/<id>',methods=['GET'])
@token
def getuser(currrentuser,id):
    user=Signup.query.filter_by(id=currrentuser).first()
    if not user:
        return 'you cannot perfom this action'

    if user.usertype != "admin":
        print(user.id)
        new_user=Signup.query.get(user.id)
        return signup_schema.jsonify(new_user)
    
    
    new_user=Signup.query.get(id)
    return signup_schema.jsonify(new_user)
@app.route('/getalluser',methods=["GET"])
@token
def getalluser(currentuser):
    new_user=Signup.query.filter_by(id=currentuser).first()

    if not new_user:
        return 'you cannot perfom this action'

    if new_user.usertype != "admin":
        return 'you cannot perfom this action'

    newuser=Signup.query.all()
    result=signups_schema.dump(newuser)


    return jsonify({'data':result,'user':new_user.usertype})
@app.route('/tryuser',methods=["GET"])
def gettryuser():
   
    newblauser=Signup.query.all()
    result=signups_schema.dump(newblauser)

    return jsonify(result)

@app.route('/updateuser/<uid>',methods=['PUT'])
@token
def updateuser(currentuser,uid):
    user=None
    new_usertype=None
    new_user=Signup.query.filter_by(id=currentuser).first()
    
    if not new_user:
        return {'please login first'}

    if new_user.usertype == "staff":
        user=Signup.query.filter_by(id=new_user.id).first()
        new_usertype='staff'
    if new_user.usertype == "admin":
        user=Signup.query.filter_by(id=uid).first()
        new_usertype=request.json['usertype']

    curr_user=user.id
    email=request.json['email']
    fullname=request.json['fullname']
    address=request.json['address']
    phone=request.json['phone']

    user.email=email
    user.fullname=fullname
    user.address=address
    user.phone=phone
    user.usertype=new_usertype

    
    
    db.session.commit()

    return jsonify({'status':'sucess'})

@app.route('/updateusertype/<id>', methods=['PUT'])
@token
def updateusertype(currentuser,id):
    newuser=Signup.query.filter_by(id=currentuser).first()

    if not newuser:
        return 'you cannot perfom this action'

    if newuser.usertype != "admin":
        return('you do not have permission')
    
    updt_user=Signup.query.get(id)

    usertype=request.json['usertype']
    updt_user.usertype=usertype

    db.session.commit()

    return signup_schema.jsonify(updt_user,{'status':'sucess'})


@app.route('/deleteuser/<id>',methods=['DELETE'])
@token
def deleteuser(currentuser,id):
    curr_user=Signup.query.filter_by(id=currentuser).first()
    print(curr_user.usertype)

    if curr_user.usertype != 'admin':
        return('you do not have permission')
        
    newuser=Signup.query.get(id)
    db.session.delete(newuser)
    db.session.commit()

    return signup_schema.jsonify(newuser)
    
    
def loginchecker(uid):
    new_date=date.today()
    new_login=Logindb.query.filter_by(date=new_date,userid=uid).all()

    if not(new_login):
    
            logged_in=time_only()
            current_status=True
            userid=uid
            result=Logindb(logged_in,current_status,userid)
            db.session.add(result)
            db.session.commit()
   
    print(new_login)
    return True

# print(loginchecker(2))
@app.route('/login')
def login():
    auth= request.authorization
    print(auth.password)
    
   

    if not auth:
        return make_response('Could not verify',401,{'WWW-Authenticate':'Basic realm="Login Required"'})

    user = Signup.query.filter_by(email=auth.username).first()

    if not user:
        return make_response('Could not verify',401,{'WWW-Authenticate':'Basic realm="Login Required"'})
    if user.is_verified != "True":
        return({'status':'Your account is not verified'})

    if check_password_hash(user.password,auth.password):
        obj={'id':user.id,'exp':datetime.datetime.utcnow()+datetime.timedelta(hours=4)}
        data=jwt.encode(obj,key)
        loginchecker(user.id)
       
        return jsonify({'token':data.decode('UTF-8'),'status':'sucess','usertype':user.usertype,'filepath':user.picturepath,'userid':user.id})


    return make_response('Could not verify',401,{'WWW-Authenticate':'Basic realm="Login Required"'})


def graph_counter(dt,args,kwargs):
    overall_data=None
    count=0
    new_user=Signup.query.filter_by(id=kwargs).first()
    if args == 'file':
        if new_user.usertype == 'admin':
            overall_data = Filesdb.query.filter_by(date=str(dt)).all()
        else:
            overall_data = Filesdb.query.filter_by(userid=new_user.id,date=str(dt)).all()
        

    elif args == 'question':
         if new_user.usertype == 'admin':
            overall_data=Question.query.filter_by(date=str(dt)).all()
         else:
             overall_data=Question.query.filter_by(userid=new_user.id,date=str(dt)).all()
    

    count=len(overall_data)
    return count

def array_sorter(args,kwargs,rev=False):
    new_value=sorted(args, key=lambda k: k[kwargs],reverse=rev)
    return new_value
# print(graph_counter('2020-04-06','file',13))
def date_filter(args,kwargs,):
    overall_data=None
    new_array=[]
    stats=None
    final_array=[]
    new_arr=[]

    if kwargs == 'file':
            overall_data = Filesdb.query.filter_by(date=str(args)).all()
            stats='filedb'
        
    elif kwargs == 'question':
            overall_data=Question.query.filter_by(date=str(args)).all()
            stats='signup'

    for i in range(len(overall_data)):
        total=0

        for j in range(len(overall_data)):

            if overall_data[i].userid == overall_data[j].userid:
                total+=1

        if overall_data[i].userid not in new_arr:

            new_arr.append(overall_data[i].userid)
            if stats == 'filedb':
                new_obj={'userid':overall_data[i].userid,'total':total,'y_axis':overall_data[i].filedb.fullname}
                final_array.append(new_obj)
            else:
                new_obj={'userid':overall_data[i].userid,'total':total,'y_axis':overall_data[i].signup.fullname}
                final_array.append(new_obj)
    sorted_array=array_sorter(final_array,'total',True)
    

    return sorted_array

def overall_filter(kwargs,weekly=False):
    overall_data=kwargs
    final_array=[]
    new_arr=[]
    print(weekly)
            

    for i in range(len(overall_data)):
        total=0
       

        for j in range(len(overall_data)):

            if overall_data[i].date == overall_data[j].date:
                total+=1

        if overall_data[i].date not in new_arr:
            new_date=str(overall_data[i].date)
            year,month,day=new_date.split("-")
            day_name=datetime.date(int(year), int(month), int(day))
            new_day=day_name.strftime("%A")
            short_form=new_day[:3]
            # print(short_form)
            new_arr.append(overall_data[i].date)
            new_obj={'date':overall_data[i].date,'total':total,'y_axis':short_form}
            final_array.append(new_obj)
            
    new_sort=array_sorter(final_array,'date')
    print(new_sort)

    return new_sort

    

def all_file():
    files= Filesdb.query.all()
    return files
def all_questions():
    questions=Question.query.all()
    return questions
def month_filter(kwargs,newmonth=False,week=False):
    array=kwargs
    new_array=[]
    new_week=None
    weekly()
    if week == '4':
        new_week=(( 7 * int(week)) + 4)
    else:
        new_week=( 7 * int(week))
    
    for i in range(len(array)):
        new_date=str(array[i].date)
        if not newmonth:
            
            if new_date in app.config['ALLOWED_DATE']:
                new_array.append(array[i])
        
        
        else:
            year,month,day=new_date.split("-")  
            if month == newmonth:
                if int(day) >((7 * int(week)) - 7) and int(day) <= new_week: 
                    new_array.append(array[i]) 
    
    final_array=overall_filter(new_array)
    return final_array


# print(month_filter(all_file()))
# weekly()

@app.route('/graph',methods=['GET'])
@token
def graph(currentuser):
    signup=Signup.query.filter_by(id=currentuser).first()
    if not signup:
        return ({'status':'you do not have this permission'})
    dats=request.args.get('stats')
    if dats:
        
        if dats == 'date':
            print(dats)
            new_date=request.headers['curr_date']
            new_methods=request.headers['send_methods']
            data_toreturn=None
            if new_methods == 'all':
                files=date_filter(new_date,'file')
                questions=date_filter(new_date,'question')
                return ({'file':files,'question':questions,'title':'User Report'})
            elif new_methods == 'file':
                data_toreturn=date_filter(new_date,'file')
            else:
                data_toreturn=date_filter(new_date,'question')
            return ({'data':data_toreturn,'title':'User Report'})
        elif dats == 'overall':
            new_methods=request.headers['send_methods']
            new_file=all_file()
            new_question=all_questions()
            data_toreturn=None
            if new_methods == 'all':
                files=month_filter(new_file)
                questions=month_filter(new_question)
                return ({'file':files,'question':questions,'title':'Overall Report'})
            elif new_methods == 'file':
                data_toreturn=month_filter(new_file)
            else:
                print(new_methods)
                data_toreturn=month_filter(new_question)
            return ({'data':data_toreturn,'title':'Overall Report'})
            
        elif dats == 'month':
            new_methods=request.headers['send_methods']
            new_file=all_file()
            new_question=all_questions()
            month=request.headers['months']
            day=request.headers['days']
            data_toreturn=None
            if new_methods == 'all':
                files=month_filter(new_file,month,day)
                questions=month_filter(new_question,month,day)
                return ({'file':files,'question':questions,'title':'Weekly Report'})
            elif new_methods == 'file':
                data_toreturn=month_filter(new_file,month,day)
            else:
                data_toreturn=month_filter(new_question,month,day)
            return ({'data':data_toreturn,'title':'Weekly Report'})
            

        
    else:
        print(dats)
        newdate=date.today()
        login_db=Logindb.query.filter_by(date=newdate).all()
        login_count=0
        file_count=graph_counter(newdate,'file',signup.id)
        question_count=graph_counter(newdate,'question',signup.id)
        target=None
        
    
        print(file_count,question_count)

        for i in range(len(login_db)):
            if login_db[i].loguser.usertype == "staff":
                login_count+=1

        print(login_count)
        if signup.usertype == 'admin':
            target=(login_count * 60)
        else:
            target=60
        return({'questions':question_count,'file':file_count,'loginneduser':login_count,'target':target})

verifier=False
@app.route('/addlink',methods=['POST'])
@token
def addlink(currentuser):

 
    global verifier
    curr_user=Signup.query.filter_by(id=currentuser).first()
    data=None
    if not curr_user:
        return "you cannot perform this action one"
    print(curr_user.usertype)
    if curr_user.usertype != "staff" and (curr_user.usertype) != "admin":
        return ({'status':"you cannot perform this action"})
  


   
    status=request.json['status']
    linkname=request.json['linkname']
    date=date.today()
    userid=curr_user.id
    process=request.json['process']
    print(linkname)
    if process == "Check": 
    
        link_validator=Question.query.filter_by(linkname=linkname).first()
    

        
        if link_validator:
            ret=link_validator.signup.fullname
            newdata={'upload':'uploaded by %s'%ret}
            data=newdata
            
            
            return jsonify({'upload':'uploaded by %s'%ret,'status':'done'})
        else :
            verifier=True
            
            return jsonify({'return':'not uploaded'})


    # else: 
    if process == 'Add':
        
        if not verifier:
            return jsonify({'not verified'})

        newlink=Question(status,linkname,date,userid)
        db.session.add(newlink) 
        db.session.commit()
        # new_link=question_schema.jsonify(newlink)
        # data=new_link

        return jsonify({'status':'uploaded'})


@app.route('/getallquestion/<stats>',methods=['GET'])
@token
def getallquestion(currentuser,stats):

    user=Signup.query.filter_by(id=currentuser).first()
    array=[]
    if not user:
        return 'you cannot perform this action'
    
    if user.usertype != "admin":
        staff_question=user.questions.all()
        
        
        tryo=Question.query.filter_by(userid=currentuser).all()
        res=questions_schema.dump(tryo)
        # for i in range(len(staff_question)):
        #     print(staff_question[i].id)


            # tryop=Question.query.get(staff_question[i].id)
            # trytwo=question_schema.jsonify(tryop)
            # res.update(trytwo)
            # print(res)
            
        return jsonify({'data':res,'user':user.usertype})

    all_question=Question.query.all()
    print(stats)
    
    for i in range(len(all_question)):
        
         if stats == "week":
             new_date=all_question[i].date
             old_split=new_date.split(" ",2)
             new_split=old_split[1]
             if new_split in app.config['ALLOWED_DATE']:
               new_object={'id':all_question[i].id,'status':all_question[i].status,'linkname':all_question[i].linkname,'date':all_question[i].date,'user':all_question[i].signup.fullname,'uid':all_question[i].userid}
               array.append(new_object)

        
         new_object={'id':all_question[i].id,'status':all_question[i].status,'linkname':all_question[i].linkname,'date':all_question[i].date,'user':all_question[i].signup.fullname,'uid':all_question[i].userid}
         array.append(new_object)

    
    result=questions_schema.dump(all_question)
    
    return jsonify({'data':array,'user':user.usertype})

@app.route('/getquestion/<ids>',methods=["GET"])
@token
def getquestion(currentuser,ids):
    user=Signup.query.filter_by(id=currentuser).first()

    if not user:
        return 'you cannot perform this action'

    if user.usertype != 'admin':
        return 'you cannot perform this action'

    result=Question.query.get(ids)
    bla=Question.query.filter_by(id=ids).first()
 
    return question_schema.jsonify(result)

@app.route('/deletequestion/<id>',methods=['DELETE'])
@token
def deletequestion(currentuser,id):
    user=Signup.query.filter_by(id=currentuser).first()

    if not user:
        return 'you cannot perform this action'

    if user.usertype != 'admin':
        return 'you cannot perform this action'
    
    result=Question.query.get(id)

    db.session.delete(result)
    db.session.commit()

    return question_schema.jsonify(result)


@app.route('/updatequestion/<id>',methods=["PUT"])
@token
def updatequestion(currentuser,id):
    user=Signup.query.filter_by(id=currentuser).first()

    if not user:
        return 'you cannot perform this action'

    if user.usertype != 'admin':
        return 'you cannot perform this action'

    status=request.json['status']
    linkname=request.json['linkname']
    date=time()
    userid=request.json['userid']

    update_question = Question.query.get(id)

    update_question.status = status
    update_question.linkname=linkname
    update_question.data=time()
    update_question.userid=userid

    db.session.commit()

    return question_schema.jsonify(update_question)
    


def word_count(filename):
    file=docx2txt.process(filename)
    file=file.replace('.','')
    file=file.replace('\n',' ')


    spl=file.split(" ")
    bla=''.join(file).split()
    length=len(bla)
    return str(length)
 
def link_validatere(link):
    link_checker=Question.query.filter_by(linkname=link).first()

    if link_checker:
        return True
    else:
        return False
def duplicate_link(link,files):
    link_checker=Filesdb.query.filter_by(url=link).first()
   

    if link_checker:
        return False
    
    else:
        return True

@app.route('/upload',methods=['POST'])
@token
def upload(currentuser):
    res=request.files.getlist("file")
    user=Signup.query.filter_by(id=currentuser).first()
  
    new_path=makefolder(user.fullname)
    check_value=0
    main_array=[]
    new_date=date.today()
    today=new_date.strftime('%Y-%m-%d')
    print(len(res))
    if len(res) == 0:
        return({'data': 'please enter file to be uploaded'})
    for i in range(len(res)):
        url=request.form['url']
        new_filename="%s %s"%(today,res[i].filename)
        print(new_filename)
        print(res[i].filename,url)
        link_check=link_validatere(url)
        if not link_check:
            return ({'data':'Sorry the link is invalid'})
        if not duplicate_link(url,new_filename):
            return({'data':'The link or file seems to be duplicate please check your link'})
        if not user:
            return 'you cannot perform this action'

        if res[i].filename == "":
            return ({'data':'file name is empty'})

        if not allowed_image(res[i].filename):
            print('err')
            return({'data':'file is not valid'})
      
        if not file_checker(new_filename,'document'):
            print('found')
            return({'data':'file already added'})
       

        
        res[i].save(os.path.join(new_path,new_filename))
        # res[i].save(os.path.join(upload_folder,res[i].filename))
        # s3_resource=boto3.resource('s3')
        # my_bucket=s3_resource.Bucket('greenhorse')
        # s3.put_object(Bucket='greenhorse',Body=res[i],Key=res[i].filename)
        upload_file(f"{user.fullname}/{new_filename}",'greenhorse')
      
        total_wordcount=word_count(new_path+"\%s"%new_filename)
        main_array.append({"name":res[i].filename,'wordcount':total_wordcount})
        check_value+=1
        filename=new_filename
        url=request.form['url']
        filepath=new_path+"\%s"%new_filename
        status=request.form['status']
        wordcount=total_wordcount
        curr_date=date.today()
        userid=user.id

        result=Filesdb(filename,url,filepath,status,wordcount,curr_date,userid)
        db.session.add(result)
        db.session.commit()
        print(main_array)

        return({'status':'file uploaded sucessfully','wordcount':wordcount})
    
    print(main_array)
    return({'status':'file uploaded sucessfully'})

    # print(res.filename)
    # return jsonify({'hi':'hi'})



@app.route('/try',methods=["POST"])
def getbla():
    link=request.json['link']
    link_checker=Question.query.filter_by(linkname=link).first()

    if link_checker:
        print('corr')
    else:
        print('wrong')


    
    return 'hi'
@app.route('/getallfile/<stats>',methods=['GET'])
@token
def getallfile(currentuser,stats):
    user=Signup.query.filter_by(id=currentuser).first()
    array=[]
    try_array=[]
   
    if not user:
        return jsonify({'you cannot perform this action'})
    if user.usertype != "admin":
        data=Filesdb.query.filter_by(userid=user.id).all()
        result=filesdbs_schema.dump(data)
        return jsonify({'data':result,'user':user.usertype})
        
        
        
    data=Filesdb.query.all()
    for i in range(len(data)):
       if stats == "week":
             new_date=data[i].date
             old_split=new_date.split(" ",2)
             new_split=old_split[1]
             if new_split in app.config['ALLOWED_DATE']:
               new_object={'id':data[i].id,'filename':data[i].filename,'filepath':data[i].filepath,'status':data[i].status,'url':data[i].url,'wordcount':data[i].wordcount,'date':data[i].date,'user':data[i].filedb.fullname,'uid':data[i].userid}
               array.append(new_object)

        
       if stats == "overall" or stats =="date":
            new_object={'id':data[i].id,'filename':data[i].filename,'filepath':data[i].filepath,'status':data[i].status,'url':data[i].url,'wordcount':data[i].wordcount,'date':data[i].date,'user':data[i].filedb.fullname,'uid':data[i].userid}
            array.append(new_object)

       if stats != "overall" and stats != "date" and stats != "week":
        #    print(type(stats))
        new_stats=int(stats)
        # print(new_stats)
        if new_stats == data[i].userid:
            new_object={'id':data[i].id,'filename':data[i].filename,'filepath':data[i].filepath,'status':data[i].status,'url':data[i].url,'wordcount':data[i].wordcount,'date':data[i].date,'user':data[i].filedb.fullname,'uid':data[i].userid}
            array.append(new_object)
            print(i,len(data))
            if i == len(data):
                stats="user"


        

    print(len(array))
    result=filesdbs_schema.dump(data)
    return jsonify({'data':array,'user':user.usertype,'stats':stats})



    

@app.route('/getfile/<id>',methods=['GET'])
@token
def getfile(currentuser,id):
    user=Signup.query.filter_by(id=currentuser).first()
    if not user:
        return jsonify({'you cannot perform this action'})


    result=Filesdb.query.get(id)
    # arr={'id':result.id,'filename':result.filename,'url':result.url,'status':result.status,'wordcount':result.wordcount,'userid':result.filedb.fullname}
    # print(arr)
    return filesdb_schema.jsonify(result)


@app.route('/updatefile/<ids>',methods=["PUT"])
@token
def updatefile(currentuser,ids):
    user=Signup.query.filter_by(id=currentuser).first()

    if user.usertype != "admin":
        return ({"you cannot perform this action"})
       
   
    filename=request.json['filename']
    url=request.json['url']
    status=request.json['status']
    wordcount=request.json['wordcount']
    userid=request.json['userid']

    
    print(request.json['wordcount'])
    update_file=Filesdb.query.get(ids)
    update_file.filename=filename
    update_file.url=url
    update_file.status=status
    update_file.wordcount=wordcount
    update_file.userid=userid
    db.session.commit()

    return jsonify({'data':'updated sucessfully','status':'sucess'})

@app.route('/deletefile/<id>',methods=['DELETE'])
@token
def deletefile(currentuser,id):
    user=Signup.query.filter_by(id=currentuser).first()
    
    if user.usertype != "admin":
        return ({"you cannot perform this action"})


    delete_file=Filesdb.query.get(id)
    db.session.delete(delete_file)
    db.session.commit()

    return jsonify({'data':'sucessfully delted'})

@app.route('/usergraph/<id>',methods=['GET'])
@token
def usergarph(currentuser,id):
    user=Signup.query.filter_by(id=currentuser).first()

   
    if not user:
        return jsonify({'you cannot perform this action'})
    if user.usertype != "admin":
        return jsonify({'you cannot perform this action'})

    newid=int(id)
    array=[]
    data=Filesdb.query.filter_by(userid=newid).all()
    
    for i in range(len(data)):
        splt_date=data[i].date.split(" ",2)
        new_date=splt_date[1]
        print(new_date)
        new_object={'id':data[i].id,'filename':data[i].filename,'date':new_date,'uid':data[i].userid,'user':data[i].filedb.fullname}
        array.append(new_object)
    print(array)
    result=filesdbs_schema.dump(data)
    return jsonify({'data':array,'user':user.usertype})

@app.route('/muliple',methods=['POST'])
def muliple():
    res=request.files.getlist("file")
    ab=0
    for i in range(len(res)):
        ab+=1
        print(res[i].filename)
    
    print(ab)
    return({'hi':'ho'})
# def download_file(filename,bucket):
#     s3_resource=boto3.resource('s3')
#     output=f"./downloads/bla.docx"
#     print(output)
#     s3_resource.Bucket(bucket).download_file(f"mainadmin/{filename}",output)
#     return output

@app.route('/download/<path:filepath>',methods=['GET'])

def download(filepath):
    new_filepath=None
    filetype=None
    new_mimetype=None
    print(filepath)    
    if '/' in filepath:
        new_path=filepath.split("/",2)
        new_filepath=new_path[1]
    else:
        new_filepath=filepath
    file_split=new_filepath.rsplit(".",2)
    new_filetype=file_split[1]
    if new_filetype.upper() in app.config['ALLOWED_IMAGE_EXTENSION']:
        filetype='document'
        new_mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif new_filetype.upper() in app.config['ALLOWED_PICTURE_EXTENSION']:
        filetype='picture'
        new_mimetype="image/jpeg"

    print(filetype)
    print(new_filepath)
    if file_checker(new_filepath,filetype):
        return({"status":'No such files please check it again'})
    print(new_mimetype)
    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket('greenhorse')
    file_obj=my_bucket.Object(filepath).get()

    r= Response(file_obj['Body'].read(),
                    mimetype=new_mimetype,
                    headers={"Content-Disposition":"attachement;filename={}".format(filepath)})
    r.headers.add("Access-Control-Allow-Origin", "*")
    r.headers.add('Access-Control-Expose-Headers','*')
    print(type(r))
    
    return r
    
@app.route('/resetpassword',methods=['POST'])
def resetpassword():
    email=request.json['email']
    print(email)
    if email == '':
        return ({'status':'please provide email'})
    tok=generate_token(email)
    print(tok)
    if not tok:
        return ({'status':'please enter valid email'})
    send_email(tok,email,'reset')
    return({'status':'Please check your email link has been sent'})

@app.route('/verification',methods=['POST'])
def verfification():
    email=request.json['email']
    print(email)
    if email == '':
        return ({'status':'please provide email'})
    tok=generate_token(email)
    print(tok)
    if not tok:
        return ({'status':'please enter valid email'})
    send_email(tok,email,'verification')
    return({'status':'Please check your email verfication link has been sent'})

@app.route('/confirmverification/<token>',methods=['GET'])
def confirmverification(token):
    user_id=token_decoder(token)
    if not user_id:
        return ({'status':'token has expired'})
    new_user=Signup.query.filter_by(id=user_id).first()
    new_user.is_verified='True'
    db.session.commit()
    return({'status':'account sucessfully verified'})
    

@app.route('/confirmpassword/<token>',methods=['POST'])
def confirmpassword(token):
    password=request.json['password']
    confirm_password=request.json['confirmpassword']

    if password != confirm_password:
        return ({'status':'confirm password'})
    user_id=token_decoder(token)
    if not user_id:
        return ({'status':'token has expired'})
    new_user=Signup.query.filter_by(id=user_id).first()
    hash_password=generate_password_hash(password,method='sha256')
    new_user.password=hash_password
    db.session.commit()
    return({'status':'password sucessfully updated'})
@app.route('/mac',methods=['GET'])
def send_mac():
    new_mac=ip_adress()
    return ({'data':new_mac})
  
Bootstrap(app)
@app.route('/')
def index():
    return render_template('index.html')
if __name__ =="__main__":
    app.run(debug=True)
    