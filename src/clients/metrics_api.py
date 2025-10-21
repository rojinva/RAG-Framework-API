import os
import uuid
import aiohttp
import asyncio
from threading import Thread


class MetricsApiClient:

    def __init__(self, feature_name: str, user_email: str):
        self.feature_name = feature_name
        self.user_email = user_email
        self.correlation_id = str(uuid.uuid4())
        self._single_thread_loop = None
        self.queue = asyncio.Queue()
        self.loop = self.get_or_create_event_loop()

    def get_or_create_event_loop(self):
        if not self._single_thread_loop:
            self._single_thread_loop = asyncio.new_event_loop()
            t = Thread(
                target=self.loop_in_thread, args=(self._single_thread_loop,), daemon=True
            )
            t.start()
        return self._single_thread_loop

    @staticmethod
    def handle_exception(loop, context):
        exception = context.get("exception")
        if exception:
            print("Exception details:", exception)

    def loop_in_thread(self, loop):
        asyncio.set_event_loop(loop)
        loop.set_exception_handler(self.handle_exception)
        loop.run_forever()

    @staticmethod
    async def send_async_request(
        url, method="GET", headers=None, json_data=None, data=None
    ):
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=headers, json=json_data, data=data
            ) as response:
                status = response.status
                text = await response.text()
                return status, text

    async def log_trace_messages(self, log_message, log_level):
        try:
            logger_endpoint_url = os.getenv("BASE_LOG_URL") + "logs"
            headers = {"Content-Type": "application/json"}
            payload = {
                "appName": os.getenv("APPNAME"),
                "subAppName": os.getenv("SUBAPPNAME"),
                "appId": os.getenv("APPID"),
                "featureName": self.feature_name,
                "userName": self.user_email,
                "logMessage": log_message,
                "logLevel": log_level,
            }
            await self.send_async_request(
                logger_endpoint_url, method="POST", headers=headers, json_data=payload
            )
        except Exception as e:
            print(f"Failed to log trace message: {e}")

    async def log_exception_messages(self, exception_message):
        try:
            logger_endpoint_url = os.getenv("BASE_LOG_URL") + "exceptions"
            headers = {"Content-Type": "application/json"}
            payload = {
                "appName": os.getenv("APPNAME"),
                "subAppName": os.getenv("SUBAPPNAME"),
                "appId": os.getenv("APPID"),
                "featureName": self.feature_name,
                "userName": self.user_email,
                "exceptionMessage": exception_message,
            }
            await self.send_async_request(
                logger_endpoint_url, method="POST", headers=headers, json_data=payload
            )
        except Exception as e:
            print(f"Failed to log exception message: {e}")

    async def trace_log_worker(self, queue):
        while True:
            _, _, log_message, log_level = await queue.get()
            await self.log_trace_messages(log_message, log_level)
            queue.task_done()

    async def exception_log_worker(self, queue):
        while True:
            _, _, exception_message = await queue.get()
            await self.log_exception_messages(exception_message)
            queue.task_done()

    def start_trace_logging_worker(self, num_workers=1):
        for _ in range(num_workers):
            self.loop.call_soon_threadsafe(
                self.loop.create_task, self.trace_log_worker(self.queue)
            )

    def start_exception_logging_worker(self, num_workers=1):
        for _ in range(num_workers):
            self.loop.call_soon_threadsafe(
                self.loop.create_task, self.exception_log_worker(self.queue)
            )

    def make_async_log_trace_request(self, log_message, log_level):
        self.start_trace_logging_worker()
        self.loop.call_soon_threadsafe(
            self.queue.put_nowait, (self.feature_name, self.user_email, log_message, log_level)
        )

    def make_async_log_exceptions_request(self, exception_message):
        self.start_exception_logging_worker()
        self.loop.call_soon_threadsafe(
            self.queue.put_nowait, (self.feature_name, self.user_email, exception_message)
        )
