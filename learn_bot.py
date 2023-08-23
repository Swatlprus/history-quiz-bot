import re
import os


def read_questions(quiz_folder):
    files = os.listdir(quiz_folder)
    questions = {}
    for file in files:
        filepath = os.path.join(quiz_folder, file)

        with open(filepath, 'r', encoding='KOI8-R') as file_questions:
            texts = file_questions.read().split('\n\n\n')

        for text in texts:
            blocks = text.split('\n\n')
            for block in blocks:
                if 'Вопрос' in block:
                    question = re.sub('Вопрос\D\d*:\n', '', block)
                elif 'Ответ' in block:
                    answer = re.sub('Ответ:\n', '', block)
            questions[question] = answer
    return questions
