from textwrap import dedent

from .trops import Trops


class TropsInit(Trops):

    def __init__(self, args, other_args):
        super().__init__(args, other_args)

        if other_args:
            msg = f"""\
                # Unsupported argments { ", ".join(other_args)}
                # > trops init --help"""
            print(dedent(msg))
            exit(1)

        if self.args.shell not in ['bash', 'zsh']:
            print("# usage: trops init [bash/zsh]")
            exit(1)

    def _init_zsh(self):

        zsh_lines = f"""\
            autoload -Uz add-zsh-hook
            ontrops() {{
                export TROPS_SID=$(trops gensid)
                if [ "$#" -ne 1 ]; then
                    echo "# upsage: on-trops <env>"
                else
                    export TROPS_ENV=$1
                    if [[ ! $PROMPT =~ "(τ)" ]]; then
                        export PROMPT="(τ)$PROMPT"
                    fi
                    # Pure prompt https://github.com/sindresorhus/pure
                    if [ -z ${{PURE_PROMPT_SYMBOL+x}} ]; then
                        if [[ ! $PURE_PROMPT_SYMBOL =~ "(τ)" ]]; then
                            export PURE_PROMPT_SYMBOL="(τ)❯"
                        fi
                    else
                        if [[ ! $PURE_PROMPT_SYMBOL =~ "(τ)" ]]; then
                            export PURE_PROMPT_SYMBOL="(τ)$PURE_PROMPT_SYMBOL"
                        fi
                    fi
                    _tr_capcmd() {{
                        trops capture-cmd $? $(fc -ln -1 -1)
                    }}
                    add-zsh-hook precmd _tr_capcmd
                fi
            }}

            offtrops() {{
                export PROMPT=${{PROMPT//\(τ\)}}
                export PURE_PROMPT_SYMBOL=${{PURE_PROMPT_SYMBOL//\(τ\)}}
                unset TROPS_ENV TROPS_SID
                add-zsh-hook -D precmd _tr_capcmd
            }}
            """

        return dedent(zsh_lines)

    def _init_bash(self):

        bash_lines = f"""\
            _trops_capcmd () {{
                trops capture-cmd $? $(fc -ln -1 -1)
            }}

            ontrops() {{
                if [ "$#" -ne 1 ]; then
                    echo "# upsage: on-trops <env>"
                else
                    export TROPS_ENV=$1
                    export TROPS_SID=$(trops gensid)
                    if [[ ! $PS1 =~ "(τ)" ]]; then
                        export PS1="(τ)$PS1"
                    fi

                    if ! [[ "${{PROMPT_COMMAND:-}}" =~ "_trops_capcmd" ]]; then
                        PROMPT_COMMAND="_trops_capcmd;$PROMPT_COMMAND"
                    fi

                fi
            }}

            offtrops() {{
                export PS1=${{PS1//\(τ\)}}
                unset TROPS_ENV TROPS_SID
                PROMPT_COMMAND=${{PROMPT_COMMAND//_trops_capcmd\;}}
            }}
            """

        return dedent(bash_lines)

    def run(self):

        print(eval(f"self._init_{ self.args.shell }()"))


def trops_init(args, other_args):

    ti = TropsInit(args, other_args)
    ti.run()


def add_init_subparsers(subparsers):

    # trops init
    parser_init = subparsers.add_parser('init', help="Initialize Trops")
    parser_init.add_argument('shell', help='shell [bash/zsh]')
    parser_init.set_defaults(handler=trops_init)
