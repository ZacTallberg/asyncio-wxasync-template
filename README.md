Asynchronous app that runs a system tray icon and gui window

Includes:
  - runtime_storage accessible from both synchronous and asychronous contexts
	- A task scheduling system to allow for any number of instances of a single function OR any number of different functions running on separate threads concurrently (including the ability to define the # of workers who process these tasks)
	- Asynchronous callbacks from functions called from button clicks/other gui interactions
