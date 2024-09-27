from typing import Protocol
from workflow import Node, Workflow


class WorkflowMutator(Protocol):
    def filter(self, node: Node) -> bool: ...
    def mutate(self, node: Node) -> Node: ...


def mutate_workflow(
    workflow: Workflow,
    mutator: WorkflowMutator,
) -> Workflow:
    new_workflow = workflow.copy()
    nodes = [node for node in new_workflow.nodes if mutator.filter(node)]
    for node in nodes:
        node = mutator.mutate(node)
    return new_workflow
