from flask import Flask, render_template, redirect, url_for, abort
from models import Pet
from flask_wtf import FlaskForm
from forms import RegistrationForm
from db import DB, DBConnNotOpen, OwnerDoesNotExist
from psycopg2 import OperationalError, errors, InterfaceError
from werkzeug.wrappers import Response
from typing import Any, Optional, Tuple

app: Flask = Flask(__name__)
app.config['SECRET_KEY'] = '1D1dn0t5tE4L7Hi5s3cR37k3Y'
db: DB = DB()

def init_db() -> None:
    try:
        db.connect()
    except OperationalError as oe:
        print('Failed to connect to database:', str(oe))
        return

    try:
        db.create_all()
        db.commit()
    except DBConnNotOpen:
        print('No database connection!!  Connect to database first!')
    except errors.InFailedSqlTransaction as sql_err:
        print('Failed to execute query:', str(sql_err))
    except InterfaceError as ie:
        print('Failed to execute query:', str(ie))

@app.errorhandler(404)
def not_found(err) -> Tuple[str, int]:
    return render_template('404.html', err=err.description['err']), 404

@app.route('/')
def index() -> str:
    try:
        return render_template('index.html', pets=db.get_pets())
    except DBConnNotOpen:
        print('No database connection!!  Connect to database first!')
    except errors.InFailedSqlTransaction as sql_err:
        print('Failed to execute query:', str(sql_err))
    except InterfaceError as ie:
        print('Failed to execute query:', str(ie))
    return render_template('index.html', pets=None)

@app.route('/register', methods=['GET', 'POST'])
def register() -> str | Response:
    form: FlaskForm = RegistrationForm()
    if form.validate_on_submit():
        try:
            db.insert(form)
            db.commit()
        except DBConnNotOpen:
            print('No database connection!!  Connect to database first!')
        except errors.InFailedSqlTransaction as sql_err:
            print('Failed to execute query:', str(sql_err))
        except InterfaceError as ie:
            print('Failed to execute query:', str(ie))
        except OwnerDoesNotExist:
            print('Owner `' + form.owner.data + '\' doesn\'t exist!')
        return redirect(url_for('index'))
    return render_template('registration_form.html', form=form)

@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id: int) -> str | Response:
    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            db.update(id, form)
            db.commit()
        except DBConnNotOpen:
            print('No database connection!!  Connect to database first!')
        except errors.InFailedSqlTransaction as sql_err:
            print('Failed to execute query:', str(sql_err))
        except InterfaceError as ie:
            print('Failed to execute query:', str(ie))
        except OwnerDoesNotExist:
            print('Owner `' + form.owner.data + '\' doesn\'t exists!')
        return redirect(url_for('index'))

    pet: Optional[Pet] = db.get_pet(id)
    if not pet:
        abort(404, { 'err': 'Pet with id ' + str(id) + ' not found' })
    form.category.data = pet.get_category()
    form.breed.data = pet.get_breed()
    form.price.data = str(pet.get_price())
    form.owner.data = pet.get_owner()
    return render_template('registration_form.html', form=form)

@app.route('/delete/<id>')
def delete(id: int) -> Response:
    try:
        db.delete(id)
        db.commit()
    except DBConnNotOpen:
        print('No database connection!!  Connect to database first!')
    except errors.InFailedSqlTransaction as sql_err:
        print('Failed to execute query:', str(sql_err))
    except InterfaceError as ie:
        print('Failed to execute query:', str(ie))
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    if db.has_connection():
        app.run(debug=True)