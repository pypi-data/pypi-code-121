from .imports import *

import __main__

@contextlib.contextmanager
def directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)


def log_pid() -> None:
    with open("pid.txt", "w") as f:
        f.write(str(os.getpid()))


def log_config() -> None:
    shutil.copy(__main__.__file__, "config.py")


def log_losses(losses: pd.DataFrame) -> None:
    losses.to_csv("losses.csv", index=False)


def log_weights(model: nn.Module) -> None:
    torch.save(model.state_dict(), "weights.pt")


def log_model(model: nn.Module) -> None:
    torch.save(model, "model.pt")


def plot_losses(losses: pd.DataFrame) -> None:
    fig = px.line(losses, title="Losses over time", log_y=True)
    fig.write_image("plot.png")
    fig.write_html("plot.html")
