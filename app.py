import sqlite3
from flask import Flask, session, render_template, request, g
from datetime import datetime

from SQLDriver import *

app = Flask(__name__)

# GLOBAL STATIC
CurrentUser = None  #UCID, password, name, email, type
CurrentTeam = None

# END GLOBAL STATIC

@app.route('/')
def index():
    # init_db()
    # initDefaultUsersAndAdmins()
    # dbTest()
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    global CurrentUser
    try:
        if request.method == 'POST':
            username = request.form['UCID']
            password = request.form['password']
            result, CurrentUser = loginUser(int(username), password)
            print(CurrentUser)
            if result:
                print("UCID:",username, "PASSWORD:",password)
                return render_template("home.html", name=("Hi " + CurrentUser[0][2] + "!"), type=CurrentUser[0][4])
            else:
                return render_template("index.html", LOGIN_ERROR_MSG="Invalid UCID or password")
        else:
            return render_template("index.html")
    except Exception as e:
        return render_template("index.html", LOGIN_ERROR_MSG=str(e))


@app.route('/register', methods=['GET', 'POST'], endpoint='register')
def register():
    if request.method == 'POST':
        response = add_new_profile(request.form['ucid'], request.form['password'], request.form['name'], request.form['email'])
        if response == "SUCCESS":
            return render_template("index.html",REGISTER_MSG="Registration successful")
        elif response == "FAILURE":
            return render_template("index.html",REGISTER_MSG="Registration failed")
        elif response == "UNIQUE constraint failed: EndUser.UCID":
            return render_template("index.html",REGISTER_MSG="UCID already exists in the system, please login")
        else:
            return render_template("index.html",REGISTER_MSG=response)
    else:
        return render_template("index.html")
        
@app.route('/stats', methods=['GET', 'POST'], endpoint='stats')
def stats():
    if request.method == 'POST':
        stats = get_user_stats(CurrentUser[0][0])
        if len(stats) == 0:
            return render_template("stats.html", matchesWon="This user does not have any stats recorded in the database yet")
        matchesWon = "matches Won: " + str(stats[0][2])
        hoursPlayed = "hours Played: " + str(stats[0][3])
        matchesPlayed = "matches Played: " + str(stats[0][4])
        return render_template("stats.html", matchesWon = matchesWon, hoursPlayed = hoursPlayed, matchesPlayed = matchesPlayed)
    else:
        return render_template("home.html")

@app.route('/SUBMIT_TEAMS', methods=['GET', 'POST'], endpoint='SUBMIT_TEAMS')
def SUBMIT_TEAMS():
    global CurrentTeam
    if request.method == 'POST':
        team_name = request.form['team_name']
        team_type = request.form['team_type']
        CurrentTeam = team_name
        # player_ucid = request.form['player_ucid']
        success, team_id = new_team(team_name, team_type, CurrentUser[0][0])
        if success:
            print("TEAM ID: ", team_id, "TEAM NAME: ", team_name, "TEAM TYPE: ", team_type)
            return render_template("teams.html", NEW_TEAM_MSG="Team created successfully", teams=get_all_teams_with_user(CurrentUser[0][0]))
        else:
            return render_template("teams.html", NEW_TEAM_MSG=team_id, teams=get_all_teams_with_user(CurrentUser[0][0]) )
    else:
        return render_template("home.html")

@app.route('/Delete_Teams', methods=['GET', 'POST'], endpoint='Delete_Teams')
def Delete_Teams():
    if request.method == 'POST':
        team_id = request.form['team_id']
        success, team_id = delete_team(team_id)
        if success:
            return render_template("teams.html", DEL_TEAM_MSG = "Deleted team successfully", teams=get_all_teams_with_user(CurrentUser[0][0]) )
        else:
            return render_template("teams.html", DEL_TEAM_MSG = "Team doesn't Exist", teams=get_all_teams_with_user(CurrentUser[0][0]) )
    else:
        return render_template("home.html")

@app.route('/add_member', methods=['GET', 'POST'], endpoint='add_member')
def add_member():
    if request.method == 'POST':
        player_ucid = request.form['player_id']
        success, msg = add_team_member(player_ucid, CurrentUser[0][0])
        if success:
            print("PLAYER UCID: ", player_ucid)
            return render_template("editTeams.html", ADD_MEMBER_MSG=msg)
        else:
            return render_template("editTeams.html", ADD_MEMBER_MSG=msg)
    else:
        return render_template("home.html")

@app.route('/remove_member', methods=['GET', 'POST'], endpoint='remove_member')
def remove_member():
    if request.method == 'POST':
        player_ucid = request.form['player_id']
        success, msg = remove_team_member(player_ucid)
        if success:
            print("PLAYER UCID: ", player_ucid)
            return render_template("editTeams.html", DELETE_MEMBER_MSG=msg)
        else:
            return render_template("editTeams.html", DELETE_MEMBER_MSG=msg)
    else:
        return render_template("home.html")

@app.route('/editTeams', methods=['GET', 'POST'], endpoint='editTeams')
def editTeams():
    if request.method == 'POST':
        return render_template("editTeams.html")
    else:
        return render_template("home.html")

@app.route('/teams', methods=['GET', 'POST'], endpoint='teams')
def teams():
    if request.method == 'POST':
            return render_template("teams.html", teams=get_all_teams_with_user(CurrentUser[0][0]))
    else:
        return render_template("home.html")

@app.route('/rent', methods=['GET', 'POST'], endpoint='rent')
def rent():
    if request.method == 'POST':
        return render_template("rent.html")
    else:
        return render_template("home.html")

@app.route('/newRental', methods=['GET', 'POST'], endpoint='newRental')
def newRental():
    # userUCID = getUCID()
    userUCID = 1
    paddle = request.form['numberOfPaddles']
    now = datetime.now()
    current_hour = now.strftime("%H")
    hour = int(current_hour)
    current_minute = now.strftime("%M")
    current_time = now.strftime("%H:%M")
    rentTime = request.form['rentTime']
    for i in range(int(rentTime[0])):
        if (hour < 24):
            hour += 1
        else:
            hour == 0
    returnTime = str(hour) + ":" + current_minute
    deposit = 5 * int(paddle[0])
    EType = paddle[1:]
    max_rental_time = rentTime[0]
    buildingName = request.form['BName']
    success, msg = new_rental(userUCID, current_time, returnTime, deposit)
    if success:
        if update_equipment_rental(EType, msg):
            return render_template("rent.html",rentalMsg="Rental Successful, Please pickup your rental at the ESS Office at ENE 134A")
    else:
        return render_template("rent.html",rentalMsg=msg)

@app.route('/cancelRental', methods=['GET', 'POST'], endpoint='cancelRental')
def cancelRental():
    if request.method == 'POST':
        success, msg = cancel_rental(CurrentUser[0][0])
        if success:
            return render_template("rent.html", rentalMsg=msg)
        else:
            return render_template("rent.html", rentalMsg=msg)

@app.route('/booking', methods=['GET', 'POST'], endpoint='booking')
def booking():
    if request.method == 'POST':
        return render_template("booking.html")
    else:
        return render_template("home.html")

@app.route('/book_spot', methods=['GET', 'POST'], endpoint='book_spot')
def book_spot():
    if request.method == 'POST':
        time_slot = request.form['time_slot']
        table_ID = request.form['table_ID']
        ucid = request.form['ucid']
        schedule_ID = request.form['schedule_ID']
        success, msg = add_time_slot(time_slot, ucid, table_ID, schedule_ID)
        if success:
            print("Time Slot: ", time_slot, "UCID: ", ucid, "Table ID: ", table_ID)
            return render_template("booking.html", msg = msg)
        else:
            return render_template("booking.html", msg = msg)
    else:
        return render_template("home.html")

@app.route('/delete_spot', methods=['GET', 'POST'], endpoint='delete_spot')
def delete_spot():
    if request.method == 'POST':
        time_slot = request.form['time_slot']
        table_ID = request.form['table_ID']
        ucid = request.form['ucid']
        schedule_ID = request.form['schedule_ID']
        success, msg = remove_time_slot(time_slot, ucid, table_ID, schedule_ID)
        if success:
            print("Time Slot: ", time_slot, "UCID: ", ucid, "Table ID: ", table_ID, "Schedule ID: " , schedule_ID)
            return render_template("booking.html", msg1 = msg)
        else:
            return render_template("booking.html", msg1 = msg)
    else:
        return render_template("home.html")
        
@app.route('/leaderBoards', methods=['GET', 'POST'], endpoint='leaderBoards')
def leaderBoards():
    if request.method == 'POST':
        totalMatches = []
        getAllTeamInfoResult, currentUserTeamsID = getUserTeamsID(CurrentUser[0][0])
        if getAllTeamInfoResult:
            displayLeaderboardName = ''
            displayScoreAndTime = "*"
            for x in currentUserTeamsID:
                getUserLeaderboardsResult, userLeaderboards = getUserTeamsLeaderBoard(x[0])
                print(userLeaderboards)
                if getUserLeaderboardsResult:
                    for x in userLeaderboards:
                        matches = getMatches(x[1])
                        leaderBoardMatches = 0
                        displayLeaderboardName += matches[len(totalMatches)][0] + "!"
                        for match in matches:
                            leaderBoardMatches += 1
                            displayScoreAndTime += "Scores for the game are: " + str(match[2]) + " for " + str(x[3]) + " and " + str(match[3]) + " for the enemy team. Time the match was played: " + match[4] + "*"
                        totalMatches.append(leaderBoardMatches)
                        displayScoreAndTime += "!"
            return render_template("leaderboards.html", displayLeaderboardName = displayLeaderboardName, displayScoreAndTime = displayScoreAndTime, 
            totalMatches = totalMatches)
        else:
            return render_template("leaderboards.html", NO_TEAM_MESSAGE = "You are not in any leaderboard")
    else:
        return render_template("teams.html")
@app.route('/adminDashboard', methods=['GET', 'POST'], endpoint='adminDashboard')
def adminDashboard():
    if request.method == 'POST':
        return render_template("adminDashboard.html")
    else:
        return render_template("home.html")

@app.route('/addLeaderboard', methods=['GET', 'POST'], endpoint='addLeaderboard')
def addLeaderboard():
    if request.method == 'POST':
        existingLeaderboardsResult, existingLeaderboards = getAllLeaderboards()
        newLeaderboard = request.form['LName']
        leaderboardEventName = request.form['EName']
        buildingName = request.form['BName']
        if existingLeaderboardsResult:
            for x in existingLeaderboards:
                if newLeaderboard == x[0]:
                    return render_template("adminDashboard.html", ADD_LEADERBOARD_MESSAGE = "Leaderboard name already exists")
        else:
            new_leaderboard(newLeaderboard, leaderboardEventName, buildingName)
            return render_template("adminDashboard.html", ADD_LEADERBOARD_MESSAGE = "New leaderboard created")
    else:
        return render_template("adminDashboard.html")

@app.route('/addGamesToLeaderboard', methods=['GET', 'POST'], endpoint='addGamesToLeaderboard')
def addGamesToLeaderboard():
    if request.method == 'POST':
        existingLeaderboardsResult, existingLeaderboards = getAllLeaderboards()
        leaderboardEntered = request.form['LName']
        scoreONE = request.form['scoreONE']
        scoreTWO = request.form['scoreTWO']
        matchDate = request.form['matchDATE']
        if existingLeaderboardsResult:
            for x in existingLeaderboards:
                if leaderboardEntered == x[0]:
                    new_Game(leaderboardEntered, scoreONE, scoreTWO, matchDate)
                    return render_template("adminDashboard.html", ADD_GAME_MESSAGE = "Game added to leaderboard")
                else:
                    return render_template("adminDashboard.html", ADD_GAME_MESSAGE = "Leaderboard doesn't exist")
        else:
            return render_template("adminDashboard.html", ADD_GAME_MESSAGE = "Leaderboard doesn't exist")
    else:
        return render_template("adminDashboard.html")

@app.route('/deleteLeaderboard', methods=['GET', 'POST'], endpoint='deleteLeaderboard')
def deleteLeaderboard():
    if request.method == 'POST':
        leaderboardToDelete = request.form['LName']
        existingLeaderboardsResult, existingLeaderboards = getAllLeaderboards()
        if existingLeaderboardsResult:
            for i in existingLeaderboards:
                if leaderboardToDelete == i[0]:
                    delete_leaderboard(leaderboardToDelete)
                    gamesToDelete = getMatches(leaderboardToDelete)
                    if gamesToDelete != None:
                        for j in gamesToDelete:
                            cancel_Game(j[1])
                        foundTeams, teamsToBeChanged = getTeamFromLeaderboard(leaderboardToDelete)
                        if foundTeams:
                            for k in teamsToBeChanged:
                                editTeamLName(leaderboardToDelete)
                        return render_template("adminDashboard.html", DELETE_GAME_MESSAGE = "Leaderboard has been deleted")
                    else:
                        return render_template("adminDashboard.html", DELETE_GAME_MESSAGE = "Leaderboard has been deleted but no games found in leaderboard")
                else:
                    return render_template("adminDashboard.html", DELETE_GAME_MESSAGE = "Leaderboard doesn't exist")
        else:
            return render_template("adminDashboard.html", DELETE_GAME_MESSAGE = "Leaderboard doesn't exist")
    else:
        return render_template("home.html")

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)