{% macro create_user(user) %}
createUser(
'{{ user.id }}',
'{{ user.nickname }}',
{% if user == room.master %}
true,
{% else %}
false,
{% endif %}
'{{ user.pfp }}')
{% endmacro %}


{% macro get_script() %}
<script type="text/javascript">

const spectators = document.getElementById("spectators");
const addTeam = document.getElementById("add-team");
const teams = document.getElementById("teams");


function createUser(id, nickname, is_master, pfp_url) {
    var user = document.createElement('div');
    user.id = id;
    user.className = 'd-flex align-items-center p-1 gap-3';

    var pfp = document.createElement('img');
    pfp.src = pfp_url;
    pfp.className = 'small-pfp';
    user.appendChild(pfp);


    var label = document.createElement('p');
    label.innerHTML = nickname;
    user.appendChild(label);

    if (is_master) {
        img = document.createElement('img')
        img.src = "{{ url_for_img('crown.png') }}";
        img.className = 'role';
        user.appendChild(img);
    };

    return user;
};
function createTeam(id, name, members) {
    var team = document.createElement('div');
    team.id = id;
    var label = document.createElement('h4');
    label.innerHTML = name;
    var list = document.createElement('div');
    list.className = 'members d-flex flex-grow-1';
    team.appendChild(label);
    team.appendChild(list);
    for (member of members) {
        list.innerHTML += member.outerHTML;
    }
    team.className = 'team m-2 border flex-grow-1 section';
    team.onclick = function() {socket.emit('move_to_team', ['{{ room.id }}', id])};
    teams.insertBefore(team, addTeam);
    return team;
}



var socket = io('/match/<id>');

// Events:
socket.on('create_team', function(id, name) {
    createTeam(id, name, []);
});
socket.on('move_to_team', function(user_id, team_id) {
    team = document.getElementById(team_id);
    user = document.getElementById(user_id);
    members = team.getElementsByClassName("members")[0];
    members.appendChild(user);
});
socket.on('move_to_spectators', function(user_id) {
    user = document.getElementById(user_id);
    members = spectators.getElementsByClassName("members")[0];
    members.appendChild(user);
});
socket.on('join', function(id, nickname, is_master, pfp) {
    user = createUser(id, nickname, is_master, pfp);
    members = spectators.getElementsByClassName("members")[0];
    members.appendChild(user);
})


socket.on('connect', function() {socket.emit('join', '{{ room.id }}')});
addTeam.onclick=function() {socket.emit('create_team', '{{ room.id }}')};
spectators.onclick=function() {socket.emit('move_to_spectators', '{{ room.id }}')};

spectators_members = spectators.getElementsByClassName("members")[0];
{% for spectator in room.spectators %}
spectators_members.appendChild({{ create_user(spectator) }});
{% endfor %}

{% for team in room.teams %}
var members = [];
{% for member in team %}
members.push({{ create_user(member) }});
{% endfor %}
createTeam('{{ team.id }}', '{{ team.name }}', members);
{% endfor %}



window.addEventListener('DOMContentLoaded', event => {

    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    let scrollToTopVisible = false;
    var m = true;
    // Closes the sidebar menu
    const menuToggle = document.body.querySelector('.menu-toggle');
    menuToggle.addEventListener('click', event => {
        event.preventDefault();
        sidebarWrapper.classList.toggle('active');
        menuToggle.classList.toggle('active');
        if (m) {
            document.getElementById("main").style.marginRight = "250px";
            m = false;
        }
        else {
            document.getElementById("main").style.marginRight = "0px";
            m = true;
        }
    })

    // Closes responsive menu when a scroll trigger link is clicked
    var scrollTriggerList = [].slice.call(document.querySelectorAll('#sidebar-wrapper .js-scroll-trigger'));
    scrollTriggerList.map(scrollTrigger => {
        scrollTrigger.addEventListener('click', () => {
            sidebarWrapper.classList.remove('active');
            menuToggle.classList.remove('active');
            document.getElementById("main").style.marginRight = "0px";
        })
    });
})



{% if room.user_is_master() %}

function clear(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

var start = document.createElement('a');
start.className = "btn rounded-pill btn-secondary";
start.innerHTML = 'Start';
start.onclick = function() {socket.emit('start', '{{ room.id }}')}

var play = document.createElement('div');
play.className = 'square-btn';
play.style.backgroundImage = 'url("{{ url_for_img('play.png') }}")'
play.onclick = function() {socket.emit('play', '{{ room.id }}')}

var pause = document.createElement('div');
pause.className = 'square-btn';
pause.style.backgroundImage = 'url("{{ url_for_img('pause.png') }}")'
pause.onclick = function() {socket.emit('pause', '{{ room.id }}')}

var state = document.getElementById('state-of-running');
state.appendChild(start);

{% endif %}


socket.on('start', function() {

{% if room.user_is_master() %}
clear(state);
state.appendChild(pause);
{% endif %}



})

socket.on('pause', function() {

{% if room.user_is_master() %}
clear(state);
state.appendChild(play);
{% endif %}



})

socket.on('play', function() {

{% if room.user_is_master() %}
clear(state);
state.appendChild(pause);
{% endif %}



})


socket.on('count_down', function(time) {
count_down = document.getElementById('count-down');
var interval = setInterval(function() {
  var minutes = Math.floor(time / 60);
  var seconds = time % 60;
  count_down.innerHTML = minutes + ":" + seconds;
  time = time - 1;
  if (time < 0) {
    clearInterval(interval);
    count_down.remove();
  }
}, 1000);
})

</script>
{% endmacro %}