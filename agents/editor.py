def editor(state):

    scores = {
        state["stories"][0]: 8,
        state["stories"][1]: 10,
        state["stories"][2]: 6
    }

    winner = max(scores, key=scores.get)

    state["story_scores"] = scores
    state["selected_story"] = winner

    state["editor_reasoning"] = (
        "Selected story with highest score"
    )

    return state