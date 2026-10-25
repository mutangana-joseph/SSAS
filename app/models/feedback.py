
class Feedback:
    def __init__(self, feedback_id, variety_id, district_id, outcome, comments, created_at):
        self.feedback_id = feedback_id
        self.variety_id = variety_id
        self.district_id = district_id
        self.outcome = outcome
        self.comments = comments
        self.created_at = created_at
