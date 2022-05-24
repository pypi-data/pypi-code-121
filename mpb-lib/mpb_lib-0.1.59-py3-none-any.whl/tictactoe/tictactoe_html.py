CSS = """
<style>
.container_t {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #eee;
}

.play-area {
  display: grid;
  width: 300px;
  height: 300px;
  grid-template-columns: auto auto auto;
}

.block {
  display: flex;
  position: relative;
  width: 100px;
  height: 100px;
  align-items: center;
  justify-content: center;
  font-size: 48pt;
  font-weight: bold;
  border: 3px solid black;
  transition: background 0.2s ease-in-out;
}

.block .number {
  font-size: 32pt;
  color: #bbb;
  position: absolute;
  top: 1.2em;
  left: 1.4em;
  z-index: 0;
}

.human {
  color: #482;
  z-index: 2;
}

.pc {
  color: #c42;
  z-index: 2;
}

.order {
  color: #46d;
  font-size: 18pt;
  position: absolute;
  top: 0.4em;
  left: 0.7em;
  z-index: 3;
}



#block_0,
#block_1,
#block_2 {
  border-top: none;
}

#block_0,
#block_3,
#block_6 {
  border-left: none;
}

#block_6,
#block_7,
#block_8 {
  border-bottom: none;
}

#block_2,
#block_5,
#block_8 {
  border-right: none;
}

.draw {
  color: orangered;
}
</style>
"""

FRAME = """
    <div class="container_t">
        <div class="play-area">
          <div id="block_0" class="block">
            {0[0]}
            <span class="number">1</span>
          </div>
          <div id="block_1" class="block pc">
            {0[1]}
            <span class="number">2</span>
          </div>
          <div id="block_2" class="block">
            {0[2]}
            <span class="number">3</span>
          </div>
          <div id="block_3" class="block">
            {0[3]}
            <span class="number">4</span>
          </div>
          <div id="block_4" class="block">
            {0[4]}
            <span class="number">5</span>
          </div>
          <div id="block_5" class="block">
            {0[5]}
            <span class="number">6</span>
          </div>
          <div id="block_6" class="block">
            {0[6]}
            <span class="number">7</span>
          </div>
          <div id="block_7" class="block">
            {0[7]}
            <span class="number">8</span>
          </div>
          <div id="block_8" class="block">
            {0[8]}
            <span class="number">9</span>
          </div>
        </div>
    </div>
"""