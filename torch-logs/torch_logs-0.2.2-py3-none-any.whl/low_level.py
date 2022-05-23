from .imports import *

# todo this should be a class se we can override?


@contextlib.contextmanager
def directory(path: str) -> Iterable[bool]:
    exists_already = os.path.exists(path)
    if not exists_already:
        os.makedirs(path)

    cwd = os.getcwd()
    os.chdir(path)

    try:
        yield exists_already
    finally:
        os.chdir(cwd)


def log_comment(comment: str):
    latest_comment_path = "../latest/comment.txt"
    if os.path.exists("../latest/comment.txt"):
        with open(latest_comment_path, "r") as f:
            assert (
                f.read() != comment
            ), "Comment did not change between runs! Write a new comment or delete the old one."

    with open("comment.txt", "w") as f:
        f.write(comment)


def log_architecture(model: nn.Module):
    with open("architecture.txt", "w") as f:
        f.write(str(model))


def log_pid() -> None:
    with open("pid.txt", "w") as f:
        f.write(str(os.getpid()))


def log_max_memory() -> None:
    with open("max_memory.txt", "w") as f:
        f.write(
            str(torch.cuda.max_memory_allocated())
        )  # todo generalize to multiple devices


def log_last_modified() -> None:
    with open("last_modified.txt", "w") as f:
        f.write(
            datetime.now()
            .isoformat(timespec="seconds")
            .replace(":", "")
            .replace("-", "")
        )


def log_config() -> None:
    shutil.copy(main.__file__, "config.py")


def log_losses(losses: pd.DataFrame) -> None:
    losses.to_csv("losses.csv", index=False)


def log_weights(model: nn.Module) -> None:
    torch.save(model.state_dict(), "weights.pt")


def log_model(model: nn.Module) -> None:
    torch.save(model, "model.pt")


def plot_losses(window_size: int) -> None:
    # todo losses from the .csv file
    losses = pd.read_csv("losses.csv")
    os.makedirs("plots", exist_ok=True)

    images = []

    colors = px.colors.qualitative.Plotly

    for col in losses.columns:
        fig = px.line(
            losses[col],
            title=f"Total weighted objective per iteration (window size {window_size})"
            if col == "objective"
            else f"Average '{col}' loss per iteration (window size {window_size})",
            y=col,
            log_y=True,
            template="plotly_dark",
            color_discrete_sequence=colors[1:] if col == "objective" else colors,
        ).update_layout(showlegend=False, xaxis_title="iteration")
        fig.write_image(f"plots/losses_{col}.png")
        fig.write_html(f"plots/losses_{col}.html")
        images.append(read_image(f"plots/losses_{col}.png"))

    save_image(torch.stack(images) / 255, "losses.png", padding=0, nrow=1)


def plot_scores() -> None:
    scores = pd.read_csv("scores.csv")
    os.makedirs("plots", exist_ok=True)

    images = []

    for col in scores.columns:
        xs = list(range(1, len(scores[col]) + 1))
        fig = (
            px.line(
                scores[col],
                x=xs,
                y=col,
                title=f"'{col}' score per checkpoint",
                log_y=True,
                template="plotly_dark",
            )
            .update_traces(mode="lines+markers")
            .update_layout(showlegend=False, xaxis_title="checkpoint")
            .update_xaxes(tickmode="array", tickvals=xs)
        )

        fig.write_image(f"plots/scores_{col}.png")
        fig.write_html(f"plots/scores_{col}.html")

        images.append(read_image(f"plots/scores_{col}.png"))

    save_image(torch.stack(images) / 255, "scores.png", padding=0, nrow=1)


def log_scores(scores: pd.DataFrame) -> None:
    scores.mean().to_frame().T.to_csv(
        "scores.csv", mode="a", index=False, header=not os.path.exists("scores.csv")
    )


def log_predictions(j: int, preds: torch.Tensor):
    if preds.ndim == 4:
        for k, image in enumerate(preds):
            name = f"{j*preds.shape[0]+k:06d}"
            directory = name[:4]
            os.makedirs(directory, exist_ok=True)
            save_image(image, f"{directory}/{name}.png")


def create_symbolic_link(name: str):
    with directory(".."):
        if os.path.exists("latest"):
            os.unlink("latest")
        os.symlink(name.split("/")[-1], "latest")
