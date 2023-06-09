import base64
import json
import time
from consts import WORKER_NODE_SET
from dtos import Task, TaskResult
import hashlib
import threading
import requests
import logging
import my_utils
import consts

# TODO update "num of worker"

class Worker:
    def __init__(self, last_work_time:float, busy:bool, continue_to_work: bool):
        self.last_work_time = last_work_time
        self.busy = busy
        self.continue_to_work = continue_to_work
        
    def check_if_idle(self):
        while self.continue_to_work:
            time.sleep(60)
            elapsed_time = time.time() - self.last_work_time
            logging.info(f'elapsed time is {elapsed_time}')
            if not self.busy and elapsed_time >= 300: # 5 minutes (300 seconds)
                self.continue_to_work=False
                logging.warning(f'i have not been busy a long time i need remove myself from {WORKER_NODE_SET} set')
                time.sleep(5) # wait some time before termination
                logging.warning('i have not been busy a long time i need to kill myself')
                num_of_worker = my_utils.my_redis.get(consts.NUM_OF_WORKERS)
                logging.info(f'num_of_worker {num_of_worker}')
                if num_of_worker is not None:
                    num_of_worker = int(num_of_worker)
                    logging.info(f'set num_of_worker to be {str(num_of_worker - 1)}')
                    my_utils.my_redis.set(consts.NUM_OF_WORKERS,str(num_of_worker - 1))
                my_utils.kill_myself()

    
    
    def work(self):
        logging.info(f'inside work function')
        stored_json = my_utils.my_redis.rpop(consts.TASK_LIST)
        if stored_json is None:
            return
        else: 
            stored_obj = json.loads(stored_json)
            task = Task(stored_obj['id'], stored_obj['buffer'], int(stored_obj['iterations']), float(stored_obj['timestamp']))
            logging.info(f'from redis recieved new task\n{json.dumps(task.__dict__)}')
            buffer = base64.b64decode(task.buffer.encode('utf-8'))
            output = hashlib.sha512(buffer).digest()
            logging.info(f"first output is {output}")
            for _ in range(task.iterations - 1):
                output = hashlib.sha512(output).digest()
                logging.info(f"now output is {output}")
            str_output = base64.b64encode(output).decode('utf-8')
            logging.info(f'str_output is\n{str_output}')
            result = TaskResult(id=task.id, output=str_output)
            result_str = json.dumps(result.__dict__)
            logging.info(f'result is\n{result_str}')
            my_utils.my_redis.lpush(consts.RESULT_LIST, result_str)
            logging.info(f'set task in redis')  
            self.last_work_time = time.time()
            return result
    
    def do_work(self):
        logging.info(f"inside do_work loop")
        while self.continue_to_work:
            time.sleep(5)
            self.busy = True
            self.work()
            self.busy = False
    

    
if __name__ == "__main__":
    worker = Worker(time.time(), False, True)
    worker_str = json.dumps(worker.__dict__)
    logging.info(f"worker started\n{worker_str}")
    thread1 = threading.Thread(target=worker.do_work)
    thread2 = threading.Thread(target=worker.check_if_idle)
    thread1.start()
    thread2.start()