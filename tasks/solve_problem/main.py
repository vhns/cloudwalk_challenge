import uvicorn
from typing import Annotated, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import SQLModel, Field, Session, create_engine, select

class Status(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    time_stamp: str = Field(nullable=False)
    status: str = Field(nullable=False)
    count: int = Field(nullable=False)

class AuthCode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    time_stamp: str = Field(nullable=False)
    auth_code: int = Field(nullable=False)
    count: int = Field(nullable=False)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/test")
def test():
    return 'foobar'

@app.post("/status")
def ingest(item: Status, session: SessionDep) -> Status:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.post("/authcodes")
def ingest(item: AuthCode, session: SessionDep) -> AuthCode:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

#if __name__ == "__main__":
#    uvicorn.run(app, access_log=False)
