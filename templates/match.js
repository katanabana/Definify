{% macro get_script() %}
<script type="text/javascript">

var socket = io('/match/<id>');


function getUser(nickname, id) {
    user = document.createElement(null);
    user.outerHTML = `{{ get_user(nickname, id) }}`;
    return user;
};

function emitCreateTeam() {
    socket.emit('create_team', '{{ room.id }}');
};

function emitMoveToSpectators() {
    console.log('dsafas');
    socket.emit('move_to_spectators', '{{ room.id }}');
};

function addUserToSection(user_id, section_id) {
    section = document.getElementById(section_id);
    user = document.getElementById(user_id);
    members = section.getElementsByClassName("members")[0];
    members.appendChild(user);
};


const spectators = document.getElementById("spectators");
const addTeam = document.getElementById("add-team");
const teams = document.getElementById("teams");

socket.on('create_team', function(id) {
    team = document.createElement('div');
    team.className = 'team m-2 border flex-grow-1 section';
    team.id = id;
    team.onclick = function() {socket.emit('move_to_team', ['{{room.id}}', id])};
    const name = document.createElement('h4');
    name.innerHTML = 'Team ' + teams.childElementCount.toString();
    members = document.createElement('ul');
    members.className = 'members';
    team.appendChild(name);
    team.appendChild(members);
    teams.insertBefore(team, addTeam);
});

socket.on('connect', function() {
socket.emit('join', '{{room.id}}');
});

socket.on('join', function(nickname, id) {
    spectators.appendChild(getUser(nickname, id));
});

socket.on('move_to_team', addUserToSection);

socket.on('move_to_spectators', function(user_id) {addUserToSection(user_id, 'spectators')});


addTeam.onclick=emitCreateTeam;
spectators.onclick=emitMoveToSpectators;
</script>
{% endmacro %}