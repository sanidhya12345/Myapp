from flask import Blueprint,render_template,redirect,request,session,jsonify,url_for
#from .models import Authentication,Notification,Master,Transaction,Services
from  flask_mail import Mail, Message
from . import db,mail
import random
import string
from sqlalchemy import text
from datetime import date,datetime
import json
from sqlalchemy import distinct

bp=Blueprint('main',__name__)
current_date = date.today()
otp_storage={}
otp_cache = {}


signup_storage={}


@bp.route('/send_otp',methods=['GET','POST'])
def send_otp():
    email=request.form['email']
    session['email']=email
    session['verify']=False
    session['usercode']=100000
    otp=generate_otp()
    otp_storage[email]=otp
    msg = Message('OTP for Authentication', recipients=[email])
    msg.body = f'Your OTP for authentication is: {otp}'
    try:
         mail.send(msg)
         return redirect("/spsignup")
    except Exception as e:
         return jsonify({'message': str(e)}), 500

@bp.route("/verify_otp",methods=['GET','POST'])
def verify_otp():
    email=session['email']
    otp_enter=request.form['otp']
    if email in otp_storage and otp_storage[email] == otp_enter:
        # Clear OTP after successful verification
        # users=Authentication.query.all()
        # for i in users:
        #     if i.email==email:
        #         session['name']=i.name
        session['verify']=True
        del otp_storage[email]
        return redirect("/spsignup")
    else:
        return jsonify({'message': 'Invalid OTP'}), 400
    

def generate_otp():
    otp = ''.join(random.choices(string.digits, k=6))
    return otp

@bp.route("/spsignuppage")
def spsignuppage():
    return render_template("spsignup.html",email="")

@bp.route("/spsignup",methods=['GET','POST'])
def spsignup():
    email=session.get('email')
    verify=session.get('verify')
    sp_code=session.get('usercode')
    if request.method=="POST":
        phone=request.form.get('phone')
        service_provider_name=request.form.get('oname')
        service_provider_estb_name=request.form.get('ename')
        service_provider_houseno=request.form.get('hno')
        service_provider_street_road=request.form.get('streetname')
        service_provider_locality_area_colony=request.form.get('locality')
        service_provider_major_landmark=request.form.get('landmark')
        service_provider_city_district_town=request.form.get('city')
        service_provider_state=request.form.get('states')
        service_provider_pincode=request.form.get('pincode')
        
        signup_storage['phone']=phone
        signup_storage['service_provider_name']=service_provider_name
        signup_storage['service_provider_estb_name']=service_provider_estb_name
        signup_storage['service_provider_houseno']=service_provider_houseno
        signup_storage['service_provider_street_road']=service_provider_street_road
        signup_storage['service_provider_locality_area_colony']=service_provider_locality_area_colony
        signup_storage['service_provider_major_landmark']=service_provider_major_landmark
        signup_storage['service_provider_city_district_town']=service_provider_city_district_town
        signup_storage['service_provider_state']=service_provider_state
        signup_storage['service_provider_pincode']=service_provider_pincode
        sp_code=sp_code+1
        return redirect("/services")
    return render_template("spsignup.html",email=email,verify=verify)


@bp.route("/signuptype")
def signuptype():
    return render_template("signuptype.html")

@bp.route("/logintype")
def logintype():
    return render_template("logintype.html")

@bp.route("/signup",methods=['GET','POST'])
def signup():
    cur=db.connection.cursor()
    userNameNotEnter=False
    passwordNotEnter=False
    emailNotEnter=False
    typeNotSelect=False
    userAlreadyExist=False
    spMessage=False
    cusMessage=False
    if request.method=="POST":
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        query='SELECT * FROM authentication WHERE name=%s LIMIT 1'
        cur.execute(query,(name,))
        userDetails=cur.fetchall()
        if not userDetails:
            if name=="":
               userNameNotEnter=True
            if email=="":
               emailNotEnter=True
            if password=="":
               passwordNotEnter=True
            if name!="" and email!="" and password!="":
               cur.execute('SELECT * FROM authentication')
               results=cur.fetchone()
               if not results:
                  q='INSERT INTO authentication (customer_id,name, email, password) VALUES (%s,%s, %s, %s)'
                  cur.execute(q,(100001,name,email,password))
                  db.connection.commit()
                  session['name']=name
                  session['dashboard']='cus'
                  return redirect("/dashboard")
               else:
                  q='INSERT INTO authentication (name, email, password) VALUES (%s, %s, %s)'
                  cur.execute(q,(name,email,password))
                  db.connection.commit()
                  session['name']=name
                  session['dashboard']='cus'
                  return redirect("/dashboard")
        cur.close()
        if userDetails!=None:
            if userDetails.type==type:
               userAlreadyExist=True
            if userDetails.type!=type:
               if userDetails.type=="sp" and type=="cus":
                  spMessage=True
               if userDetails.type=="cus" and type=="sp":
                  cusMessage=True
    return render_template('signup.html',userNameNotEnter=userNameNotEnter,emailNotEnter=emailNotEnter,passwordNotEnter=passwordNotEnter,typeNotSelect=typeNotSelect,userAlreadyExist=userAlreadyExist,spMessage=spMessage,cusMessage=cusMessage)

@bp.route("/dashboard")
def dashboard():
    cur=db.connection.cursor()
    cur.execute("SELECT * FROM master")
    results=cur.fetchall()
    list=[]
    for item in range(0,len(results)):
        list.append("-".join([str(i) for i in [*results[item].values()]]))
    master=list
    name=session.get('name') 
    # unique=db.session.query(Master.phone,Master.service_provider_code,Master.service_provider_name,Master.service_provider_locality_area_colony,Master.service_provider_city_district_town).distinct()
    # results=db.session.execute(unique)
    cur.execute("SELECT DISTINCT phone,service_provider_code,service_provider_name,service_provider_locality_area_colony,service_provider_city_district_town FROM master")
    res=cur.fetchall()
    cur.close()
    return render_template("dashboard.html",name=name,master=str(master),results=res)

@bp.route("/spdashboard")
def spdashboard():
    name=session.get('name')
    print(name)
    return render_template("spdashboard.html",name=name)

@bp.route("/services",methods=['GET','POST'])
def services():
    cur=db.connection.cursor()
    if request.method=="POST":
        data_array = request.form.get('data_array')
        data=json.loads(data_array)
        phone=signup_storage.get('phone')
        email=session['email']
        service_provider_name=signup_storage.get('service_provider_name')
        service_provider_estb_name=signup_storage.get('service_provider_estb_name')
        service_provider_houseno=signup_storage.get('service_provider_houseno')
        service_provider_street_road=signup_storage.get('service_provider_street_road')
        service_provider_locality_area_colony=signup_storage.get('service_provider_locality_area_colony')
        service_provider_major_landmark=signup_storage.get('service_provider_major_landmark')
        service_provider_city_district_town=signup_storage.get('service_provider_city_district_town')
        service_provider_state=signup_storage.get('service_provider_state')
        service_provider_pincode=signup_storage.get('service_provider_pincode')
        spc=100000
        cur.execute("SELECT * FROM master")
        res=cur.fetchall()
        if res:
            cur.execute("SELECT * FROM master")
            mster=cur.fetchall()
            for i in mster:
                spc=i.service_provider_code
        for i in range(0,len(data)):
             service_id=data[i]['serviceId']
             service_description=data[i]['serviceDesc']
             service_time=data[i]['serviceTime']
             service_cost=data[i]['serviceCost']
             query="INSERT INTO master(phone,service_provider_code,service_provider_name,service_provider_email,service_provider_estb_name,service_provider_houseno,service_provider_street_road,service_provider_locality_area_colony,service_provider_major_landmark,service_provider_city_district_town,service_provider_state,service_provider_pincode,service_id,service_description,service_time,service_cost) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
             cur.execute(query,(phone,spc+1,service_provider_name,email,service_provider_estb_name,service_provider_houseno,service_provider_street_road,service_provider_locality_area_colony,service_provider_major_landmark,service_provider_city_district_town,service_provider_state,service_provider_pincode,service_id,service_description,service_time,service_cost))
             db.connection.commit()
        signup_storage.clear()
        session['name']=service_provider_name
        session['dashboard']='sp'
        return redirect("/spdashboard")
    cur.execute("SELECT * FROM services")
    allservices=cur.fetchall()
    cur.close()
    print(allservices)
    return render_template("services.html",allservices=allservices)

@bp.route("/")
def index():
    if not session.get("name") and not session.get("dashboard"):
        return render_template("index.html",name="",dashboard="")
    return render_template("index.html",name=session['name'],dashboard=session['dashboard'])
@bp.route("/home")
def home():
    return render_template("index.html",name=session['name'])

@bp.route("/logout")
def logout():
    session.pop('name',None)
    session.pop('email',None)
    session.pop('verify',None)
    session.pop('dashboard',None)
    return redirect("/")

@bp.route("/login",methods=['GET','POST'])
def login():
    cur=db.connection.cursor()
    userNameNotEnter=False
    passwordNotEnter=False
    userNotExist=False
    if request.method=="POST":
        name=request.form['name']
        password=request.form['password']
        query="SELECT name FROM authentication WHERE name=%s LIMIT 1"
        cur.execute(query,(name,))
        user=cur.fetchall()
        if name=="":
            userNameNotEnter=True
        if password=="":
            passwordNotEnter=True         
        if user==None:
           userNotExist=True
        if user:
            session['name']=name
            session['dashboard']='cus'
            cur.close()
            return redirect("/dashboard")
    return render_template("login.html",userNameNotEnter=userNameNotEnter,passwordNotEnter=passwordNotEnter,userNotExist=userNotExist)

@bp.route("/splogin",methods=['GET','POST'])
def splogin():
    cur=db.connection.cursor()
    if request.method=="POST":
        phone=request.form.get('phone')
        usercode=request.form.get('password')
        # sp=Master.query.filter_by(phone=phone).first()
        # spc=str(sp).split("-")[1]
        # name=str(sp).split("-")[2]
        query="SELECT * FROM `master` WHERE service_provider_code=%s LIMIT 1"
        cur.execute(query,(usercode,)) 
        user=cur.fetchall()  
        print(user)     
        if user:
            session['name']=user[0]['service_provider_name']
            session['dashboard']='sp'
            return redirect("/spdashboard")
    return render_template("splogin.html")

# @bp.route("/verifyotp",methods=['GET','POST'])
# def verifyotp():
#     email=session['email']
#     otp_enter=request.form['otp']
#     if email in otp_storage and otp_storage[email] == otp_enter:
#         # Clear OTP after successful verification
#         users=Authentication.query.all()
#         for i in users:
#             if i.email==email:
#                 session['name']=i.name
#         del otp_storage[email]
#         return redirect('/dashboard')
#     else:
#         return jsonify({'message': 'Invalid OTP'}), 400
    
@bp.route('/transaction',methods=['GET','POST'])
def transaction():
    cur=db.connection.cursor()
    if request.method=="POST":
        name=session['name']
        #users=Authentication.query.all()
        cur.execute("SELECT * FROM authentication")
        users=cur.fetchall()
        customer_id=0
        for i in users:
            if i['name']==name:
                customer_id=i['customer_id']
        current_year = str(current_date.strftime("%Y"))
        year=current_year[-2]+current_year[-1]
        data_array = request.form.get('data_array')
        tid=str(year)+str(customer_id)+str(random.randint(100, 999))
        transaction_id=int(tid)
        data=json.loads(data_array)
        service_provider_code=data[0]['serviceProviderCode']
        service_provider_name=data[0]['serviceProviderName']
        service_provider_location=data[0]['serviceProviderLocation']
        service_provider_city=data[0]['serviceProviderCity']
        all_services_requested=''
        for i in range(0,len(data)):
            if data[i]['serviceCheck']==True:
                all_services_requested=all_services_requested+str(data[i]['serviceId'])+";"
        service_date_html=request.form.get('date')
        service_time_html=request.form.get('time')
        date_obj = datetime.strptime(service_date_html, '%Y-%m-%d').date()
        time_obj = datetime.strptime(service_time_html, '%H:%M').time()
        total_service_time = request.form.get('hidden_totalservicetime')
        total_service_cost = request.form.get('hidden_totalcost')
        #trans=Transaction(transaction_id=transaction_id,customer_id=customer_id,customer_name=name,service_provider_code=service_provider_code,service_provider_name=service_provider_name,service_provider_location=service_provider_location,service_provider_city=service_provider_city,all_services_requested=all_services_requested,service_date=date_obj,service_time=time_obj,total_service_time=total_service_time,total_service_cost=total_service_cost)
        query="INSERT INTO transactional (t_id,customer_id,customer_name,service_provider_code,service_provider_name,service_provider_location,service_provider_city,all_services_requested,service_date,service_time,total_service_time,total_service_cost) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur.execute(query,(tid,customer_id,name,service_provider_code,service_provider_name,service_provider_location,service_provider_city,all_services_requested,date_obj,time_obj,total_service_time,int(total_service_cost)))
        db.connection.commit()
        session['customerid']=customer_id
        q="SELECT DISTINCT service_provider_email FROM `master` WHERE service_provider_code=%s"
        cur.execute(q,(service_provider_code,))
        res=cur.fetchall()
        email=res[0]['service_provider_email']
        url1='http://127.0.0.1:5000/approval'
        url2='http://127.0.0.1:5000/reject'
        html_content = f'''
        <html>
        <body>
        <p>
        Customer Id: {customer_id}<br>
        Customer Name:{name}<br>
        Services Requested: {all_services_requested}<br>
        Service Time: {time_obj}<br>
        Service Date: {date_obj}<br>
        </p>
        <a href="{url1}" style="
            display: inline-block;
            padding: 10px 20px;
            font-size: 16px;
            color: white;
            background-color: #00712D;
            text-decoration: none;
            border-radius: 5px;">
            Accept
        </a>
        <a href="{url2}" style="
            display: inline-block;
            padding: 10px 20px;
            font-size: 16px;
            color: white;
            background-color: #F5004F;
            text-decoration: none;
            border-radius: 5px;">
            Reject
        </a>
        </body>
        </html>
        '''
        msg = Message('Waiting for Approval', recipients=[email],html=html_content)
        msg.body = f'Your requested service is wating for approval'
        try:
          mail.send(msg)
        except Exception as e:
          return jsonify({'message': str(e)}), 500
        cur.close()
        return redirect("/dashboard")
@bp.route("/approval")
def approval():
    cur=db.connection.cursor()
    qu="SELECT email FROM authentication WHERE customer_id=%s"
    cur.execute(qu,(session['customerid'],))
    res=cur.fetchall()
    cemail=res[0]['email']
    msg = Message('Service Acceptance', recipients=[cemail])
    msg.body = f'Your Request is Accepted'
    mail.send(msg)
    query="UPDATE transactional SET booking_status='Accepted' WHERE customer_id=%s"
    cur.execute(query,(session['customerid'],))
    db.connection.commit()
    cur.close()
    session.pop('customerid',None)
    return render_template("approval.html")
@bp.route("/reject")
def reject():
    cur=db.connection.cursor()
    qu="SELECT email FROM authentication WHERE customer_id=%s"
    cur.execute(qu,(session['customerid'],))
    res=cur.fetchall()
    cemail=res[0]['email']
    msg = Message('Service Acceptance', recipients=[cemail])
    msg.body = f'Your Request is Rejected'
    mail.send(msg)
    query="UPDATE transactional SET booking_status='Rejected' WHERE customer_id=%s"
    cur.execute(query,(session['customerid'],))
    db.connection.commit()
    cur.close()
    session.pop('customerid',None)
    return render_template("reject.html")
# @bp.route('/notificationpage')
# def notificationPage():
#     allNotifications=Notification.query.filter_by(name=session['name']).all()
#     return render_template("notification.html",allNotifications=allNotifications,name=session['name'])

# @bp.route('/delete/<int:id>')
# def deleteNotification(id):
#     notify=Notification.query.filter_by(id=id).first()
#     db.session.delete(notify)
#     db.session.commit()
#     return redirect("/notificationpage")

@bp.route('/sendotp',methods=['GET','POST'])
def sendotp():
    email=request.form['email']
    session['email']=email
    otp=generate_otp()
    otp_storage[email]=otp
    msg = Message('OTP for Authentication', recipients=[email])
    msg.body = f'Your OTP for authentication is: {otp}'
    
    try:
         mail.send(msg)
         return redirect("/verifyotppage")
    except Exception as e:
         return jsonify({'message': str(e)}), 500
    
@bp.route('/sendotpemail',methods=['GET','POST'])
def sendotpemail():
    email=request.form.get('email')
    return f"{email}"

@bp.route("/otpsendpage")
def otpsend():
    return render_template("otpsend.html")

@bp.route("/verifyotppage")
def verify():
    return render_template("otpverification.html")

# @bp.route("/spprofile")
# def spprofile():
#     name=session['name']
#     sp=Master.query.filter_by(service_provider_name=name).first()
#     ename=str(sp).split("-")[3]
#     return render_template("spprofile.html",name=name,ename=ename)