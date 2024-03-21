from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
import random
import qrcode
import os
# import EAN13 from barcode module 
from barcode import EAN13 
# import ImageWriter to generate an image file 
from barcode.writer import ImageWriter 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aadhar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    mobile = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    parent_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    state = db.Column(db.String(30), nullable=False)
    random_number = db.Column(db.String(12), nullable=False)
    

@app.route('/', methods=['GET', 'POST'])
def registration_form():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        address = request.form['address']
        parent_name = request.form['parent_name']
        gender = request.form['gender']
        mobile = request.form['mobile']
        state = request.form['state']

        existing_user = User.query.filter_by(mobile=mobile).first()
        if existing_user:
            return render_template('user_already_exist.html')

        random_number = generate_random_number(mobile)
        new_user = User(name=name, dob=dob, address=address, parent_name=parent_name, gender=gender, mobile=mobile, random_number=random_number, state=state)
        db.session.add(new_user)
        db.session.commit()
        # Encoding data using make() function
        img = qrcode.make(random_number)
        # Define the image file path
        img_path = os.path.join('static/images', f"MyQRCode.png")
        # Saving as an image file
        img.save(img_path)

        # my_code = EAN13(random_number, writer=ImageWriter()) 

        # # Our barcode is ready. Let's save it. 
        # my_code.save(img_path)

        
        # Pass random_number to the template
        return render_template('registration_success.html', **locals())

    return render_template('registration_form.html')


def generate_random_number(mobile_number):
    with app.app_context():
        random.seed(mobile_number)
        random_number = str(random.randint(10**11, 10**12 - 1))
        str_number = str(random_number)
        my_code = EAN13(str_number, writer=ImageWriter()) 
        # Define the image file path
        img_path = os.path.join('static/images', f"MyQRCode.png")
        # Our barcode is ready. Let's save it. 
        my_code.save(img_path)

        number_str = str(random_number)
        part1 = number_str[:4] 
        part2 = number_str[4:8]
        part3 = number_str[8:]
        result = part1 + " " + part2 + " " + part3
    return result


# def qr_code(qr_num):
# # Encoding data using make() function
#     img = qrcode.make(qr_num)
# # Saving as an image file
#     img.save('MyQRCode1.png')
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all database tables
    app.run(debug=True)
