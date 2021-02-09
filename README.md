# Thread Pool for Python

A thread pool module for simplifying multithreading code in Python.

Uses a priority queue with "runner threads" that wait infinitely for new tasks.


# Usage

```python
from tpool.pool import pool

NUMBER_OF_THREADS = 8

def hello_threading(x, y, foo='bar'):
    return x, y, foo

def main():
    
    # Initialize thread pool with 8 threads.
    thread_pool = pool(number_of_threads=NUMBER_OF_THREADS)
    
    # Execute a function on a separate thread. Save the task id to get the return value later.
    task_id = thread_pool.execute(hello_threading, 1, 2, foo='baz')
    
    # Get the function's return value.
    return_value = thread_pool.get_return_value(task_id)
    
    print(return_value)
    # (1, 2, baz)

```

For a more extended example, please see the demo/main.py
