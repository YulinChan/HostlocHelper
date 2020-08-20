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
        if not os.path.exists('./post-list.txt'):
            os.system("touch ./post-list.txt")
        f = open('./post-list.txt', 'r')
        # 若用readlines默认会把'\n'读入，但splitlines产生的列表无序
        existed_post = f.read().splitlines()
        f.close()
        f = open('./post-list.txt', 'a')
        for i in post_list:
            # 用find会出错，原因未知（no attribute）
            title = i.tr.th.find('a', class_="s xst").text
            link = 'https://www.hostloc.com/' + i.tr.th.find('a', class_="s xst")['href']
            if link not in existed_post:
                f.write(link + '\n')
                p_list[title] = link
                self.log.write(self.time() + '   ' + title)
                print(self.time() + '   ' + title)

        return p_list

    def reply(self, url, msg):
        # 帖子id
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


if __name__ == '__main__':
    me = Hostloc('你的账号', '你的密码')
    # 自定义回复字典，请自行更改
    me.reply_dict = {
        '明盘出': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd', '帮顶，lz早出', '顶就完事儿，楼主早出', '1,2,3 我顶，楼主早出'),
        '溢价出': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd', '帮顶，lz早出', '顶就完事儿，楼主早出', '1,2,3 我顶，楼主早出'),
        '明盘收': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '溢价收': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '【出】': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd', '帮顶，lz早出 szbd', '顶就完事儿，楼主早出', '1,2,3 我顶，祝楼主早出'),
        '出个': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd', '帮顶，lz早出 szbd', '顶就完事儿，楼主早出', '1,2,3 我顶，祝楼主早出'),
        '出台': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd', '帮顶，lz早出 szbd', '顶就完事儿，楼主早出', '1,2,3 我顶，祝楼主早出'),
        '出一个': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd', '帮顶，lz早出 szbd', '顶就完事儿，楼主早出', '1,2,3 我顶，祝楼主早出'),
        '出几个': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd', '帮顶，lz早出 szbd', '顶就完事儿，楼主早出', '1,2,3 我顶，祝楼主早出'),
        '出几台': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd', '帮顶，lz早出 szbd', '顶就完事儿，楼主早出', '1,2,3 我顶，祝楼主早出'),
        '出一台': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd', '帮顶，lz早出 szbd', '顶就完事儿，楼主早出', '1,2,3 我顶，祝楼主早出'),
        '出几只': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd', '帮顶，lz早出 szbd', '顶就完事儿，楼主早出', '1,2,3 我顶，祝楼主早出'),
        '出一只': ('帮顶，祝楼主早出 紫薯布丁', '绑定，祝早出 zsbd', '帮顶，lz早出 szbd', '顶就完事儿，楼主早出', '1,2,3 我顶，祝楼主早出'),
        '【收】': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '收个': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '收只': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '收台': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '收一个': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '收几个': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '收一台': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '收几台': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '收几只': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '收一只': ('帮顶，祝楼主早收 zsbd', '绑定，祝早收 zsbd', '帮顶，lz早收啊', '顶就完事儿，祝楼主早收', '1,2,3 我顶，楼主早收'),
        '震惊': ('射射，有被震jing到:lol', '全球UC震惊论坛yc010t', 'wow真的好震惊耶yc010t', '好活，6ml全震出来了:lol', 'mjj日常震惊yc010t'),
        '咋用': ('wow我也不会,楼下回答:lol', '遇事不慌，Google一下你就知道:lol', '有问题就来loc就对了，这里能人多', '帮顶，召唤万能的mjj'),
        '求助': ('帮顶，坐等大佬解决:lol', '万能的mjj们正在赶来', 'emmm，楼下回答:lol', '帮顶，一支穿云箭，'),
        '怎么样': ('emm，不太清楚，楼下回答:lol', '这还行吧', '等待经验丰富的mjj回答'),
        '怎么办': ('啊这。。。', '帮顶，坐等大佬解决:lol', '万能的mjj们正在赶来', 'emmm，楼下回答:lol'),
        '为什么': ('谁知道呢，帮顶，坐等楼下回答:lol', '不知道啊，楼下回答', '我也想知道，楼主优先:lol'),
        '是不是': ('应该不是吧 紫薯布丁', '应该是吧 szbd', '不知道啊，楼下回答', '好像不是诶 。', '貌似是的呢 。'),
        '不懂就问': ('问就不懂:lol', '对喽，不懂就问', '万能的Goole，Google一下你就知道:lol', '帮顶，等待热心mjj', 'wo我也想知道'),
        '如何': ('俺也没经验，楼下回答吧:lol', '帮顶，坐等大佬:lol', '万能的mjj们正在赶来', 'emmm，楼下回答:lol'),
        '真香': ('确实 zsbd :lol', '真香警告:lol', '全球真香论坛:lol', '花生瓜子矿泉水，前排占位吃瓜喽:lol'),
        '女票': ('全球女票论坛，前排占位吃瓜:lol', '全球女票论坛 szbd', 'mjj 女票日常', '还是女票的香:lol'),
        '灵车': ('全球灵车论坛，前排占位吃瓜:lol', '全球灵车论坛:lol', '灵车才刺激:lol', '车越灵越刺激'),
        '牛逼': ('全球nb论坛yc010t，前排占位吃瓜:lol', '全球nb论坛yc010t', 'mjj牛逼日常:lol'),
        '骗子': ('全球被骗论坛yc010t', '全球诈骗经验交流中心yc010t', '网络诈骗层出不穷，mjj屡屡上当', '吃一*长一智'),
        '被骗': ('全球被骗论坛yc010t', '全球诈骗经验交流中心yc010t', '网络诈骗层出不穷，mjj屡屡上当', '吃一*长一智'),
        '福利': ('全球福利论坛yc010t', 'mjj日常福利:lol'),
        '翻车': ('全球翻车论坛yc010t', 'mjj日常翻车:lol'),
        '测评': ('全球测评论坛yc010t', 'mjj日常测评:lol'),
        '脚本': ('全球脚本论坛yc010t', 'quan球脚本蕉流论坛:lol', 'mjj日常脚本:lol'),
        'T楼': ('那我就来给mjj们当分母咯:lol', '我来瞅瞅，说不定就中了呢！', '分母越大，mjj中奖几率就越小，我来啦', '中奖绝缘体前来一试'),
        '踢楼': ('那我就来给mjj们当分母咯:lol', '我来瞅瞅，说不定就中了呢！', '分母越大，mjj中奖几率就越小，我来啦', '中奖绝缘体前来一试'),
        '求分享': ('同求，帮顶，楼主优先:lol', '全球资源分享论坛:lol', '我也整一个:lol', '在线坐等热心mjj', '人有我有yc012t'),
        '帮我': ('帮顶，一支穿云箭，千军万马来相见yc007t', '楼主稍等，热心的mjj们正在赶来', '全球互帮互助论坛', '绑定，坐等大佬出山'),
        '大佬们': ('萌新路过，假装大佬:lol', '小萌新不敢回答yc014t', '萌新悄悄路过'),
        '新人报道': ('又多一个mjj:lol\n遂令天下父母心，\n不重生男重生女。\n生女犹得嫁比邻，\n生男长大mjj。', '欢迎欢迎yc013t', '欢迎萌新！')
    }
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
