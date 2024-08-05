# https://github.com/odysseusmax/animated-lamp/blob/master/bot/database/database.py
import motor.motor_asyncio
from sample_info import tempDict
from info import DATABASE_NAME, DATABASE_URI,SECONDDB_URI, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, P_TTI_SHOW_OFF, SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT, AUTO_DELETE, MAX_BTN, AUTO_FFILTER, SHORTLINK_API, SHORTLINK_URL, IS_SHORTLINK, TUTORIAL, IS_TUTORIAL
import datetime
import pytz

class Database:
    
    def __init__(self, database_name):
        #primary db 
        self._client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.users = self.db.uersz
        self.req = self.db.requests
        #secondary db
        self._client2 = motor.motor_asyncio.AsyncIOMotorClient(SECONDDB_URI)
        self.db2 = self._client2[database_name]
        self.col2 = self.db2.users
        self.grp2 = self.db2.groups
        self.users2 = self.db2.uersz
        self.req2 = self.db2.requests       
        """self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.users = self.db.uersz
        self.req = self.db.requests"""
        
    async def find_join_req(self, id):
        req = await self.req.find_one({'id': id})
        if not req:
            req = await self.req2.find_one({'id': id})
        return bool(req)
        
    async def add_join_req(self, id):
        print(f"tempDict: {tempDict['indexDB']}\n\nDATABASE_URI: {DATABASE_URI}")
        if tempDict['indexDB'] == DATABASE_URI:
            await self.req.insert_one({'id': id})
        else:
            await self.req2.insert_one({'id': id})
        
    async def del_join_req(self):
        await self.req.drop()
        await self.req2.drop()

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )


    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        print(f"tempDict: {tempDict['indexDB']}\n\nDATABASE_URI: {DATABASE_URI}")
        if tempDict['indexDB'] == DATABASE_URI:
            await self.col.insert_one(user)
        else:
            await self.col2.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        if not user:
            user = await self.col2.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = ((await self.col.count_documents({}))+(await self.col2.count_documents({})))
        return count
    

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id': int(id)})
        if not user:
            await self.col2.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
        else:
            await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        user = await self.col.find_one({'id': int(user_id)})
        if not user:
            await self.col2.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})
        else:
            await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            user = await self.col2.find_one({'id':int(id)})
            if not user:
                return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        users_list = (await (self.col.find({})).to_list(length=None))+(await (self.col2.find({})).to_list(length=None))
        return users_list        
    

    async def delete_user(self, user_id):
        user = await self.col.find_one({'id': int(user_id)})
        if user:
            await self.col.delete_many({'id': int(user_id)})
        else:
            await self.col2.delete_many({'id': int(user_id)})


    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        users = self.col2.find({'ban_status.is_banned': True})
        chats = self.grp2.find({'chat_status.is_disabled': True})
        b_chats += [chat['id'] async for chat in chats]
        b_users += [user['id'] async for user in users]
        return b_users, b_chats
    


    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        print(f"tempDict: {tempDict['indexDB']}\n\nDATABASE_URI: {DATABASE_URI}")
        if tempDict['indexDB'] == DATABASE_URI:
            await self.grp.insert_one(chat)
        else:
            await self.grp2.insert_one(chat)
    

    async def get_chat(self, id):
        chat = await self.grp.find_one({'id':int(id)})
        if not chat:
            chat = await self.grp2.find_one({'id':int(id)})
        return False if not chat else chat.get('chat_status')
    

    async def re_enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
            )
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        else:
            await self.grp2.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
        else:
            await self.grp2.update_one({'id': int(id)}, {'$set': {'settings': settings}})
        
    
    async def get_settings(self, id):
        default = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'auto_delete': AUTO_DELETE,
            'auto_ffilter': AUTO_FFILTER,
            'max_btn': MAX_BTN,
            'template': IMDB_TEMPLATE,
            'shortlink': SHORTLINK_URL,
            'shortlink_api': SHORTLINK_API,
            'is_shortlink': IS_SHORTLINK,
            'tutorial': TUTORIAL,
            'is_tutorial': IS_TUTORIAL
        }
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', default)
        else:
            chat = await self.grp2.find_one({'id':int(id)})
            if chat:
                return chat.get('settings', default)
        return default
    

    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
            )
        chat = await self.grp.find_one({'id':int(chat)})
        if chat:
            await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
        else:
            await self.grp2.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
    

    async def total_chat_count(self):
        count = (await self.grp.count_documents({}))+(await self.grp2.count_documents({}))
        return count
    

    async def get_all_chats(self):
        return ((await (self.grp.find({})).to_list(length=None))+(await (self.grp2.find({})).to_list(length=None)))


    async def get_db_size(self):
        size = await self.db.command("dbstats")
        size2 = await self.db2.command("dbstats")
        return size['dataSize'] + size2['dataSize']
    
    async def get_user(self, user_id):
        user_data = await self.users.find_one({"id": user_id})
        if not user_data:
            user_data = await self.users2.find_one({"id": user_id})
        return user_data
    
    
    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)
    
    async def update_one(self, filter_query, update_data):
        try:
            result1 = await self.users.update_one(filter_query, update_data)
            result2 = await self.users2.update_one(filter_query, update_data)
            return result1.matched_count == 1 or result2.matched_count == 1
        except Exception as e:
            print(f"Error updating document: {e}")
            return False    

    async def has_premium_access(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            expiry_time = user_data.get("expiry_time")
            if expiry_time is None:
                # User previously used the free trial, but it has ended.
                return False
            elif isinstance(expiry_time, datetime.datetime) and datetime.datetime.now() <= expiry_time:
                return True
            else:
                await self.remove_premium_access(user_id)
        return False


    async def get_expired(self, current_time):
        expired_users = []
        data1 = self.users.find({"expiry_time": {"$lt": current_time}})
        async for user in data1:
            expired_users.append(user)
        data2 = self.users2.find({"expiry_time": {"$lt": current_time}})
        async for user in data2:
            expired_users.append(user)
        return expired_users

    async def remove_premium_access(self, user_id):
        return await self.update_one(
            {"id": user_id}, {"$set": {"expiry_time": None}}
        )
        
    async def check_trial_status(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            return user_data.get("has_free_trial", False)
        return False

    async def give_free_trial(self, user_id):
        seconds = 5 * 60         
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        user_data = {"id": user_id, "expiry_time": expiry_time, "has_free_trial": True}
        await self.update_user(user_data)
        
        
db = Database(DATABASE_NAME)
