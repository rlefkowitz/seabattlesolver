class SeaBattle():

    def __init__(self, size):
        self.size = size
        self.ships = {}
        if size == 10:
            self.shipsizes = [4, 3, 2, 1]
            self.ships = {4: 1, 3: 2, 2: 3, 1: 4}
            self.shipsfound = {4: 0, 3: 0, 2: 0, 1: 0}
        if size == 8:
            self.shipsizes = [4, 3, 2]
            self.ships = {4: 1, 3: 3, 2: 3}
            self.shipsfound = {4: 0, 3: 0, 2: 0}
        self.board = ASBB(size)

    def hit(self, r, c):
        self.board.hit(r, c)

    def miss(self, r, c):
        self.board.miss(r, c)

    def sank(self, s, r, c, h):
        self.board.sank(s, r, c, h)
        self.shipsfound[s] += 1

    def pickspot(self):
        rem = {s: self.ships[s] - self.shipsfound[s] for s in self.shipsizes}
        probs = self.board.probs(self.shipsizes, rem)
        print("\n".join(str(r) for r in probs))
        maxp, loc = 0, (-1, -1)
        for r in range(self.size):
            for c in range(self.size):
                if probs[r][c] > maxp:
                    maxp = probs[r][c]
                    loc = (r, c)
        return loc

    def __str__(self):
        return "\n".join("".join(map(str, r)) for r in self.board.t)

    def command(self, s):
        spl = s.split(" ")
        if spl[0] == "p":
            print(tuple(x + 1 for x in self.pickspot()))
        if spl[0] == "h":
            self.hit(int(spl[1]) - 1, int(spl[2]) - 1)
        if spl[0] == "m":
            self.miss(int(spl[1]) - 1, int(spl[2]) - 1)
        if spl[0] == "s":
            self.sank(int(spl[1]), int(spl[2]) - 1,
                      int(spl[3]) - 1, int(spl[4] == "h"))


class ASBB():

    def __init__(self, s):
        self.s = s
        self.t = [[ASBS() for c in range(s)] for r in range(s)]

    def probs(self, shipsizes, ships):
        psv = PSBB(self.s)
        psv.t = [[not self.valid(r, c) for c in range(self.s)]
                 for r in range(self.s)]
        res = [[0 for c in range(self.s)] for r in range(self.s)]
        for r in range(self.s):
            for c in range(self.s):
                if not self.valid(r, c):
                    res[r][c] = -1
                    continue
                for size in shipsizes:
                    if ships[size]:
                        for o in (0, 1):
                            # print("Trying to place a %d-ship at (%d, %d) %s" % (size, r, c, "horizontally" if o else "vertically"))
                            if psv.shipfits(size, r, c, o):
                                tmp = psv.copy()
                                tmp.placeship(size, r, c, o)
                                tmpships = ships.copy()
                                tmpships[size] -= 1
                                if tmp.placeships(shipsizes, tmpships):
                                    if o:
                                        hitmult = 100 * sum(
                                            self.t[r][c + i].hit for i in range(size))
                                        for i in range(size):
                                            res[r][c + i] += (1 + hitmult) * \
                                                ships[size]
                                    else:
                                        hitmult = 100 * sum(
                                            self.t[r + i][c].hit for i in range(size))
                                        for i in range(size):
                                            res[r + i][c] += (1 + hitmult) * \
                                                ships[size]
                if self.t[r][c].hit:
                    res[r][c] = -1
        # tmp = [[x for x in r] for r in res]

        # def gettmp(r, c):
        #     if self.offboard(r, c):
        #         return -1
        #     return tmp[r][c]

        # for r in range(self.s):
        #     for c in range(self.s):
        #         res[r][c] -= max(gettmp(r - 1, c - 1), gettmp(r - 1, c + 1),
        #                          gettmp(r + 1, c - 1), gettmp(r + 1, c + 1)) / 10
        return res

    def hit(self, r, c):
        if not self.offboard(r, c):
            self.t[r][c].hit = 1
            self.miss(r - 1, c - 1)
            self.miss(r - 1, c + 1)
            self.miss(r + 1, c - 1)
            self.miss(r + 1, c + 1)

    def miss(self, r, c):
        if not self.offboard(r, c):
            self.t[r][c].miss = 1

    def sank(self, s, r, c, h):
        if h:
            self.miss(r, c - 1)
            self.miss(r, c + s)
            for i in range(s):
                self.hit(r, c + i)
                self.miss(r - 1, c + i)
                self.miss(r + 1, c + i)
                self.t[r][c + i].sunk = 1
        else:
            self.miss(r - 1, c)
            self.miss(r + s, c)
            for i in range(s):
                self.hit(r + i, c)
                self.miss(r + i, c - 1)
                self.miss(r + i, c + 1)
                self.t[r + i][c].sunk = 1

    def valid(self, r, c):
        return not (self.t[r][c].sunk or self.t[r][c].miss)

    def offboard(self, r, c):
        return (r < 0 or c < 0 or r >= self.s or c >= self.s)


class ASBS():

    def __init__(self):
        self.sunk = 0
        self.miss = 0
        self.hit = 0

    def __str__(self):
        if self.sunk:
            return "X"
        if self.miss:
            return "-"
        if self.hit:
            return "!"
        return "^"


class PSBB():

    def __init__(self, s):
        self.s = s
        self.t = [[0 for c in range(s)] for r in range(s)]

    def copy(self):
        res = PSBB(self.s)
        res.t = [[x for x in r] for r in self.t]
        return res

    def placeship(self, s, r, c, h):
        if h:
            for i in range(s + 2):
                for j in range(3):
                    self.occ(r + j - 1, c + i - 1)
        else:
            for i in range(s + 2):
                for j in range(3):
                    self.occ(r + i - 1, c + j - 1)

    def shipfits(self, s, r, c, h):
        if h:
            if c + s > self.s:
                return False
            return not any(self.t[r][c + i] for i in range(s))
        if r + s > self.s:
            return False
        return not any(self.t[r + i][c] for i in range(s))

    def placeships(self, shipsizes, ships):
        done = True
        size = shipsizes[0]
        for shipsize in shipsizes:
            if ships[shipsize]:
                done = False
                size = shipsize
                break
        if done:
            return True
        for r in range(self.s):
            for c in range(self.s):
                if not self.t[r][c]:
                    for o in (0, 1):
                        if self.shipfits(size, r, c, o):
                            tmp = self.copy()
                            tmp.placeship(size, r, c, o)
                            tmpships = ships.copy()
                            tmpships[size] -= 1
                            if tmp.placeships(shipsizes, tmpships):
                                return True
        return False

    def occ(self, r, c):
        if not self.offboard(r, c):
            self.t[r][c] = 1

    def offboard(self, r, c):
        return (r < 0 or c < 0 or r >= self.s or c >= self.s)


game = SeaBattle(10)

print("Welcome to Sea Battle!\n")

comm = ""
while True:
    print(game)
    print("What would you like to do?")
    comm = input("")
    if comm == "exit":
        break
    game.command(comm)

print("Thanks for playing!")
