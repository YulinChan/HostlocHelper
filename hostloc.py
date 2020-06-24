#!/bin/python3
import random
import time

import requests
from bs4 import BeautifulSoup


class Hostloc:
    def __init__(self, name, passwd):
        self.log = open('hostloc.log', 'a', encoding='utf-8')
        self.name = name
        self.passwd = passwd
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61',
            'referer': 'https://www.hostloc.com/forum.php', 'origin': 'https://www.hostloc.com'}
        self.data = {'fastloginfield': 'username',
                     'username': name,
                     'password': passwd,
                     'quickforward': 'yes',
                     'handlekey': 'ls'}
        self.params = {'mod': 'logging',
                       'action': 'login',
                       'loginsubmit': 'yes',
                       'infloat': 'yes',
                       'lssubmit': 'yes',
                       'inajax': 1}
        self.session = requests.session()
        login = self.session.post('https://www.hostloc.com/member.php', headers=self.headers, params=self.params,
                                  data=self.data)
        self.log.write(self.time() + f'{self.name}登录成功!\n')
        print(self.time() + f'{self.name}登录成功!')

    def checkStatus(self):
        r = self.session.get('https://www.hostloc.com/home.php?mod=spacecp')
        soup = BeautifulSoup(r.text, 'lxml')
        print(soup.title)

    def visitOthers(self):
        uid = random.randint(1, 48385)
        visit = self.session.get(f'https://www.hostloc.com/space-uid-{uid}.html', headers=self.headers)
        self.log.write(self.time() + f'已访问uid为{uid}的用户\n')
        print(self.time() + f'已访问uid为{uid}的用户')

    def getTids(self, page=100):
        tidList = []
        r = self.session.get(f'https://www.hostloc.com/forum.php?mod=forumdisplay&fid=45&page={page}',
                             headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        listId = soup.find('table', id="threadlisttableid").find_all('tbody')
        for i in listId:
            t = i['id'].split('_')[-1]
            if t.isdigit():
                tidList.append(t)
        return tidList

    def comment(self, tid):
        url = f'https://www.hostloc.com/thread-{tid}-1-1.html'  # 帖子id,楼层,页码
        r = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        formhash = soup.find('input', {'name': 'formhash'})['value']
        params = {'mod': 'post',
                  'action': 'reply',
                  'fid': '45',
                  'tid': tid,
                  'extra': 'page=1',
                  'replysubmit': 'yes',
                  'infloat': 'yes',
                  'handlekey': 'fastpost',
                  'inajax': '1'}
        messageList = ['wow发现好贴，我反手就是一个顶！',
                       '这帖子不错呢，我小小白赶紧先顶一个再学习',
                       '这么好的帖子，我小小白偷偷看完不顶说不过去啊',
                       '坛子里难得一见的好贴子，大写的赞！',
                       '久违的好帖子了，赶紧赞一个！',
                       '小小白飘过，听说看了贴然后回复，就可以得到一个积分，所以我看完帖子总是不忘评论一下的',
                       '每天来坛子里逛一逛，看一看帖子，学习一下经验，顺便评论一下',
                       '坛子新人儿前来围观，向大佬们学习经验了',
                       '来了来了，看帖子学习vps知识，是我每天必做的功课，今天我也来学习了，学完总不忘留个痕迹',
                       '每天来坛子逛一逛，看看大佬们发的帖子，收获颇多']
        data = {'message': random.choice(messageList),
                'formhash': formhash,
                'usesig': '1',
                'subject': ''}
        p = self.session.post(url, params=params, data=data, headers=self.headers)
        self.log.write(self.time() + p.text + '\n')
        print(self.time() + p.text)

    # 投票项目太少，没有必要
    def poll(self):
        pollList = []
        r = self.session.get('https://www.hostloc.com/misc.php?mod=ranklist&type=poll&view=heats&orderby=all',
                             headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        pollLink = soup.find('ul', class_="el pll").find_all('h4')
        for i in pollLink:
            pollList.append('https://www.hostloc.com/' + i.a['href'])
        return pollList

    def time(self):
        strftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return strftime

    def __del__(self):
        self.log.close()


if __name__ == '__main__':
    me = Hostloc('账号', '密码')
    me.visitOthers()
    for i in range(20):
        me.visitOthers()
        time.sleep(5)  # 休息5s,以防触发ddcc防护机制

    # 不建议使用水贴功能，容易被封号
    # for i in me.getTids():
    #     me.comment(i)
    #     time.sleep(60)  # 发言间隔60s
