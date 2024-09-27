from enum import Enum
from workflow_mutators.mutator import WorkflowMutator
from workflow import Node


class direction(Enum):
    LEFT = 1
    RIGHT = 2
    FRONT = 3
    BACK = 4


def angle_to_direction(angle: int) -> tuple[direction, direction]:
    if angle == 0:
        return direction.FRONT, direction.FRONT
    elif angle == 45:
        return direction.FRONT, direction.RIGHT
    elif angle == 90:
        return direction.RIGHT, direction.RIGHT
    elif angle == 135:
        return direction.RIGHT, direction.BACK
    elif angle == 180:
        return direction.BACK, direction.BACK
    elif angle == 225:
        return direction.BACK, direction.LEFT
    elif angle == 270:
        return direction.LEFT, direction.LEFT
    elif angle == 315:
        return direction.LEFT, direction.FRONT
    else:
        raise ValueError("Invalid angle")


class IPAdapterMutator(WorkflowMutator):
    def __init__(
        self,
        left_image: str = None,
        right_image: str = None,
        front_image: str = None,
        back_image: str = None,
        angle: int = None,
    ):
        self.images = {}
        self.set_images(left_image, right_image, front_image, back_image)
        self.angle = angle

    def set_images(
        self, left_image: str, right_image: str, front_image: str, back_image: str
    ):
        self.images = {
            direction.LEFT: left_image,
            direction.RIGHT: right_image,
            direction.FRONT: front_image,
            direction.BACK: back_image,
        }

    def set_angle(self, angle: int):
        self.angle = angle

    def filter(self, node: Node) -> bool:
        return node.title == "IPADAPTER_LOAD_1" or node.title == "IPADAPTER_LOAD_2"

    def mutate(self, node: Node) -> Node:
        if node.title == "IPADAPTER_LOAD_1":
            node.inputs["image"] = self.images[angle_to_direction(self.angle)[0]]
        elif node.title == "IPADAPTER_LOAD_2":
            node.inputs["image"] = self.images[angle_to_direction(self.angle)[1]]
        return node
