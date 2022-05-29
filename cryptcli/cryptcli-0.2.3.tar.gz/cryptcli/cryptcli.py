import typer
from typing import List, Optional
from rich.console import Console
from rich.table import Table
import requests, json, time
import plotext as pltx
import inquirer
app = typer.Typer()
console = Console()

def getResp(crypto: str):
    url = f"https://api.coincap.io/v2/assets/{crypto}"
    console.print(f"Querying {url}...")
    resp = requests.get(url)
    return resp

def secFormat(seconds: int):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)

@app.command()
def info(crypto: str):
    """
    provides basic info for a specific crypto
    """
    print()
    resp = getResp(crypto)
    # console.print(resp)
    if (resp.status_code != 200):
        console.print(f"[bold red blink]Error: reponse code {resp.status_code}...[/ bold red blink]")
        return
    text = resp.text
    data = json.loads(text)['data']
    # console.print(data)

    table = Table(
        title = f"-== {crypto} ({data['symbol']}) ==-",
        title_justify = "left",
        title_style = "bold orange3",
    )
    table.add_column("Rank")
    table.add_column("Price")
    table.add_column("Supply")
    table.add_column("Down or Up (24hr)")
    table.add_row(
        str(data['rank']),
        f"${data['priceUsd']}",
        str(data['supply']),
        f"[red]{data['changePercent24Hr']}[/ red]" if data['changePercent24Hr'][0] == "-" else f"[green]{data['changePercent24Hr']}[/ green]",
    )
    console.print(table)
    print()

@app.command()
def price(crypto: str):
    """
    displays the price of a specific crypto
    """
    print()
    resp = getResp(crypto)
    # console.print(resp)
    if (resp.status_code != 200):
        console.print(f"[bold red blink]Error: reponse code {resp.status_code}...[/ bold red blink]")
        return
    text = resp.text
    data = json.loads(text)['data']
    console.print(f"[bold dim]The price of [green italic]{crypto}[/ green italic] is [yellow italic]${data['priceUsd']}[/ yellow italic].[/ bold dim]")
    print()

@app.command()
def list(num: Optional[int] = 10):
    """
    lists out the top crypto prices
    """
    resp = requests.get("https://api.coincap.io/v2/assets")
    if (resp.status_code != 200):
        console.print(f"[bold red blink]Error: reponse code {resp.status_code}...[/ bold red blink]")
        return
    text = resp.text
    data = json.loads(text)['data']

    for idx, crypto in enumerate(data):
        if (idx >= num):
            break
        console.print(f"({idx + 1}) {crypto['id']} : ${crypto['priceUsd']}")
        time.sleep(0.01)

@app.command()
def hist(cryptos: List[str]):
    """
    displays pricing graph for a certain interval
    """
    if (len(cryptos) > 2):
        console.print("[red bold]At this time, you can only graph two cryptos at a time...[/ red bold]")
        return
    questions = [
      inquirer.List('data',
                    message="Range",
                    choices=['1D', '1W', '1M', '6M', '1Y'],
                ),
    ]
    interval = inquirer.prompt(questions)

    convertedRange =  "d1"
    match interval['data']:
        case "1Y":
            convertedRange = "d1"
        case "1D":
            convertedRange = "m1"
        case "1M":
            convertedRange = "h1"
        case "1W":
            convertedRange = "m15"
        case "6M":
            convertedRange = "h6"
    colors = [["green","red+"],["yellow","blue"]]
    for idx, crypto in enumerate(cryptos):
        resp = requests.get(f"https://api.coincap.io/v2/assets/{crypto}/history?interval={convertedRange}")
        if (resp.status_code != 200):
            console.print(f"[bold red blink]Error: reponse code {resp.status_code}...[/ bold red blink]")
            return
        text = resp.text
        data = json.loads(text)['data']

        prices = []
        for instance in data:
            prices.append(float(instance['priceUsd']))
        price_up = (prices[-1] - prices[0]) > 0 
        pltx.plot(prices, label=f"price of {crypto}", yside = "left" if idx == 0 else "right", color = colors[idx][0] if price_up else colors[idx][1])
    
    pltx.canvas_color(236)
    pltx.axes_color(236)
    pltx.ticks_color("white")
    pltx.ticks_style("bold")
    pltx.xlabel(f"Time ({interval['data']})")
    pltx.xfrequency(0)
    pltx.ylabel("Price (USD)")
    pltTitle = f"{interval['data']} price range of"
    for idx, crypto in enumerate(cryptos):
        if idx < len(cryptos) - 1:
            pltTitle += f" {crypto},"
        else:
            pltTitle += f" and {crypto}."
    pltx.title(pltTitle)
    pltx.show()

@app.command()
def live(crypto: str):
    priceVals = []
    timeCount = 0
    upperLim: float = 0
    lowerLim: float = 0
    startTime = time.time()
    while True:
        resp = requests.get(f"https://api.coincap.io/v2/assets/{crypto}")
        if (resp.status_code != 200):
            #console.print(f"[bold red blink]Error: reponse code {resp.status_code}...[/ bold red blink]")
            #return
            priceVals.append(priceVals[len(priceVals) - 1]) # append the prev value
        else:
            text = resp.text
            data = json.loads(text)['data']
            priceVals.append(float(data['priceUsd']))
            if len(priceVals) == 1:
                lowerLim = float(data['priceUsd'])
                upperLim = lowerLim + 0.00001
            if float(data['priceUsd']) > upperLim:
                upperLim = float(data['priceUsd'])
            elif float(data['priceUsd']) < lowerLim:
                lowerLim = float(data['priceUsd'])

        pltx.clt()
        pltx.cld()
        
        pltx.canvas_color(236) 
        pltx.axes_color(236)
        pltx.ticks_color("white")
        pltx.ticks_style("bold")
        pltx.xlabel(f"Time elepsed: {round(time.time() - startTime, 1)}s")
        pltx.xlabel(f"Time elapsed: {secFormat(round(time.time() - startTime, 0))}")
        pltx.ylabel("Price (USD)")
        percentGain = round((priceVals[len(priceVals) - 1] - priceVals[0]) / priceVals[0] * 100, 2)
        pltx.title(f"Live price chart of {crypto} : {percentGain}%")

        pltx.ylim(upperLim, lowerLim)
        pltx.xlim(0 if len(priceVals) == 1 else 1, len(priceVals))
        pltx.xfrequency(0)
        pltx.plot(priceVals, label=f"Price of {crypto}", color = "red" if percentGain < 0 else "green")
        pltx.show()
        pltx.sleep(1)
        timeCount += 1


if __name__ == "__main__":
    app()
