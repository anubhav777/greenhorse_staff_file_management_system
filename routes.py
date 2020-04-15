from app import app,mail
from flask import request,jsonify,send_file,Response,render_template
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash,check_password_hash
import jwt
import boto3
import datetime
from datetime import date
from models import *
from file import *
key=app.config['SECRET']

@app.route('/signup',methods=['POST'])
def register():
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
    
    path=makefolder('Users')
    
    validator=Signup.query.filter_by(email=email).first()

    if validator:
        return ({'status':'error','noty':'This email has already been registered'})
    if not profile_checker(picturepath):
        return({'status':'error','noty':'the pictiure seems to be in wrong format or seems to have been uploaded'})
    filepath.save(os.path.join(path,filename))
    upload_file(picturepath,'greenhorse')
    new_data=Signup(email,fullname,address,phone,password,usertype,registertime,is_verified,picturepath)
    db.session.add(new_data)
    db.session.commit()
    remove_file=os.path.join(path,filename)
    file_remove(remove_file)
    # return signup_schema.jsonify(new_data)
    return({'status':'success','noty':'Sucessfully registered'})

@app.route('/getuser/<id>',methods=['GET'])
@token
def getuser(currrentuser,id):
    user=Signup.query.filter_by(id=currrentuser).first()
    if not user:
        return  ({'status':'error','noty':'you cannot perfom this action'})

    if user.usertype != "admin":
        
        new_user=Signup.query.get(user.id)
        return signup_schema.jsonify(new_user)
    
    
    new_user=Signup.query.get(id)
    return signup_schema.jsonify(new_user)
@app.route('/getalluser',methods=["GET"])
@token
def getalluser(currentuser):
    new_user=Signup.query.filter_by(id=currentuser).first()

    if not new_user:
        return ({'status':'error','noty':'you cannot perfom this action'})

    if new_user.usertype != "admin":
        return  ({'status':'error','noty':'you cannot perfom this action'})

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

    return jsonify({'status':'success','noty':'User Sucessfully Updated'})

@app.route('/updateusertype/<id>', methods=['PUT'])
@token
def updateusertype(currentuser,id):
    newuser=Signup.query.filter_by(id=currentuser).first()

    if not newuser:
        return ({'status':'error','noty':'you cannot perfom this action'})

    if newuser.usertype != "admin":
        return ({'status':'error','noty':'you cannot perfom this action'})
    
    updt_user=Signup.query.get(id)

    usertype=request.json['usertype']
    updt_user.usertype=usertype

    db.session.commit()

    return signup_schema.jsonify(updt_user)


@app.route('/deleteuser/<id>',methods=['DELETE'])
@token
def deleteuser(currentuser,id):
    curr_user=Signup.query.filter_by(id=currentuser).first()
   

    if curr_user.usertype != 'admin':
        return ({'status':'error','noty':'you cannot perfom this action'})
        
    newuser=Signup.query.get(id)
    db.session.delete(newuser)
    db.session.commit()

   
    return jsonify({'status':'alert','noty':'User Sucessfully Deleted'})
    



@app.route('/login')
def login():
    auth= request.authorization
    
    
   

    if not auth:
        return ({'status':'error','noty':'you login credetials do not match'})

    user = Signup.query.filter_by(email=auth.username).first()

    if not user:
        return ({'status':'error','noty':'you login credetials do not match'})
    if user.is_verified != "True":
        return({'status':'error','noty':'Your account is not verified'})

    if check_password_hash(user.password,auth.password):
        obj={'id':user.id,'exp':datetime.datetime.utcnow()+datetime.timedelta(hours=4)}
        data=jwt.encode(obj,key)
        loginchecker(user.id)
       
        return jsonify({'token':data.decode('UTF-8'),'status':'success','usertype':user.usertype,'filepath':user.picturepath,'userid':user.id})


    return ({'status':'error','noty':'you login credetials do not match'})



@app.route('/graph',methods=['GET'])
@token
def graph(currentuser):
    users=False
    signup=Signup.query.filter_by(id=currentuser).first()
    if not signup:
        return  ({'status':'error','noty':'you cannot perfom this action'})
    if signup.usertype == 'staff':
        users=signup.id
    
    dats=request.args.get('stats')
    if dats:
        
        if dats == 'date':
            if users:
                return ({'status':'error','noty':'you cannot perfom this action'})
            
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
            new_file=all_file(users)
            new_question=all_questions(users)
            data_toreturn=None
            if new_methods == 'all':
                files=month_filter(new_file)
                questions=month_filter(new_question)
                return ({'file':files,'question':questions,'title':'Overall Report'})
            elif new_methods == 'file':
                data_toreturn=month_filter(new_file)
            else:
                
                data_toreturn=month_filter(new_question)
            return ({'data':data_toreturn,'title':'Overall Report'})
            
        elif dats == 'month':
            if users:
                return({'status':'you cannot perform this action'})
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
       
        newdate=date.today()
        login_db=Logindb.query.filter_by(date=newdate).all()
        login_count=0
        file_count=graph_counter(newdate,'file',signup.id)
        question_count=graph_counter(newdate,'question',signup.id)
        target=None
        
    
       

        for i in range(len(login_db)):
            if login_db[i].loguser.usertype == "staff":
                login_count+=1

       
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
        return  ({'status':'error','noty':'you cannot perfom this action'})
    
    if curr_user.usertype != "staff" and (curr_user.usertype) != "admin":
        return ({'status':'error','noty':'you cannot perfom this action'})
  


   
    status=request.json['status']
    linkname=request.json['linkname']
    new_date=date.today()
    userid=curr_user.id
    process=request.json['process']
  
    if process == "Check": 
    
        link_validator=Question.query.filter_by(linkname=linkname).first()
    

        
        if link_validator:
            ret=link_validator.signup.fullname
            newdata={'upload':'uploaded by %s'%ret}
            data=newdata
            
            
            return jsonify({'noty':'uploaded by %s'%ret,'status':'alert'})
        else :
            verifier=True
            
            return jsonify({'return':'Question is not uploaded'})


    # else: 
    if process == 'Add':
        
        if not verifier:
            return ({'status':'error','noty':'The Question is not verified'})

        newlink=Question(status,linkname,new_date,userid)
        db.session.add(newlink) 
        db.session.commit()
        # new_link=question_schema.jsonify(newlink)
        # data=new_link

        return jsonify({'status':'alert','noty':'The question is uploaded'})



@app.route('/getallquestion',methods=['GET'])
@token
def getallquestion(currentuser):

    user=Signup.query.filter_by(id=currentuser).first()
    array=[]
    if not user:
        return  ({'status':'error','noty':'you cannot perfom this action'})
    
    if user.usertype != "admin":
        staff_question=user.questions.all()
        
        
        tryo=Question.query.filter_by(userid=currentuser).all()
        res=questions_schema.dump(tryo)
            
        return jsonify({'data':res,'user':user.usertype})

    all_question=Question.query.all()
    
    for i in range(len(all_question)):
    
         new_object={'id':all_question[i].id,'status':all_question[i].status,'linkname':all_question[i].linkname,'date':all_question[i].date,'user':all_question[i].signup.fullname,'uid':all_question[i].userid}
         array.append(new_object)

    
    result=questions_schema.dump(all_question)
    
    return jsonify({'status':'success','data':array,'user':user.usertype})

@app.route('/getquestion/<ids>',methods=["GET"])
@token
def getquestion(currentuser,ids):
    user=Signup.query.filter_by(id=currentuser).first()
    extras=request.args.get('userid')

    if not user:
        return  ({'status':'error','noty':'you cannot perfom this action'})

    if user.usertype != 'admin':
        return  ({'status':'error','noty':'you cannot perfom this action'})
    
    if not extras:
        result=Question.query.get(ids)
        bla=Question.query.filter_by(id=ids).first()
    
        return question_schema.jsonify(result)
    
    all_question=Question.query.filter_by(userid=extras).all()

    new_result=[]
    for i in range(len(all_question)):
    
         new_object={'id':all_question[i].id,'status':all_question[i].status,'linkname':all_question[i].linkname,'dates':all_question[i].date,'user':all_question[i].signup.fullname,'uid':all_question[i].userid,'sno':(i+1)}
         new_result.append(new_object)

    
    return jsonify({'data':new_result})

    

@app.route('/deletequestion/<id>',methods=['DELETE'])
@token
def deletequestion(currentuser,id):
    user=Signup.query.filter_by(id=currentuser).first()

    if not user:
        return  ({'status':'error','noty':'you cannot perfom this action'})

    if user.usertype != 'admin':
        return  ({'status':'error','noty':'you cannot perfom this action'})
    
    result=Question.query.get(id)

    db.session.delete(result)
    db.session.commit()

    
    return  ({'status':'alert','noty':'the question is deleted sucessfully'})


@app.route('/updatequestion/<id>',methods=["PUT"])
@token
def updatequestion(currentuser,id):
    user=Signup.query.filter_by(id=currentuser).first()

    if not user:
        return  ({'status':'error','noty':'you cannot perfom this action'})

    if user.usertype != 'admin':
        return  ({'status':'error','noty':'you cannot perfom this action'})

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

    data=question_schema.jsonify(update_question)
    return  ({'status':'alert','noty':'the question is updated sucessfully','data':data})
    


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
    
    if len(res) == 0:
        return({'status':'error','noty': 'please enter file to be uploaded'})
    for i in range(len(res)):
        url=request.form['url']
        new_filename="%s %s"%(today,res[i].filename)
       
        link_check=link_validatere(url)
        if not link_check:
            return ({'status':'error','noty':'Sorry the link is invalid'})
        if not duplicate_link(url,new_filename):
            return({'status':'error','noty':'The link or file seems to be duplicate please check your link'})
        if not user:
            return  ({'status':'error','noty':'you cannot perfom this action'})

        if res[i].filename == "":
            return ({'status':'error','noty':'file name is empty'})

        if not allowed_image(res[i].filename):
           
            return({'status':'error','noty':'file is not valid'})
      
        if not file_checker(new_filename,'document'):
            
            return({'status':'error','noty':'file already added'})
       

        
        res[i].save(os.path.join(new_path,new_filename))
      
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
        
        remove_file=os.path.join(new_path,new_filename)
        file_remove(remove_file)
        return({'status':'alert','noty':'File uploaded Successfully','wordcount':wordcount})
    
    
    return({'status':'file uploaded sucessfully'})








    
    return 'hi'
@app.route('/getallfile',methods=['GET'])
@token
def getallfile(currentuser):
    user=Signup.query.filter_by(id=currentuser).first()
    array=[]
    try_array=[]
   
    if not user:
        return  ({'status':'error','noty':'you cannot perfom this action'})
    if user.usertype != "admin":
        data=Filesdb.query.filter_by(userid=user.id).all()
        result=filesdbs_schema.dump(data)
        return jsonify({'data':result,'user':user.usertype})
        
        
        
    data=Filesdb.query.all()
    for i in range(len(data)):
            new_object={'id':data[i].id,'filename':data[i].filename,'filepath':data[i].filepath,'status':data[i].status,'url':data[i].url,'wordcount':data[i].wordcount,'date':data[i].date,'user':data[i].filedb.fullname,'uid':data[i].userid}
            array.append(new_object)

   
    result=filesdbs_schema.dump(data)
    return jsonify({'data':array,'user':user.usertype})



    

@app.route('/getfile/<id>',methods=['GET'])
@token
def getfile(currentuser,id):
    user=Signup.query.filter_by(id=currentuser).first()
    extras=request.args.get('userid')
    if not user:
        return  ({'status':'error','noty':'you cannot perfom this action'})

    if not extras:
        result=Filesdb.query.get(id)
   
        return filesdb_schema.jsonify(result)
    all_question=Filesdb.query.filter_by(userid=extras).all()

    new_result=[]
    for i in range(len(all_question)):
    
         new_object={'id':all_question[i].id,'status':all_question[i].status,'linkname':all_question[i].filename,'dates':all_question[i].date,'user':all_question[i].filedb.fullname,'uid':all_question[i].userid,'sno':(i+1)}
         new_result.append(new_object)

    
    return jsonify({'data':new_result})


@app.route('/updatefile/<ids>',methods=["PUT"])
@token
def updatefile(currentuser,ids):
    user=Signup.query.filter_by(id=currentuser).first()

    if user.usertype != "admin":
        return  ({'status':'error','noty':'you cannot perfom this action'})
       
   
    filename=request.json['filename']
    url=request.json['url']
    status=request.json['status']
    wordcount=request.json['wordcount']
    userid=request.json['userid']

    
 
 
    update_file=Filesdb.query.get(ids)
    update_file.filename=filename
    update_file.url=url
    update_file.status=status
    update_file.wordcount=wordcount
    update_file.userid=userid
    db.session.commit()

    return jsonify({'noty':'File Updated sucessfully','status':'alert'})

@app.route('/deletefile/<id>',methods=['DELETE'])
@token
def deletefile(currentuser,id):
    user=Signup.query.filter_by(id=currentuser).first()
    
    if user.usertype != "admin":
        return  ({'status':'error','noty':'you cannot perfom this action'})


    delete_file=Filesdb.query.get(id)
    db.session.delete(delete_file)
    db.session.commit()

    return jsonify({'status':'alert','noty':'File sucessfully delted'})

@app.route('/usergraph/<id>',methods=['GET'])
@token
def usergarph(currentuser,id):
    user=Signup.query.filter_by(id=currentuser).first()

   
    if not user:
        return  ({'status':'error','noty':'you cannot perfom this action'})
    if user.usertype != "admin":
        return  ({'status':'error','noty':'you cannot perfom this action'})

    newid=int(id)
    array=[]
    data=Filesdb.query.filter_by(userid=newid).all()
    
    for i in range(len(data)):
        splt_date=data[i].date.split(" ",2)
        new_date=splt_date[1]
       
        new_object={'id':data[i].id,'filename':data[i].filename,'date':new_date,'uid':data[i].userid,'user':data[i].filedb.fullname}
        array.append(new_object)
   
    result=filesdbs_schema.dump(data)
    return jsonify({'data':array,'user':user.usertype})

@app.route('/muliple',methods=['POST'])
def muliple():
    res=request.files.getlist("file")
    ab=0
    for i in range(len(res)):
        ab+=1
       
    
    
    return({'hi':'ho'})


@app.route('/download/<path:filepath>',methods=['GET'])

def download(filepath):
    new_filepath=None
    filetype=None
    new_mimetype=None
   
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

    if file_checker(new_filepath,filetype):
        return({"status":'No such files please check it again'})
    
    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket('greenhorse')
    file_obj=my_bucket.Object(filepath).get()

    r= Response(file_obj['Body'].read(),
                    mimetype=new_mimetype,
                    headers={"Content-Disposition":"attachement;filename={}".format(filepath)})
    r.headers.add("Access-Control-Allow-Origin", "*")
    r.headers.add('Access-Control-Expose-Headers','*')
   
    
    return r
    
@app.route('/resetpassword',methods=['POST'])
def resetpassword():
    email=request.json['email']
    
    if email == '':
        return ({'status':'error','noty':'please provide email'})
    tok=generate_token(email)
    
    if not tok:
        return ({'status':'error','noty':'please enter valid email'})
    send_email(tok,email,'reset')
    return({'status':'alert','noty':'Please check your email link has been sent'})

@app.route('/verification',methods=['POST'])
def verfification():
    email=request.json['email']
    
    if email == '':
        return ({'status':'error','noty':'please provide email'})
    tok=generate_token(email)
  
    if not tok:
        return ({'status':'error','noty':'please enter valid email'})
    send_email(tok,email,'verification')
    return({'noty':'Please check your email verfication link has been sent','status':'alert','progress':'sucess'})

@app.route('/confirmverification/<token>',methods=['GET'])
def confirmverification(token):
    user_id=token_decoder(token)
    if not user_id:
        return ({'status':'error','noty':'token has expired'})
    new_user=Signup.query.filter_by(id=user_id).first()
    new_user.is_verified='True'
    db.session.commit()
    return({'status':'alert','noty':'account sucessfully verified'})
    

@app.route('/confirmpassword/<token>',methods=['POST'])
def confirmpassword(token):
    password=request.json['password']
    confirm_password=request.json['confirmpassword']
    if password != confirm_password:
        return ({'status':'error','noty':'Confirm password does not math with the password'})
    user_id=token_decoder(token)
    if not user_id:
        return ({'status':'error','noty':'token has expired'})
    new_user=Signup.query.filter_by(id=user_id).first()
    hash_password=generate_password_hash(password,method='sha256')
    new_user.password=hash_password
    db.session.commit()
    return({'status':'alert','noty':'password sucessfully updated'})
@app.route('/mac',methods=['GET'])
def send_mac():
    new_mac=ip_adress()
    return ({'data':new_mac})
  

@app.route('/')
def index():
    return  "<h1>Welcome to our server !!</h1>"
