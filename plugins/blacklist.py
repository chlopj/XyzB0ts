import botsdk.Bot
from botsdk.BotRequest import BotRequest
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.Cookie import getCookie, setCookie
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.Permission import permissionCmp
from botsdk.tool.Permission import GetSystemPermissionAndCheck

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "blacklist"
        self.addFilter(self.blackListCheck)
        self.addTarget("TargetRouter", "TargetRouter", self.blacklist)

    async def blacklist(self, request: BotRequest):
        '''/blacklist [add/remove] qq'''
        data = request.getFirstTextSplit()
        bot = request.getBot()
        groupid = request.getGroupId()
        cookie = request.getCookie("blackList")
        if cookie is None:
            cookie = []
        if "list" in data:
            await request.sendMessage(MessageChain().text(str(cookie)))
            return
        if len(data) < 3:
            await request.sendMessage(MessageChain().text("/blacklist [add/remove] qq"))
            return
        target = data[2]
        try:
            target = str(int(target))
            if target != data[2] or GetSystemPermissionAndCheck(target, "ADMINISTRATOR"):
                raise
        except Exception as e:
                await request.sendMessage(MessageChain().text("???"))
                return 
        groupMemberList = await bot.memberList(groupid)
        groupMemberList = groupMemberList["data"]
        checkFlag = True
        if GetSystemPermissionAndCheck(request.getSenderId(), "ADMINISTRATOR"):
            checkFlag = False
        else:
            for i in groupMemberList:
                if str(i["id"]) == target:
                    i["id"] = str(i["id"])
                    if permissionCmp(request.getPermission(), i["permission"]):
                        checkFlag = False
                    break
        if checkFlag:
            await request.sendMessage(MessageChain().text("权限不足或该qq不在群"))
            return
        if data[1] == "add":
            if target not in cookie:
                cookie.append(target)
        elif data[1] == "remove":
            if target in cookie:
                cookie.remove(target)
        request.setCookie("blackList", cookie)
        await request.sendMessage(MessageChain().text("完成"))

    async def blackListCheck(self, request):
        if request.getType() == "GroupMessage":
            cookie = request.getCookie("blackList")
            if cookie is not None and request.getSenderId() in cookie:
                return False
        return True

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
