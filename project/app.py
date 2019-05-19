import base64
import datetime
import mimetypes
import os
import time

import xhtml2pdf.pisa as pisa
import json
from io import StringIO, BytesIO
import flask
from flask import Flask, request, redirect, url_for, current_app, make_response, render_template, send_from_directory
from jinja2 import Environment, PackageLoader
from pymysql.constants.FIELD_TYPE import JSON
import difflib


from Database import Database
app = Flask(__name__)
# -*- coding: utf-8 -*-
#Home page
@app.route('/')
def mainPage():
    database = Database;
    ip = request.remote_addr
    database.record(ip)
    mainInf = database.selectAll();

    return flask.render_template("mainPage.html", mainInf=mainInf)

#Article content page
@app.route('/articlePage/<articleId>')
def articlePage(articleId):

        database = Database;
        ip = request.remote_addr
        database.browseTime(ip,articleId)
        articleInf = database.selectArticle(articleId)
        commentInf=database.selectComment(articleId)
        return flask.render_template("articlePage.html", articleInf=articleInf,commentInf=commentInf)

@app.route('/enterPage')
def enterPage():
    return flask.render_template('enterPage.html');

#Topic content page
@app.route('/topicPage/<topicId>/<childTopicId>')
def topicPage(topicId,childTopicId):
    database = Database;
    articleInf= database.selectTopic(topicId,childTopicId)
    print(articleInf)
    articleInfHot=database.selectHotArticle(topicId,childTopicId)
    articleInfHotList=[]
    articleInfList=[]

    for article in articleInfHot:
        if (article[3] + article[4] + article[5] + article[11]):
            a = '%.2f' % (50 + (((article[3] - article[4]) * 2.5 + article[11] * 1.5 + article[5]) / (
                    article[3] * 5 + article[4] * 5 + article[5] * 2 + article[11] * 3) * 100))
        else:
            a=0
        tup2 = (a,)
        article = article + tup2
        articleInfHotList.append(article)

    for article in articleInf:

        if (article[3] + article[4] + article[5] + article[11]):
           a='%.2f' % (50+(((article[3] - article[4]) * 2.5 + article[11]*1.5+ article[5]) / (
                article[3]*5 + article[4]*5 + article[5]*2 + article[11]*3) * 100))
        else:
            a = 0
        tup2=(a,)
        article=article+tup2
        articleInfList.append(article)

    return flask.render_template('topicPage.html',topicId=topicId, childTopicId=childTopicId,articleInfHot=articleInfHotList,articleInf=articleInfList);

#Donate Page
@app.route('/donatePage')
def donatePage():
    return flask.render_template('donatePage.html');
#Search for articles by keyword
@app.route('/selectByKeywords',methods=['POST'])
def selectResult():
    keywords=request.form['keywords']
    database = Database;
    resultInfList=database.selectByKeywords(keywords)
    return flask.render_template('selectResult.html',resultInfList=resultInfList,keywords=keywords);
#Personal home page
@app.route("/personal/<userId>")
def select(userId):
    database=Database;
    personalInf=database.selectPersonal(userId)
    return flask.render_template("personalPage.html",personalInf=personalInf,email=userId)

@app.route('/addArticlePage',methods=['POST'])
def toAddArticlePage():
    topicId = request.form['topicId']
    childTopicId=request.form['childTopicId']
    return flask.render_template('addArticlePage.html',topicId=topicId,childTopicId=childTopicId);




#Add topic
@app.route('/insertTopic',methods=['POST'])
def insertTopic():
    email=request.form['email']
    topicName=request.form['topicName']
    addTopic = 1
    s=''
    database = Database
    allName=database.selectTopicName()
    for name in allName:
        for c in name[0]:
            if c.isspace():
                nameAbbr=name[0].lower().split(" ")
                s=''
                for abbr in nameAbbr:
                    s+=abbr[0:1]

                if(topicName.lower()==s):
                    addTopic = 0
                    break

        seq = difflib.SequenceMatcher(None, name[0].lower(), topicName.lower())
        ratio = seq.ratio()
        print(ratio)
        if(ratio>0.58):
            addTopic=0
            break

    if(addTopic):
        database.insertTopic(email,topicName)
        return redirect(url_for('mainPage'))
    else:
        return "The topic already exists"

#Add subtopics
@app.route('/insertChildTopic', methods=['POST'])
def insertChildTopic():
    parentTopicId = request.form['parentTopicId']
    topicName = request.form['topicName']
    addTopic = 1
    s = ''
    database = Database
    allName = database.selectAllTopicName()
    for name in allName:
        for c in name[0]:
            if c.isspace():
                nameAbbr = name[0].lower().split(" ")
                s = ''
                for abbr in nameAbbr:
                    s += abbr[0:1]

                if (topicName.lower() == s):
                    addTopic = 0
                    break

        seq = difflib.SequenceMatcher(None, name[0].lower(), topicName.lower())
        ratio = seq.ratio()
        if (ratio >0.9):
            addTopic = 0
            break

    if (addTopic):
        database.insertChildTopic(parentTopicId, topicName)
        return redirect(url_for('mainPage'))
    else:
        return "The topic already exists"

@app.route('/download/<articleId>', methods=['GET'])
def download_pdf(articleId):
    database = Database
    article=database.selectArticleContent(articleId)
    name=article[10]
    name=str(name).encode()
    print(name)
    with open('templates/test.pdf', 'wb') as f:
        f.write(base64.b64decode(article[9]))
    response = make_response(send_from_directory('templates', 'test.pdf', as_attachment=True))
    response.headers["Content-Disposition"] = (
        "attachment; filename='{0}'; filename*=UTF-8''{0}".format(article[10].encode('utf-8').decode('ISO-8859-1')+ '.pdf'))
    response.headers['Content-Type'] = 'application/pdf'

    return response


@app.route('/goodVote/<articleId>',methods=['GET','POST'])
def goodVote(articleId):
    ip = request.remote_addr

    database = Database
    database.goodVote(ip,articleId)
    return "ok"

@app.route('/badVote/<articleId>',methods=['GET','POST'])
def badVote(articleId):
    ip = request.remote_addr
    print(articleId)
    database = Database
    database.badVote(ip,articleId)
    return "ok"



@app.route('/cGoodVote/<commentId>',methods=['GET','POST'])
def cGoodVote(commentId):
    ip = request.remote_addr

    database = Database
    database.cGoodVote(ip,commentId)
    return "ok"

@app.route('/cBadVote/<commentId>',methods=['GET','POST'])
def cBadVote(commentId):
    ip = request.remote_addr

    database = Database
    database.cBadVote(ip,commentId)
    return "ok"

@app.route('/detection',methods=['POST'])
def detection():
    topicId = request.form['topicId']
    childTopicId=request.form['childTopicId']
    articleName = request.form['articleName']
    authorName = request.form['authorName']
    email = request.form['email']
    articleAbstract = request.form['articleAbstract']
    articleHighlight = request.form['articleHighlight']
    file = request.files['file']
    encoded = base64.b64encode(file.read())
    file=encoded.decode('ascii')
    database = Database
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    r=database.selectArticleByAuthor(email)
    if r:
        t=time.mktime(time.strptime(now_time, '%Y-%m-%d %H:%M')) - time.mktime(time.strptime(r[0], '%Y-%m-%d %H:%M'))
        if(t>300):

            database.insertArticle(articleName, authorName, email, articleAbstract, articleHighlight, file,
                               topicId,childTopicId)

            return "1"
        else:
            return "2"
    elif(r==None):

        database.insertArticle(articleName, authorName, email, articleAbstract, articleHighlight, file,
                               topicId,childTopicId)

        return "1"



@app.route('/insertComment',methods=['POST'])
def insertComment():
    articleId = request.form['articleId']
    comment = request.form['comment']
    database = Database

    ip = request.remote_addr
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    r = database.selectCommentByIp(ip)
    if r:
        t = time.mktime(time.strptime(now_time, '%Y-%m-%d %H:%M')) - time.mktime(time.strptime(r[0], '%Y-%m-%d %H:%M'))
        if (t > 300):
            database.insertCommet(comment, articleId)
    elif (r == None):

        database.insertCommet(comment, articleId)
    return 'ok'

@app.route('/management')
def management():
    database = Database
    article =database.selectAllArticle()

    return flask.render_template('managementPage.html', article=article);

@app.route('/hidden/<articleId>/<ishidden>')
def hidden(articleId,ishidden):
    database = Database
    database.hiddenArticle(articleId,ishidden)

    article = database.selectAllArticle()
    return flask.render_template('managementPage.html', article=article);

@app.route('/delete/<articleId>')
def delete(articleId):
    database = Database
    database.deleteArticle(articleId)
    database.deleteComment(articleId)
    comments = database.selectAllComments()
    article = database.selectAllArticle()
    return flask.render_template('managementPage.html', article=article,comments=comments);


@app.route('/deleteComment/<commentId>')
def deleteComment(commentId):
    database = Database
    database.deleteComment(commentId)

    comments = database.selectAllComments()
    article = database.selectAllArticle()
    return flask.render_template('managementPage.html', article=article,comments=comments);
@app.route('/toManagementPage')
def toManagementPage():
    return flask.render_template('toManagement.html');


@app.route('/toAuthorPage/<authorEmail>')
def toAuthorPage(authorEmail):

    database = Database
    articleInf=database.selectAllArticleByAuthor(authorEmail)
    print(articleInf)
    return flask.render_template('authorPage.html',articleInf=articleInf);
#To manage the interface
@app.route('/toManagement',methods=['POST'])
def toManagement():
    database = Database
    psw=request.form['psw']
    if(psw=="123456"):
        article = database.selectAllArticle()
        comments = database.selectAllComments()
        records=database.searchRecord()
        return flask.render_template('managementPage.html', article=article,comments=comments,records=records);
    else:
        return flask.render_template('toManagement.html');


if __name__ == '__main__':
    app.run(debug=True)
