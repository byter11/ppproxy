from . import db

class Filter(db.Model):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(80), unique=True, nullable=False)
  site = db.Column(db.String(120), unique=True, nullable=False)

  def __repr__(self):
    return f'<Filter {self.name} | {self.site}'