import matplotlib.pyplot as plt


def plot_gradient_norms(model, variables=None, ax=None, ax2=None):
    if ax is None:
        plt.figure(figsize=(10, 4))
        ax = plt.gca()

    for name, grad_norms in model.log_gradient_norms.items():
        if name in variables:
            ax.plot(grad_norms, label=name, alpha=0.5)

    ax.set_xlabel("iters")
    ax.set_ylabel("gradient norm")
    ax.set_yscale("log")
    ax.legend(loc="upper left")
    ax.set_title("Gradient norms during SVI")

    if ax2 is None:
        ax2 = ax.twinx()

    for name, grad_norms in model.log_learning_rates.items():
        if name in variables:
            ax2.plot(grad_norms, label="lr" + name, alpha=0.5)

    ax2.set_ylabel("lr")
    ax2.set_yscale("log")
    ax2.legend(loc="upper right")

    return ax, ax2
