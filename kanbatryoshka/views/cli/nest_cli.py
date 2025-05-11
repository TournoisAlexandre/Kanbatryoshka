import sys
import os
from kanbatryoshka.models.nest import Nest

class NestCLI:
    def __init__(self):
        self.app = Nest()
        self.commands = {
            "help": self.show_help,
            "exit": self.exit_app,
            "ls": self.list_items,
            "create-board": self.create_board,
            "select-board": self.select_board,
            "add-list": self.add_list,
            "add-task": self.add_task,
            "open-task": self.open_task_board,
            "back": self.go_back,
            "move-task": self.move_task,
            "path": self.show_path,
            "clear": self.clear_screen
        }

    def clear_screen(self, *args):
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self):
        print("=== kanbatryoshka - CLI ===")
        print("Tapez 'help' pour voir les commandes disponibles.")

        while(True):
            current = self.app.get_current_board()
            prompt = "> " if not current else f"{current.title} > "

            try:
                command = input(prompt).strip()
                if not command:
                    continue

                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in self.commands:
                    self.commands[cmd](*args)
                else:
                    print(f"Commande inconnue: {cmd}")
                    print("Tapez 'help' pour voir les commandes disponibles.")

            except Exception as e:
                print(f"Erreur; {str(e)}")

    def show_help(self, *args):
        print("\n=== Commandes disponibles ===")
        print("help                                 - Affiche cette aide")
        print("exit                                 - Quitte l'application")
        print("ls                                   - Liste les tableaux, listes et tâches")
        print("create-board <titre> [description]   - Crée un nouveau tableau")
        print("select-board <board_id>              - Sélectionne un tableau")
        print("add-list <titre>                     - Ajoute une liste au tableau courant")
        print("add-task <list_id> <titre> [desc]    - Ajoute une tâche à une liste")
        print("open-task <list_id> <task_id>        - Ouvre le tableau d'une tâche")
        print("back                                 - Retourne au tableau parent")
        print("move-task <task_id> <src_id> <dst_id>- Déplace une tâche entre listes")
        print("path                                 - Affiche le chemin de navigation")
        print("clear                                - Efface l'écran\n")

    def exit_app(self, *args):
        print("au revoir!")
        sys.exit(0)
    
    def list_items(self, *args):
        if not args:
            self._list_all()
        elif args[0] == "boards":
            self._list_boards()
        elif args[0] == "lists" and len(args) > 1:
            self._list_tasks(args[1])

    def _list_all(self):
        current = self.app.get_current_board()

        if not current:
            print("\n=== Tableaux principaux ===")
            if not self.app.boards:
                print("Aucun tableau créé. Utilisez 'create-board' pour commencer.")
            else:
                for idx, board in enumerate(self.app.boards):
                    print(f"{idx+1}. [{board.id}] {board.title} - {board.description}")
            print()
            return
        
        print(f"\n=== Tableau: {current.title} ===")
        print(f"Description: {current.description}")
        
        if not current.lists:
            print("Aucune liste dans ce tableau. Utilisez 'add-list' pour en créer.")
        
        for idx, lst in enumerate(current.lists):
            print(f"\n-- Liste {idx+1}: [{lst.id}] {lst.title} --")
            if not lst.tasks:
                print("  Aucune tâche dans cette liste.")
            
            for task_idx, task in enumerate(lst.tasks):
                print(f"  {task_idx+1}. [{task.id}] {task.title}")
                if task.description:
                    print(f"     {task.description}")
                print(f"     [Double-cliquez pour ouvrir le board imbriqué]")
        print()

    def _list_boards(self):
        print("\n=== Tableaux principaux ===")
        if not self.app.boards:
            print("Aucun tableau créé.")
        else:
            for idx, board in enumerate(self.app.boards):
                print(f"{idx+1}. [{board.id}] {board.title}")
        print()

    def _list_tasks(self, list_id):
        current = self.app.get_current_board()
        if not current:
            print("Aucun tableau sélectionné.")
            return
        
        for lst in current.lists:
            if lst.id == list_id:
                print(f"\n=== Tâches dans la liste: {lst.title} ===")
                if not lst.tasks:
                    print("Aucune tâche dans cette liste.")
                
                for idx, task in enumerate(lst.tasks):
                    print(f"{idx+1}. [{task.id}] {task.title}")
                    if task.description:
                        print(f"   {task.description}")
                print()
                return
        
        print(f"Liste avec ID {list_id} non trouvée.")

    def create_board(self, *args):
        if not args:
            print("Erreur: Le titre du tableau est requis.")
            return
        
        title = args[0]
        description = " ".join(args[1:]) if len(args) > 1 else ""
        
        board = self.app.create_board(title, description)
        print(f"Tableau créé avec succès: [{board.id}] {board.title}")

    def select_board(self, *args):
        if not args:
            print("Erreur: L'ID du tableau est requis.")
            return
        
        board_id = args[0]
        if self.app.select_board(board_id):
            board = self.app.get_current_board()
            print(f"Tableau sélectionné: {board.title}")
        else:
            print(f"Tableau avec ID {board_id} non trouvé.")

    def add_list(self, *args):
        if not args:
            print("Erreur: Le titre de la liste est requis.")
            return
        
        current = self.app.get_current_board()
        if not current:
            print("Erreur: Aucun tableau sélectionné.")
            return
        
        title = " ".join(args)
        list_obj = self.app.add_list_to_current_board(title)
        print(f"Liste ajoutée: [{list_obj.id}] {list_obj.title}")

    def add_task(self, *args):
        if len(args) < 2:
            print("Erreur: L'ID de la liste et le titre de la tâche sont requis.")
            return
        
        list_id = args[0]
        title = args[1]
        description = " ".join(args[2:]) if len(args) > 2 else ""
        
        task = self.app.add_task_to_list(list_id, title, description)
        if task:
            print(f"Tâche ajoutée: [{task.id}] {task.title}")
        else:
            print(f"Liste avec ID {list_id} non trouvée.")
    
    def open_task_board(self, *args):
        if len(args) < 2:
            print("Erreur: L'ID de la liste et l'ID de la tâche sont requis.")
            return
        
        list_id = args[0]
        task_id = args[1]
        
        if self.app.navigate_to_task_board(list_id, task_id):
            board = self.app.get_current_board()
            print(f"Navigué vers le tableau de la tâche: {board.title}")
        else:
            print("Tâche ou liste non trouvée.")
    
    def go_back(self, *args):
        if self.app.back_to_parent():
            board = self.app.get_current_board()
            print(f"Retourné au tableau parent: {board.title}")
        else:
            print("Déjà au niveau principal.")
    
    def move_task(self, *args):
        if len(args) < 3:
            print("Erreur: L'ID de la tâche, l'ID de la liste source et l'ID de la liste cible sont requis.")
            return
        
        task_id = args[0]
        source_list_id = args[1]
        target_list_id = args[2]
        
        if self.app.move_task_between_lists(task_id, source_list_id, target_list_id):
            print(f"Tâche [{task_id}] déplacée avec succès.")
        else:
            print("Échec du déplacement. Vérifiez les IDs.")
    
    def show_path(self, *args):
        path = self.app.get_board_path()
        if not path:
            print("Vous êtes au niveau principal.")
            return
        
        print("Chemin de navigation:")
        print(" > ".join(path))