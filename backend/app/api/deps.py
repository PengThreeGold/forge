from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db

# 导入数据库会话依赖
def get_current_db(db: Session = Depends(get_db)):
    return db