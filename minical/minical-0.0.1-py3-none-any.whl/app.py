"""
The Flask app
"""
import os

from flask import Flask, request, render_template, redirect, url_for

from . import errors
from . import util
from . import whats_next

app = Flask(__name__)

@app.route("/cal", methods=["GET"])
def page_main():
    """redirect to main page"""
    return redirect(url_for("page_events"))

@app.route("/cal/events", methods=["GET"])
def page_events():
    """main page"""
    events = whats_next.load_events()
    return render_template("events.html", events=events)

@app.route("/cal/new_event", methods=["GET"])
def page_new_event():
    """page for making new event"""
    return render_template("new_event.html", event_template=get_event_template())

def add_or_overwrite_event(try_again_template, orig_event_name=None):
    """Make a new file with event text, or overwrite an existing one. Uses request"""
    assert try_again_template in ["new_event.html", "edit_event.html"]
    event_text = request.form["event_text"].strip()
    error_message = None
    print("Event text is:", event_text)
    event = util.parse_event_text(event_text)
    print("Parsed event is:", event)

    try:
        util.validate_event(event)
        new_path = os.path.join(util.EVENTS_DIR, event["name"])

        if "edit" in try_again_template:
            should_rename = False
            if orig_event_name and orig_event_name != event["name"]:
                should_rename = True
                if os.path.exists(new_path):
                    raise errors.BadEventError(
                        "New event name exists. Please give it a unique name.")

        if "new" in try_again_template:
            if os.path.exists(new_path):
                raise errors.BadEventError("That event name exists. Please give it a unique name.")

    except errors.BadEventError as e:
        error_message = f"Invalid event: {str(e)}"
    except Exception as e: # pylint: disable=broad-except
        error_message = f"Something unexpected went wrong: {str(e)}. " \
            "You might have mistyped some fieldnames or semicolons"
    else:
        if "new" in try_again_template:
            with open(new_path, "w", encoding="utf8") as new_f_out:
                new_f_out.write(event_text)

        if "edit" in try_again_template:
            # Will write to old path whether renaming or not
            old_path = os.path.join(util.EVENTS_DIR, orig_event_name)
            with open(old_path, "w", encoding="utf8") as edit_f_out:
                edit_f_out.write(event_text)
            if should_rename:
                os.rename(old_path, new_path)

        return redirect(url_for("page_events", success=1))

    if error_message:
        print(error_message)
        return render_template(
            try_again_template,
            event=event,
            event_template=get_event_template(),
            error_message=error_message,
            previous_text=event_text), 400


@app.route("/cal/events", methods=["POST"])
def add_event():
    """handle POST submission of new event"""
    return add_or_overwrite_event(orig_event_name=None, try_again_template="new_event.html")


@app.route("/cal/edit_event/<name>", methods=["GET"])
def page_edit_event(name):
    """show page for editing an event"""
    event = util.load_event_from_file(name)
    return render_template("edit_event.html", event=event, event_template=get_event_template())

@app.route("/cal/edit_event/<name>", methods=["POST"])
def edit_event(name):
    """handle POST submission of edited event"""
    return add_or_overwrite_event(orig_event_name=name, try_again_template="edit_event.html")

@app.route("/cal/delete_event/<name>", methods=["POST"])
def delete_event(name):
    """delete event"""
    path_to_remove = os.path.join(util.EVENTS_DIR, name)
    assert os.path.isfile(path_to_remove)
    os.remove(path_to_remove)
    return redirect(url_for("page_events", success=1))

def get_event_template():
    """Get an event template to show to the user as an example"""
    template_path = os.path.join(os.path.dirname(__file__), "event_template.txt")
    with open(template_path, encoding="utf8") as f_in:
        event_template = f_in.read().strip()
    return event_template

def main():
    """Start a webserver"""
    port = int(os.environ["MINICAL_PORT"])
    # First arg is passed as the program's name,
    # see docs like https://docs.python.org/2/library/os.html#os.execl
    # (The Python 2 docs seem clearer about this than the Python 3 docs)
    #os.execlp("gunicorn", "gunicorn", "-n", "minical", "-b", f"127.0.0.1:{port}", "app:app")

    # Want to try gunicorn, but one step at a time, packaging is very confusing at the moment
    app.run("127.0.0.1", port=port)

if __name__ == "__main__":
    main()
