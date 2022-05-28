from fastrestapi import run, request, Post
import bottle
import flask


@Post("/test1")
def test1():
    aaa = request.json.get("aaa")
    print(f"@req json aaa : {aaa}")

    aaa = request.json.get("aaa")
    print(f"@req json aaa : {aaa}")

    return "hi? test1"


if __name__ == "__main__":
    run("localhost", 5000)
