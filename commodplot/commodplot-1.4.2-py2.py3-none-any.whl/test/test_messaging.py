import plotly.graph_objects as go
import pytest

from commodplot import messaging


@pytest.mark.skip()
def test_compose_and_send_report():
    fig = go.Figure(
        data=[go.Bar(x=[1, 2, 3], y=[1, 3, 2])],
        layout=go.Layout(
            title=go.layout.Title(text="A Figure Specified By A Graph Object")
        ),
    )

    subject = "test_email"
    content = """
        <html>
            <body>
                <h1 style="text-align: center;">Simple Data Report</h1>
                <p>Here could be a short description of the data.</p>
                <p><img src="cid:0"></p>
            </body>
        </html>'
        """

    img = fig.to_image(width=1200, height=350, engine="kaleido")
    images = {"0": img}
    sender = "testcommodplot@mailinator.com"
    messaging.compose_and_send_report(
        subject=subject,
        content=content,
        images=images,
        sender_email=sender,
        receiver_email=sender,
    )


@pytest.mark.skip()
def test_compose_jinja_report():
    fig = go.Figure(
        data=[go.Bar(x=[1, 2, 3], y=[1, 3, 2])],
        layout=go.Layout(
            title=go.layout.Title(text="A Figure Specified By A Graph Object")
        ),
    )

    data = {"name": "test", "fig1": fig}

    subject = "test_email"
    sender = "testcommodplot@mailinator.com"
    messaging.compose_and_send_jinja_report(
        subject=subject,
        data=data,
        template="test_report.html",
        package_loader_name="commodplot",
        sender_email=sender,
        receiver_email=sender,
    )
