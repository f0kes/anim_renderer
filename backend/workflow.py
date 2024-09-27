from dataclasses import dataclass
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.normpath(os.path.join(script_dir, ".", "assets"))
json_path = os.path.normpath(os.path.join(assets_path, "anim.json"))
mutated_path = os.path.normpath(os.path.join(assets_path, "mutated.json"))

with open(json_path, "r") as file:
    data = json.load(file)


@dataclass
class Node:
    id: int = 0
    class_type: str = ""
    title: str = ""
    inputs: dict = None

    def copy(self):
        return Node(
            id=self.id,
            class_type=self.class_type,
            title=self.title,
            inputs=self.inputs,
        )


@dataclass
class Workflow:
    nodes: list[Node]

    def copy(self):
        return Workflow([node.copy() for node in self.nodes])


def unpack_node(data: dict, id: int = 0) -> Node:
    node = Node()
    node.id = id
    node.inputs = data.get("inputs", [])

    meta: dict = data.get("_meta", {})
    node.class_type = data.get("class_type", "")
    node.title = meta.get("title", "")

    return node


def pack_node(node: Node) -> dict:
    return {
        "inputs": node.inputs,
        "class_type": node.class_type,
        "_meta": {
            "title": node.title,
        },
    }


def workflow_from_dict(data: dict) -> Workflow:
    nodes = [unpack_node(node[1], node[0]) for node in data.items()]
    return Workflow(nodes=nodes)


def find_node_in_dict(data: dict, node_id: int) -> dict:
    for node in data.items():
        if node[0] == node_id:
            return node[1]
    return None


# should search for the node with the id and update it (only changed fields)
def mutate_dict_with_workflow(data: dict, workflow: Workflow) -> dict:
    new_data = data.copy()
    for node in workflow.nodes:
        node_dict = find_node_in_dict(new_data, node.id)
        if node_dict:
            node_dict.update(pack_node(node))
    return new_data


if __name__ == "__main__":
    workflow = workflow_from_dict(data)
    # node = node where title = "IPADAPTER_LOAD_1"
    node = next(
        (node for node in workflow.nodes if node.title == "IPADAPTER_LOAD_1"), None
    )
    if node:
        node.inputs = ["new_value"]
    mutated_data = mutate_dict_with_workflow(data, workflow)
    # save mutated_data to file
    with open(mutated_path, "w+") as file:
        json.dump(mutated_data, file, indent=4)
