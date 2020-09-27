import asyncio

from graia.application import GraiaMiraiApplication, Session
from graia.application.event.mirai import NewFriendRequestEvent
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain, Image
from graia.application.friend import Friend
from graia.application.group import Group, Member
from graia.broadcast import Broadcast

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)

qqClient = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://0.0.0.0:8080", # 填入 httpapi 服务运行的地址
        authKey="INITKEYjzSpjHUR", # 填入 authKey
        account=3277619822, # 你的机器人的 qq 号
        websocket=True # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    ),
    enable_chat_log=True
)

class QQChan:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.group = None
        self.member = None
    def SetId(self, group, member):
        self.group = group
        self.member = member
    def GetType(self):
        if self.group is None and self.member is None:
            return None
        elif self.group is None and self.member is not None:
            return 'friend'
        elif self.group is not None and self.member is None:
            return 'group'
        else:
            return 'temp'

GretellChan = QQChan()
CheibriadosChan = QQChan()

@bcc.receiver("GroupMessage")
async def group_message_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    #print(message.asDisplay())
    global GretellChan
    global CheibriadosChan
    if message.asDisplay()[0] in ['!','.','=','&','?','^']:
        #yield from client.send_message(message.channel, '%s wants his !lg' % nick)
        #yield irc_client.message('##kramell', '%s used !lg in discord channel %s' % (nick, message.channel))
        # '!RELAY -n 1 -channel ' + (pm ? 'msg' : chan) + ' -nick ' + nick + ' -prefix ' + chan + ':' + ' ' + message
        forsequell = '!RELAY -n 1 -channel msg -nick %s -prefix group:%s:%s: %s' % (member.id, group.id, member.id, message.asDisplay())
        #print(forsequell)
        await ircClient.message('Sequell', forsequell)
    
    if message.asDisplay().startswith('@?'):
        await GretellChan.lock.acquire()
        GretellChan.SetId(group.id, None)
        await ircClient.message('Gretell', message.asDisplay())
        await asyncio.sleep(10)
        if GretellChan.lock.locked():
            GretellChan.lock.release()
    
    if message.asDisplay().startswith('%'):
        await CheibriadosChan.lock.acquire()
        CheibriadosChan.SetId(group.id, None)
        await ircClient.message('Cheibriados', message.asDisplay())
        await asyncio.sleep(10)
        if CheibriadosChan.lock.locked():
            CheibriadosChan.lock.release()

@bcc.receiver("TempMessage")
async def temp_message_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    global GretellChan
    global CheibriadosChan
    if message.asDisplay()[0] in ['!','.','=','&','?','^']:
        forsequell = '!RELAY -n 1 -channel msg -nick %s -prefix temp:%s:%s: %s' % (member.id, group.id, member.id, message.asDisplay())
        await ircClient.message('Sequell', forsequell)
    
    if message.asDisplay().startswith('@?'):
        await GretellChan.lock.acquire()
        GretellChan.SetId(group.id, member.id)
        await ircClient.message('Gretell', message.asDisplay())
        await asyncio.sleep(10)
        if GretellChan.lock.locked():
            GretellChan.lock.release()
    
    if message.asDisplay().startswith('%'):
        await CheibriadosChan.lock.acquire()
        CheibriadosChan.SetId(group.id, member.id)
        await ircClient.message('Cheibriados', message.asDisplay())
        await asyncio.sleep(10)
        if CheibriadosChan.lock.locked():
            CheibriadosChan.lock.release()

@bcc.receiver("NewFriendRequestEvent")
async def new_friend_request_handler(event: NewFriendRequestEvent):
    if event.sourceGroup is not None:
        if event.sourceGroup == 145375663:
            await event.accept()
            return
    memberList = await qqClient.memberList(145375663)
    for member in memberList:
        if event.supplicant == member.id:
            await event.accept()
            return
    await event.reject()

@bcc.receiver("FriendMessage")
async def friend_message_handler(app: GraiaMiraiApplication, message: MessageChain, sender: Friend):
    global GretellChan
    global CheibriadosChan
    if message.asDisplay()[0] in ['!','.','=','&','?','^']:
        forsequell = '!RELAY -n 1 -channel msg -nick %s -prefix friend::%s: %s' % (sender.id, sender.id, message.asDisplay())
        await ircClient.message('Sequell', forsequell)
    
    if message.asDisplay().startswith('@?'):
        await GretellChan.lock.acquire()
        GretellChan.SetId(None, sender.id)
        await ircClient.message('Gretell', message.asDisplay())
        await asyncio.sleep(10)
        if GretellChan.lock.locked():
            GretellChan.lock.release()
    
    if message.asDisplay().startswith('%'):
        await CheibriadosChan.lock.acquire()
        CheibriadosChan.SetId(None, sender.id)
        await ircClient.message('Cheibriados', message.asDisplay())
        await asyncio.sleep(10)
        if CheibriadosChan.lock.locked():
            CheibriadosChan.lock.release()

import pydle
import re
import traceback
import sys

clrstrip = re.compile("\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)

class MyIrcClient(pydle.Client):
    global GretellChan
    global CheibriadosChan
    async def on_message(self, target, source, message):
        try:
            print(message.encode('utf-8'))
            await super().on_message(target, source, message)
            
            message = clrstrip.sub('', message)
            
            if source=='Sequell':
                msgarray = message.split(':')
                serv = msgarray[0]
                group = msgarray[1]
                member = msgarray[2]
                msg = ':'.join(msgarray[3:])
                
                url_regex = '(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
                msg_split = re.split(url_regex, msg)
                
                msg = ''.join(msg_split)
                
                if msg[:3]=='/me':
                    msg = '*'+msg[3:].strip()+'*'
                
                if re.search('\[\d\d?/\d\d?\]:', msg):
                    s = re.split('(\[\d\d?/\d\d?\]:)', msg)
                    msg = s[0] + s[1] + '\n' + ''.join(s[2:]).strip()
                
                response = [Plain(msg)]
                img_url_regex = '(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\.(?:jpg|png|gif))'
                for url in re.findall(img_url_regex, msg):
                    response.append(Image.fromNetworkAddress(url=url))
                        
                if serv == 'group':
                    await qqClient.sendGroupMessage(group, MessageChain.create(response))
                elif serv == 'temp':
                    await qqClient.sendTempMessage(group, member, MessageChain.create(response))
                elif serv == 'friend':
                    await qqClient.sendFriendMessage(member, MessageChain.create(response))

            chan = None
            if source == 'Gretell':
                chan = GretellChan
            if source == 'Cheibriados':
                chan = CheibriadosChan

            if chan is not None:
                if chan.lock.locked():
                    if chan.GetType() == 'group':
                        await qqClient.sendGroupMessage(chan.group, MessageChain.create([Plain(message)]))
                    elif chan.GetType() == 'friend':
                        await qqClient.sendFriendMessage(chan.member, MessageChain.create([Plain(message)]))
                    elif chan.GetType() == 'temp':
                        await qqClient.sendTempMessage(chan.group, chan.member, MessageChain.create([Plain(message)]))
                    if chan.lock.locked():
                        chan.lock.release()


        except Exception:
            print("Exception irc thread:")
            traceback.print_exc(file=sys.stdout)


ircClient = MyIrcClient('CrawlQQ')
asyncio.ensure_future(ircClient.connect('chat.freenode.net', tls=True), loop=loop)
qqClient.launch_blocking()
