from datetime import datetime

from main.extensions import db
from sqlalchemy.orm import *


class sql_queries(db.Model):
    __tablename__ = 'sql_queries'
    Id = db.Column(db.Integer(), primary_key=True)
    Name = db.Column(db.String(), nullable=False, unique=True)
    Querry = db.Column(db.String(), nullable=False, unique=True)
    Description = db.Column(db.String())
    Github_link = db.Column(db.String())
    Last_result = db.Column(db.String())
    group_id = db.Column(db.Integer(),db.ForeignKey('group_query.id'))
    executions = relationship("sql_query_executions", backref="querry")


class group_query(db.Model):
    __tablename__ = 'group_query'
    id = db.Column(db.Integer(), primary_key=True)
    queries_id = db.Column(db.String())
    group_name = db.Column(db.String(), nullable=False)
    Last_result = db.Column(db.String())
    Description = db.Column(db.String())
    Github_link = db.Column(db.String())
    query_group = relationship("sql_queries", backref="group_query")
    execution_query = relationship("sql_query_executions", backref="exe_query")


class sql_query_executions(db.Model):
    __tablename__ = 'sql_query_executions'
    Id = db.Column(db.Integer(), primary_key=True)
    sql_querry_id = db.Column(db.Integer(), db.ForeignKey('sql_queries.Id'))
    envmt_Test = db.Column(db.Boolean(), nullable=False, default=False)
    envmt_Prod_lu = db.Column(db.Boolean(), nullable=False, default=False)
    envmt_Prod_ch = db.Column(db.Boolean(), nullable=False, default=False)
    start_date = db.Column(db.String(), nullable=False)
    end_date = db.Column(db.String(), nullable=False)
    frequency = db.Column(db.String(), nullable=False)
    Status = db.Column(db.Boolean(), nullable=False, default=True)
    Customer_Id = db.Column(db.String(), nullable=False)
    DateBegin = db.Column(db.String())
    DateEnd = db.Column(db.String())
    Margin = db.Column(db.Double())
    Name = db.Column(db.String(), nullable=False)
    Intraday_Schedule = db.Column(db.Boolean(), nullable=False)
    Intraday_schedule_Begin = db.Column(db.Time())
    Intraday_schedule_End = db.Column(db.Time())
    Intraday_schedule_Frequency = db.Column(db.Float())
    Time_Execution = db.Column(db.Time())
    Is_not_Intraday = db.Column(db.Boolean(), nullable=False)
    weekly_day = db.Column(db.String())
    have_parameters = db.Column(db.Boolean(), nullable=False)
    Send_slack_empty = db.Column(db.Boolean(), nullable=False, default=True)
    Send_mail_empty = db.Column(db.Boolean(), nullable=False, default=True)
    list_email = db.Column(db.String())
    list_cc_email = db.Column(db.String())
    Multi_Intraday = db.Column(db.Boolean(), nullable=False, default=True)
    Multi_Intraday_schedule = db.Column(db.String())
    send_to_slack = db.Column(db.Boolean(), nullable=False, default=True)
    send_mail = db.Column(db.Boolean(), nullable=False, default=True)
    file_extension = db.Column(db.String(), nullable=False)
    group_id = db.Column(db.Integer(), db.ForeignKey('group_query.id'))


def __repr__(self):
    return f'sql_queries {self.Name}'
