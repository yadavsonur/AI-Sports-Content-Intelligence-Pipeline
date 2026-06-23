from typing import TypedDict

class WorkflowState(TypedDict):

    stories: list

    editor_decision: object

    script: str