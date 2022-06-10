from bs4 import BeautifulSoup as BS
from tkinter import *
import requests
import csv

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36', 'accept': '*/*'}
url = 'http://dspk.cs.gkovd.ru/login/index.php'
URL_TEST = 'http://dspk.cs.gkovd.ru/mod/quiz/attempt.php?id='
data ={}
Labels = ["username", "password", "№ Теста:"]
questions = {} # словарь для данных из файла
answers_result = list() # список для найденых ответов

window = Tk()
window.attributes('-toolwindow', True)
window.title("ТЕСТ")

def save_txt():
    data[Labels[0]] = username.get().strip('\n ') # считываем текущий введенный логин
    data[Labels[1]] = password.get().strip('\n ') # считываем текущий введенный пароль
    with open('login_pass.txt', 'w', encoding='utf-8') as file: # сохраняем их в файл
        for key, val in data.items():
            file.write('{} {}\n'.format(key,val)) # из словаря data в формате индекс значение

def read_txt():
    with open('login_pass.txt', encoding='utf-8') as file:
        for line in file:
            key, value = line.split()
            data[key] = value

def read_csv(name_file):
    with open(name_file, encoding='utf8') as csv_file: # открываем файл с помощью менеджера контекста, при таком подходе файл закрывается автоматически
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader: # выполняем для каждой строки
            questions[row.pop(0)] = row

def clicked():
    data[Labels[0]] = username.get().strip('\n ')
    data[Labels[1]] = password.get().strip('\n ')
    user_session = requests.Session() # создаем сессию
    user_session.post(url, data=data, headers=HEADERS) # отправляем логин и пароль на сервер
    response = user_session.get(URL_TEST+userTest.get().strip('\n '), headers=HEADERS) # запрашиваем страницу с тестом для анализа
    parse = BS(response.text, 'lxml') # парсим страницу
    name_user = parse.find('div', class_= 'logininfo').a.text.strip('\n ').split(' ')[0] # находим имя пользователя
    answers_result.append(name_user) # пишем для кого подготовлены ответы
    questions_div = parse.find_all('div', class_='que') # парсим все div-ы с вопросами
    read_csv('dataDSPK.csv') # загружаем из файла имеющиеся ответы в словарь questions
    for question in questions_div: # для каждого вопроса выполняем
        find_que = question.find('div', class_= 'qtext').text.strip('\n ')
        answers = list()
        answers.append('№' + question.find('span', class_='no').text.split(' ')[1] + ': ') # находим номер в тесте задаваемого вопроса, и добавляем в список
        if find_que in questions: # если номер вопроса найден в базе файла,
            td_answers = question.find_all('td', class_='text') # то находим все номера предложенных в тесте ответов на данный вопрос
            test_answers = list() # чистим список
            for label_ans in td_answers: # и собираем номера ответов в список
                try:
                    test_answers.append(re.sub(r'\b\w[.]\s', '', label_ans.find('label').text).strip('\n '))
                except Exception as e:
                    test_answers.append('?')
            for resp in test_answers: # проверяем каждый ответ из теста на правильность
                if resp in questions[find_que]: # если ответ найден в базе он правильный
                    answers.append(test_answers.index(resp) + 1) # то записываем номер (позицию) ответа
        answers_result.append(' '.join(map(str, answers)))
    print(answers_result)
    for txt in answers_result: # отрисовываем ответы на начальном окне
        lbl = Label(window, text=txt)
        lbl.grid(column = 0, row = answers_result.index(txt) + 5, padx = 5, sticky = W)

def clickquit():
    save_txt()
    window.destroy()

read_txt() # считываем логин и пароль из файла
print(data)

for txt in Labels: # отрисовываем нужные надписи на начальном окне
    lbl = Label(window, text=txt)
    lbl.grid(column = 0, row = Labels.index(txt), padx = 5, pady = 5, sticky = E)

# отрисовываем поле ввода логина, с предустановленным значением из файла
username = Entry(window,width=12)
username.insert(0, data['username'])
username.grid(column=1, row=0)

# отрисовываем поле ввода пароля, с предустановленным значением из файла
password = Entry(window,width=12, show = '*')
password.insert(0, data['password'])
password.grid(column=1, row=1)

userTest = Entry(window,width=12)
userTest.grid(column=1, row=2, padx=5)

btnquit = Button(window, text="Выход", command=clickquit)
btnquit.grid(column=0, row=4, sticky=E)

btn = Button(window, text="Пуск!", command=clicked)
btn.grid(column=1, row=4, sticky=E, padx=5)

window.mainloop()
