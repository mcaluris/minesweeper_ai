import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def get_safes(self):
        if self.safes:
            return self.safes
        return []

    def get_mines(self):
        if self.mines:
            return self.mines
        return []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        cells, new_count = self.nearby_cells(cell, count)
        new_sentence = Sentence(cells, new_count)
        self.make_inferences(new_sentence)

        # update knowledge
        self.knowledge.append(new_sentence)
        self.clean_up()
        self.remove_knowns()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        """
        for safe_move in self.safes:
            if safe_move not in self.moves_made and safe_move not in self.mines:
                return safe_move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        """
        moves_left_to_play = []
        for i in range(8):
            for j in range(8):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    moves_left_to_play.append((i, j))
        random.shuffle(moves_left_to_play)
        if moves_left_to_play:
            return moves_left_to_play[0]
        return None

    def nearby_cells(self, cell, count):

        cells = set()

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width and (i, j) not in self.safes and (i, j) not in self.mines:
                    cells.add((i, j))
                if (i, j) in self.mines:
                    count -= 1
        return cells, count

    def remove_knowns(self):
        new_knowledge = []
        for sentence in self.knowledge:
            new_knowledge.append(sentence)
            if sentence.known_mines():
                new_mines = copy.deepcopy(sentence.known_mines())
                for mine in new_mines:
                    self.mark_mine(mine)
                new_knowledge.pop(-1)
            elif sentence.known_safes():
                new_safes = copy.deepcopy(sentence.known_safes())
                for safe in new_safes:
                    self.mark_safe(safe)
                new_knowledge.pop(-1)
        self.knowledge = new_knowledge

    def clean_up(self):
        unique_knowledge = []
        for sentence in self.knowledge:
            if sentence not in unique_knowledge:
                unique_knowledge.append(sentence)
        self.knowledge = unique_knowledge

    def make_inferences(self, new_sentence):
        for sentence in self.knowledge:
            self.clean_up()
            if sentence.cells.issuperset(new_sentence.cells):
                set_difference = sentence.cells.difference(new_sentence.cells)
                if set_difference:
                    if sentence.count == new_sentence.count:
                        for safe in set_difference:
                            self.mark_safe(safe)
                    elif len(set_difference) == sentence.count - new_sentence.count:
                        for mine in set_difference:
                            self.mark_mine(mine)
                    else:
                        new_new_sentence = Sentence(
                            set_difference, sentence.count - new_sentence.count)
                        self.knowledge.append(new_new_sentence)
            elif new_sentence.cells.issuperset(sentence.cells):
                set_difference = sentence.cells.difference(new_sentence.cells)
                if set_difference:
                    if sentence.count == new_sentence.count:
                        for safe in set_difference:
                            self.mark_safe(safe)
                    elif len(set_difference) == new_sentence.count - sentence.count:
                        for mine in set_difference:
                            self.mark_mine(mine)
                    else:
                        new_new_sentence = Sentence(
                            set_difference, new_sentence.count - sentence.count)
                        self.knowledge.append(new_new_sentence)
