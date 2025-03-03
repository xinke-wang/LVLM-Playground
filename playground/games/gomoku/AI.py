class AI:

    def __init__(self, chessboard):
        self.chessboard = chessboard
        self.size = len(chessboard)
        self.count = 0

    def ai(self, color, deep, pre_evaluate):
        if deep >= 2:
            temp = self.evaluateBoard(2, self.chessboard) - self.evaluateBoard(
                1, self.chessboard)
            return temp
        if color == 2:
            values = -100000000
        else:
            values = 100000000
        for i in range(15):
            for j in range(15):
                if self.chessboard[i][j][2] == 0:
                    if self.judge_empty(i, j):
                        continue
                    self.chessboard[i][j][2] = color
                    evaluate = self.ai(3 - color, deep + 1, values)
                    if color == 2:
                        if evaluate > pre_evaluate:
                            self.chessboard[i][j][2] = 0
                            self.count += 1
                            return 100000000
                    else:
                        if evaluate < pre_evaluate:
                            self.chessboard[i][j][2] = 0
                            self.count += 1
                            return -100000000
                    if color == 2:
                        if evaluate >= values:
                            values = evaluate
                    else:
                        if evaluate <= values:
                            values = evaluate
                    self.chessboard[i][j][2] = 0
        return values

    def judge_empty(self, m, n):
        directions = [(-1, 0), (1, 0), (-1, 1), (1, -1), (0, 1), (0, -1),
                      (1, 1), (-1, -1)]
        j = 0
        count = 1
        while j < len(directions):
            a = 0
            while a <= 1:
                x, y = m, n
                a += 1
                for i in range(2):
                    if x + directions[j][0] < 0 or x + directions[j][
                            0] > self.size - 1 or y + directions[j][
                                1] < 0 or y + directions[j][1] > self.size - 1:
                        break
                    x += directions[j][0]
                    y += directions[j][1]
                    if self.chessboard[x][y][2] == 0:
                        count += 1
                    else:
                        break
                j += 1
        if count == 17:
            return 1
        return 0

    def judge(self, m, n):
        directions = [(-1, 0), (1, 0), (-1, 1), (1, -1), (0, 1), (0, -1),
                      (1, 1), (-1, -1)]
        j = 0
        while j < len(directions):
            count = 1
            a = 0
            while a <= 1:
                x, y = m, n
                a += 1
                for i in range(4):
                    if x + directions[j][0] < 0 or x + directions[j][
                            0] > self.size - 1 or y + directions[j][
                                1] < 0 or y + directions[j][1] > self.size - 1:
                        break
                    x += directions[j][0]
                    y += directions[j][1]
                    if self.chessboard[x][y][2] == self.chessboard[m][n][2]:
                        count += 1
                    else:
                        break
                j += 1
            if count >= 5:
                if self.chessboard[m][n][2] == 2:
                    return 1
        return 0

    def evaluateBoard(self, color, chessboard):
        values = 0
        directions = [(-1, 0), (1, 0), (-1, 1), (1, -1), (0, 1), (0, -1),
                      (1, 1), (-1, -1)]
        directions_2 = [(1, 0), (1, -1), (0, 1), (1, 1)]
        for row in range(self.size):
            for col in range(self.size):
                if chessboard[row][col][2] != color:
                    continue
                j = 0
                while j < len(directions):
                    count = 1
                    a = 0
                    record = []
                    while a <= 1:
                        x, y = row, col
                        a += 1
                        for i in range(4):
                            if x + directions[j][0] < 0 or x + directions[j][
                                    0] > self.size - 1 or y + directions[j][
                                        1] < 0 or y + directions[j][
                                            1] > self.size - 1:
                                record.append(3 - color)
                                break
                            x += directions[j][0]
                            y += directions[j][1]
                            if chessboard[x][y][2] == chessboard[row][col][2]:
                                count += 1
                            else:
                                record.append(chessboard[x][y][2])
                                break
                        j += 1
                    if count >= 5:
                        values += 200000
                    elif count == 4:
                        if record[0] == record[1] == 0:
                            values += 70000
                        elif (record[0] == 0 and record[1] == (3 - color)) or (
                                record[0] == (3 - color) and record[1] == 0):
                            values += 1000
                    elif count == 3:
                        if record[0] == record[1] == 0:
                            values += 1000
                        elif (record[0] == 0 and record[1] == (3 - color)) or (
                                record[0] == (3 - color) and record[1] == 0):
                            values += 150
                    elif count == 2:
                        if record[0] == record[1] == 0:
                            values += 1000
                        elif (record[0] == 0 and record[1] == (3 - color)) or (
                                record[0] == (3 - color) and record[1] == 0):
                            values += 150
                    k = 0
                    while k < len(directions_2):
                        x, y = row, col
                        record = []
                        record.append(chessboard[x][y][2])
                        for i in range(4):
                            if i == 1 and len(record) == 2:
                                if record[0] != record[1] and record[
                                        0] and record[1]:
                                    values += 10
                            if x + directions_2[k][0] < 0 or x + directions_2[
                                    k][0] > self.size - 1 or y + directions_2[
                                        k][1] < 0 or y + directions_2[k][
                                            1] > self.size - 1:
                                break
                            x += directions_2[k][0]
                            y += directions_2[k][1]
                            record.append(chessboard[x][y][2])
                        if len(record) == 5:
                            count = record.count(0)
                            if (count == 1 and record[1] == 0
                                    and record.count(color)
                                    == 4) or (count == 1 and record[3] == 0
                                              and record.count(color) == 4):
                                values += 3000
                            if count == 1 and record[2] == 0 and record.count(
                                    color) == 4:
                                values += 2600
                        k += 1
        return values
