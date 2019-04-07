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

@app.route('/')
def mainPage():
    database = Database;

    mainInf = database.selectAll();

    return flask.render_template("mainPage.html", mainInf=mainInf)

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

@app.route('/topicPage/<topicId>')
def topicPage(topicId):
    database = Database;
    articleInf= database.selectTopic(topicId)
    articleInfHot=database.selectHotArticle(topicId)
    return flask.render_template('topicPage.html',topicId=topicId, articleInfHot=articleInfHot,articleInf=articleInf);

@app.route('/donatePage')
def donatePage():
    return flask.render_template('donatePage.html');

@app.route('/selectByKeywords',methods=['POST'])
def selectResult():
    keywords=request.form['keywords']
    database = Database;
    resultInfList=database.selectByKeywords(keywords)

    return flask.render_template('selectResult.html',resultInfList=resultInfList,keywords=keywords);

@app.route("/personal/<userId>")
def select(userId):
    database=Database;

    personalInf=database.selectPersonal(userId)

    print(personalInf)
    return flask.render_template("personalPage.html",personalInf=personalInf,email=userId)
@app.route('/addArticlePage',methods=['POST'])
def toAddArticlePage():
    topicId = request.form['topicId']
    return flask.render_template('addArticlePage.html',topicId=topicId);





@app.route('/insertTopic',methods=['POST'])
def insertTopic():
    email=request.form['email']
    topicName=request.form['topicName']
    addTopic = 1
    s=''
    database = Database
    allName=database.selectTopicName()
    print(allName)

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
        if(ratio>0.43):
            addTopic=0
            break

    if(addTopic):
        database.insertTopic(email,topicName)
        return redirect(url_for('mainPage'))
    else:
        return "The topic already exists"
@app.route('/download/<articleId>', methods=['GET'])
def download_pdf(articleId):
    database = Database
    article=database.selectArticleContent(articleId)
    with open('templates/test.pdf', 'wb') as f:
        f.write(base64.b64decode(article[9]))
    response = make_response(send_from_directory('templates', 'test.pdf', as_attachment=True))
    response.headers["Content-Disposition"] = (
        "attachment; filename='{0}'; filename*=UTF-8''{0}".format(article[10] + '.pdf'))
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
                               topicId)
            return "1"
    elif(r==None):

        database.insertArticle(articleName, authorName, email, articleAbstract, articleHighlight, file,
                               topicId)
        return "1"
    else:
        return "2"


@app.route('/insertComment',methods=['POST'])
def insertComment():
    articleId = request.form['articleId']
    comment = request.form['comment']
    database = Database
    database.insertCommet(comment,articleId)
    return 'ok'

if __name__ == '__main__':
    app.run(debug=True)
