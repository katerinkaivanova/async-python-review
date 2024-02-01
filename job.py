import json
import logging
import shutil
import ssl
from pathlib import Path
from urllib.request import urlopen


logger = logging.getLogger()


# review: дублирует декоратор в scheduler.py, не используется в модуле
def coroutine(f):
    def wrap(*args, **kwargs):
        gen = f(*args, **kwargs)
        gen.send(None)
        return gen
    return wrap


# review: таски лучше перенести в отдельный модуль, например, tasks.py
# чтобы в текущем модуле осталась только логика Job
def get_and_write_data(condition, url):
    # review: для работы с сетью очень сильно рекомендую использовать requests
    # https://stackoverflow.com/questions/2018026/what-are-the-differences-between-the-urllib-urllib2-urllib3-and-requests-modul
    context = ssl._create_unverified_context()
    # review: название директорий и файлов передаём в таску параметром
    # мы же хотим переиспользовать таски :)
    file = 'punchline.txt'
    with condition:
        with urlopen(url, context=context) as req:
            resp = req.read().decode('utf-8')
            resp = json.loads(resp)
        if req.status != 200:  # review: заменить на константу
            # review: полезно использовать кастомизированные ошибки
            # можно добавить их в отдельный модуль exceptions.py и использовать:
            # msg = f'Error during execute request. {resp.status}: {resp.reason}'
            # raise CustomException(msg)
            # https://www.pythontutorial.net/python-oop/python-custom-exception/
            raise Exception(
                f'Error during execute request. {resp.status}: {resp.reason}',
            )
        data = resp
        if isinstance(data, dict):
            path = Path(file)
            # review: настраиваем logger и пишем в logger.info()
            setup = data['setup']
            punchline = data['punchline']
            print(
                f'Setup: {setup} \n'
                f'Punchline: {punchline}',
            )
            with open(path, mode='a') as config:
                config.write(str(data))
        else:
            # review: добавить настройки логгера, чтобы ошибки фиксировались в едином стиле / формате
            logger.error(type(data))
            logger.error(ValueError)
            # review: аналогично предложению выше, необходимо кастомизировать ошибки
            # и где-то их отлавливать :)
            raise ValueError

# review: задачи переделываем в симпатичные корутины, нам же нужна практика :)
# ниже, как пример:
# def delete_file(name: str) -> Generator[str, None, None]:
#     if os.path.exists(name):
#         os.remove(name)
#         yield f'file {name} is delete'
#     else:
#         yield f'file {name} not exists'


# review: переделываем в корутину и переносим в отдельный модуль
def copy_file(condition, x=None):
    # review: название директорий и файлов передаём в таску параметром
    file = 'punchline.txt'
    to_path = './jokes/'
    with condition:
        condition.wait(timeout=1)
        try:
            shutil.copy(file, to_path)
        except FileNotFoundError as ex:
            logger.error('Файл не найден %s', ex)


# review: переделываем в корутину и переносим в отдельный модуль
def delete_file(condition, x=None):
    # review: название директорий и файлов передаём в таску параметром
    file = 'punchline.txt'
    obj = Path(file)
    with condition:
        condition.wait(timeout=1)
        try:
            obj.unlink()  # reviw: используем os.remove()
            logger.info('Удалил файл')
        except FileNotFoundError as ex:
            logger.error(ex)


class Job:
    # review: скорее всего нам понадобится идентифицировать задачи, чтобы зафиксировать результат их работы
    # для начала можем воспользоваться int, затем разогнаться до UUID https://docs.python.org/3/library/uuid.html
    # задаем задаче необходимые параметры по времени работы, количеству попыток, зависимостям и т. д.
    # id: int
    # func: Callable
    # start_at: datetime | None = None
    # max_working_time: int = -1
    # tries: int = 0
    # dependencies: list[int] = field(default_factory=list)
    # status: Enum = field(init=False)
    def __init__(
            self,
            func=None,
            name=None,
            args=None,
    ):
        self.args = args
        self.name = name
        self.func = func

    # def __post_init__(self):
    #     self.coroutine = self.func()
    #     self.status = Status.none

    # review: переделаем работы Планировщика через корутины
    # метод run будет возвращать результат завершения задачи True/False
    # https://lerner.co.il/2020/05/08/making-sense-of-generators-coroutines-and-yield-from-in-python/
    # https://superfastpython.com/python-coroutine/
    # def run(self) -> bool:
    #     try:
    #         выполнить весь код корутины до оператора yield
    #         result = next(self.coroutine)
    #         logger.info(f'job id:{self.id}, get result: {result}')
    #     except StopIteration:
    #         ...
    #         добавить логику при завершения работы генератора
    #
    #     except Exception as err:
    #         ...
    #         не забывать про возможные ошибки при выполнении задач
    #
    #     в случае успеха:
    #     return True

    def run(self, *args):
        tar = self.func(*args)
        logger.info('тип объекта в Job.run %s', type(tar))
        logger.debug('запуск объекта %s', tar)
        return tar

    # review: добавить методы
    # def restart(self):
    #    pass

    # def stop(self):
    #    pass

    # ...
    # etc
