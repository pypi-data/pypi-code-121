SCRIPT = """
// constants
var wo_width = 800,
    wo_height = 300,
    ball_x = 66,
    ball_y = -10,
    ball_r = 10,
    ball_height = 5,
    wall_x = 720,
    wall_y = wo_height,
    wall_w = 60,
    wall_h = 30,
    wall_color1 = 'brown',
    wall_color2 = 'gray',
    fl2_width = wall_w+20,
    fl2_height = -ball_y,
    cannon_x = 10,
    cannon_y = 460,
    cannon_w = 40,
    cannon_h = 20,
    with_sound = false,
    breakable = true;


make_world = function(add_wall, delta) {
	setup();
    load_sound();
    
	//Add a floor
	var floor = Matter.Bodies.rectangle(wo_width/2, wo_height, wo_width, 10, {
        label: 'floor',
		density:5000.0,
		friction: 80,
        restitution: 900,
		isStatic: true, //An immovable object
		render: {
			visible: true
		}
	});
	Matter.World.add(world, floor);

	var floor2 = Matter.Bodies.rectangle(wall_x+delta-10, wo_height, fl2_width, -fl2_height, {
        label: 'floor',
		density:5000.0,
		friction: 80,
        restitution: 900,
		isStatic: true, //An immovable object
		render: {
			visible: true
		}
	});
	//Matter.World.add(world, floor2);



    walls = add_wall(delta);
	
	Matter.Events.on(engine, 'collisionStart', function(event) {
	var pairs = event.pairs;

    if( pairs[0].bodyB.label == 'ball') {
         var bx = pairs[0].bodyB.velocity.x, by = pairs[0].bodyB.velocity.y,
             bv = bx**2+by**2;
         if( bv > 60 && breakable ){
         
            if( pairs[0].bodyA.label.startsWith('wall')) {
                var tb = pairs[0].bodyA, ox = tb.bounds.min.x, oy = tb.bounds.min.y,
                    vx = tb.velocity.x*20, vy = tb.velocity.y*20;
                var i = 0;
                for( var x = 0; x < 3; x++ ) {
                    for( var y = 0; y < 3; y++ ) {

                        var wall = make_wall(ox+x*(wall_h/3), oy+y*(wall_h/3),
                                            wall_w/3.5, wall_h/3.5, 300, 's_wall'+i, wall_color1);
                        Matter.World.add(world, wall);
                        walls.push(wall);             
                        i ++;   
                    }
                }
                Matter.World.remove(world, pairs[0].bodyA);
                pairs[0].bodyB.label = 'ball_col'
                if( with_sound ) {
                    heavy_hit.play();
                }
            } else {
                if( with_sound ) {
                    light_hit.play();
                    breakable = false;
                }
            }
         } else {
             if( with_sound ) {
                 light_hit.play();
                breakable = false;
             }
             pairs[0].bodyA.label = 'ball_col'
         }
	 }
	});

	//Start the engine
	Matter.Engine.run(engine);
	Matter.Render.run(render);

};

var load_sound = function() {
    blast = new Howl({
        src: ['https://github.com/shibats/mpb_samples/blob/main/assets/blast.mp3?raw=true'],
        preload: true,
        html5: true
    });

    light_hit = new Howl({
        src: ['https://github.com/shibats/mpb_samples/blob/main/assets/light_hit.mp3?raw=true'],
        preload: true,
        html5: true,
        volume: 0.3
    });
    
    heavy_hit = new Howl({
        src: ['https://github.com/shibats/mpb_samples/blob/main/assets/heavy_hit.mp3?raw=true'],
        preload: true,
        html5: true,
        volume: 0.25
    });

};

var setup = function() {
    //Fetch our canvas
	var canvas = document.getElementById('world');

	//Setup Matter JS
	engine = Matter.Engine.create();
	world = engine.world;
	body = Matter.Body;
	render = Matter.Render.create({
		canvas: canvas,
		engine: engine,
		options: { 
			width: wo_width,
			height: wo_height,
			background: 'transparent',
			wireframes: false,
			showAngleIndicator: false
		}
	});

};


var make_wall = function(x, y, w, h, density, label, color ) {
    var wall = Matter.Bodies.rectangle(x, y, w, h, { 
        label: label,
        density: density,
        friction: 1,
        frictionAir: 0.01,
        restitution: 0.001,
        render: {
            fillStyle: color,
            strokeStyle: 'black',
            lineWidth: 1
        }
    });
    return wall
}

add_wall1 = function(delta) {
    //Add a wall
	var walls = [];
	for(var i=0; i <= 5; i++ ) {
        var wall = make_wall(wall_x, wall_y-i*wall_h, wall_w, wall_h, 800, 'wall'+i, wall_color1);
		Matter.World.add(world, wall);
		walls.push(wall);
	}
    return walls;
};

add_wall2 = function(delta) {
    //Add a wall
	var walls = [];
	for(var i=0; i <= 5; i++ ) {
        var col = wall_color2, label = 'hwall'+i;
        if( i == 1 ) {
            col = wall_color1
            label = 'wall'+i;
        }
        var wall = make_wall(wall_x+delta, wall_y-i*wall_h, wall_w, wall_h, 800, label, col);
		Matter.World.add(world, wall);
		walls.push(wall);
	}
    return walls;
};


var bang = function(powder) {
    var but = document.getElementById('button');
    but.disabled = true;
    var but2 = document.getElementById('button2');
    but2.disabled = true;


    //Add a ball
    var ball = Matter.Bodies.circle(ball_x, ball_y+wo_height-ball_r-ball_height, ball_r, {
        label: 'ball',
        density:2000.0,
        friction: 0.99,
        frictionAir: 0.0002,
        restitution: 0.0001,
        render: {
            fillStyle: '#222',
            strokeStyle: 'black',
            lineWidth: 1
        }
    });
    var v = powder/10;
    body.setVelocity(ball, {x:v, y:-v});
    if( with_sound ) { 
        blast.play();
    }

    Matter.World.add(world, ball);

};

var sound_on = function() {
  with_sound = true;
};

"""

LOAD_SCRIPT = """
	<script>

var script = document.createElement( 'script' );

script.type = 'text/javascript';
script.src = 'https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.17.1/matter.min.js';

var firstScript = document.getElementsByTagName( 'script' )[ 0 ];
firstScript.parentNode.insertBefore( script, firstScript );
	</script>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/howler/2.2.3/howler.min.js" type="text/javascript"></script>
"""


HTML_TEMPLATE = """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.17.1/matter.min.js" type="text/javascript"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/howler/2.2.3/howler.min.js" type="text/javascript"></script>
		<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
		<style>
#cannon {
	background-image: url('https://github.com/shibats/mpb_samples/blob/main/assets/cannon2.png?raw=true');
	background-size: cover;
	width: 80px;
	height: 80px;
	margin-top: -76px;
	margin-left: 8px;
	z-index: -10;
}

#countdown {
    margin-top: -100px;
    margin-left: 2em;
}

.container {
}


.world_outer {
  margin-left: 0;
  width: 800px;
}

.button_wrapper {
	text-align: center;
}

button {
  font-size: 14pt;
  margin: 0.5em 0;
  text-align: center:
}

@media screen and (max-width:900px) {
  .container {
      -webkit-transform: scale(0.75);
      transform: scale(0.75);
      margin-left: -6em;
      margin-top: -1em;
  }
}

@media screen and (max-width: 500px) {
  .container {
      -webkit-transform: scale(0.4);
      transform: scale(0.4);
      margin-left: -6em;
      margin-top: -1em;
  }
}

@media screen and (max-width: 300px) {
  .container {
      -webkit-transform: scale(0.2);
      transform: scale(0.2);
      margin-left: -6em;
      margin-top: -1em;
  }
}


@media screen and (max-width: 200px) {
  .container {
      -webkit-transform: scale(0.25);
      transform: scale(0.25);
      margin-left: -6em;
      margin-top: -3em;
  }
}

		</style>
    <div class="container">
        <div class="button_wrapper">
            <button id="button" onclick="countdown(); sound_on();"><span class="material-icons">volume_up</span>音ありでうつ</button>
            <button id="button2" onclick="countdown();"><span class="material-icons">volume_off</span>音なしでうつ</button>
            <h2>火薬量: ${powder} ${dist_display}</h2>
       </div>
		<div class="world_outer">
            <canvas id="world"></canvas>
            <div id="cannon"></div>
            <h2 id="countdown">--</h2>
		</div>
    </div>
	<script>
        ${SCRIPT}

        make_world(add_wall${stage}, ${delta});
        var countdown = function() {
            setTimeout(function() {bang(${powder}*3, true);}, 2000);
            var countdown = 3;
            var cd = function() {
                countdown--;
                var elem = document.getElementById('countdown');
                elem.innerHTML = countdown;
            };
            cd();
            setTimeout(cd, 1000);
            setTimeout(cd, 2000);

            var button1 = document.getElementById('button'),
                button2 = document.getElementById('button2');
            button1.disabled = true;
            button2.disabled = true;

        };

	</script>
"""