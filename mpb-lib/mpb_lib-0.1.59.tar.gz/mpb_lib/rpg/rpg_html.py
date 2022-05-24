# rpg_html.py
#
# rpgの実行時に表示する，HTMLやCSS，JavaSCriptなどを集めたモジュール
# 
# Copyright (c) 2021 Atsush Shibata(shivata@m-info.co.jp)
#
# Released under the MIT license.

HTML_FRAME = """
 <link href="https://fonts.googleapis.com/css?family=M+PLUS+Rounded+1c&amp;subset=japanese" rel="stylesheet">
 <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
 <style>

.box {
    font-family: 'M PLUS Rounded 1c', sans-serif;
    font-size: 14pt;
    color : #ffffff;
    text-shadow : 2px 2px 2px rgba(51, 51, 51, 0.8);
    background-color : #0033cc;
    background : linear-gradient(#3366ff, #0033cc, #000066);
    padding : 12px 16px;
    box-shadow :
        3px 3px 5px rgba(51, 51, 51, 0.7) inset,
        0 0 2px 3px #666666,
        0 0 0   6px #ffffff,
        0 0 2px 8px #666666;
    width: 90%;
    margin: auto;
    margin-top: 8px;
    margin-bottom: 8px;
}

#box dt {
    font-weight: bold;
    color: #e84;
    margin: 0.4em 0 0 0;
    font-size: 16pt;
}

#box dd {
    font-weight: bold;
    padding: 0.1em 0;
}

.button {
    font-size: 12pt;
    color: black;
    background-color: white;
}


</style>
<div>
  <div id='box_$body_id' class='box'>
  </div>
</div>
<script>
function add_message(m, e) {
    var elem = document.getElementById('box_$body_id');
    var child = document.createElement(e);
    child.innerHTML     = m;
    elem.appendChild(child)
}

function add_rawhtml(h) {
    var elem = document.getElementById('box_$body_id');
    elem.innerHTML += h;
}

</script>
"""

INITIAL_OUTPUT = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/howler/2.2.3/howler.min.js"></script>
<script>
var death = new Howl({
    src: ['https://github.com/shibats/mpb_samples/blob/main/assets/deth.mp3?raw=true'],
    preload: true,
    html5: true
});

var hero_emerge = new Howl({
    src: ['https://github.com/shibats/mpb_samples/blob/main/assets/hero_emerge.mp3?raw=true'],
    preload: true,
    html5: true
});

var hit1 = new Howl({
    src: ['https://github.com/shibats/mpb_samples/blob/main/assets/hit1.mp3?raw=true'],
    preload: true,
    html5: true
});

var hit2 = new Howl({
    src: ['https://github.com/shibats/mpb_samples/blob/main/assets/hit2.mp3?raw=true'],
    preload: true,
    html5: true
});

var monster_emerge = new Howl({
    src: ['https://github.com/shibats/mpb_samples/blob/main/assets/monster_emerge.mp3?raw=true'],
    preload: true,
    html5: true
});

var success = new Howl({
    src: ['https://github.com/shibats/mpb_samples/blob/main/assets/success.mp3?raw=true'],
    preload: true,
    html5: true
});

var status_sound = new Howl({
    src: ['https://github.com/shibats/mpb_samples/blob/main/assets/status.mp3?raw=true'],
    preload: true,
    html5: true
});

var fight_music = new Howl({
    src: ['https://github.com/shibats/mpb_samples/blob/main/assets/fight_music.mp3?raw=true'],
    preload: true,
    html5: true
});
/*Howler.autoUnlock = true;*/

</script>

"""
