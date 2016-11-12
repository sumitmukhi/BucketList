import os
import boto
import boto.s3
import sys
from boto.s3.key import Key
from flask import Flask, render_template, json, request,redirect,session, send_from_directory, url_for
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash, secure_filename

mysql = MySQL()
app = Flask(__name__)
# app.secret_key = 'why would I tell you my secret key?'
# import os ---> os.urandom(24)
app.secret_key = '<\x13\x00\x96\x04nuQ\xde\xe5\xc3\xc7\x1a"VPd\x96Jd\x04\xfa~\x8f'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

mysql.init_app(app)

s3_connection = boto.connect_s3('AKIAJWKZQGTRDDR7CTRQ','rS1AtPVFmHrlwen48ZAPJb8zji0abFoWneO131k/')
bucket = s3_connection.get_bucket('aws-learnup')

conn = mysql.connect()
cursor = conn.cursor()


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showAddWish')
def showAddWish():
    return render_template('addWish.html')

@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/deleteWish',methods=['POST'])
def deleteWish():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')

            # conn = mysql.connect()
            # cursor = conn.cursor()
            cursor.callproc('sp_deleteWish',(_id,_user))
            result = cursor.fetchall()

            if len(result) is 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'an error occurred'})
        else:
            return render_template('error.html', error = 'Unauthorized access')
    except Exception as e:
        return json.dumps({'status':str(e)})
    # finally:
    #     cursor.close()
    #     conn.close()

@app.route('/updateWish', methods=['POST'])
def updateWish():
    try:
        if session.get('user'):
            _user = session.get('user')
            _title = request.form['title']
            _description = request.form['description']
            _wish_id = request.form['id']

            # conn = mysql.connect()
            # cursor = conn.cursor()
            cursor.callproc('sp_updateWish',(_title,_description,_wish_id, _user))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'ERROR'})
    except Exception as e:
        return json.dumps({'status':'Unauthorized access'})
    # finally:
    #     cursor.close()
    #     conn.close()

@app.route('/getWishById',methods=['POST'])
def getWishById():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')

            # conn = mysql.connect()
            # cursor = conn.cursor()
            cursor.callproc('sp_GetWishById',(_id,_user))
            result = cursor.fetchall()

            wish = []
            wish.append({
                    'Id':result[0][0],
                    'Title':result[0][1],
                    'Description':result[0][2]
                })
            return json.dumps(wish)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/getWish')
def getWish():
    try:
        if session.get('user'):
            _user = session.get('user')

            # con = mysql.connect()
            # cursor = con.cursor()
            cursor.callproc('sp_GetWishByUser',(_user,))
            wishes = cursor.fetchall()

            wishes_dict = []
            for wish in wishes:
                wish_dict = {
                        'Id': wish[0],
                        'Title': wish[1],
                        'Description': wish[2],
                        'Date': wish[4]}
                wishes_dict.append(wish_dict)

            return json.dumps(wishes_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

@app.route('/addWish',methods=['POST'])
def addWish():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _description = request.form['inputDescription']
            _user = session.get('user')

            # conn = mysql.connect()
            # cursor = conn.cursor()
            cursor.callproc('sp_addWish',(_title,_description,_user))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'An error occurred!')

        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
    # finally:
    #     cursor.close()
    #     conn.close()

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to mysql

        # con = mysql.connect()
        # cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()


        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')


    except Exception as e:
        return render_template('error.html',error = str(e))
    # finally:
    #     cursor.close()
    #     con.close()

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/signUp',methods=['POST','GET'])
def signUp():
    print "signup"
    # print request.data
    print request.form
    print '--------------------------'
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        file = request.files['photo']
        # print file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = _email+".png"
            print os.path
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            key = boto.s3.key.Key(bucket, filename)
            key.set_contents_from_filename('uploads/'+filename)

        # validate the received values
        if _name and _email and _password:
            # All Good, let's call MySQL
            # conn = mysql.connect()
            # cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            image = "https://s3-ap-southeast-1.amazonaws.com/aws-learnup/"+filename
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password, image))
            data = cursor.fetchall()
            if len(data) > 0:
                conn.commit()
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    # finally:
    #     cursor.close()
    #     conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
