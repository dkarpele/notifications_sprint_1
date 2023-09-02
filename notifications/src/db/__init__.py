from abc import ABC, abstractmethod


class AbstractStorage(ABC):
    """
    Абстрактный класс для работы с хранилищем данных.
    Описывает какие методы должны быть у подобных классов.
    """

    @abstractmethod
    async def close(self):
        """
        Абстрактный асинхронный метод для закрытия соединения
        """
        ...


class AbstractQueueInternal(ABC):
    """
    Абстрактный класс для работы с очередями AQMP.
    Описывает какие методы должны быть у подобных классов.
    """
    @abstractmethod
    async def connect(self, url: str,
                      topic_name: str,
                      queue_name: str):
        pass

    @abstractmethod
    async def produce(self,
                      routing_key: str,
                      data: dict,
                      correlation_id):
        pass

    @abstractmethod
    async def consume(self, routing_key: str):
        pass
