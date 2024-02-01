# review: отличный прогресс! начало положено, нужно немного потрудиться и всё получится :)
# 1. для начала желательно разобраться с директориями, добавить requirements, scripts, tests, etc.
#    так появится привычка к структурированию проекта и вся логика не будет свалена в кучу
# 2. также нужно настроить ruff, который при каждом запуске будет причесывать код
#    и предупреждать о пропущенных аннотациях типов, ошибках в коде и других проблемах.
#    сохранит кучу времени -> https://github.com/astral-sh/ruff

import logging

# review: база решения должна строиться на использовании корутин, попробуем разобраться
import multiprocessing

# review: в модуле sheduler.py оставим логику самого планировщика
# запуск задач можем вынести отдельно в main.py
from job import Job, copy_file, delete_file, get_and_write_data


logging.basicConfig(level=logging.DEBUG)


def coroutine(f):
    def wrap(*args, **kwargs):
        gen = f(*args, **kwargs)
        gen.send(None)
        return gen
    return wrap


class Scheduler:
    # review: в задании необходимо ограничить число задач, которые одновременно может выполнять планировщик
    # нам понадобится очередь для тех задач, которые выполняются и буфер для задач, которые только
    # ожидают выполнения, так же нам необходимо фиксировать задачи, которые завершились успешно или с ошибкой
    # таким образом:
    # pool_size: int = 10
    # _queue: Queue = Queue(pool_size)
    # _buffer: deque = field(default_factory=deque)
    # _end_jobs: set[int] = field(default_factory=set)
    # _wrong_jobs: set[int] = field(default_factory=set)
    # _worked: bool = False
    def __init__(
            self,
            max_working_time=1,  # review: время работы должно быть аттрибутом Job
            tries=0,  # review: количество попыток должно быть аттрибутом Job
            dependencies=(),  # review: зависимости должны быть аттрибутом Job
            start_at=None,  # review: datetime | None = None
    ):
        super().__init__()  # review: ?
        self.task_list: list[Job] = []  # review: лучше использовать Queue
        self.start_at = start_at
        self.max_working_time = max_working_time
        self.tries = tries
        # review: зависимости должны быть аттрибутом Job
        self.dependencies = dependencies if dependencies is not None else None

    # review: пусть базово планировщик будет проверять зависимости у задачи
    # и добавлять их в очередь для обработки или в буфер для ожидания обработки
    # def schedule(self, job: Job) -> None:
    #     if job.dependencies and not self._check_dependencies(job):
    #         return
    #     if self._queue.qsize() < self.pool_size:
    #         self._queue.put(job)
    #         return
    #     self._buffer.append(job)

    # review: будем извлекать задачи, например, следующим образом:
    # def _get_job(self) -> Job | None:
    #     if self._queue.empty():
    #         logging.debug('Queue is empty')
    #         return None
    #     job = self._queue.get()
    #     if len(self._buffer) > 0 and self._queue.qsize() < self.pool_size - 1:
    #         self._queue.put(self._buffer.popleft())
    #     return job

    # review: добавить проверку зависимостей:
    # def _check_dependencies(self, job) -> bool:
    #   ...

    @coroutine  # review: корутинами д. б. задачи, которые будет запускать планировщик
    def schedule(self):
        processes = []
        while True:
            task_list = (yield)
            print(task_list)
            for task in task_list:
                logging.info(f'Планировщик: запускаю задачу - {task.name}')
                p = multiprocessing.Process(target=task.run, args=(condition, url))
                p.start()
                processes.append(p)
            for process in processes:
                logging.info(process)
                process.join()
                logging.info(f' process {process} stopped!')

    # review: здесь будем вызывать Job.run()
    # и фиксировать выполненный результат в .lock-файлы
    # def _process(self, job) -> None:
    #   ...

    # review: при запуске планировщик будет ожидать новые задачи и выполнять их
    # def run(self):
    #     yield
    #     while self._worked:
    #         job = self._get_job()
    #         if job:
    #             self._process(job)
    #         else:
    #             logging.info('scheduler job empty')
    #             break
    #         yield

    def run(self, jobs: tuple):
        gen = self.schedule()
        gen.send(jobs)

    # review: добавить методы
    # def start(self):
    #    pass

    # def restart(self):
    #    pass

    # def stop(self):
    #    pass

    # def _save(self):
    #   сохраняем результаты работы

    # def _load(self):
    #   загружаем результаты работы при рестарте

    # ...
    # etc.


# review: переносим в main.py
if __name__ == '__main__':
    condition = multiprocessing.Condition()
    url = 'https://official-joke-api.appspot.com/random_joke'
    job1 = Job(
        func=get_and_write_data,
        name='Запрос в сеть',
        args=(condition, url),
    )
    job2 = Job(
        func=copy_file,
        name='Удалить файл',
        args=(condition, ),
    )
    job3 = Job(
        func=delete_file,
        name='Скопировать файл',
        args=(condition,),
    )
    g = Scheduler()
    g.run((job1, job2, job3))
