import sqlalchemy
import databases
from notes_proj.config import config
metadata=sqlalchemy.MetaData()
note_table=sqlalchemy.Table("notes",metadata,sqlalchemy.Column("id",sqlalchemy.Integer,primary_key=True),sqlalchemy.Column("title",sqlalchemy.String,nullable=False),sqlalchemy.Column("body",sqlalchemy.String,nullable=False),sqlalchemy.Column("user_id",sqlalchemy.Integer,sqlalchemy.ForeignKey("users.id")),sqlalchemy.Column("doc",sqlalchemy.DATE),sqlalchemy.UniqueConstraint("user_id","title",name="user_title"))
#sqlalchemy.UniqueConstraint is used to enforce composite unique constraint for user lvl titles to be unique hence both user_id+title must be unique in unison
user_table=sqlalchemy.Table("users",metadata,sqlalchemy.Column("id",sqlalchemy.Integer,primary_key=True),sqlalchemy.Column("email",sqlalchemy.String,nullable=False),sqlalchemy.Column("password",sqlalchemy.String,nullable=False),sqlalchemy.Column("isConfirmed",sqlalchemy.Boolean,default=False))
engine=sqlalchemy.create_engine(url=config.DATABASE_URL)
metadata.create_all(engine)
database=databases.Database(url=config.ASYNC_DATABASE_URL,force_rollback=config.DB_FORCE_ROLLBACK)
try:
  with engine.connect() as connection:
    print("Connection successful!")
except Exception as e:
  print(f"Failed to connect: {e}")
