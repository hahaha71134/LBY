import datetime
import hashlib
import json
import re
import sqlite3
import time
# -*- coding: utf-8 -*-



class Database:
    def browseTime(ip,articled):
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()


        sql2="select * from browse  where ip='%s' and articleId=%s"%(ip,articled)

        c.execute(sql2)

        r = c.fetchall()

        if(r==[]):
            conn = sqlite3.connect('school2.sqlite3')
            c = conn.cursor()
            sql = "Update  article set record=record+1 where articleId=%s" % (articled)
            print(sql)
            c.execute(sql)
            c.close()
            conn.commit()
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        sql = "Insert or ignore into browse values('%s',%s)" % (ip, articled)
        c.execute(sql)
        c.close()
        conn.commit()

    def selectPersonal(id):

        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()


        sql = "SELECT * FROM article where author='"+id+"'"

        c.execute(sql)
        r = c.fetchall()


        personalInfList=[]
        for article in r:
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

    def selectAll():

        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()


        sql = "SELECT topicId,topicName FROM topic "

        c.execute(sql)
        r = c.fetchall()


        personalInfList=[]
        for topic in r:
            earchRecord = {}
            earchRecord['topicName'] = topic[1]
            earchRecord['topicId'] = topic[0]
            sql2= "SELECT * FROM article where topicId=" + str(topic[0])+" and hidden=1 ORDER BY date DESC"


            c.execute(sql2)
            r1 = c.fetchall()


            articleList = []
            for article in r1:
                articleJson = {}
                articleJson['articleId']=article[0]
                articleJson['date'] = article[1]
                articleJson['author'] = article[2]
                articleJson['goodNum'] = article[3]
                articleJson['badNum'] = article[4]
                articleJson['commentNum'] = article[5]
                articleJson['abstract'] = article[6]
                articleJson['highlight'] = article[7]
                articleJson['topicId'] = article[8]
                articleJson['content'] = article[9]
                articleJson['articleName'] = article[10]
                articleJson['record'] = article[11]
                articleJson['score'] ='%.2f' %((( article[3]-article[4])*0.5+article[11]*0.2+ article[5]*0.3)/(article[3]+article[4]+article[5]+article[11])*100)
                articleList.append(articleJson)
            earchRecord['article'] =articleList
            personalInfList.append(earchRecord)



        c.close()
        conn.commit()
        return personalInfList

    def selectArticle(id):

            conn = sqlite3.connect('school2.sqlite3')
            c = conn.cursor()


            sql = "SELECT * FROM article where articleId='"+id+"'"

            c.execute(sql)
            r = c.fetchone()
            return r
    def selectArticleContent(id):

            conn = sqlite3.connect('school2.sqlite3')
            c = conn.cursor()


            sql = "SELECT * FROM article where articleId='"+id+"'"

            c.execute(sql)
            r = c.fetchone()
            return r
    def selectComment(id):

            conn = sqlite3.connect('school2.sqlite3')
            c = conn.cursor()


            sql = "SELECT * FROM comment where articleId="+id+" order by goodNum-badNUm DESC"
            print(sql)
            c.execute(sql)
            r = c.fetchall()
            return r
    def selectTopic(id):
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()

        sql = "SELECT * FROM article where topicId='" + id + "' order by date DESC"

        c.execute(sql)
        r = c.fetchall()
        return r
    def selectHotArticle(id):
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()

        sql = "SELECT * FROM article where topicId='" + id + "'"+"ORDER BY goodNum*5-badNum*5+commentNum*3+record*3 LIMIT 3"
        c.execute(sql)
        r = c.fetchall()


        return r
    def selectByKeywords(keywords):
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        sql = "SELECT articleId FROM comment where content like '%" + keywords + "%'"
        c.execute(sql)
        r = c.fetchall()


        sql2="SELECT articleId FROM article where authorName like '%"+keywords+"%' or articleName  like '%"+keywords+"%' or abstract  like '%"+keywords+"%' or highlight  like '%"+keywords+"%'"
        c.execute(sql2)
        r2 = c.fetchall()

        r2.extend(r)

        list1 = []  # 创建一个新的数组来存储无重复元素的数组
        for element in r2:
            if (element not in list1):
                list1.append(element)
        array=[]
        print(list1)
        for article in list1:
            conn = sqlite3.connect('school2.sqlite3')
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

            conn = sqlite3.connect('school2.sqlite3')
            c = conn.cursor()
            c.execute(sql3)
            r3 = c.fetchall()
            print(r3)
            c.close()
            conn.commit()
            commentList = []
            for comment in r3:
                commentJson = {}
                commentJson['commentId'] = comment[0]
                commentJson['articleId'] = comment[1]
                commentJson['content'] = comment[2]
                print("comment")
                print(comment[2])
                commentJson['goodNum'] = comment[3]
                commentJson['badNum'] = comment[4]

                commentList.append(commentJson)
            earchRecord['comment'] = commentList
            resultInfList.append(earchRecord)

        print(resultInfList)
        return resultInfList

    def insertArticle(articleName, authorName, email, articleAbstract, articleHighlight, articleContent, topicId):
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        sql = "Insert into article values(NULL,'%s','%s',%s,%s,%s,'%s','%s',%s,'%s','%s',%s,'%s')"%(now_time,email,0,0,0,articleAbstract,articleHighlight,topicId,articleContent,articleName,0,authorName)
        print(sql)
        c.execute(sql)
        c.close()
        conn.commit()

    def insertTopic(email, topicName):
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        sql = "Insert into topic values(NULL,'%s','%s','%s')" % (topicName, email, now_time)
        c.execute(sql)

        c.close()
        conn.commit()

    def goodVote(ip,articleId):
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        sql=" INSERT or  ignore INTO praise VALUES('%s','%s',0,0)"%(ip,articleId)
        c.execute(sql)
        c.close()
        conn.commit()

        conn = sqlite3.connect('school2.sqlite3')
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
            print(sql3)
        if (r[0]==0):
            sql2="Update praise set goodPraise=1 where ip='%s' and article='%s'"%(ip,articleId)
            c.execute(sql2)
            sql3="Update article set goodNum=goodNum+1 where articleId=%s"%(articleId)
            c.execute(sql3)
            c.close()
            conn.commit()

    def badVote(ip,articleId):
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        sql=" INSERT or  ignore INTO praise VALUES('%s','%s',0,0)"%(ip,articleId)
        c.execute(sql)
        c.close()
        conn.commit()

        conn = sqlite3.connect('school2.sqlite3')
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
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        sql=" INSERT or  ignore INTO commentVote VALUES('%s',%s,0,0)"%(ip,commentId)
        c.execute(sql)
        c.close()
        conn.commit()

        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        sql1 = "select goodVote from commentVote where ip='%s' and commentId=%s" % (ip, commentId)

        c.execute(sql1)
        r = c.fetchone()
        if (r[0]==1):
            sql2="Update commentVote set goodVote=0 where ip='%s' and commentId='%s'"%(ip,commentId)
            c.execute(sql2)

            sql3="Update comment set goodNum=goodNum-1 where commentId=%s"%(commentId)
            c.execute(sql3)
            c.close()
            conn.commit()
            print(sql3)
        if (r[0]==0):
            sql2="Update commentVote set goodVote=1 where ip='%s' and commentId='%s'"%(ip,commentId)
            c.execute(sql2)
            sql3="Update comment set goodNum=goodNum+1 where commentId=%s"%(commentId)
            c.execute(sql3)
            c.close()
            conn.commit()


    def cBadVote(ip,commentId):
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        sql=" INSERT or  ignore INTO commentVote VALUES('%s',%s,0,0)"%(ip,commentId)
        c.execute(sql)
        c.close()
        conn.commit()
        print(sql)
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        sql1 = "select badVote from commentVote where ip='%s' and commentId=%s" % (ip, commentId)
        print(sql1)
        c.execute(sql1)
        r = c.fetchone()
        if (r[0]==1):
            sql2="Update commentVote set badVote=0 where ip='%s' and commentId='%s'"%(ip,commentId)
            c.execute(sql2)
            print(sql2)
            sql3="Update comment set badNum=badNum-1 where commentId=%s"%(commentId)
            c.execute(sql3)
            c.close()
            conn.commit()
            print(sql3)
        if (r[0]==0):
            sql2="Update commentVote set badVote=1 where ip='%s' and commentId='%s'"%(ip,commentId)
            c.execute(sql2)
            sql3="Update comment set badNum=badNum+1 where commentId=%s"%(commentId)
            c.execute(sql3)
            c.close()
            conn.commit()

    def selectTopicName():

        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        sql = "select topicName from topic"
        c.execute(sql)
        r = c.fetchall()

        c.close()
        return r

    def selectArticleByAuthor(email):
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        sql = "select date from article where author='%s' order by date DESC LIMIT 1"%(email)
        print(sql)
        c.execute(sql)
        r = c.fetchone()

        c.close()
        return r

    def insertCommet(comment,articleId):
        conn = sqlite3.connect('school2.sqlite3')
        c = conn.cursor()
        sql = " INSERT into comment VALUES(Null,%s,'%s',0,0)" % (articleId, comment)
        c.execute(sql)
        c.close()
        conn.commit()


