# rpg.py
#
# RPG風のユニット管理，表示をするシンプルなクラス
# Colaboratory，またはJupyter上での利用を想定
# 
# Copyright (c) 2021 Atsush Shibata(shivata@m-info.co.jp)
#
# Released under the MIT license.


from string import Template
from random import random
from time import sleep

from IPython.display import display, HTML
try:
    from google.colab.output import eval_js
except:
    def eval_js(js):
        body = HTML(f"""<script>
        {js}
        </script>""")
        display(body)

from .rpg_html import HTML_FRAME, INITIAL_OUTPUT
FRAME_TMPL = Template(HTML_FRAME)

# ユーティリティ関数

def load_audio():
    """
    音声ファイルを事前ロードするための関数
    """
    body = HTML(INITIAL_OUTPUT)
    display(body)


def play_audio(the_id):
    """
    IDを指定して音声を再生するJavaScriptを出力する関数
    """
    display(HTML(f"""<script>
    {the_id}.play();
    </script>
    """))


def pause_audio(the_id):
    """
    音声を止めるJavaScriptを出力する関数
    """
    display(HTML(f"""<script>
        {the_id}.stop();
        </script>
    """))


load_audio()  # モジュールインポート時に音声を事前ロードする


def play_with_button(sound_id, playable,
                     play_title="音を出す",
                     stop_title="音を消す"):
    """
    「音を鳴らす」ボタンを表示する
    """
    if playable:
        play_audio(sound_id)
    else:
        rawhtml = (f"""add_rawhtml('<button """
            f"""class="button" onclick="javascript:{sound_id}.play();">"""
            f"""<span class="material-icons">volume_up</span>"""
            f"""{play_title}</button>　');""")
        rawhtml += (f"""add_rawhtml('<button """
            f"""class="button" onclick="javascript:{sound_id}.stop();">"""
            f"""<span class="material-icons">volume_off</span>"""
            f"""{stop_title}</button>'); console.log('foo&');""")
        eval_js(rawhtml)



def add_message(message, elem="p"):
    """
    JavaScriptをinvokeして出力にメッセージを追加するユーティリティ関数
    """
    eval_js(f"add_message('{message}', '{elem}')")



class ユニット:
    """
    RPG風のシンプルなユニットクラス
    """

    playable = False
    body_id = 0
    play_title = "音を出す"
    stop_title = "音を消す"

    # メッセージ類
    msg_emerge = Template("$kindがうまれた。")

    msg_status = "ステータス"
    msg_occupation = "職業　"
    msg_hp = "体力　"
    msg_power = "パワー"

    msg_dead = Template("$kindは死んでいるので戦えない。")
    msg_t_dead = Template("$kindは死んでいる。これ以上はかわいそうだ。")
    mgs_fight = Template("$kindと$t_kindが戦った。")
    msg_hit = Template("$kindが$t_kindに$damage_targetのダメージを与えた。")
    msg_beat = Template("$kindは$t_kindを倒した！")
    msg_beaten = Template("$kindは$t_kindに倒されて死んでしまった。")


    def __init__(self, kind):
        """
        初期化メソッド
        
        初期化時に，音を鳴らすHTMLを出力して，表示中のブラウザが
        音を鳴らせるかどうか判別して，フラグを管理する
        """
        try:
            # ブラウザが音を慣らせるかどうかを判別
            display(HTML(f"""
        <audio id="nosound" preload>
        <source src="https://github.com/shibats/mpb_samples/blob/main/assets/nosound.mp3?raw=true" type="audio/mp3">
        </audio>
            """))
            eval_js(f"""
                    var bgm1 = document.querySelector("#nosound");
                    bgm1.play();
                    """)
        except:
            self.__class__.playable = False

        # ステータス表示のエレメントIDを初期化

        # ステータスを初期化
        self.kind = kind
        self.体力 = 0
        self.パワー = 0
        # 音声を先読みするため，HTMLを出力
        load_audio()

        # kindが「戦士」かどうかで，出現音声を分ける
        sound_id = "monster_emerge"
        if kind == "戦士":
            sound_id = "hero_emerge"

        # メッセージを表示
        display(HTML(FRAME_TMPL.substitute(body_id=self.body_id)))
        play_with_button(sound_id, self.playable,
                         self.play_title, self.stop_title)
        add_message(self.msg_emerge.substitute(kind=self.kind))
        self.__class__.body_id += 1


    def ステータス(self):
        """
        ステータスを表示する
        """

        load_audio()

        display(HTML(FRAME_TMPL.substitute(body_id=self.body_id)))
        self.__class__.body_id += 1

        play_with_button("status_sound", self.playable,
                         self.play_title, self.stop_title)

        add_message(self.msg_status, "dt")
        add_message(self.msg_occupation+f" : {self.kind: >5}", "dd")
        add_message(self.msg_hp+f" : {self.体力: >5}", "dd")
        add_message(self.msg_power+f" : {self.パワー: >5}", "dd")


    def 戦う(self, target):
        """
        ユニットのインスタンスtargetと戦う
        """
        load_audio()
        display(HTML(FRAME_TMPL.substitute(body_id=self.body_id)))
        self.__class__.body_id += 1

        if self.体力 <= 0:
            # 体力がない場合
            add_message(self.msg_dead.substitute(kind=self.kind))
            play_with_button("death", self.playable,
                             self.play_title, self.stop_title)
            return

        if target.体力 <= 0:
            # 戦う相手の体力がない場合
            add_message(self.msg_t_dead.substitute(kind=target.kind))
            play_with_button("death", self.playable,
                             self.play_title, self.stop_title)
            return

        # 双方のダメージを乱数で決める
        damage_mine = int(target.パワー*(random()/2+0.5))
        damage_target = int(self.パワー*(random()/2+0.5))
        self.体力 -= damage_mine
        target.体力 -= damage_target

        play_with_button("fight_music", self.playable,
                         self.play_title, self.stop_title)
        msg = self.mgs_fight.substitute(kind=self.kind, t_kind=target.kind)
        add_message(msg)
        sleep(2)

        # こちらの攻撃
        play_audio("hit1")
        msg = self.msg_hit.substitute(kind=self.kind,
                                      t_kind=target.kind,
                                      damage_target=damage_target)
        add_message(msg)
        sleep(1)

        if target.体力 <= 0:
            # 勝った場合
            pause_audio("fight_music")
            play_audio("success")
            msg = self.msg_beat.substitute(kind=self.kind,
                                           t_kind=target.kind)
            add_message(msg)
            return

        # 相手の攻撃
        msg = self.msg_hit.substitute(kind=target.kind,
                                      t_kind=self.kind,
                                      damage_target=damage_mine)
        add_message(msg)
        play_audio("hit1")
        sleep(1)

        if self.体力 <= 0:
            # 負けた場合
            pause_audio("fight_music")
            play_audio("death")
            msg = self.msg_beaten.substitute(kind=self.kind,
                                             t_kind=target.kind)
            add_message(msg)


class Unit(ユニット):
    """
    クラス ユニット の英語版
    """
    playable = False
    body_id = 100

    play_title = "Play"
    stop_title = "Stop"

    # メッセージ類
    msg_emerge = Template("$kind has born.")

    msg_status = "Status"
    msg_occupation = "Occupation　"
    msg_hp =         "Hitpoint  　"
    msg_power =      "Strength    "

    msg_dead = Template("$kind has been already dead.")
    msg_t_dead = Template("$kind had died.")
    mgs_fight = Template("$kind fought with $t_kind.")
    msg_hit = Template("$kind gave $damage_target damage to $t_kind.")
    msg_beat = Template("$kind beat $t_kind !")
    msg_beaten = Template("$kind  has been defeated by $t_kind.")


    def __init__(self, kind):
        self.kind = kind
        self.hitpoint = 0
        self.strength = 0
        # kindが「Hero」かどうかで，出現音声を分ける
        sound_id = "monster_emerge"
        if kind.lower() == "hero":
            sound_id = "hero_emerge"

        # メッセージを表示
        display(HTML(FRAME_TMPL.substitute(body_id=self.body_id)))
        play_with_button(sound_id, self.playable,
                         self.play_title, self.stop_title)
        add_message(self.msg_emerge.substitute(kind=self.kind))
        self.__class__.body_id += 1


    def copy_status_to(self):
        """
        hitpointを体力に，Strengthをパワーにコピーする
        """
        self.体力 = self.hitpoint
        self.パワー = self.strength


    def copy_status_from(self):
        """
        体力をにhitpoint，パワーをStrengthにコピーする
        """
        self.hitpoint = self.体力
        self.strength = self.パワー


    def status(self):
        """
        ステータスを表示する
        """
        self.copy_status_to()
        self.ステータス()


    def fight(self, target):
        self.copy_status_to()
        target.copy_status_to()
        self.戦う(target)
        self.copy_status_from()
        target.copy_status_from()

