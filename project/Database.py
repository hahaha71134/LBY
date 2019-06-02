import datetime
import hashlib
import json
import re
import sqlite3
import time
# -*- coding: utf-8 -*-
from flask import  request


class Database:
    #browse times
    def browseTime(ip,articled):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()


        sql2="select * from browse  where ip='%s' and articleId=%s"%(ip,articled)

        c.execute(sql2)

        r = c.fetchall()

        if(r==[]):
            conn = sqlite3.connect('article.sqlite3')
            c = conn.cursor()
            sql = "Update  article set record=record+1 where articleId=%s" % (articled)
            c.execute(sql)
            c.close()
            conn.commit()
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql = "Insert or ignore into browse values('%s',%s)" % (ip, articled)
        c.execute(sql)
        c.close()
        conn.commit()

    # Search profiles by id
    def selectPersonal(id):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()

        ip = request.remote_addr
        sql2 = "SELECT articleId FROM comment where ip='" + ip + "'"

        c.execute(sql2)
        r2 = c.fetchall()
        print(r2)

        sql = "SELECT articleId FROM article where author='%s'"%(id)

        c.execute(sql)
        r = c.fetchall()
        r2.extend(r)

        list1 = []  # 鍒涘缓涓€涓柊鐨勬暟缁勬潵瀛樺偍鏃犻噸澶嶅厓绱犵殑鏁扮粍
        for element in r2:
            if (element not in list1):
                list1.append(element)
        list2=[]
        for articleId in list1:
            sql3 = "SELECT * FROM article where articleId=%s" % (articleId)

            c.execute(sql3)
            r3 = c.fetchall()
            list2.extend(r3)
        personalInfList=[]
        for article in list2:
            earchRecord = {}
            earchRecord['articleId'] = article[0]
            earchRecord['date'] = article[1]
            earchRecord['author'] = article[2]
            earchRecord['goodNum'] = article[3]
            earchRecord['badNum'] = article[4]
            earchRecord['commentNum'] = article[5]
            earchRecord['abstract'] = article[6]
            earchRecord['highlight'] = article[7]
            earchRecord['topicId'] = article[8]
            earchRecord['content'] = article[9]
            earchRecord['articleName'] = article[10]
            earchRecord['record'] = article[11]

            sql2= "SELECT topicName FROM topic where topicId='" + article[8] + "'"
            c.execute(sql2)
            r1 = c.fetchall()

            articleList = []
            for article in r1:
                articleJson = {}
                articleJson['topicName']=article[0]

                articleList.append(articleJson)
            earchRecord['article'] =articleList
            personalInfList.append(earchRecord)

        c.close()
        conn.commit()
        return personalInfList

    # Search all articles
    def selectAll():

        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()


        sql = "SELECT topicId,topicName FROM topic "

        c.execute(sql)
        r = c.fetchall()


        personalInfList=[]
        for topic in r:
            earchRecord = {}
            earchRecord['topicName'] = topic[1]
            earchRecord['topicId'] = topic[0]
            sql2= "SELECT * FROM childTopic where parentTopicId=" + str(topic[0])


            c.execute(sql2)
            r1 = c.fetchall()

            childTopicList = []
            for childTopic in r1:
                childTopicJson = {}
                childTopicJson['childTopicId']= childTopic[0]
                childTopicJson['topicName'] =  childTopic[1]
                childTopicJson['date'] =  childTopic[2]
                childTopicJson['parentTopicId'] =  childTopic[3]

                childTopicList.append(childTopicJson)
            earchRecord['childTopic'] =childTopicList
            personalInfList.append(earchRecord)



        c.close()
        conn.commit()
        return personalInfList
    #Search for articles by ID

    def selectArticle(id):

            conn = sqlite3.connect('article.sqlite3')
            c = conn.cursor()


            sql = "SELECT * FROM article where articleId='"+id+"'"

            c.execute(sql)
            r = c.fetchone()
            return r
    def selectArticleByIp(ip):

            conn = sqlite3.connect('article.sqlite3')
            c = conn.cursor()


            sql = "SELECT * FROM article where ip='"+ip+"'"

            c.execute(sql)
            r = c.fetchone()
            return r
    #Search for article content by ID
    def selectArticleContent(id):

            conn = sqlite3.connect('article.sqlite3')
            c = conn.cursor()


            sql = "SELECT * FROM article where articleId='"+id+"'"

            c.execute(sql)
            r = c.fetchone()
            return r
    #Search for comments on articles by ID
    def selectComment(id):

            conn = sqlite3.connect('article.sqlite3')
            c = conn.cursor()


            sql = "SELECT * FROM comment where articleId="+id+" order by date DESC"

            c.execute(sql)
            r = c.fetchall()
            return r
    #Search for titles by ID and childTopicId
    def selectTopic(id,childTopicId):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()

        if(childTopicId!="0"):
            sql = "SELECT * FROM article where childTopicId='" + childTopicId + "' and hidden=1 order by date DESC"


        else:
            sql = "SELECT * FROM article where topicId='" + id + "' and hidden=1 order by date DESC"

        c.execute(sql)
        r = c.fetchall()
        return r
    def selectHotArticle(id,childTopicId):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        if (childTopicId!="0"):
            sql = "SELECT * FROM article where childTopicId='" + id + "'" + " and hidden=1  ORDER BY (goodNum*2.5- badNum*2.5 + record + commentNum * 1.5 )/(goodNum*5+badNum*5+record*2+commentNum*3) DESC LIMIT 3"

        else:
            sql = "SELECT * FROM article where topicId='" + id + "'"+" and hidden=1  ORDER BY (goodNum*2.5 - badNum*2.5 + record + commentNum * 1.5 )/(goodNum*5+badNum*5+record*2+commentNum*3) DESC LIMIT 3"
        c.execute(sql)
        r = c.fetchall()
        return r
    def selectByKeywords(keywords):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql = "SELECT articleId FROM comment where content like '%" + keywords + "%'"
        c.execute(sql)
        r = c.fetchall()


        sql2="SELECT articleId FROM article where authorName like '%"+keywords+"%' or articleName  like '%"+keywords+"%' or abstract  like '%"+keywords+"%' or highlight  like '%"+keywords+"%'"
        c.execute(sql2)
        r2 = c.fetchall()

        r2.extend(r)

        list1 = []  # 鍒涘缓涓€涓柊鐨勬暟缁勬潵瀛樺偍鏃犻噸澶嶅厓绱犵殑鏁扮粍
        for element in r2:
            if (element not in list1):
                list1.append(element)
        array=[]

        for article in list1:
            conn = sqlite3.connect('article.sqlite3')
            c = conn.cursor()
            sql4="SELECT * FROM article where articleId="+ str(article[0])
            c.execute(sql4)
            r4= c.fetchall()
            array.extend(r4)
            c.close()
            conn.commit()


        resultInfList = []
        for article in array:
            earchRecord = {}
            earchRecord['articleId'] = article[0]
            earchRecord['date'] = article[1]
            earchRecord['author'] = article[2]
            earchRecord['goodNum'] = article[3]
            earchRecord['badNum'] = article[4]
            earchRecord['commentNum'] = article[5]
            earchRecord['abstract'] = article[6]
            earchRecord['highlight'] = article[7]
            earchRecord['topicId'] = article[8]
            earchRecord['content'] = article[9]
            earchRecord['articleName'] = article[10]
            earchRecord['record'] = article[11]
            earchRecord['authorName'] = article[12]
            sql3 = "SELECT * FROM comment where articleId=" + str(article[0])

            conn = sqlite3.connect('article.sqlite3')
            c = conn.cursor()
            c.execute(sql3)
            r3 = c.fetchall()

            c.close()
            conn.commit()
            commentList = []
            for comment in r3:
                commentJson = {}
                commentJson['commentId'] = comment[0]
                commentJson['articleId'] = comment[1]
                commentJson['content'] = comment[2]

                commentJson['goodNum'] = comment[3]
                commentJson['badNum'] = comment[4]

                commentList.append(commentJson)
            earchRecord['comment'] = commentList
            resultInfList.append(earchRecord)


        return resultInfList

    def insertArticle(articleName, authorName, email, articleAbstract, articleHighlight, articleContent, topicId,childTopicId):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        sql = "Insert into article values(NULL,'%s','%s',%s,%s,%s,'%s','%s',%s,'%s','%s',%s,'%s',1,'%s')"%(now_time,email,0,0,0,articleAbstract,articleHighlight,topicId,articleContent,articleName,0,authorName,childTopicId)

        c.execute(sql)
        c.close()
        conn.commit()

    def insertTopic(email, topicName):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        sql = "Insert into topic values(NULL,'%s','%s','%s')" % (topicName, email, now_time)
        c.execute(sql)

        c.close()
        conn.commit()
    def insertChildTopic(parentTopicId, topicName):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        sql = "Insert into childTopic values(NULL,'%s','%s',%s)" % (topicName, now_time,parentTopicId )
        c.execute(sql)
        c.close()
        conn.commit()

    def goodVote(ip,articleId):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql=" INSERT or  ignore INTO praise VALUES('%s','%s',0,0)"%(ip,articleId)
        c.execute(sql)
        c.close()
        conn.commit()

        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql1 = "select goodPraise from praise where ip='%s' and article='%s'" % (ip, articleId)

        c.execute(sql1)
        r = c.fetchone()
        if (r[0]==1):
            sql2="Update praise set goodPraise=0 where ip='%s' and article='%s'"%(ip,articleId)
            c.execute(sql2)

            sql3="Update article set goodNum=goodNum-1 where articleId=%s"%(articleId)
            c.execute(sql3)
            c.close()
            conn.commit()

        if (r[0]==0):
            sql2="Update praise set goodPraise=1 where ip='%s' and article='%s'"%(ip,articleId)
            c.execute(sql2)
            sql3="Update article set goodNum=goodNum+1 where articleId=%s"%(articleId)
            c.execute(sql3)
            c.close()
            conn.commit()

    def badVote(ip,articleId):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql=" INSERT or  ignore INTO praise VALUES('%s','%s',0,0)"%(ip,articleId)
        c.execute(sql)
        c.close()
        conn.commit()

        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql1 = "select badPraise from praise where ip='%s' and article='%s'" % (ip, articleId)

        c.execute(sql1)
        r = c.fetchone()
        if (r[0]==1):
            sql2="Update praise set badPraise=0 where ip='%s' and article='%s'"%(ip,articleId)
            c.execute(sql2)

            sql3="Update article set badNum=badNum-1 where articleId=%s"%(articleId)
            c.execute(sql3)
            c.close()
            conn.commit()

        if (r[0]==0):
            sql2="Update praise set badPraise=1 where ip='%s' and article='%s'"%(ip,articleId)
            c.execute(sql2)
            sql3="Update article set badNum=badNum+1 where articleId=%s"%(articleId)
            c.execute(sql3)
            c.close()
            conn.commit()

    def cGoodVote(ip,commentId):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql=" INSERT or  ignore INTO commentVote VALUES('%s',%s,0,0)"%(ip,commentId)
        c.execute(sql)
        c.close()
        conn.commit()

        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql1 = "select goodVote from commentVote where ip='%s' and commentId=%s" % (ip, commentId)

        c.execute(sql1)
        r = c.fetchone()
        if (r[0]==0):
            sql2="Update commentVote set goodVote=1 where ip='%s' and commentId='%s'"%(ip,commentId)
            c.execute(sql2)
            sql3="Update comment set goodNum=goodNum+1 where commentId=%s"%(commentId)
            c.execute(sql3)
            c.close()
            conn.commit()


    def cBadVote(ip,commentId):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql=" INSERT or  ignore INTO commentVote VALUES('%s',%s,0,0)"%(ip,commentId)
        c.execute(sql)
        c.close()
        conn.commit()

        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql1 = "select badVote from commentVote where ip='%s' and commentId=%s" % (ip, commentId)

        c.execute(sql1)
        r = c.fetchone()

        if (r[0]==0):
            sql2="Update commentVote set badVote=1 where ip='%s' and commentId='%s'"%(ip,commentId)
            c.execute(sql2)
            sql3="Update comment set badNum=badNum+1 where commentId=%s"%(commentId)
            c.execute(sql3)
            c.close()
            conn.commit()

    def selectTopicName():

        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql = "select topicName from topic"
        c.execute(sql)
        r = c.fetchall()

        c.close()
        conn.commit()
        return r

    def selectAllTopicName():

        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql = "select topicName from topic"
        c.execute(sql)
        r = c.fetchall()
        c.close()
        conn.commit()
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql1 = "select topicName from childTopic"
        c.execute(sql1)
        r1 = c.fetchall()
        c.close()
        conn.commit()
        r1.extend(r)
        return r1

    def selectArticleByAuthor(email,ip):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql = "select date from article where author='%s' and ip='%s' order by date DESC LIMIT 1"%(email,ip)
        c.execute(sql)
        r = c.fetchone()
        c.close()
        conn.commit()
        return r
    def selectAllArticleByAuthor(email):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql = "select * from article where author='%s' order by date"%(email)
        c.execute(sql)
        r = c.fetchall()
        c.close()
        conn.commit()
        return r
    def selectCommentByIp(ip):

        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql = "select date from comment where ip='%s' order by date DESC LIMIT 1" % (ip)

        c.execute(sql)
        r = c.fetchone()

        c.close()
        conn.commit()
        return r
    def insertCommet(comment,articleId):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        ip = request.remote_addr
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        sql = " INSERT into comment VALUES(Null,%s,'%s',0,0,'%s','%s')" % (articleId, comment,now_time,ip)
        c.execute(sql)
        c.close()
        conn.commit()
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql ="Update article set commentNum=commentNum+1 where articleId=%s"%(articleId)
        c.execute(sql)
        c.close()
        conn.commit()

    def selectAllArticle():

        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql = "select * from article"
        c.execute(sql)
        r=c.fetchall()
        c.close()
        conn.commit()
        return r

    def hiddenArticle(articleId,ishidden):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()

        sql=""
        if(ishidden=='1'):
            sql = "Update article set hidden=0 where articleId=%s"%(articleId)

        elif(ishidden=='0'):
            sql = "Update article set hidden=1 where articleId=%s"%(articleId)

        c.execute(sql)
        c.close()
        conn.commit()
    def deleteArticle(articleId):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()


        sql = "Delete from article where articleId=%s" % (articleId)

        c.execute(sql)
        c.close()
        conn.commit()

    def deleteCommentByArticleId(articleId):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()

        sql = "Delete from comment where articleId=%s" % (articleId)

        c.execute(sql)
        c.close()
        conn.commit()

    def selectAllComments():
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql = "select * from comment"
        c.execute(sql)
        r = c.fetchall()
        c.close()
        conn.commit()
        return r
    def deleteComment(commentId):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()

        sql = "Delete from comment where commentId=%s" % (commentId)

        c.execute(sql)
        c.close()
        conn.commit()
    def record(ip):
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        sql = "Insert or ignore into record values('%s','%s')" % (ip, now_time)

        c.execute(sql)
        c.close()
        conn.commit()

    def searchRecord():
        conn = sqlite3.connect('article.sqlite3')
        c = conn.cursor()
        sql="select * from record"
        c.execute(sql)
        r=c.fetchall()

        c.close()
        conn.commit()
        return r
