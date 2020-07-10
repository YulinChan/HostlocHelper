import time
import random

import requests
from bs4 import BeautifulSoup


class Hostloc:
    def __init__(self, name, passwd):
        self.log = open('hostloc.log', 'a', encoding='utf-8')
        self.name = name
        self.passwd = passwd
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
                        'referer': 'https://www.hostloc.com/forum.php',
                        'origin': 'https://www.hostloc.com',
                        'Host': 'www.hostloc.com'}
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

    def checkStatus(self):
        r = self.session.get('https://www.hostloc.com/home.php?mod=spacecp')
        soup = BeautifulSoup(r.text, 'lxml')
        # print(soup.title.text)
        if soup.title.text == '个人资料 -  全球主机交流论坛 -  Powered by Discuz!':
            self.log.write(self.time() + f'{self.name}登录成功!\n')
            print(self.time() + f'  {self.name}登录成功!')
        else:
            self.log.write(self.time() + f'{self.name}登录失败!\n')
            print(self.time() + f'{self.name}登录失败!')

    def visitOthers(self):
        uid = random.randint(1, 48385)
        visit = self.session.get(f'https://www.hostloc.com/space-uid-{uid}.html', headers=self.headers)
        self.log.write(self.time() + f'已访问uid为{uid}的用户\n')
        print(self.time() + f'已访问uid为{uid}的用户')

    # 获取帖子id（tid）
    def getTids(self, page=1):
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


    def comment(self, tid, msg):
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

        data = {'message': msg,
                'formhash': formhash,
                'usesig': '1',
                'subject': ''}
        p = self.session.post(url, params=params, data=data, headers=self.headers)
        self.log.write(self.time() + p.text + '\n')
        print(self.time() + p.text)

    def time(self):
        strftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return strftime

    def __del__(self):
        self.log.close()


if __name__ == '__main__':
    me = Hostloc('name', 'passwd')
    # me.checkStatus()
    # me.visitOthers()
    for i in range(20):
        me.visitOthers()
        # 以防触发ddcc防护机制
        time.sleep(random.randrange(5, 10))


