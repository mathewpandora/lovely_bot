from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, get_db, init_db
from app.load_credentials import load_credentials_from_file
from app.models import Credential, Valentine
from app.schemas import CredentialRead, ValentineCreate, ValentineRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with async_session() as session:
        loaded = await load_credentials_from_file(session)
        if loaded:
            print(f"Loaded {loaded} credentials from file")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/credentials/{credential_id}", response_model=CredentialRead)
async def get_credential(credential_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Credential).where(Credential.id == credential_id))
    cred = result.scalar_one_or_none()
    if cred is None:
        raise HTTPException(status_code=404, detail="Credential not found")
    return cred


@app.post("/valentines", response_model=ValentineRead)
async def create_valentine(body: ValentineCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Credential).where(Credential.id == body.recipient_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    val = Valentine(
        text=body.text,
        track_link=body.track_link,
        recipient_id=body.recipient_id,
    )
    db.add(val)
    await db.commit()
    await db.refresh(val)
    return val


@app.get("/valentines/{valentine_id}", response_model=ValentineRead)
async def get_valentine(valentine_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Valentine).where(Valentine.id == valentine_id))
    val = result.scalar_one_or_none()
    if val is None:
        raise HTTPException(status_code=404, detail="Valentine not found")
    return val


@app.get("/valentines/recipient/{recipient_id}", response_model=list[ValentineRead])
async def list_valentines_by_recipient(recipient_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Valentine).where(Valentine.recipient_id == recipient_id))
    return list(result.scalars().all())
