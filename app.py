import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import statistics
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "replace_with_secure_key")
app.config['NEWS_API_KEY'] = os.environ.get("NEWS_API_KEY", "")

# ----------------- Helpers -----------------

def analyze(total):
    if total < 8:
        return "Low", 100 - int(total/8*40), "Excellent — your footprint is low!"
    elif total < 15:
        return "Moderate", 70 - int((total-8)/7*20), "Moderate footprint. Improve habits."
    else:
        return "High", 40 - int((total-15)/20*30), "High footprint! Reduce energy and travel."

def diet_analysis(diet_kgs):
    if diet_kgs < 1:
        return {"category":"Low","text":"Low footprint diet.","tips":["Plant meals","Local produce"]}
    elif diet_kgs < 3:
        return {"category":"Moderate","text":"Moderate diet impact.","tips":["Reduce red meat","Seasonal veggies"]}
    else:
        return {"category":"High","text":"High diet impact.","tips":["2-3 meat meals/week","Legumes and grains"]}

def update_gamification(total):
    g = session.get('game', {"points":0,"badges":[],"last_date":None,"streak":0})
    # Points
    g['points'] += 30 if total<8 else 15 if total<15 else 5
    # Streak
    last = g.get('last_date')
    today = datetime.utcnow().date()
    if last:
        last_date = datetime.fromisoformat(last).date()
        g['streak'] = g.get('streak',0)+1 if today==last_date+timedelta(days=1) else 1 if today!=last_date else g.get('streak',0)
    else:
        g['streak']=1
    g['last_date']=datetime.utcnow().isoformat()
    # Badges
    badges=set(g.get('badges',[]))
    if g['points']>=100: badges.add("Eco Enthusiast")
    if g['streak']>=7: badges.add("7-Day Streak")
    if total<8: badges.add("Low Impact Day")
    g['badges']=list(badges)
    session['game']=g
    return g

def fetch_news(limit=5):
    key=app.config.get('NEWS_API_KEY') or os.environ.get('NEWS_API_KEY')
    if not key:
        return [{"title":"Sample news headline","source":"Local"}]
    try:
        r = requests.get("https://newsapi.org/v2/everything",
                         params={"q":"environment","language":"en","pageSize":limit,"apiKey":key})
        r.raise_for_status()
        return [{"title":a["title"],"source":a["source"]["name"],"url":a["url"]} for a in r.json().get("articles",[])]
    except:
        return [{"title":"News fetch failed","source":"System"}]

# ----------------- Routes -----------------

@app.route('/')
def index():
    saved=session.get('last_inputs',{})
    return render_template('index.html', saved=saved)

@app.route('/result', methods=['POST'])
def result():
    try:
        travel=float(request.form.get("travel",0))
        electricity=float(request.form.get("electricity",0))
        diet=float(request.form.get("diet",0))
        shopping=float(request.form.get("shopping",0))
    except:
        return redirect(url_for('index'))
    total=round(travel+electricity+diet+shopping,2)
    level,score,message=analyze(total)
    diet_report=diet_analysis(diet)
    game=update_gamification(total)
    snapshots=session.get('snapshots',[])
    snapshots.append({"timestamp":datetime.utcnow().isoformat(),"travel":travel,"electricity":electricity,"diet":diet,"shopping":shopping,"total":total,"level":level})
    session['snapshots']=snapshots[-30:]
    session['last_inputs']={"travel":travel,"electricity":electricity,"diet":diet,"shopping":shopping}
    return render_template('result.html', travel=travel, electricity=electricity, diet=diet,
                           shopping=shopping, total=total, level=level, score=score, message=message,
                           diet_report=diet_report, game=game)

@app.route('/dashboard')
def dashboard():
    snapshots=session.get('snapshots',[])
    labels=[s['timestamp'][:16].replace('T',' ') for s in snapshots]
    totals=[s['total'] for s in snapshots]
    latest=snapshots[-1] if snapshots else None
    avg=round(statistics.mean(totals),2) if totals else 0
    game=session.get('game',{"points":0,"badges":[],"streak":0})
    news=fetch_news(limit=5)
    return render_template('dashboard.html', labels=labels, totals=totals,
                           latest=latest, avg=avg, game=game, news=news)

@app.route('/tips')
def tips():
    tips_list=[
        {"title":"Reduce Short Car Trips","text":"Walk or use public transport."},
        {"title":"Efficient Electricity Use","text":"Switch to LED, unplug devices."},
        {"title":"Mindful Diet Choices","text":"More plant-based meals."},
        {"title":"Conscious Shopping","text":"Buy durable goods."},
        {"title":"Small Goals","text":"Consistent changes are sustainable."}
    ]
    return render_template('tips.html', tips=tips_list)

@app.route('/avatar')
def avatar():
    snapshots=session.get('snapshots',[])
    total=snapshots[-1]['total'] if snapshots else 0
    return render_template('avatar.html', total=total)

@app.route('/habit')
def habit():
    return render_template('habit.html')

@app.route('/quiz')
def quiz():
    questions=[
        {"q":"Which food has lowest footprint?","options":["Beef","Chicken","Vegetables"],"answer":2},
        {"q":"Best electricity saving habit?","options":["LED bulbs","Incandescent","Leave ON"],"answer":0}
    ]
    return render_template('quiz.html', questions=questions)

@app.route('/leaderboard')
def leaderboard():
    game=session.get('game',{"points":0,"badges":[],"streak":0})
    return render_template('leaderboard.html', game=game)

@app.route('/history')
def history():
    snapshots=session.get('snapshots',[])
    return render_template('history.html', snapshots=snapshots)

@app.route('/api/snapshots')
def api_snapshots():
    return jsonify(session.get('snapshots',[]))

if __name__=='__main__':
    app.run(debug=True)
@app.route("/about")
def about():
    project_name = "CarbonAI - Smart Carbon Footprint Analyzer"
    team = ["Arati Lod", "Team Member 1", "Team Member 2"]
    return render_template("about.html", project=project_name, team=team)
