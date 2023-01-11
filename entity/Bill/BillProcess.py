from entity.Entity import EntityProcess
from processes.Bill import create_fsm_bill, read_fsm_bill, change_fsm_bill, delete_fsm_bill


class BillProcess(EntityProcess):

    async def create_process(self, message):
        await create_fsm_bill(message)

    async def read_process(self, message):
        await read_fsm_bill(message)

    async def update_process(self, message):
        await change_fsm_bill(message)

    async def delete_process(self, message):
        await delete_fsm_bill(message)
