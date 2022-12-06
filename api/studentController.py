from flask import Blueprint,request, Response, jsonify
from utils import (db_write,db_read,token_required)
from assessorController import mapAssessmentObject
from datetime import date

student_blueprint = Blueprint("student_blueprint",__name__)

@student_blueprint.route('/valid_assessment',methods=["GET"])
@token_required
def getAssessment():
    assessment_id = request.args.get('aid')
    assessment = db_read("""SELECT * FROM assessment WHERE assessment_id = %s""", (assessment_id,))
    if assessment:
       mappedData =  mapAssessmentObject(assessment)[0]
       mappedData['expired'] = True if mappedData['deadline']< date.today() else False
       return jsonify(mappedData),200
    else:
        return Response(status=200)
    
@student_blueprint.route('/assessment_enlistment')
@token_required
def enlistStudent():
    student_id = request.args.get('sid')
    assessment_id = request.args.get('aid')
    #INSERT INTO essay(essay.assessment_id) SELECT 'ass' WHERE NOT EXISTS(SELECT * FROM essay WHERE essay.essay_id=2)
    if db_write( """INSERT INTO essay(assessment_id,student_id) VALUES (%s,%s)""",
    (assessment_id,student_id),):
        return jsonify({"success":True,"assessment_id":assessment_id}),201
    else:
        return jsonify({"success":False, "message":"Something Went wrong"}),409

def mapEnlisted(rows):
    objects = []
    for row in rows:
        objects.append(
            {"essay_id":row[0], 
             "assessment_code":row[1], 
             "content":row[3],
             "score": (row[4]+row[5]) if row[4]!=-1 else 'N/A',
             "late_submit": 'N/A' if row[3]=='' else row[6],
             "topic":row[9],
             "deadline": row[10],
             "pending": True if row[3]=='' else False,
             "assessor": row[12]
             }
        )
    return objects

@student_blueprint.route('/assessments_enlisted', methods=["GET"])
@token_required
def enlistedAssessments():
    student_id = request.args.get('sid')
    rows =  db_read("""SELECT * FROM essay e INNER JOIN assessment a ON e.assessment_id= a.assessment_id INNER JOIN user u on u.username=a.assessor_id WHERE e.student_id= %s ORDER BY a.deadline ASC""", (student_id,))
    if rows:
        enlisted = mapEnlisted(rows)
        return jsonify(enlisted),200
    else:
        return Response(status=200)


@student_blueprint.route('assessment_submission',methods=['POST'])
@token_required
def submitAssessment():
    student_id = request.json['student_id']
    assessment_id = request.json['assessment_code'];
    content = request.json['content']
    deadline = db_read("""SELECT deadline FROM assessment WHERE assessment_id = %s""", (assessment_id,))[0][0]
    late_submit = False if deadline>=date.today() else True
    
    if db_write("""UPDATE essay SET content = %s, late_submit = %s WHERE student_id=%s AND assessment_id=%s""",(content,late_submit,student_id,assessment_id,)):
        return jsonify({"success":True}),201
    else:
        return Response(status = 409)
    

def mapAnalyticsData(rows):
    agg_score = 0
    lowest = 11
    highest = -1
    late_submissions = 0
    score_date = []
    scores = []
    
    for row in rows:
        
        score = row[4]+row[5]
        scores.append(score)
        lowest = score if score<lowest else lowest
        highest = score if score>highest else highest
        agg_score+=score
        late_submissions+= row[6]
        score_date.append({"score":score,"date":row[10]})
    
    object = {
        "submissions": len(rows),
        "avg_score": round((agg_score/len(rows)),1) if rows else 0,
        "lowest": lowest if lowest!=11 else 0,
        "highest":highest if highest!=-1 else 0,
        "late_sub": late_submissions,
        "scores":scores,
        "score_date":score_date
    }        
    return object
    
    
@student_blueprint.route('analytics_data',methods=["GET"])
@token_required
def getAnalyticsData():
    sid = request.args.get('sid')
    
    rows = db_read("""SELECT * FROM essay e INNER JOIN assessment a ON e.assessment_id= a.assessment_id WHERE e.student_id=%s AND e.manual_score>%s ORDER BY deadline ASC""",(sid,-1,))
    
    return jsonify({"success":True, "data": mapAnalyticsData(rows)}),200