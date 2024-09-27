from backend.workflow import Node
from workflow_mutators.mutator import WorkflowMutator


class PromptMutator(WorkflowMutator):
    def __init__(self, prompt: str):
        self.prompt = prompt

    def filter(self, node: Node) -> bool:
        return node.title == "PROMPT"

    def mutate(self, node: Node) -> Node:
        node.inputs[0] = self.prompt
        return node
