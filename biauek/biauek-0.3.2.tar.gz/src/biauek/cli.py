import asyncio
import pathlib
import argparse
import getpass
from . import *

def _add_post_parsers(post_parser):
    post_parser.add_argument("body", nargs="?", default="", type=str, metavar="POST_CONTENT", help="post content")
    post_file_or_url_parser = post_parser.add_mutually_exclusive_group()

    post_file_or_url_parser.add_argument("-f", "--file", type=pathlib.Path, metavar="FILE", help="path to a file to attach")
    post_file_or_url_parser.add_argument("-u", "--url", type=str, metavar="URL", help="url to embed")
    post_parser.add_argument("-r", "--rename", type=str, metavar="FILENAME", help="upload file with a different name")

def _validate_post_args(parser, args):
    if args.rename and args.url:
        parser.error("argument -r/--rename: not allowed with argument -u/--url")

    if args.rename and not args.file:
        parser.error("argument -r/--rename: requires argument -f/--file")

async def _get_attachment(session, args):
    if args.file is not None:
        return await session.attach_file(args.file, rename=args.rename)
    elif args.url is not None:
        return await session.attach_url(args.url)
    else:
        return None

async def _main():
    # root parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--user-agent", type=str, metavar="USER_AGENT", help="use different user agent for requests")
    
    login_parser = parser.add_mutually_exclusive_group(required=True)
    login_parser.add_argument("-l", "--login", type=str, metavar="LOGIN_COOKIE", help="a valid login cookie")
    login_parser.add_argument("-i", "--ask", action="store_true", help="enter login cookie interactively")

    # subcommand parsers
    subparsers = parser.add_subparsers(dest="subcommand")
    post_parser = subparsers.add_parser("post", help="publish post")
    comment_parser = subparsers.add_parser("comment", help="publish comment")
    observe_parser = subparsers.add_parser("observe", help="observe user")
    unobserve_parser = subparsers.add_parser("unobserve", help="unobserve user")
    edit_parser = subparsers.add_parser("edit", help="edit post or comment")
    delete_parser = subparsers.add_parser("delete", help="delete post or comment")
    dump_parser = subparsers.add_parser("dump", help="dump mode, takes file paths as positional arguments")

    # post parser
    _add_post_parsers(post_parser)

    # comment parser
    comment_parser.add_argument("post_id", type=str, metavar="POST_ID", help="id of the post to comment")
    _add_post_parsers(comment_parser)

    # observe parser
    observe_parser.add_argument("username", type=str, metavar="USERNAME", help="username to observe")

    # unobserve parser
    unobserve_parser.add_argument("username", type=str, metavar="USERNAME", help="username to unobserve")

    # edit parser
    edit_subparsers = edit_parser.add_subparsers(dest="edit_subcommand", required=True)

    edit_post_parser = edit_subparsers.add_parser("post")
    edit_post_parser.add_argument("post_id", type=str, metavar="POST_ID", help="id of the post to edit")
    _add_post_parsers(edit_post_parser)

    edit_comment_parser = edit_subparsers.add_parser("comment")
    edit_comment_parser.add_argument("comment_id", type=str, metavar="COMMENT_ID", help="id of the comment to edit")
    _add_post_parsers(edit_comment_parser)

    # delete parser
    delete_subparsers = delete_parser.add_subparsers(dest="delete_subcommand", required=True)

    delete_post_parser = delete_subparsers.add_parser("post")
    delete_post_parser.add_argument("post_id", type=str, metavar="POST_ID", help="id of the post to delete")

    delete_comment_parser = delete_subparsers.add_parser("comment")
    delete_comment_parser.add_argument("comment_id", type=str, metavar="COMMENT_ID", help="id of the comment to delete")

    # dump parser
    dump_parser.add_argument("files", type=pathlib.Path, nargs="+", metavar="FILES", help="files to be posted all at once")
    dump_parser.add_argument("-r", "--rename", type=str, metavar="FILENAME", help="upload all files with this name")

    args = parser.parse_args()

    login = args.login

    if args.ask:
        login = getpass.getpass(prompt="enter login cookie: ")

    try:
        if args.subcommand == "post":
            _validate_post_args(post_parser, args)

            async with Session(login, user_agent=args.user_agent) as session:
                attachment = await _get_attachment(session, args)

                await session.post(args.body, attachment_id=attachment)

        elif args.subcommand == "comment":
            _validate_post_args(post_parser, args)

            async with Session(login, user_agent=args.user_agent) as session:
                attachment = await _get_attachment(session, args)

                await session.comment(args.post_id, args.body, attachment_id=attachment)

        elif args.subcommand == "observe":
            async with Session(login, user_agent=args.user_agent) as session:
                await session.observe(args.username)

        elif args.subcommand == "unobserve":
            async with Session(login, user_agent=args.user_agent) as session:
                await session.unobserve(args.username)

        elif args.subcommand == "edit":
            if args.edit_subcommand == "post":
                _validate_post_args(post_parser, args)

                async with Session(login, user_agent=args.user_agent) as session:
                    attachment = await _get_attachment(session, args)

                    await session.edit_post(args.post_id, args.body, attachment_id=attachment)

            elif args.edit_subcommand == "comment":
                _validate_post_args(post_parser, args)

                async with Session(login, user_agent=args.user_agent) as session:
                    attachment = await _get_attachment(session, args)
                    
                    await session.edit_comment(args.comment_id, args.body, attachment_id=attachment)

            else:
                edit_parser.print_help()

        elif args.subcommand == "delete":
            if args.delete_subcommand == "post":
                async with Session(login, user_agent=args.user_agent) as session:
                    await session.delete_post(args.post_id)

            elif args.delete_subcommand == "comment":
                async with Session(login, user_agent=args.user_agent) as session:
                    await session.delete_comment(args.comment_id)
                
            else:
                delete_parser.print_help()

        elif args.subcommand == "dump":
            async with Session(login, user_agent=args.user_agent) as session:
                for file in args.files:
                    attachment = await session.attach_file(file, rename=args.rename)
                    await session.post("", attachment_id=attachment)

        else:
            parser.print_help()

    except Exception as exception:
        print(f"exception: {exception}")

def main():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_main())

if __name__ == "__main__":
    main()
