#coding:utf-8
import sys 
reload(sys)
sys.setdefaultencoding('utf-8')



import sys
import urllib2
import time
import json
import requests

from Public.public import GetWechatSecret,GetWechatID,GetWechatCorp



class Token(object):
    def __init__(self, corpid, corpsecret):
        self.baseurl = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}'.format(corpid, corpsecret)
        self.expire_time = sys.maxint

    def get_token(self):
        if self.expire_time > time.time():
            request = urllib2.Request(self.baseurl)
            response = urllib2.urlopen(request)
            ret = response.read().strip()
            ret = json.loads(ret)
            if 'errcode' in ret.keys():
                print >> ret['errmsg'], sys.stderr
                sys.exit(1)
            self.expire_time = time.time() + ret['expires_in']
            self.access_token = ret['access_token']
            print self.access_token
        return self.access_token

def send_msg(userid,title, content):
    if GetWechatCorp() and GetWechatSecret() and GetWechatID():
        corpid = GetWechatCorp()
        corpsecret = GetWechatSecret()
        qs_token = Token(corpid=corpid, corpsecret= corpsecret).get_token()
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}".format(qs_token)
        payload = {
            "touser": userid,
            "msgtype": "text",
            "agentid": GetWechatID(),
            "text": {
                "content": "标题:\n{0}\n内容:\n{1}".format(title, content)
            },
            "safe": "0"
        }
        ret = requests.post(url, data=json.dumps(payload,ensure_ascii=False))
    
    
def send_news_message(to_user,title, content, picurl="", alert_url=""):
    if GetWechatCorp() and GetWechatSecret() and GetWechatID():
        corpid = GetWechatCorp()
        corpsecret = GetWechatSecret()
        qs_token = Token(corpid=corpid, corpsecret= corpsecret).get_token()
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}".format(qs_token)
        payload = {
            "touser": "%s" % to_user,
            "msgtype": "news",
            "agentid": GetWechatID(),
            "news": {
                "articles": [
                    {
                        "title": title,
                        "description": content,
                        "url": alert_url.encode('utf-8'),
                        "picurl": picurl.encode('utf-8'),
                    },
                ],
            },
            "safe": "0"
        }
        ret = requests.post(url, data=json.dumps(payload,ensure_ascii=False).encode('utf-8'))

if __name__ == "__main__":
    '''
    userid = sys.argv[1]
    title = sys.argv[2]
    content = sys.argv[3]
    send_msg(userid, title, content)
    '''
    send_news_message("18321628933", '新虚拟机申请', '标题:<br>新虚拟机申请<br>内容:<br>资源位置：测试环境 <br>申请用户：mianbao <br>使用模板：C <br>申请数量 1 台')