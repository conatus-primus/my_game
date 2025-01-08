# логирование действий оператора и событий программы
# один файл на одну сессию
import datetime


class logger:
    def __init__(self):
        # открываем файл лога
        pass

    def write(self, msg):
        print(msg)
        # TODO переделать путь к файлу лога
        with open('c:/000/log.txt', 'at') as wf:
            current_datetime = datetime.datetime.now()
            # TODO форматированный вывод времени
            wf.write(f'{current_datetime.hour}:{current_datetime.minute} {current_datetime.date()} {msg}\n')
