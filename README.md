# Thread Pool for Python

A thread pool module for simplifying multithreading code in Python.

Uses a priority queue with "runner threads" that wait infinitely for new tasks.


# Usage

```python
from tpool.pool import pool

NUMBER_OF_THREADS = 8


def main():
    # Initialize thread pool with 8 threads.
    thread_pool = pool(number_of_threads=NUMBER_OF_THREADS)

```

For a more extended usage example, please see the demo/main.py
