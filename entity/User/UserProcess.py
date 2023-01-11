from entity.Entity import EntityProcess
from processes.Users.create_user import create_fsm_user


class UserProcess(EntityProcess):

    async def create_process(self, message):
        await create_fsm_user(message)

    async def read_process(self):
        pass

    async def update_process(self):
        pass

    async def delete_process(self):
        pass
