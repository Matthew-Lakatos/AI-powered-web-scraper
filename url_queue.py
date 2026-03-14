from collections import deque


class URLQueue:

    def __init__(self):
        self.queue = deque()
        self.seen = set()

    def add(self, url):

        if url not in self.seen:
            self.queue.append(url)
            self.seen.add(url)

    def add_many(self, urls):

        for url in urls:
            self.add(url)

    def get(self):

        if self.queue:
            return self.queue.popleft()

        return None

    def empty(self):

        return len(self.queue) == 0
