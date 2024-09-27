from backend.workflow_mutators.mutator import WorkflowMutator
from backend.workflow import Node


class SuperMutator(WorkflowMutator):
    def __init__(self, mutators: list[WorkflowMutator]):
        self.mutators = mutators

    def filter(self, node: Node) -> bool:
        return any([mutator.filter(node) for mutator in self.mutators])

    def mutate(self, node: Node) -> Node:
        for mutator in self.mutators:
            if mutator.filter(node):
                return mutator.mutate(node)
        return node
