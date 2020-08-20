#!/usr/bin/python3
import os
import random
import re
import time

import requests
from bs4 import BeautifulSoup


class Hostloc:
    def __init__(self, name, passwd):
        self.log = open('./hostloc.log', 'a', encoding='utf-8')
        if not os.path.exists('./post-list.txt'):
            os.system("touch ./post-list.txt")
        self.name = name
        self.passwd = passwd
        # 一关键词对多答案，再随机给出答案，防止被识破
        self.reply_dict = {}
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
        r = self.session.get('https://www.hostloc.com/home.php?mod=spacecp', headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
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

    # 获取帖子标题及链接
    def getPost(self, url):
        # 帖子标题及链接暂存字典
        p_list = {}
        # 这个按发帖时间排序的链接与默认的不同。获取到帖子链接形式也不同
        r = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        post_list = soup.find('table', id="threadlisttableid").find_all('tbody', id=re.compile(r"normalthread_\d+"))
        f = open('./post-list.txt', 'r')
        # 若用readlines默认会把'\n'读入，但splitlines产生的列表无序
        existed_post = f.read().splitlines()
        f.close()
        f = open('./post-list.txt', 'a')
        for i in post_list:
            title = i.tr.th.find('a', class_="s xst").text
            link = 'https://www.hostloc.com/' + i.tr.th.find('a', class_="s xst")['href']
            if link not in existed_post:
                f.write(link + '\n')
                p_list[title] = link
                self.log.write(self.time() + '   ' + title)
                print(self.time() + '   ' + title)
        f.close()
        return p_list

    def reply(self, url, msg):
        # gruop(1)返回第一组，0或不填则返回整个匹配字符串
        tid = re.search('tid=(\d+)', url).group(1)
        r = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        title = soup.h1.text
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
        self.log.write(self.time() + title + '<---' + msg + '\n')
        print(self.time() + title + '<---' + msg)

    # f用于指定评论的楼层，默认为1楼
    def comment(self, url, msg, f=1):
        # 帖子id
        # gruop(1)返回第一组，0或不填则返回整个匹配字符串
        tid = re.search('tid=(\d+)', url).group(1)
        r = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        title = soup.h1.text
        formhash = soup.find('input', {'name': 'formhash'})['value']
        # pid是post id，可在页面源码找到
        pid = soup.find('div', id="postlist").find_all('div', id=re.compile(r"post_\d+"))[f]['id'].split('_')[-1]
        pmsg = soup.find('div', id="postlist").find_all('div', id=re.compile(r"post_\d+"))[f].text.replace('\n', '')
        params = {'mod': 'post',
                  'action': 'reply',
                  'comment': 'yes',
                  'tid': tid,
                  'pid': pid,
                  'extra': 'page=1',
                  'page': '1',
                  'commentsubmit': 'yes',
                  'infloat': 'yes',
                  'inajax': '1'}

        data = {'message': msg,
                'formhash': formhash,
                'handlekey': 'comment'}
        p = self.session.post(url, params=params, data=data, headers=self.headers)
        self.log.write(self.time() + title + '\n' + pmsg + '<---' + msg + '\n')
        print(self.time() + title + '\n' + pmsg + '<---' + msg)

    def votepoll(self, url):
        tid = re.search('tid=(\d+)', url).group(1)
        r = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        title = soup.h1.text
        formhash = soup.find('input', {'name': 'formhash'})['value']
        answer = soup.find('table', {'summary': "poll panel"}).find('td', {'class': "pslt"}).input['value']

        post_params = {'mod': 'post',
                       'action': 'reply',
                       'fid': '45',
                       'tid': tid,
                       'extra': 'page=1',
                       'replysubmit': 'yes',
                       'infloat': 'yes',
                       'handlekey': 'fastpost',
                       'inajax': '1'}
        msg = random.choice(('mjj通道 szbd', 'mjj专属豪华通道:lol', 'mjj专属通道yc007t', '最后一个默认mjj通道yc010t'))
        post_data = {'message': msg,
                     'formhash': formhash,
                     'usesig': '1',
                     'subject': ''}

        params = {'mod': 'misc',
                  'action': 'votepoll',
                  'fid': '45',
                  'tid': tid,
                  'pollsubmit': 'yes',
                  'quickforward': 'yes',
                  'inajax': '1'}

        data = {'formhash': formhash,
                'pollanswers[]': answer}
        v = self.session.post(url, params=params, data=data, headers=self.headers)
        p = self.session.post(url, params=post_params, data=post_data, headers=self.headers)
        self.log.write(self.time() + title + '   已投票且评论\n')
        print(self.time() + title + '   已投票且评论')

    def time(self):
        strftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return strftime

    def clean(self):
        self.post_list = {}
        self.vote_list = {}
        self.log.write(self.time() + '  列表信息清除完毕！\n')
        # 关了日志再打开是为了及时把消息及时写入文件中
        self.log.close()
        self.log = open('./hostloc.log', 'a', encoding='utf-8')
        print(self.time() + ' 列表信息清除完毕！\n')

    def __del__(self):
        self.log.close()


if __name__ == '__main__':
    me = Hostloc('你的账号', '你的密码')
    # 自定义回复字典，请自行更改
    me.reply_dict = {'明盘出': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd')}
    me.checkStatus()
    # 单次运行
    me.post_list = me.getPost(
        'https://www.hostloc.com/forum.php?mod=forumdisplay&fid=45&filter=author&orderby=dateline')
    me.vote_list = me.getPost(
        'https://www.hostloc.com/forum.php?mod=forumdisplay&fid=45&filter=author&orderby=dateline&specialtype=poll')

    for vote in me.vote_list.values():
        me.votepoll(vote)
        time.sleep(random.randrange(60, 120))

    for i in me.post_list:
        for j in me.reply_dict:
            if j in i:
                me.reply(me.post_list[i], random.choice(me.reply_dict[j]))
                time.sleep(random.randrange(60, 120))
                # 一个帖子只回复一个关键词
                break

    # 持续运行
    while 0:
        me.post_list = me.getPost(
            'https://www.hostloc.com/forum.php?mod=forumdisplay&fid=45&filter=author&orderby=dateline')
        me.vote_list = me.getPost(
            'https://www.hostloc.com/forum.php?mod=forumdisplay&fid=45&filter=author&orderby=dateline&specialtype=poll')

        for vote in me.vote_list.values():
            me.votepoll(vote)
            time.sleep(random.randrange(60, 120))

        for i in me.post_list:
            for j in me.reply_dict:
                if j in i:
                    me.reply(me.post_list[i], me.reply_dict[j])
                    time.sleep(random.randrange(60, 120))
        me.clean()
        time.sleep(random.randrange(60, 120))
