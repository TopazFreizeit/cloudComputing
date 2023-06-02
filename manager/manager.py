class TaskManager:
    def __init__(self):
        self.tasks : list[tuple[str,bytes,int]] = []
        self.workers : dict[str, bool] = {}
        self.task_results = []

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task):
        self.tasks.remove(task)

    def get_tasks(self):
        return self.tasks

    def add_worker(self, worker, state):
        self.workers[worker] = state

    def remove_worker(self, worker):
        del self.workers[worker]

    def get_workers(self):
        return self.workers

    def update_worker_state(self, worker, state):
        self.workers[worker] = state

    def add_task_result(self, result):
        self.task_results.append(result)

    def get_task_results(self):
        return self.task_results
    
    def find_worker_node(self):
        self.task_results