import pytest
from kanbatryoshka.models.board import Board
from kanbatryoshka.models.list import List
from kanbatryoshka.models.task import Task
from kanbatryoshka.models.nest import Nest

#region Task

def test_task_creation():
    task = Task("Test Task Title", "Test Task Description")

    assert task.title == "Test Task Title"
    assert task.description == "Test Task Description"
    assert task.id is not None
    assert task.created_at is not None
    assert task.updated_at is not None
    assert task.board is not None

#endregion Task

#region List

def test_list_creation():
    list = List("Test List Title")

    assert list.title == "Test List Title"
    assert list.id is not None
    assert list.created_at is not None
    assert len(list.tasks) == 0

def test_add_task():
    list = List("Test List Title")
    task = Task("Test Task Title")
    list.add_task(task)

    assert len(list.tasks) == 1
    assert list.tasks[0] == task

def test_remove_task():
    list = List("Test List Title")
    task = Task("Test Task Title")
    list.add_task(task)

    assert len(list.tasks) == 1
    list.remove_task(task.id)
    assert len(list.tasks) == 0

#endregion List

#region Board

def test_board_creation():
    board = Board("Test Board Title", "Test Board Description")

    assert board.title == "Test Board Title"
    assert board.description == "Test Board Description"
    assert board.id is not None
    assert board.created_at is not None
    assert board.updated_at is not None
    assert len(board.lists) == 3

def test_add_list():
    board = Board("Test Board Title", "Test Board Description")
    initial_count = len(board.lists)
    list = List("Test List Title")
    board.add_list(list)

    assert len(board.lists) == initial_count + 1
    assert board.lists[-1] == list

def test_remove_list():
    board = Board("Test Board Title", "Test Board Description")
    initial_count = len(board.lists)
    list = board.lists[0]

    board.remove_list(list.id)

    assert len(board.lists) == initial_count - 1

#endregion Board

@pytest.fixture
def nest():
    return Nest()

#region Nest

def test_nest_creation(nest):
    assert len(nest.boards) == 0
    assert nest.current_board is None
    assert len(nest.navigation_stack )== 0

def test_create_board(nest):
    board = nest.create_board("Test Board Title", "Test Board Description")

    assert len(nest.boards) == 1
    assert nest.boards[0] == board
    assert board.title == "Test Board Title"
    assert board.description == "Test Board Description"

def test_select_board(nest):
    board = nest.create_board("Test Board Title")
    assert nest.current_board is None
    result = nest.select_board(board.id)
    assert result is True
    assert nest.current_board == board

def test_get_current_board(nest):
    board = nest.create_board("Test Board Title")
    result = nest.select_board(board.id)
    assert nest.get_current_board() == board

def test_navigate_to_task_board(nest):
    board = nest.create_board("Test Board Title")
    nest.select_board(board.id)
    list_id = board.lists[0].id
    task = Task("Test Task")
    board.lists[0].add_task(task)

    result = nest.navigate_to_task_board(list_id, task.id)
    assert result is True
    assert nest.get_current_board() == task.board
    assert len(nest.navigation_stack) == 1

def test_back_to_parent(nest):
    board = nest.create_board("Test Board Title")
    nest.select_board(board.id)
    list_id = board.lists[0].id
    task = Task("Test Task")
    board.lists[0].add_task(task)
    nest.navigate_to_task_board(list_id, task.id)

    result = nest.back_to_parent()
    assert result is True
    assert nest.get_current_board() == board
    assert len(nest.navigation_stack) == 0

def test_add_list_to_current_board(nest):
    board = nest.create_board("Test Board Title")
    nest.select_board(board.id)
    assert len(nest.current_board.lists) == 3
    list = nest.add_list_to_current_board("Test List Title")
    assert len(nest.current_board.lists) == 4
    assert nest.current_board.lists[-1] == list
    assert list.title == "Test List Title"

def test_remove_list_from_current_board(nest):
    board = nest.create_board("Test Board Title")
    nest.select_board(board.id)
    assert len(nest.current_board.lists) == 3
    list = nest.add_list_to_current_board("Test List Title")
    assert len(nest.current_board.lists) == 4
    nest.remove_list_from_current_board(list.id)
    assert len(nest.current_board.lists) == 3

def test_add_task_to_list(nest):
    board = nest.create_board("Test Board Title")
    nest.select_board(board.id)
    list_id = nest.current_board.lists[0].id
    
    task = nest.add_task_to_list(list_id, "Test Task Title", "Test Task Description")

    assert len(board.lists[0].tasks) == 1
    assert board.lists[0].tasks[0] == task
    assert task.title == "Test Task Title"
    assert task.description == "Test Task Description"

def test_move_task_between_lists(nest):
    board = nest.create_board("Test Board")
    nest.select_board(board.id)
    source_list_id = board.lists[0].id
    target_list_id = board.lists[1].id

    task = nest.add_task_to_list(source_list_id, "Task to Move")
    assert len(board.lists[0].tasks) == 1
    assert len(board.lists[1].tasks) == 0

    result = nest.move_task_between_lists(task.id, source_list_id, target_list_id)
    assert result is True
    assert len(board.lists[0].tasks) == 0
    assert len(board.lists[1].tasks) == 1
    assert board.lists[1].tasks[0].title == "Task to Move"

def test_get_board_path(nest):
    main_board = nest.create_board("Main Board")
    nest.select_board(main_board.id)
    
    list_id = main_board.lists[0].id
    task = nest.add_task_to_list(list_id, "Test Task")
    
    nest.navigate_to_task_board(list_id, task.id)
    
    path = nest.get_board_path()
    
    assert len(path) == 2

    assert path[0] == "Main Board"
    assert path[1] == "Board: Test Task"

    task_board = nest.current_board
    sublist_id = nest.add_list_to_current_board("New list").id
    subtask = nest.add_task_to_list(sublist_id, "Subtask")

    nest.navigate_to_task_board(sublist_id, subtask.id)
    
    path = nest.get_board_path()
    
    assert len(path) == 3
    assert path[0] == "Main Board"
    assert path[1] == "Board: Test Task"
    assert path[2] == "Board: Subtask"
    
    nest.back_to_parent()
    path = nest.get_board_path()
    assert len(path) == 2
    
    nest.back_to_parent()
    path = nest.get_board_path()
    assert len(path) == 1   

#endregion Nest