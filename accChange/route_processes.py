from entity.Entity import EntityProcess
from .processes import create_fsm_acc_change, exist_fsm_acc_change


class AccChangeProcess(EntityProcess):

    async def create_process(self, message):
        await create_fsm_acc_change(message)

    async def read_process(self, message):
        await exist_fsm_acc_change(message, action = 'read')

    async def update_process(self, message):
        await exist_fsm_acc_change(message, action = 'change')

    async def delete_process(self, message):
        await exist_fsm_acc_change(message, action = 'delete')
