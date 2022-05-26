#!/usr/bin/python3

import json
import os
import socket
import threading
import uuid
import tempfile

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 8547              # Arbitrary non-privileged port


html = '''
HTTP/1.1 200 OK
Content-Length: {}
'''

body ='''{}
'''

setCookie ='''Set-Cookie: id={}
'''

cookieTable = dict()
requestValues = dict()
listOfFiles= dict()
listOfCookies= []

#This function reads a file
def readFile(path):
    try:
        f = None
        f= open(path, encoding='cp437')
        #response = sendResponse(f,requestValues)encoding='cp437'
        
    except FileNotFoundError as e:
        f = None
    return f

#gets all the memos on the server
def doGetAPI(path, reqValues):
    
    response = None
    #open the file that stores a the list of users and their posts
    with open("memo.json", "r+") as file:
        parsedPosts = {}

        #convet json file to dict
        data = json.load(file)
        #get all the posts a user has made as files, then read the coresponding text
        for key in data:
            userPostFiles = data[key]
            parsedPosts.setdefault(key, [])
            for memoFile in userPostFiles:
                #read the files to get the memo
                fd =open(memoFile, "r")
                actualPost =fd.read()
                parsedPosts[key].append(actualPost)
    x= json.dumps(parsedPosts, indent=2)
    response = sendAPIResponse(x, reqValues)
    return response

#This function handles POST requests
#It accepts the request as input, then gets the file path it need to post to 
#Then it parses the post body to get the id and memo
def postAPI(req):
    #Split the POST line by spaces so that we get the file path
    
    print(req[0], "\n")
    #post has to have a body
    if len(req) > 1:
        #get the post body
        postBody = req[len(req) -1] 

        #split the rest of the request into key-value pairs
        for values in req:
            key = values.split(":")
            if(len(key) == 2):
                requestValues[key[0]]= key[1]
        
        #parse user input
        print(postBody, "\n")

        user =None;
        newMemo = None;

        #parse the body of the post request

        newMemoField = postBody
        newMemo = newMemoField.replace("enterMemo=", "")
            
        if("Cookie" in requestValues):
            #remove whitespace
            id = requestValues["Cookie"]
            id = id.split(";")
            user = id[0].replace(" ","")

            try:
                #create temporary file to store memo in
                temp_file = tempfile.NamedTemporaryFile(mode='w+t',prefix="temp_", dir="./db_memo", delete=False)
                
                #print(temp_file.name)

                #write the memo to the file
                temp_file.writelines(newMemo)
                #listOfFiles[user] = temp_file.name
                temp_file.close()

                #update the database that links files to the user that created them
                with open("memo.json", "r+") as file:
                    data = json.load(file)
                    if (user in data):
                        userPosts = data[user]
                        userPosts.append(temp_file.name)
                    else:
                        newValues ={user:[temp_file.name]}
                        data.update(newValues)
                    file.seek(0)
                    json.dump(data, file)
                    response = sendAPIResponse("", requestValues)
            except json.JSONDecodeError as e:
                response = handleBadRequest()
        else: 
            response= handleBadRequest()
    else:
        response= handleBadRequest()
    return response
            
        
def deleteAPI(req):
    #Split the DELETE line by spaces so that we get the file path
    splitRequest =req[0].split(" ")
    print(splitRequest, "\n")

    #file path will be the next string after POST
    filePath = splitRequest[1]   

    #split the rest of the request into key-value pairs
    for values in req:
        key = values.split(":")
        if(len(key) == 2):
            requestValues[key[0]]= key[1]

    #remove api from the file path so that we can get the actual file name
    memoPath = filePath.replace("/api/memo/","")
    

    #split the path into memo & id
    userID, memoPos = memoPath.split("&")
    
    data = None
    with open("memo.json", "r") as file:
        #convert the user-file database to dict
        data = json.load(file)
        #check if that user exists
        if(userID in data):
            if(len(data[userID])>int(memoPos)):
                fileToRemove =data[userID].pop(int(memoPos))
                os.unlink(fileToRemove)
                with open("memo.json","w") as f:
                    json.dump(data, f)
                response= sendAPIResponse("", requestValues)
            else:
                response = handleBadRequest()
        else:
            response = handleBadRequest()
    return response


def putAPI(req):
    #Split the DELETE line by spaces so that we get the file path
    splitRequest =req[0].split(" ")
    print(splitRequest, "\n")

    #file path will be the next string after POST
    filePath = splitRequest[1]  

    #get the post body
    postBody = req[len(req) -1]  

    #split the rest of the request into key-value pairs
    for values in req:
        key = values.split(":")
        if(len(key) == 2):
            requestValues[key[0]]= key[1]
    #get cookie and remove whitespace (this will be the current user updating the file)
    id = requestValues["Cookie"]
    id = id.split(";")
    currUser = id[0].replace(" ","")

    #remove api from the file path so that we can get the actual file name
    memoPath = filePath.replace("/api/memo/","")
    

    #split the path into memo & id
    userID, memoPos = memoPath.split("&")
    
    data = None
    with open("memo.json", "r+") as file:
        #convert the user-file database to dict
        data = json.load(file)
        #check if that user exists
        if(userID in data):
            #check if the user has create that specific file
            if(len(data[userID])>int(memoPos)):
                #get the file that needs to be updated
                fileToedit =data[userID].pop(int(memoPos))
                #write to the file
                fileToedit.writelines(postBody)
                #check if the person editing editing the files already has an entry in the db
                if(currUser in data):
                    userPosts = data[currUser]
                    userPosts.append(fileToedit)
                else:
                    newValues ={currUser:[fileToedit]}
                    data.update(newValues)
                file.seek(0)
                json.dump(data, file)
                response= sendAPIResponse("", requestValues)
            else:
                response = handleBadRequest()
        else:
            response = handleBadRequest()
    return response
    

def handleGetRequest(req):
    #Split the GET line
    
    splitRequest =req[0].split(" ")
    print(splitRequest, "\n")

    #file path will be the next string after GET
    filePath = splitRequest[1] 

    #get the keyvalue pairs do we can check for cookies
    requestValues.clear()
    for values in req:
        key = values.split(":")
        if(len(key) == 2):
            requestValues[key[0]]= key[1]
    
    #check if it an api request
    if("api" in filePath):
        #do get api
        response = doGetAPI(filePath, requestValues )
    else:
        #get normal file
        if (len(filePath) >1):
            filePath =filePath[1:] #remove the first /                    
            
            requestedFile = readFile(filePath)

            #if there is no file found send a 404
            if (requestedFile != None):
                response = sendResponse(requestedFile,requestValues)
            else:
                response = handleBadRequest()
        else:
            #home
            goHome = readFile("index.html")
            response = sendResponse(goHome,requestValues)
    return response



def sendResponse(fileName, reqValues):

    #check for cookies
    if("Cookie" in reqValues):
        myBody = body.format(fileName.read())
        daLength = len(myBody)
        myhtml = html.format(daLength)
        response = myhtml + "\n" + myBody
    else:
        #set-cookies
        myBody = body.format(fileName.read())
        daLength = len(myBody)
        myhtml = html.format(daLength)
        trackingCookie =uuid.uuid1()
        listOfCookies.append(trackingCookie)
        newCookie = setCookie.format(trackingCookie)
        response = myhtml +newCookie  + "\n" + myBody 

    
    #print(response, "\n")
    return response

def sendAPIResponse(fileName, reqValues):
    
    #check for cookies
    #print (reqValues)
    if("Cookie" in reqValues):
        myBody = body.format(fileName)
        daLength = len(myBody)
        myhtml = html.format(daLength)
        response = myhtml + "\n" + myBody
    else:
        #set-cookies
        myBody = body.format(fileName)
        daLength = len(myBody)
        myhtml = html.format(daLength)
        trackingCookie =uuid.uuid1()
        listOfCookies.append(trackingCookie)
        newCookie = setCookie.format(trackingCookie)
        response = myhtml +newCookie  + "\n" + myBody 
    return response
    
def handleBadRequest():

    badHtml =  '''
HTTP/1.1 404 Not Found
Content-Length: {}
'''
    notFoundBody = '''<html>
<body>
<h1>404 Not Found</h1>
</body>
</html>'''
    bodyLength = len(notFoundBody)
    myBadHtml = badHtml.format(bodyLength)
    response = myBadHtml + "\n" + notFoundBody
    print(response)
    return response


def threading_function(conn,addr):
    global res
    with conn:
        print('Connected by', addr)
        
        data = conn.recv(1024)
        if data:
            
            deData = data.decode()
            #print(deData)
            #parse request header
            splitHead= deData.split("\r\n") 
            

            if("favicon" in splitHead[0]):
                pass
            else:
                if("GET" in splitHead[0]):
                    res = handleGetRequest(splitHead)
                elif("POST" in splitHead[0]):
                   res= postAPI(splitHead)
                elif("PUT" in splitHead[0]):
                    res = putAPI(splitHead)
                elif("DELETE" in splitHead[0]):
                    res = deleteAPI(splitHead)
                conn.sendall(res.encode()) 
        conn.close()



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
    s.bind((HOST, PORT))
    s.listen()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while True:
        conn, addr = s.accept()
        newThread = threading.Thread(target=threading_function, args=(conn,addr,))
        newThread.start()