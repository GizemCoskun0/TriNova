from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Text, DateTime, Boolean
from datetime import datetime
from sqlalchemy.orm import relationship
from database import Base

user_allergies = Table(
    "user_allergies",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("allergy_id", Integer, ForeignKey("allergies.id")),
)

user_diets = Table(
    "user_diets",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("diet_id", Integer, ForeignKey("diets.id")),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    inventory_items = relationship("Inventory", back_populates="owner")
    allergies = relationship("Allergy", secondary=user_allergies, back_populates="users")
    diets = relationship("Diet", secondary=user_diets, back_populates="users")

    meal_plans = relationship("MealPlan", back_populates="owner")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    amount = Column(Float, default=1.0)
    unit = Column(String, default="unit")
    
    owner = relationship("User", back_populates="inventory_items")

class Allergy(Base):
    __tablename__ = "allergies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    users = relationship("User", secondary=user_allergies, back_populates="allergies")

class Diet(Base):
    __tablename__ = "diets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    users = relationship("User", secondary=user_diets, back_populates="diets")

class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user_email = Column(String, index=True)

    plan_day = Column(String, nullable=False)
    meal_type = Column(String, nullable=False)
    recipe_id = Column(Integer)
    recipe_title = Column(String, nullable=False)
    recipe_image = Column(String)
    source_url = Column(String)

    ready_in_minutes = Column(Integer)
    servings = Column(Integer)

    ingredients = Column(Text)
    instructions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="meal_plans")
class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user_email = Column(String, index=True)

    item_name = Column(String, nullable=False)
    amount = Column(Float, default=1.0)
    unit = Column(String, default="unit")

    source_recipe_title = Column(String)
    is_checked = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)    

class FavoriteRecipe(Base):
    __tablename__ = "favorite_recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    recipe_id = Column(Integer)
    recipe_title = Column(String, nullable=False)
    recipe_image = Column(String)
    source_url = Column(String)
    ingredients = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)    