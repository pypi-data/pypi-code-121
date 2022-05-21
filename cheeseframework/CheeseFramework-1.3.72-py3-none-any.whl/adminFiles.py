class AdminFiles:
	def sayHello():
		print('hello')

	admin_files_index_html = """<html lang="cs">
<head>
    <meta charset='utf-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/admin/files/styles/style.css">
    <link rel="icon" href="/admin/files/web/favicon.ico" type="image/x-icon">
    <title>CHAdmin</title>
</head>
<body>
    <h1>CHAdmin</h1>
    <label id="release"></label>
    <div id="control" class="controlDiv">
        <button onclick="shutdown()" id="shutdownButt" style="background-color:#ff0000">Shutdown</button>
        <button onclick="restart()" id="restartButt">Restart server</button>
        <button onclick="saveChanges()" id="saveButt">Save configuration</button>
        <button onclick="pullChanges()" id="updateButt">Get new version from git</button>
    </div>
    <table id="settingsTable"></table>
    <label id="logDesc"></label><br><br>
    <div id="log" class="logDiv">
        <table id="logTable" class="logTable"></table>
    </div>

    <script src="https://kubaboi.github.io/CheeseFramework/public/scripts/cookies.js"></script>
    <script src="https://kubaboi.github.io/CheeseFramework/public/scripts/communication.js"></script>
    <script src="https://kubaboi.github.io/CheeseFramework/public/scripts/time.js"></script>
    
    <script src="admin/files/scripts/settings.js"></script>
    <script src="admin/files/scripts/log.js"></script>
    <script src="admin/files/scripts/controll.js"></script>
    <script src="admin/files/scripts/release.js"></script>
    <script>
        buildSettingTable();
        buildLogTable();
        setRelease();
    </script>
</body>
</html>"""

	admin_files_allLogs_html = """<html lang="cs">
<html>
<head>
    <meta charset='utf-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/admin/files/styles/style.css">
    <link rel="icon" href="/admin/files/web/favicon.ico" type="image/x-icon">
    <title>Cheese logs</title>
</head>
<body>
    <h1>Cheese Logs</h1>
    <button onclick="location='/admin'">CHAdmin</button><br><br>
    <table>
        TABLE
    </table>
    <script>
        dontRunScript = true;
    </script>
    <script src="https://kubaboi.github.io/CheeseFramework/public/scripts/communication.js"></script>
    <script src="https://kubaboi.github.io/CheeseFramework/public/scripts/time.js"></script>
    <script src="/admin/files/scripts/log.js"></script>
</body>
</html>"""

	admin_files_activeLog_html = """<html lang="cs">
<html>
<head>
    <meta charset='utf-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/admin/files/styles/style.css">
    <link rel="icon" href="/admin/files/web/favicon.ico" type="image/x-icon">
    <title>Cheese log</title>
</head>
<body>
    <button onclick="location='/admin/logs'">All logs</button>
    <button onclick="location='/admin'">CHAdmin</button>
    <h1 id="logDesc">Cheese log - </h1>
    <div id="log" class="logDivBig">
        <table id="logTable" class="logTable"></table>
    </div>

    <script src="https://kubaboi.github.io/CheeseFramework/public/scripts/cookies.js"></script>
    <script src="https://kubaboi.github.io/CheeseFramework/public/scripts/communication.js"></script>
    <script src="https://kubaboi.github.io/CheeseFramework/public/scripts/time.js"></script>

    <script>//dontRunScript = true;</script>
    <script src="/admin/files/scripts/log.js"></script>
</body>
</html>"""

	admin_files_scripts_settings_js = """
async function buildSettingTable() {
    response = await callEndpoint("GET", "/admin/getSettings");
    if (!response.ERROR) {
        for (const key in response) {
            if (response.hasOwnProperty(key)) {
                addSetting(key, response[key]);
            }
        }
        document.title = "CHAdmin - " + response.name;
    }
}

function addSetting(setting, value) {
    var table = document.querySelector("#settingsTable");

    var row = document.createElement("tr");
    var nameColumn = document.createElement("td");
    var valueColumn = document.createElement("td");

    nameColumn.innerHTML = setting;
    if (setting == "dbPassword")
        valueColumn.innerHTML = "<input type='password' value='" + value + "'>";
    else
        valueColumn.innerHTML = "<input type='text' value='" + value + "'>";
    
    row.appendChild(nameColumn);
    row.appendChild(valueColumn);
    table.appendChild(row);
}"""

	admin_files_scripts_release_js = """function getRelease() {
    url = "/admin/cheeseRelease";
    
    return new Promise(resolve => {
        sendGet(url, debug, function(response){
            resolve(response);
        });  
    });
}

async function setRelease() {
    var lbl = document.getElementById("release");

    var response = await getRelease();
    if (!response.ERROR) {
        lbl.innerHTML = "Cheese Framework (v" + response.RELEASE + ")"
    }
}"""

	admin_files_scripts_log_js = """debug = false;

setTitle();
async function setTitle() {
    response = await callEndpoint(`GET`, `/admin/getSettings`);
    if (!response.ERROR) {
        document.title = `Cheese logs - ${response.name}`;
    }
}

function getActiveLog() {
    url = `/admin/getActiveLog`;
    
    return new Promise(resolve => {
        sendGet(url, debug, function(response){
            resolve(response);
        });  
    });
}

function deleteLog(log) {
    url = `/admin/deleteLog?log=${log}`;
    
    return new Promise(resolve => {
        sendGet(url, debug, function(response){
            resolve(response);
        });  
    });
}

async function buildLogTable() {
    response = await getActiveLog();
    if (!response.ERROR) {
        var table = document.querySelector(`#logTable`);
        table.innerHTML = ``;
        table.innerHTML = response.RESPONSE.LOG;

        var label = document.querySelector(`#logDesc`);
        if (label.tagName == `LABEL`) {
            label.innerHTML = `<button onclick=\"location='/admin/logs'\">All logs</button>	&nbsp;
            <button onclick=\"location='/admin/files/activeLog.html'\">Full log</button>`;
        }
        else {
            label.innerHTML = `Cheese log - ${response.RESPONSE.LOG_DESC} - <label class='okGreen'>ACTIVE</label>`;
        }
    }
}

if (typeof dontRunScript == `undefined`) updateInterval = setInterval(update, 1000);
var oldC = 0;
var oldScrollHeight = 0;
function update() {
    buildLogTable();
    element = document.getElementById(`log`);
    var a = element.scrollTop;
    var b = element.scrollHeight - element.clientHeight;
    if (oldC < 500 && oldScrollHeight != element.scrollHeight) {
        element.scrollTop = b;
    }

    oldScrollHeight = element.scrollHeight;
    oldC = b - a;
}

async function deleteFile(log) {
    response = await deleteLog(log);
    if (!response.ERROR) {
        alert(`Log ${log} was deleted`);
        location.reload();
    }
    else {
        alert(`An error occurred: ${response.ERROR}`);
    }
}"""

	admin_files_scripts_controll_js = """function apiFunction(url) {    
    return new Promise(resolve => {
        sendGet(url, debug, function(response){
            resolve(response);
        });  
    });
}

function shutdown() {
    if (confirm(`Do you really want to turn off the server?`)) {
        document.getElementById(`shutdownButt`).disabled = true;
        document.getElementById(`restartButt`).disabled = true;
        apiFunction(`/admin/shutdown`);
    }
}

function restart() {
    if (confirm(`Do you really want to restart your application?\nIt will took about 20 seconds.`)) {
        clearInterval(updateInterval);
        document.getElementById(`restartButt`).disabled = true;
        apiFunction(`/admin/restart`);
        textInterval = setInterval(function() { loadingText(`Waiting for response from server`); }, 200);
        setTimeout(buildTableWithDelay, 500);
    }
}

async function buildTableWithDelay() {
    response = await getActiveLog();
    if (!response.ERROR) {
        if (response.RESPONSE.LOG.includes(`<label class='warning'>Restart will start in 5 seconds</label></td></tr>\n`)) {
            clearInterval(textInterval);

            element = document.getElementById(`log`);
            var b = element.scrollHeight - element.clientHeight;
            element.scrollTop = b;
            
            prepareRestart();
            setTimeout(checkLife, 15000);
        }
        else {
            setTimeout(buildTableWithDelay, 500);
        }
    }
}

function prepareRestart() {
    textInterval = setInterval(function() { loadingText(`Server is restarting`); }, 200);
}
var dots = 0;
function loadingText(text) {
    for (let i = 0; i < dots; i++) {
        text += `.`;
    }
    dots += 1;
    if (dots >= 10) dots = 0;
    document.querySelector(`#logTable`).innerHTML = text;
}

async function saveChanges() {
    var configString = `{`;
    var confTable = document.getElementById(`settingsTable`);
    var rows = confTable.querySelectorAll(`tr`);
    
    for (var i = 0; i < rows.length; i++) {
        var tds = rows[i].querySelectorAll(`td`);
        var inp = tds[1].querySelector(`input`);
        var val = validateValue(inp.value);
        configString += `\"${tds[0].innerHTML}\": ${val},`; 
    }
    configString = configString.substring(0, configString.length - 1);
    configString += `}`;

    setCookie(`config`, configString, 0.01)
    var response = await callEndpoint(`GET`, `/admin/changeConfiguration`);
    if (response.ERROR != null) {
        alert(`ERROR: ` + response.ERROR);
    }

}

function validateValue(value) {
    var int = parseInt(value);
    if (!isNaN(int) && int.toString().length == value.length) return int;
    else if (value == `false`) return false;
    else if (value == `true`) return true;
    return `"${value}"`;
}

async function checkLife() {
    fetch(`/alive`)
    .then(
        (response) => {
            updateInterval = setInterval(update, 1000);
            clearInterval(textInterval);
            document.getElementById(`restartButt`).disabled = false;
            alert(`Server has been restarted :)`);
        },
        (err) => {
            setTimeout(checkLife, 500);
        }
    );
}

async function pullChanges() {
    var response = await apiFunction(`/admin/update`);
    if (response.ERROR) {
        alert(response.ERROR);
    }
}"""

	admin_files_styles_style_css = """body {
    color: white;
    background-color: #2b2b2b;
    font-family: Arial, Helvetica, sans-serif;
}

a{color:#4542fc;}
a:visited{color:#9c2b2b;}

.header { font-weight: bold; }
.okBlue { color: #4542fc; }
.okCyan { color: #0ff; }
.okGreen { color: #0f0; }
.warning { color: #ff0; }
.fail { color: #f00; }
.bold { font-weight: bold; }
.underLine { text-decoration: underline; }

.logDiv {
    position: fixed;
    width: 50%;
    right: 0%;
    top: 5%;
    height: 94%;
    overflow-y: scroll;
    overflow-x: hidden;
    scroll-behavior: smooth;
    background-color: black;
    border: 2px solid #fff;
}

.logDivBig {
    position: fixed;
    width: 100%;
    left: 0%;
    top: 9%;
    height: 90%;
    overflow-y: scroll;
    overflow-x: hidden;
    scroll-behavior: smooth;
    background-color: black;
    border: 2px solid #fff;
}

.logTable {
    word-wrap: break-word;
    word-break: break-all;
    table-layout: fixed;
}

#logDesc {
    position: fixed;
    width: 50%;
    right: 0%;
    top: 15px;
}

td, th {
    min-width: 180px;
    vertical-align: top;
    text-align: left;
}

.controlDiv {
    padding: 10px;
}"""

