from entity.Entity import EntityProcess
from processes.Category import create_fsm_cat, read_fsm_cats, change_fsm_cat, delete_fsm_cat


class CategoryProcess(EntityProcess):

    async def create_process(self, message):
        await create_fsm_cat(message)

    async def read_process(self,message):
        await read_fsm_cats(message)

    async def update_process(self,message):
        await change_fsm_cat(message)

    async def delete_process(self,message):
        await delete_fsm_cat(message)
