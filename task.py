import time
import datetime
import asyncio
import printer
import random
# from super_user import SuperUser


def CurrentTime():
    currenttime = int(time.mktime(datetime.datetime.now().timetuple()))
    return currenttime


class Messenger():
    instance = None
    
    def __new__(cls, users=[], var_super_user=None, loop=None):
        if not cls.instance:
            cls.instance = super(Messenger, cls).__new__(cls)
            cls.instance.queue = asyncio.Queue()
            cls.instance.loop = loop
            cls.instance._observers = users
            cls.instance._var_super_user = var_super_user
            cls.instance.dict_user_status = dict()
            cls.instance.black_list = ['handle_1_room_activity', 'handle_1_room_TV', 'handle_1_activity_raffle', 'handle_1_TV_raffle', 'draw_lottery', 'open_silver_box', 'post_watching_history']
        return cls.instance

    def register(self, ob):
        print('register', ob)
        self._observers.append(ob)

    def remove(self, user_id):
        self.dict_user_status[user_id] = False
        
    def check_status(self, func, user_id):
        if func not in self.black_list:
            return True
        else:
            return self.dict_user_status.get(user_id, True)
            
    def print_blacklist(self):
        print('小黑屋状态:', self.dict_user_status)
        

    async def notify(self, func, value, id=None):
        # print('小黑屋状态:', self.dict_user_status)
        if id is None:
            list_tasks = []
            for i, user in enumerate(self._observers):
                if self.check_status(func, i):
                    task = asyncio.ensure_future(user.update(func, value))
                    list_tasks.append(task)
                if not ((i+1) % 100):
                    await asyncio.wait(list_tasks, return_when=asyncio.ALL_COMPLETED)
                    # await asyncio.sleep(1)
                    list_tasks = []
            if list_tasks:
                await asyncio.wait(list_tasks, return_when=asyncio.ALL_COMPLETED)
        elif id >= 0:
            user = self._observers[id]
            if self.check_status(func, id):
                return await user.update(func, value)
        else:
            user = self._var_super_user
            answer = await user.update(func, value)
            return answer
            
    async def raffle_notify(self, func, value, id=None):
        await asyncio.sleep(0)
        if id is None:
            list_tasks = []
            for i, user in enumerate(self._observers):
                if self.check_status(func, i):
                    task = asyncio.ensure_future(user.update(func, value))
                    list_tasks.append(task)
                if not ((i+1) % 100):
                    await asyncio.wait(list_tasks, return_when=asyncio.ALL_COMPLETED)
                    # await asyncio.sleep(1)
                    list_tasks = []
            if list_tasks:
                await asyncio.wait(list_tasks, return_when=asyncio.ALL_COMPLETED)
        elif id >= 0:
            user = self._observers[id]
            if self.check_status(func, id):
                asyncio.ensure_future(user.update(func, value))
        else:
            user = self._var_super_user
            answer = await user.update(func, value)
            return answer
            
    def set_delay_times(self, time_range):
        return ((i,random.uniform(0, time_range)) for i in range(len(self._observers)))
            

# 被观测的
class RaffleHandler(Messenger):

    async def join_raffle(self):
        while True:
            raffle = await self.queue.get()
            await asyncio.sleep(3)
            list_raffle0 = [self.queue.get_nowait() for i in range(self.queue.qsize())]
            list_raffle0.append(raffle)
            list_raffle = list(set(list_raffle0))
                
            # print('过滤完毕')
            if len(list_raffle) != len(list_raffle0):
                print('过滤机制起作用', list_raffle)
            
            for i, value in enumerate(list_raffle):
                # 总督预处理
                if isinstance(value[0][0], str):
                    value = list(value)
                    value[0] = [await self.notify('find_live_user_roomid', value[0], -1)]
                    list_raffle[i] = value
            tasklist = []
            for i in list_raffle:
                task = asyncio.ensure_future(self.handle_1_roomid_raffle(i))
                tasklist.append(task)
            await asyncio.wait(tasklist, return_when=asyncio.ALL_COMPLETED)
        
    def push2queue(self,  value, func, id=None):
        self.queue.put_nowait((value, func, id))
        return
    
    async def handle_1_roomid_raffle(self, i):
        if i[1] in ['handle_1_room_TV', 'handle_1_room_captain']:
            if (await self.notify('check_if_normal_room', i[0], -1)):
                await self.notify('post_watching_history', i[0])
                await self.notify(i[1], i[0], i[2])
        else:
            print('hhjjkskddrsfvsfdfvdfvvfdvdvdfdfffdfsvh', i)
        
        
class Task(Messenger):
        
    async def init(self):
        self.call_after('sliver2coin', 0)
        self.call_after('doublegain_coin2silver', 0)
        self.call_after('DoSign', 0)
        self.call_after('Daily_bag', 0)
        self.call_after('Daily_Task', 0)
        self.call_after('link_sign', 0)
        # self.call_after('send_gift', 0)
        #self.call_after('auto_send_gift', 0)
        self.call_after('BiliMainTask', 0)
        self.call_after('judge', 0)
        self.call_after('open_silver_box', 0)
        
    async def run(self):
        #await self.init()
        while True:
            i = await self.queue.get()
            print(i, '一级')  
            # await self.notify(*i)
            await self.raffle_notify(*i)
                
    def call_after(self, func, delay, id=None, time_range=None):
        if time_range is None:
            value = (func, (), id)
            self.loop.call_later(delay, self.queue.put_nowait, value)
            print(value)
        else:
            for id, add_time in self.set_delay_times(time_range):
                value = (func, (), id)
                self.loop.call_later(delay + add_time, self.queue.put_nowait, value)
                
        return 
        
    def call_at(self, func, time_expected, tuple_values, id=None, time_range=None):
        current_time = CurrentTime()
        delay = time_expected - current_time
        if time_range is None:
            value = (func, tuple_values, id)
            self.loop.call_later(delay, self.queue.put_nowait, value)
            print(value)
        else:
            print(time_range, 'hhhhhjjjkkkkkkkkk')          
            for id, add_time in self.set_delay_times(time_range):
                value = (func, tuple_values, id)
                print('分布时间', value, id, add_time)
                self.loop.call_later(delay + add_time, self.queue.put_nowait, value)
                
        return
        
    async def heartbeat(self):
        while True:
            printer.info([f'用户普通心跳以及实物抽奖检测开始'], True)
            await self.notify('heartbeat', ())
            # await self.notify('draw_lottery', ())
            for i in range(87, 95):
                answer = await self.notify('handle_1_room_substant', (i,), 0)
                if answer is None:
                    # print('结束')
                    break
            printer.info([f'用户普通心跳以及实物抽奖检测完成'], True)
            await asyncio.sleep(300)



