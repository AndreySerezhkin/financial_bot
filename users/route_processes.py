from entity.Entity import EntityProcess
import users.processes as user


class UserProcess(EntityProcess):

    async def create_process(self, message):
        await user.create_fsm_user(message)

    async def read_process(self):
        pass

    async def update_process(self):
        pass

    async def delete_process(self):
        pass
