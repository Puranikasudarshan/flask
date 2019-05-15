from app import db, app, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    Fname = db.Column(db.String(40), nullable=False)
    Lname = db.Column(db.String(40), nullable=False)
    phone_number = db.Column(db.String(20),  unique=True, nullable=False)
    date_of_birth = db.Column(db.Date(), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    tickets = db.relationship('Ticket', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}','{self.password}','{self.email}')"


class Passenger(db.Model):
    pnr_no = db.Column(db.String(40), primary_key=True)
    gender = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    seat_no = db.Column(db.String(20), nullable=False, unique=True)
    reservation_status = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    train_no = db.Column(db.Integer, db.ForeignKey('train.train_no'),  nullable=False)

    def __repr__(self):
        return f"Passenger('{self.pnr_no}','{self.gender}','{self.name}')"


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date(), nullable=False)
    source = db.Column(db.String(40), nullable=False)
    destination = db.Column(db.String(40), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    passengers = db.relationship('Passenger', backref='traveler', lazy=True)

    def __repr__(self):
        return f"Ticket('{self.id}','{self.date}','{self.source}')"


class Train(db.Model):
    train_no = db.Column(db.Integer, primary_key=True, autoincrement=False)
    train_type = db.Column(db.String(40), nullable=False)
    source = db.Column(db.String(40), nullable=False)
    departure_time = db.Column(db.Time(), nullable=False)
    station_code = db.Column(db.String(40), db.ForeignKey('station.station_code'), nullable=False)
    train_statuses = db.relationship('Train_status', backref='train_status', lazy=True)
    passengerses = db.relationship('Passenger', backref='passengers', lazy=True)


class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_code = db.Column(db.String(40), nullable=False)
    station_name = db.Column(db.String(40), nullable=False)
    hault = db.Column(db.String(10), nullable=False)
    arrival_time = db.Column(db.Time(), nullable=False)
    trains = db.relationship('Train', backref='arriving_train', lazy=True)


class Train_status(db.Model):
    train_name = db.Column(db.String(40), primary_key=True)
    available_seats = db.Column(db.Integer, nullable=False)
    fare = db.Column(db.Integer, nullable=False)
    waiting_seats = db.Column(db.Integer)
    train_no = db.Column(db.Integer, db.ForeignKey('train.train_no'), primary_key=True)
