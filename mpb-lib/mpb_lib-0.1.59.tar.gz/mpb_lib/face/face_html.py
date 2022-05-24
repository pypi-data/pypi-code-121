HTML_FRAME = """
    <div id="face">
        <div id="left_eyeblow"></div>
        <div id="right_eyeblow"></div>
        <div id="left_eye"></div>
        <div id="right_eye"></div>
        <div id="mouth"></div>
    </div>
"""

WORD = """
    <p class="balloon" id="word"></p>
"""


STYLES = """
<style>
    #face {
        background-image:url("https://github.com/shibats/mpb_samples/blob/main/assets/face/assistant_face.png?raw=true");
        width: 362px;
        height: 420px;
        margin-left: -100px;
        margin-top: -100px;
        transform: scale(0.5, 0.5);
    }
    #left_eyeblow {
        background-image:url("https://github.com/shibats/mpb_samples/blob/main/assets/face/eyeblow_l.png?raw=true");
        width: 54px;
        height: 20px;
        position: absolute;
        left: 100px;
        top: 180px;
    }
    #right_eyeblow {
        background-image:url("https://github.com/shibats/mpb_samples/blob/main/assets/face/eyeblow_r.png?raw=true");
        width: 54px;
        height: 20px;
        position: absolute;
        left: 205px;
        top: 180px;
    }
    #left_eye {
        background-image:url("https://github.com/shibats/mpb_samples/blob/main/assets/face/eye_l_1.png?raw=true");
        width: 56px;
        height: 38px;
        position: absolute;
        left: 100px;
        top: 220px;
    }
    #right_eye {
        background-image:url("https://github.com/shibats/mpb_samples/blob/main/assets/face/eye_r_1.png?raw=true");
        width: 56px;
        height: 38px;
        position: absolute;
        left: 205px;
        top: 220px;
    }
    #mouth {
        background-image:url("https://github.com/shibats/mpb_samples/blob/main/assets/face/mouth_1.png?raw=true");
        width: 78px;
        height: 60px;
        position: absolute;
        left: 140px;
        top: 305px;
    }

    .balloon {
        position: absolute;
        display: inline-block;
        margin: 1.5em 0 1.5em 15px;
        padding: 7px 10px;
        min-width: 120px;
        max-width: 95%;
        color: #555;
        font-size: 16px;
        background: #FFF;
        border: solid 3px #555;
        border-radius: 8px;
        box-sizing: border-box;
    }
    .balloon:before {
        content: "";
        position: absolute;
        top: 50%;
        left: -24px;
        margin-top: -12px;
        border: 12px solid transparent;
        border-right: 12px solid #FFF;
        z-index: 2;
    }
    .balloon:after {
        content: "";
        position: absolute;
        top: 50%;
        left: -30px;
        margin-top: -14px;
        border: 14px solid transparent;
        border-right: 14px solid #555;
        z-index: 1;
    }
    p.balloon  {
        margin-left: 200px;
        margin-top: -300px;
        padding: 0.5em;
        font-size: 24pt;
    }
</style>
"""

SCRIPT = """
<script>
    function setBackground(the_id, im) {
     var elementReference = document.getElementById(the_id);
     elementReference.style.backgroundImage = "url(https://github.com/shibats/mpb_samples/blob/main/assets/face/"+im+"?raw=true)";
     var backgroundImage = elementReference.style.backgroundImage;
    }

    function setXPosition(the_id, x) {
     var elementReference = document.getElementById(the_id);
     elementReference.style.left = x;
    }


    function setYPosition(the_id, x) {
     var elementReference = document.getElementById(the_id);
     elementReference.style.top = x;
    }


    function rotate(the_id, deg) {
     var elementReference = document.getElementById(the_id);
     elementReference.style.transform = "rotate("+deg+"deg)";
     var backgroundImage = elementReference.style.backgroundImage;
    }
    
    function say(msg) {
        var elementReference = document.getElementById("word");
        elementReference.innerHTML = msg;

    }

    /*
    setXPosition("left_eye", 105);
    setBackground("left_eye", "eye_l_1.png");
    setBackground("right_eye", "eye_r_1.png");
    setBackground("mouth", "mouth_1.png");
    rotate("left_eyeblow", -20);
    rotate("right_eyeblow", 20);
    say("オホホホホホ2");
    */
</script>
    
"""
