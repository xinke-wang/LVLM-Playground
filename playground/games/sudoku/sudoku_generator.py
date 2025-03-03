from random import randint, shuffle


def checkGrid(grid):
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                return False
    return True


def fillGrid(grid):
    numberList = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    for i in range(81):
        row = i // 9
        col = i % 9
        if grid[row][col] == 0:
            shuffle(numberList)

            for value in numberList:
                if not (value in grid[row]):
                    if value not in [grid[r][col] for r in range(9)]:
                        square = [
                            grid[r][c]
                            for r in range(row // 3 * 3, row // 3 * 3 + 3)
                            for c in range(col // 3 * 3, col // 3 * 3 + 3)
                        ]
                        if value not in square:
                            grid[row][col] = value
                            if checkGrid(grid):
                                return True
                            elif fillGrid(grid):
                                return True
            break
    grid[row][col] = 0
    return False


def solveGrid(grid, counter):
    for i in range(81):
        row = i // 9
        col = i % 9
        if grid[row][col] == 0:
            for value in range(1, 10):
                if not (value in grid[row]):
                    if value not in [grid[r][col] for r in range(9)]:
                        square = [
                            grid[r][c]
                            for r in range(row // 3 * 3, row // 3 * 3 + 3)
                            for c in range(col // 3 * 3, col // 3 * 3 + 3)
                        ]
                        if value not in square:
                            grid[row][col] = value
                            if checkGrid(grid):
                                counter[0] += 1
                                break
                            elif solveGrid(grid, counter):
                                return True
            break
    grid[row][col] = 0
    return False


def generate_puzzle(grid, attempts):
    counter = [0]

    while attempts > 0:
        row, col = randint(0, 8), randint(0, 8)
        while grid[row][col] == 0:
            row, col = randint(0, 8), randint(0, 8)

        backup = grid[row][col]
        grid[row][col] = 0

        copyGrid = [[grid[r][c] for c in range(9)] for r in range(9)]
        counter[0] = 0

        solveGrid(copyGrid, counter)

        if counter[0] != 1:
            grid[row][col] = backup
            attempts -= 1

    return grid
