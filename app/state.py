class AppState:
    def __init__(self):
        self.blocks = []
        self.answers = {}
        self.project_type = None

    def set_blocks(self, blocks):
        self.blocks = blocks

    def is_block_complete(self, block_id):
        block = next((b for b in self.blocks if b.id == block_id), None)
        if not block:
            return False
        return len(self.answers.get(block_id, {})) == len(block.questions)

    def has_any_complete_block(self):
        return any(self.is_block_complete(b.id) for b in self.blocks)

    def to_dict(self):
        return {"answers": self.answers, "project_type": self.project_type}

    def load_dict(self, data):
        self.answers = data.get("answers", {})
        self.project_type = data.get("project_type")

    def clear(self):
        self.blocks = []
        self.answers = {}
        self.project_type = None
