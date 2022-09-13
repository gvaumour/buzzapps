from app import app
from flask import render_template, request, jsonify
from app.models import Player,Game



@app.route("/", methods=["GET"])
def home():

    config_file = "config.json"
    my_game = Game(config_file)
    my_players = []

    players_info = ""
    for index in range(my_game.nb_players):

        player = Player(index, "Greg" + str(index))
        my_players.append(player)
        players_info += str(player)

    return render_template("index.html", players_info=players_info)


@app.route("/get-book-row/<int:id>", methods=["GET"])
def get_book_row(id):
    response = f"""
    <tr>
        <td></td>
        <td></td>
        <td>
            <button class="btn btn-primary"
                hx-get="/get-edit-form/{id}">
                Edit Title
            </button>
        </td>
        <td>
            <button hx-delete="/delete/{id}"
                class="btn btn-primary">
                Delete
            </button>
        </td>
    </tr>
    """
    return response
