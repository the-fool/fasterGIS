from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, RadioField, SelectField, BooleanField, SubmitField, FileField
from wtforms.validators import Required, NumberRange, Length, regexp
import re

class AddTaskForm(Form):
    name = StringField('Quick Name', 
                       validators=[Length(0,64, 
                       'Must be less than 64 characters')])
    iterations = IntegerField('Quantity of Iterations', 
                   validators=[Required(), NumberRange(1, 100, 
                   message='Must be between 1 - 100')])
    simul_type = SelectField('Type of Simulation')
    data_set = FileField(u'Data set')
    submit = SubmitField('Create')
