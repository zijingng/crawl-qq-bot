import asyncio

from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain, Image
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

qqGroup = None
qqId = None

@bcc.receiver("GroupMessage")
async def group_message_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    #print(message.asDisplay())
    global qqGroup
    if message.asDisplay()[0] in ['!','.','=','&','?','^']:
        #yield from client.send_message(message.channel, '%s wants his !lg' % nick)
        #yield irc_client.message('##kramell', '%s used !lg in discord channel %s' % (nick, message.channel))
        # '!RELAY -n 1 -channel ' + (pm ? 'msg' : chan) + ' -nick ' + nick + ' -prefix ' + chan + ':' + ' ' + message
        forsequell = '!RELAY -n 1 -channel msg -nick %s -prefix group:%s:%s: %s' % (member.id, group.id, member.id, message.asDisplay())
        #print(forsequell)
        await ircClient.message('Sequell', forsequell)
    
    if message.asDisplay().startswith('@?'):
        qqGroup = group
        qqId = None
        await ircClient.message('Gretell', message.asDisplay())
    
    if message.asDisplay().startswith('%'):
        qqGroup = group
        qqId = None
        await ircClient.message('Cheibriados', message.asDisplay())

@bcc.receiver("TempMessage")
async def group_message_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    global qqGroup
    global qqId
    if message.asDisplay()[0] in ['!','.','=','&','?','^']:
        forsequell = '!RELAY -n 1 -channel msg -nick %s -prefix temp:%s:%s: %s' % (member.id, group.id, member.id, message.asDisplay())
        await ircClient.message('Sequell', forsequell)
    
    if message.asDisplay().startswith('@?'):
        qqGroup = group
        qqId = member.id
        await ircClient.message('Gretell', message.asDisplay())
    
    if message.asDisplay().startswith('%'):
        qqGroup = group
        qqId = member.id
        await ircClient.message('Cheibriados', message.asDisplay())

import pydle
import re
import traceback
import sys

clrstrip = re.compile("\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)

class MyIrcClient(pydle.Client):
    async def on_message(self, target, source, message):
        global qqGroup
        global qqId
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
                #msg_urls = re.findall(url_regex, msg)
                msg_split = re.split(url_regex, msg)
                
                for mdchar in ['\\','*','_','~','`']:
                    for i in range(0,len(msg_split),2):
                        msg_split[i] = msg_split[i].replace(mdchar,'\\'+mdchar)
                    #msg_wo_ulrs = msg_wo_ulrs.replace(mdchar,'\\'+mdchar)
                
                #msg = msg_wo_ulrs.format(*msg_urls)
                msg = ''.join(msg_split)
                
                if msg[:3]=='/me':
                    msg = '*'+msg[3:].strip()+'*'
                #msg = msg.replace('/me','*'+client.user.name+'*')
                
                if re.search('\[\d\d?/\d\d?\]:', msg):
                    s = re.split('(\[\d\d?/\d\d?\]:)', msg)
                    #msg = s[0] + s[1] + '```\n' + ''.join(s[2:]).strip() + '\n```' # put only the content of the ?? in a block
                    msg = s[0] + s[1] + '\n' + ''.join(s[2:]).strip()
                else:
                    #msg = '```\n' + msg + '\n```' # put in a code block to preserve formatting
                    msg = msg
                
                response = [Plain(msg)]
                img_url_regex = '(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\.(?:jpg|png|gif))'
                for url in re.findall(img_url_regex, msg):
                    response.append(Image.fromNetworkAddress(url=url))
                        
                if serv == 'group':
                    await qqClient.sendGroupMessage(group, MessageChain.create(response))
                elif serv == 'temp':
                    await qqClient.sendTempMessage(group, member, MessageChain.create(response))
            if source=='Gretell':
                if qqId is None:
                    await qqClient.sendGroupMessage(qqGroup, MessageChain.create([Plain(message)]))
                else:
                    await qqClient.sendTempMessage(qqGroup, qqId, MessageChain.create([Plain(message)]))

            if source=='Cheibriados':
                if qqId is None:
                    await qqClient.sendGroupMessage(qqGroup, MessageChain.create([Plain(message)]))
                else:
                    await qqClient.sendTempMessage(qqGroup, qqId, MessageChain.create([Plain(message)]))

        except Exception:
            print("Exception irc thread:")
            traceback.print_exc(file=sys.stdout)


ircClient = MyIrcClient('CrawlQQ')
asyncio.ensure_future(ircClient.connect('chat.freenode.net', tls=True), loop=loop)
qqClient.launch_blocking()
