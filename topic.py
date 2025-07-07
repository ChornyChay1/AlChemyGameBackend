from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import null
from sqlalchemy.orm import Session
from DB import SessionLocal
from PydanticModels import *
from DB import *
from utils import get_db,decode_token

router = APIRouter()

@router.post("/adventures/{adventure_id}/topics", response_model=TopicModel)
def create_topic(adventure_id: int, topic_data: TopicCreate, db: Session = Depends(get_db)):
    # Создаем новую тему
    db_topic = Topic(
        adventure_id=adventure_id,
        topic_name=topic_data.topic_name,
        topic_text=topic_data.topic_text,
        topic_type=topic_data.topic_type.value,
        x=topic_data.x,
        y=topic_data.y,
        next_topic_id=topic_data.next_topic_id
    )
    # Добавляем объект в сессию и сохраняем изменения в базе данных
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)

    # Создание вопросов для темы
    for question_data in topic_data.questions:
        question_type = question_data.question_type
        if question_type == QuestionType.CLOSE.value:
            db_question = CloseQuestion(
                question_text=question_data.question_text,
                answer=question_data.answer,
                topic_id=db_topic.id
            )
        elif question_type == QuestionType.TEST.value:
            db_question = TestQuestion(
                question_text=question_data.question_text,
                answers=','.join(question_data.available_answers),
                correct_index=question_data.correct_index,
                topic_id=db_topic.id
            )
        elif question_type == QuestionType.COMPLIANCE.value:
            db_question = ComplianceQuestion(
                question_text=question_data.question_text,
                right_association=','.join([f"{k}:{v}" for k, v in question_data.right_association.items()]),
                topic_id=db_topic.id
            )
        elif question_type == QuestionType.RATIO.value:
            db_question = RatioQuestion(
                question_text=question_data.question_text,
                formula_id=question_data.formula_id,
                answer=question_data.answer,
                topic_id=db_topic.id
            )
        else:
            continue  # Если тип вопроса не совпадает, пропускаем

        # Добавляем вопрос в базу данных
        db.add(db_question)

    # Сохраняем изменения
    db.commit()

    return db_topic
@router.put("/topics/{topic_id}", response_model=TopicModel)
def update_topic(topic_id: int, topic: TopicCreate, db: Session = Depends(get_db)):
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    for key, value in topic.dict().items():
        setattr(db_topic, key, value)
    db.commit()
    return db_topic

@router.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    db.delete(db_topic)
    db.commit()
    return {"message": "Topic deleted"}



class AnswerCheckRequest(BaseModel):
    answers: List[str]  # Теперь это просто список строк, а не словарей
@router.post("/adventures/{adventure_id}/finish", status_code=status.HTTP_200_OK)
def finish_topic(adventure_id: int, request: Request, answer_data: AnswerCheckRequest, db: Session = Depends(get_db)):

    username = decode_token(request)
    db_user = db.query(User).filter(User.username == username).first()

    user_adventure = db.query(UserAdventure).filter(
        UserAdventure.user_id == db_user.id,
        UserAdventure.adventure_id == adventure_id
    ).first()
    
    if not user_adventure or user_adventure.current_topic_index is None:
        raise HTTPException(status_code=404, detail="No available topic to finish in this adventure")

    # Получаем текущую тему
    current_topic = db.query(Topic).filter(Topic.id == user_adventure.current_topic_index).first()
    if not current_topic:
        raise HTTPException(status_code=404, detail="Current topic not found")

    # Проверка ответов пользователя
    total_score = 0
    for question, user_answer in zip(current_topic.questions, answer_data.answers):
        score = question.check_answer(user_answer)  # Теперь это строка, а не словарь
        total_score += score

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.rating += total_score  # Добавляем общий балл к рейтингу пользователя

    # Обновляем статус текущей темы на завершенную
    user_adventure.current_topic_index = None  # Завершаем текущую тему

    # Устанавливаем следующую тему, если указано next_topic_id
    if current_topic.next_topic_id!=null:
        next_topic = db.query(Topic).filter(Topic.id == current_topic.next_topic_id).first()
        if next_topic:
            user_adventure.current_topic_index = next_topic.id 
        else:
            user_adventure.current_topic_index = 0

            # Устанавливаем следующую тему как текущую

    db.commit()  # Сохраняем все изменения в базе данных

    return {
        "message": "Current topic finished and next topic assigned if available", 
        "total_score": total_score,
        "new_rating": db_user.rating
    }


@router.post("/change_adventure/{adventure_id}", response_model=UserAdventureModel)
def change_adventure(adventure_id: int, request: Request, db: Session = Depends(get_db)):
    username = decode_token(request)  # Получаем имя пользователя из токена

    # Получаем пользователя по имени
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Проверяем, есть ли уже такое приключение у пользователя
    user_adventure = db.query(UserAdventure).filter(UserAdventure.user_id == db_user.id, UserAdventure.adventure_id == adventure_id).first()

    if user_adventure:
        # Если приключение уже есть, возвращаем его ID
        return user_adventure

    # Если приключения нет, добавляем новое приключение в таблицу UserAdventure
    new_user_adventure = UserAdventure(user_id=db_user.id, adventure_id=adventure_id, current_topic_index = 2)
    db.add(new_user_adventure)
    db.commit()
    db.refresh(new_user_adventure)
    return UserAdventureModel.from_orm(new_user_adventure)