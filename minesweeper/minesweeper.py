import itertools
import random


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
        self.known_mine_set = set()
        self.known_safe_set = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            for cell in self.cells.copy():
                self.mark_mine(cell=cell)
        return self.known_mine_set
        raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            for cell in self.cells.copy():
                self.mark_safe(cell=cell)
        return self.known_safe_set
        raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if (cell in self.cells):
            self.known_mine_set.add(cell)
            self.cells.remove(cell)
            self.count-=1
        return
        raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if (cell in self.cells):
            self.known_safe_set.add(cell)
            self.cells.remove(cell)
        return
        raise NotImplementedError


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

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        print(f"current cell >>>>>> ::::: {cell}")
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # add sentences based on the value of cell into the knowledge of our AI
        new_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell or (i, j) in self.safes:
                    continue
                if ((i, j) in self.mines):
                    count-=1
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    new_cells.add((i, j))
        new_sentence = Sentence(new_cells, count)
        if new_sentence not in self.knowledge:
            self.knowledge.append(new_sentence)

        # remove a cell if it exists in an old sentence
        for sentence in self.knowledge:
            for _cell in sentence.cells.copy():
                if cell == _cell:
                    sentence.cells.remove(_cell)

        self.mark_sels_as_mine_or_safe()

        # checking if a set is a subset of another set, and creating a new set
        new_sentences = []
        for sentence in self.knowledge:
            for _sentence in self.knowledge:
                if sentence == _sentence or len(sentence.cells) == len(_sentence.cells):
                    continue
                if sentence.cells.issubset(_sentence.cells):
                    new_cells = _sentence.cells.difference(sentence.cells)
                    new_count = _sentence.count - sentence.count
                    new_sentences.append(Sentence(cells=new_cells, count=new_count))
                elif _sentence.cells.issubset(sentence.cells):
                    new_cells = sentence.cells.difference(_sentence.cells)
                    new_count = sentence.count - _sentence.count
                    new_sentences.append(Sentence(cells=new_cells, count=new_count))
        if new_sentence:
            self.knowledge.extend(new_sentences)

        self.mark_sels_as_mine_or_safe()
        
        return
        raise NotImplementedError

    def mark_sels_as_mine_or_safe(self):
        # marking additional cells as mines or safe
        sentences_to_remove = []
        for sentence in self.knowledge.copy():
            if len(sentence.cells) == 0:
                sentences_to_remove.append(sentence)
                continue
            if len(sentence.cells) == sentence.count and sentence.count != 0:
                for cell in sentence.cells.copy():
                    self.mark_mine(cell)
                sentences_to_remove.append(sentence) # remove the sentence since all cells are mines
            if (sentence.count == 0):
                for cell in sentence.cells.copy():
                    self.mark_safe(cell)
                sentences_to_remove.append(sentence) # remove the senetence since all cells are safe
        
        for sentence in sentences_to_remove:
            if sentence in self.knowledge:
                self.knowledge.remove(sentence)

        for sentence in self.knowledge:
            for cell in sentence.cells.copy():
                if cell in self.mines:
                    sentence.remove(cell)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None
        raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        random_moves = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    random_moves.append((i, j))
        if (random_moves):
            return random.choice(random_moves)
        return None
        raise NotImplementedError
