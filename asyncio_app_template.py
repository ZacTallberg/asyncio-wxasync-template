##------------------>
from aioscheduler import Manager, QueuedScheduler
import asyncio
from asyncio.events import get_event_loop
from datetime import datetime
import logging
from pythonping import ping
import threading
import wx
from wx.adv import TaskBarIcon, EVT_TASKBAR_LEFT_DOWN, EVT_TASKBAR_RIGHT_DOWN
from wxasync import WxAsyncApp, StartCoroutine


## wxasync --> https://github.com/sirk390/wxasync
## wxpython docs --> https://wxpython.org/Phoenix/docs/html/index.html
## wx.adv.TaskBarIcon --> https://stackoverflow.com/questions/49758794/python-3-wx-change-tray-icon
## bitcoin pirces --> https://linuxhit.com/how-to-easily-get-bitcoin-price-quotes-in-python/
## dynamic system tray icon text --> https://stackoverflow.com/questions/55381039/dynamic-system-tray-text-python-3
## simple wxasync app --> https://www.programmersought.com/article/55676496874/

##-------------> Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('logs.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)
##---------/

##------------------> Initialization
global _appdata
GlobalWxAsyncApp = None
_appdata = None
##---------/

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, loop=None):
        super(TaskBarIcon, self).__init__()
        self.set_grey()
        self.loop = loop or get_event_loop()
        self.Bind(EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.Bind(EVT_TASKBAR_RIGHT_DOWN, self.on_right_down)

    def set_green(self):
        green = 'green_icon.ico'
        self.SetIcon(wx.Icon(green))
    def set_red(self):
        red = 'red_icon.ico'
        self.SetIcon(wx.Icon(red))
    def set_grey(self):
        grey = 'grey_icon.ico'
        self.SetIcon(wx.Icon(grey))

    def on_left_down(self, event):
        logger.debug("Left click")
        # self.on_set_icon(_appdata.green)

    def on_right_down(self, event):
        logger.debug("Right click")
        # self.on_set_icon(_appdata.red)

    def on_hello(self, event):
        # logger.DEBUG('Hello!')
        print('Hello!')

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
##---------/

##-------------> Instantiate variables
loop = asyncio.get_event_loop()
app = WxAsyncApp()
number_of_beats = "Heartbeats!"
icon = TaskBarIcon()
start_time = datetime.now()
image_grey = './grey_icon.png'
image_red = './red_icon.png'
image_green = './green_icon.png'
##---------/

##-------------> Instantiate RUNTIME_STORAGE, which is persistent local storage outside the asyncio loop
RUNTIME_STORAGE = threading.local()
RUNTIME_STORAGE.loop = None
RUNTIME_STORAGE.global_app = None
RUNTIME_STORAGE.start_time = start_time
RUNTIME_STORAGE.grey = image_grey
RUNTIME_STORAGE.green = image_green
RUNTIME_STORAGE.red = image_red
RUNTIME_STORAGE.running = False
RUNTIME_STORAGE.heartbeats = 0
RUNTIME_STORAGE.number_of_beats = ''
RUNTIME_STORAGE.ping_status = ''
RUNTIME_STORAGE.beats_label = None
RUNTIME_STORAGE.status_label = None
RUNTIME_STORAGE.icon = icon 
RUNTIME_STORAGE.app = app
RUNTIME_STORAGE.count = 30000
RUNTIME_STORAGE.managers = 1
RUNTIME_STORAGE.manager = None
RUNTIME_STORAGE.ping_status = ''
####------------------> global variable ref
_appdata = RUNTIME_STORAGE
##---------/

##  point size = text size (int)
##  family = wx.DEFAULT, wx.DECORATIVE, wx.ROMAN, wx.SCRIPT, wx.SWISS, wx.MODERN. wx.MODERN 
##  style = wx.NORMAL, wx.SLANT or wx.ITALIC
##  weight = wx.NORMAL, wx.LIGHT or wx.BOLD
##  underlining =  True or False.
##  face_name = An optional string specifying the actual typeface to be used. If None, a default typeface will chosen based on the family.
class MainGUI(wx.Frame):   
    def __init__(self, parent=None,title=None,x_size=None,y_size=None):
        super(MainGUI, self).__init__(parent, title=title or 'wxasync gui and system tray icon template', size=((x_size or 610),(y_size or 100)))
        try:
            panel = wx.Panel(self) 
            vbox = wx.BoxSizer(wx.VERTICAL)
            label_num_beats = wx.StaticText(panel,-1,style=wx.ALIGN_CENTER)
            _appdata.beats_label = label_num_beats
            label_ping_status = wx.StaticText(panel,-1,style=wx.ALIGN_CENTER)
            _appdata.status_label = label_ping_status
            
            font = wx.Font(18,  wx.SWISS, wx.BOLD, wx.NORMAL) 
            label_num_beats.SetFont(font) 
            label_num_beats.SetLabel('THIS IS A TEST') 
            label_num_beats.SetForegroundColour((255,0,0)) 
            label_num_beats.SetBackgroundColour((0,0,0)) 
            vbox.Add(label_num_beats,0,wx.ALIGN_CENTER)

            label_ping_status.SetFont(font)
            label_ping_status.SetLabel('ANOTHER TEST')
            label_ping_status.Wrap(200)
            label_ping_status.SetForegroundColour((255,0,0)) 
            label_ping_status.SetBackgroundColour((0,0,0)) 
            vbox.Add(label_ping_status,0,wx.ALIGN_LEFT)

            panel.SetSizer(vbox)
            self.Centre()
            self.Show()

        except Exception as e:
            logger.error(e)

        StartCoroutine(self.update_gui, self)

    async def update_gui(self):
        while True:
            try:
                _appdata.status_label.SetLabel(_appdata.ping_status)
                _appdata.beats_label.SetLabel(_appdata.number_of_beats)
                await asyncio.sleep(0.5)
            except KeyboardInterrupt:
                logger.info("Received exit, exiting from outer exception loop")
            except Exception as e:
                logger.error(e)
                await asyncio.sleep(0.5)
##---------/

##------------------> Instantiate frame for interacting with
frame = MainGUI()
app.SetTopWindow(frame)
_appdata.frame = frame
##---------/

##-------------> Custom AsyncBind callback to account for _appdata
def AsyncBind(object, event, async_callback):
    if _appdata.app:
        print('have app data')
        app.AsyncBind(object, event, async_callback)
    elif GlobalWxAsyncApp is None:
        raise Exception("Create a 'WxAsyncApp' first")
    
    GlobalWxAsyncApp.AsyncBind(object, event, async_callback)

##-------------> Run a ping to google, set _appdata var based on response
async def ping_now(n):
    response = ping('8.8.8.8', count=1, timeout=1) 
    response_string_sanitized = str(response)[0:40].strip()
    if 'timed out' in str(response):
        logger.info(response_string_sanitized)
        _appdata.ping_status = 'No internet: {}'.format(response_string_sanitized)
        _appdata.icon.set_red()
        return False
    else:
        logger.info(response_string_sanitized)
        _appdata.ping_status = 'We have internet: {}'.format(response_string_sanitized)
        _appdata.icon.set_green()
        return True

##-------------> find all futures/tasks still running and wait for them to finish, called when app is quit()
async def quit():
    pending_tasks = [
        task for task in asyncio.all_tasks() if not task.done()
    ]
    print(pending_tasks)
    tasks = loop.run_until_complete(asyncio.gather(*pending_tasks))
    tasks.cancel()
    tasks.exception()
    loop.close()

##-------------> Beat once according to the my job queue scheduled by the aioscheduler manager.
async def heartbeat(n: int):
    try:
        _appdata.number_of_beats = "{} heartbeats <3".format(n)
        _appdata.heartbeats = n
        await ping_now(n)
        await asyncio.sleep(1)
        return True
    except KeyboardInterrupt:
        logger.info("Received exit, exiting from outer exception loop")
        await quit()
    except Exception as e:
        logger.error(e)
        await quit()

##-------------> With multiple manager schedulers, I can run any number of instances of a single function
##-------------> and have them automatically allocated to run on different threads concurrently
##-------------> Start the heart beating, with the number of different threads to run on {{@_appdata.managers() -> int:}}
##-------------> This is essentially a my template to automatically schedule jobs to run on disparate threads concurrently
async def start_beating(managers=None):
    logger.info('Hello!')
    # The number of Schedulers to use-- Leaving out cls defaults to TimedScheduler
    manager = Manager(managers or _appdata.managers, cls=QueuedScheduler)
    manager.start()
    _appdata.manager = manager
    try:
        # Schedule 30,000 instances of the 'heartbeat' job spread across {_appdata.managers} number of threads
        for n, i in enumerate(range(30000)):
            manager.schedule(heartbeat(n+1))
        print('scheduled')
        return True
    except KeyboardInterrupt:
        await quit()
    except Exception as e:
        logger.error(e)
        await quit()

async def initialize_async_progress_dialogue():
    await start_beating()

    ## If you want to kick off any other loops/functions, do it here

##------------->  Runtime
loop.create_task(initialize_async_progress_dialogue())
loop.run_until_complete(app.MainLoop())
