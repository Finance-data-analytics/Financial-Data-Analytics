import re

from wtforms import *
from wtforms.validators import *
from wtforms.widgets import *
from flask_wtf import *
from main.models import *


class AddQuerry(FlaskForm):

    def validate_group_name(form, field):
        num_queries = sum(1 for query in form.Querry if query.data.strip())
        if num_queries > 1 and not field.data.strip():
            raise ValidationError('Group name is required when there are multiple SQL queries.')

    def validate_sql_content(form, field):
        sanitized_query = re.sub(r'\/\*[\s\S]*?\*\/', '', field.data)
        sanitized_query = re.sub(r'--.*$', '', sanitized_query, flags=re.MULTILINE)
        queries = [q.strip() for q in sanitized_query.split(';') if q.strip()]

        for query in queries:
            if not (query.startswith('SELECT') or query.startswith('DELETE') or query.startswith('UPDATE')):
                raise ValidationError(
                    f'The query {query} is starting with {query.split()[0]}. All queries must start with either SELECT, DELETE, or UPDATE in capital letters!')

    Name = StringField(label='Name Of The Query', validators=[DataRequired()])
    group_name = StringField(validators=[validate_group_name], default=None)
    Querry = FieldList(TextAreaField(label='SQL Code Of The Query', validators=[DataRequired(), validate_sql_content]),
                       min_entries=1)
    Description = TextAreaField(label='Description of the query')
    Github_link = StringField(label='link to github issue')
    submit = SubmitField(label='Add The Query')

    def validate_Name(self, name_check):
        name = sql_queries.query.filter_by(Name=name_check.data).first()
        if name:
            raise ValidationError('Query Name already taken')


class ScheduleQuerry(FlaskForm):
    Name = StringField(label="Name of the execution", validators=[InputRequired()])

    selected_query_ids = StringField(widget=HiddenInput())

    selected_customer_ids = StringField(widget=HiddenInput(), validators=[Optional()])

    DateBegin = SelectField(label='Beginning of the Search',
                            choices=[('None', 'None'), ('CURRENT_DATE-1', 'CURRENT_DATE-1'),
                                     ('CURRENT_DATE-2', 'CURRENT_DATE-2'),
                                     ('CURRENT_DATE-3', 'CURRENT_DATE-3'), ('CURRENT_DATE-3', 'CURRENT_DATE-3'),
                                     ('CURRENT_DATE-4', 'CURRENT_DATE-4')], validators=[Optional()])

    DateEnd = SelectField(label='End of the Search',
                          choices=[('None', 'None'), ('CURRENT_DATE', 'CURRENT_DATE'),
                                   ('CURRENT_DATE-1', 'CURRENT_DATE-1'),
                                   ('CURRENT_DATE-2', 'CURRENT_DATE-2'), ('CURRENT_DATE-3', 'CURRENT_DATE-3'),
                                   ('CURRENT_DATE-3', 'CURRENT_DATE-3'), ('CURRENT_DATE-4', 'CURRENT_DATE-4')],
                          validators=[Optional()])

    Margin = DecimalField(label='Margin', validators=[Optional()])

    envmt_Test = BooleanField(label='Test Environment', default=False)

    envmt_Prod_lu = BooleanField(label='Prod LU Environment', default=True)

    envmt_Prod_ch = BooleanField(label='Prod CH Environment', default=False)

    frequency = SelectField('Frequency', choices=[('daily', 'Daily'), ('weekly', 'Weekly')],
                            validators=[DataRequired()])

    start_date = SelectField('Beginning',
                             choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
                                      ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'),
                                      ('sunday', 'Sunday')], validators=[DataRequired()])
    end_date = SelectField('End',
                           choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
                                    ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'),
                                    ('sunday', 'Sunday')], validators=[DataRequired()])

    Intraday_Schedule = BooleanField(label='Intraday Schedule', default=False)

    Intraday_schedule_Begin = TimeField(label='Intraday Schedule Begin', validators=[Optional()])

    Intraday_schedule_End = TimeField(label='Intraday Schedule End', validators=[Optional()])

    Intraday_schedule_Frequency = FloatField(label='Intraday Schedule Frequency', validators=[Optional()])

    Time_Execution = TimeField(label='Time Execution', validators=[Optional()])

    Is_not_Intraday = BooleanField(label='Is Not Intraday', default=True)

    Multi_Intraday = BooleanField(label='Multi-Intraday', default=False)

    multi_intraday_data = HiddenField()

    weekly_day = SelectMultipleField(
        label="day of the week",
        choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'),
                 ('wednesday', 'Wednesday'), ('thursday', 'Thursday'),
                 ('friday', 'Friday'), ('saturday', 'Saturday'),
                 ('sunday', 'Sunday')]
    )

    have_parameters = BooleanField(label='Does the querry have parameters(margin,customer,date)', default=False)

    Send_slack_empty = BooleanField(label='Sent the report to Slack when no row returned?', default=True)

    Send_mail_empty = BooleanField(label='Sent the report by mail when no row returned?', default=True)

    list_email = StringField(label="List of email to send the report")

    list_email_cc = StringField(label="List of email to cc")

    send_slack = BooleanField(label='Send the report to slack ?', default=True)

    send_mail = BooleanField(label='Send the report by mail ?', default=False)

    file_extension = SelectMultipleField(
        label="File extension",
        choices=[('None', 'None'),('xlsx', 'Xlsx'), ('csv', 'CSV')]
    )

    submit = SubmitField(label='Schedule The Query')
