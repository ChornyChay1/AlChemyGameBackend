
from Logic.question import CloseQuestion
from Logic.topic import CommonTopic, Event
from Logic.adventure import Adventure
from Logic.user import User

def test_adventure_system():
    # Создание вопросов
    q1 = CloseQuestion("Что такое Python?", "Язык программирования")
    q2 = CloseQuestion("Какой символ используется для комментариев в Python?", "#")
    q3 = CloseQuestion("Что такое переменная?", "Хранение данных")
    q4 = CloseQuestion("Какой оператор используется для сложения?", "+")

    event  = Event(100,200)
 
    topic1 = CommonTopic(topic_id=1, video_id=None, questions=[q1, q2],event=event)
    topic2 = CommonTopic(topic_id=2, video_id=None, questions=[q3, q4],event=event)

 
    adventure = Adventure(name="Приключение 1", image_id=1)
    adventure.set_topics([topic1, topic2])

 
    user = User(username="Пользователь1")

    # Добавление приключения пользователю
    user.add_adventure(adventure)
    user_adventure = user.get_adventure_by_name(adventure.get_name())
    if user_adventure is None:
        print("Приключение не найдено")
    # Тестовые ответы пользователя
    answers = [
        ["Язык программирования", "#"],  
        ["Неправильный ответ", "+"]      
    ]

    # Обработка ответов для каждой темы
    for i, topic in enumerate(user_adventure.get_topics()):
        result = topic.finish_test(answers[i])
        if result:
            print(f"Тема {topic.get_topic_id()} завершена. Рейтинг: {topic.get_rate()}")
        else:
            print(f"Тема {topic.get_topic_id()} уже завершена или не может быть завершена.")

 
    user.finish_adventure("Приключение 1")

 
    print("Рейтинг пользователя:", user.get_rating())
    print("Завершенные приключения:", len(user.completed_adventures))
    
 
    assert len(user.completed_adventures) == 1, "Пользователь должен иметь одно завершенное приключение."
    assert user.get_rating() >= 0, "Рейтинг пользователя должен быть неотрицательным."

 
    assert topic1.get_rate() >= 0, "Рейтинг темы 1 должен быть неотрицательным."
    assert topic2.get_rate() >= 0, "Рейтинг темы 2 должен быть неотрицательным."
    
    print("Все тесты пройдены успешно!")

 
test_adventure_system()
