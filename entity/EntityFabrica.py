from bill.router_processes import BillProcess
from accChange.route_processes import AccChangeProcess
from category.router_processes import CategoryProcess
from entity.Entity import EntityProcess


class EntityFabrica():

    object: EntityProcess

    @classmethod
    async def create_object(cls, entity) -> EntityProcess:
        """Создание объекта сущности"""

        if entity == 'Счета':
            cls.object = BillProcess()
        elif entity == 'Изменения в балансе':
            cls.object = AccChangeProcess()
        elif entity == 'Категории':
            cls.object = CategoryProcess()

    @classmethod
    async def execute_process(cls, message):
        """Вызов метода сущности"""

        if message.text in 'Создать':
            await cls.object.create_process(message)
        elif message.text in 'Посмотреть':
            await cls.object.read_process(message)
        elif message.text in 'Изменить':
            await cls.object.update_process(message)
        elif message.text in 'Удалить':
            await cls.object.delete_process(message)
