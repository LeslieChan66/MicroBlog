from sqlalchemy import DateTime

from app.exts import db
from datetime import datetime
class Posts(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    content=db.Column(db.Text)
    timestamp = db.Column(DateTime,nullable=False,default=datetime.utcnow())
    rid = db.Column(db.Integer,index=True,default=0)
    uid = db.Column(db.Integer,db.ForeignKey('user.id'))
    __mapper_args__={
        "order_by":timestamp.desc()
    }






