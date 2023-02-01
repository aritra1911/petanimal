from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

class RegistrationForm(FlaskForm):
    category = SelectField(
        'Category* : ',
        choices=[('dog', 'Dog'), ('cat', 'Cat')],
        validators=[DataRequired()]
    )
    breed = StringField('Breed : ')
    price = StringField('Price* : ', validators=[DataRequired()])
    owner = StringField('Owner* : ', validators=[DataRequired()])
    submit = SubmitField('Submit')