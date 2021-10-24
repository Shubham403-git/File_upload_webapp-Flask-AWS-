from flask import *
import os
import subprocess as sp
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import boto3
from botocore.exceptions import NoCredentialsError


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Pass@123'
app.config['MYSQL_DB'] = 'imagedata'
mysql = MySQL(app)
app.config['UPLOAD_FOLDER'] = '/var/www/webapp'

#UPLOAD_FOLDER = '/var/www/webapp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}



#app.config['MAX_CONTENT_LENGTH'] = 1 * 1000 * 1000
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def uploads(filename):
    #ACCESS_KEY = os.environ['ACCESS_KEY']
    #SECRET_KEY = os.environ['SECRET_KEY']
    ACCESS_KEY = "AKIAU6X3MVRESQUACKVE"
    SECRET_KEY= "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"

    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    local_file="/var/www/webapp/"+filename
    bucket= "quixote-files"
    object_name= filename
    try:
        s3.upload_file(local_file, bucket,object_name,
    ExtraArgs={'ACL': 'public-read'})
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False



@app.route('/')
def upload():
    return render_template("file_upload_form.html")

@app.route('/success', methods = ['POST'])
def success():


    if request.method == 'POST':

            # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        blob = request.files['file'].read()
        size = len(blob) / 1024 /1024



            # If the user does not select a file, the browser submits an
            # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and  size > 1.024:
            return"it should be less than 1 MiB"
        if file and allowed_file(file.filename):

            #filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            #file.save(filename)
            f = file.filename
            if  uploads(f):
            #sp.getoutput("aws s3 cp /var/www/webapp/".filename+"  s3://quixote-files/")
                tp = sp.getoutput("date")
                link = "https://quixote-files.s3.ap-south-1.amazonaws.com/"+file.filename
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO filedata (filename, timestamp, size, link) VALUES (%s, %s, %s,%s)", (file.filename, tp, size, link))
                mysql.connection.commit()
            #os.system("rm -rf *.jpg")
            #os.system("rm -rf *.jpeg")
            #os.system("rm -rf *.png")
                return render_template("success.html", name = file.filename , time =tp,size=  size, link =  link )
            else:
                return" Oops something went wrong "

        return "Please choose only JPG/ PNG / JPEG file AND it should be less than 1 MiB"


@app.route('/getlinks')
def Index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM filedata")
    data = cur.fetchall()
    cur.close()
    return render_template('alldata.html', data=data )



#if __name__ == '__main__':
    #app.run(debug = True)


