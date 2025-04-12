"""
Створити класс що буде мати базові властивості типу dict.

Наявність у класса варіації хеш-таблиці
Додавання нової пари ключ:значення
Вставка нової пари в правльне місце хеш-таблиці через обчислення індексу
Отримання значення за ключем
Маштабування хеш-таблиці при заповенні на обраний вами відсоток шляхом перехешування (міграціі)
"""

class MyHashTable:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.size = 0
        self.data = [None] * self.capacity

    def _hash(self, key):
        return hash(key) % self.capacity

    def put(self, key, value):
        """Додавання або оновлення пари ключ-значення."""
        if self.size / self.capacity >= 0.9:
            self._resize()

        index = self._hash(key)

        while self.data[index] is not None:
            k, v = self.data[index]
            if k == key:
                self.data[index] = (key, value)
                return
            index = (index + 1) % self.capacity

        self.data[index] = (key, value)
        self.size += 1

    def get(self, key):
        """Отримання значення за ключем."""
        index = self._hash(key)

        while self.data[index] is not None:
            k, v = self.data[index]
            if k == key:
                return v
            index = (index + 1) % self.capacity

        raise KeyError(f"Ключ '{key}' не знайдено.")

    def _resize(self):
        """Масштабування таблиці при переповненні."""
        old_data = self.data
        self.capacity *= 2
        self.data = [None] * self.capacity
        self.size = 0

        for item in old_data:
            if item is not None:
                self.put(*item)

    def __str__(self):
        return str([item for item in self.data if item is not None])

ht = MyHashTable()

ht.put("apple", 10)
ht.put("banana", 20)
ht.put("orange", 30)

print(ht.get("banana"))
print(ht)                # [('apple', 10), ('banana', 20), ('orange', 30)]

ht.put("banana", 99)
print(ht.get("banana"))

for i in range(100):
    ht.put(f"key{i}", i)

print(f"Поточний розмір: {ht.capacity}")

