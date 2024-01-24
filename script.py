from random import randint


class Dot:  # Класс Точка на доске
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):  # не понял зачем он нужен
        return f'({self.x!r}, {self.y!r})'


class BoardException(Exception):  # Класс Исключения
    pass


class BoardOutExeption(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за игровое поле!"


class BoardUserExeption(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"


class BoardWrongShipExeption(BoardException):
    pass


class Ship:  # Класс корабля
    def __init__(self, bow, l, o):
        self.bow = bow  # объект класса точка (x y), начальная у корабля (верхний левый угол)
        self.l = l  # длина корабля
        self.o = o  # рандомно между 0 и 1 расположение по горизонтали или вертикали корабля
        self.lives = l  # жизни корабля

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x  # Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))    board.add_ship(ship)    for d in ship.dots:
            cur_y = self.bow.y
            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:  # Класс игровой доски
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [["O"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def add_ship(self, ship):  # board.add_ship(ship)    ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
        for d in ship.dots:  # итерация по списку из объектов точек для каждого объекта класса корабль
            if self.out(d) or d in self.busy:
                raise BoardWrongShipExeption()  # поднимая ошибку код данного метода прерывается
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not self.out(cur) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):  # принимает объект класса точка и проверят ее на возможность вхождения в игровое поле
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutExeption()
        if d in self.busy:
            raise BoardUserExeption()
        self.busy.append(d)
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Game:  # Класс игрового процесса
    def __init__(self, size=6):
        self.size = size  # размер доски, по умолчанию
        pl = self.random_board()  # доска человека
        co = self.random_board()  # доска компьютера
        co.hid = True  # прячет доску компьютера
        self.ai = AI(co, pl)  # компьютер (computer, player)
        self.us = User(pl, co)  # игрок (игрок, компьютер)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)  # создание пустой игрой доски объекта класса
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipExeption:
                    pass
        board.begin()
        return board

    @staticmethod
    def greet():
        print("--------------------")
        print("  Приветствуем вас  ")
        print("       в игре       ")
        print("    морской  бой    ")
        print("--------------------")
        print(" формат ввода:  x y ")
        print("  х - номер строки  ")
        print("  y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            print(num, 'num')
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break
            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        Game.greet()
        self.loop()


class Player:

    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):  # не реализованная ошибка (не используется в процессе игры)
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print("Введите две координаты!")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


g = Game()
g.start()
