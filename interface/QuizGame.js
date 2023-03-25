
var file_questions = Array()
var questions_file = ""
var songs = []

// Check for BlobURL support
var blob = window.URL || window.webkitURL;

class QuizGame
{
    constructor(server_hostname, server_port, name)
    {
        this.ws_hostname = server_hostname;
        this.ws_port = server_port;
        this.name = name;
        this.during_answer = false

        this.seed = Math.random().toString(36).replace(/[^a-z]+/g, '');

        this.answered_player = []
        this.list = [];
        this.current_music = 0;
        this.volume_playList = 1.0;

        this.init_ws();
    }

    init_ws()
    {
        this.ws = new WebSocket("ws://" + this.ws_hostname + ":" + this.ws_port);

        let ws = this.ws;

        ws.onmessage = (evt) =>
        {
            let data = JSON.parse(evt.data)
            if (Object.keys(data).length == 0)
                return;

            if (data.action  == "button_pressed") {
                if (this.during_answer && this.playing_colors.includes(data.player_color)) {
                    this.player_color = data.player_color
                    this.check_answer()
                }
            }

        };

        ws.onopen = (e) =>
        {
            console.log("Socket connected")
            this.ws_send({
                "action" : "connection",
                "client_type": "interfaceGM",
                "client_name" : this.name
            })

            this.update_interface()
        }

        ws.onerror = () =>
        {
            ws.close();
            clearTimeout(this.ws_timeout);
            this.ws_timeout = setTimeout(this.init_ws.bind(this), 500);
        }

        ws.onclose = (e) =>
        {
            console.log("Socket closed")

            if (e.reason == "closing")
            {
                setTimeout(this.init_ws.bind(this), 5000);
            }
            else
            {
                clearTimeout(this.ws_timeout);
                this.ws_timeout = setTimeout(this.init_ws.bind(this), 500);
            }
            this.update_interface()
        }
    }

    ws_send(data)
    {
        if (this.ws.readyState == WebSocket.OPEN)
        {
            if (typeof data == "string")
                this.ws.send(data);
            // if data is a dict
            else if (data.constructor == Object) {
                console.log(data)
                this.ws.send(JSON.stringify(data));
            }
            else {
                alert("The ws message was not send: " + data)
            }
        }
    }


    update_interface() {
        if(this.ws.readyState == WebSocket.OPEN) {
            document.getElementById("game_connection").hidden = true
            document.getElementById("game_connected").hidden = false
        }
        else {
            document.getElementById("game_connection").hidden = false
            document.getElementById("game_connected").hidden = true
            document.getElementById("game_config").hidden = true
        }

    }

    start_question() {

        if (this.during_answer)
            return
        
        this.players.forEach(player => player.has_already_answer = false)

        document.getElementById("resume_button").hidden = false
        document.getElementById("start_button").hidden = true

        this.during_answer = true

        this.ws_send({
            "action" : "startQuestion"
        })

        if (this.game_mode == "blindtest")
            document.getElementById("audio_player").play()

    }

    resume_question() {

        if (this.during_answer)
            return

        let playing_colors = []
        this.players.forEach(player => {
            if ( !(this.answer_mode === "answer_one" && player.has_already_answer))
                playing_colors.push(player.color)
        })

        this.during_answer = true
        this.ws_send({
            "action" : "resumeQuestion",
            "colors" : playing_colors
        })        
        document.getElementById("audio_player").play()
    }

    stop_question() {
 
        if (this.game_mode == "blindtest")
            document.getElementById("audio_player").pause()
        
        document.getElementById("resume_button").hidden = true
        document.getElementById("start_button").hidden = false

        if (!this.during_answer)
            return

        this.during_answer = false
        this.ws_send({
            "action" : "stopQuestion"
        })
    }

    next_question() {
        if (this.during_answer)
            this.stop_question()

        this.ws_send({
            "action": "turnLedsOff",
        })
        if (this.current_question == this.nb_questions)
            return

        document.getElementById("resume_button").hidden = true
        document.getElementById("start_button").hidden = false

        this.answered_player = []
        this.current_question++
        if (this.current_question == this.nb_questions)
            this.end_game()

        this.update_score_interface()
    }

    end_game(){

        this.ws_send({
            "action" : "endRound",
        })

        alert("Game is over")
    }

    previous_question() {
        if (this.during_answer)
            this.stop_question()

        document.getElementById("resume_button").hidden = true
        document.getElementById("start_button").hidden = false

        if (this.current_question == 0)
            return;

        this.answered_player = []
        this.current_question--
        this.update_score_interface()
    }

    accept_answer(score) {
        let modal = document.getElementById("modal_answer")
        modal.style.display = "none";
        this.update_score(this.player_color, score)

        if (score == this.points_per_questions)
            this.next_question()
        else
            this.resume_question()
    }
    refuse_answer() {
        let modal = document.getElementById("modal_answer")
        modal.style.display = "none";
        this.resume_question()
    }

    update_score(player_color, score) {
        let player = this.players.find(player => {return player.color === player_color})

        player.score += score
        if (player.score < 0)
            player.score = 0

        this.ws_send({
            "action" : "updateScore",
            "player_color" : player_color,
            "score" : player.score
        })
        this.update_score_interface()
    }

    init_game() {
        if (this.read_config() > 0)
        {
            // error handle in this.error
            alert(this.error)
            return;
        }
        if (this.game_mode != "blindtest" && this.game_mode != "quiz"){
            alert("This game mode is not implemented")
            return
        }

        this.nb_questions = this.questions_array.length
        this.current_question = 0

        document.getElementById("game_config").hidden = true
        document.getElementById("question_player").hidden = false
        if (this.game_mode == "quiz")
            document.getElementById("audio_player").hidden = true

        this.render_question_list()
        this.render_player_list()
        this.render_anwer_modal()

        this.update_score_interface()

        this.ws_send({
            "action" : "initGame",
            "game_type" : this.game_mode,
            "nb_players" : this.players.length,
            "nb_questions" : this.nb_questions,
            "answer_mode" : this.answer_mode,
            "players" : this.players,
            "questions": this.questions_array
        })
    }

    read_quiz_file() {

        let question = ""
        let answer = ""
        this.questions_array = []

        file_questions.split("\n").forEach(line => {
            if (line.empty)
                return
            let split_line = line.split(":")

            if (split_line.length < 2)
                return;

            if (split_line[0] == "Question") 
                question = split_line.slice(1).join('').trim()

            if (split_line[0] == "Réponse") {
                answer = split_line.slice(1).join('').trim()

                if (question == "")
                    alert("No question found for answer " + answer + ", skipping this")
                else {
                    this.questions_array.push({
                        "question" : question,
                        "answer" : answer
                    })    
                }
                question = ""
            }
        })
    }

    read_blindtest_file()
    {
        this.questions_array = []

        if (file_questions.length == 0) {
            this.error = "Question file not found"
            return 1
        }

        file_questions.split("\n").forEach(line => {
            if (line.empty)
                return
            let split_line = line.split("\t")
            
            if (split_line.length != 3)
                return;

            let mp3 = split_line[2].trim()

            let blob = songs.find(x => {
                return x.file === mp3;})

            if (blob == undefined) {  
                this.error = "Pb while parsing the config file: song not found " + split_line[2]
                return 1
            }

            this.questions_array.push({
                "auteur" : split_line[0],
                "chanson" : split_line[1],
                "mp3": mp3,
                "blob" : blob.blob
            })
        })

        if (this.questions_array.length == 0) {
            this.error = "Did not manage to parse the question file"
            return 1;
        }
        return 0;
    }

    check_answer() {

        let player = this.players.find(player => {return player.color === this.player_color})
        if (player == undefined)
            return;
        if (this.answer_mode === "answer_one" && player.has_already_answer)
            return;


        this.ws_send({
            "action" : "setOneColor",
            "color": this.player_color,
        })

        this.during_answer = false
        
        if (this.game_mode == "blindtest")
            document.getElementById("audio_player").pause()
        
        document.getElementById("text_answer").innerHTML = "Le joueur " + player.name + " a buzzé"



        if (this.answer_mode === "answer_one")
            player.has_already_answer = true

        let modal_answer = document.getElementById("modal_answer")
        modal_answer.style.display = "block";
    }

    read_config() {

        let e = document.getElementById("game_mode_select");
        let game_mode = e.value;
        if (game_mode != "blindtest" && game_mode != "quiz")
        {
            this.error = "Wrong value for the game mode (blindtest/quiz)"
            return 1;
        }

        this.game_mode = game_mode

        e = document.getElementById("points_per_question")
        let points_per_questions = e.value
        if (points_per_questions < 1) {
            this.error = "Wrong input for points per question"
            return 1;
        }
        this.points_per_questions = points_per_questions

        // Creating the player array based on filled player's names
        this.players = []
        this.playing_colors = []
        let colors = ["red", "yellow" , "white" , "blue" , "green"]
        colors.forEach(color => {
            let name = document.getElementById(color + "_name").value
            if (name) {
                this.players.push({
                    "color" : color,
                    "name" : name,
                    "score" : 0
                })
                this.playing_colors.push(color)
            }
        })

        e = document.getElementById("answer_mode_select");
        let answer_mode = e.value
        if (answer_mode != "answer_one" && answer_mode != "answer_freeforall") {
            this.error = "Wrong answer mode: "
            return 1;
        }
        this.answer_mode = answer_mode

        if(this.game_mode == "blindtest")
            return this.read_blindtest_file()
        else 
            return this.read_quiz_file()        
    }

    read_questions(e) {
        let files = e.target.files;
        songs = []

        for (let i = 0 ; i < files.length ; i++) {
            if (files[i].name.endsWith("txt")) {
                questions_file = files[i].name

                let reader = new FileReader();
                reader.onload = function(e) {
                    var contents = e.target.result
                    file_questions = contents

                };
                reader.readAsText(files[i]);
            }
            else {
                // We store the song url
                songs.push({
                    "blob": blob.createObjectURL(files[i]),
                    "file": files[i].name
                })
            }
        }
    }

    render_player_list() {

        let player_list = document.getElementById("player_list")

        this.players.forEach(player => {
          
            var tr = document.createElement('tr');
            tr.setAttribute("id","player_row");
          
            let td_color = document.createElement('td');
            td_color.innerHTML = player.color

            let td_name = document.createElement('td');
            td_name.setAttribute("id","player_row");
            td_name.innerHTML = player.name

            let td_score = document.createElement('td');
            td_score.setAttribute("id", player.color + "_score");
            td_score.innerHTML = "0"

            let td_button = document.createElement('td');
            td_button.setAttribute("id",player.color + "_buttons");
            td_button.innerHTML = "<button onclick='quizGame.update_score(\""+ player.color +"\", 1)'> + </button>"
            td_button.innerHTML += "<button onclick='quizGame.update_score(\""+ player.color +"\", -1)'> - </button>"

            tr.appendChild(td_color);
            tr.appendChild(td_name);
            tr.appendChild(td_score);
            tr.appendChild(td_button);

            player_list.appendChild(tr);
        })


        document.getElementById("fichier_name").innerHTML =
            "<b> Fichier </b> " + questions_file

    }

    /**
     * Generate the HTML table for the list of question of the round
     */
    render_question_list() {

        let question_list = document.getElementById("question_list")

        if (this.game_mode == "blindtest") {

            document.getElementById("question_player_header").innerHTML = "Blindtest Game"
            document.getElementById("question_list_header").innerHTML = "Blindtest Playlist"
            // Table Header Generation
            question_list.innerHTML = "<tr> <th> Titre </th> <th> Chanteur </th> <th>Fichier</th> </tr>"
            this.questions_array.forEach( (element, index, arr) => {

                let tr = document.createElement('tr');
                tr.setAttribute('class','song_item');

                let td_titre = document.createElement('td');
                td_titre.innerHTML = element.chanson
                let td_auteur = document.createElement('td');
                td_auteur.innerHTML = element.auteur
                let td_fichier = document.createElement('td');
                td_fichier.innerHTML = element.mp3

                tr.appendChild(td_titre)
                tr.appendChild(td_auteur)
                tr.appendChild(td_fichier)

                question_list.appendChild(tr)
            })
        }
        else if (this.game_mode == "quiz") {

            document.getElementById("question_player_header").innerHTML = "Quiz Game"
            document.getElementById("question_list_header").innerHTML = "Question List"
            question_list.innerHTML = "<tr> <th> Question </th> <th> Reponse </th></tr>"
            this.questions_array.forEach( (element, index, arr) => {

                let tr = document.createElement('tr');
                tr.setAttribute('class','song_item');

                let td_question = document.createElement('td');
                td_question.innerHTML = element.question
                let td_reponse = document.createElement('td');
                td_reponse.innerHTML = element.answer

                tr.appendChild(td_question)
                tr.appendChild(td_reponse)

                question_list.appendChild(tr)
            })

        }
    }

    render_anwer_modal() {

        let div = document.getElementById("modal-content")
        for(let i = 1 ; i <= this.points_per_questions; i++) {

            let button = document.createElement("button")
            button.setAttribute("onclick" , "quizGame.accept_answer(" + i  + ")")
            button.innerHTML = "+" + i
            div.appendChild(button)
        }
    }

    update_score_interface() {
        this.players.forEach( player => {
            document.getElementById(player.color + "_score").innerHTML = player.score
        })

        document.getElementById("question_number").innerHTML = "<b>Question </b>" +
            (this.current_question+1) + "/" + this.nb_questions

        if (this.game_mode == "blindtest") {
            document.getElementById("answer_name").innerHTML =
            "<b>Réponse:</b> <br />Auteur: " + this.questions_array[this.current_question].auteur +
                "<br /> Chanson: " + this.questions_array[this.current_question].chanson

            if (document.getElementById("audio_player").src !== this.questions_array[this.current_question].blob)
                document.getElementById("audio_player").src =
                    this.questions_array[this.current_question].blob
        }
        else if (this.game_mode == "quiz") {
            document.getElementById("answer_name").innerHTML = "<b> Question : </b> " + 
            this.questions_array[this.current_question].question + 
            "<br /> <b> Réponse : </b> " + this.questions_array[this.current_question].answer
        }

    }
}

let findGetParameter = (parameterName, defaultValue) =>
{
    let result = null,
        tmp = [];
    let items = location.search.substr(1).split("&");
    for (let index = 0; index < items.length; index++)
    {
        tmp = items[index].split("=");
        if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
    }

    if (result === null)
        result = defaultValue;
    return result;
}

