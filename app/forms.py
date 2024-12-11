from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, TextAreaField, DateField, SubmitField,
                     SelectMultipleField, IntegerField, BooleanField, FloatField, SelectField, FieldList, FormField)
from wtforms.validators import InputRequired, Email, EqualTo, Optional, Length, NumberRange


class SignUpForm(FlaskForm):
    email = StringField('email',
                        validators=[InputRequired(), Email(message="Enter a valid email")],
                        render_kw={"class": "form-control", "placeholder": "Enter Email"})

    first_name = StringField('first_name',
                             validators=[InputRequired()],
                             render_kw={"class": "form-control", "placeholder": "Enter First Name"})

    username = StringField('username',
                           validators=[InputRequired()],
                           render_kw={"class": "form-control", "placeholder": "Enter Username"})

    password = PasswordField('password',
                             validators=[InputRequired(), EqualTo('confirm', message="Passwords don't match")],
                             render_kw={"class": "form-control", "placeholder": "Enter Password"})

    confirm = PasswordField('confirm',
                            validators=[InputRequired()],
                            render_kw={"class": "form-control", "placeholder": "Confirm Password"})

    birthdate = DateField('birthdate',
                          validators=[Optional()],
                          render_kw={"class": "form-control", "placeholder": "dd-mm-yyyy"})

    gender = SelectField('gender',
                         validators=[Optional()],
                         choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                         render_kw={"class": "form-control", "placeholder": "Select gender"})

    city = StringField('city',
                       validators=[Optional(), Length(max=150)],
                       render_kw={"class": "form-control", "placeholder": "Enter city"})

    county = StringField('county',
                         validators=[Optional(), Length(max=150)],
                         render_kw={"class": "form-control", "placeholder": "Enter county"})

    country = StringField('country',
                          validators=[Optional(), Length(max=150)],
                          render_kw={"class": "form-control", "placeholder": "Enter country"})

    submit = SubmitField('Submit',
                         render_kw={"class": "btn btn-primary btn-lg w-100"})


class UpdateForm(FlaskForm):
    email = StringField('email',
                        validators=[Optional(), Email(message="Enter a valid email")],
                        render_kw={"class": "form-control", "placeholder": "Enter Email"})

    first_name = StringField('first_name',
                             validators=[Optional()],
                             render_kw={"class": "form-control", "placeholder": "Enter First Name"})

    username = StringField('username',
                           validators=[Optional()],
                           render_kw={"class": "form-control", "placeholder": "Enter Username"})

    password = PasswordField('password',
                             validators=[Optional(), EqualTo('confirm', message="Passwords don't match")],
                             render_kw={"class": "form-control", "placeholder": "Enter Password"})

    confirm = PasswordField('confirm',
                            validators=[Optional()],
                            render_kw={"class": "form-control", "placeholder": "Confirm Password"})

    birthdate = DateField('birthdate',
                          validators=[Optional()],
                          render_kw={"class": "form-control", "placeholder": "dd-mm-yyyy"})

    gender = SelectField('gender',
                         choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                         render_kw={"class": "form-control", "placeholder": "Select gender"})

    city = StringField('city',
                       validators=[Optional(), Length(max=150)],
                       render_kw={"class": "form-control", "placeholder": "Enter city"})

    county = StringField('county',
                         validators=[Optional(), Length(max=150)],
                         render_kw={"class": "form-control", "placeholder": "Enter county"})

    country = StringField('country',
                          validators=[Optional(), Length(max=150)],
                          render_kw={"class": "form-control", "placeholder": "Enter country"})

    submit = SubmitField('Submit',
                         render_kw={"class": "btn btn-primary btn-lg w-100"})


class LogInForm(FlaskForm):
    email = StringField('email',
                        validators=[InputRequired(), Email(message="Enter a valid email")],
                        render_kw={"class": "form-control", "placeholder": "Enter Email"})

    password = PasswordField('password',
                             validators=[InputRequired()],
                             render_kw={"class": "form-control", "placeholder": "Enter Password"})

    submit = SubmitField('Submit',
                         render_kw={"class": "btn btn-primary btn-lg w-100"})


class WorkoutForm(FlaskForm):
    name = StringField('name',
                       validators=[InputRequired()],
                       render_kw={"class": "form-control", "placeholder": "Enter Workout Name"})

    description = StringField('description',
                              validators=[Optional(), Length(max=1000)],
                              render_kw={"class": "form-control", "placeholder": "Enter Description"})

    exercises = SelectMultipleField('exercises',
                                    coerce=int,
                                    validators=[InputRequired()],
                                    render_kw={"class": "form-control select2-multiple", "multiple": "multiple"})

    submit = SubmitField('Submit',
                         render_kw={"class": "btn btn-primary btn-lg w-100"})


class ExerciseSetForm(FlaskForm):
    set_number = IntegerField('Set Number', validators=[InputRequired()])
    reps = IntegerField('Reps', validators=[InputRequired(), NumberRange(min=1)])
    weight = FloatField('Weight (optional)', validators=[Optional()])
    is_completed = BooleanField('Completed')
    rest_time = IntegerField('Rest Time (seconds)', validators=[Optional()])


class SessionExerciseForm(FlaskForm):
    exercise_id = SelectField('Exercise', coerce=int, validators=[InputRequired()])
    sets = FieldList(FormField(ExerciseSetForm), min_entries=1)


class WorkoutSessionForm(FlaskForm):
    workout_id = SelectField('Workout Plan (Optional)', coerce=int, validators=[Optional()])
    notes = TextAreaField('Session Notes', validators=[Optional()])
    exercises = FieldList(FormField(SessionExerciseForm), min_entries=1)
    submit = SubmitField('Complete Workout')


class EmptyWorkoutForm(FlaskForm):
    exercise_id = SelectField('Exercise', coerce=int, validators=[InputRequired()])
    sets = FieldList(FormField(ExerciseSetForm), min_entries=1)
    submit = SubmitField('Log Exercise')


class HeightForm(FlaskForm):
    height = IntegerField('height', validators=[InputRequired()])
    date = DateField('date', validators=[InputRequired()])
    submit = SubmitField('Log Height')


class WeightForm(FlaskForm):
    weight = FloatField('weight', validators=[InputRequired()])
    date = DateField('date', validators=[InputRequired()])
    submit = SubmitField('Log Weight')
