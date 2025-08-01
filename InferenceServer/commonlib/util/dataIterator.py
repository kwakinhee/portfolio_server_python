class DataIterator:

    def __init__(self, data, n:int):
        self.i = -1
        self.n = n
        self.data = data

    def __iter__(self):
        return self
    
    def __next__(self):
        self.i += 1
        if self.i == self.n: self.i = 0

        return self.data[self.i]

