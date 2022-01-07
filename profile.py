from os import abort
from sqlite3.dbapi2 import Cursor
from flask import render_template,Blueprint,request, session
from phonenumbers.phonenumber import PhoneNumber
from werkzeug.utils import redirect,secure_filename
from defs import Patient
from functions import *
from phonenumbers import geocoder
from phonenumbers import carrier
import phonenumbers
from models.models import *
import os
from config import *
ProfilePage=Blueprint("profile",__name__)
'''
I already have the data in the session and i will detect if the user is patient or doctor by using group id
id=1 ----> will edit the data
id=0 -----> will go to the profile normally
The methods of the page if the method is Post and id=1 then the user will come from the profile page to profile edit Page to edit the data
if the method is post and the id=0 then the user will come from the update page to the normal profile page 
if the method is Get and id=0 then the user will come form the home page 
call the query Update and if the query is succeed it will return the bool value is_updated=true to tall me and i will save the new data in the session  
Some NOTES: 1-if the user not login the link of the profile page will lead to login first if he attemps to get profile will the URI
2- in the profile the job will decide according to the GroupID 
3- 
'''
#start the connection 
connection = open_connection("hospital.db")
cursor = get_cursor(connection)
Database_Setup(cursor)
AllowedExtaions=set(["jpg","png","gif","jfif","jpeg"])
UPLOAD_FOLDER="static\images\\"
@ProfilePage.route("/profile/<string:id>",methods=["POST","GET"])
def profile(id):
    if "ID" in session: #Edit page
        Data={}
        patients=[]
        if("Group_id" not in session):
            # the query to get the status
            result3= selectFromTable(cursor,"PatientStatus",PatientStatus_attributes,[PatientStatus.All.value],[(PatientStatus.Patient_ID.value,session['ID'])])
            result2=SelecT_ALL_Prescription_Patient_sorted_by_date(cursor,session["ID"])
            print(result2)
            if len(result3)!=0:
                Data["disease1"]=result3[0][1]
                Data["disease2"]=result3[0][2]
                Data["disease3"]=result3[0][3]
                Data["disease4"]=result3[0][4]
                Data["disease5"]=result3[0][5]
                
            if len(result2)!=0:
                Data["DoctorName"]=result2[0][0]
                Data["DATE"]=result2[0][1]
                Data["Treatment"]=result2[0][2]
        if("Group_id" not in session):
            DataOfUser=selectFromTable(cursor,"Patient",Patient_attributes,[Patient.All.value],[(Patient.Patient_ID.value,session['ID'])])
        else:
            DataOfUser=selectFromTable(cursor,"Employee",Employee_attributes,[Employee.All.value],[(Employee.Employee_ID.value,session['ID'])])
            patients = [patient[1] for patient in zip(range(4),selectFromTable(cursor, "Patient", Patient_attributes, [Patient.Patient_ID.value , Patient.FNAME.value, Patient.lNAME.value, Patient.GENDER.value], []))]
        session["Fname"]                =DataOfUser[0][1]
        session["Lname"]                =DataOfUser[0][2]
        session["Age"]                  =DataOfUser[0][3]
        session["Email"]                =DataOfUser[0][10]
        session["password"]             =DataOfUser[0][11]
        session["Gender"]               =DataOfUser[0][9]
        session["PhoneNumber"]          =DataOfUser[0][5]
        session["Addresscountry"]       =DataOfUser[0][6]
        session["Addressstreet"]        =DataOfUser[0][8]
        session["Addresscity"]          =DataOfUser[0][7]
        session["image"]                =DataOfUser[0][12]
        print(session)
        if id=="Edit" and request.method=="GET":
            return render_template("Profile.html",edit=id,data=Data,data1=session,patients=patients,Session_id=session["ID"])
        elif id=="mainprofile": #main profile page
            if request.method=="POST":
                Fname=request.form.get("Fname")
                Lname=request.form.get("Lname")
                email=request.form.get("email")
                password=request.form.get("password")
                phoneNumber =request.form.get("Phone")
                Addresscountry=request.form.get("Addresscountry")
                Addressstreet=request.form.get("Addressstreet")
                Addresscity=request.form.get("Addresscity")
                PhoneCountry="+"+str(codes[recode(Addresscountry)]) 
                phone = phonenumbers.parse(PhoneCountry+phoneNumber)
                if not(has_numbers(Fname)) and not(has_numbers(Lname)and(phonenumbers.is_valid_number(phone))):
                    new_info=['"'+Fname+'"','"'+Lname+'"','"'+email+'"','"'+password+'"',phoneNumber,'"'+Addresscountry+'"','"'+Addresscity+'"','"'+Addressstreet+'"']
                    if("Group_id" not in session):
                        is_upadated = Update(cursor,'Patient',[Patient.Patient_ID.value],[session['ID']],[Patient.FNAME.value,Patient.lNAME.value,Patient.Email.value,Patient.Password.value,Patient.PhoneNumber.value,Patient.Addresscountry.value,Patient.Addresscity.value,Patient.Addressstreet.value],new_info)
                    else:
                        is_upadated = Update(cursor,'Employee',[Employee.Employee_ID.value],[session['ID']],[Employee.FNAME.value,Employee.lNAME.value,Employee.Email.value,Employee.Password.value,Employee.PhoneNumber.value,Employee.Addresscountry.value,Employee.Addresscity.value,Employee.Addressstreet.value],new_info)
                    if is_upadated:
                        connection.commit()
                        session["Fname"]=Fname
                        session["Lname"]=Lname
                        session["Email"]=email
                        session["password"]=password
                        session["PhoneNumber"]=phoneNumber
                        session["Addresscountry"]=Addresscountry
                        session["Addressstreet"]=Addressstreet
                        session["Addresscity"]=Addresscity
                        return redirect("/profile/mainprofile")
                        return render_template("Profile.html",edit=0,data=Data,data1=session,patients=patients,Session_id=session["ID"])
                    else:
                        return redirect("/profile/mainprofile")
                        return render_template("Profile.html",edit=id,data1=session,data=Data,patients=patients,Session_id=session["ID"])
                else :
                    return redirect("/profile/mainprofile")
                    return render_template("Profile.html",edit=id,data1=session,data=Data,patients=patients,Session_id=session["ID"])
            else :
                return render_template("Profile.html",edit=id,data1=session,data=Data,patients=patients,Session_id=session["ID"])
        else:
            return redirect("/home")
    else:
        return "login first"

#the profile page of the admin 
#when the home page is ended i will add a button to the profile page and i will select which route should be called
#if Group_id==A  


@ProfilePage.route("/AdminProfile/<Operation>",methods=["POST","GET"])
def Admin(Operation):
    if session["Group_id"]=="A":
        if(Operation=="Department"):
            #query to get the data of the departments
            Result= selectFromTable(cursor,'Department',Department_attributes,[Deparment.All.value] ,[] )
            return render_template("ShowDataToAdmin.html",Type=Operation,Data=Result)
        elif Operation=="Employee":
            #query to get the data of the employees
            Result= selectEmployeesExceptAdmin(cursor)
            return render_template("ShowDataToAdmin.html",Type=Operation,Data=Result)
        elif Operation=="Patient":
            Result= selectFromTable(cursor,'Patient',Patient_attributes,[Patient.All.value] ,[] )
            return render_template("ShowDataToAdmin.html",Type=Operation,Data=Result)
        elif Operation=="Donation":
            Result=selectFromTable(cursor,'Donation',Donation_attributes,[Donation.All.value] ,[] )
            return render_template("ShowDataToAdmin.html",Type=Operation,Data=Result)
        
    else:
        return "you are not allowed"

#route to insert the Departments by the Admin
@ProfilePage.route("/AdminProfile/Departments/<string:operation>",methods=["POST","GET"])
def AdminSettingsDepartments(operation):
    if session["Group_id"]=="A":
        if operation=="Insert":
            info = cursor.execute('''select ID from Employee ;''').fetchall()
            return render_template("AdminSettings.html",SSNList=info[0],Type="Departments",selector=operation)
    else:
        return "you are not allowed"
#route to insert the employees by the Admin
@ProfilePage.route("/AdminProfile/Employees/<string:operation>",methods=["POST","GET"])
def AdminSettingsEmployees(operation):
    if session["Group_id"]=="A":
        Departments=cursor.execute('''select ID from Department ;''').fetchall()
        if operation=="Insert":
            return render_template("AdminSettings.html",SSNList=session,DEList=Departments[0],Type="Employees",selector=operation)
    else:
        return "you are not allowed"
#########################DONE#########################################################
#rout to check the data form the Admin
@ProfilePage.route("/AdminProfile/checkdata/Insert",methods=["POST"])
def AdmincheckoutDataforInsert():
    if request.form.get("Departmentname") !=None :
        #the data of the department
        Departmentname=request.form.get("Departmentname")
        Startdate=request.form.get("StartDate")
        Departmentmanager=request.form.get("Manager")
        #Bolbol check the data and insert it in the database
        
        Employee_joinDate = getJoinDateOfEmployee(cursor,Departmentmanager)
        Startdate1=datetime.strptime(str(Startdate),'%Y-%m-%d')
        if(not(datetime.strptime(Employee_joinDate[0][0],'%d-%m-%Y')<Startdate1)):
            return "this Employee joined the hospital after this date " 
        DepartmentNames=getDepartmentnames(cursor)
        for i in range(len(DepartmentNames)):
            if Departmentname in DepartmentNames[i]: 
                return "there is department has the same name"
        Columns2 = [Deparment.All.value]
        info= [ Departmentname,Departmentmanager,str(Startdate1)]
        insert_general(cursor,'Department',Department_attributes,Columns2,info)
        connection.commit()
        return redirect("/AdminProfile/Department")
        
    else:
        # the data of the employee
        Fname=request.form.get("Fname")
        Lname=request.form.get("Lname")
        Email=request.form.get("Email")
        Password=request.form.get("Password")
        #Manager=request.form.get("Manager")----> what is this
        Age=request.form.get("Age")
        PhonNumber=request.form.get("PhonNumber")
        Addresscountry=request.form.get("Addresscountry")
        Addressstreet=request.form.get("Addressstreet")
        Addresscity=request.form.get("Addresscity")
        Department_ID=request.form.get("Department")
        joinDate=request.form.get("joinDate") #there is problem in it 
        #Startdate2=datetime.strptime(str(joinDate),'%Y-%m-%d')
        GroupID=request.form.get("GroupID")
        Gender=request.form.get("Gender")
        PhoneCountry="+"+str(codes[recode(Addresscountry)]) 
        phone = phonenumbers.parse(PhoneCountry+PhonNumber)
        if not(has_numbers(Fname)) and not(has_numbers(Lname))and phonenumbers.is_valid_number(phone)and(Age.isdecimal())and(int(Age)>0):
            new_info=[Fname,Lname,Age,PhoneCountry,PhonNumber,Addresscountry,Addresscity,Addressstreet,Gender,Email,Password,str(joinDate),Department_ID,GroupID]
        else :
            return 'wrong data'           
        #Bolbol check the data and insert it in the database
        insert_general(cursor,'Employee',Employee_attributes,[Employee.All.value],new_info)
        connection.commit()
        return redirect("/AdminProfile/Employee")
########################################################################################################
@ProfilePage.route("/AdminProfile/checkdata/Edit/<int:ID>",methods=["POST"])
def AdmincheckoutDataforEdit(ID):
    print("from the edit")
    if request.form.get("Departmentname") !=None and request.method== "POST" :
        #the data of the department
        Departmentname=request.form.get("Departmentname")
        Startdate=request.form.get("StartDate")
        Departmentmanager=request.form.get("Manager")
        department_Data = selectFromTable(cursor,'Department',Department_attributes,[Deparment.All.value] ,[(Deparment.Department_ID.value,ID)] )
        if Startdate=="":
            Startdate=department_Data[0][3]
        elif Departmentname=="":
            Departmentname=department_Data[0][1]
        Employee_joinDate =getJoinDateOfEmployee(cursor,Departmentmanager)
        DepartmentNames=getDepartmentnames(cursor,department_Data[0][1])
        print(DepartmentNames)
        for i in range(len(DepartmentNames)):
            if Departmentname in DepartmentNames[i]: 
                return "there is department has the same name"
        Columns2 = [Deparment.All.value]
        info= [ '"'+Departmentname+'"',Departmentmanager,'"'+str(Startdate)+'"']
        Update(cursor,'Department',[Deparment.Department_ID.value],[ID],[Deparment.Department_Name.value,Deparment.Manager_id.value,+Deparment.Start_Date.value],info)
        connection.commit()
        return redirect("/AdminProfile/Department")
        
    else:
        # the data of the employee
        Employee_Data = selectFromTable(cursor,'Employee',Employee_attributes,[Employee.All.value] ,[(Employee.Employee_ID.value,ID)] )
        Fname=request.form.get("Fname")
        Lname=request.form.get("Lname")
        Email=request.form.get("Email")
        Password=request.form.get("Password")
        #Manager=request.form.get("Manager")----> what is this
        Age=request.form.get("Age")
        PhonNumber=request.form.get("PhonNumber")
        Addresscountry=request.form.get("Addresscountry")
        Addressstreet=request.form.get("Addressstreet")
        Addresscity=request.form.get("Addresscity")
        Department_ID=request.form.get("Department")
        joinDate=request.form.get("joinDate") #there is problem in it 
        if joinDate=="":
            joinDate=Employee_Data[0][12]
        #Startdate2=datetime.strptime(str(joinDate),'%Y-%m-%d')
        GroupID=request.form.get("GroupID")
        Gender=request.form.get("Gender")
        PhoneCountry="+"+str(codes[recode(Addresscountry)]) 
        phone = phonenumbers.parse(PhoneCountry+PhonNumber)
        if not(has_numbers(Fname)) and not(has_numbers(Lname))and phonenumbers.is_valid_number(phone)and(Age.isdecimal())and(int(Age)>0):
            new_info=[Fname,Lname,Age,PhoneCountry,PhonNumber,Addresscountry,Addresscity,Addressstreet,Gender,Email,Password,str(joinDate),Department_ID,GroupID]
        else :
            return 'wrong data'           
        #Bolbol check the data and insert it in the database
        new_info2 = ['"'+Fname+'"','"'+Lname+'"',Age,PhoneCountry,PhonNumber,'"'+Addresscountry+'"','"'+Addresscity+'"','"'+Addressstreet+'"','"'+Gender+'"','"'+Email+'"','"'+Password+'"','"'+str(joinDate)+'"',Department_ID,'"'+GroupID+'"']
        Update(cursor,'Employee',[Employee.Employee_ID.value],[ID],[Employee.FNAME.value,Employee.lNAME.value,Employee.Age.value,Employee.Phonecountry.value,Employee.PhoneNumber.value,Employee.Addresscountry.value,Employee.Addresscity.value,Employee.Addressstreet.value,Employee.GENDER.value,Employee.Email.value,Employee.Password.value,Employee.JoinDate.value,Employee.D_id.value,Employee.Group_id.value],new_info2)
        connection.commit()
        return redirect("/AdminProfile/Employee")
##################DONE#############################
# route to delete the Departments by using the id
@ProfilePage.route('/DeleteDepartment/<int:id>')
def deleteDepartment(id):
    # query to delete
    Delete(cursor,'Department',[Deparment.Department_ID.value],[id])
    connection.commit()
    return redirect("/AdminProfile/Department")
##########################################################

##################DONE#############################
# route to delete the Employees by using the id
@ProfilePage.route('/DeleteEmployee/<int:id>')
def deleteEmployee(id):
    # query to delete
    Delete(cursor,'Employee',[Employee.Employee_ID.value],[id])
    connection.commit()
    return redirect("/AdminProfile/Employee")
###########################################################
# route to delete the patients by using the id
##################DONE#####################################
@ProfilePage.route('/DeletePatient/<int:id>')
def deletePatient(id):
    # query to delete
    Delete(cursor,'Patient',[Patient.Patient_ID.value],[id])
    connection.commit()
    return redirect("/AdminProfile/Patient")
######################################################################
#route to edit the data of the Employees
@ProfilePage.route('/EditEmployee/<int:id>')
def EditEmployee(id):
    # query to get the data of the id
    employee_Data = selectFromTable(cursor,'Employee',Employee_attributes,[Employee.All.value] ,[(Employee.Employee_ID.value,id)] )
    DepartmentIDS=selectFromTable(cursor,'Department',Department_attributes,[Deparment.Department_ID.value],[])
    return render_template("EditData.html",Type="Employees",SSNList =session,DEList=DepartmentIDS[0],DataEmp=employee_Data)
    #bolbol get the data and check it
#route to edit the data of the Departments
@ProfilePage.route('/EditDepartment/<int:id>')
def EditDepartment(id):
    # query to retrive the data of the id
    department_Data = selectFromTable(cursor,'Department',Department_attributes,[Deparment.All.value] ,[(Deparment.Department_ID.value,id)] )
    manager_Data = selectFromTable(cursor,'Employee',Employee_attributes,[Employee.Employee_ID.value],[])
    return render_template("EditData.html",Type="Departments",SSNList=manager_Data[0],DataDP=department_Data)
    #bolbol get the data and check it

@ProfilePage.route('/employee/<int:employee_id>/patients',methods=["GET"])
def showAllPatient(employee_id):
    patients = selectFromTable(cursor, "Patient", Patient_attributes, [Patient.Patient_ID.value, Patient.FNAME.value, Patient.lNAME.value, Patient.GENDER.value], [])
    return render_template("Patients.html", patients=patients)

@ProfilePage.route('/patients/<int:patient_id>', methods=["GET"])
def Show_my_patients(patient_id):
    patient = selectFromTable(cursor, "Patient", Patient_attributes, [Patient.All.value],[(Patient.Patient_ID.value,patient_id)])[0]
    # print("#####################################################################")
    # print("Ahmed Alaa is debugging here! Watch Out!!!")
    # print(session)
    # print("#####################################################################")
    Data={}
    result3= selectFromTable(cursor,"PatientStatus",PatientStatus_attributes,[PatientStatus.All.value],[(PatientStatus.Patient_ID.value,patient_id)])
    result2=SelecT_ALL_Prescription_Patient_sorted_by_date(cursor,patient_id)
    print(result2)
    if len(result3)!=0:
        Data["disease1"]=result3[0][1]
        Data["disease2"]=result3[0][2]
        Data["disease3"]=result3[0][3]
        Data["disease4"]=result3[0][4]
        Data["disease5"]=result3[0][5]
        
    if len(result2)!=0:
        Data["DoctorName"]=result2[0][0]
        Data["DATE"]=result2[0][1]
        Data["Treatment"]=result2[0][2]
    data = {
        "Fname": patient[1],
        "Lname": patient[2],
        "Age": patient[3],
        "PhoneNumber": patient[5],
        "Addresscountry": patient[6],
        "Addresscity": patient[7],
        "Addressstreet": patient[8],
        "Gender": patient[9],
        "Email": patient[10]
    }
    print(result3,result2)
    return render_template("Profile.html", data1=data,data=Data,Doctor=1)

#route to accept the donation
@ProfilePage.route('/acceptDonation/<int:id>')
def AcceptDonation(id):
    # query to update the donation
    Update(cursor,'Donation',[Donation.Donation_ID.value],[id],[Donation.state.value],['"D"'])
    connection.commit()
    return redirect("/AdminProfile/Donation")

#route to reject the donation
@ProfilePage.route('/rejectDonation/<int:id>')
def RejectDonation(id):
    # query to update the donation
    Update(cursor,'Donation',[Donation.Donation_ID.value],[id],[Donation.state.value],['"C"'])
    connection.commit()
    return redirect("/AdminProfile/Donation")

@ProfilePage.route("/doctors/<int:doctor_id>", methods=["GET"])
def Show_doctor(doctor_id):
    doctor = selectFromTable(cursor, "Employee", Employee_attributes, [Employee.All.value], [(Employee.Employee_ID.value,doctor_id)])[0]
    Data = {
        "Fname": doctor[1],
        "Lname": doctor[2],
        "Age": doctor[3],
        "PhoneNumber": doctor[5],
        "Addresscountry": doctor[6],
        "Addresscity": doctor[7],
        "Addressstreet": doctor[8],
        "Gender": doctor[9],
        "Email": doctor[10],
        "Group_id":doctor[14]
    }
    return render_template("Profile.html",edit=0, data1=Data,Session_id=session["ID"])


@ProfilePage.route("/takephoto",methods=["POST"])
def setPhoto():
    photo=request.files["image"]
    if photo.mimetype[6:] in AllowedExtaions :
        print(photo)
        secure_filename(photo.filename)
        print(photo.mimetype)
        if "Group_id" not in session:
            photo.filename="patient"+str(session["ID"])+photo.filename
        else:
            photo.filename="Employee"+str(session["ID"])+photo.filename
        print (os.path.join(UPLOAD_FOLDER,photo.filename))
        photo.save(os.path.join(UPLOAD_FOLDER,photo.filename))
        return photo.mimetype
    else:
        return "error in Extaion"