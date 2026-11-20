from flask import Flask, render_template, flash, redirect, request, send_from_directory, url_for, send_file
import mysql.connector, os
from tensorflow.keras.utils import img_to_array, load_img
from tensorflow.keras.preprocessing.image import ImageDataGenerator 
from keras.preprocessing import image
from tensorflow.keras.models import load_model
import numpy as np
from google.generativeai import GenerativeModel
import google.generativeai as genai
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configure Gemini AI API (replace with your actual API key)
genai.configure(api_key="AIzaSyA2Z2RxqBpt8kCcW2FD8_dBO5Vv9pSLZYk ")

mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    port=3306,
    database='foods'
)

mycursor = mydb.cursor()

# Global variable to track logged-in user
user_email = None

def executionquery(query, values):
    mycursor.execute(query, values)
    mydb.commit()
    return

def retrivequery1(query, values):
    mycursor.execute(query, values)
    data = mycursor.fetchall()
    return data

def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data

@app.route('/')
def index():
    global user_email
    if user_email:  # If user is logged in, redirect to home
        return redirect(url_for('home'))
    return render_template('index.html', is_logged_in=False)

@app.route('/logout')
def logout():
    global user_email
    user_email = None  # Reset user_email on logout
    return redirect(url_for('index'))

@app.route('/register', methods=["GET", "POST"])
def register():
    global user_email
    if user_email:  # If already logged in, redirect to home
        return redirect(url_for('home'))
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        c_password = request.form['c_password']
        if password == c_password:
            query = "SELECT UPPER(email) FROM users"
            email_data = retrivequery2(query)
            email_data_list = []
            for i in email_data:
                email_data_list.append(i[0])
            if email.upper() not in email_data_list:
                query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                values = (name, email, password)
                executionquery(query, values)
                return render_template('login.html', is_logged_in=False, message="Successfully Registered! Please go to login section")
            return render_template('register.html', is_logged_in=False, message="This email ID is already exists!")
        return render_template('register.html', is_logged_in=False, message="Conform password is not match!")
    return render_template('register.html', is_logged_in=False)

@app.route('/login', methods=["GET", "POST"])
def login():
    global user_email
    if user_email:  # If already logged in, redirect to home
        return redirect(url_for('home'))
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])

        if email.lower() == "admin@gmail.com":
            if password.lower() == "admin":
                user_email = email
                return redirect("/admin_home")
            else:
                return render_template('login.html', is_logged_in=False, message="Invalid Password!!")
        
        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password__data = retrivequery1(query, values)
            if password.upper() == password__data[0][0]:
                user_email = email
                return redirect("/home")
            return render_template('login.html', is_logged_in=False, message="Invalid Password!!")
        return render_template('login.html', is_logged_in=False, message="This email ID does not exist!")
    return render_template('login.html', is_logged_in=False)

@app.route('/admin_home')
def admin_home():
    global user_email
    if not user_email:  # Restrict access if not logged in
        return redirect(url_for('login'))
    return render_template('admin_home.html', is_logged_in=True)

@app.route('/add_recipie', methods=["GET", "POST"])
def add_recipie():
    global user_email
    if not user_email:  # Restrict access if not logged in
        return redirect(url_for('login'))
    if request.method == "POST":
        r_name = request.form['r_name']
        myfile = request.files['image']
        ingredients = request.form['ingredients']
        procedure = request.form['procedure']
        video_link = request.form['video_link']

        fn = myfile.filename
        mypath = os.path.join('static/images/', fn)
        myfile.save(mypath)
 
        query = "INSERT INTO recipies(`name`, `image`, `ingredients`, `making_procedure`, `video`) VALUES (%s, %s, %s, %s, %s)"
        values = (r_name, mypath, ingredients, procedure, video_link)
        executionquery(query, values)
        return render_template('add_recipie.html', is_logged_in=True, message="Sucessfully added!")
    return render_template('add_recipie.html', is_logged_in=True)

@app.route('/view_recipie', methods=["GET", "POST"])
def view_recipie():
    global user_email
    if not user_email:  # Restrict access if not logged in
        return redirect(url_for('login'))
    if request.method == "POST":
        id = request.form['id']
        query = "SELECT * FROM recipies WHERE id = %s"
        values = (id,)
        data = retrivequery1(query, values)
        return render_template('view_recipie.html', is_logged_in=True, data=data)

    query = "SELECT * FROM recipies"
    data = retrivequery2(query)
    return render_template('view_recipie.html', is_logged_in=True, datas=data)

@app.route('/update_recipie', methods=["POST"])
def update_recipie():
    global user_email
    if not user_email:  # Restrict access if not logged in
        return redirect(url_for('login'))
    id = request.form['id']
    r_name = request.form['r_name']
    myfile = request.files['image']
    ingredients = request.form['ingredients']
    procedure = request.form['procedure']
    video_link = request.form['video_link']
    alt = request.form['alt']

    if myfile:
        fn = myfile.filename
        mypath = os.path.join('static/images/', fn)
        myfile.save(mypath)
    else:
        mypath = alt

    query = "SELECT * FROM recipies WHERE id = %s"
    values = (id,)
    data = retrivequery1(query, values)

    query = "UPDATE recipies SET name = %s, image = %s, ingredients = %s, making_procedure = %s, video = %s WHERE id = %s"
    values = (r_name, mypath, ingredients, procedure, video_link, id)
    executionquery(query, values)

    query = "SELECT * FROM recipies"
    data = retrivequery2(query)
    return render_template('view_recipie.html', is_logged_in=True, datas=data, message="Successfully Updated!")

@app.route('/delete_recipie', methods=["POST"])
def delete_recipie():
    global user_email
    if not user_email:  # Restrict access if not logged in
        return redirect(url_for('login'))
    id = request.form['id']

    query = "DELETE FROM recipies WHERE id = %s"
    values = (id,)
    executionquery(query, values)

    query = "SELECT * FROM recipies"
    data = retrivequery2(query)
    return render_template('view_recipie.html', is_logged_in=True, datas=data, message="Successfully Deleted!!")

@app.route('/home')
def home():
    global user_email
    if not user_email:  # Restrict access if not logged in
        return redirect(url_for('login'))
    return render_template('home.html', is_logged_in=True)

@app.route('/about')
def about():
    global user_email
    # Check if user_email is set to pass the correct login status to the template
    is_logged_in = bool(user_email)
    # The page is now accessible even if the user is not logged in.
    return render_template('about.html', is_logged_in=is_logged_in)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global user_email
    if not user_email:  # Restrict access if not logged in
        return redirect(url_for('login'))
    if request.method == 'POST':
        myfile = request.files['image']
        fn = myfile.filename
        mypath = os.path.join('static/user_images/', fn)
        myfile.save(mypath)

        classes = ["burger", "butter_naan", "chai", "chapati",
                   "chole_bhature", "dal_makhani", "dhokla", "fried_rice",
                   "idli", "jalebi", "kaathi_rolls", "kadai_paneer",
                   "kulfi", "masala_dosa", "momos", "paani_puri", "pakode",
                   "pav_bhaji", "pizza", "samosa"]
        
        try:
            model = load_model("final_cnn.h5")
        except ImportError as e:
            return render_template('upload.html', is_logged_in=True, message="Error loading model: Please ensure h5py is installed.")
        except Exception as e:
            return render_template('upload.html', is_logged_in=True, message=f"Error loading model: {str(e)}")

        test_img = image.load_img(mypath, target_size=(224, 224))
        test_img = image.img_to_array(test_img)
        test_img = np.expand_dims(test_img, axis=0)
        test_img = test_img / 255.0
        
        # Perform prediction
        prediction = model.predict(test_img)
        result = classes[np.argmax(prediction)]
        print(11111111, result)
        name = result.upper()

        query = "SELECT * FROM recipies WHERE UPPER(name) = %s"
        values = (name,)
        data = retrivequery1(query, values)

        if data:
            prediction = data
        else:
            prediction = "Unknown"

        return render_template('upload.html', is_logged_in=True, path=mypath, prediction=prediction)
    return render_template('upload.html', is_logged_in=True)

@app.route('/search', methods=['GET', 'POST'])
def search():
    global user_email
    if not user_email:  # Restrict access if not logged in
        return redirect(url_for('login'))
    if request.method == 'POST':
        text = request.form['text']
        name = text.upper()

        query = "SELECT * FROM recipies WHERE UPPER(name) = %s"
        values = (name,)
        data = retrivequery1(query, values)
        print(11111111111111, data)
        if data:
            prediction = data
        else:
            prediction = "Unknown"

        return render_template('search.html', is_logged_in=True, prediction=prediction)
    return render_template('search.html', is_logged_in=True)

@app.route('/generate_recipe', methods=['GET', 'POST'])
def generate_recipe():
    global user_email
    if not user_email:  # Restrict access if not logged in
        return redirect(url_for('login'))
    if request.method == 'POST':
        session = request.form['session']
        calories = request.form['calories']
        type_cuisine = request.form['type']
        ingredients_to_use = request.form['ingredients_to_use']
        preferred = request.form['preferred']
        ingredients_not_to_use = request.form['ingredients_not_to_use']
        # Prepare the prompt for Gemini AI
        prompt = f"""
        Generate a recipe for a {session} dish with approximately {calories} calories.
        The cuisine type should be {type_cuisine}.
        Use the following ingredients: {ingredients_to_use}.
        Preferred: {preferred if preferred else 'None'}.
        Do not use the following ingredients: {ingredients_not_to_use if ingredients_not_to_use else 'None'}.
        Provide a detailed recipe description including ingredients, quantities, and step-by-step instructions.
        """
        try:
            # Initialize the Gemini model
            Genminimodel = GenerativeModel('gemini-2.5-flash')  # Adjust model name as per Gemini AI SDK
            response = Genminimodel.generate_content(prompt)
            
            # --- MODIFICATION START ---
            recipe = response.text
            # Remove the double asterisks (**) which are used for bolding in markdown
            # This cleans the output to be plain text titles/labels.
            cleaned_recipe = recipe.replace('**', '')
            # --- MODIFICATION END ---

        except Exception as e:
            # Use 'flash' or a specific message to inform the user about the error
            return render_template('generate_recipe.html', is_logged_in=True, message=f"Error generating recipe: {str(e)}")
        
        # Pass the cleaned recipe to the template
        return render_template('generate_recipe.html', is_logged_in=True, recipe=cleaned_recipe)
    return render_template('generate_recipe.html', is_logged_in=True)

if __name__ == '__main__':
    app.run(debug=True)