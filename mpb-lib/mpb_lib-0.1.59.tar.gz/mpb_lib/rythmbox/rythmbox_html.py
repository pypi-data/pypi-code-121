JAVASCRIPT = """
var position = 0, speed = 200, blocks = ${cols},
    sound = {'red':'crave', 'yellow':'kick', 'green':'snare', 'blue':'hat', 'lime':'hat', 'purple':'tom', 'orange':'crap' },
    make_sound = false;
if( !timer_id ) {
    var timer_id = null;
}

var load_sound = function() {
    sounds = {
    'clap' : new Howl({
        src: ['https://github.com/shibats/mpb_samples/blob/main/assets/rithmmachine/clap.wav?raw=true'],
        preload: true,
        html5: true,
    }),

    'kick' : new Howl({
        src: ['https://github.com/shibats/mpb_samples/blob/main/assets/rithmmachine/kick.wav?raw=true'],
        preload: true,
        html5: true,
    }),

    'snare' : new Howl({
        src: ['https://github.com/shibats/mpb_samples/blob/main/assets/rithmmachine/snare.wav?raw=true'],
        preload: true,
        html5: true,
    }),

    'cymbal' : new Howl({
        src: ['https://github.com/shibats/mpb_samples/blob/main/assets/rithmmachine/cymbal.wav?raw=true'],
        preload: true,
        html5: true,
    }),

    'hat' : new Howl({
        src: ['https://github.com/shibats/mpb_samples/blob/main/assets/rithmmachine/hat.wav?raw=true'],
        preload: true,
        html5: true,
    }),

    'tom' : new Howl({
        src: ['https://github.com/shibats/mpb_samples/blob/main/assets/rithmmachine/tom.wav?raw=true'],
        preload: true,
        html5: true,
    }),

    'crave' : new Howl({
        src: ['https://github.com/shibats/mpb_samples/blob/main/assets/rithmmachine/clave.wav?raw=true'],
        preload: true,
        html5: true
    }),

    }

    
};


var getelements = function(classname) {
    var elem = document.getElementsByClassName(classname);
    var array = Array.prototype.slice.call(elem);
    return array;
}

var proceed = function() {
    oldelem = getelements('pos'+position);
    for( var item in oldelem ){
        oldelem[item].classList.remove('tick');
    };

    position = (position+1)%blocks;
    elem = getelements('pos'+position);
    for( var item in elem ){
        elem[item].classList.add('tick');
        console.log(make_sound)
        if( make_sound && elem[item].classList.value.includes(' on') ) {
            var s = sound[elem[item].classList[1]];
            sounds[s].play();
        }
    };

};

var periodic = function() {
    proceed();
    timer_id = setTimeout(periodic, speed);
};

var sound_on = function() {
    make_sound = true;
}

var sound_off = function() {
    make_sound = false;
}

load_sound();

if( timer_id ) {
    clearTimeout(timer_id);
    timer_id = null;
}

periodic();
"""

HEAD = """
  <script src="https://cdnjs.cloudflare.com/ajax/libs/howler/2.2.3/howler.min.js"></script>
  <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
"""

HTML_FRAME = """
  <style>
.container {
  display: block;
  margin: auto;

}

.indicator {
  margin: 0;
  display: inline-block;
  height:2em;
  width: 30px;
  color: white;
  text-align: center;
  background-color: #888;
  border: 2px solid #fff;
  border-radius: 4px;
  
}

.button {
  margin: 0;
  display: inline-block;
  height: 30px;
  width: 30px;
  border: 2px solid #fff;
  border-radius: 4px;
}

.red {
  background-color: #5c0011;
}

.yellow {
  background-color: #614700;
}

.green {
  background-color:#092b00;
}

.blue {
  background-color: #002766;
}

.lime {
  background-color: #254000;
}

.purple {
  background-color: #120338;
}

.orange {
  background-color: #612500;
}



.tick {
  border: 2px solid #fe8;
}

.indicator.tick {
  background-color: #eee;
}

.red.tick  {
  background-color: #a8071a;
}

.yellow.tick {
  background-color: #ad8b00;
}

.green.tick {
  background-color: #237804;
}

.blue.tick {
  background-color: #0050b3;
}

.lime.tick {
  background-color: #5b8c00;
}

.purple.tick {
  background-color: #391085;
}

.orange.tick {
  background-color: #ad4e00;
}



.red.on  {
  background-color: #cf1322;
}

.yellow.on {
  background-color: #d4b106;
}

.green.on {
  background-color: #389e0d;
}

.blue.on {
  background-color: #096dd9;
}

.red.on.tick  {
  background-color: #ff7875;
}

.yellow.on.tick {
  background-color: #fff566;
}

.green.on.tick {
  background-color: #95de64;
}

.blue.on.tick {
  background-color: #69c0ff;
}

.lime.on.tick {
  background-color: #d3f261;
}

.purple.on.tick {
  background-color: #b37feb;
}

.orange.on.tick {
  background-color: #ffc069;
}


  </style>

  <div class="container">
    <button id="sound_on" onclick="sound_on();"><span class="material-icons">volume_up</span>音を鳴らす</button>
    <button id="sound_off" onclick="sound_off();"><span class="material-icons">volume_off</span>音を止める</button>

    ${markers}

    ${blocks}

  </div>

  <script>
  ${script}
  </script>

"""

MCOL_TEMPLATE = """
      <div id="${an_id}_${pos}" class="${klass} pos${pos}">
        ${pos}
      </div>
"""

COL_TEMPLATE = """
      <div id="${an_id}_${pos}" class="${klass} pos${pos}">
      </div>
"""


ROW_TEMPLATE = """
    <div class="row">
      ${cols}
    </div>
"""
