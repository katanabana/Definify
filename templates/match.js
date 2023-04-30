{% macro create_user(user) %}
createUser('{{ user.id }}', '{{ user.nickname }}','{{ user.pfp }}', '{{ user.score }}');
{% endmacro %}

{% macro get_script() %}
<script type="text/javascript">

// constants:

const socket = io('/match/<id_>');
const currentUserId = '{{ current_user.id }}';
var speaker = $('#speaker');
var speakerTeamId = null;
const gameplay = $('#gameplay').remove();

const spectators = $('#spectators'){% if not room.spectators %}.remove(){% endif %};
const guesses = gameplay.find('#guesses');
const guessInput = gameplay.find('#guess');

// helpers:

function createUser(id, nickname, pfp_url, scoreValue) {

    var user = $('<div>');
    user.attr('id', id);
    user.addClass('rounded d-flex justify-content-between align-content-center p-1 gap-3');

    var pfp = $('<img>');
    pfp.attr('src', pfp_url);
    pfp.addClass('small-pfp');
    user.append(pfp);


    var label = $('<p>');
    label.text(nickname);
    label.addClass('flex-grow-1')
    user.append(label);

    var score = $('<p>');
    score.addClass('border rounded score');
    score.text(scoreValue);
    user.append(score);
    score.hide();

    if (id == currentUserId) {
        user.css('background-color', '#5c5c8a');
    };

    return user;
};

function createTeam(teamId, name) {

    var team = $('<div>');
    team.attr('id', teamId);
    team.addClass('team m-2 border flex-grow-1 section');
    team.click(function() {socket.emit('move_to_team', ['{{ room.id }}', teamId])});
    team.insertBefore('#add-team');

    var label = $('<p>');
    label.text(name);
    team.append(label)

    var members = $('<div>');
    members.addClass('members d-flex flex-grow-1 flex-column');
    team.append(members);

    return team;
}

function moveToSection(userId, newSectionId) {

    var user = $('#' + userId);
    var previousSectionMembers = user.parent();
    var previousSection = previousSectionMembers.parent();

    if (previousSectionMembers.children().length == 1) {
        if (previousSection.attr('id') == 'spectators') {
            spectators.remove();
        }
        else {
            previousSection.remove();
            {% if room.user_is_master %}
            if ($('#teams').children().length == 1) {
                $('#start').hide();
            }
            {% endif %}
        }
    }
    if (newSectionId == 'spectators') {
        $('#members').prepend(spectators);
    }{% if room.started %} else {
        user.find('.score').show();
    }{% endif %}

    var newSectionMembers = $('#' + newSectionId + ' .members');
    newSectionMembers.append(user);

    if (newSectionId != 'spectators' && newSectionMembers.children().length > 1 && newSectionMembers.has('#' + currentUserId)) {
        $('#add-team').show();
    } else if (previousSectionMembers.has('#' + currentUserId) && previousSectionMembers.children().length == 1) {
        $('#add-team').hide();
    }

    {% if room.user_is_master() %}
    if ((previousSection.attr('id') == 'spectators' || previousSectionMembers.children().length > 1 || previousSectionMembers.children().length == 0) && (newSectionId == 'spectators' || newSectionMembers.children().length > 1)) {
        $('#start').show();
    } else {
        $('#start').hide();
    }
    {% endif %}
}

// event handlers:
gameplay.find('#speak').click(function() {socket.emit('speak', ['{{ room.id }}'])});


$('#add-team').click(function() {socket.emit('create_team', ['{{ room.id }}'])});
$('#spectators').click(function() {socket.emit('move_to_spectators', ['{{ room.id }}'])});
{% if room.user_is_master() %}
$('#start').click(function() {socket.emit('start', ['{{ room.id }}'])});
{% endif %}

$('#start').hide();

// loading room:
{% for user in room.spectators %}
var user = {{ create_user(user) }}
$('#spectators .members').append(user);
{% endfor %}

{% for team in room.teams %}

var team = createTeam('{{ team.id }}', '{{ team.name }}');

{% for user in team %}
var user = {{ create_user(user) }}
team.find('.members').append(user);
{% if room.started %}
user.find('.score').show();
{% endif %}
{% endfor %}
{% endfor %}


// socket configuration (handling events emitted by server):

socket.on('connect', function() {socket.emit('join', ['{{ room.id }}'])});

socket.on('join', function(userId, nickname, pfp) {
    $('#members').prepend(spectators);
    spectators.find('.members').append(createUser(userId, nickname, pfp, 0));
})

socket.on('create_team', function(userId, teamId, name) {
    createTeam(teamId, name);
    moveToSection(userId, teamId);
    if (userId == currentUserId) {
        $('#add-team').hide();
    }
});

socket.on('move_to_team', moveToSection);

socket.on('move_to_spectators', function(userId) {
moveToSection(userId, 'spectators');
if (currentUserId == userId) {
    $('#add-team').show();
}
});

socket.on('start', function() {
$('#start').remove();
$('#add-team').remove();
$('.score').show();
$('#main').append(gameplay);
guessInput.remove();
guesses.remove();
})

socket.on('wait', function(userId) {
    var prevSpeaker = speaker;
    var prevSpeakerTeamId = speakerTeamId;
    speaker = $('#' + userId);
    speakerTeamId = speaker.parent().parent().attr('id');

    prevSpeaker.replaceWith(speaker);
    $('#' + prevSpeakerTeamId).find('.members').append(prevSpeaker);

    $('#' + prevSpeakerTeamId).addClass('border');
    $('#' + speakerTeamId).addClass('border-green');

    if (currentUserId == userId) {
        $('#speak').show();
    } else {
        $('#speak').hide();
    }
    $('#word').text('');
    guesses.remove();
})

socket.on('speak', function() {
    guesses.children().remove();
    guesses.remove();
    if ($('#' + speakerTeamId).find('#' + currentUserId).length && currentUserId != speaker.attr('id')) {
        $('#guesses-container').append(guessInput);
        guessInput.keydown(function(event) {
    if (event.code == 'Enter') {
        socket.emit('guess', ['{{ room.id }}', guessInput.val()]);
    }
})
    } else {
        guessInput.remove();
    }
    $('#speak').hide();

    var time = {{ room.speak_time }};
    var interval = setInterval(function() {
        var minutes = Math.floor(time / 60);
        var seconds = time % 60;
        $('#count-down').text(minutes + ":" + seconds);
        time = time - 1;
        if (time < 0) {
        clearInterval(interval);
        $('#count-down').text('');
        }
    }, 1000);
})

socket.on('guess', function(userId, guess_text, correct) {
    var guess = $('<div>');
    guess.addClass('rounded d-flex');
    var user = $('#' + userId).clone();
    user.removeAttr('id');
    user.find('.small-pfp').css('width', 20);
    user.find('.small-pfp').css('height', 20);
    user.find('.score').remove();
    guess.append(user);
    guess_text_el = $('<p>');
    guess_text_el.text(': ' + guess_text);
    guess.append(guess_text_el);
    if (correct) {
        guess.addClass('border-green')
        var score = $('#' + userId + ' .score');
        score.text(parseInt(score.text()) + 1);
        speaker.find('.score').text(parseInt(speaker.find('.score').text()) + 1);
        scores = $('.score');
        //scores.sort(function(x, y) { return parseInt(x.text()) - parseInt(y.text()) });
//        scores[0].css('background-color', 'yellow');
//        scores[1].css('background-color', 'gray');
//        scores[2].css('background-color', 'brown');
//        for (var score of scores.slice(3, -1)) {
//            score.css('background-color', 'transparent');
//        }

    }
    $('#guesses-container').prepend(guesses);
    guesses.append(guess);
})

socket.on('update_word', function(word) {$('#word').text(word)})

socket.on('end', function(teamId) {
    var team = $('#' + teamId);
    team.find('.members').append(speaker);
    $('#main').html('We have a winner team!');
    $('#main').append(team);
})

</script>
{% endmacro %}