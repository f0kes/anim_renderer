from base64 import b64encode
import json
import os
import uuid
from flask import Flask, jsonify, request
import requests
from requests.auth import HTTPBasicAuth
from dataclasses import dataclass
from typing import List, Optional
import datetime
from flask_cors import CORS
import urllib3
import websocket  # NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import logging

from workflows.animation_workflow import AnimationWorkflow
import model
import secret
import settings
from model import ProjectList, Project, parse_project_state

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
CORS(app)
projects: ProjectList
current_project: Optional[Project] = None
current_project_url: Optional[str] = None


animation_workflow = AnimationWorkflow(
    input_path=settings.INPUT_PATH,
    output_path=settings.OUTPUT_PATH,
    json_path=settings.JSON_PATH,
)


USERNAME = secret.USER_LOGIN
PASSWORD = secret.USER_PASSWORD
MAIN_SERVER_URL = settings.COMFYUI
client_id = str(uuid.uuid4())
ws = websocket.WebSocket()


def fetch_projects_from_main_server():
    global projects
    auth = HTTPBasicAuth(USERNAME, PASSWORD)
    response = requests.get(f"{MAIN_SERVER_URL}/api/projects", auth=auth)
    response.raise_for_status()
    projects_data = response.json()
    projects = model.project_list_from_dict(projects_data)


def construct_project_url(project: Project) -> Optional[str]:
    if project.state is None:
        return None
    if project.state.port is None:
        return None
    if project.state.state != "running":
        return None
    port = project.state.port
    return f"{MAIN_SERVER_URL}/comfy/{port}"


@app.route("/fetch", methods=["GET"])
def fetch():
    try:
        fetch_projects_from_main_server()
        return (
            jsonify(
                {
                    "message": "Projects fetched successfully",
                    "projects": projects.projects,
                }
            ),
            200,
        )
    except requests.RequestException as e:
        app.logger.error(
            "An error occurred while fetching projects: %s", e, exc_info=True
        )

        return jsonify({"error": str(e)}), 500


def basic_auth_header(username, password):
    assert ":" not in username
    user_pass = f"{username}:{password}"
    basic_credentials = b64encode(user_pass.encode()).decode()
    return ("Authorization", f"Basic {basic_credentials}")


@app.route("/set_project", methods=["POST"])
def set_project():
    global ws, client_id
    try:
        fetch_projects_from_main_server()
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500
    global current_project, current_project_url, projects
    project_id = request.json.get("project_id")
    if not project_id:
        return jsonify({"error": "project_id is required"}), 400

    project = next((p for p in projects if p.id == project_id), None)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    project_url = construct_project_url(project)
    if not project_url:
        return jsonify({"error": "Project is not running"}), 400
    current_project = project
    current_project_url = project_url
    project_url_ws = project_url.replace("http://", "ws://")

    auth_header = basic_auth_header(USERNAME, PASSWORD)
    print("{}/ws?clientId={}".format(project_url_ws, client_id))
    # debug log
    logging.debug(
        "Connecting to websocket at %s",
        "{}/ws?clientId={}".format(project_url_ws, client_id),
    )
    ws.connect(
        "{}/ws?clientId={}".format(project_url_ws, client_id),
        header={auth_header[0]: auth_header[1]},
    )
    # Here you would typically store or use this URL for subsequent operations
    return (
        jsonify({"message": "Project set successfully", "project_url": project_url}),
        200,
    )


@app.route("/project_api/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE"])
def reroute_to_current_project(subpath):
    global current_project_url
    if not current_project_url:
        return jsonify({"error": "No project set"}), 400
    url = f"{current_project_url}/{subpath}"
    auth = HTTPBasicAuth(USERNAME, PASSWORD)
    response = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key != "Host"},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        auth=auth,
    )

    # Return the response from the external server
    return (response.content, response.status_code, response.headers.items())


@app.route("/queue_render", methods=["POST"])
def queue_render():
    global current_project_url, animation_workflow, ws
    if "data" not in request.form:
        return jsonify({"error": "No data provided"}), 400

    try:
        data = json.loads(request.form["data"])
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400

    if "name" not in data:
        return jsonify({"error": "Name is required"}), 400

    name = data["name"]
    image_types = ["front", "back", "left", "right"]
    uploaded_files = {}
    auth = HTTPBasicAuth(USERNAME, PASSWORD)
    for image_type in image_types:
        if image_type not in request.files:
            return jsonify({"error": f"No {image_type} image uploaded"}), 400
        file = request.files[image_type]
        if file.filename == "":
            return jsonify({"error": f"No selected file for {image_type} image"}), 400
        if file:
            # post to current project/upload/image
            url = f"{current_project_url}/upload/image"
            new_filename = f"{name}_{image_type}.png"
            files = {"image": (new_filename, file)}
            data = {"type": "input", "overwrite": "true"}
            print("sending request to", url)
            response = requests.post(url, files=files, data=data, auth=auth)

            if response.status_code == 200:
                uploaded_files[image_type] = (
                    response.json()
                )  # Assuming the response contains JSON data
            else:
                return (
                    jsonify(
                        {
                            "error": f"Failed to upload {image_type} image. Status code: {response.status_code}"
                        }
                    ),
                    500,
                )
    names = {}
    for type, file in uploaded_files.items():
        names[type] = file["name"]
    workflows = animation_workflow.retrieve_workflows(
        left_image=names["left"],
        right_image=names["right"],
        front_image=names["front"],
        back_image=names["back"],
        model_name=name,
    )
    for workflow in workflows:
        resp = queue_prompt(workflow)
        if resp.status_code != 200:
            # save the failed workflow
            with open(f"failed_{name}.json", "w+") as file:
                json.dump(workflow, file, indent=4)
            return (
                jsonify(
                    {
                        "error": f"Failed to queue prompt. Status code: {resp.status_code}"
                    }
                ),
                500,
            )

    return (
        jsonify(
            {
                "message": f"All files uploaded successfully for {name}",
                "uploaded_files": uploaded_files,
            }
        ),
        200,
    )


@app.route("/progress", methods=["GET"])
def progress():
    global ws
    progress = check_progress(ws)
    return jsonify({"progress": progress}), 200


# return jsonify({"progress": 0.5}), 200


def queue_prompt(prompt):
    global client_id, current_project_url
    # prompt = json.dumps(prompt)
    p = {"prompt": prompt, "client_id": client_id}
    logging.debug(type(p["prompt"]))
    logging.debug(json.dumps(p))
    data = json.dumps(p).encode("utf-8")
    url = f"{current_project_url}/prompt"
    headers = {"Content-Type": "application/json"}
    auth = HTTPBasicAuth(USERNAME, PASSWORD)

    response = requests.post(url, json=p, headers=headers, auth=auth)

    return response


# ws is of type websocket
def check_progress(ws: websocket.WebSocket):
    while True:
        try:
            output = ws.recv()
            if isinstance(output, str):
                message = json.loads(output)
                data = message["data"]
                if message["type"] == "progress":
                    value = data["value"]
                    maximum = data["max"]
                    return value / maximum
                if message["type"] == "status":
                    queue_remaining = data["exec_info"]["queue_remaining"]
                    if queue_remaining == 0:
                        return 1.0
            else:
                continue
        except:
            continue


if __name__ == "__main__":
    app.run(debug=True, port=5000)
