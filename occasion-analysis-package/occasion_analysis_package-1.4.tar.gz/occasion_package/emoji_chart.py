import pandas as pd
# For creating frequency chart
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import plotly
# For getting emoji count
import advertools as adv


def create_emoji_chart(import_file_path):
    """
    The function will create Emoji Frequency Chart.

    Parameters:
        import_file_path (string): File Path to export the data.
                                   Please enter file path with double backslash "\\\\" with file name.
                                   There should be two columns in the file: "use_case", "all_text".
                                   File name should be .csv extension.
    """
    df = pd.read_csv(import_file_path, low_memory=False, encoding="utf-8-sig")
    df = df[["use_case", "all_text"]]
    print("File Read!")
    text = df["all_text"]

    ##Getting Emoji Summary
    emoji_summary = adv.extract_emoji(text)
    emoji_counts = emoji_summary["top_emoji"]

    emoji_counter = pd.DataFrame(emoji_counts, columns=["Emoji", "Count"])
    emoji_counter.set_index("Emoji")
    max_value = emoji_counter._get_value(0, "Count")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            y=emoji_counter["Emoji"],
            x=emoji_counter["Count"],
            name="Emoji Counts",
            marker_color="white",
            orientation="h",
            text=emoji_counter["Emoji"],
            textposition="top center",
            mode="markers+text",
            textfont=dict(size=25),
        )
    )

    fig.update_yaxes(visible=False, range=[50, 0])
    fig.update_xaxes(
        title="Number of Times Used Range 50-500", range=[50, 500]
    )  # 1000 instead of using max_value

    fig.update_layout(
        template="simple_white",
        # height=len(emoji_counter)*0.5, width = 1500
    )
    fig.show()
