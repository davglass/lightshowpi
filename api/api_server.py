#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading
import argparse
import re
import cgi
import json
import os
from time import gmtime, strftime
from status import status as getStatus
import mimetypes
import platform
import sys
import base64
import Cookie
import datetime
import random

config = None
userData = None

def read(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return data

configFile = '/home/pi/.api.json'
if os.path.isfile(configFile):
    config = json.loads(read(configFile))

if config and config['username'] and config['password']:
    userData = base64.b64encode('{:s}:{:s}'.format(config['username'], config['password']))

mimetypes.init()

def writeLog(ip, str):
    cmdLog = open('/var/log/api/commands.log', 'a')
    cmdLog.write("[{:s}] {:s} - {:s}\n".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), ip, str))
    cmdLog.close()


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def version_string(self):
        return 'HackSI LightShow UI'

    def log_message(self, format, *args):
        sys.stdout.write("%s - - [%s] %s %s\n" %
                    (self.address_string(),
                        self.log_date_time_string(),
                        format%args,
                        str(self.headers['user-agent'])))
        sys.stdout.flush()

    def log_message_error(self, format, *args):
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))
        sys.stderr.flush()

    def log_request(self, code='-', size='-'):
        if self.path != '/music.json' and self.path != '/lights/status':
            self.log_message('"%s" %s %s', self.requestline, str(code), str(size))

    def log_error(self, format, *args):
        self.log_message_error(format, *args)

    def json(self, status, data):
        data = json.dumps(data, indent=4, sort_keys=True)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)
        return

    def sendFile(self, name):
        data = read(name)
        cType, encoding = mimetypes.guess_type(name)

        if name.endswith('/index.html'):
            data = data.replace('{{hostname}}', platform.node())
        
        self.send_response(200)
        self.send_header('Content-Type', cType)
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)
        
    def do_HEAD(self):
        if self.checkAuth():
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            return

        self.do_AUTHHEAD()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="HackSI Lights"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def checkAuth(self):
        if not config or not userData:
            self.send_response(200)
            return True

        cookie = Cookie.SimpleCookie()
        cHeader = self.headers.getheader('Cookie')
        if cHeader:
            cookie.load(cHeader)
        
        if cookie and cookie['session'].value == 'logged_in':
            self.send_response(200)
            self.send_header('Cookie', cHeader)
            return True
        if self.headers.getheader('Authorization') == None:
            self.do_AUTHHEAD()
            self.wfile.write('Not Authorized Yet')
            return False
        elif self.headers.getheader('Authorization') == 'Basic ' + userData:
            self.send_response(200)
            expiration = datetime.datetime.now() + datetime.timedelta(days=1)
            cookie['session'] = 'logged_in'
            cookie['session']['path'] = '/'
            cookie['session']['expires'] = expiration.strftime('%a, %d-%b-%Y %H:%M:%S CST')
            self.wfile.write(cookie.output() + '\n')
            return True
        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.getheader('Authorization'))
            self.wfile.write('not authenticated')
            return False

    def do_GET(self):
        
        if not self.checkAuth():
            return

        cmd = False

        fileName = '/home/pi/api/html' + self.path
        if self.path == '/':
            fileName = fileName + '/index.html'

        if os.path.isfile(fileName):
            return self.sendFile(fileName)

        if self.path.startswith('/lights/'):
            if self.path.startswith('status', 8):
                return self.json(200, getStatus())
            elif self.path.startswith('on', 8):
                cmd = '/home/pi/bin/lights_on'
            elif self.path.startswith('off', 8):
                cmd = '/home/pi/bin/lights_off'
            
        if self.path.startswith('/controller/'):
            if self.path.startswith('cylon', 12):
                cmd = '/home/pi/bin/pattern cylon'
            elif self.path.startswith('dance', 12):
                cmd = '/home/pi/bin/pattern dance'
            elif self.path.startswith('flash', 12):
                cmd = '/home/pi/bin/pattern flash'
            elif self.path.startswith('random_pattern', 12):
                cmd = '/home/pi/bin/pattern random_pattern'
        
        if self.path.startswith('/show/'):
            if self.path.startswith('start', 6):
                cmd = '/home/pi/bin/start_lights'
            elif self.path.startswith('stop', 6):
                cmd = '/home/pi/bin/stop_lights'
            elif self.path.startswith('enable', 6):
                cmd = '/home/pi/bin/enable_show'
            elif self.path.startswith('disable', 6):
                cmd = '/home/pi/bin/disable_show'
        
        if cmd:
            writeLog(self.client_address[0], cmd)
            if re.search('/home/pi/bin/', cmd):
                os.system('/home/pi/bin/stop_controller background')
                os.system(cmd)
            data = {
                'ip': self.client_address[0],
                'when': format(strftime("%Y-%m-%d %H:%M:%S", gmtime())),
                'command': cmd
            }
            return self.json(200, data)

        self.send_response(404)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write('404 Not Found')
        return
 
"""
Dont worry about the stuff below this line..
Really, it's just boilerplate cruft
"""

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
 
    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)
 
class SimpleHttpServer():
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler)
 
    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
 
    def waitForThread(self):
        self.server_thread.join()
 
    def stop(self):
        self.server.shutdown()
        self.waitForThread()
 
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('--port', default=8888, type=int, help='Listening port for HTTP Server')
    parser.add_argument('--ip', default='0.0.0.0', help='HTTP Server IP')
    args = parser.parse_args()
 
    server = SimpleHttpServer(args.ip, args.port)
    server.start()
    server.waitForThread()
