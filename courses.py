import requests
import execjs
import json
import base64
import ddddocr

class LoginFailed(Exception):
    pass

class Courses:
    def __init__(self,username:str = '',password:str = '') -> None:
        self.username = username
        self.password = password
        self.base_url = 'https://xk.nju.edu.cn/xsxkapp'
        self.headers = {
        'User=Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
        }

    # 加密密码
    def DES(self) -> str:
        with open('des.min.js') as f:
            js = f.read()
        ctx = execjs.compile(js)
        password = ctx.call('strEnc',self.password,'this','password','is')
        password = password.encode()
        password_encrypted = base64.b64encode(password)
        return password_encrypted

    # 登录
    def login(self) -> bool:
        self.get_vcode()
        login_name = self.username
        login_pwd = self.DES()
        vcode = self.vcode
        vtoken = self.vtoken
        payload = {
            'loginName':login_name,
            'loginPwd':login_pwd,
            'verifyCode':vcode,
            'vtoken':vtoken
        }
        url = self.base_url + '/sys/xsxkapp/student/check/login.do'
        res = requests.post(url,headers=self.headers,data=payload)
        data = json.loads(res.text)['data']
        if data:
            login_token = data['token']
            self.login_token = login_token
            self.login_cookies = requests.utils.dict_from_cookiejar(res.cookies)
            return True
        else:
            raise LoginFailed('Login FAILED!!Please try again.')
    
    # 获取学生信息
    def get_student_info(self) -> dict:
        url = self.base_url + '/sys/xsxkapp/student/' + self.username + '.do'
        payload = {
            'token':self.login_token,
            'language':'zh_cn'
        }
        res = requests.post(url,cookies=self.login_cookies,headers=payload)
        self.student_info = json.loads(res.text)['data']
        self.elective_batch_code = self.student_info['electiveBatchList'][-1]['code']
        self.major = self.student_info['major']
        self.grade = self.student_info['grade']
        return self.student_info

    # 获取课表
    def get_courses(self) -> list:
        headers = {
            'token':self.login_token,
            'language':'zh_cn'
        }
        query = {"data":
                    {"studentCode":self.username,
                     "electiveBatchCode":self.elective_batch_code,
                     "teachingClassType":"ZY",
                     "queryContent":"ZXZY:"+self.major+",ZXNJ:"+self.grade+","
                    },
                 "pageSize":"10",
                 "pageNumber":"0",
                 "order":"isChoose -"
                }
        data = {
            'querySetting':str(query)
        }
        url = self.base_url+'/sys/xsxkapp/elective/programCourse.do'
        res = requests.post(url,cookies=self.login_cookies,data=data,headers=headers)  
        self.courses = json.loads(res.text)['dataList']
        return self.courses

    def get_token(self) -> str:
        url  =self.base_url + '/sys/xsxkapp/student/4/vcode.do'
        res = requests.post(url,headers=self.headers,allow_redirects=False)
        data = json.loads(res.text)['data']
        token = data['token']
        self.token = token
        return token
    
    def get_vtoken(self) -> str:
        vtoken = self.get_token()
        self.vtoken = vtoken
        return vtoken

    def get_vcode(self) -> str:      
        ocr = ddddocr.DdddOcr()
        self.get_vtoken()
        url = self.base_url + '/sys/xsxkapp/student/vcode/image.do?vtoken=' + self.vtoken
        res = requests.get(url)
        vcode = ocr.classification(res.content)
        self.vcode = vcode
        return vcode