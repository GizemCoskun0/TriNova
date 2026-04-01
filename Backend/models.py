from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Many-to-Many
# The link between users and allergies
user_allergies = Table(
    'user_allergies', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('allergy_id', Integer, ForeignKey('allergies.id'))
)

# The link between users and diets
user_diets = Table(
    'user_diets', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('diet_id', Integer, ForeignKey('diets.id'))
)

# Main Tables
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    # Relationships
    allergies = relationship("Allergy", secondary=user_allergies, back_populates="users")
    diets = relationship("Diet", secondary=user_diets, back_populates="users")
    favorites = relationship("FavoriteRecipe", back_populates="user")

class Allergy(Base):
    __tablename__ = 'allergies'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False) # "peanuts", "dairy",etc.
    
    users = relationship("User", secondary=user_allergies, back_populates="allergies")

class Diet(Base):
    __tablename__ = 'diets'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False) # "vegan", "vegetarian",etc.
    
    users = relationship("User", secondary=user_diets, back_populates="diets")

class FavoriteRecipe(Base):
    __tablename__ = 'favorite_recipes'
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(String(50), nullable=False) # Recipe ID to be received from the external API (Spoonacular)
    title = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="favorites")