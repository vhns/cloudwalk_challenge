import uvicorn
import asyncio
import statistics
from typing import Annotated, Optional
from json import dumps
from collections import deque, defaultdict

from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket
from sqlmodel import SQLModel, Field, Session, create_engine, select

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

WINDOW_SIZE = 20

history = defaultdict(lambda: deque(maxlen=WINDOW_SIZE))

def detect_anomaly(status: str, value: int):
    hist = history[status]

    if len(hist) < 5:
        hist.append(value)
        return False, None

    avg = statistics.mean(hist)
    stdev = statistics.stdev(hist) if len(hist) > 1 else 0

    hist.append(value)

    # rules
    if stdev > 0 and abs(value - avg) > 3 * stdev:
        return True, f"Spike detected: {value} vs avg {avg:.2f}"

    if value == 0 and avg > 0:
        return True, "Drop to zero"

    return False, None

class Status(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    time_stamp: str = Field(nullable=False)
    status: str = Field(nullable=False)
    count: int = Field(nullable=False)

class AuthCode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    time_stamp: str = Field(nullable=False)
    auth_code: int = Field(nullable=False)
    count: int = Field(nullable=False)

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

@app.get("/test")
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: SessionDep):
    await websocket.accept()
    last_id = 0

    while True:
        statement = (
            select(Status)
            .where(Status.id > last_id)
            .order_by(Status.id)
        )

        result = session.exec(statement)
        rows = result.all()

        if rows:
            last_id = rows[-1].id

            payload = []

            for row in rows:
                # detect anomaly
                is_anomaly, reason = detect_anomaly(row.status, row.count)

                item = row.model_dump()

                # enrich payload
                item["anomaly"] = is_anomaly
                item["reason"] = reason

                payload.append(item)

            await websocket.send_text(dumps(payload))

            print(f"Sent {len(rows)} rows (with anomaly detection). Last ID: {last_id}")

        await asyncio.sleep(1)
