from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user,logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'app'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_with_me.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)  # Initialize login manager with the Flask app

# Your models and routes go here...

class User(UserMixin, db.Model):  # Inherit from UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Experiences(db.Model):  # Adjusted model name to singular
    id = db.Column(db.Integer, primary_key=True)
    place = db.Column(db.String(100), nullable=False)
    contact_details_email = db.Column(db.String(100))  # Correct column name
    contact_details_phone = db.Column(db.String(20))   # Correct column name
    experience_text = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('experiences', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def start():
    return render_template('signin.html')

@app.route('/index')
def index():
    experiences = Experiences.query.all()  # Adjusted model name
    return render_template('index.html', experiences=experiences)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)  # Log in the user
            return redirect(url_for('index'))
        else:
            return render_template('signin.html', error="Invalid username or password")
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('signin'))
    return render_template('signup.html')

@app.route('/addexp', methods=['GET', 'POST'])
def addexp():
    if request.method == 'POST':
        place = request.form['place']
        contact_details_email = request.form['email']
        contact_details_phone = request.form['contact_number']
        experience_text = request.form['experience']
        
        # Check if mandatory fields are filled
        if not (place and contact_details_email and experience_text):
            return render_template('home.html', error="Please fill out all mandatory fields")
        
        # Get the current user's ID
        user_id = current_user.id

        # Create a new Experience object with the provided data
        new_experience = Experiences(place=place, 
                                    contact_details_email=contact_details_email, 
                                    contact_details_phone=contact_details_phone,
                                    experience_text=experience_text,
                                    user_id=user_id)  # Assign the user_id
                                    
        # Add the new experience to the database session and commit the transaction
        db.session.add(new_experience)
        db.session.commit()
        
        # Redirect the user back to the home page
        return redirect(url_for('index'))
    
    return render_template('addexp.html')

@app.route('/signout')
def signout():
    logout_user()  # Log out the current user
    return redirect(url_for('start')) 


@app.route('/empty_tables')
def empty_tables():
    try:
        db.session.query(User).delete()
        db.session.query(Experiences).delete()
        db.session.commit()
        return 'Tables emptied successfully'
    except Exception as e:
        db.session.rollback()
        return f'Error: {str(e)}'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
