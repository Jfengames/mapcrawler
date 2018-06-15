HOST = ''
PORT = 3306
USER = ''
PASSWD =  ''
DB = ''
CHARSET = 'utf8'

ADSL_SERVER_URL = ''
ADSL_SERVER_AUTH = ('','')

KEYS = ['',
        '',
        '',
        ]


MAIL_NOTIFY = True
if MAIL_NOTIFY:
        # 推荐发送使用139邮箱，测试可用
        MAIL_CONFIG = {"fromaddr": "xxxx@139.com",
                      "to": "XX@xx.com",
                      "passwd": "", #密码
                      "server": "smtp.139.com"}