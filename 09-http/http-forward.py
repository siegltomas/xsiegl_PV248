#!/usr/bin/env python3

import sys  
import json  
from http.server import BaseHTTPRequestHandler, HTTPServer  
import http  
import socket  
import ssl  
import traceback  

TIME_OUT = "timeout"
JSON_ERROR = "invalid json"
ENCODING = "UTF-8"
CONNECTION_ERROR = "connection failed"

def process_url_address(url_address):    
    del_https = "https://"
    del_http = "http://"

    url_address = url_address.replace(del_https, "")   
    url_address = url_address.replace(del_http, "") 
    url_address_list = url_address.split("/", 1)   
    
    if len(url_address_list) == 0:    
        sys.exit() 
    if len(url_address_list) == 1:    
       return url_address_list[0], "/"
    else: # url_address_list > 1
       return url_address_list[0], ("/" + url_address_list[1])

def process_request(url_address, type_of_request, headers = {}, content = None, timeout = 1):    
    address_name, params = process_url_address(url_address)      
    try: 
       http_connection = None
       if type_of_request == "GET":
          http_connection = http.client.HTTPConnection(address_name, timeout = timeout)            
          http_connection.request(type_of_request, params, headers=headers)   
       elif type_of_request == "POST":
          http_connection = http.client.HTTPConnection(address_name, timeout = timeout)            
          http_connection.request(type_of_request, params, content, headers=headers)   
       return http_connection.getresponse()
    except socket.timeout as e:   #
       return TIME_OUT            #
    except:                       # 
       traceback.print_exc()      #
       return None                #


def get_post_handler(url_address):
    class RequestHandlerHTTP(BaseHTTPRequestHandler):
        def do_GET(self):   
            headers = self.headers
            request_outcome = process_request(url_address, "GET", headers, None, 1)
            info = {}             
            
            if request_outcome == TIME_OUT:
               info["code"] = TIME_OUT
            elif request_outcome:
               info["code"] = request_outcome.status
               info["headers"] = dict(request_outcome.getheaders())
               content = request_outcome.read().decode(ENCODING)
              
               try:
                  json_loads_content = json.loads(content)
                  info["json"] = json_loads_content
               except:                  
                  info["content"] = content
            else:
               info["code"] = CONNECTION_ERROR            
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')            
            self.end_headers()
            self.wfile.write(bytes(json.dumps(info, indent=4, ensure_ascii = False), ENCODING))            

        def do_POST(self):             
            info = {}                 
            
            try:
               content_len = int(self.headers['Content-Length'])
               loaded_data = self.rfile.read(content_len).decode(ENCODING)               
               loaded_data = json.loads(loaded_data)
               
               type_of_request = "GET"
               try:
                  type_of_request = loaded_data["type"]
               except:
                  pass

               if type_of_request != "POST": type_of_request = "GET"
              
               url_address = loaded_data["url"]               
               headers = loaded_data["headers"] if "headers" in loaded_data else {}
              
               content = None
               if type_of_request == "POST":
                  content = loaded_data["content"]
                  content = content.encode(ENCODING)                 
          
               timeout = 1 # one second
               try:
                  timeout = int(loaded_data[TIME_OUT])
               except:
                  pass                       
               
               request_outcome = process_request(url_address, type_of_request, headers, content, timeout) 
              
               if request_outcome == TIME_OUT:
                  info["code"] = TIME_OUT
               elif request_outcome:      
                  info["code"] = request_outcome.status   
                  info["headers"] = dict(request_outcome.getheaders())                 
                  content = request_outcome.read().decode(ENCODING)
                  
                  try:
                    json_loads_content = json.loads(content)
                    info["json"] = json_loads_content
                  except:                  
                    info["content"] = content
               else:
                  info["code"] = CONNECTION_ERROR
               
               self.send_response(200)
               self.send_header('Content-Type', 'application/json')               
               self.end_headers()
               self.wfile.write(bytes(json.dumps(info, indent=4, ensure_ascii = False), ENCODING))
            except:
               info["code"] = JSON_ERROR
               self.send_response(200)
               self.send_header('Content-Type', 'application/json')
               self.end_headers()
               self.wfile.write(bytes(json.dumps(info, indent=4, ensure_ascii = False), ENCODING))

    return RequestHandlerHTTP


def main():      
    if len(sys.argv) < 3:
        print("argv error: not enough program arguments")
        print("invocation: ./http-forward.py port upstream")
        sys.exit()

    http_server = HTTPServer(('', int(sys.argv[1])), get_post_handler(sys.argv[2]))
    http_server.serve_forever()

# start
main()
