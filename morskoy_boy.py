import tkinter as tk
from tkinter import messagebox
import random


class Ship:
    def __init__(self, size):
        self.size = size
        self.positions = []
        self.hits = 0

    def is_sunk(self):
        return self.hits == self.size


class Game_Ship:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Морской бой")
        self.root.geometry("800x600")

        self.colors = {
            "water": "#4A90E2",
            "ship": "#5D4037",
            "ship_hit": "#D32F2F",
            "miss": "#BDBDBD",
            "around_ship": "#757575",
            "highlight": "#81C784",
            "invalid": "#E57373"
        }

        self.player_board = [[0] * 10 for _ in range(10)]
        self.bot_board = [[0] * 10 for _ in range(10)]

        self.player_ships = []
        self.bot_ships = []

        self.ships_to_place = {1: 4, 2: 3, 3: 2, 4: 1}
        self.selected_ship_size = None
        self.ship_orientation = "horizontal"

        self.player_turn = True
        self.bot_hunt_stack = []
        self.bot_last_hit = None
        self.game_over_flag = False

        self.sozdanie_glavnogo_okna()
    def sozdanie_glavnogo_okna(self):
        self.clear_window()
        self.game_over_flag = False

        tk.Label(self.root, text="Игра: морской бой", font=("Arial", 24, "bold"), fg="black").pack(pady=20)

        center_frame = tk.Frame(self.root)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Button(center_frame, text="Начать игру", font=("Arial", 14), command=self.nachalo_igri,
                  bg="lightgreen", width=20, height=2).pack(pady=10)
        tk.Button(center_frame, text="Справка", font=("Arial", 14), command=self.spravka,
                  bg="lightblue", width=20, height=2).pack(pady=10)
    def spravka(self):
        messagebox.showinfo("Справка",
                            "Цель игры: уничтожить первому все корабли соперника. \n\n"
                            "Корабли: \n- однопалубный: 4;\n- двухпалубный: 3;\n- трёхпалубный: 2;\n- четырёпалубный: 1.\n\n"
                            "Правила размещения: \n"
                            "- корабли нельзя располагать по диагонали — только по горизонтали или вертикали;\n"
                            "- корабли не должны касаться друг друга ни боками, ни углами;\n"
                            "- между ними должна быть хотя бы одна клетка;\n"
                            "- размещать можно в любой части поля, соблюдая размер и форму.\n")

    def nachalo_igri(self):
        self.sozdanie_igrovogo_polya()
    def sozdanie_igrovogo_polya(self):
        self.clear_window()
        self.game_over_flag = False
        tk.Label(self.root, text="Расстановка кораблей", font=("Arial", 18, "bold")).pack(pady=10)

        self.info_label = tk.Label(self.root, text="Выберите корабль для размещения:", font=("Arial", 12))
        self.info_label.pack()

        ship_frame = tk.Frame(self.root)
        ship_frame.pack(pady=10)

        self.ship_buttons = {}
        for size in sorted(self.ships_to_place.keys()):
            count = self.ships_to_place[size]
            btn = tk.Button(ship_frame, text=f"{size}-палубный ({count} шт)",
                            width=15, height=2, bg="lightblue",
                            command=lambda s=size: self.vibor_korablya(s))
            btn.pack(side=tk.LEFT, padx=5)
            self.ship_buttons[size] = btn

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        tk.Button(control_frame, text="Повернуть корабль", command=self.vibor_orientacii).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Рандомная расстановка", command=self.random_rasstanovka_korablei).pack(
            side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Начать игру", command=self.proverka_na_razmechenie_vsex_korablei,
                  bg="lightgreen").pack(side=tk.LEFT, padx=5)

        self.sozdanie_polya_rasstanovka_korablei()
    def sozdanie_polya_rasstanovka_korablei(self):
        board_frame = tk.Frame(self.root)
        board_frame.pack(pady=20)

        letters_frame = tk.Frame(board_frame)
        letters_frame.pack()
        tk.Label(letters_frame, width=3).grid(row=0, column=0)
        for j in range(10):
            tk.Label(letters_frame, text=chr(65 + j), width=3, font=("Arial", 10, "bold")).grid(row=0, column=j + 1)

        self.board_frame = tk.Frame(board_frame)
        self.board_frame.pack()
        self.buttons = [[None] * 10 for _ in range(10)]

        for i in range(10):
            tk.Label(self.board_frame, text=str(i + 1), width=3, font=("Arial", 10, "bold")).grid(row=i, column=0)
            for j in range(10):
                btn = tk.Button(self.board_frame, width=3, height=1, bg=self.colors["water"],
                                command=lambda x=i, y=j: self.razmechenie_vibrannogo_korablya(x, y))
                btn.grid(row=i, column=j + 1, padx=1, pady=1)
                btn.bind("<Enter>", lambda e, x=i, y=j: self.navedenie_na_kletky_pri_rasstanovke(x, y))
                btn.bind("<Leave>", lambda e: self.skritie_prosmotra_pri_navedenii())
                self.buttons[i][j] = btn
    def vibor_korablya(self, size):
        if self.game_over_flag:
            return
        if self.ships_to_place[size] > 0:
            self.selected_ship_size = size
            for s, btn in self.ship_buttons.items():
                if s == size:
                    btn.config(bg="darkblue", fg="white", relief='sunken')
                else:
                    if self.ships_to_place[s] > 0:
                        btn.config(bg="lightblue", fg="black", relief='raised')
                    else:
                        btn.config(bg="#ff7777", fg="black", relief='raised')
            self.info_label.config(text=f"Выбран {size}-палубный корабль")
    def vibor_orientacii(self):
        if self.game_over_flag:
            return
        self.ship_orientation = "vertical" if self.ship_orientation == "horizontal" else "horizontal"
    def navedenie_na_kletky_pri_rasstanovke(self, x, y):
        if self.game_over_flag or not self.selected_ship_size:
            return

        size = self.selected_ship_size
        positions = self.vichislenie_koordinat(x, y, size)
        if not positions:
            return

        valid = self.proverka_na_razmechenie_korablya(positions)
        for px, py in positions:
            self.buttons[px][py].config(bg=self.colors["highlight"] if valid else self.colors["invalid"])
    def skritie_prosmotra_pri_navedenii(self):
        for i in range(10):
            for j in range(10):
                self.buttons[i][j].config(
                    bg=self.colors["ship"] if self.player_board[i][j] == 1 else self.colors["water"])
    def vichislenie_koordinat(self, x, y, size):
        if self.ship_orientation == "horizontal":
            if y + size > 10:
                return None
            return [(x, y + i) for i in range(size)]
        else:
            if x + size > 10:
                return None
            return [(x + i, y) for i in range(size)]
    def proverka_na_razmechenie_korablya(self, positions):
        for px, py in positions:
            if self.player_board[px][py] != 0:
                return False
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                nx, ny = px + dx, py + dy
                if 0 <= nx < 10 and 0 <= ny < 10 and self.player_board[nx][ny] != 0:
                    if (nx, ny) not in positions:
                        return False
        return True
    def razmechenie_vibrannogo_korablya(self, x, y):
        if self.game_over_flag:
            return
        if not self.selected_ship_size or self.ships_to_place[self.selected_ship_size] <= 0:
            return

        size = self.selected_ship_size
        positions = self.vichislenie_koordinat(x, y, size)
        if not positions or not self.proverka_na_razmechenie_korablya(positions):
            return

        ship = Ship(size)
        for pos in positions:
            self.player_board[pos[0]][pos[1]] = 1
            self.buttons[pos[0]][pos[1]].config(bg=self.colors["ship"])
            ship.positions.append(pos)

        self.player_ships.append(ship)
        self.ships_to_place[size] -= 1

        self.ship_buttons[size].config(text=f"{size}-палубный ({self.ships_to_place[size]} шт)")
        if self.ships_to_place[size] == 0:
            self.ship_buttons[size].config(bg="#ff7777", fg="black", state=tk.DISABLED)
            self.selected_ship_size = None
        else:
            self.ship_buttons[size].config(bg="lightblue", fg="black")
        self.info_label.config(text="Выберите корабль для размещения")
    def random_rasstanovka_korablei(self):
        if self.game_over_flag:
            return
        self.player_board = [[0] * 10 for _ in range(10)]
        self.player_ships = []
        self.ships_to_place = {1: 4, 2: 3, 3: 2, 4: 1}

        for size, count in list(self.ships_to_place.items()):
            for _ in range(count):
                placed = False
                attempts = 0
                while not placed and attempts < 100:
                    orientation = random.choice(["horizontal", "vertical"])
                    x = random.randint(0, 9 if orientation == "horizontal" else 10 - size)
                    y = random.randint(0, 10 - size if orientation == "horizontal" else 9)

                    positions = self.vichislenie_koordinat(x, y, size)
                    if positions and self.proverka_na_razmechenie_korablya(positions):
                        ship = Ship(size)
                        for pos in positions:
                            self.player_board[pos[0]][pos[1]] = 1
                            ship.positions.append(pos)
                        self.player_ships.append(ship)
                        self.ships_to_place[size] -= 1
                        placed = True
                    attempts += 1

        for i in range(10):
            for j in range(10):
                self.buttons[i][j].config(
                    bg=self.colors["ship"] if self.player_board[i][j] == 1 else self.colors["water"])

        for size, btn in self.ship_buttons.items():
            btn.config(text=f"{size}-палубный ({self.ships_to_place[size]} шт)")
            if self.ships_to_place[size] == 0:
                btn.config(bg="#ff7777", fg="black", state=tk.DISABLED)
            else:
                btn.config(bg="lightblue", fg="black", state=tk.NORMAL)
    def proverka_na_razmechenie_vsex_korablei(self):
        if self.game_over_flag:
            return
        if any(count > 0 for count in self.ships_to_place.values()):
            messagebox.showwarning("Не все корабли размещены", "Нужно разместить все корабли!")
            return

        self.rasstanovka_korablei_protivnika()
        self.start_game()
    def rasstanovka_korablei_protivnika(self):
        self.bot_board = [[0] * 10 for _ in range(10)]
        self.bot_ships = []
        bot_ships_to_place = {1: 4, 2: 3, 3: 2, 4: 1}

        for size, count in bot_ships_to_place.items():
            for _ in range(count):
                placed = False
                while not placed:
                    orientation = random.choice(["horizontal", "vertical"])
                    x = random.randint(0, 9 if orientation == "horizontal" else 10 - size)
                    y = random.randint(0, 10 - size if orientation == "horizontal" else 9)

                    positions = self.vichislenie_koordinat(x, y, size)
                    if positions and self.proverka_rasstanovki_korablei_protivnika(positions):
                        ship = Ship(size)
                        for pos in positions:
                            self.bot_board[pos[0]][pos[1]] = 1
                            ship.positions.append(pos)
                        self.bot_ships.append(ship)
                        placed = True
    def proverka_rasstanovki_korablei_protivnika(self, positions):
        for px, py in positions:
            if self.bot_board[px][py] != 0:
                return False
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                nx, ny = px + dx, py + dy
                if 0 <= nx < 10 and 0 <= ny < 10 and self.bot_board[nx][ny] != 0:
                    if (nx, ny) not in positions:
                        return False
        return True
    def start_game(self):
        self.clear_window()
        self.game_over_flag = False
        tk.Label(self.root, text="Бой начался!", font=("Arial", 18, "bold")).pack(pady=10)

        boards_frame = tk.Frame(self.root)
        boards_frame.pack(pady=20)

        self.sozdanie_igrovogo_polya_battle(boards_frame, "Ваше поле", self.player_board, 0, False)
        self.sozdanie_igrovogo_polya_battle(boards_frame, "Поле противника", self.bot_board, 1, True)

        self.status_label = tk.Label(self.root, text="Ваш ход!", font=("Arial", 14), fg="black")
        self.status_label.pack(pady=10)
    def sozdanie_igrovogo_polya_battle(self, parent, title, board, column, interactive):
        frame = tk.Frame(parent)
        frame.grid(row=0, column=column, padx=20)
        tk.Label(frame, text=title, font=("Arial", 12, "bold")).pack()

        board_frame = tk.Frame(frame)
        board_frame.pack(pady=10)

        buttons = [[None] * 10 for _ in range(10)]
        for i in range(10):
            for j in range(10):
                if interactive:
                    btn = tk.Button(board_frame, width=3, height=1, bg=self.colors["water"],
                                    command=lambda x=i, y=j: self.obrabotka_xoda_polzovatelya(x, y))
                else:
                    if board[i][j] == 2:
                        color = self.colors["ship_hit"]
                        text = "X"
                    elif board[i][j] == 3:
                        color = self.colors["miss"]
                        text = "•"
                    elif board[i][j] == 5:
                        color = self.colors["around_ship"]
                        text = "•"
                    elif board[i][j] == 1:
                        color = self.colors["ship"]
                        text = ""
                    else:  # Вода
                        color = self.colors["water"]
                        text = ""

                    btn = tk.Button(board_frame, width=3, height=1, bg=color, text=text,
                                    state=tk.DISABLED, disabledforeground="white")
                btn.grid(row=i, column=j, padx=1, pady=1)
                buttons[i][j] = btn

        if interactive:
            self.bot_buttons = buttons
        else:
            self.player_buttons = buttons
    def obrabotka_xoda_polzovatelya(self, x, y):
        if self.game_over_flag or not self.player_turn or self.bot_board[x][y] in (2, 3, 5):
            return

        if self.bot_board[x][y] == 1:
            self.bot_board[x][y] = 2
            self.bot_buttons[x][y].config(bg=self.colors["ship_hit"], text="X",
                                          disabledforeground="white", state=tk.DISABLED)
            for ship in self.bot_ships:
                if (x, y) in ship.positions:
                    ship.hits += 1
                    if ship.is_sunk():
                        self.otmetka_vokrug_korablya(ship)
                        self.status_label.config(text="Вы потопили корабль!")
                    else:
                        self.status_label.config(text="Попадание! Снова Ваш ход!")
                    break
        else:
            self.bot_board[x][y] = 3
            self.bot_buttons[x][y].config(bg=self.colors["miss"], text="•",
                                          disabledforeground="black", state=tk.DISABLED)
            self.status_label.config(text="Промах! Ход противника.")
            self.player_turn = False
            self.root.after(400, self.xod_protivnika)

        if all(ship.is_sunk() for ship in self.bot_ships):
            self.game_over("Вы победили!")
    def otmetka_vokrug_korablya(self, ship):
        for px, py in ship.positions:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < 10 and 0 <= ny < 10 and self.bot_board[nx][ny] == 0:
                        self.bot_board[nx][ny] = 5
                        self.bot_buttons[nx][ny].config(bg=self.colors["around_ship"], text="•",
                                                        disabledforeground="black")
    def xod_protivnika(self):
        if self.game_over_flag:
            return
        if self.bot_hunt_stack:
            x, y = self.bot_hunt_stack.pop(0)
            if 0 <= x < 10 and 0 <= y < 10 and self.player_board[x][y] not in (2, 3, 5):
                self.obrabotka_xoda_protivnika(x, y)
                return

        empty_cells = [(i, j) for i in range(10) for j in range(10) if self.player_board[i][j] not in (2, 3, 5)]
        if empty_cells:
            x, y = random.choice(empty_cells)
            self.obrabotka_xoda_protivnika(x, y)
    def obrabotka_xoda_protivnika(self, x, y):
        if self.player_board[x][y] == 1:
            self.player_board[x][y] = 2
            self.player_buttons[x][y].config(bg=self.colors["ship_hit"], text="X")

            for ship in self.player_ships:
                if (x, y) in ship.positions:
                    ship.hits += 1
                    if ship.is_sunk():
                        self.otmetka_vokrug_korablya_igroka(ship)
                        self.status_label.config(text="Противник потопил ваш корабль!")
                    else:
                        self.status_label.config(text="Противник попал!")
                        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < 10 and 0 <= ny < 10:
                                self.bot_hunt_stack.append((nx, ny))
                    break
            self.root.after(400, self.xod_protivnika)
        else:
            self.player_board[x][y] = 3
            self.player_buttons[x][y].config(bg=self.colors["miss"], text="•")
            self.status_label.config(text="Ваш ход!")
            self.player_turn = True

        if all(ship.is_sunk() for ship in self.player_ships):
            self.game_over("Противник победил!")
    def otmetka_vokrug_korablya_igroka(self, ship):
        for px, py in ship.positions:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < 10 and 0 <= ny < 10 and self.player_board[nx][ny] == 0:
                        self.player_board[nx][ny] = 5
                        self.player_buttons[nx][ny].config(bg=self.colors["around_ship"], text="•")
    def game_over(self, message):
        self.game_over_flag = True
        messagebox.showinfo("Игра окончена", message)

        tk.Button(self.root, text="Начать игру заново", command=self.restart_game,
                  font=("Arial", 14), bg="lightgreen", width=20, height=2).pack(pady=20)
    def restart_game(self):
        self.player_board = [[0] * 10 for _ in range(10)]
        self.bot_board = [[0] * 10 for _ in range(10)]
        self.player_ships = []
        self.bot_ships = []
        self.ships_to_place = {1: 4, 2: 3, 3: 2, 4: 1}
        self.selected_ship_size = None
        self.ship_orientation = "horizontal"
        self.player_turn = True
        self.bot_hunt_stack = []
        self.bot_last_hit = None
        self.game_over_flag = False

        self.sozdanie_igrovogo_polya()
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = Game_Ship()
    game.run()