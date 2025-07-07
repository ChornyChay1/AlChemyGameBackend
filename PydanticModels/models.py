from typing import List, Optional, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum
from passlib.context import CryptContext

 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class FileInfo(BaseModel):
    id: int
    name: str 

class QuestionType(str, Enum):
    TEST = "TestQuestion"
    CLOSE = "CloseQuestion"
    COMPLIANCE = "ComplianceQuestion"
    RATIO = "RatioQuestion"

class QuestionBase(BaseModel):
    question_text: str
    question_type: QuestionType

class QuestionCommon(QuestionBase):
    answer: Optional[str] = ""
    formula_id: Optional[int] = 0
    left_expression: Optional[List[str]] = []
    right_expression: Optional[List[str]] = []
    right_association: Optional[Dict[str, str]] = []
    answers: Optional[List[str]] = []
    correct_index:Optional[ int] = 0
class CloseQuestionModel(QuestionBase):
    answer: str
    question_type: QuestionType = QuestionType.CLOSE

class TestQuestionModel(QuestionBase):
    answers: List[str]
    correct_index: int
    question_type: QuestionType = QuestionType.TEST

class ComplianceQuestionModel(QuestionBase):
    left_expression: List[str]
    right_expression: List[str]
    right_association: Dict[str, str]
    question_type: QuestionType = QuestionType.COMPLIANCE

class ImageQuestionModel(QuestionBase):
    formula_id: int
    answer: str
    question_type: QuestionType = QuestionType.RATIO
 
class TopicType(str, Enum):
    COMMON = "CommonTopic"
    PRACTICAL = "PracticalTopic"

class TopicModel(BaseModel):
    id: int
    topic_name: str
    topic_text: str
    questions: List[QuestionCommon]  
    topic_type: TopicType
    next_topic_id: Optional[int]
    theory_id:Optional[int]
    video_id:Optional[int]
    x: int
    y: int

    class Config:
        orm_mode = True

 
class TopicCreate(BaseModel):
    topic_name: str
    topic_text: str
    questions: List[QuestionCommon]
    topic_type: TopicType
    x:int
    y:int
    next_topic_id: Optional[int]
    theory_id:Optional[int]=0
    video_id:Optional[int]=0


class AdventureModel(BaseModel):
    id:int
    name: str
    adventure_text:str
    image_id: int
    topics: List[TopicModel]

class AdventureCreate(BaseModel):
    name: str
    image_id: int 
    adventure_text:str



class UserAdventureBase(BaseModel):
    user_id: int
    adventure_id: int

class UserAdventureCreate(UserAdventureBase):
    pass

class UserAdventureModel(UserAdventureBase):
    id: int
    current_topic_index: int = 0   

    class Config:
        orm_mode = True
        from_attributes = True   



class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

 

class UserDB(UserBase):
    hashed_password: str
    adventures: List[UserAdventureModel] = []
    completed_adventures: List[UserAdventureModel] = []
    rating: int = 0
 
class UserGet(UserBase):
    id: int
    adventures: List[UserAdventureModel] = []
    completed_adventures: List[UserAdventureModel] = []
    rating: int = 0
    total_adventures: int = 0
    completed_adventures_count: int = 0
    progress_percentage: float = 0.0
    class Config:
        orm_mode = True
        from_attributes = True  

