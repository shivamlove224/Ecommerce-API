from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User, Product
from schemas import UserCreate, UserLogin, ProductCreate
from passlib.context import CryptContext
from typing import List

# Database URL (replace with your actual PostgreSQL URL)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:zoro%40123@localhost/fastapi"

# Database setup
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
# FastAPI setup
app = FastAPI()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Password hashing functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# Routes


@app.post("/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = get_password_hash(user.password)

    # Create the user
    new_user = User(email=user.email, hashed_password=hashed_password, name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created", "user_id": new_user.id}


@app.post("/signin")
async def signin(user: UserLogin, db: Session = Depends(get_db)):
    # Check if the user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # For simplicity, we return a mock token (replace with JWT logic)
    return {"access_token": "fake_token", "token_type": "bearer"}


@app.post("/products/", response_model=ProductCreate)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Check if the user exists
    db_user = db.query(User).filter(User.id == product.user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Create a new product
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        category=product.category,
        user_id=product.user_id,
    )

    # Add the product to the database
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@app.delete("/deleteproduct/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    # Get the product to delete
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete the product
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted", "product_id": product_id}
