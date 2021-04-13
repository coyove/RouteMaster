class MapData:
    data1 = [] # Q1, include +x, include +y
    data2 = [] # Q2, exclude +y, include -x
    data3 = [] # Q3, exclude -x, include -y
    data4 = [] # Q4, exclude -y, exclude -x
    
    def _which(self, x: int, y: int):
        data = None
        if x >= 0 and y >= 0:
            data = self.data1
        elif x < 0 and y >= 0:
            x = -x
            data = self.data2
        elif x > 0 and y < 0:
            y = -y
            data = self.data4
        else:
            x, y = -x, -y
            data = self.data3
        return data, x, y

    def put(self, x: int, y: int, d):
        data, x, y = self._which(x, y)
        while len(data) <= y:
            data.append([])
        while len(data[y]) <= x:
            data[y].append(None)
        data[y][x] = d

    def get(self, x: int, y: int):
        data, x, y = self._which(x, y)
        if len(data) <= y:
            return None
        if len(data[y]) <= x:
            return None
        return data[y][x]
