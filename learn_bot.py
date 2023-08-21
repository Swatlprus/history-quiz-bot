import re


with open('quiz-questions/1vs1200.txt', 'r', encoding='KOI8-R') as file_questions:
  texts = file_questions.read().split('\n\n\n')


questions = {}
for text in texts:
    if len(text) != 0:
        start_question_index = re.search(r'Вопрос\s\d*:', text).end()
        end_question_index = re.search('Ответ:', text).start()
        start_answer_index = re.search('Ответ:', text).end()
        end_answer_index = re.search('Автор:', text).start()
        question = text[start_question_index:end_question_index]
        answer = text[start_answer_index:end_answer_index]
        questions[question] = answer
