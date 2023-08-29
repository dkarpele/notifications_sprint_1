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
