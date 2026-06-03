class Node:
    def __init__(self, value):
        self.value = value
        self.prev  = None
        self.next  = None


class DequeDS:
    def __init__(self):
        self.head  = None
        self.tail  = None
        self._size = 0
        self.mode  = "deque"

    def add_front(self, value):
        n = Node(value)
        if self.is_empty():
            self.head = self.tail = n
        else:
            n.next         = self.head
            self.head.prev = n
            self.head      = n
        self._size += 1

    def add_rear(self, value):
        n = Node(value)
        if self.is_empty():
            self.head = self.tail = n
        else:
            n.prev         = self.tail
            self.tail.next = n
            self.tail      = n
        self._size += 1

    def remove_front(self):
        if self.is_empty(): return None
        v = self.head.value
        if self._size == 1:
            self.head = self.tail = None
        else:
            self.head      = self.head.next
            self.head.prev = None
        self._size -= 1
        return v

    def remove_rear(self):
        if self.is_empty(): return None
        v = self.tail.value
        if self._size == 1:
            self.head = self.tail = None
        else:
            self.tail      = self.tail.prev
            self.tail.next = None
        self._size -= 1
        return v

    def peek_front(self): return self.head.value if not self.is_empty() else None
    def peek_rear(self):  return self.tail.value if not self.is_empty() else None
    def is_empty(self):   return self._size == 0
    def size(self):       return self._size
    def get_mode(self):   return self.mode

    def clear(self):
        self.head = self.tail = None
        self._size = 0

    def to_list(self):
        result, cur = [], self.head
        while cur:
            result.append(cur.value)
            cur = cur.next
        return result

    def set_mode(self, mode):
        if mode not in ("deque", "stack", "queue"):
            raise ValueError(f"Invalid mode: {mode}")
        self.mode = mode

    def __repr__(self):
        return f"DequeDS(mode={self.mode}, size={self._size}, items={self.to_list()})"