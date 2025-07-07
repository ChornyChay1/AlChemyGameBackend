from Logic.question import CloseQuestion
from Logic.topic import CommonTopic,Event
from Logic.adventure import Adventure
 
question1 = CloseQuestion("What is 2 + 2?", "4")
question2 = CloseQuestion("Capital of France?", "Paris")

 
assert question1.get_question() == "What is 2 + 2?", "Ошибка в get_question()"
assert question1.check_answer("4") == 1, "Ошибка: неверная проверка правильного ответа"
assert question2.check_answer("London") == 0, "Ошибка: неверная проверка неправильного ответа"
event  = Event(100,200)

 
topic = CommonTopic(topic_id=1, video_id=None, questions=[question1, question2],event=event)

 
assert topic.get_questions() == ["What is 2 + 2?", "Capital of France?"], "Ошибка в get_questions()"
 
answers = ["4", "Paris"]
assert topic.finish_test(answers) is True, "Ошибка: тест не завершён"
assert topic.get_rate() == 2, "Ошибка в оценке: ожидалась оценка 2"

 
adventure = Adventure("Math and Geography Adventure", image_id=123)
adventure.set_topics([topic])

 
assert len(adventure.get_topics()) == 1, "Ошибка: темы не установлены правильно"

 
found_topic = adventure.get_topic_by_id(1)
assert found_topic is not None, "Ошибка: тема с ID 1 не найдена"
assert found_topic.get_topic_id() == 1, "Ошибка: неверный ID темы"

 
assert adventure.finish() is True, "Ошибка: приключение не завершилось"
assert adventure.get_rate() == 2, "Ошибка в итоговом рейтинге"

 
assert adventure.finish() is False, "Ошибка: приключение должно завершаться только один раз"

print("Все тесты успешно пройдены!")
