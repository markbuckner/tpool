# Thread pool object to streamline multi-threading your code.
#
# Initializes a 'pool' with the specified number of threads.
# The threads wait indefinitely for new tasks, and get recycled when they finish a task.
#
# Tasks may be given a priority to place them at the front of the pool's queue for execution.

# Imports.
import threading
import time
import queue


# Thread pool class for simplifying setup of multi-threaded code.
class pool:

    def __init__(self, number_of_threads=2, max_tasks=256):
        """
        Creates a thread pool that contains a specified number of threads that wait to execute target functions.
        """
        # Task ID counter.
        self.task_id = 0  # Initialize to zero and increment atomically for each new task.
        self.task_id_lock = threading.Lock()  # Simple lock for atomic increments.

        # Task queue of functions the user wants executed on separate threads.
        self.task_queue = queue.PriorityQueue(maxsize=max_tasks)

        # Dictionary for return values.
        self.return_values = {}

        # Lock for return values.
        # Note: This might not be necessary, but this code will not rely on Python's dict.pop() to be threadsafe.
        self.return_value_lock = threading.Lock()

        # The number of runner threads for the pool to use.
        self.number_of_threads = number_of_threads

        # Flag to stop runner threads from picking up more tasks.
        self.stop_threads = False

        # Initialize thread pool.
        self._start_thread_pool()

    def execute(self, func, *args, priority="normal", **kwargs):
        """
        Executes function in its own thread, using pre-initialized thread from pool.

        :param func: The function to execute.
        :param args: The function arguments.
        :param priority: The priority of the task.
        :param kwargs: The function keyword arguments.
        :return: The function's return value, if any.
        """
        # Can't execute a new task if pool was already stopped.
        if self.stop_threads:
            raise RuntimeError(
                f"Can't execute new task with thread pool when it's stopped! self.stop_threads={self.stop_threads}")

        # Increment the task ID atomically with a basic lock.
        with self.task_id_lock:
            self.task_id += 1

        # Add function to execute to task queue.
        # put() is thread-safe natively.
        self.task_queue.put((self._to_numeric_priority(priority), self.task_id, func, args, kwargs))

        # Initialize return value.
        self.return_values[self.task_id] = "IN_PROGRESS"

        # Returns task ID.
        return self.task_id

    def is_task_in_progress(self, task_id):
        """
        Returns True if the task hasn't returned yet.

        :param task_id: The task ID number.
        :return: True if task ID is in progress.
        """
        return self.return_values[task_id] == "IN_PROGRESS"

    def get_return_value(self, task_id, timeout=86400):
        """
        Gets the return value of a task executed by the thread pool.

        Blocks until return value is available, or times out.

        See is_task_in_progress() for checking task completion without blocking.

        :param task_id: The task ID number.
        :param timeout: Seconds to wait for return value before timing out.
        :return: The return value of the task. Returns "UNFINISHED" if return value check times out.
        """
        # Initialize timer.
        timer = 0.0

        # Wait for task to complete before getting return value.
        while self.is_task_in_progress(task_id):
            time.sleep(0.1)
            timer += 0.1  # Increment timer. Inexact with sleep, but close enough for this timeout purpose.
            if timer > timeout:
                return "UNFINISHED (timed out waiting for return value)"

        # Pop the return value when getting it, so the dictionary doesn't grow infinitely.
        with self.return_value_lock:
            return self.return_values.pop(task_id)

    # Sets a flag to stop all the runner threads in the pool.
    # They will finish all current running tasks, and then not pick up another task when done.
    def stop(self):
        """
        Stops the thread pool.

        The threads will finish their current tasks and then not pick up any new tasks.

        Intended to be used at program close to stop worker threads so the program can exit.
        """
        # Set flag.
        self.stop_threads = True

    def _run(self):
        """
        Internal runner function.
        Picks up tasks from the priority queue and executes them in own thread.
        """
        # Run forever until signaled to stop.
        while not self.stop_threads:

            # Wait for a task from the queue.
            while True:

                try:
                    priority, task_id, function, args, kwargs = self.task_queue.get(timeout=1)

                except queue.Empty:

                    # Stop waiting.
                    if self.stop_threads:
                        return

                    # Keep waiting.
                    else:
                        continue

                # Execute task in the context of this runner thread.
                if args:
                    if kwargs:
                        self.return_values[task_id] = function(*args, **kwargs)
                    else:
                        self.return_values[task_id] = function(*args)
                elif kwargs:
                    self.return_values[task_id] = function(**kwargs)
                else:
                    self.return_values[task_id] = function()

    def _start_thread_pool(self):
        """
        Starts all the runner threads in the pool.

        Called by the thread pool constructor, so the threads start automatically.

        The runner threads wait for new tasks to execute forever until stop() is called on the thread pool.
        """
        # Create and start threads.
        for i in range(0, self.number_of_threads):
            new_thread = threading.Thread(group=None, target=self._run)
            new_thread.start()

    def _to_numeric_priority(self, priority):
        """
        Converts string priority to integer, for priority queue sorting.
        """
        if priority == 'ultra_low':
            return 4
        elif priority == 'low':
            return 3
        elif priority == 'normal':
            return 2
        elif priority == 'high':
            return 1
        elif priority == 'ultra_high':
            return 0
        else:
            raise ValueError('Priority keyword argument must be "ultra_low", "low", "normal", "high", or "ultra_high"')
