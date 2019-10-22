from flask import Flask, request, session
from flask_cors import CORS, cross_origin
from copy import deepcopy

from claire_clever import ClaireClever

app = Flask(__name__)
CORS(app)
claire = ClaireClever()
    
def initiate_bot_dict():
    global bot_dict
    bot_dict = dict()
    bot_dict[0] = "dummy"
    
@app.route('/chatbot', methods = ['POST', 'GET'])
@cross_origin()
def chatbot():
    global bot_dict
    question = request.form['question']
    id = request.form['id']
    close_session = request.form['close_session']

    if close_session == "True":
        del bot_dict[int(id)]
        return {"answer": "", "id": id, "close_session": close_session}
    elif close_session == "False":
        if id == "To be set.":
            candidate_id = 0
            while id == "To be set.":
                if candidate_id not in bot_dict.keys():
                    id = candidate_id
                else:
                    candidate_id += 1
            bot_dict[id] = deepcopy(claire)
        id = int(id)
        answer, close_session = bot_dict[id].compute(question)
        if close_session == "True":
            del bot_dict[int(id)]
        return {"answer": answer, "id": str(id), "close_session": close_session}

if __name__ == "__main__":
    initiate_bot_dict()
    app.run(debug=True)
