
class Player:

    def __init__(self, index, name):
        self.name = name
        self.id = index
        self.score = 0
        self.state = False


    def __repr__(self):
        return '<div class="row"> \
                <div class="cell" data-title="ID"> ' + str(self.id) + '</div> \
                <div class="cell" data-title="Name"> ' + str(self.name) + '</div> \
                <div class="cell" data-title="Score"> ' + str(self.score) + '</div> \
                <div class="cell" data-title="State"> Not done </div> \
                </div>'

class Game:

    def __init__(self, config_file):
        self.config_file = config_file
        self.nb_questions =  10
        self.score_per_question = 10
        self.nb_players = 4
