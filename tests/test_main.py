#!/usr/bin/env python3
import subprocess
import os, sys
from os import path
import socket
import time


subprocess.check_call(["cp", '-r',  '../src/', './'])
subprocess.check_call(["cp",  '../CLI/ADES', './'])
os.system('mv ./src/* ./')
subprocess.check_call(["rm","-rf", './src/'])
subprocess.check_call(["pip", "install",'-r', './requirements.txt'])
os.system('nohup python3 -m http.server 9000 &')
os.system('nohup python3 main.py &')


time.sleep(10)
if path.exists('1'):
    os.system('rm -rf 1 2 3 4')

def get_ticket():
    ip=subprocess.check_output(['hostname','-i']).strip().decode()+':5566'
    if not path.exists('1'):
        f = open("1", "w+")
        process=subprocess.Popen(['../CLI/request-resource.sh', '-s', ip,'-r','/pep/ADES'], stderr = f)
        time.sleep(5)
    f.flush()
    with open('1','r+') as m:
        for i in m:
            a =''.join(i)
            if 'ticket' in a:
            
                ticket = a[a.find('ticket')+7:-1]
    f.close()
    return ticket
        
def get_id_token():
    if not path.exists('2'):
        r = open("2", "w+")
        pro=subprocess.Popen(['../CLI/authenticate-user.sh', '-S', '-a', 'demoexample.gluu.org','-i','a297e2ca-0f18-4740-a36e-7058f169a81b','-p','VtVukKiRvzf2a1coAKf72hPVg0iUypzKZfYZ5Z1A','-s','openid', '-u', 'alvlDemo', '-w', 'alvl', '-r', 'none'], stdout = r)
        time.sleep(2)
    r.flush()
    r.close()
    id_token = ''
    with open('2','r+') as m:
        for i in m:
            a =''.join(i)
            if 'id_token' in a:
                
                id_token = a[a.find('id_token')+11:a.find('token_type')-3]
    return id_token

def get_acces_token(ticket, id_token):
    if not path.exists('3'):
        r = open("3", "w+")
        pro=subprocess.Popen(['../CLI/get-rpt.sh', '-S', '-a', 'demoexample.gluu.org','-t',ticket,'-i','a297e2ca-0f18-4740-a36e-7058f169a81b','-p','VtVukKiRvzf2a1coAKf72hPVg0iUypzKZfYZ5Z1A','-s','openid','-c', id_token], stdout = r)
        time.sleep(2)
    r.flush()
    r.close()
    access_token = ''
    with open('3','r+') as m:
        for i in m:
            a =''.join(i)
            if 'access_token' in a:
                access_token = a[a.find('access_token')+15:a.find('token_type')-3]
    return access_token

def get_resource(access_token):
    
    ip=subprocess.check_output(['hostname','-i']).strip().decode()+':5566'
    o = open("4", "w+")
    process=subprocess.Popen(['../CLI/request-resource.sh', '-s', ip,'-r','/pep/ADES', '-t', access_token], stdout = o)
    time.sleep(5)
    o.close()

    with open('4','r+') as m:
        for i in m:
            a =''.join(i)
            if 'TestPEP' in a:
                return a
        
            

def main():
    if not path.exists('1'):
        t=get_ticket()
        i=get_id_token()
        print('t: ')
        print(t)
        print('i: ')
        print(i)
        a=get_acces_token(t, i)
        print('a: ')
        print(a)
        r=get_resource(a)
        print('r: ')
        print(r)
        if r:
            print('Success')
            os.system('rm -rf 1 2 3 4')
            os.system('rm -rf ADES config config.py custom_oidc.py custom_uma.py main.py nohup.out requirements.txt __pycache__')

 
main()





