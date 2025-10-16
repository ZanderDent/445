from flask import Flask, render_template, jsonify, send_from_directory, request
from datetime import datetime
import json
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# ---------- Helpers (CPM) ----------
def topological_order(tasks):
    name_to_task = {t["activityName"]: t for t in tasks}
    indeg = {t["activityName"]: 0 for t in tasks}
    graph = {t["activityName"]: [] for t in tasks}

    for t in tasks:
        preds = t.get("immediatePredecessor", []) or []
        for p in preds:
            if p not in name_to_task:
                raise ValueError(f"Predecessor '{p}' referenced by '{t['activityName']}' does not exist.")
            indeg[t["activityName"]] += 1
            graph[p].append(t["activityName"])

    # Kahn
    queue = [n for n, d in indeg.items() if d == 0]
    order = []
    while queue:
        n = queue.pop(0)
        order.append(n)
        for m in graph[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                queue.append(m)

    if len(order) != len(tasks):
        raise ValueError("Cycle detected in precedence graph.")
    return order, graph, name_to_task

def cpm(tasks):
    # normalize fields
    for t in tasks:
        if "activityName" not in t: t["activityName"] = t.get("task") or t.get("name")
        if "duration" not in t or t["duration"] is None:
            # last resort: duration from dates (inclusive)
            s = t.get("start"); f = t.get("finish")
            if s and f:
                d = (datetime.fromisoformat(f) - datetime.fromisoformat(s)).days + 1
                t["duration"] = max(1, d)
            else:
                t["duration"] = 1
        t["immediatePredecessor"] = t.get("immediatePredecessor") or t.get("predecessors") or []

    order, graph, name_to_task = topological_order(tasks)

    # forward pass
    for name in order:
        t = name_to_task[name]
        preds = t.get("immediatePredecessor", []) or []
        es = 0
        for p in preds:
            es = max(es, name_to_task[p]["EF"])
        t["ES"] = es
        t["EF"] = es + int(t["duration"])

    project_finish = max(name_to_task[n]["EF"] for n in name_to_task)

    # reverse pass
    rev = list(reversed(order))
    succs = {n: [] for n in name_to_task}
    for u, outs in graph.items():
        for v in outs:
            succs[u].append(v)

    for name in rev:
        t = name_to_task[name]
        if not succs[name]:
            lf = project_finish
        else:
            lf = min(name_to_task[s]["LS"] for s in succs[name])
        t["LF"] = lf
        t["LS"] = lf - int(t["duration"])
        t["TF"] = t["LF"] - t["EF"]
        t["Critical"] = (t["TF"] == 0)

    return {
        "project_duration_days": project_finish,
        "tasks": list(name_to_task.values()),
        "critical_path_activities": [n for n in order if name_to_task[n]["Critical"]],
    }

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("home.html")
    
@app.route("/schedule")
def homepage():
    return render_template("schedule.html")

@app.route("/survey")
def survey():
    return render_template("survey.html")

@app.route("/budget")
def budger():
    return render_template("budget.html")

@app.route("/api/schedule.json")
def schedule_json():
    # serve the editable JSON from /static so you can change it without touching Python
    return send_from_directory("static", "schedule.json", mimetype="application/json")

@app.route("/viewer")
def viewer():
    # default to your STL; allow override via ?file=/static/whatever.stl
    model_url = request.args.get("file", "/static/our_design.stl")
    return render_template("viewer.html", model_url=model_url)

@app.route("/wdm")
def wdm():
    return render_template("wdm.html")



@app.route("/api/cpm", methods=["POST"])
def api_cpm():
    data = request.get_json(force=True) or {}
    tasks = data.get("tasks", [])
    try:
        result = cpm(tasks)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
