import random
from .constants import RESOURCES

class GameService:
    def __init__(self, repo):
        self.repo = repo

    async def gather(self, gid, uid, cooldown):
        wait = await self.repo.cooldown(gid,uid,"gather",cooldown)
        if wait:
            return {"wait":wait}
        resource = random.choices(RESOURCES,weights=(35,30,15,20),k=1)[0]
        amount = random.randint(3,7)
        await self.repo.add_resource(gid,uid,resource,amount)
        await self.repo.award_xp(gid,uid,12)
        if resource in ("wood","stone"):
            await self.repo.quest_progress(gid,resource,amount)
        return {"resource":resource,"amount":amount}

    async def explore(self, gid, uid, cooldown):
        wait = await self.repo.cooldown(gid,uid,"explore",cooldown)
        if wait:
            return {"wait":wait}
        finds = [
            ("wood",4,20,"You discovered a quiet woodland trail."),
            ("stone",4,22,"You found an ancient quarry beside a river."),
            ("crystal",2,35,"A crystal formation shimmered beneath the hills."),
            ("food",5,18,"You found a fertile valley ready for cultivation."),
            (None,0,45,"You mapped an unknown landmark for the civilization."),
        ]
        resource, amount, xp, story = random.choice(finds)
        if resource:
            await self.repo.add_resource(gid,uid,resource,amount)
        await self.repo.award_xp(gid,uid,xp)
        await self.repo.add_world_xp(gid,8)
        await self.repo.quest_progress(gid,"explore",1)
        return {"resource":resource,"amount":amount,"xp":xp,"story":story}
