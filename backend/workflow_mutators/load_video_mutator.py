import os
from workflow_mutators.mutator import WorkflowMutator
from workflow import Node


class LoadVideoMutator(WorkflowMutator):
    def __init__(
        self,
        input_path: str = None,
        output_path: str = None,
        model_name: str = None,
        render_context: list[str] = None,
        animation: str = None,
        angle: int = None,
    ):
        self.input_path = input_path
        self.output_path = output_path
        self.model_name = model_name
        self.context = render_context
        self.animation = animation
        self.angle = angle

    def retrieve_animations(self) -> list[str]:
        # concatenate input_path and model_name
        # return a list of names of subdirs in the directory
        model_path = os.path.normpath(
            os.path.join(self.input_path, self.model_name, "diffuse")
        )
        return os.listdir(model_path)

    def construct_paths_for_rotated_animation(self) -> dict:
        loads = [
            ("LOAD_{0}".format(context.upper()), context) for context in self.context
        ]
        paths = {}
        for load in loads:
            paths[load[0]] = os.path.normpath(
                os.path.join(
                    self.input_path,
                    self.model_name,
                    load[1],
                    self.animation,
                    str(self.angle),
                )
            )
        paths["SAVE_ANIM"] = os.path.normpath(
            os.path.join(
                self.output_path, self.model_name, self.animation, str(self.angle)
            )
        )
        return paths

    def filter(self, node: Node) -> bool:
        loads = ["LOAD_{0}".format(context.upper()) for context in self.context]
        return node.title in loads or node.title == "SAVE_ANIM"

    def mutate(self, node: Node) -> Node:
        paths = self.construct_paths_for_rotated_animation()
        if node.title == "SAVE_ANIM":
            node.inputs["output_path"] = paths["SAVE_ANIM"]
        else:
            node.inputs["directory"] = paths[node.title]
        return node
