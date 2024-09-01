import httpx
import os
from uuid import uuid4
import json


class ChatGLM:
    def __init__(self, api_key: str, model: str = "glm-4-flash", storage: str = ""):
        self.model = model
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"})
        self.history = []
        self.storage = storage
        if not self.is_valid_path(storage):
            raise ValueError("storage path is not valid")

    def is_valid_path(self, path_str: str):
        try:
            os.path.exists(path_str)
            return True
        except Exception:
            return False

    def get_creation_time(self, file_path):
        return os.path.getctime(file_path)

    async def send(self, message: dict):
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        async with self.client as client:
            self.history.append(message)
            playload = {"model": self.model, "messages": self.history}
            response = await client.post(url, json=playload)
            if response.status_code == 200:
                result = response.json()
                # print(result)
                content = result["choices"][0]["message"]
                self.history.append({"role": content.get(
                    "role"), "content": content.get("content")})
                return content
            else:
                return response.status_code, response.json()

    async def save(self):
        id = str(uuid4())
        print(os.path.join(self.storage, f"{id}.json"))
        with open(os.path.join(self.storage, f"{id}.json"), "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)
        return id

    async def load(self, id: str):
        with open(os.path.join(self.storage, f"{id}.json"), "r", encoding="utf-8") as f:
            self.history = json.load(f)

    async def sort_files(self, folder_path):
        # 获取文件夹下的所有文件
        files = [os.path.join(folder_path, f) for f in os.listdir(
            folder_path) if f.endswith('.json')]

        # 根据创建时间排序
        files.sort(key=self.get_creation_time, reverse=True)
        return files

    async def get_conversations(self):
        files = await self.sort_files(self.storage)
        conversations = []
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                message_exist = False
                for message in data:
                    if message.get("role") == "user":
                        conversations.append({"title": message.get("content")[
                                             :10], "id": os.path.basename(file_path)[:-5]})
                        message_exist = True
                        break
                if not message_exist:
                    conversations.append(
                        {"title": None, "id": os.path.basename(file_path)[:-5]})
        return conversations

    async def delete_conversation(self, id: str):
        file_path = os.path.join(self.storage, f"{id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False
