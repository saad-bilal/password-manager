from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, NumberRange

# Login form with email, password and remember me fields
class LoginForm(FlaskForm):
    # User email
    email = StringField('Email', validators=[DataRequired(), Email()])

    # User password
    password = PasswordField('Password', validators=[DataRequired()])

    # Submit button
    submit = SubmitField('Login')

# Registration form with username, email, password and remember me fields
class RegistrationForm(FlaskForm):
    # Username
    username = StringField('Username', validators=[DataRequired()])

    # User email
    email = StringField('Email', validators=[DataRequired(), Email()])

    # User password
    password = PasswordField('Password', validators=[DataRequired()])

    # Submit button
    submit = SubmitField('Register')

# Password form with various fields for password generation and storage
class PasswordForm(FlaskForm):
    # Website for the password
    website = StringField('Website', validators=[DataRequired()])

    # Password
    password = StringField('Password')

    # Length of the password
    length = IntegerField('Length', validators=[NumberRange(min=1, max=100)], default=5)

    # Type of password
    password_type = SelectField('Password Type', choices=[('random', 'Random Password'), ('passphrase', 'Passphrase')], default='random')

    # Options for password generation
    use_random_password = BooleanField('Use Random Password', default=True)
    use_passphrase = BooleanField('Use Passphrase', default=False)
    include_uppercase = BooleanField('Include Uppercase Letters', default=True)
    include_lowercase = BooleanField('Include Lowercase Letters', default=True)
    include_numbers = BooleanField('Include Numbers', default=True)
    include_special = BooleanField('Include Special Characters', default=True)
    capitalize = BooleanField('Capitalize First Letter of Each Word', default=True)
    add_numbers = BooleanField('Add Numbers to Each Word', default=True)

    # Separator for passphrase
    separator = SelectField('Word Separator', choices=[('-', 'Hyphen'), ('_', 'Underscore'), (',', 'Comma'), ('.', 'Period'), (' ', 'Space')], default='-')

    # Submit button
    submit = SubmitField('Save')