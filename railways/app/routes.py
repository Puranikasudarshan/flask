from app import app, db ,bcrypt, mail
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required, logout_user, login_user
from app.forms import RegistrationForm, LoginForm, UpdateForm, BookTicketForm, SelectTrainForm, BookForm, RequestResetForm, ResetPasswordForm
from app.models import User, Passenger, Ticket, Train, Station, Train_status
from datetime import date
from flask_mail import Message
from random import randint


@app.route('/')
@app.route('/home')
def home():
    train = Train.query.all()
    station = Station.query.all()
    return render_template('Home.html',trains = train, stations = station)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        now = form.date.data
        currdate = now.strftime('%Y-%m-%d')
        user = User(username = form.username.data, password = hashed_password,\
            email = form.email.data, Fname = form.firstName.data, Lname = form.lastName.data ,\
            phone_number = form.phone.data, date_of_birth = currdate, sex = form.gender.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account has been created you can now login ', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'register', form = form )

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'login successful', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))


        else:
            flash(f'Login unsuccessful invalid username or password', 'danger')
    return render_template('login.html', title = 'login', form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f'logged out', 'success')
    return redirect(url_for('home'))

@app.route('/account', methods = ['GET', 'POST'])
@login_required
def account():
    form = UpdateForm()
    if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.email = form.email.data
            password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = password
            db.session.commit()
            flash(f'your account has been updated','success')
            return redirect(url_for('home'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    else:
        flash(f'invalid input','danger')
    return render_template('update.html', title = 'update', form = form)


@app.route('/about', methods = ['GET', 'POST'])
def about():
    return render_template('about.html', title = 'about')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', title = 'gallery')


def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

@app.route('/bookedticket')
@login_required
def bookedticket():
    page = request.args.get('page',1, type = int)
    user = User.query.filter_by(id = current_user.id).first_or_404()
    tickets = Ticket.query.filter_by(author = user).order_by(Ticket.date.desc()).paginate(page = page, per_page = 6)
    return render_template('tickets.html', title = 'booked-tickets', tickets = tickets)

@app.route('/bookedticket/<int:ticket_id>')
@login_required
def bookedticketme(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    return render_template('updatetickets.html', title = 'booked-ticket', ticket = ticket)

@app.route('/boookedticket/<int:ticket_id>/delete')
@login_required
def bookedticketdelete(ticket_id):
        ticket = Ticket.query.get_or_404(ticket_id)
        passenger = Passenger.query.filter_by(id = ticket_id).first()
        if ticket.author != current_user:
            abort(403)
        db.session.delete(passenger)
        db.session.delete(ticket)
        db.session.commit()
        flash("ticket deleted","success")
        return redirect(url_for('home'))


@app.route('/search_train',methods = ['GET','POST'])
def search_train():
    form = SelectTrainForm()
    form1 = BookForm()
    trains = []
    station = []
    train_nos = []
    if form.validate_on_submit():
        train = db.session.execute("select train_no, source, station_name,departure_time, arrival_time from train,station "+
                                  "where train.source = '"+form.source.data+"' and station.station_name = '"+form.destination.data+"' "+
                                  " and train.station_code = station.id").fetchall()
        if train:
            train_list = [(i.train_no, i.train_no) for i in train]
            form1.trains.choices = train_list
            return render_template('trains.html', trains = train, form1 = form1)
        else:
            flash('no trains found', 'danger')

    if form1.trains.data:
        return redirect(url_for('book', messages=form1.trains.data))

    return render_template('search_train.html',title = 'search', form = form)

def send_ticket_email(user, passenger):
    msg = Message('Ticket', sender = 'noreply@demo.com', recipients=[user.email])
    msg.body = f'''Ticket for your journey
    Indian Railway wishes a happy journey:
    { passenger.pnr_no,
    passenger.name,
    passenger.gender,
    passenger.age,
    passenger.seat_no,
    passenger.reservation_status,
    passenger.train_no }  please donot reply back'''

    mail.send(msg)


def seat_no_generator():
    b = "b"
    i= random_with_N_digits(2);
    seat_no = (b + str(i));
    return seat_no

@app.route('/bookticket', methods = ['GET', 'POST'])
@login_required
def book():
    trainselect = request.args['messages']
    train = db.session.execute('select source,station_name from train,station where train_no ='+trainselect+' and train.station_code = station.id').fetchall()
    train_status = db.session.execute('select fare,train_name from train_status,train where train.train_no = '+trainselect+ ' and train_status.train_no = train.train_no').fetchall()
    user = User.query.filter_by(email = current_user.email).first()
    for item in train_status:
        fare = item[0]
        name = item[1]
    for item in train:
        trainsource = item[0]
        traindestination = item[1]
    print(train_status)
    form = BookTicketForm()
    form.source.data = trainsource
    form.destination.data = traindestination
    form.fare.data = fare
    form.train_name.data = name
    if form.validate_on_submit():
        if form.Date.data < date.today():
            flash('Invalid date', 'danger')
        else:
            pnr_no = random_with_N_digits(10)
            train_statuss = Train_status.query.filter_by(train_no = trainselect).first()
            seat_no = seat_no_generator()
            if(train_statuss.available_seats) > 0:
                tickets = Ticket(date = form.Date.data, source = trainsource, destination = traindestination,
                    author = current_user)
                db.session.add(tickets)
                db.session.flush()
                passengers = Passenger(pnr_no = pnr_no, gender = form.gender.data, name = form.name.data,
                    seat_no = seat_no, reservation_status = "cnf", age = form.Age.data, traveler = tickets,
                    train_no = trainselect )
                db.session.add(passengers)
                train_statuss.available_seats -= 1
                db.session.commit()
                send_ticket_email(user, passengers)
                flash('Ticket booked', 'success')
                return redirect(url_for('home'))
            else:
                tickets = Ticket(date = form.Date.data, source = trainsource, destination = traindestination,
                    author = current_user)
                db.session.add(tickets)
                db.session.flush()
                passengers = Passenger(pnr_no = pnr_no, gender = form.gender.data, name = form.name.data,
                    seat_no = seat_no, reservation_status = "waiting", age = form.Age.data,traveler = tickets,
                    train_no = trainselect )
                db.session.add(passengers)
                train_statuss.waiting_seats += 1
                db.session.commit()
                send_ticket_email(user, passengers)
                flash('waiting list','danger')
                return redirect(url_for('home'))
    return render_template('book_a_ticket.html', title = 'Book', form = form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset request', sender = 'noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password visit following link:
{url_for('reset_token', token = token, _external = True)}

    If you did not this request then simply ignore this
    '''
    mail.send(msg)


@app.route('/reset_password', methods =['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash("an email has been sent","success")
        return redirect(url_for('login'))
    return render_template('reset_request.html',title = 'Reset Password', form=form)


@app.route('/reset_password/<token>', methods =['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("that is invalid or expired token")
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():#getting data from forms
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')#generating hashed password
        user.password = hashed_password
        db.session.commit()#commiting the changes
        flash(f'passowrd has been updated','success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title = 'Reset password', form = form)
