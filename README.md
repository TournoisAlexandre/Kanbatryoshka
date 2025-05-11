# Kanbatryoshka - Nested Kanban Board Manager
*Nest is the easy-to-pronounce name*
## Description
Kanbatryoshka is a project management application based on the Kanban methodology, allowing you to create task boards organized in lists. Its distinctive feature is the ability to nest boards within tasks, creating a flexible hierarchical structure to organize your projects. (There may be other software that does the same thing, I don't know, I was frustrated by the lack of sub-task management with Trello and decided to create my own version). For now this is a POC.

## Features

### Board Management
- Create boards with title and description
- Navigate between different boards
- Delete boards

### List Management
- Add custom lists to a board
- Move lists with drag-and-drop
- Delete lists

### Task Management
- Create tasks with title and description
- Edit and delete tasks
- Move tasks between lists
- Nest boards within tasks (recursive functionality)

### Navigation
- Hierarchical navigation between boards
- Breadcrumb trail to visualize board hierarchy
- Return to parent board

## Architecture

Kanbatryashka is built using the Model-View-Controller (MVC) design pattern:

### Model
- `Nest`: Main class managing all boards and business logic
- `Board`: Represents a board containing lists
- `List`: Represents a list containing tasks
- `Task`: Represents a task that can contain its own board

### View
- `BoardWidget`: Displays a board with its lists
- `ListWidget`: Displays a list with its tasks
- `TaskWidget`: Displays a task with its title and description

### Controller
- `BoardController`: Manages interactions with a board
- `ListController`: Manages interactions with a list
- `TaskController`: Manages interactions with a task

## Technologies Used
- Python 3.x
- PySide6 (Qt graphical interface)

## How to Use the Application

### Getting Started
1. Launch the application via the main file
2. An initial board is automatically displayed

### Creating a List
1. Click the "+ Add a list" button on the right
2. Enter the name of the list
3. Confirm to add the list

### Creating a Task
1. Click the "+ Add a task" button at the bottom of a list
2. Enter the title and description of the task
3. Confirm to add the task

### Navigating Nested Boards
1. Double-click on a task to open its nested board
2. Use the back button to return to the parent board

### Editing a Task
1. Click on the "✎" icon of a task
2. Modify the title and/or description
3. Confirm to save the changes

### Export/Import a Board
1. Click on the "File" menu at the top left
2. Click on the "Save" menu option to pick where you want to export the board
3. Click on the "Load" menu option to pick from where you want to import a board
## Benefits
- Hierarchical organization of projects
- Intuitive interface with drag-and-drop
- Flexible structure adapted to complex projects
- Clear visualization of task progress

## Coming Soon (more or less)
- Hierarchy and timeline visualisation
- Undo/Redo
- Relationship and dependancies between tasks
- Priority System
- Schedule
- Time Tracking
- Progress calculation
- Labels and filters for tasks
- Templates
- Media Management
- UI/UX Improvements
- Statistics and Analytics
- Cloud synchronization
- Real-time collaboration
- Third-Party integration


---

*Kanbatryashka - Organize your projects in a hierarchical and intuitive way.*
