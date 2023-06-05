import base64
import json
import time
from consts import WORKER_NODE_SET
from dtos import Task, TaskResult
import hashlib
import threading
import logging
import my_utils
from worker import Worker

class AutoScaler:
    def get_all_worker_nodes(self):
        workers = my_utils.my_redis.smembers(WORKER_NODE_SET)
        logging.info(f"found {len(workers)} workers")
        all_workers_as_objects = []
        return all_workers_as_objects
        
    def check_if_need_to_add_more_worker(self):
        while True:
            time.sleep(30)
            workers = self.get_all_worker_nodes()
            for worker in workers:
                elapsed_time = time.time() - worker.last_work_time
                logging.info(f'elapsed time for worker with ip {worker.ip} is {elapsed_time}')
                if not self.busy and elapsed_time >= 30: # 5 minutes (300 seconds)
                    logging.warning('i have not beed busy a long time i need to scale in')

    
    
    def work(self):
        stored_json = my_utils.my_redis.rpop('new-tasks-list')
        if stored_json is None:
            return
        else: 
            stored_obj = json.loads(stored_json)
            task = Task(stored_obj['id'], stored_obj['buffer'], int(stored_obj['iterations']))
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
            my_utils.my_redis.lpush('result-tasks-list', result_str)
            logging.info(f'set task in redis')  
            self.last_work_time = time.time()
            return result
    
    def do_work(self):
        while True:
            time.sleep(5)
            self.busy = True
            self.work()
            self.busy = False
    

    
if __name__ == "__main__":
    worker = Worker(my_utils.my_ip)
    worker_str = json.dumps(worker.__dict__)
    logging.info(f"worker started\n{worker_str}")
    my_utils.my_redis.sadd(WORKER_NODE_SET, worker_str)
    logging.info(f"put worker on redis set")
    thread1 = threading.Thread(target=worker.do_work)
    thread2 = threading.Thread(target=worker.check_if_idle)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()