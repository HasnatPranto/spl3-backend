from flask import Blueprint,request, Response, jsonify
from utils import (db_write,db_read)
from utils import token_required
from ml_models.evaluate import getSystemScore

evaluation_blueprint = Blueprint("evaluation_blueprint",__name__)

def mapPapers(rows):
    objects = []
    for row in rows:
        objects.append(
            {"essay_id":row[0],
             "content":row[3],
             "manual_score": row[4] if row[4]!=-1 else 'Pending',
             "system_score": row[5] if row[5]!=-1 else 'Pending',
             "late_submit": 'N/A' if row[3]=='' else row[6],
             "topic":row[9],
             "deadline": row[10],
             "submitted": False if row[3]=='' else True,
             "student": row[12]
             }
        )
    return objects


@evaluation_blueprint.route('enlisted_students',methods=["GET"])
@token_required
def getSubmittedPapers():
    assessment_id = request.args.get('am_id')
    rows = db_read("""SELECT * FROM essay e INNER JOIN assessment a ON e.assessment_id= a.assessment_id INNER JOIN user u on u.username=e.student_id WHERE e.assessment_id=%s ORDER BY a.deadline ASC""",(assessment_id,))
    if rows:
        students = mapPapers(rows)
        return jsonify(students),200
    else:
        return Response(status=200)
    
    
@evaluation_blueprint.route('system_score',methods=["POST"])
@token_required
def evaluate():
    essay = request.json['essay']
    result = getSystemScore(essay)
    
    if result: 
        return jsonify({"success": True, "result":result}),200
    else:
        return jsonify({"success": False}),200

def calculateScore(mscore,sscore,weight):
    #print(round(((mscore*(1-weight))+(sscore*weight)),2))
    return round(((mscore*(1-weight))+(sscore*weight)),1)

@evaluation_blueprint.route('final_score',methods=["POST"])
@token_required
def finalScore():
    mscore = float(request.json['mscore'])
    sscore = float(request.json['sscore'])
    weight = float(request.json['weight'])
    
    return [calculateScore(mscore,sscore,weight)]


@evaluation_blueprint.route('score_submission', methods = ["POST"])
@token_required
def submitScore():
    w = float(request.json['weight'])
    mscore = round((float(request.json['manualScore'])*(1-w)),1)
    sscore = round((float(request.json['systemScore'])*(w)),1)
    essay_id = request.json["eid"]
    
    if db_write("""UPDATE essay SET manual_score = %s, system_score = %s WHERE essay_id=%s""",(mscore,sscore,essay_id)):
        return jsonify({"success":True}),201
    else:
        return Response(status = 409)