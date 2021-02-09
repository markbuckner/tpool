# Thread Pool for Python

A thread pool module for simplifying multithreading code in Python.

Uses a priority queue and with "runner threads" that wait infinitely for new tasks.


# Usage

```python
from tpool.pool import pool
import time  # for sleep

NUMBER_OF_THREADS = 8


def main():
    # Initialize thread pool.
    thread_pool = pool(number_of_threads=NUMBER_OF_THREADS)

    # Demonstrate launching functions without blocking.
    for i in range(0,
                   NUMBER_OF_THREADS + 4):  # 4 more than thread count; this demonstrates recycling threads to do work.
        task_id = thread_pool.execute(do_work, priority='ultra_low')

    # Demonstrate a function with args.
    for i in range(0, 10):
        task_id = thread_pool.execute(function_with_args, 2, 3, priority="low")

    # Demonstrate a function with keyword args.
    for i in range(0, 10):
        task_id = thread_pool.execute(function_with_kwargs, dog="Spot", priority="high")

    # Demonstrate a function with both keyword args and positional args
    for i in range(0, 10):
        task_id = thread_pool.execute(function_with_args_and_kwargs, 1, 2, a='a', c='CCCCCC',
                                      priority="ultra_high")

    # Note that the above tasks go in order from lowest priority to highest.
    # The thread pool will execute the higher priority tasks first, despite being added
    # to the queue later than the lower priority tasks. This is because the underlying
    # queue is a Priority Queue. Higher priority tasks get moved to the front automatically.

    # Demonstrate a function that takes too long for you and times out.
    task_id = thread_pool.execute(function_that_takes_too_long)
    print(
        f'Timeout function return value: {thread_pool.get_return_value(task_id, timeout=1)}')  # Only give the function 1 sec.

    print('The pool will now stop, so the program may exit.')
    thread_pool.stop()
    # If you don't stop the thread pool, the runner threads will prevent your program from exiting.
    # This is because they wait indefinitely for new tasks until signaled to stop.

# Helper function definitions.
def do_work():
    print('A thread is doing work.')
    time.sleep(3)
    bignumber = 2 ** (2 ** 12)
    return bignumber


def function_with_args(x, y):
    print(f'Adding {x} and {y}')
    print(x + y)
    return x + y


def function_with_kwargs(dog='Rover'):
    print(f'Converting {dog} to all-caps.')
    dog = dog.upper()
    print(dog)
    return dog


def function_with_args_and_kwargs(x, y, a='a', b='b', c='c'):
    print(f'Some args and kwargs:{x}, {y}, {a}, {b}, {c}')
    return x + 100, y + 100, a.upper(), b.upper(), c.lower()


def function_that_takes_too_long():
    time.sleep(5)
    return 'Interesting return value, but never seen because takes too long and times out.'


if __name__ == '__main__':
    main()

```
