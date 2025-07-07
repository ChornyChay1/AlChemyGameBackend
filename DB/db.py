from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Text, Table
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from typing import List, Dict
from enum import Enum
from sqlalchemy.dialects.sqlite import JSON  




Base = declarative_base()
class FileTable(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

 
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rating = Column(Integer, default=0)
 
    adventures = relationship("UserAdventure", back_populates="user") 

 
class Adventure(Base):
    __tablename__ = 'adventures'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    image_id = Column(Integer, nullable=False)
    rating = Column(Integer, default=0)
    is_finished = Column(Boolean, default=False)
    adventure_text = Column(String)


    topics = relationship("Topic", back_populates="adventure")
    user_adventures = relationship("UserAdventure", back_populates="adventure")
    
    def __repr__(self):
        return f"<Adventure(name={self.name}, rating={self.rating}, is_finished={self.is_finished})>"

 
class TopicType(Enum):
    COMMON = "CommonTopic" 

 
class Topic(Base):
    __tablename__ = 'topic'
    id = Column(Integer, primary_key=True,  autoincrement=True)
    topic_name = Column(Text)
    topic_text = Column(Text)
    topic_type = Column(String, nullable=False, default=TopicType.COMMON.value)
    next_topic_id = Column(Integer)
    video_id = Column(Integer, default=0)
    theory_id = Column(Integer, default=0)

 
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    adventure_id = Column(Integer, ForeignKey('adventures.id'))
    adventure = relationship("Adventure", back_populates="topics")
     

class QuestionType(Enum):
    TEST = "TestQuestion"
    CLOSE = "CloseQuestion"
    COMPLIANCE = "ComplianceQuestion"
    RATIO = "RatioQuestion"

# Базовый класс для вопросов
class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey('topic.id'))

    topic = relationship("Topic", backref="questions")

    __mapper_args__ = {
        'polymorphic_identity': 'question',
        'polymorphic_on': question_type
    }

    def get_answer(self) -> str:
        raise NotImplementedError

    def check_answer(self, answer: str) -> int:
        raise NotImplementedError

    def get_question(self) -> str:
        return self.question_text

    def get_type(self) -> str:
        return self.question_type


 

class CloseQuestion(Question):
    __tablename__ = 'close_questions'
    
    id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    answer = Column(String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': QuestionType.CLOSE.value,
    }

    def get_answer(self) -> str:
        return self.answer

    def check_answer(self, answer: str) -> int:
        return 1 if answer == self.answer else 0


class TestQuestion(Question):
    __tablename__ = 'test_questions'

    id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    _answers = Column("answers", Text)  # Используем _answers для хранения в базе данных
    correct_index = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': QuestionType.TEST.value,
    }

    @property
    def answers(self):
        # Преобразуем строку в список при доступе к данным
        return self._answers.split(',') if self._answers else []

    @answers.setter
    def answers(self, value):
        # Преобразуем список в строку перед сохранением в базе данных
        self._answers = ','.join(value)

    def get_answer(self) -> str:
        return self.answers[self.correct_index]  # Используем answers как список

    def check_answer(self, answer_index: str) -> int:
        return 1 if int(answer_index) == self.correct_index else 0


class ComplianceQuestion(Question):
    __tablename__ = 'compliance_questions'

    id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    right_association = Column(JSON)  # Используем JSON тип для хранения ассоциаций

    __mapper_args__ = {
        'polymorphic_identity': QuestionType.COMPLIANCE.value,
    }

    def get_answer(self) -> Dict[str, str]:
        return self.right_association

    def check_answer(self, answer_association: Dict[str, str]) -> int:
        return 1 if answer_association == self.right_association else 0



class RatioQuestion(Question):
    __tablename__ = 'ratio_questions'

    id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    formula_id = Column(Integer)
    answer = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': QuestionType.RATIO.value,
    }

    def get_answer(self) -> str:
        return self.answer

    def check_answer(self, answer: str) -> int:
        return 1 if answer == self.answer else 0


class UserAdventure(Base):
    __tablename__ = 'user_adventures'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    adventure_id = Column(Integer, ForeignKey('adventures.id'))
    current_topic_index = Column(Integer, default=0)
    
    user = relationship("User", back_populates="adventures")
    adventure = relationship("Adventure", back_populates="user_adventures")

    def __repr__(self):
        return f"<UserAdventure(user_id={self.user_id}, adventure_id={self.adventure_id})>"

 
DATABASE_URL = "sqlite:///game_database.db"   
engine = create_engine(DATABASE_URL, echo=True)

# Создаем все таблицы
Base.metadata.create_all(engine)

 
SessionLocal = sessionmaker(bind=engine)
