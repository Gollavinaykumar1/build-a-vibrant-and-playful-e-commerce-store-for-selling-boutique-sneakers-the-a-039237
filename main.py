from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from sqlalchemy import create_engine

# Database setup
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI setup
app = FastAPI()

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Crypt context
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

# SQLAlchemy models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class Sneaker(Base):
    __tablename__ = "sneakers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)

class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    sneaker_id = Column(Integer)

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

class SneakerRequest(BaseModel):
    name: str
    price: float
    description: str

# JWT functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "secret_key", algorithm="HS256")
    return encoded_jwt

# Login and registration endpoints
@app.post("/api/v1/auth/login", response_model=Token)
async def login_for_access_token(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(form_data.email, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/register", response_model=RegisterRequest)
async def register_user(register_data: RegisterRequest, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(register_data.password)
    db_user = User(email=register_data.email, username=register_data.username, hashed_password=hashed_password)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already taken",
        )
    return register_data

# Sneaker endpoints
@app.get("/api/v1/sneakers", response_model=List[SneakerRequest])
async def read_sneakers(db: Session = Depends(get_db)):
    sneakers = db.query(Sneaker).all()
    return jsonable_encoder(sneakers)

@app.post("/api/v1/sneakers", response_model=SneakerRequest)
async def create_sneaker(sneaker_data: SneakerRequest, db: Session = Depends(get_db)):
    db_sneaker = Sneaker(name=sneaker_data.name, price=sneaker_data.price, description=sneaker_data.description)
    db.add(db_sneaker)
    db.commit()
    db.refresh(db_sneaker)
    return jsonable_encoder(db_sneaker)

# Cart endpoints
@app.get("/api/v1/cart", response_model=List[SneakerRequest])
async def read_cart(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    cart = db.query(Cart).filter(Cart.user_id == user.id).all()
    sneakers = []
    for item in cart:
        sneaker = db.query(Sneaker).filter(Sneaker.id == item.sneaker_id).first()
        sneakers.append(sneaker)
    return jsonable_encoder(sneakers)

@app.post("/api/v1/cart", response_model=SneakerRequest)
async def add_to_cart(sneaker_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    db_cart = Cart(user_id=user.id, sneaker_id=sneaker_id)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    sneaker = db.query(Sneaker).filter(Sneaker.id == sneaker_id).first()
    return jsonable_encoder(sneaker)