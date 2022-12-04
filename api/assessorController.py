from flask import Blueprint,request, Response, jsonify
import re

import uuid
import base64

from utils import (db_write,db_read)
from utils import token_required

assesseor_blueprint = Blueprint("assessor_blueprint",__name__)

def uuid_url64():
    rv = base64.b64encode(uuid.uuid4().bytes).decode('utf-8')
    return re.sub(r'[\=\+\/]', lambda m: {'+': '-', '/': '_', '=': ''}[m.group(0)], rv)

@assesseor_blueprint.route('/index',methods=["GET"])
@token_required
def index():
    return jsonify(str(uuid_url64())), 20


@assesseor_blueprint.route('create_assessment',methods=["POST"])
@token_required
def newAssessment():
    assessment_id = str(uuid_url64())
    assessor_id = request.json["assessor_id"]
    deadline = request.json["deadline"]
    topic = request.json["topic"]
   
    if db_write( """INSERT INTO assessment (assessment_id,assessor_id, topic, deadline) VALUES (%s, %s, %s, %s)""",
    (assessment_id,assessor_id,topic,deadline),):
        return jsonify({"assessment_id":assessment_id}),201
    else:
        return Response(409)
    
def mapAssessmentObject(rows):
    objects = []
    assessor_fullname = db_read("""SELECT full_name FROM user WHERE username = %s""", (rows[0][1],))[0]
    for row in rows:
        objects.append({"assessment_code":row[0], "assessor":assessor_fullname[0], "topic":row[2],"deadline":row[3],})
    return objects


@assesseor_blueprint.route('running_assessments', methods=["GET"])
@token_required
def getRunningAssessments():
    assessor_id = request.args.get('aid')
    assessments = db_read("""SELECT * FROM assessment WHERE assessor_id = %s AND deadline >= CURRENT_DATE() ORDER BY deadline ASC""", (assessor_id,))
    if assessments:
       mappedData =  mapAssessmentObject(assessments)
       return jsonify(mappedData),200
    else:
        return Response(status=200)


@assesseor_blueprint.route('completed_assessments', methods=["GET"])
@token_required
def getCompletedAssessments():
    assessor_id = request.args.get('aid')
    assessments = db_read("""SELECT * FROM assessment WHERE assessor_id = %s AND deadline < CURRENT_DATE() ORDER BY deadline DESC""", (assessor_id,))
    if assessments:
       mappedData =  mapAssessmentObject(assessments)
       return jsonify(mappedData),200
    else:
       return Response(status=200)
   
