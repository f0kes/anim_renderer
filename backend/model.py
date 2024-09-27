from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import datetime
import requests
import secret
import settings
from requests.auth import HTTPBasicAuth


@dataclass
class ProjectState:
    id: str
    name: str
    pid: Optional[int]
    port: Optional[int]
    state: str
    status_message: str
    __dict__ = lambda self: {
        "id": self.id,
        "name": self.name,
        "pid": self.pid,
        "port": self.port,
        "state": self.state,
        "status_message": self.status_message,
    }


@dataclass
class Project:
    id: str
    state: ProjectState
    project_folder_name: str
    project_folder_path: str
    last_modified: datetime.datetime
    port: int
    __dict__ = lambda self: {
        "id": self.id,
        "state": self.state.__dict__,
        "project_folder_name": self.project_folder_name,
        "project_folder_path": self.project_folder_path,
        "last_modified": self.last_modified.timestamp(),
        "port": self.port,
    }


@dataclass
class ProjectList:
    projects: List[Project]
    __dict__ = lambda self: [proj.__dict__ for proj in self.projects]

    def __iter__(self):
        return iter(self.projects)


def parse_project_state(state_dict: Optional[dict]) -> ProjectState:
    if state_dict is None:
        return ProjectState(
            id=None, name=None, pid=None, port=None, state=None, status_message=None
        )
    return ProjectState(
        id=state_dict.get("id"),
        name=state_dict.get("name"),
        pid=state_dict.get("pid"),
        port=state_dict.get("port"),
        state=state_dict.get("state"),
        status_message=state_dict.get("status_message"),
    )


def project_list_from_dict(data: dict) -> ProjectList:
    projects = [
        Project(
            id=proj.get("id"),
            state=parse_project_state(proj.get("state")),
            project_folder_name=proj.get("project_folder_name"),
            project_folder_path=proj.get("project_folder_path"),
            last_modified=datetime.datetime.fromtimestamp(proj.get("last_modified", 0)),
            port=proj.get("port"),
        )
        for proj in data
    ]
    return ProjectList(projects)


def debug_print_project_list(project_list: ProjectList):
    for project in project_list.projects:
        print(f"Project ID: {project.id}")
        print(f"State: {project.state}")
        print(f"Project Folder Name: {project.project_folder_name}")
        print(f"Project Folder Path: {project.project_folder_path}")
        print(f"Last Modified: {project.last_modified}")
        print(f"Port: {project.port}")
        print()


def test(api_url: str, login: str, password: str):
    auth = HTTPBasicAuth(login, password)
    response = requests.get(f"{api_url}/api/projects", auth=auth)
    response.raise_for_status()
    project_list = project_list_from_dict(response.json())
    debug_print_project_list(project_list)


if __name__ == "__main__":
    test(settings.COMFYUI, secret.USER_LOGIN, secret.USER_PASSWORD)
