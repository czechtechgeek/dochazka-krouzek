from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)  # HH:MM
    sort_order = db.Column(db.Integer, default=0)
    children = db.relationship('Child', backref='group', lazy=True, cascade='all, delete-orphan')

    def child_count(self):
        return len(self.children)

class Child(db.Model):
    __tablename__ = 'children'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    subgroup = db.Column(db.String(100), nullable=True, default=None)

    def __repr__(self):
        return self.name

    def subgroups(children):
        """Group children by subgroup, return list of (subgroup_name, [children])."""
        from collections import OrderedDict
        groups = OrderedDict()
        for c in children:
            sg = c.subgroup or ''
            if sg not in groups:
                groups[sg] = []
            groups[sg].append(c)
        return list(groups.items())

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # present, absent, excused
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)

    child = db.relationship('Child', backref='attendance_records', lazy=True)
    group = db.relationship('Group', backref='attendance_records', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('child_id', 'date', name='unique_attendance_per_child_date'),
    )