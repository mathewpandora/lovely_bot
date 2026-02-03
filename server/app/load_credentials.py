from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Credential


async def load_credentials_from_file(session: AsyncSession) -> int:
    path = Path(settings.ids_passwords_path)
    if not path.exists():
        return 0
    result = await session.execute(select(Credential).limit(1))
    if result.scalar_one_or_none() is not None:
        return 0
    count = 0
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            part = line.split(",", 1)
            if len(part) != 2:
                continue
            uid, pwd = part[0].strip(), part[1].strip()
            if not uid.isdigit():
                continue
            session.add(Credential(id=int(uid), password=pwd))
            count += 1
    await session.commit()
    return count
