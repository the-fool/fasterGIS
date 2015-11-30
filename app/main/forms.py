from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, RadioField, SelectField, BooleanField, SubmitField
from wtforms.validators import Required, NumberRange, Length

class AddTaskForm(Form):
    name = StringField('Quick Name', 
                       validators=[Length(0,64, 
                       'Must be less than 64 characters')])
    iterations = IntegerField('Quantity of Iterations', 
                   validators=[Required(), NumberRange(1, 1000, 
                   message='Must be between 1 - 1000')])
    simul_type = SelectField('Type of Simulation')
    submit = SubmitField('Create')
