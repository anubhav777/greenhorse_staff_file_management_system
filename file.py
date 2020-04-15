from models import *
from flask import request,send_file,Response,send_from_directory,render_template
import socket
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
from getmac import get_mac_address
from app import app,mail
key=app.config['SECRET']

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
    
    return mac_ad


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
        
    except:
        return False
    return uid


def makefolder(fgh):
    path="./%s"%fgh
    if not os.path.exists(path):
        os.mkdir(fgh)
        return(path)
    else:
           
            return (path)

def allowed_image(file):
 
    filename=str(file)
  
    
    if not "." in filename:
       
        return False
    
    ext=filename.rsplit(".",1)[1]

    if ext.upper() in app.config['ALLOWED_IMAGE_EXTENSION']:
        return True
    else:
       
        return False

def file_checker(filename,filetype):
    file_check=None
    if filetype == "document":
        file_check=Filesdb.query.filter_by(filename=filename).first()
       
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
  
    new_filename=str(path_split[1])

    if new_path:
        return False
    if not "." in new_filename:
        return False
    new_split=new_filename.rsplit(".",2)
    file_check=new_split[1]
 
    if file_check.upper() in app.config['ALLOWED_PICTURE_EXTENSION']:
        return True
    else:
        return False


def upload_file(file_name, bucket):
    object_name = file_name
   
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)

    return response 
def file_remove(args):
    os.remove(args)
    return 'done'

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

    return True



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

def date_filter(args,kwargs):
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
                new_obj={'userid':overall_data[i].userid,'total':total,'y_axis':overall_data[i].filedb.fullname,'date':overall_data[i].date}
                final_array.append(new_obj)
            else:
                new_obj={'userid':overall_data[i].userid,'total':total,'y_axis':overall_data[i].signup.fullname,'date':overall_data[i].date}
                final_array.append(new_obj)
    sorted_array=array_sorter(final_array,'total',True)
    

    return sorted_array

def overall_filter(kwargs,weekly=False):
    overall_data=kwargs
    final_array=[]
    new_arr=[]

            

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
          
            new_arr.append(overall_data[i].date)
            new_obj={'date':overall_data[i].date,'total':total,'y_axis':short_form}
            final_array.append(new_obj)
            
    new_sort=array_sorter(final_array,'date')
   

    return new_sort

    

def all_file(users=False):

    files=None
    if users:
        files=Filesdb.query.filter_by(userid=users).all()
    else:
        files= Filesdb.query.all()
 
    return files
def all_questions(users=False):
    questions=None
    if users:
        questions=Question.query.filter_by(userid=users).all()
    else:
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
