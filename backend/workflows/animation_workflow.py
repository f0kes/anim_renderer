from typing import List
from workflows.workflow_conatiner import WorkflowContainer, container_from_json
from workflow_mutators.ip_adapter_mutator import IPAdapterMutator
from workflow_mutators.load_video_mutator import LoadVideoMutator


class AnimationWorkflow:
    def __init__(self, input_path: str, output_path: str, json_path: str):
        self.workflow_container = container_from_json(json_path)
        self.ip_adapter_mutator = IPAdapterMutator()
        self.render_context = ["diffuse", "depth"]
        self.loader_mutator = LoadVideoMutator(
            input_path=input_path,
            output_path=output_path,
            render_context=self.render_context,
        )

        self.workflow_container.add_mutator(self.ip_adapter_mutator)
        self.workflow_container.add_mutator(self.loader_mutator)
        self.animation_names = []
        self.rotations = [0, 45, 90, 135, 180, 225, 270, 315]

    def retrieve_workflows(
        self, left_image, right_image, front_image, back_image, model_name
    ) -> List[dict]:
        self.ip_adapter_mutator.set_images(
            left_image, right_image, front_image, back_image
        )
        self.loader_mutator.model_name = model_name
        self.animation_names = self.loader_mutator.retrieve_animations()
        workflows = []
        for animation in self.animation_names:
            for angle in self.rotations:
                self.loader_mutator.animation = animation
                self.loader_mutator.angle = angle
                self.ip_adapter_mutator.set_angle(angle)
                self.workflow_container.apply_mutators()
                workflows.append(self.workflow_container.get_data_copy())
        return workflows
