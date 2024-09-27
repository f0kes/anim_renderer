import json
import os
from typing import Callable, Protocol
import copy
from workflow import mutate_dict_with_workflow, workflow_from_dict
from workflow_mutators.mutator import WorkflowMutator, mutate_workflow


script_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.normpath(os.path.join(script_dir, ".", "assets"))
json_path = os.path.normpath(os.path.join(assets_path, "anim.json"))
mutated_path = os.path.normpath(os.path.join(assets_path, "mutated.json"))


class WorkflowContainer:
    def __init__(self, data: dict):
        self.data = data
        self.workflow = workflow_from_dict(data)
        self.mutators: list[WorkflowMutator] = []

    def load_from_file(self, path: str = json_path):
        with open(path, "r") as file:
            self.data = json.load(file)
            self.workflow = workflow_from_dict(self.data)

    def add_mutator(self, mutator: WorkflowMutator):
        self.mutators.append(mutator)

    def apply_mutators(self):
        for mutator in self.mutators:
            self.workflow = mutate_workflow(self.workflow, mutator)
        self.data = mutate_dict_with_workflow(self.data, self.workflow)

    def get_data_copy(self):
        return copy.deepcopy(self.data)


def container_from_json(path: str = json_path) -> WorkflowContainer:
    with open(path, "r") as file:
        data = json.load(file)
    return WorkflowContainer(data)
