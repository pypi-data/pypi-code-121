import base64
from io import BytesIO
builtin_kube='''html,body,div,span,object,iframe,p,blockquote,pre,a,abbr,acronym,address,big,cite,code,del,dfn,em,img,ins,kbd,q,s,samp,small,strike,strong,sub,sup,tt,var,b,u,i,center,dl,dt,dd,ol,ul,li,fieldset,form,label,legend,table,caption,tbody,tfoot,thead,tr,th,td,article,aside,canvas,details,embed,figure,figcaption,footer,header,hgroup,menu,nav,output,ruby,section,summary,time,mark,audio,video,h1,h2,h3,h4,h5,h6{margin:0;padding:0;border:0;outline:0;font-size:100%;vertical-align:baseline;background:transparent;font-style:normal;}article,aside,details,figcaption,figure,footer,header,hgroup,nav,section{display:block;}img,object,embed,video,iframe{max-width:100%;}blockquote,q{quotes:none;}blockquote p:before,blockquote p:after,q:before,q:after{content:'';content:none;}table{border-collapse:collapse;border-spacing:0;}caption,th,td{text-align:left;vertical-align:top;font-weight:normal;}thead th,thead td{font-weight:bold;vertical-align:bottom;}a img,th img,td img{vertical-align:top;}button,input,select,textarea{margin:0;}textarea{overflow:auto;}button{width:auto;overflow:visible;}input[type=button],input[type=submit],button{cursor:pointer;}input[type="radio"],input[type="checkbox"]{font-size:110%;}hr{display:block;height:1px;border:0;border-top:1px solid #ddd;}.group:after{content:".";display:block;height:0;clear:both;visibility:hidden;}body{background:#ffffff;color:#000000;font-size:0.875em;line-height:1.5em;font-family:Helvetica,Arial,Tahoma,sans-serif;}a{color:#336699;}a:hover{color:#19334d;}h1,h2,h3,h4,h5,h6{font-weight:bold;margin-bottom:0.5em;}h1{font-size:2.5714285714285716em;line-height:1em;}h2{font-size:2.142857142857143em;line-height:1.1em;}h3{font-size:1.7142857142857142em;line-height:1.3em;}h4{font-size:1.2857142857142858em;line-height:1.3em;}h5{font-size:1.1428571428571428em;line-height:1.3em;}h6{font-size:1em;line-height:1.3em;text-transform:uppercase;}hgroup h1,hgroup h2,hgroup h3,hgroup h4{margin-bottom:.1em;}.subheader{font-size:1.2em;font-weight:normal;color:#8f8f8f;margin-bottom:1em;}p,ul,ol,dl,dd,dt,blockquote,td,th{line-height:1.5em;}ul,ol,ul ul,ol ol,ul ol,ol ul{margin:0 0 0 2em;}ol ol li{list-style-type:lower-alpha;}ol ol ol li{list-style-type:lower-roman;}p,ul,ol,dl,blockquote,hr,pre,hgroup,table,form,fieldset{margin-bottom:1.5em;}dl dt{font-weight:bold;}dd{margin-left:1em;}blockquote{margin-bottom:1.5em;padding-left:1.5em;border-left:1px solid #ccc;color:#666;}blockquote small,cite{color:#888;font-style:italic;}blockquote p{margin-bottom:1em;}small,blockquote cite{font-size:0.85em;line-height:1;}blockquote .pull-right,.row blockquote .pull-right{float:none;text-align:right;display:block;}address{font-style:italic;}del{text-decoration:line-through;}abbr[title],dfn[title]{border-bottom:1px dotted #000;cursor:help;}strong,b{font-weight:bold;}em,i{font-style:italic;}sub,sup{font-size:0.7em;line-height:0;position:relative;}sup{top:-0.5em;}sub{bottom:-0.25em;}figcaption{font-size:0.85em;font-style:italic;}ins,mark{background-color:#ffee55;color:#000000;text-decoration:none;}pre,code,kbd,samp{font-size:90%;font-family:Menlo,Monaco,monospace,sans-serif;}pre{background:#f8f8f8;border:1px solid #ddd;border-radius:3px;padding:1.5em;white-space:pre;overflow:auto;}code{padding:2px 3px;line-height:1;background:#f8f8f8;border:1px solid #ddd;}kbd{padding:0 6px;border-radius:4px;box-shadow:0 2px 0 rgba(0,0,0,0.2),0 0 0 1px #ffffff inset;background-color:#fafafa;border-color:#ccc #ccc white;border-style:solid solid none;border-width:1px 1px medium;color:#444;font-weight:bold;white-space:nowrap;}input[type="text"],input[type="password"],input[type="email"],textarea{font-size:13px;}fieldset{padding:2em 1.5em;margin-bottom:1.5em;border:1px solid #dddddd;}legend{font-size:1.2em;text-transform:uppercase;font-weight:bold;padding:0 1em;}tfoot th,tfoot td{background-color:#f2f2f2;}th,td{border-bottom:1px solid #eeeeee;padding:0.75em 0.5em;}table caption{text-transform:uppercase;font-weight:bold;padding-left:0.5em;color:#666;}table.simple td,table.simple th{border:none;padding:0.75em 0.7em 0.75em 0;}table.bordered td,table.bordered th{border:1px solid #ddd;}table.stroked td,table.stroked th{border-bottom:1px solid #eee;}table.striped tbody tr:nth-child(odd) td{background-color:#f8f8f8;}table.hovered tbody tr:hover td,table.hovered thead tr:hover th{background-color:#f6f6f6;}.thead-gray td,.thead-gray th{background-color:#f0f0f0;}.thead-black td,.thead-black th{font-weight:normal;color:#f6f6f6;color:rgba(255,255,255,0.9);background-color:#222;}table.bordered .thead-black td,table.bordered .thead-black th{border:1px solid #444;}.forms label{display:block;margin-bottom:2px;}.descr{color:#999999;font-size:0.85em;line-height:1.5em;}div.descr{margin:4px 0;}.columnar div.descr{margin-bottom:10px;}.forms ul{list-style:none;margin:0;}.forms ul li{margin-bottom:10px;}.forms.columnar ul li{margin-bottom:15px;}fieldset.liner{border:none;padding:0;}fieldset.liner legend{padding:0;width:100%;padding-bottom:12px;}fieldset.liner legend span{padding:0;padding-bottom:8px;border-bottom:1px solid #eee;display:block;}.forms ul.multicolumn:after{content:".";display:block;height:0;clear:both;visibility:hidden;}.forms ul.multicolumn li{float:left;margin-right:12px;margin-bottom:0;line-height:1.8em;}.forms ul.multicolumn li label{margin-bottom:0;}.forms ul.multicolumn li.width-50{width:48%;margin-right:2%;}.forms ul.multicolumn li.width-33{width:31%;margin-right:2%;}.forms.columnar legend{margin-bottom:1em;}.forms.columnar label{float:left;width:150px;text-align:right;margin-right:20px;}.forms.columnar .push,.forms.columnar div.descr{margin-left:170px;}.forms.columnar li fieldset label{float:none;width:auto;text-align:left;margin-right:0;}.forms.columnar li fieldset{border:none;padding:0;margin:0;padding-left:170px;position:relative;}.forms.columnar li fieldset section{padding:0;position:absolute;width:150px;text-align:right;left:0;top:0;}.forms.columnar li fieldset section label{float:none;width:auto;margin-right:0;text-align:right;}.forms.columnar li fieldset div.descr{margin-left:0;}.forms li.form-section{font-weight:bold;border-bottom:1px solid #eee;padding:1.5em 0 .7em 0;font-size:1.1em;margin-bottom:1.5em;}.columnar li.form-section{padding-left:170px;}table.tableforms td{font-size:90%;padding:1px 10px 3px 0 !important;border:none;}table.tableforms tr.labels td{padding-top:.8em !important;font-weight:bold;}input[type="radio"],input[type="checkbox"]{position:relative;top:-1px;}input[type="text"],input[type="password"],input[type="email"],textarea{position:relative;z-index:2;font-family:Helvetica,Arial,Tahoma,sans-serif;height:23px;border:1px solid #ccc;margin:0;padding:1px 2px;background-color:white;color:#333;font-size:13px;line-height:1;border-radius:1px;box-shadow:0 1px 2px rgba(0,0,0,0.2) inset;-webkit-transition:border 0.3s ease-in;-moz-transition:border 0.3s ease-in;-ms-transition:border 0.3s ease-in;-o-transition:border 0.3s ease-in;transition:border 0.3s ease-in;}textarea{line-height:1.4em;}.error,.success{margin-left:5px;font-weight:normal;font-size:0.85em;}input.input-error,textarea.input-error,select.input-error,.input-error{border-color:#da3e5a;box-shadow:0 0 0 2px rgba(218,62,90,0.3),0 1px 2px rgba(0,0,0,0.2) inset;}input.input-success,textarea.input-success,select.input-success,.input-success{border-color:#18a011;box-shadow:0 0 0 2px rgba(24,160,17,0.3),0 1px 2px rgba(0,0,0,0.2) inset;}input.input-gray,textarea.input-gray,select.input-gray,.input-gray{border-color:#ccc;box-shadow:0 0 0 2px rgba(204,204,204,0.3),0 1px 2px rgba(0,0,0,0.2) inset;}input:focus,textarea:focus{outline:none;border-color:#5ca9e4;box-shadow:0 0 0 2px rgba(70,161,231,0.3),0 1px 2px rgba(0,0,0,0.2) inset;}input.input-search{padding-right:10px;padding-left:10px;margin-bottom:0;border-radius:15px;}.input-append,.input-prepend{display:inline-block;background-color:#eee;height:23px;border:1px solid #ccc;margin:0;padding:1px 8px;color:#333;font-size:14px;line-height:20px;}.input-prepend{margin-right:-1px;}.input-append{position:relative;z-index:1;margin-left:-1px;}.btn{position:relative;cursor:pointer;outline:none;display:inline-block;text-align:center;text-decoration:none;font-family:Arial,Helvetica,sans-serif;line-height:1;font-size:13px;font-weight:normal;padding:6px 16px;border-radius:4px;background-color:#f3f3f3;background-image:-moz-linear-gradient(top,#ffffff,#e1e1e1);background-image:-ms-linear-gradient(top,#ffffff,#e1e1e1);background-image:-webkit-gradient(linear,0 0,0 100%,from(#ffffff),to(#e1e1e1));background-image:-webkit-linear-gradient(top,#ffffff,#e1e1e1);background-image:-o-linear-gradient(top,#ffffff,#e1e1e1);background-image:linear-gradient(top,#ffffff,#e1e1e1);filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#ffffff',endColorstr='#e1e1e1',GradientType=0);border:1px solid #dadada;border-left:1px solid #d2d2d2;border-right:1px solid #d2d2d2;border-bottom-color:#a9a9a9;box-shadow:0 1px 0 rgba(0,0,0,0.15),inset 0 1px 1px 0 rgba(255,255,255,0.6);text-shadow:0 1px 0px #ffffff;}.btn,.btn:hover{color:#000;}.btn:hover{filter:none;background:none;background:#eee;text-shadow:0 1px 0px rgba(255,255,255,0.8);text-decoration:none;box-shadow:0 1px 0 rgba(0,0,0,0.15);}.btn-big.btn-active,.btn-big.btn-active:hover{padding:11px 25px;}.btn-active,.btn-active:hover{box-shadow:0 2px 4px rgba(0,0,0,0.4) inset;color:#555;border:none;background:none;filter:none;background-color:#ddd;text-shadow:0 1px 0px rgba(255,255,255,0.8);padding:7px 17px 8px 17px;}.btn-small{padding:4px 12px;font-size:11px;}.btn-small.btn-active{padding:5px 12px;}.btn-big{padding:10px 24px;font-size:20px;}.btn-square{-moz-border-radius:0;-webkit-border-radius:0;border-radius:0;}.btn-round{border-radius:15px;border-radius:0 '''
kube = BytesIO()
kube.write(builtin_kube.encode('utf8'))
sfile_dict = {'builtin_kube.css':kube}

builtin_style='''body {position:relative;z-index:1;/*background:url(bg.png)*/;background-color: #edf1f7;color: #333333; font: 13px  微软雅黑,Microsoft Yahei,Verdana, Arial, Helvetica, sans-serif; line-height: 1;
-webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}
::selection { color: #fff; background: #fb6aa1; }
::-moz-selection {color:#fff;background:#fb6aa1;}
input::-ms-clear { display: none; }
a:link, a:visited { color: #444; text-decoration: none; -webkit-transition: background-color .15s linear, color .15s linear; -moz-transition: background-color .15s linear, color .15s linear; -o-transition: background-color .15s linear, color .15s linear; -ms-transition: background-color .15s linear, color .15s linear; transition: background-color .15s linear, color .15s linear; }
a:hover { color: #fd6ca3; }
.clear { clear: both; }
.box { background: #fff; /*border: solid 1px #d9dbdd; border-bottom-color:#dcdee0;*/border-radius:6px}
.boxx{border-radius: 5px 5px 0px 0px;}
h2 { font-size: 16px; /*font-weight: bold;首页文章不加粗*/ line-height: 1.5em; padding-bottom: 10px; }
h3 { font-size: 15px; line-height: 36px; height: 36px; }
.search_no{line-height: 30px;height: auto;font-size: 14px;padding:10px 5px;}
.search_no div{;text-align:center;font-size: 15px;margin: 30px auto;padding: 10px;border-radius: 5px;border: 1px solid #54aaff;color:#1e88e5 }
.search_no div a{color: deeppink}
.search_no span{color:red}
.container { max-width: 1180px; margin: 0 auto; }
strong { font-weight: bold; }
blockquote, pre { margin:40px 0 40px 0px;padding:0 20px 0 20px;border-left:1px solid #EEE;color:#AAA ;font-style:italic;line-height:24px}
blockquote p, pre p { text-indent: 0 !important }
center { margin: 0 auto; text-align: center }
.container_lod{}
/*header*/
.mainbar { background:#1b1b1b; /*border-bottom:1px solid #dfe5e9; */width:100%; height:40px;  }
#topbar { height: 40px; line-height: 40px; float: left; overflow: hidden; }
#topbar ul { list-style: none; }
#topbar ul li { height: 33px; line-height: 40px; float: left; padding: 0 50px 0 0; text-align: center; font-size:12px }
#topbar ul li a{ color:#565656}
#topbar ul li a:hover{ color:#fd6ca3}
#topbar ul ul { display: none; }
.toolbar { height: 30px; line-height: 30px; float: left; }
#rss { float: right; }
#rss ul li { margin: 10px 0 0 14px; float: right }
.icon1, .icon1 span.hover, .icon2, .icon2 span.hover, .icon3, .icon3 span.hover, .icon4, .icon4 span.hover, .icon5, .icon5 span.hover, .icon6, .icon6 span.hover { display: block; width: 24px; height: 24px; background: url(images/social_icon.gif) no-repeat; }
.icon1 { background-position: 0 -48px; }
.icon1 span.hover { background-position: 0 -72px; }
.icon2 { background-position: 0 -192px; }
.icon2 span.hover { background-position: 0 -216px; }
.icon3 { background-position: 0 -240px; }
.icon3 span.hover { background-position: 0 -264px; }
.icon4 { background-position: 0 -96px; }
.icon4 span.hover { background-position: 0 -120px; }
.icon5 { background-position: 0 -144px; }
.icon5 span.hover { background-position: 0 -168px; }
.icon6 { background-position: 0 0; }
.icon6 span.hover { background-position: 0 -24px; }
#blogname { outline: none; overflow: hidden; float:left; margin-top:1px; width:194px; }
#blogname h1 { text-indent: -9999px; height: 0; width: 0; }
#blognamess { outline: none; overflow: hidden; float:left; margin-top:15px; width:194px; }
#blognamess h1 { text-indent: -9999px; height: 0; width: 0; }
.search_phone { display: none }
/*loading*/
#main_loading{ position: fixed !important; position: absolute; top: 0; left: 0; height: 100px; width: 200px; z-index: 999; background: #000 url(images/loading.gif) no-repeat center; opacity: 0.6; filter: alpha(opacity=60); font-size: 14px; line-height: 20px; top: 50%; left: 50%; margin-top: -50px; margin-left: -100px; border-radius: 5px; }
#loading-one{ color: #fff; position: absolute; top: 50%; left: 50%; margin: 50px 0 0 -50px; padding: 3px 10px; }
#loading-one_m{
    olor: #fff;
    position: absolute;
    top: 50%; left: 50%;
    margin: 50px 0 0 -50px;
    padding: 3px 10px;}
#main_loading_m{
    position: absolute;
    margin-top: 200px;
    left: 50%;
    margin-left: -100px;
    height: 100px;
    width: 200px;
    z-index: 999;
    background: #000 url(images/loading.gif) no-repeat center;
    opacity: 0.6;
    filter: alpha(opacity=60);
    font-size: 14px;
    line-height: 20px;
    border-radius: 5px;
}


/*nav导航*/
.mainmenus { /*position:fixed;margin:0 auto; width:100%;*/
    /*background:url("images/navbg.png") repeat-x;*/
    background:#222222;position: relative;width: 100%;box-shadow:1px 2px 2px gray;
}
.home { float: left; height: 60px; width: 175px; background-image: url(images/logo.png) ; text-indent: -9999px;background-repeat: no-repeat;}/*顶部LOGO*/
.home_none { float: left; height: 60px; width: 175px; background-image: url(images/logo.png) ; text-indent: -9999px; background-repeat: no-repeat;}/*顶部LOGO*/
.home_none:hover { background-image: url(images/logo2.png)  }
.topnav { height: 60px;  font-size: 17px; /*font-weight: bold; */text-align: center; position:relative;text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.4); margin-left:-30px;}
.topnav a { color: #989898; height: 60px; font-size:16px;line-height: 60px;  }/*导航文字样式*/
.topnav a:hover  { color: #ef5b9c;}
.topnav ul { z-index: 999; }
.topnav li { height: 60px;line-height: 60px; float: left; position: relative; width: auto; transition: all 0.1s;box-sizing: border-box;}
.topnav li a:link, .topnav li a:visited { float: left; position: relative; display: block;padding:0 15px}
.topnav li a:hover, .topnav .current_page_item ,.topnav .current-menu-item,.topnav .current-post-parent{ /*background: #34495e;导航菜单颜色*/ float: left; position: relative; }
.topnav .color a{color: #ff4500}
.topnav .menu-item-has-children:after{position: absolute;right: 3px;top:28px;display: inline-block;content: '';width: 0;height: 0;border: 4px solid transparent;border-top:4px solid #ccc}
.topnav .menu-item-has-children .menu-children-ico{display: none}
.topnav ul ul {display:none;opacity:0;background-color: #333333;width: 800px;position: absolute; top: 57px; z-index: 999; left: 0; padding: 5px;margin: 0;}
.topnav ul ul:before{position: absolute;content: '';border: 8px solid transparent;border-bottom: 8px solid #333333;top:-16px;left: 40px;}
.topnav ul ul li { font-size: 13px; color: #363636; display: inline-block; position: relative; height: 35px; line-height: 35px; }
.topnav ul ul li a{transition: all 0.3s}
.topnav ul ul li a:link, .topnav ul ul li a:visited { padding:0;margin:0 3px;text-align: center;padding-top: 0;font-size: 14px; color: #ccc; display: inline-block; position: relative; width: 80px; height: 36px; line-height: 36px;   font-weight: normal; }
.topnav ul ul li a:hover { color: #ef5b9c;position: relative; font-weight: normal; }
.topnav ul ul ul { display: none; position: absolute; top: -1px; left: 190px; z-index: 999; }/*cuowu*/
.topnav ul ul ul li { font-size: 13px; color: #363636; display: block; position: relative; height: 36px; line-height: 36px; text-align: center; }
.topnav ul ul ul li a:link, .topnav ul ul ul li a:visited { font-size: 13px; color: #fff; display: block; position: relative; width: 150px; height: 36px; line-height: 36px; text-align: left; background: #363636; font-weight: normal; }
.topnav ul ul ul li a:hover { font-size: 13px; color: #fff; display: block; position: relative; width: 150px; height: 36px; line-height: 36px; text-align: left; background: #fd6ca3; font-weight: normal; }
.topnav .menu-button {display:none; position: absolute; top:8px; right:54px; cursor: pointer; }
.topnav .menu-button.active{background:rgba(0,0,0,0.2); border-radius:5px;}
.topnav .menu-button i{ display:block; width:100%; height:33px; background:url(images/icon.png) no-repeat -2px -236px;}
.menu-ico_span{color: #cccccc;float:right;background: none;height: 33px;line-height: 33px;}
.topnav .menu-right{ position:absolute; right:0; top:0}
.topnav .menu-right .menu-search{ position:relative;}
.topnav .menu-right #menu-search{ margin-top:8px; height:40px;width:14px;background: url(images/icon.png) no-repeat 5px -193px;}
.topnav .menu-right .menu-search .menu-search-form{ width: 200px; display:none; position:absolute; top:60px; right:0; background:#2c3e50; padding:15px; z-index:900}
.topnav .menu-right .menu-search .menu-search-form .button{border: none; background:#363636; color: #fff; padding: 6px 12px;}
.topnav .menu-right .current_page_item .menu-search-form{ display:block}
.topnav .menu-children-ico{ position: absolute;top:25px;right: 0px;color: #989898}
.subsidiary {height: 60px; padding: 0 10px; background:#fff; }
.bulletin { overflow: hidden; height: 40px; margin: 10px 0; line-height: 40px; ; border-radius: 5px; width:50%; background: url(images/gg.png) no-repeat #ffedc7 11px 11px; }
.sixth{ color: #999999;}
.sixth a{ color: #999999;}
.sywzad {float:left; height: 40px; line-height: 60px; width:25%;}
.sywzad a{ font-size:14px ; padding:0px 15px; color:#34495e;}
.sywzad a:hover{color:#3498db;}
.bdsharebuttonbox{ padding-top:10px; padding-left:-50px; float: left;}
.ggbaidu{ padding-top:5px; padding-left:-50px;float: right;}
.bulletin span { width: 70px; padding-left:10px; color:#6b3612;}
.bulletin marquee { color: #6b3612; }
.bdshare_small { margin-top: 10px; }
.triangle-down {  width: 0;  height: 0;border-left: 5px solid transparent;border-right: 5px solid transparent; border-top: 5px solid #a4a1a1;  display: inline-block;margin:0 0 0 5px;position: relative;  top:-2px;}
#mgssd_tips{text-align: center;font-size: 15px;color: #666;}


/*****************面包屑*******************/
.subsidiarys { background: #fff; height: 34px;}
.bulletins { overflow: hidden; height: 24px; margin: 5px 0; line-height: 24px; }
.bulletins span { width: 70px; }
.bulletins marquee { color: #999999; }
.bulletins a{ color: #999999; }
.bulletins { color: #999999; font-size:12px; }
.bdshares_small { margin-top: 5px; }

/*************************侧边栏***********************/
#sidebar { width: 280px; margin-left: 16px; float: right;}
#sidebar-follow { width: 316px; }
.widget { padding: 10px; }
.widget h3 { padding: 0; margin-bottom: 10px; height: 40px; line-height: 30px; border-bottom: #eff2f5  solid 1px; /*侧边栏*/font-size: 15px; font-weight: bold; color:#444}
.widget span { color: #fd6ca3; }
.widget em { color: #666; font-style: normal; margin-right: 20px; float: right; }
.widget ul { padding: 1px 0 1px 0; }
.widget ul li { line-height: 1.5em; border-bottom: dashed 1px #eff2f5 ; padding: 5px 0 }
.blogroll li { display: inline-block; margin-right: 10px }
/*文本*/
.textwidget { margin: -3px; overflow: hidden; width: 300px; }
.textwidget img { max-width: 300px; height: auto ;transition: all 0.4s}
.textwidget img:hover{opacity: 0.8}

.inter-top .textwidget { margin:0; overflow: hidden; width: auto; }
.inter-top .textwidget img { max-width: inherit; height: auto }
/*文章tab*/
#wzbt{position: relative;font-size: 20px;font-size: 2.0rem;line-height: 35px;text-align: center;padding: 7px 10px;font-weight: bold}
#tabnav { display: block; clear: both; zoom: 1; }
#tabnav li { float: left; width: 85px; border-bottom: #eff2f5  solid 1px; /*文章侧边框下线*/text-align: center; cursor: pointer; list-style: none; font-weight: bold; font-size: 15px; padding-bottom: 5px; margin-bottom: 5px; }
#tabnav .selected { position: relative; background-color: #fff; color: #fd6ca3; cursor: default; border-bottom: #eff2f5  solid 1px; }
#tab-content .hide { display: none; }
#tab-content ul { overflow: hidden; list-style: none }
#tab-content ul li { float: left; width: 100%; border-bottom: dashed 1px #eff2f5 ; background: url(images/zt_con_li.png) no-repeat left 12px;text-indent: 0.8em; }
#tab-content ul li a { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block }
/*评论*/
.r_comment { position: relative; overflow: hidden; height: auto; }
.r_comment ul { list-style: none; overflow: hidden; position: relative; }
.r_comment li { line-height: 22px !important; clear: both; height: 48px; margin-bottom: 5px; overflow: hidden; border-bottom: dashed 1px #eff2f5 ; }
.r_comment li:hover { border-right: #eff2f5 solid 3px; background: #f8f8f8; }
.r_comment ul li img.avatar { height: 35px; width: 35px; float: left; margin: 4px 8px 0 0; background: #fff; border: 1px solid #ddd; border-radius: 5px; }
/*登录*/
#loginform p { line-height: 26px; margin-bottom: 5px; }
#loginform input.login { width: 140px; padding: 2px; color: #444; border: 1px solid #dfdfdf; box-shadow: inset 2px 3px 5px #eee; }
#loginform input.denglu { width: 70px; margin-top: 5px; height: 63px; color: #444; text-align: center; border: 1px solid #dfdfdf; font-size: 16px; }
#loginform input.denglu:hover { background: #fd6ca3; color: #fff; }
.loginl { float: left; margin: 5px 10px 5px 0; }
.loginl label { margin-right: 10px; }
#loginform label input[type="checkbox"]{ vertical-align:middle; margin-right:3px}
#loginform input:focus { border: 1px solid #ccc; }
.register { margin: 0 10px 0 50px; }
.v_avatar { margin: 5px; float: left; width: 64px; }
.v_avatar img { border-radius: 5px; }
.v_li li { list-style-type: none; float: left; width: 100px; padding: 5px; }
/*标签*/
.tagcloud { height: auto; overflow: hidden; }
.tagcloud a:link, tagclouda:visited { font-size:12px; color:#999;padding: 3px 8px;  border:solid 1px #cccccc; margin: 2px; height: 20px; line-height: 30px; -moz-border-radius: 3px; border-radius: 3px; white-space: nowrap; -webkit-transition: background-color .15s linear, color .15s linear; -moz-transition: background-color .15s linear, color .15s linear; -o-transition: background-color .15s linear, color .15s linear; -ms-transition: background-color .15s linear, color .15s linear; transition: background-color .15s linear, color .15s linear; }
.tagcloud a:hover {  color: #fd6ca3; border:solid 1px #fd6ca3; }
.action { border-top: solid 1px #F3F3F3; margin-top: 5px; padding-top: 5px; text-align: right; }
.action a { color: #CCCCCC; }
/*图文*/
.imglist{ /*margin-left:-10px*/}
.imglist li{ width:280px; /*margin-left:10px;border-bottom:none !important; padding:0 !important;*/min-height: 70px;}
.imglist li h4{width:170px;float:left; margin:10px 0 10px 15px;height:20px;white-space: nowrap;text-overflow:ellipsis; overflow:hidden;}
.imglist li img{ float:left;width:65px; height:60px}
.imgtimes {float:left; font-size:12px; line-height:12px; margin-left:15px; color:#999;}
.imgtimes span { color:#999999}
.imgtimes a{ color:#999;}
.imgss{float:left; margin-top:5px; margin-bottom:5px;}
.post h4 {color:#444}
.post h4:hover {color:#fd6ca3}


/*日历*/
#wp-calendar{width: 100%;border-collapse: collapse;border-spacing: 0;  magrin:0 auto;       }
#wp-calendar #today{font-weight: 900; color: #990099 ;display:block;background-color: #F3F3F3; text-align:center;}
#wp-calendar thead{font-size:14px;}
#wp-calendar tfoot td{border-top:1px solid #F3F3F3;background-color:white; }
#wp-calendar tfoot td a{ color:#CCCCCC;}
#wp-calendar caption{font-size:15px;border-bottom: #eff2f5  solid 1px;padding:5px 0;margin-bottom:10px;}
#wp-calendar thead th{text-align:center;}
#wp-calendar tbody td{text-align:center;padding: 7px 0;}
#wp-calendar a {color: #990099; text-decoration: none; cursor:pointer;}
#wp-calendar a:hover {color:#fd6ca3 ; text-decoration:none;font-weight:900;}
/*首页文章列表*/
.mainleft { width: auto; overflow: hidden;margin-top: 50px;}
#post_container { margin-left: -16px; position:relative;}
#post_container li { display: block;width: 500px;margin-top:2px; width: 280px; margin-left: 18.5px; float: left; border: 1px solid #ccc; box-sizing: border-box; transition: all 0.2s; box-shadow:0px 2px  5px -3px gray; padding:2px;  }

/*

.post_hover { transition: all 0.3s  }

.post_hover:hover{ box-shadow:5px 5px 10px 1px gray;}

*/

#post_container li:hover{  box-shadow:0px 5px  6px -3px gray; position:relative; top:-1px; }

.thumbnail { max-height: 500px; overflow: hidden;  }
.thumbnail a { display: block; /*padding: 10px 10px 0 10px;*/ }
.thumbnail img {min-width: 280px; height: auto; }
.article { padding: 5px 10px 0px 10px;position:relative;}/*高度*/
.article h2{  line-height:1.5em; font-size:14px; font-weight:400;text-align: center;overflow: hidden}
.article h2 a{ color:#444444; }
.article h2 a:hover{ color:#fd6ca3;}
.info { margin-left:-2px;  margin-top:-10px; color: #9aabb8; margin-bottom:2px; /* white-space: nowrap;text-overflow: ellipsis; position: relative; border-top: 1px solid #DFDFDF; background: #F9F9F9; line-height: 25px; padding: 0 -2px;*/ /*text-align: center; */ }
.info span { height: 20px; line-height: 17px;font-size:12px;}
.info span a { color: #999999;  line-height:2em;}/*文章标题字颜色*/
.info span a:hover { color: #333333; }
.info_ico { background: url(images/info.png) no-repeat; padding: 0 5px 0 20px; }
.info_category { border-radius: 5px; /*background-color:#dfe5e9;*/ color:#9aabb8; padding:0px 0px 0px 5px; }
.info_categorys { border-radius: 5px; background-color:#dfe5e9; color:#9aabb8; padding:0px 5px 0px 5px; }
.info_date { background-position: 0 -1px; }
.info_views { background-position: 0 -62px; }
.info_comment { background-position: 0 -43px; }
.info_author { background-position: 0 -82px; }
.entry_post { line-height: 0px; color: #666; margin-bottom:0px; word-break: break-all; }
.entry_post  p{ padding-bottom:10px;}
.sticky { background: #fd6ca3; height: 25px; width: 45px; position: absolute; z-index: 20; top: -1px; right: -1px; color: #fff; font-weight: bold; text-align: center; line-height: 25px; }
.ssticky { font-size:14px;color:#FFF;padding-left:8px;height: 70px;width: 72px; line-height:2.8em;display: block;overflow: hidden;background-position: -314px 0;position: absolute;left:0;top:0;z-index: 10;}
.icons,.flex-direction-nav li a{background: url("./images/icons.png") no-repeat;}
.arrow-catpanel-top { position: absolute; /*background: url(images/arrow-catpanel-top.png) no-repeat 0px 0px;*/ width: 52px; height: 14px; bottom:-1px; left: 130px; z-index: 10; }
/*zoom { width: auto; height: auto; display: block; position: relative; overflow: hidden; background: none; }*/

/*.zoomOverlay { position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    display: none; !*margin: 10px 10px 0 10px;对应图像尺寸*!
    background-image: url(images/zoom.png);
    background-repeat: no-repeat;
    background-position: center;
    background-color:gba(247, 164, 164, 0.97) !important}*/
#post_container .fixed-hight h2 a{ /*display:block;*/white-space: nowrap;text-overflow:ellipsis; overflow:hidden;display: block;text-align: center}/*文章列表标题center无效因为这里有display*/
#post_container .fixed-hight .entry_post{overflow: hidden;height: 1px;}
#post_container .fixed-hight .info{ overflow:hidden; height:26px;}
#post_container .fixed-hight .thumbnail{height:159px; overflow: hidden;background:url("") no-repeat;background-size: cover;}

/*分页*/
.navigation.pagination a{transition: all 0.2s}
.pagination a,.pagination span { width: 40px; text-align: center; height: 40px; line-height: 40px; margin: 0px 0 0px 4px; display: inline-block; text-decoration: none; border-style:solid; border-width:1px; border-color:#ccc;color: #999; border-radius:3px;}
.pagination a.extend { padding: 0 5px;display: none; }
.pagination .current { height: 40px; width: 40px;color: #fd6ca3; border-style:solid; border-width:1px; border-color:#fd6ca3; margin: 20px 0 0 4px; margin-bottom:60px; }
.pagination a:hover { height: 40px; width: 40px; color: #fd6ca3; text-decoration: none; /*background: #348fca;*/ border-radius:3px;border-style:solid; border-width:1px; border-color:#fd6ca3;}
.pagination .page_previous, .pagination .prev { width: 80px; height: 40px; text-align: center; }
.pagination .page_previous:hover, .pagination .prev:hover { width: 80px; height: 40px; text-align: center; }
.pagination .page_next, .pagination .next, .pagination .page_next:hover, .pagination .next:hover { width: 80px; height: 40px; text-align: center; }
.pagination .fir_las, .pagination .fir_las:hover { width: 34px; height: 80px; text-align: center; }
/*single文章页面*/
.article_container { padding:30px;border: 1px solid #EEEEEE;box-shadow: 2px 2px 3px #EEE;position: relative}
.article_container h1 {/*文章页面对齐样式*/ color:#222222; margin-top:-10px; position: relative; font-size: 1.8em; line-height: 30px; text-align: center; padding: 7px 0; font-weight: bold;}
.article_info { text-align: left;/*文章页面对齐*/ margin-bottom:10px; line-height: 1.5em; color:#9aabb8;/*文章页文字颜色*/ font-size:12px; }
.xian { margin-left:-15px;  margin-right:-15px;border-bottom:#eff2f5 solid 1px;/*文章页标题下划线*/ margin-bottom:15px; line-height: 1.5em; color:#999;/*文章页文字颜色*/  }
.article_info a { color: #9aabb8 }
.article_info a:hover { text-decoration: underline;color: #9aabb8 }
.context { overflow: hidden; }
#post_content{ padding:10px 0px}/*缩近*/
#post_content a{ /*text-decoration:underline*/}
.context, .context p, .context pre { line-height: 2em; font-size: 14px;}
.context a{ color:#fd6ca3;font-size: 14px;line-height: 2em; }
.context ol, .context ul { margin-left: 40px; }
.context ol li, .context ul li { line-height: 2em; }
.context ol li { list-style-type: decimal; }
.context ul li { list-style: url(images/zt_con_li.png);}
.context h3,.context h4,.context h5{/*border-bottom:#dedede 1px solid;*/padding-bottom:2px;margin-bottom:10px;font-weight:bold;font-size:20px;padding-top:5px;}
.context h1{font-size:28px;font-weight:bold;}
.context .other{padding:10px 0;margin-bottom:15px;color: #555;font-size:18px;margin:15px 0;border-bottom: 1px solid #eaeaea;font-family: 微软雅黑,Microsoft Yahei,Verdana, Arial, Helvetica, sans-serif;font-weight:800;}
.context p embed, .context object { margin: 0 auto }
.context code { background: #FFF8DF; color: #9C2E0E; font-style: italic; padding: 2px 3px; line-height: 2em; }
.context table{border-top:solid 1px #ddd;border-left:solid 1px #ddd;width:100%;margin-bottom:16px}
.context table th{background-color:#f9f9f9;text-align:center}
.context table td,.article-content table th{border-bottom:solid 1px #ddd;border-right:solid 1px #ddd;padding:5px 10px}
.context .alignleft{float:left;text-align:left;margin-right:10px}
.context .aligncenter{text-align: center;display:block;margin:auto;}
.context .alignright{float:right;text-align:right;margin-left:10px}
.context .wp-caption {border: solid 1px #eee;border-radius: 2px;padding:5px;box-shadow: 2px 2px 0 #fbfbfb;margin-bottom: 15px; max-width:100%;}
.context .wp-caption:hover {border-color: #ddd;}
.context .wp-caption-text {margin:  5px -5px -5px;border-radius: 0 0 2px 2px;background-color: #fbfbfb;border-top: 1px solid #eee;padding: 5px;color: #999;}
.context .article_tags { font-size: 12px; line-height: 40px; margin-top: 15px; text-align: center; border-top: 1px #cdcdcd dashed; border-bottom: 1px #cdcdcd dashed; }
.context .img-responsive{display:block;height:auto;max-width:100%}
.baishare {  margin: 8px 0 0 0; _margin: 5px 14px 0 0; }
#authorarea { position: relative; float: left; padding:10px; line-height:20px; }
#authorarea{ width:300px;  float:left;}
#authorarea ul{ width:880px; }
#authorarea li{ width:270px; float:left; display:block;overflow:hidden; padding-right:10px;}
#authorarea li a { line-height:25px; display:block; word-break:keep-all; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.author_arrow { position: absolute; float: left; border-style: solid; border-width: 10px; /*border-color: transparent #fff transparent transparent;*/ height: 0; width: 0; font-size: 0; top: 42px; left: 80px; }
.authorinfo { height: 80px; padding-left: 110px; }
.post-navigation { clear: both; overflow: hidden;  }
.post-navigation div { display: block; position: relative; font-size: 14px; color: #999; }
.post-next { float: right; text-align: right; padding-right: 30px; }
.post-previous { float: left; padding-left: 30px; }
.post-navigation div a:after { position: absolute; color: #CCC; font-size: 36px; margin-top: -11px; height: 22px; line-height: 22px; top: 34%; }
.post-previous a:after { content: '«'; left: 0px; }
.post-next a:after { content: '»'; right: 0px; }
/*相关文章*/
.articlecc { padding: 5px 10px 0px 10px;position:relative;height: 20px;
}/*高度*/
.articlecc h2{  line-height:1.5em; font-size:14px; font-weight:600; overflow: hidden;
}
.articlecc h2 a{ color:#444444; width:250px;display:block; word-break:keep-all; white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
.articlecc h2 a:hover{ color:#fd6ca3;}
.thumbnailcc {height: 150px; overflow: hidden; }
.thumbnailcc a { display: block; /*padding: 10px 10px 0 10px;*/ }
.thumbnailcc img {width: 100%;height: auto;transition: all 0.3s}
.related { float:left; }
.related ul { width:950px;  }
.related ul li{ width:280px; float:left; margin-right:20px;overflow: hidden;}
.related ul li:hover img{opacity: 0.8}
.related_box { float: left; width: 280px; height: 285px;}
.related_box:hover { background-color:#f0f2f7;  }/*颜色*/
.related_box a:hover {color:#779ed4 }
.related_box .r_title { padding: 0 8px; text-align: center; }
.related_box .r_pic { margin: 8px auto; width: 140px; height: 94px;}
.related_box .r_pic img { width: 140px; height: 94px; }
#content table, #content button { margin: 10px auto; }
#content p { margin: 0 0 20px 0 }
#content hr { background: url(images/sprite-2.png) no-repeat -1px -93px; height: 3px; border: none; margin: 15px 0 }
#content .content_post ol li { list-style: decimal inside; color: #272727; line-height: 26px; font-size: 13px }
#content .content_post ul li { background: url(images/li.png) no-repeat; text-indent: 1.3em; color: #272727; line-height: 26px; font-size: 13px }
#content b, #content strong { font-weight: blod }
#content i, #content em, #content var, #content dfn { font-style: italic }
#content th, #content td { display: table-cell; vertical-align: inherit; padding: 1px; line-height: 2em }
#content th { font-weight: 700; padding: 1px }
#content td { text-align: inherit; padding: 1px }
#content .pagelist { padding: 10px 0; background: #f3f3f3; text-align: center; margin-top: 20px ;}
#content .pagelist>span,#content .pagelist>a{background-color: #fff ;/*border: 1px#ddd solid ;*/color: #99a1a7;margin-left: 5px;padding: 4px 10px ;text-transform: uppercase; border-radius:3px}
#content .pagelist>a:hover,#content .pagelist>span{background-color: #348fca;color: #fff !important;}
#content .pagelist a { margin-right: 10px }
.alignleft { float: left; margin: 5px 15px 5px 0 }
.alignright { float: right; margin: 5px 0 5px 15px }
/*comments*/
#comments { font-size: 15px; font-weight: bold; margin-left: 10px; height:auto; padding-top: 20px;  }
#comments_box .navigation{ margin-right:10px; font-size:12px}
#comments_box .pagination a,#comments_box .pagination span,#comments_box .pagination .current{ line-height:20px; height:20px}
#respond_box {  font:  微软雅黑,Microsoft Yahei,Verdana, Arial, Helvetica, sans-serif; }
#respond { margin: 10px 10px 20px 10px; border-top: 1px solid #dedede; padding-top: 10px; }/*评论线*/
#respond p { line-height: 30px; text-align: right; }
#respond h3 { font-size: 16px; font-weight: bold; line-height: 25px; height: 25px; }
.comt-box { border: solid 1px #DDD; border-color: #C6C6C6 #CCC #CCC #C6C6C6; border-radius: 3px; padding: 8px; box-shadow: inset 2px 0 2px #F2F2F2, inset 0 2px 2px #EEE, 0 2px 0 #F8F8F8, 2px 0 0 #F8F8F8; background-color: white; clear: right; }
.comt-area { _margin-top: -35px; border: 0; background: none; width: 100%; font-size: 12px; color: #666; margin-bottom: 5px; min-height: 70px; box-shadow: none; }
.comt-ctrl { position: relative; margin: 0 -8px -8px; _margin-right: -10px; height: 32px; line-height: 32px; border-radius: 0 0 3px 3px; border-top: solid 1px #DDD; background-color: #FBFBFB; box-shadow: inset 0 1px 0 #FBFBFB; color: #999; }
.comt-submit { position: absolute; right: -1px; top: -1px; border: solid 1px #CCC; height: 34px; width: 120px; cursor: pointer; font-weight: bold; color: #666; font-size: 12px; border-radius: 0 0 3px 0; background-image: -webkit-linear-gradient(#F6F6F6, #E2E2E2); text-shadow: 0 -1px 0 white; }
#comment-author-info { margin-bottom: 10px; height: 27px; }
#comment-author-info label { margin-left: 5px; }
#comment-author-info input { width: 20.5%; margin-left: -4px; margin-top: -5px \9; vertical-align: middle \9; }
.comment_input { margin-left: 27px; }
#real-avatar { float: left; width: 27px; }
#real-avatar img { width: 27px; height: 27px; }
.comt-addsmilies, .comt-addcode { float: left; color: #888; padding: 0 10px; }
.comt-smilies { display: none; position: absolute; top: 0; left: 40px; height: 30px; background-color: #FBFBFB; overflow: hidden; }
.comt-smilies a { float: left; padding: 8px 1px 0px; }
.comt-num { font-size: 12px; color: #999; float: right; margin-right: 140px; }
.comt-num em { font-weight: bold; font-size: 14px; }
.commentlist .comment { list-style: none; border-top: 1px solid #ddd; }
.commentlist li.comment ul.children { margin-left: 20px; }
.commentlist .depth-1 { margin: 0; }
.commentlist li { position: relative; }
.commentlist .thread-even { background: #fafafa; }
.commentlist .comment-body { padding: 10px; border-left: 5px solid transparent; }
.commentlist .comment-body:hover { background: #f5f5f5; border-left: 5px solid #fd6ca3; }
.commentlist .comment-body p { margin: 5px 0 5px 50px; line-height: 22px; }
.reply a:link, .reply a:visited { text-align: center; font-size: 12px; }
.datetime { font-size: 12px; color: #aaa; text-shadow: 0px 1px 0px #fff; margin-left: 50px; }
.commentmetadata { font-size: 12px; color: #aaa; text-shadow: 0px 1px 0px #fff; margin-left: 50px; }
ol.commentlist li div.vcard img.avatar { width: 40px; height: 40px; position: relative; float: left; margin: 4px 10px 0 0; border-radius: 5px; }
ol.commentlist li div.floor { float: right; color: #bbb }
.children li.comment-author-admin { border-top: #dedede solid 1px; }
/*footer*/
#footnav a, #friendlink a { color: #666666; font-size:10px; }
#footnav a:hover, #friendlink a:hover { color: #fd6ca3}
#footer { text-align: center; background: #1a1a1a; padding: 20px 0 15px 0; font-size: 12px; color: #666666; line-height: 1.5em; box-shadow: 0px -2px 3px gray;margin-top: 30px;}
#footer p { text-align: center; }
.footnav { line-height: 30px; font-size: 12px; }
.footnav ul { list-style: none; text-align: center; }
.footnav ul li { height: 30px; line-height: 30px; display: inline; padding: 0 10px 0 0; }
.footnav ul ul { display: none; }
.copyright { color: #666666;font-size:12px;}
.copyright p{ line-height:2em }
.copyright a { color: #666666; font-size:12px;}
.copyright a:hover { color: #fd6ca3; }
#footer p.author a { color: #666666; }
#footer p.author a:hover { text-decoration: underline }
#footer .footer_about p span{color: orangered}
#footer .footer_about p span:after{content: '友链及广告合作请联系QQ：'}

/*gototop*/
#tbox { width:45px; float: right; position: fixed; right: 20px; bottom: 150px; }
#pinglun, #home, #gotop { width:45px; height:45px; background: #fd6ca3 url(images/icon.png) no-repeat; display: block; margin-bottom: 5px; filter: alpha(Opacity=50); -moz-opacity: 0.5; opacity: 0.5; }
#pinglun:hover, #home:hover, #gotop:hover { filter: alpha(Opacity=100); -moz-opacity: 1; opacity: 1; }
#pinglun { background-position: 0 -50px;display: none }
#home { background-position: 0 5px; }
#gotop { background-position: 0 -100px; }
/*幻灯*/
/*.slider {!* border:10px solid #FFF;width: 648px;*! overflow: hidden; padding-top:10px;}!*边框*!
#focus { width: 100%; height: 370px; overflow: hidden; position: relative; }
#focus ul { height: 430px; position: absolute; }
#focus ul li { float: left; width: 648px; height: 370px; overflow: hidden; position: relative; background: #ccc; }
#focus ul li div { position: absolute; overflow: hidden; }
#focus .button { position: absolute; width: 648px; height: 10px; padding: 5px 10px; right: 0; bottom: 0; text-align: right; }
#focus .button span { display: inline-block; _display: inline; _zoom: 1; width: 25px; height: 10px; _font-size: 0; margin-left: 5px; cursor: pointer; background: #fff; }
#focus .button span.on { background: #fff; }
#focus .preNext { width: 45px; height: 100px; position: absolute; top: 125px; background: url(images/sprite.png) no-repeat 0 0; cursor: pointer; }
#focus .pre { left: 0; }
#focus .next { right: 0; background-position: right top; }
#focus ul li a { display: block; overflow: hidden; }
#focus ul li a img { width: 650px; height: auto; }
.flex-caption { float:right;  background: #fff; border:10px solid #FFF;opacity: 0.8; color: #fff; height: 430px;padding: -20px -40px;}
.flex-caption a { color: #999; }
.flex-caption:hover { opacity: 1; }
.flex-caption .btn { display: none; }
.slides_entry { display: none; }
!*读者墙*!*/
/*.readers-list { line-height: 19px !important; text-align: left; overflow: hidden; _zoom: 1;}
.readers-list li { width: 200px; float: left; *margin-right:-1px}
.readers-list a, .readers-list a:hover strong { background-color: #f2f2f2; background-image: -webkit-linear-gradient(#f8f8f8, #f2f2f2); background-image: -moz-linear-gradient(#f8f8f8, #f2f2f2); background-image: linear-gradient(#f8f8f8, #f2f2f2) }
.readers-list a { font-size:12px;  line-height:19px !important; position: relative; display: block; height: 36px; margin: 4px; padding: 4px 4px 4px 44px; color: #999; overflow: hidden; border: #ccc 1px solid; border-radius: 2px; box-shadow: #eee 0 0 2px }
.readers-list img, .readers-list em, .readers-list strong { -webkit-transition: all .2s ease-out; -moz-transition: all .2s ease-out; transition: all .2s ease-out }
.readers-list img { width: 36px; height: 36px; float: left; margin: 0 8px 0 -40px; border-radius: 2px }
.readers-list em { color: #666; font-style: normal; margin-right: 10px }
.readers-list strong { color: #ddd; width: 40px; text-align: right; position: absolute; right: 6px; top: 4px; font: bold 14px/16px microsoft yahei }
.readers-list a:hover { border-color: #bbb; box-shadow: #ccc 0 0 2px; background-color: #fff; background-image: none }
.readers-list a:hover img { opacity: .6; margin-left: 0 }
.readers-list a:hover em { color: #fd6ca3; font: bold 12px/36px microsoft yahei }
.readers-list a:hover strong { color: #fd6ca3; right: 150px; top: 0; text-align: center; border-right: #ccc 1px solid; height: 44px; line-height: 40px }
.readers-list span.name{word-break:break-all; max-width:120px; display:block}*/
/*文章归档*/
.articles_all { line-height: 35px; padding-left: 15px; border-top: #dedede solid 1px }
.car-container { padding: 0 15px 10px 15px; }
.car-collapse .car-yearmonth { cursor: s-resize; }
a.car-toggler { line-height: 30px; font-size: 14px; color: #c30 }
.car-list li { list-style: none; line-height: 24px }
.car-list li ul { padding-left: 30px }
.car-plus, .car-minus { width: 15px; display: block; float: left; font-family: Courier New, Lucida Console, MS Gothic, MS Mincho; }
.car-monthlisting span { color: #ccc; }
.new { float: left;; margin-top:5px;}

/*友情链接*/
.flink, .linkstandard { list-style: none; }
.flink ul ul, .linkstandard ul { padding: 0 15px 10px 15px; list-style: none; line-height: 24px; }
.flink ul ul li { float: left; height: 30px; width: 25%; overflow: hidden; line-height: 30px; }
.flink ul li h2, .linkstandard h2 { clear: both; font-size: 16px }
/*页面*/
.cont_none ul, .cont_none ul li { list-style: none; margin: 0; }
/**/
.toppostbox{ margin-right:6px; float: right;/*border:10px solid #FFF;*/ width:315px;height:370px;position:relative;overflow:hidden; }
.toppostbox li{float:right;width:330px;height:55px;margin-bottom: 1px ;padding:9px;background:/*#f5f5f5*/#FFF;/*padding:8px 0px 10px 180px; margin: 0px -15px 1px 0px;*/}
.toppostbox img{float:left;width:86px;height:55px;position:relative;}
.toppostinfo{float:left;width:164px;height:55px;padding-left:40px;line-height:18px;position:relative;}/*随机文字位置*/
.topposttitle{width:164px;white-space:nowrap;overflow:hidden;-o-text-overflow:ellipsis;text-overflow:ellipsis;}
.topposttitle a{font-size:14px;line-height:1.5;}
.topposttitle a:hover{color:#fd6ca3;}
.toppostdate{float:right;width:164px;font-size:12px;color:#999;line-height:1.5;}
.sysjt {float:right;margin-right:10px; }/*随机图片位置*/
/*资讯列表*/
.spost_list{margin-bottom:00px;padding:10px 30px 10px 15px;background-color:#FFF;/*box-shadow:0 1px 2px #CCC;*/overflow:hidden; border-bottom:#eff2f5 solid 1px;white-space: nowrap;text-overflow:ellipsis; overflow:hidden; }
.spost_list:hover{ /*box-shadow: #b8c4d1 0px 0px 5px;*/ background-color:#f9f9f9; }
.spost_list h2{padding:10px 10px 10px 0px; overflow:hidden;text-overflow:ellipsis}
.spost_list h2 a{color:#444444;font-size:18px;overflow:hidden;white-space:nowrap}
.spost_list h2 a:hover{color:#fd6ca3;text-decoration:none}
.sexcerpt{margin-top:10px;line-height:18px; color:#444;}
.sexcerpt h2{padding:10px 10px 10px 0px; overflow:hidden;text-overflow:ellipsis}
.sexcerpt h2 a{color:#444444;font-size:18px;overflow:hidden;white-space:nowrap; font-weight:600; }
.sexcerpt h2 a:hover{color:#fd6ca3;text-decoration:none}
.sexcerpt p{ line-height:25px; color:#999}
.smore{padding-left:20px}
.smeta{font-size:12px;clear:both;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;color:#999;border-top:1px solid #EEE;margin:20px -30px 0 -30px;padding:10px 30px 0 30px}
.smeat_span{margin-right:15px}
.smeta a{color:#444}
.smeta a:hover{color:#444;text-decoration:underline}
.sthumbnail{float:left;padding:4px;/*border-radius:3px;border:1px solid #ccc;background:#f9f9f9;box-shadow:1px 1px 2px #d3d3d3;*/margin:0 15px 15px 0;}
.sthumbnail img{display:block;width:236px;height:150px;border-radius:5px;}

.smore{padding-left:20px;}
.2thumbnail { max-height: 500px; overflow: hidden;}
.2thumbnail a { display: block; /*padding: 10px 10px 0 10px;*/ }
.2thumbnail img { width: 330px; height: auto; }
.2zoom { width: auto; height: auto; display: block; position: relative; overflow: hidden; background: none; }
.2zoomOverlay { position: absolute; top: 0; left: 0; bottom: 0; right: 0; display: none; /*margin: 10px 10px 0 10px;对应图像尺寸*/ background-image: url(images/zoom.png); background-repeat: no-repeat; background-position: center;}
.sinfo { padding:0px 0px 5px 15px; color: #999;   /* white-space: nowrap;text-overflow: ellipsis; position: relative; border-top: 1px solid #DFDFDF; background: #F9F9F9; line-height: 25px; padding: 0 -2px;*/ /*text-align: center; */}
.sinfo span { height: 20px; line-height: 17px; font-size: 12px; color:#9aabb8;margin-left:-5px; }
.sinfo span a {  line-height:2;  color: #999;  }
.sinfo span a:hover { color: #9aabb8; }
.sinfo_ico { background: url(images/info.png) no-repeat; padding: 0 5px 0 20px; }
.sinfo_date { background-position: 0 -1px; }
.sinfo_views { background-position: 0 -62px; }
.sinfo_comment { background-position: 0 -43px; }
.sinfo_author { background-position: 0 -82px; }
.syad {width:auto 0; padding:40px 0px 5px 0px;text-align:center;margin-left:auto; margin-right:auto; background-color:#141414;}
.syads {width:auto 0; padding:0px 0px 5px 0px;text-align:center;margin-left:auto; margin-right:auto;}

/*文字广告*/
.bannerx{margin-bottom:10px;padding:10px 15px;border:solid 1px #bce8f1;border-radius:5px;background:#d9edf7;color:#31708f;font-size:14px; margin:10px 0px;}/*蓝*/
.banner{margin-bottom:5px;padding:5px 15px;border:solid 1px #faebcc;border-radius:5px;background:#fcf8e3;color:#a66d3b;font-size:14px; margin-top:30px;}/*黄*/
.banner lan{margin-bottom:10px;padding:10px 15px;border:solid 1px #d6e9c6;border-radius:5px;background:#dff0d8;color:#3c763d;font-size:14px}/*绿*/
.banner lan{margin-bottom:10px;padding:10px 15px;border:solid 1px #ebccd1;border-radius:5px;background:#f2dede;color:#a94442;font-size:14px}/*红*/
.banner a { font-weight:bold; color:#F00}
#blognamess{ display: none  }
.left { float:left}
.indexPart2Right ul li{ list-style-type: decimal; }
.indexPart2Right { border-radius:5px; width:260px;height:auto;padding:20px 10px 20px 10px; margin-left:20px;white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.indexPart2Right:hover { }
.indexPart2Right li { width:260px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:5px; _margin-top:14px;}
.indexPart2Right li a {white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:260px; color:#666;  font-size:12px;}
.indexPart2Right li a:hover { color:#fd6ca3; }
.indexPart2Right li span {
    display:inline-block;
    margin-right:8px;
    background:#ff6100;
    width:22px;
    text-align:center;
    color:#fff;
    transition:all .5s ease-out;
    -webkit-transition:all .5s ease-out;
    -moz-transition:all .5s ease-out;
    -o-transition:all .5s ease-out;
    -ms-transition:all .5s ease-out
}
.indexPart2Right li:hover span {
    transform:rotate(360deg);
    -webkit-transform:rotate(360deg);
    -ms-transform:rotate(360deg);
    -moz-transform:rotate(360deg)
}
.indexPart2Right h3 {
    font:bold 14px/normal 'MicroSoft Yahei';
    color:#ddd;

    width:260px;
}
.indexPart2Right h3 span a {
    float:right;
    font-size:12px;
    color:#666;
    background-color:#222222;
    padding:0 5px;
    border-radius:3px;
}
.indexPart2Right h3 span a:hover {
    float:right;
    font-size:12px;
    color:#fff;
    background-color:#fd6ca3;
    padding:0 5px;
    border-radius:3px;
}
.fens{
    background-color:#141414;

    padding-top:20px;
    padding-bottom:20px;
}
/*new jia*/
#container {
    margin:0 auto;
    padding:0px 0px 10px 0
}
#content .single-container {
    width:1200px;
    margin:20px 0 40px 0;
    padding:40px;
    height:auto
}
#content .review {

    margin-top:20px;
    padding:0px
}
.archive-header-info {
    text-shadow:0 1px 0 #FFF;
    color:#333
}
.archive-header-info {
    width:70%;
    margin-right:0
}
.archive-description {
    font-size:15px;
    line-height:18px;
    font-weight:300
}
.archive-description a {
    color:#fd6ca3;
    font-weight:600
}
.archive-description {
    color:#777
}
.archive-description {
    margin-bottom:40px
}
.header-logo a, .archive-title, .archive-title h1, .review .review-title h1, .similar-title, .single-title, .single-container h1, .single-container h2, .single-container h3, .footer-column h3, .footer-promo-title, .thumb .thumb-info .thumb-title .thumb-name h2, #header-bottom-left ul li a, .notice, .dashboard-section {
    font-weight:700;
    letter-spacing:-1px
}
.archive-title {
    font-size:30px;
    line-height:32px
}
.archive-title h1 {
    font-size:32px;
    line-height:32px
}
.archive-title {
    padding-top:15px;
    margin-bottom:10px
}
.archive-header-info {
    float:left;
    width:840px;
    margin-right:55px
}
.archive-header-ad {
    float:left;
    width:280px
}
.review-cats{color:#AAA; margin-top:20px; }
.review-cats a
{line-height:3em;
    -webkit-border-radius:4px;
    -moz-border-radius:4px;
    border-radius:4px
}
.review-cats a {
    font-weight:300
}
.review-cats a {
    color:#AAA;
    border:1px solid #ccc;
    text-transform:capitalize
}
.review-cats a:hover {
    color:#FD6CA3;
    border:1px solid #FD6CA3
}
.review-cats {
    line-height:30px;
    margin-bottom:20px
}
.review-cats strong
{color:#666666;
    font-weight:normal;
    display:block;
    font-size:8px;
    text-transform:uppercase;
    line-height:10px;
    margin-bottom:10px
}

.review-cats a {
    height:30px;
    padding:4px 9px;
    text-decoration:none;
    margin:0 5px 30px 0 !important;
    white-space:nowrap;
    background:none
}
/**/
.floating-pagi a {
    z-index:1000
}
.floating-pagi a {
    display:block;
    position:fixed;
    top:50%;
    width:60px;
    height:60px;
    outline:none
}
.floating-pagi .floating-pagi-next a {
    left:30px;
    -webkit-transform:rotate(-180deg);
    -moz-transform:rotate(-180deg);
    -ms-transform:rotate(-180deg);
    -o-transform:rotate(-180deg);
    filter:progid:DXImageTransform.Microsoft.BasicImage(rotation=3)
}
.floating-pagi .floating-pagi-prev a {

    right:30px
}
.floating-pagi svg {
    width:60px;
    height:60px
}
.floating-pagi svg {
    fill:#999
}
.floating-pagi:hover svg {
    fill:#FD6CA3
}
.floating-pagi a:hover {
    border:none;
    text-decoration:none
}
/*PCsearch*/
#header-bottom-right {display: none; width:170px; margin:0; padding:8px 15px;position: absolute; right: 0; top:60px; background-color: #313030;}
#header-bottom-right .search { width: 100%;  border: 1px solid gray; }
#header-bottom-right .search-field-holder { width: 100%;}
#header-bottom-right .search-field-holder .search-field { display: inline-block; width: 130px; padding: 5px 0; height: 18px; text-indent: 5px; background:#fbfafa;transition: all 0.2s; }
#header-bottom-right .search-field-holder .sousuo{ width: 32px;height: 32px; background: url("images/search-bottom.png") no-repeat;  float: right;  display: inline-block; border: none; }
#header-bottom-right .search-field-holder .search-field:hover{ background: #fff}
#header-bottom-right .search-field-holder .sousuo:hover{opacity: 0.8}
.search-button-top{position: absolute;right: 0;top:50%;margin-top: -15px;z-index: 99999}
.search-button-top button{height: 32px;width: 32px;background: url("images/search-top.png") no-repeat;border: none;opacity: 0.7;transition: all 0.2s;}
.search-button-top button:hover{opacity: 1}

.header-search {
    clear:both;
    float:none;
    width:360px;
    display:block;
    position:absolute;
    top:50px;
    margin-left:20px;
    z-index:10000;
    border-bottom:1px solid #000;
    box-shadow:0 1px 0 #222;
    padding-bottom:20px
}
.search {
    width:345px;

}
.header_search_button{
    float: right;
    height: 28px;
    line-height: 28px;
    border: none;
    border-radius: 5px;
    background-color: #eee;
}
.header_search_button:hover{ background-color: #fff;}
/*文章列表*/
#copost_container { margin-left: -16px; position:relative; }
#copost_container li { margin-top:2px; width: 280px; margin-left: 18.5px; -webkit-transition: all .7s ease-out .1s; -moz-transition: all .7s ease-out; -o-transition: all .7s ease-out .1s; transition: all .7s ease-out .1s; float: left; }
.copost_hover { padding:5px;   }
.copost_hover:hover { /*border-bottom: #b8c4d1 solid 1px; box-shadow: #fff 0px 0px 5px;*/}/*文章列表下划线*/
.cothumbnail { max-height: 500px; overflow: hidden; height:100px; }
.cothumbnail a { display: block; /*padding: 10px 10px 0 10px;*/ }
.cothumbnail img {min-width: 270px;  min-height:100px;height: auto; }
.coarticle { position:relative;  }/*高度*/
.coarticle h2{  line-height:3em; font-size:16px; font-weight:600;  }
.coarticle h2 a{ color:#444444; }
.coarticle h2 a:hover{ color:#fd6ca3;}
.coinfo {color: #444;  white-space: nowrap;text-overflow: ellipsis; position: relative; padding: 10px 0px; margin-top:-20px; font-size:12px;}
.coinfo span{font-weight:bold; line-height:1.8em}
.coentry_post { line-height: 22px; color: #666; margin-bottom: 5px; word-break: break-all; }
.sticky { background: #fd6ca3; height: 25px; width: 45px; position: absolute; z-index: 20; top: -1px; right: -1px; color: #fff; font-weight: bold; text-align: center; line-height: 25px; }
.ssticky { font-size:14px;color:#FFF;padding-left:8px;height: 70px;width: 72px; line-height:2.8em;display: block;overflow: hidden;background-position: -314px 0;position: absolute;left:0;top:0;z-index: 10;}
.icons,.flex-direction-nav li a{background: url("./images/icons.png") no-repeat;}
.arrow-catpanel-top { position: absolute; /*background: url(images/arrow-catpanel-top.png) no-repeat 0px 0px;*/ width: 52px; height: 14px; bottom:-1px; left: 130px; z-index: 10; }
.zoom { width: auto; height: auto; display: block; position: relative; overflow: hidden; background: none; }
/*

.zoomOverlay { position: absolute; top: 0; left: 0; bottom: 0; right: 0; display: none; !*margin: 10px 10px 0 10px;对应图像尺寸*! background-image: url(images/zoom.png); background-repeat: no-repeat; background-position: center; background-color:rgba(247, 164, 164, 0.97) !important}
*/

#copost_container .fixed-hight h2 a{ display:block;white-space: nowrap;text-overflow:ellipsis; overflow:hidden;}
#copost_container .fixed-hight .coentry_post{overflow: hidden;height: 42px;}
#copost_container .fixed-hight .coinfo{ overflow:hidden; height:140px; width:270px;}
#copost_container .fixed-hight .cothumbnail{height:110px;; overflow: hidden;}
.cobox { background: #fff; /*border: solid 1px #d9dbdd; border-bottom-color:#dcdee0;*/}
.coboxx{}

/*全屏幻灯代码*/
#sliderbox {
    position:relative;
    clear:both;
    overflow:hidden
}
#slidebanner {
    width:1900px;
    height:500px;
    margin-left:-950px;
    text-align:center;
    _text-align:left;
    overflow:hidden;
    position:relative;
    left:50%;
    z-index:90;
    clear:both
}
#slideshow li {
    width:1900px;
    height:500px;
    position:absolute;
    left:0;
    top:0
}
#slideshow li img {
    width:1900px;
    height:500px;
    display:block
}
#slidebanner .bx-wrapper {
    height:auto
}
#slidebanner .bx-wrapper .bx-pager {
    width:100%;
    text-align:center;
    position:absolute;
    left:0;
    bottom:10px;
    z-index:90
}
#slidebanner .bx-wrapper .bx-pager .bx-pager-item, #slidebanner .bx-wrapper .bx-controls-auto .bx-controls-auto-item {
    display:inline
}
#slidebanner .bx-wrapper .bx-pager a {
    margin-left:10px;
    width:48px;
    height:4px;
    font-size:0;
    background:#fff;
    overflow:hidden;
    display:inline-block;
    text-decoration:none;
    moz-border-radius:50px;
    -webkit-border-radius:50px;
    border-radius:50px
}
#slidebanner .bx-wrapper .bx-pager a.active {
    background:#2c4476
}
#sliderbox .bx-prev, #sliderbox .bx-next {
    width:60px;
    height:100%;
    _height:400px;
    text-indent:-9999px;
    background:url(images/arrow-slider.png) no-repeat -50px 48%;
    overflow:hidden;
    display:none;
    position:absolute;
    top:0;
    z-index:100;
    filter:alpha(opacity=60);
    -moz-opacity:.6;
    opacity:.6
}
#sliderbox .bx-prev {
    left:3%;
    _left:69%
}
#sliderbox .bx-next {
    right:3%;
    background-position:10px 48%
}
#sliderbox .bx-prev:hover, #sliderbox .bx-next:hover {
    filter:alpha(opacity=100);
    -moz-opacity:1;
    opacity:1
}
.bx-controls-auto {
    display:none
}
.banner-shadow {
    width:100%;
    height:25px;
    background:url(images/shadow.png) repeat;
    overflow:hidden
}
.banner {
    text-align:center;
    background:#eee;
    overflow:hidden;
    position:relative
}
.banner img {
    width:100%;
    display:block
}

/*mycss*/
#center_span{width: 450px;
    height: 60px;
    line-height: 60px;
    text-align: center;
    background: #fee9ea url(images/warning.png) no-repeat 5px center;
    border: 1px solid #de888a;
    -moz-border-radius: 5px;
    -webkit-border-radius: 5px;
    border-radius: 5px;
    font-size: 20px;
    margin: 0 auto;
    margin-bottom: 20px;


}
#center_title{color: red;}
#center_title:hover{color: deeppink}
#shenming{
    font-size: 15px;
    margin: 30px auto;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #f6ceba;
    color:#ff4500

}

#shenming p{
    padding: 0px;
    margin: 0;
    

}
#shenming p a{
color: blue;

}

#shenming .shenming_link a{
color: #ff4500

}


#download{
    margin: 1px auto;width: 100%;height: 100%;text-align: center;
}
#download a{display: inline-block;width: 300px;}
#download img:hover{
    opacity: 0.8;
}
.padd{display: none}
/*about*/
.about{width: 90%;padding: 15px;margin: 0 auto;text-align: center;background-color: white;transition: all 0.3s}
.about .about_tab{margin: 0 auto;height: auto;text-align: center;width: 350px;margin-bottom: 20px;}
.about .about_tab a{text-align: center;width: 150px;color: #666;height:40px;line-height: 40px;display:inline-block;margin: 0 1px;font-size: 18px;border:1px solid orangered;color: black;}
.about .about_tab .about_tab_one{background-color: orangered;color: white}
.about .about_tab a:hover{background-color: #fe652c;color: white}
.about .about_tab .about_tabl{border-radius: 20px 0px 0px 20px;}
.about .about_tab .about_tabr{border-radius: 0px 20px 20px 0px;}
.about .about_content{height: auto;margin-bottom: 200px;}
.about .about_content p{width: 80%;margin: 0 auto;font-size: 17px;line-height: 34px;color: #666}
.about .about_right{display: none}
.about .about_content h4{font-size: 25px;width:100%;text-align: center;margin-top: 40px;}
.about .about_content .about_mgs{width: 550px;height: 150px;margin:0 auto;background-image: linear-gradient(120deg, #f093fb 0%, #f5576c 100%);padding: 0 30px;margin: 20px auto;border-radius: 3px;transition: all 0.2s}
.about .about_content .about_mgs .about_mgsl{height: 100%;width:170px;;display: inline-block}
.about .about_content .about_mgs .about_mgsl img{width: 172px;height: 45px;position:relative;top: 50%;margin-top: -22px;}
.about .about_content .about_mgs .about_mgsr{width: 300px;height: 100%; ;float: right;padding:0;}
.about .about_content .about_mgs .about_mgsr p {font-size: 15px;line-height: 25px;color: #eee;margin: 0;width: 100%;margin-top: 10px;}
.about .about_content .about_mgs .about_mgsr .about_mgsr_title {color: white;font-size: 20px;font-family:verdana}

.about .about_content .about_dmm{background-image: linear-gradient(120deg, #84fab0 0%, #1fb835 100%);}
.about .about_content .about_dmm .about_mgsl  img{height: 75px;position:relative;top: 50%;margin-top: -37px;}
.about .about_content .about_r18{background-image: radial-gradient(circle 248px at center, #16d9e3 0%, #30c7ec 47%, #46aef7 100%);}
.about .about_content .about_r18 .about_mgsl img{height: 60px;position:relative;top: 50%;margin-top: -30px;}
.about .about_content .about_mgs:hover{-moz-box-shadow:0px 0px 20px #8C8C8C; -webkit-box-shadow:0px 0px 20px #8C8C8C; box-shadow:0px 0px 20px #8C8C8C;}
.about .about_content .about_if{width: 100%;text-align: center;font-size: 20px;color: black;margin: 40px 0;color: #666}

.about .about_content .about_contact{width: 100%;text-align: center;font-size: 20px;margin-top: 40px;}
.about .about_content .about_contact a{border: 1px solid #3498DB;padding: 10px 100px;transition: all 0.3s;border-radius: 20px;color: black;font-weight: 500;}
.about .about_content .about_contact a:hover{background-color: #3498DB;color: white;-moz-box-shadow:0px 0px 10px #8C8C8C; -webkit-box-shadow:0px 0px 10px #8C8C8C; box-shadow:0px 0px 10px #8C8C8C;}
.about .about_content .about_pc_qq{display: none;background-color: #f2dede;color: #b94a48;width: 286px;font-size: 14px;text-align: center;;height: auto;margin-top: 15px;border: 1px solid #eed3d7;border-radius: 5px;}
.about .about_content .about_mobile_qq{display: none;color: black;width: 100%;text-align: center}
.about .about_content .about_mobile_qq a{display: inline-block}

/*正在跳转付款页面*/
#open_js{position: absolute;top:180px;width: 200px;height:80px;text-align: center;left: 50%;margin-left: -100px;font-size: 14px;line-height: 20px;}
#open_js img{;display:block;margin:0 auto;width: 50px;margin-bottom: 15px}
#space{width: 35px;display: inline-block}

/*排序*/
.container .sort{width: 99%;height: 30px;;padding: 5px 2px;margin: 0 auto;background-color: #fff;margin-bottom:10px}
.container .sort .sort_left{height: 30px;line-height:30px;float: left;font-size: 16px;}
.container .sort .sort_right{height: 30px;line-height:30px;float: right;font-size: 16px;}


/*losePASS*/
.resetpass{background-color: #fff;text-align: center;padding: 20px;}
.page .content.resetpass{padding:20px;text-align:center;margin-right:0}
.resetpass form{width:300px;margin:0 auto;text-align:left}
.resetpass form p{margin-bottom:20px}
.resetpass form p .form-control{width: 200px;height: 30px;line-height: 30px;}
.resetpass form p .getstart{border: 1px solid #ff5f33;background-color: #ff5f33;text-align: center;font-size: 20px;color: #fff;padding: 10px 20px;width: 200px;}
.resetpass form p .getstart:hover{background-color:#f97652 }
.resetpass h1{font-size:24px;font-weight:normal;margin-bottom: 20px;}
.resetpass h3{color:#777;font-size: 24px;}
.resetpass h3 .glyphicon{top:4px}
.resetpasssteps{margin-bottom:50px;overflow:hidden}
.resetpasssteps li{width:33.33333%;text-align:center;float:left;background-color:#eee;color:#666;line-height:33px;position:relative;padding-left:15px;box-sizing: border-box;}
.resetpasssteps li.active{background-color:#E74C3C;color:#fff;text-align: center;}
.resetpasssteps li .glyphicon{position:absolute;right:-17px;top:-3px;font-size:36px;color:#fff;z-index:2}
.errtip{background-color:#FCEAEA;color:#DB5353;padding:8px 15px;font-size:14px;border:1px solid #FC9797;}

.tips_info{
    text-align: center;
    font-size: 15px;
    margin: 5px auto;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #54aaff;
    color:#1e88e5}
.tips_info a{color: deeppink}
.last_page{display: none}
.last_page a{font-size: 16px;padding: 10px 15px;background-color: #1e88e5;color: #fff;display: block;width: 110px;margin: 0 auto;margin-top: 20px;text-align: center}
.last_page a:hover{opacity: 0.8}

@media only screen and (min-width:1330px) {
    .container { max-width: 1180px; !important; }
    /*.slider { width: 1306px !important; }幻粉*/
    #focus ul li { width: 975px; }
    #focus ul li img { width: 666px; }
    #focus ul li a { float: none; }
    #focus .button { width: 975px; }
    .slides_entry { display: block !important; margin-top: 10px; font-size: 14.7px; line-height: 1.5em; }
    .flex-caption { left: 650px !important; width: 292px; bottom: 0 !important; height: 370px; /*border-bottom: 1px #999 dashed*/}/*左边高度*.1 */
    .flex-caption h2 { /*line-height: 1.5em; margin-bottom: 20px; padding: 10px 0 20px 0; */font-size: 14px;/* font-weight: bold;*/  }
    .flex-caption a:hover { color: #fd6ca3; }
    .flex-caption .btn { display: block !important; margin-top: 30px; width: 55px; }
    .flex-caption .btn a { color: #fd6ca3; }
    #focus ul li a img { width: 975px !important; }/*幻灯全屏*/
    .related_box{ width:158px !important}
}
@media (max-width: 1220px) {
    #center_title {
        font-size: 16px;
        font-weight: normal
    }
    #center_span {
        width: 300px;
        height: 35px;
        line-height: 35px;
        background: #fee9ea url() no-repeat 0px center
    }
  #post_content img{height: auto}
}
@media (max-width: 1201px) {
    .topnav ul li a:link {}
    .topnav{margin: 0 auto;padding: 0 10px;}
    .search-button-top button{margin-right: 50px;}
    .mainleft{text-align: center;}
    #post_container{text-align: center;width:100%;margin: 0 auto;}
    .thumbnail img{min-width: 220px;}
    #post_container li{width: 220px;float:none;display: inline-block}
    #post_container .fixed-hight .thumbnail{height: 125px;}
    .article{padding: 5px 2px 0px 2px}
    .article h2{font-size: 10px;font-weight: 400}
    .pagination{text-align: center}
}

@media only screen and (min-width:1024px)and (max-width:1200px) {
    .related { width: 100% }
    .related ul { width: 600px;  }
    .related ul li{ width:250px; height:180px;}
    .related_box { float: left; width: 280px; height: 285px;}
    .related_box:hover { background-color:#f0f2f7;  }/*颜色*/
    .related_box a:hover {color:#779ed4 }
    .related_box .r_title { padding: 0 8px; text-align: center; }
    .related_box .r_pic { margin: 8px auto; width: 140px; height: 94px;}
    .related_box .r_pic img { width: 140px; height: 94px; }
    #blognamess{ display: none  }
    .subsidiary,.archive-header-ad{ display: none !important; }
    .adphone{display:none;}
    .left {  float:left }
    .indexPart2Right ul li{ list-style-type: decimal; }
    .indexPart2Right {
        border-radius:5px;
        /*background-color:#FFF;*/
        width:200px;
        height:auto;
        padding:20px 10px 20px 10px;
        margin-left:20px;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }
    .indexPart2Right:hover { /*border-bottom: #b8c4d1 solid 1px; box-shadow: #b8c4d1 0px 0px 5px;*/}/*文章列表下划线*/
    .indexPart2Right li {
        width:260px;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
        margin-top:5px;
        _margin-top:14px;
    }
    .indexPart2Right li a {
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
        width:260px;
        color:#666;
        font-size:12px;
    }
    .indexPart2Right li a:hover {
        color:#fd6ca3;
        /*text-decoration:underline;*/
    }
    .indexPart2Right li span {
        display:inline-block;
        margin-right:8px;
        background:#ff6100;
        width:22px;
        text-align:center;
        color:#fff;
        transition:all .5s ease-out;
        -webkit-transition:all .5s ease-out;
        -moz-transition:all .5s ease-out;
        -o-transition:all .5s ease-out;
        -ms-transition:all .5s ease-out
    }
    .indexPart2Right li:hover span {
        transform:rotate(360deg);
        -webkit-transform:rotate(360deg);
        -ms-transform:rotate(360deg);
        -moz-transform:rotate(360deg)
    }
    .indexPart2Right h3 {
        font:bold 14px/normal 'MicroSoft Yahei';
        color:#ddd;
        /*border-bottom:3px solid #eff2f5;*/
        width:260px;
    }
    .indexPart2Right h3 span a {
        float:right;
        font-size:12px;
        color:#666;
        background-color:#222222;
        padding:0 5px;
        border-radius:3px;
    }
    .indexPart2Right h3 span a:hover {
        float:right;
        font-size:12px;
        color:#fff;
        background-color:#fd6ca3;
        padding:0 5px;
        border-radius:3px;
    }
    .fens{
        background-color:#141414;

        padding-top:20px;
        padding-bottom:20px;
    }
}

@media(max-width:980px) {
    .adphone,.related{display:block;}
    #blognamess{display: none}
    #shenming .shenming_link{display: none}
}

@media only screen and (max-width:900px){
    #post_container li:hover{top:0px}
    .topnav .menu-item-has-children .menu-children-ico{display: inline-block;}
    .topnav .menu-item-has-children:after{content: '';border: none;}
    .related { float:left }
    .related ul { width: 600px;  }
    .related ul li{ width:280px; height:180px;float:left; margin-right:20px;}
    .related_box { float: left; width: 280px; height: 285px;}
    .related_box:hover { background-color:#f0f2f7;  }/*颜色*/
    .related_box a:hover {color:#779ed4 }
    .related_box .r_title { padding: 0 8px; text-align: center; }
    .related_box .r_pic { margin: 8px auto; width: 140px; height: 94px;}
    .related_box .r_pic img { width: 140px; height: 94px; }
    /*菜单*/
    .search-button-top button{display: none}
    .topnav{height: 50px;}
    .topnav{overflow: visible;}
  .topnav ul ul{background-color: #222222}
    .topnav .menu-button{  display:block;  float: left;  top:8px;  left: 10px;  width: 74px;}
    #header-bottom-right{width: 120px;top:8px;right: 0px;z-index: 9999 ;position: absolute;float: right;padding: 0;margin: 0;display: inline-block;}
    #header-bottom-right .search{  width:94%;overflow:hidden;height: 30px;  line-height: 30px;  padding: 0px;  margin: 0px; border: none}
    #header-bottom-right .search-field-holder .sousuo{;padding:0;position: absolute;  background: url("images/search-bottom.png") center no-repeat;  background-size: 80%;  width: 40px;  height: 30px;
        border: none;
        right: 0;top: 0}
    #header-bottom-right .search-field-holder{display: inline-block;height: auto;vertical-align: top;position: relative}
    #header-bottom-right .search-field-holder .search-field{width: 120px;}
    .search-icon{display: none}
    #menus{ display:none;padding:30px 0px 15px 0px; }
    #menus.open{ display:block; -webkit-transition: all .5s ease-in-out; -moz-transition: all .5s ease-in-out; -ms-transition: all .5s ease-in-out; transition: all .5s ease-in-out;}
    .container{padding: 10px}
    #menus li{ height:40px;width:100%;margin-left: 5px;margin-bottom:3px;}
    #menus li a{width:100% !important;line-height:40px;height:40px;font-size: 14px;}
    #menus li a:hover{text-indent: 0px}
    #menus .menu-item-has-children{height: auto;position: relative}
    #menus .menu-item-has-children .chevron-down{position: absolute;padding: 12px;right: 0;top:0;}
    #menus .menu-children-ico{position: absolute;padding: 12px;right: 0;top:0;}
    #menus .menu-children-ico:active{background-color: #ef5b9c}
    #menus .menu-item-has-children ul li a{}
    .topnav a{height: 40px;}
    .topnav li .sub-menu{ position:relative;width: 100%; top:0; left:0px;display: none;opacity: 1;overflow: auto;}
    .topnav ul ul li{color: #cecdcd}
    #menus .sub-menu li{width: auto;display: inline-block;}
    #menus .sub-menu li a{color: #cecdcd}
    .topnav li .sub-menu:before{ content: '';border: none;}
}

@media (max-width: 884px) {
    .search-button-top button{margin-right: 4px;}
    .topnav ul li a:link{padding: 3px 4px 0 4px}
    .topnav{height:60px;}
    .topnav li{height: 60px;}
    .topnav a{line-height: 50px;}
    .topnav ul li a:link{font-size: 10px;}
    .article_container h1{font-size: 1.0em}
}
@media (max-width: 750px) {
    #post_container li{width: 40%}
    #post_container .fixed-hight .thumbnail{height: auto}
    .thumbnail img{width: 100%}
    #post_container li{padding: 0}
    #post_container .fixed-hight h2 a{font-weight: 400}

}
@media  (max-width: 725px){
    .thumbnail img{min-width: 260px;}
    #post_container li{min-width: 260px}
  #mgssd_tips{display: none}
}

@media (max-width: 650px){
    /* #download{display: block}*/
    .topnav .menu-button{left: 0px;}
  .topnav ul ul{background-color: #31302E}

    .padd{display: block;height: 10px;}
    #header-bottom-right{width: 90px;}
    #header-bottom-right .search-field-holder .search-field{width: 75px;}
    .article h2{font-size:12px;font-weight: 600}
    .search-button-top button{display: none}
    .topnav{height: 50px;}
    .article_container{padding: 5px;}
    .pagination{font-size: 12px;}
    .mainmenus { margin-bottom: 1.5em; background-color: #edf1f7;box-shadow: none;}
    .mainmenus .container {background-color: #313030 }
    #sidebar,.subsidiary, .slider, #rss, .banner,.extend, .article_related,#head,.slider,.fens,.subsidiarys,.sthumbnail,.sinfo,.menu-right,#authorarea ,#blogname,#container,.related,.tximgcc{ display: none !important; }
    .mainleft { margin: 0 auto; overflow:visible}

    #comment-author-info { height: auto; }
    #comment-author-info input { width: 60.5%; margin-bottom: 5px; }
    .search_phone { display: block }
    #post_container{ margin-left:0}
    /*#post_container li{ width:100%; margin-left:0; max-width:100%}*/
    #post_container li{min-width:auto;width: 48%;margin-left: 1px;}
    #post_container li .thumbnail a{ text-align:center}
    #post_container li .arrow-catpanel-top{ display:none}
    #post_container li .zoomOverlay{ display:none !important}
    #copost_container{ margin-left:0}
    #copost_container li{ width:100%; margin-left:0; max-width:100%}
    #copost_container li .cothumbnail a{ text-align:center}
    #post_container li .thumbnail a img{min-width: auto;width: 100%}
    #copost_container li .arrow-catpanel-top{ display:none}
    #copost_container li .zoomOverlay{ display:none !important}
    #post_container .fixed-hight .thumbnail{height: auto;}
    #tbox{ right:0;}
    .topnav ul ul li a:link, .topnav ul ul li a:visited{}

    #header-bottom-right .search-field-holder .sousuo{width: 30px;}
  .resetpasssteps li{display: block;width: 100%}
/*	.topnav{overflow: visible;}
    .topnav .menu-button{  display:block;  float: left;  top:8px;  left: 10px;  width: 74px;}
    #menus{ display:none;padding:30px 0px 15px 0px; background-color: #313030}
    #menus.open{ display:block; -webkit-transition: all .5s ease-in-out; -moz-transition: all .5s ease-in-out; -ms-transition: all .5s ease-in-out; transition: all .5s ease-in-out;}
    .container{padding: 10px}
    #menus li{ height:40px;width:100%;margin-left: 10px;margin-bottom:5px;border-bottom: 1px solid #1c1c1c;}
    #menus li a{width:90% !important;line-height:40px;height:40px;font-size: 14px;}
    #menus li a:hover{text-indent: 0px}
    #menus .menu-item-has-children{height: auto;position: relative}
    #menus .menu-item-has-children .chevron-down{position: absolute;padding: 12px;right: 0;top:0;}
    #menus .menu-children-ico{position: absolute;padding: 12px;right: 0;top:0;}
    #menus .menu-children-ico:active{background-color: #ef5b9c}
    #menus .menu-item-has-children ul li a{background-color: #313030}
    .topnav a{height: 40px;}
    .topnav li .sub-menu{ position:relative; top:0; left:0px;display: none;opacity: 1}
    .topnav ul ul li{color: #cecdcd}
    #menus .sub-menu li{width: auto;}
    #menus .sub-menu li a{color: #cecdcd}
    .topnav li .sub-menu:before{ content: '';border: none;}*/
    #post_content h3 strong{font-size: 13px}
    #home,#pinglun{display: none}
    .navigation{width: 100%}
    .pagination a, .pagination span{width: 40px;height: 25px;line-height: 25px;}
    .pagination .current { height: 25px; width:40px;color: #fd6ca3; border-style:solid; border-width:1px; border-color:#fd6ca3; margin: 10px 5px;}
    .page_previous, .pagination .prev{width: 50px;height: 25px;}
    .pagination .page_next, .pagination .next, .pagination .page_next:hover, .pagination .next:hover { width: 50px;height: 25px; text-align: center; }
    .pagination .prev:hover{;width:50px;height: 25px;;line-height: 25px;}
    .pagination a:hover{width: 40px;height: 25px;line-height: 25px;}
    .article_container h1{font-size: 0.8em}
    #download a{width: 160px;}
    #about_container{min-width: 95% !important;}
    #about_mainleft{width: 100%}
    .about .about_content p{width: 95%}
    .about .about_content .about_mgs{height: 215px;width:80%;}
    .about .about_content .about_mgs .about_mgsl{display: block;width:100%;height: auto;text-align: center}
    .about .about_content .about_mgs .about_mgsr{display: block;width: 100%;height: 100px;text-align: center}
    .about .about_content .about_mgs .about_mgsl img{top:0;margin-top: 15px;}
    .about .about_content .about_mobile_qq{display: block;}
    .about .about_content .about_contact{display: none}
}
@media  (max-width: 395px){
    .about{min-width: 300px;}

    .about .about_tab{width: 100%;}
    .about .about_tab a{width: 40%;}
    .about .about_hide{display: none}
    .about .about_content p{line-height: 28px;width: 100%}
    .about .about_content .about_mgstage{height:230px;}
    .about .about_content .about_contact a{padding: 10px 70px;}
}
.after_qq:after{content: "QQ1405617552"}
.after_emil:after{content: ""}
.footer_warning{font-size: 12px;color: orangered }
.footer_warning:after{content: "提示："}
'''
ks = BytesIO()
ks.write(builtin_style.encode('utf8'))
sfile_dict['builtin_style.css'] = ks 

buildjq = b'''LyohIGpRdWVyeSB2My4zLjEgfCAoYykgSlMgRm91bmRhdGlvbiBhbmQgb3RoZXIgY29udHJpYnV0b3JzIHwganF1ZXJ5Lm9yZy9saWNlbnNlICovCiFmdW5jdGlvbihlLHQpeyJ1c2Ugc3RyaWN0Ijsib2JqZWN0Ij09dHlwZW9mIG1vZHVsZSYmIm9iamVjdCI9PXR5cGVvZiBtb2R1bGUuZXhwb3J0cz9tb2R1bGUuZXhwb3J0cz1lLmRvY3VtZW50P3QoZSwhMCk6ZnVuY3Rpb24oZSl7aWYoIWUuZG9jdW1lbnQpdGhyb3cgbmV3IEVycm9yKCJqUXVlcnkgcmVxdWlyZXMgYSB3aW5kb3cgd2l0aCBhIGRvY3VtZW50Iik7cmV0dXJuIHQoZSl9OnQoZSl9KCJ1bmRlZmluZWQiIT10eXBlb2Ygd2luZG93P3dpbmRvdzp0aGlzLGZ1bmN0aW9uKGUsdCl7InVzZSBzdHJpY3QiO3ZhciBuPVtdLHI9ZS5kb2N1bWVudCxpPU9iamVjdC5nZXRQcm90b3R5cGVPZixvPW4uc2xpY2UsYT1uLmNvbmNhdCxzPW4ucHVzaCx1PW4uaW5kZXhPZixsPXt9LGM9bC50b1N0cmluZyxmPWwuaGFzT3duUHJvcGVydHkscD1mLnRvU3RyaW5nLGQ9cC5jYWxsKE9iamVjdCksaD17fSxnPWZ1bmN0aW9uIGUodCl7cmV0dXJuImZ1bmN0aW9uIj09dHlwZW9mIHQmJiJudW1iZXIiIT10eXBlb2YgdC5ub2RlVHlwZX0seT1mdW5jdGlvbiBlKHQpe3JldHVybiBudWxsIT10JiZ0PT09dC53aW5kb3d9LHY9e3R5cGU6ITAsc3JjOiEwLG5vTW9kdWxlOiEwfTtmdW5jdGlvbiBtKGUsdCxuKXt2YXIgaSxvPSh0PXR8fHIpLmNyZWF0ZUVsZW1lbnQoInNjcmlwdCIpO2lmKG8udGV4dD1lLG4pZm9yKGkgaW4gdiluW2ldJiYob1tpXT1uW2ldKTt0LmhlYWQuYXBwZW5kQ2hpbGQobykucGFyZW50Tm9kZS5yZW1vdmVDaGlsZChvKX1mdW5jdGlvbiB4KGUpe3JldHVybiBudWxsPT1lP2UrIiI6Im9iamVjdCI9PXR5cGVvZiBlfHwiZnVuY3Rpb24iPT10eXBlb2YgZT9sW2MuY2FsbChlKV18fCJvYmplY3QiOnR5cGVvZiBlfXZhciBiPSIzLjMuMSIsdz1mdW5jdGlvbihlLHQpe3JldHVybiBuZXcgdy5mbi5pbml0KGUsdCl9LFQ9L15bXHNcdUZFRkZceEEwXSt8W1xzXHVGRUZGXHhBMF0rJC9nO3cuZm49dy5wcm90b3R5cGU9e2pxdWVyeToiMy4zLjEiLGNvbnN0cnVjdG9yOncsbGVuZ3RoOjAsdG9BcnJheTpmdW5jdGlvbigpe3JldHVybiBvLmNhbGwodGhpcyl9LGdldDpmdW5jdGlvbihlKXtyZXR1cm4gbnVsbD09ZT9vLmNhbGwodGhpcyk6ZTwwP3RoaXNbZSt0aGlzLmxlbmd0aF06dGhpc1tlXX0scHVzaFN0YWNrOmZ1bmN0aW9uKGUpe3ZhciB0PXcubWVyZ2UodGhpcy5jb25zdHJ1Y3RvcigpLGUpO3JldHVybiB0LnByZXZPYmplY3Q9dGhpcyx0fSxlYWNoOmZ1bmN0aW9uKGUpe3JldHVybiB3LmVhY2godGhpcyxlKX0sbWFwOmZ1bmN0aW9uKGUpe3JldHVybiB0aGlzLnB1c2hTdGFjayh3Lm1hcCh0aGlzLGZ1bmN0aW9uKHQsbil7cmV0dXJuIGUuY2FsbCh0LG4sdCl9KSl9LHNsaWNlOmZ1bmN0aW9uKCl7cmV0dXJuIHRoaXMucHVzaFN0YWNrKG8uYXBwbHkodGhpcyxhcmd1bWVudHMpKX0sZmlyc3Q6ZnVuY3Rpb24oKXtyZXR1cm4gdGhpcy5lcSgwKX0sbGFzdDpmdW5jdGlvbigpe3JldHVybiB0aGlzLmVxKC0xKX0sZXE6ZnVuY3Rpb24oZSl7dmFyIHQ9dGhpcy5sZW5ndGgsbj0rZSsoZTwwP3Q6MCk7cmV0dXJuIHRoaXMucHVzaFN0YWNrKG4+PTAmJm48dD9bdGhpc1tuXV06W10pfSxlbmQ6ZnVuY3Rpb24oKXtyZXR1cm4gdGhpcy5wcmV2T2JqZWN0fHx0aGlzLmNvbnN0cnVjdG9yKCl9LHB1c2g6cyxzb3J0Om4uc29ydCxzcGxpY2U6bi5zcGxpY2V9LHcuZXh0ZW5kPXcuZm4uZXh0ZW5kPWZ1bmN0aW9uKCl7dmFyIGUsdCxuLHIsaSxvLGE9YXJndW1lbnRzWzBdfHx7fSxzPTEsdT1hcmd1bWVudHMubGVuZ3RoLGw9ITE7Zm9yKCJib29sZWFuIj09dHlwZW9mIGEmJihsPWEsYT1hcmd1bWVudHNbc118fHt9LHMrKyksIm9iamVjdCI9PXR5cGVvZiBhfHxnKGEpfHwoYT17fSkscz09PXUmJihhPXRoaXMscy0tKTtzPHU7cysrKWlmKG51bGwhPShlPWFyZ3VtZW50c1tzXSkpZm9yKHQgaW4gZSluPWFbdF0sYSE9PShyPWVbdF0pJiYobCYmciYmKHcuaXNQbGFpbk9iamVjdChyKXx8KGk9QXJyYXkuaXNBcnJheShyKSkpPyhpPyhpPSExLG89biYmQXJyYXkuaXNBcnJheShuKT9uOltdKTpvPW4mJncuaXNQbGFpbk9iamVjdChuKT9uOnt9LGFbdF09dy5leHRlbmQobCxvLHIpKTp2b2lkIDAhPT1yJiYoYVt0XT1yKSk7cmV0dXJuIGF9LHcuZXh0ZW5kKHtleHBhbmRvOiJqUXVlcnkiKygiMy4zLjEiK01hdGgucmFuZG9tKCkpLnJlcGxhY2UoL1xEL2csIiIpLGlzUmVhZHk6ITAsZXJyb3I6ZnVuY3Rpb24oZSl7dGhyb3cgbmV3IEVycm9yKGUpfSxub29wOmZ1bmN0aW9uKCl7fSxpc1BsYWluT2JqZWN0OmZ1bmN0aW9uKGUpe3ZhciB0LG47cmV0dXJuISghZXx8IltvYmplY3QgT2JqZWN0XSIhPT1jLmNhbGwoZSkpJiYoISh0PWkoZSkpfHwiZnVuY3Rpb24iPT10eXBlb2Yobj1mLmNhbGwodCwiY29uc3RydWN0b3IiKSYmdC5jb25zdHJ1Y3RvcikmJnAuY2FsbChuKT09PWQpfSxpc0VtcHR5T2JqZWN0OmZ1bmN0aW9uKGUpe3ZhciB0O2Zvcih0IGluIGUpcmV0dXJuITE7cmV0dXJuITB9LGdsb2JhbEV2YWw6ZnVuY3Rpb24oZSl7bShlKX0sZWFjaDpmdW5jdGlvbihlLHQpe3ZhciBuLHI9MDtpZihDKGUpKXtmb3Iobj1lLmxlbmd0aDtyPG47cisrKWlmKCExPT09dC5jYWxsKGVbcl0scixlW3JdKSlicmVha31lbHNlIGZvcihyIGluIGUpaWYoITE9PT10LmNhbGwoZVtyXSxyLGVbcl0pKWJyZWFrO3JldHVybiBlfSx0cmltOmZ1bmN0aW9uKGUpe3JldHVybiBudWxsPT1lPyIiOihlKyIiKS5yZXBsYWNlKFQsIiIpfSxtYWtlQXJyYXk6ZnVuY3Rpb24oZSx0KXt2YXIgbj10fHxbXTtyZXR1cm4gbnVsbCE9ZSYmKEMoT2JqZWN0KGUpKT93Lm1lcmdlKG4sInN0cmluZyI9PXR5cGVvZiBlP1tlXTplKTpzLmNhbGwobixlKSksbn0saW5BcnJheTpmdW5jdGlvbihlLHQsbil7cmV0dXJuIG51bGw9PXQ/LTE6dS5jYWxsKHQsZSxuKX0sbWVyZ2U6ZnVuY3Rpb24oZSx0KXtmb3IodmFyIG49K3QubGVuZ3RoLHI9MCxpPWUubGVuZ3RoO3I8bjtyKyspZVtpKytdPXRbcl07cmV0dXJuIGUubGVuZ3RoPWksZX0sZ3JlcDpmdW5jdGlvbihlLHQsbil7Zm9yKHZhciByLGk9W10sbz0wLGE9ZS5sZW5ndGgscz0hbjtvPGE7bysrKShyPSF0KGVbb10sbykpIT09cyYmaS5wdXNoKGVbb10pO3JldHVybiBpfSxtYXA6ZnVuY3Rpb24oZSx0LG4pe3ZhciByLGksbz0wLHM9W107aWYoQyhlKSlmb3Iocj1lLmxlbmd0aDtvPHI7bysrKW51bGwhPShpPXQoZVtvXSxvLG4pKSYmcy5wdXNoKGkpO2Vsc2UgZm9yKG8gaW4gZSludWxsIT0oaT10KGVbb10sbyxuKSkmJnMucHVzaChpKTtyZXR1cm4gYS5hcHBseShbXSxzKX0sZ3VpZDoxLHN1cHBvcnQ6aH0pLCJmdW5jdGlvbiI9PXR5cGVvZiBTeW1ib2wmJih3LmZuW1N5bWJvbC5pdGVyYXRvcl09bltTeW1ib2wuaXRlcmF0b3JdKSx3LmVhY2goIkJvb2xlYW4gTnVtYmVyIFN0cmluZyBGdW5jdGlvbiBBcnJheSBEYXRlIFJlZ0V4cCBPYmplY3QgRXJyb3IgU3ltYm9sIi5zcGxpdCgiICIpLGZ1bmN0aW9uKGUsdCl7bFsiW29iamVjdCAiK3QrIl0iXT10LnRvTG93ZXJDYXNlKCl9KTtmdW5jdGlvbiBDKGUpe3ZhciB0PSEhZSYmImxlbmd0aCJpbiBlJiZlLmxlbmd0aCxuPXgoZSk7cmV0dXJuIWcoZSkmJiF5KGUpJiYoImFycmF5Ij09PW58fDA9PT10fHwibnVtYmVyIj09dHlwZW9mIHQmJnQ+MCYmdC0xIGluIGUpfXZhciBFPWZ1bmN0aW9uKGUpe3ZhciB0LG4scixpLG8sYSxzLHUsbCxjLGYscCxkLGgsZyx5LHYsbSx4LGI9InNpenpsZSIrMSpuZXcgRGF0ZSx3PWUuZG9jdW1lbnQsVD0wLEM9MCxFPWFlKCksaz1hZSgpLFM9YWUoKSxEPWZ1bmN0aW9uKGUsdCl7cmV0dXJuIGU9PT10JiYoZj0hMCksMH0sTj17fS5oYXNPd25Qcm9wZXJ0eSxBPVtdLGo9QS5wb3AscT1BLnB1c2gsTD1BLnB1c2gsSD1BLnNsaWNlLE89ZnVuY3Rpb24oZSx0KXtmb3IodmFyIG49MCxyPWUubGVuZ3RoO248cjtuKyspaWYoZVtuXT09PXQpcmV0dXJuIG47cmV0dXJuLTF9LFA9ImNoZWNrZWR8c2VsZWN0ZWR8YXN5bmN8YXV0b2ZvY3VzfGF1dG9wbGF5fGNvbnRyb2xzfGRlZmVyfGRpc2FibGVkfGhpZGRlbnxpc21hcHxsb29wfG11bHRpcGxlfG9wZW58cmVhZG9ubHl8cmVxdWlyZWR8c2NvcGVkIixNPSJbXFx4MjBcXHRcXHJcXG5cXGZdIixSPSIoPzpcXFxcLnxbXFx3LV18W15cMC1cXHhhMF0pKyIsST0iXFxbIitNKyIqKCIrUisiKSg/OiIrTSsiKihbKl4kfCF+XT89KSIrTSsiKig/OicoKD86XFxcXC58W15cXFxcJ10pKiknfFwiKCg/OlxcXFwufFteXFxcXFwiXSkqKVwifCgiK1IrIikpfCkiK00rIipcXF0iLFc9IjooIitSKyIpKD86XFwoKCgnKCg/OlxcXFwufFteXFxcXCddKSopJ3xcIigoPzpcXFxcLnxbXlxcXFxcIl0pKilcIil8KCg/OlxcXFwufFteXFxcXCgpW1xcXV18IitJKyIpKil8LiopXFwpfCkiLCQ9bmV3IFJlZ0V4cChNKyIrIiwiZyIpLEI9bmV3IFJlZ0V4cCgiXiIrTSsiK3woKD86XnxbXlxcXFxdKSg/OlxcXFwuKSopIitNKyIrJCIsImciKSxGPW5ldyBSZWdFeHAoIl4iK00rIiosIitNKyIqIiksXz1uZXcgUmVnRXhwKCJeIitNKyIqKFs+K35dfCIrTSsiKSIrTSsiKiIpLHo9bmV3IFJlZ0V4cCgiPSIrTSsiKihbXlxcXSdcIl0qPykiK00rIipcXF0iLCJnIiksWD1uZXcgUmVnRXhwKFcpLFU9bmV3IFJlZ0V4cCgiXiIrUisiJCIpLFY9e0lEOm5ldyBSZWdFeHAoIl4jKCIrUisiKSIpLENMQVNTOm5ldyBSZWdFeHAoIl5cXC4oIitSKyIpIiksVEFHOm5ldyBSZWdFeHAoIl4oIitSKyJ8WypdKSIpLEFUVFI6bmV3IFJlZ0V4cCgiXiIrSSksUFNFVURPOm5ldyBSZWdFeHAoIl4iK1cpLENISUxEOm5ldyBSZWdFeHAoIl46KG9ubHl8Zmlyc3R8bGFzdHxudGh8bnRoLWxhc3QpLShjaGlsZHxvZi10eXBlKSg/OlxcKCIrTSsiKihldmVufG9kZHwoKFsrLV18KShcXGQqKW58KSIrTSsiKig/OihbKy1dfCkiK00rIiooXFxkKyl8KSkiK00rIipcXCl8KSIsImkiKSxib29sOm5ldyBSZWdFeHAoIl4oPzoiK1ArIikkIiwiaSIpLG5lZWRzQ29udGV4dDpuZXcgUmVnRXhwKCJeIitNKyIqWz4rfl18OihldmVufG9kZHxlcXxndHxsdHxudGh8Zmlyc3R8bGFzdCkoPzpcXCgiK00rIiooKD86LVxcZCk/XFxkKikiK00rIipcXCl8KSg/PVteLV18JCkiLCJpIil9LEc9L14oPzppbnB1dHxzZWxlY3R8dGV4dGFyZWF8YnV0dG9uKSQvaSxZPS9eaFxkJC9pLFE9L15bXntdK1x7XHMqXFtuYXRpdmUgXHcvLEo9L14oPzojKFtcdy1dKyl8KFx3Kyl8XC4oW1x3LV0rKSkkLyxLPS9bK35dLyxaPW5ldyBSZWdFeHAoIlxcXFwoW1xcZGEtZl17MSw2fSIrTSsiP3woIitNKyIpfC4pIiwiaWciKSxlZT1mdW5jdGlvbihlLHQsbil7dmFyIHI9IjB4Iit0LTY1NTM2O3JldHVybiByIT09cnx8bj90OnI8MD9TdHJpbmcuZnJvbUNoYXJDb2RlKHIrNjU1MzYpOlN0cmluZy5mcm9tQ2hhckNvZGUocj4+MTB8NTUyOTYsMTAyMyZyfDU2MzIwKX0sdGU9LyhbXDAtXHgxZlx4N2ZdfF4tP1xkKXxeLSR8W15cMC1ceDFmXHg3Zi1cdUZGRkZcdy1dL2csbmU9ZnVuY3Rpb24oZSx0KXtyZXR1cm4gdD8iXDAiPT09ZT8iXHVmZmZkIjplLnNsaWNlKDAsLTEpKyJcXCIrZS5jaGFyQ29kZUF0KGUubGVuZ3RoLTEpLnRvU3RyaW5nKDE2KSsiICI6IlxcIitlfSxyZT1mdW5jdGlvbigpe3AoKX0saWU9bWUoZnVuY3Rpb24oZSl7cmV0dXJuITA9PT1lLmRpc2FibGVkJiYoImZvcm0iaW4gZXx8ImxhYmVsImluIGUpfSx7ZGlyOiJwYXJlbnROb2RlIixuZXh0OiJsZWdlbmQifSk7dHJ5e0wuYXBwbHkoQT1ILmNhbGwody5jaGlsZE5vZGVzKSx3LmNoaWxkTm9kZXMpLEFbdy5jaGlsZE5vZGVzLmxlbmd0aF0ubm9kZVR5cGV9Y2F0Y2goZSl7TD17YXBwbHk6QS5sZW5ndGg/ZnVuY3Rpb24oZSx0KXtxLmFwcGx5KGUsSC5jYWxsKHQpKX06ZnVuY3Rpb24oZSx0KXt2YXIgbj1lLmxlbmd0aCxyPTA7d2hpbGUoZVtuKytdPXRbcisrXSk7ZS5sZW5ndGg9bi0xfX19ZnVuY3Rpb24gb2UoZSx0LHIsaSl7dmFyIG8scyxsLGMsZixoLHYsbT10JiZ0Lm93bmVyRG9jdW1lbnQsVD10P3Qubm9kZVR5cGU6OTtpZihyPXJ8fFtdLCJzdHJpbmciIT10eXBlb2YgZXx8IWV8fDEhPT1UJiY5IT09VCYmMTEhPT1UKXJldHVybiByO2lmKCFpJiYoKHQ/dC5vd25lckRvY3VtZW50fHx0OncpIT09ZCYmcCh0KSx0PXR8fGQsZykpe2lmKDExIT09VCYmKGY9Si5leGVjKGUpKSlpZihvPWZbMV0pe2lmKDk9PT1UKXtpZighKGw9dC5nZXRFbGVtZW50QnlJZChvKSkpcmV0dXJuIHI7aWYobC5pZD09PW8pcmV0dXJuIHIucHVzaChsKSxyfWVsc2UgaWYobSYmKGw9bS5nZXRFbGVtZW50QnlJZChvKSkmJngodCxsKSYmbC5pZD09PW8pcmV0dXJuIHIucHVzaChsKSxyfWVsc2V7aWYoZlsyXSlyZXR1cm4gTC5hcHBseShyLHQuZ2V0RWxlbWVudHNCeVRhZ05hbWUoZSkpLHI7aWYoKG89ZlszXSkmJm4uZ2V0RWxlbWVudHNCeUNsYXNzTmFtZSYmdC5nZXRFbGVtZW50c0J5Q2xhc3NOYW1lKXJldHVybiBMLmFwcGx5KHIsdC5nZXRFbGVtZW50c0J5Q2xhc3NOYW1lKG8pKSxyfWlmKG4ucXNhJiYhU1tlKyIgIl0mJigheXx8IXkudGVzdChlKSkpe2lmKDEhPT1UKW09dCx2PWU7ZWxzZSBpZigib2JqZWN0IiE9PXQubm9kZU5hbWUudG9Mb3dlckNhc2UoKSl7KGM9dC5nZXRBdHRyaWJ1dGUoImlkIikpP2M9Yy5yZXBsYWNlKHRlLG5lKTp0LnNldEF0dHJpYnV0ZSgiaWQiLGM9Yikscz0oaD1hKGUpKS5sZW5ndGg7d2hpbGUocy0tKWhbc109IiMiK2MrIiAiK3ZlKGhbc10pO3Y9aC5qb2luKCIsIiksbT1LLnRlc3QoZSkmJmdlKHQucGFyZW50Tm9kZSl8fHR9aWYodil0cnl7cmV0dXJuIEwuYXBwbHkocixtLnF1ZXJ5U2VsZWN0b3JBbGwodikpLHJ9Y2F0Y2goZSl7fWZpbmFsbHl7Yz09PWImJnQucmVtb3ZlQXR0cmlidXRlKCJpZCIpfX19cmV0dXJuIHUoZS5yZXBsYWNlKEIsIiQxIiksdCxyLGkpfWZ1bmN0aW9uIGFlKCl7dmFyIGU9W107ZnVuY3Rpb24gdChuLGkpe3JldHVybiBlLnB1c2gobisiICIpPnIuY2FjaGVMZW5ndGgmJmRlbGV0ZSB0W2Uuc2hpZnQoKV0sdFtuKyIgIl09aX1yZXR1cm4gdH1mdW5jdGlvbiBzZShlKXtyZXR1cm4gZVtiXT0hMCxlfWZ1bmN0aW9uIHVlKGUpe3ZhciB0PWQuY3JlYXRlRWxlbWVudCgiZmllbGRzZXQiKTt0cnl7cmV0dXJuISFlKHQpfWNhdGNoKGUpe3JldHVybiExfWZpbmFsbHl7dC5wYXJlbnROb2RlJiZ0LnBhcmVudE5vZGUucmVtb3ZlQ2hpbGQodCksdD1udWxsfX1mdW5jdGlvbiBsZShlLHQpe3ZhciBuPWUuc3BsaXQoInwiKSxpPW4ubGVuZ3RoO3doaWxlKGktLSlyLmF0dHJIYW5kbGVbbltpXV09dH1mdW5jdGlvbiBjZShlLHQpe3ZhciBuPXQmJmUscj1uJiYxPT09ZS5ub2RlVHlwZSYmMT09PXQubm9kZVR5cGUmJmUuc291cmNlSW5kZXgtdC5zb3VyY2VJbmRleDtpZihyKXJldHVybiByO2lmKG4pd2hpbGUobj1uLm5leHRTaWJsaW5nKWlmKG49PT10KXJldHVybi0xO3JldHVybiBlPzE6LTF9ZnVuY3Rpb24gZmUoZSl7cmV0dXJuIGZ1bmN0aW9uKHQpe3JldHVybiJpbnB1dCI9PT10Lm5vZGVOYW1lLnRvTG93ZXJDYXNlKCkmJnQudHlwZT09PWV9fWZ1bmN0aW9uIHBlKGUpe3JldHVybiBmdW5jdGlvbih0KXt2YXIgbj10Lm5vZGVOYW1lLnRvTG93ZXJDYXNlKCk7cmV0dXJuKCJpbnB1dCI9PT1ufHwiYnV0dG9uIj09PW4pJiZ0LnR5cGU9PT1lfX1mdW5jdGlvbiBkZShlKXtyZXR1cm4gZnVuY3Rpb24odCl7cmV0dXJuImZvcm0iaW4gdD90LnBhcmVudE5vZGUmJiExPT09dC5kaXNhYmxlZD8ibGFiZWwiaW4gdD8ibGFiZWwiaW4gdC5wYXJlbnROb2RlP3QucGFyZW50Tm9kZS5kaXNhYmxlZD09PWU6dC5kaXNhYmxlZD09PWU6dC5pc0Rpc2FibGVkPT09ZXx8dC5pc0Rpc2FibGVkIT09IWUmJmllKHQpPT09ZTp0LmRpc2FibGVkPT09ZToibGFiZWwiaW4gdCYmdC5kaXNhYmxlZD09PWV9fWZ1bmN0aW9uIGhlKGUpe3JldHVybiBzZShmdW5jdGlvbih0KXtyZXR1cm4gdD0rdCxzZShmdW5jdGlvbihuLHIpe3ZhciBpLG89ZShbXSxuLmxlbmd0aCx0KSxhPW8ubGVuZ3RoO3doaWxlKGEtLSluW2k9b1thXV0mJihuW2ldPSEocltpXT1uW2ldKSl9KX0pfWZ1bmN0aW9uIGdlKGUpe3JldHVybiBlJiYidW5kZWZpbmVkIiE9dHlwZW9mIGUuZ2V0RWxlbWVudHNCeVRhZ05hbWUmJmV9bj1vZS5zdXBwb3J0PXt9LG89b2UuaXNYTUw9ZnVuY3Rpb24oZSl7dmFyIHQ9ZSYmKGUub3duZXJEb2N1bWVudHx8ZSkuZG9jdW1lbnRFbGVtZW50O3JldHVybiEhdCYmIkhUTUwiIT09dC5ub2RlTmFtZX0scD1vZS5zZXREb2N1bWVudD1mdW5jdGlvbihlKXt2YXIgdCxpLGE9ZT9lLm93bmVyRG9jdW1lbnR8fGU6dztyZXR1cm4gYSE9PWQmJjk9PT1hLm5vZGVUeXBlJiZhLmRvY3VtZW50RWxlbWVudD8oZD1hLGg9ZC5kb2N1bWVudEVsZW1lbnQsZz0hbyhkKSx3IT09ZCYmKGk9ZC5kZWZhdWx0VmlldykmJmkudG9wIT09aSYmKGkuYWRkRXZlbnRMaXN0ZW5lcj9pLmFkZEV2ZW50TGlzdGVuZXIoInVubG9hZCIscmUsITEpOmkuYXR0YWNoRXZlbnQmJmkuYXR0YWNoRXZlbnQoIm9udW5sb2FkIixyZSkpLG4uYXR0cmlidXRlcz11ZShmdW5jdGlvbihlKXtyZXR1cm4gZS5jbGFzc05hbWU9ImkiLCFlLmdldEF0dHJpYnV0ZSgiY2xhc3NOYW1lIil9KSxuLmdldEVsZW1lbnRzQnlUYWdOYW1lPXVlKGZ1bmN0aW9uKGUpe3JldHVybiBlLmFwcGVuZENoaWxkKGQuY3JlYXRlQ29tbWVudCgiIikpLCFlLmdldEVsZW1lbnRzQnlUYWdOYW1lKCIqIikubGVuZ3RofSksbi5nZXRFbGVtZW50c0J5Q2xhc3NOYW1lPVEudGVzdChkLmdldEVsZW1lbnRzQnlDbGFzc05hbWUpLG4uZ2V0QnlJZD11ZShmdW5jdGlvbihlKXtyZXR1cm4gaC5hcHBlbmRDaGlsZChlKS5pZD1iLCFkLmdldEVsZW1lbnRzQnlOYW1lfHwhZC5nZXRFbGVtZW50c0J5TmFtZShiKS5sZW5ndGh9KSxuLmdldEJ5SWQ/KHIuZmlsdGVyLklEPWZ1bmN0aW9uKGUpe3ZhciB0PWUucmVwbGFjZShaLGVlKTtyZXR1cm4gZnVuY3Rpb24oZSl7cmV0dXJuIGUuZ2V0QXR0cmlidXRlKCJpZCIpPT09dH19LHIuZmluZC5JRD1mdW5jdGlvbihlLHQpe2lmKCJ1bmRlZmluZWQiIT10eXBlb2YgdC5nZXRFbGVtZW50QnlJZCYmZyl7dmFyIG49dC5nZXRFbGVtZW50QnlJZChlKTtyZXR1cm4gbj9bbl06W119fSk6KHIuZmlsdGVyLklEPWZ1bmN0aW9uKGUpe3ZhciB0PWUucmVwbGFjZShaLGVlKTtyZXR1cm4gZnVuY3Rpb24oZSl7dmFyIG49InVuZGVmaW5lZCIhPXR5cGVvZiBlLmdldEF0dHJpYnV0ZU5vZGUmJmUuZ2V0QXR0cmlidXRlTm9kZSgiaWQiKTtyZXR1cm4gbiYmbi52YWx1ZT09PXR9fSxyLmZpbmQuSUQ9ZnVuY3Rpb24oZSx0KXtpZigidW5kZWZpbmVkIiE9dHlwZW9mIHQuZ2V0RWxlbWVudEJ5SWQmJmcpe3ZhciBuLHIsaSxvPXQuZ2V0RWxlbWVudEJ5SWQoZSk7aWYobyl7aWYoKG49by5nZXRBdHRyaWJ1dGVOb2RlKCJpZCIpKSYmbi52YWx1ZT09PWUpcmV0dXJuW29dO2k9dC5nZXRFbGVtZW50c0J5TmFtZShlKSxyPTA7d2hpbGUobz1pW3IrK10paWYoKG49by5nZXRBdHRyaWJ1dGVOb2RlKCJpZCIpKSYmbi52YWx1ZT09PWUpcmV0dXJuW29dfXJldHVybltdfX0pLHIuZmluZC5UQUc9bi5nZXRFbGVtZW50c0J5VGFnTmFtZT9mdW5jdGlvbihlLHQpe3JldHVybiJ1bmRlZmluZWQiIT10eXBlb2YgdC5nZXRFbGVtZW50c0J5VGFnTmFtZT90LmdldEVsZW1lbnRzQnlUYWdOYW1lKGUpOm4ucXNhP3QucXVlcnlTZWxlY3RvckFsbChlKTp2b2lkIDB9OmZ1bmN0aW9uKGUsdCl7dmFyIG4scj1bXSxpPTAsbz10LmdldEVsZW1lbnRzQnlUYWdOYW1lKGUpO2lmKCIqIj09PWUpe3doaWxlKG49b1tpKytdKTE9PT1uLm5vZGVUeXBlJiZyLnB1c2gobik7cmV0dXJuIHJ9cmV0dXJuIG99LHIuZmluZC5DTEFTUz1uLmdldEVsZW1lbnRzQnlDbGFzc05hbWUmJmZ1bmN0aW9uKGUsdCl7aWYoInVuZGVmaW5lZCIhPXR5cGVvZiB0LmdldEVsZW1lbnRzQnlDbGFzc05hbWUmJmcpcmV0dXJuIHQuZ2V0RWxlbWVudHNCeUNsYXNzTmFtZShlKX0sdj1bXSx5PVtdLChuLnFzYT1RLnRlc3QoZC5xdWVyeVNlbGVjdG9yQWxsKSkmJih1ZShmdW5jdGlvbihlKXtoLmFwcGVuZENoaWxkKGUpLmlubmVySFRNTD0iPGEgaWQ9JyIrYisiJz48L2E+PHNlbGVjdCBpZD0nIitiKyItXHJcXCcgbXNhbGxvd2NhcHR1cmU9Jyc+PG9wdGlvbiBzZWxlY3RlZD0nJz48L29wdGlvbj48L3NlbGVjdD4iLGUucXVlcnlTZWxlY3RvckFsbCgiW21zYWxsb3djYXB0dXJlXj0nJ10iKS5sZW5ndGgmJnkucHVzaCgiWypeJF09IitNKyIqKD86Jyd8XCJcIikiKSxlLnF1ZXJ5U2VsZWN0b3JBbGwoIltzZWxlY3RlZF0iKS5sZW5ndGh8fHkucHVzaCgiXFxbIitNKyIqKD86dmFsdWV8IitQKyIpIiksZS5xdWVyeVNlbGVjdG9yQWxsKCJbaWR+PSIrYisiLV0iKS5sZW5ndGh8fHkucHVzaCgifj0iKSxlLnF1ZXJ5U2VsZWN0b3JBbGwoIjpjaGVja2VkIikubGVuZ3RofHx5LnB1c2goIjpjaGVja2VkIiksZS5xdWVyeVNlbGVjdG9yQWxsKCJhIyIrYisiKyoiKS5sZW5ndGh8fHkucHVzaCgiLiMuK1srfl0iKX0pLHVlKGZ1bmN0aW9uKGUpe2UuaW5uZXJIVE1MPSI8YSBocmVmPScnIGRpc2FibGVkPSdkaXNhYmxlZCc+PC9hPjxzZWxlY3QgZGlzYWJsZWQ9J2Rpc2FibGVkJz48b3B0aW9uLz48L3NlbGVjdD4iO3ZhciB0PWQuY3JlYXRlRWxlbWVudCgiaW5wdXQiKTt0LnNldEF0dHJpYnV0ZSgidHlwZSIsImhpZGRlbiIpLGUuYXBwZW5kQ2hpbGQodCkuc2V0QXR0cmlidXRlKCJuYW1lIiwiRCIpLGUucXVlcnlTZWxlY3RvckFsbCgiW25hbWU9ZF0iKS5sZW5ndGgmJnkucHVzaCgibmFtZSIrTSsiKlsqXiR8IX5dPz0iKSwyIT09ZS5xdWVyeVNlbGVjdG9yQWxsKCI6ZW5hYmxlZCIpLmxlbmd0aCYmeS5wdXNoKCI6ZW5hYmxlZCIsIjpkaXNhYmxlZCIpLGguYXBwZW5kQ2hpbGQoZSkuZGlzYWJsZWQ9ITAsMiE9PWUucXVlcnlTZWxlY3RvckFsbCgiOmRpc2FibGVkIikubGVuZ3RoJiZ5LnB1c2goIjplbmFibGVkIiwiOmRpc2FibGVkIiksZS5xdWVyeVNlbGVjdG9yQWxsKCIqLDp4IikseS5wdXNoKCIsLio6Iil9KSksKG4ubWF0Y2hlc1NlbGVjdG9yPVEudGVzdChtPWgubWF0Y2hlc3x8aC53ZWJraXRNYXRjaGVzU2VsZWN0b3J8fGgubW96TWF0Y2hlc1NlbGVjdG9yfHxoLm9NYXRjaGVzU2VsZWN0b3J8fGgubXNNYXRjaGVzU2VsZWN0b3IpKSYmdWUoZnVuY3Rpb24oZSl7bi5kaXNjb25uZWN0ZWRNYXRjaD1tLmNhbGwoZSwiKiIpLG0uY2FsbChlLCJbcyE9JyddOngiKSx2LnB1c2goIiE9IixXKX0pLHk9eS5sZW5ndGgmJm5ldyBSZWdFeHAoeS5qb2luKCJ8IikpLHY9di5sZW5ndGgmJm5ldyBSZWdFeHAodi5qb2luKCJ8IikpLHQ9US50ZXN0KGguY29tcGFyZURvY3VtZW50UG9zaXRpb24pLHg9dHx8US50ZXN0KGguY29udGFpbnMpP2Z1bmN0aW9uKGUsdCl7dmFyIG49OT09PWUubm9kZVR5cGU/ZS5kb2N1bWVudEVsZW1lbnQ6ZSxyPXQmJnQucGFyZW50Tm9kZTtyZXR1cm4gZT09PXJ8fCEoIXJ8fDEhPT1yLm5vZGVUeXBlfHwhKG4uY29udGFpbnM/bi5jb250YWlucyhyKTplLmNvbXBhcmVEb2N1bWVudFBvc2l0aW9uJiYxNiZlLmNvbXBhcmVEb2N1bWVudFBvc2l0aW9uKHIpKSl9OmZ1bmN0aW9uKGUsdCl7aWYodCl3aGlsZSh0PXQucGFyZW50Tm9kZSlpZih0PT09ZSlyZXR1cm4hMDtyZXR1cm4hMX0sRD10P2Z1bmN0aW9uKGUsdCl7aWYoZT09PXQpcmV0dXJuIGY9ITAsMDt2YXIgcj0hZS5jb21wYXJlRG9jdW1lbnRQb3NpdGlvbi0hdC5jb21wYXJlRG9jdW1lbnRQb3NpdGlvbjtyZXR1cm4gcnx8KDEmKHI9KGUub3duZXJEb2N1bWVudHx8ZSk9PT0odC5vd25lckRvY3VtZW50fHx0KT9lLmNvbXBhcmVEb2N1bWVudFBvc2l0aW9uKHQpOjEpfHwhbi5zb3J0RGV0YWNoZWQmJnQuY29tcGFyZURvY3VtZW50UG9zaXRpb24oZSk9PT1yP2U9PT1kfHxlLm93bmVyRG9jdW1lbnQ9PT13JiZ4KHcsZSk/LTE6dD09PWR8fHQub3duZXJEb2N1bWVudD09PXcmJngodyx0KT8xOmM/TyhjLGUpLU8oYyx0KTowOjQmcj8tMToxKX06ZnVuY3Rpb24oZSx0KXtpZihlPT09dClyZXR1cm4gZj0hMCwwO3ZhciBuLHI9MCxpPWUucGFyZW50Tm9kZSxvPXQucGFyZW50Tm9kZSxhPVtlXSxzPVt0XTtpZighaXx8IW8pcmV0dXJuIGU9PT1kPy0xOnQ9PT1kPzE6aT8tMTpvPzE6Yz9PKGMsZSktTyhjLHQpOjA7aWYoaT09PW8pcmV0dXJuIGNlKGUsdCk7bj1lO3doaWxlKG49bi5wYXJlbnROb2RlKWEudW5zaGlmdChuKTtuPXQ7d2hpbGUobj1uLnBhcmVudE5vZGUpcy51bnNoaWZ0KG4pO3doaWxlKGFbcl09PT1zW3JdKXIrKztyZXR1cm4gcj9jZShhW3JdLHNbcl0pOmFbcl09PT13Py0xOnNbcl09PT13PzE6MH0sZCk6ZH0sb2UubWF0Y2hlcz1mdW5jdGlvbihlLHQpe3JldHVybiBvZShlLG51bGwsbnVsbCx0KX0sb2UubWF0Y2hlc1NlbGVjdG9yPWZ1bmN0aW9uKGUsdCl7aWYoKGUub3duZXJEb2N1bWVudHx8ZSkhPT1kJiZwKGUpLHQ9dC5yZXBsYWNlKHosIj0nJDEnXSIpLG4ubWF0Y2hlc1NlbGVjdG9yJiZnJiYhU1t0KyIgIl0mJighdnx8IXYudGVzdCh0KSkmJigheXx8IXkudGVzdCh0KSkpdHJ5e3ZhciByPW0uY2FsbChlLHQpO2lmKHJ8fG4uZGlzY29ubmVjdGVkTWF0Y2h8fGUuZG9jdW1lbnQmJjExIT09ZS5kb2N1bWVudC5ub2RlVHlwZSlyZXR1cm4gcn1jYXRjaChlKXt9cmV0dXJuIG9lKHQsZCxudWxsLFtlXSkubGVuZ3RoPjB9LG9lLmNvbnRhaW5zPWZ1bmN0aW9uKGUsdCl7cmV0dXJuKGUub3duZXJEb2N1bWVudHx8ZSkhPT1kJiZwKGUpLHgoZSx0KX0sb2UuYXR0cj1mdW5jdGlvbihlLHQpeyhlLm93bmVyRG9jdW1lbnR8fGUpIT09ZCYmcChlKTt2YXIgaT1yLmF0dHJIYW5kbGVbdC50b0xvd2VyQ2FzZSgpXSxvPWkmJk4uY2FsbChyLmF0dHJIYW5kbGUsdC50b0xvd2VyQ2FzZSgpKT9pKGUsdCwhZyk6dm9pZCAwO3JldHVybiB2b2lkIDAhPT1vP286bi5hdHRyaWJ1dGVzfHwhZz9lLmdldEF0dHJpYnV0ZSh0KToobz1lLmdldEF0dHJpYnV0ZU5vZGUodCkpJiZvLnNwZWNpZmllZD9vLnZhbHVlOm51bGx9LG9lLmVzY2FwZT1mdW5jdGlvbihlKXtyZXR1cm4oZSsiIikucmVwbGFjZSh0ZSxuZSl9LG9lLmVycm9yPWZ1bmN0aW9uKGUpe3Rocm93IG5ldyBFcnJvcigiU3ludGF4IGVycm9yLCB1bnJlY29nbml6ZWQgZXhwcmVzc2lvbjogIitlKX0sb2UudW5pcXVlU29ydD1mdW5jdGlvbihlKXt2YXIgdCxyPVtdLGk9MCxvPTA7aWYoZj0hbi5kZXRlY3REdXBsaWNhdGVzLGM9IW4uc29ydFN0YWJsZSYmZS5zbGljZSgwKSxlLnNvcnQoRCksZil7d2hpbGUodD1lW28rK10pdD09PWVbb10mJihpPXIucHVzaChvKSk7d2hpbGUoaS0tKWUuc3BsaWNlKHJbaV0sMSl9cmV0dXJuIGM9bnVsbCxlfSxpPW9lLmdldFRleHQ9ZnVuY3Rpb24oZSl7dmFyIHQsbj0iIixyPTAsbz1lLm5vZGVUeXBlO2lmKG8pe2lmKDE9PT1vfHw5PT09b3x8MTE9PT1vKXtpZigic3RyaW5nIj09dHlwZW9mIGUudGV4dENvbnRlbnQpcmV0dXJuIGUudGV4dENvbnRlbnQ7Zm9yKGU9ZS5maXJzdENoaWxkO2U7ZT1lLm5leHRTaWJsaW5nKW4rPWkoZSl9ZWxzZSBpZigzPT09b3x8ND09PW8pcmV0dXJuIGUubm9kZVZhbHVlfWVsc2Ugd2hpbGUodD1lW3IrK10pbis9aSh0KTtyZXR1cm4gbn0sKHI9b2Uuc2VsZWN0b3JzPXtjYWNoZUxlbmd0aDo1MCxjcmVhdGVQc2V1ZG86c2UsbWF0Y2g6VixhdHRySGFuZGxlOnt9LGZpbmQ6e30scmVsYXRpdmU6eyI+Ijp7ZGlyOiJwYXJlbnROb2RlIixmaXJzdDohMH0sIiAiOntkaXI6InBhcmVudE5vZGUifSwiKyI6e2RpcjoicHJldmlvdXNTaWJsaW5nIixmaXJzdDohMH0sIn4iOntkaXI6InByZXZpb3VzU2libGluZyJ9fSxwcmVGaWx0ZXI6e0FUVFI6ZnVuY3Rpb24oZSl7cmV0dXJuIGVbMV09ZVsxXS5yZXBsYWNlKFosZWUpLGVbM109KGVbM118fGVbNF18fGVbNV18fCIiKS5yZXBsYWNlKFosZWUpLCJ+PSI9PT1lWzJdJiYoZVszXT0iICIrZVszXSsiICIpLGUuc2xpY2UoMCw0KX0sQ0hJTEQ6ZnVuY3Rpb24oZSl7cmV0dXJuIGVbMV09ZVsxXS50b0xvd2VyQ2FzZSgpLCJudGgiPT09ZVsxXS5zbGljZSgwLDMpPyhlWzNdfHxvZS5lcnJvcihlWzBdKSxlWzRdPSsoZVs0XT9lWzVdKyhlWzZdfHwxKToyKigiZXZlbiI9PT1lWzNdfHwib2RkIj09PWVbM10pKSxlWzVdPSsoZVs3XStlWzhdfHwib2RkIj09PWVbM10pKTplWzNdJiZvZS5lcnJvcihlWzBdKSxlfSxQU0VVRE86ZnVuY3Rpb24oZSl7dmFyIHQsbj0hZVs2XSYmZVsyXTtyZXR1cm4gVi5DSElMRC50ZXN0KGVbMF0pP251bGw6KGVbM10/ZVsyXT1lWzRdfHxlWzVdfHwiIjpuJiZYLnRlc3QobikmJih0PWEobiwhMCkpJiYodD1uLmluZGV4T2YoIikiLG4ubGVuZ3RoLXQpLW4ubGVuZ3RoKSYmKGVbMF09ZVswXS5zbGljZSgwLHQpLGVbMl09bi5zbGljZSgwLHQpKSxlLnNsaWNlKDAsMykpfX0sZmlsdGVyOntUQUc6ZnVuY3Rpb24oZSl7dmFyIHQ9ZS5yZXBsYWNlKFosZWUpLnRvTG93ZXJDYXNlKCk7cmV0dXJuIioiPT09ZT9mdW5jdGlvbigpe3JldHVybiEwfTpmdW5jdGlvbihlKXtyZXR1cm4gZS5ub2RlTmFtZSYmZS5ub2RlTmFtZS50b0xvd2VyQ2FzZSgpPT09dH19LENMQVNTOmZ1bmN0aW9uKGUpe3ZhciB0PUVbZSsiICJdO3JldHVybiB0fHwodD1uZXcgUmVnRXhwKCIoXnwiK00rIikiK2UrIigiK00rInwkKSIpKSYmRShlLGZ1bmN0aW9uKGUpe3JldHVybiB0LnRlc3QoInN0cmluZyI9PXR5cGVvZiBlLmNsYXNzTmFtZSYmZS5jbGFzc05hbWV8fCJ1bmRlZmluZWQiIT10eXBlb2YgZS5nZXRBdHRyaWJ1dGUmJmUuZ2V0QXR0cmlidXRlKCJjbGFzcyIpfHwiIil9KX0sQVRUUjpmdW5jdGlvbihlLHQsbil7cmV0dXJuIGZ1bmN0aW9uKHIpe3ZhciBpPW9lLmF0dHIocixlKTtyZXR1cm4gbnVsbD09aT8iIT0iPT09dDohdHx8KGkrPSIiLCI9Ij09PXQ/aT09PW46IiE9Ij09PXQ/aSE9PW46Il49Ij09PXQ/biYmMD09PWkuaW5kZXhPZihuKToiKj0iPT09dD9uJiZpLmluZGV4T2Yobik+LTE6IiQ9Ij09PXQ/biYmaS5zbGljZSgtbi5sZW5ndGgpPT09bjoifj0iPT09dD8oIiAiK2kucmVwbGFjZSgkLCIgIikrIiAiKS5pbmRleE9mKG4pPi0xOiJ8PSI9PT10JiYoaT09PW58fGkuc2xpY2UoMCxuLmxlbmd0aCsxKT09PW4rIi0iKSl9fSxDSElMRDpmdW5jdGlvbihlLHQsbixyLGkpe3ZhciBvPSJudGgiIT09ZS5zbGljZSgwLDMpLGE9Imxhc3QiIT09ZS5zbGljZSgtNCkscz0ib2YtdHlwZSI9PT10O3JldHVybiAxPT09ciYmMD09PWk/ZnVuY3Rpb24oZSl7cmV0dXJuISFlLnBhcmVudE5vZGV9OmZ1bmN0aW9uKHQsbix1KXt2YXIgbCxjLGYscCxkLGgsZz1vIT09YT8ibmV4dFNpYmxpbmciOiJwcmV2aW91c1NpYmxpbmciLHk9dC5wYXJlbnROb2RlLHY9cyYmdC5ub2RlTmFtZS50b0xvd2VyQ2FzZSgpLG09IXUmJiFzLHg9ITE7aWYoeSl7aWYobyl7d2hpbGUoZyl7cD10O3doaWxlKHA9cFtnXSlpZihzP3Aubm9kZU5hbWUudG9Mb3dlckNhc2UoKT09PXY6MT09PXAubm9kZVR5cGUpcmV0dXJuITE7aD1nPSJvbmx5Ij09PWUmJiFoJiYibmV4dFNpYmxpbmcifXJldHVybiEwfWlmKGg9W2E/eS5maXJzdENoaWxkOnkubGFzdENoaWxkXSxhJiZtKXt4PShkPShsPShjPShmPShwPXkpW2JdfHwocFtiXT17fSkpW3AudW5pcXVlSURdfHwoZltwLnVuaXF1ZUlEXT17fSkpW2VdfHxbXSlbMF09PT1UJiZsWzFdKSYmbFsyXSxwPWQmJnkuY2hpbGROb2Rlc1tkXTt3aGlsZShwPSsrZCYmcCYmcFtnXXx8KHg9ZD0wKXx8aC5wb3AoKSlpZigxPT09cC5ub2RlVHlwZSYmKyt4JiZwPT09dCl7Y1tlXT1bVCxkLHhdO2JyZWFrfX1lbHNlIGlmKG0mJih4PWQ9KGw9KGM9KGY9KHA9dClbYl18fChwW2JdPXt9KSlbcC51bmlxdWVJRF18fChmW3AudW5pcXVlSURdPXt9KSlbZV18fFtdKVswXT09PVQmJmxbMV0pLCExPT09eCl3aGlsZShwPSsrZCYmcCYmcFtnXXx8KHg9ZD0wKXx8aC5wb3AoKSlpZigocz9wLm5vZGVOYW1lLnRvTG93ZXJDYXNlKCk9PT12OjE9PT1wLm5vZGVUeXBlKSYmKyt4JiYobSYmKChjPShmPXBbYl18fChwW2JdPXt9KSlbcC51bmlxdWVJRF18fChmW3AudW5pcXVlSURdPXt9KSlbZV09W1QseF0pLHA9PT10KSlicmVhaztyZXR1cm4oeC09aSk9PT1yfHx4JXI9PTAmJngvcj49MH19fSxQU0VVRE86ZnVuY3Rpb24oZSx0KXt2YXIgbixpPXIucHNldWRvc1tlXXx8ci5zZXRGaWx0ZXJzW2UudG9Mb3dlckNhc2UoKV18fG9lLmVycm9yKCJ1bnN1cHBvcnRlZCBwc2V1ZG86ICIrZSk7cmV0dXJuIGlbYl0/aSh0KTppLmxlbmd0aD4xPyhuPVtlLGUsIiIsdF0sci5zZXRGaWx0ZXJzLmhhc093blByb3BlcnR5KGUudG9Mb3dlckNhc2UoKSk/c2UoZnVuY3Rpb24oZSxuKXt2YXIgcixvPWkoZSx0KSxhPW8ubGVuZ3RoO3doaWxlKGEtLSllW3I9TyhlLG9bYV0pXT0hKG5bcl09b1thXSl9KTpmdW5jdGlvbihlKXtyZXR1cm4gaShlLDAsbil9KTppfX0scHNldWRvczp7bm90OnNlKGZ1bmN0aW9uKGUpe3ZhciB0PVtdLG49W10scj1zKGUucmVwbGFjZShCLCIkMSIpKTtyZXR1cm4gcltiXT9zZShmdW5jdGlvbihlLHQsbixpKXt2YXIgbyxhPXIoZSxudWxsLGksW10pLHM9ZS5sZW5ndGg7d2hpbGUocy0tKShvPWFbc10pJiYoZVtzXT0hKHRbc109bykpfSk6ZnVuY3Rpb24oZSxpLG8pe3JldHVybiB0WzBdPWUscih0LG51bGwsbyxuKSx0WzBdPW51bGwsIW4ucG9wKCl9fSksaGFzOnNlKGZ1bmN0aW9uKGUpe3JldHVybiBmdW5jdGlvbih0KXtyZXR1cm4gb2UoZSx0KS5sZW5ndGg+MH19KSxjb250YWluczpzZShmdW5jdGlvbihlKXtyZXR1cm4gZT1lLnJlcGxhY2UoWixlZSksZnVuY3Rpb24odCl7cmV0dXJuKHQudGV4dENvbnRlbnR8fHQuaW5uZXJUZXh0fHxpKHQpKS5pbmRleE9mKGUpPi0xfX0pLGxhbmc6c2UoZnVuY3Rpb24oZSl7cmV0dXJuIFUudGVzdChlfHwiIil8fG9lLmVycm9yKCJ1bnN1cHBvcnRlZCBsYW5nOiAiK2UpLGU9ZS5yZXBsYWNlKFosZWUpLnRvTG93ZXJDYXNlKCksZnVuY3Rpb24odCl7dmFyIG47ZG97aWYobj1nP3QubGFuZzp0LmdldEF0dHJpYnV0ZSgieG1sOmxhbmciKXx8dC5nZXRBdHRyaWJ1dGUoImxhbmciKSlyZXR1cm4obj1uLnRvTG93ZXJDYXNlKCkpPT09ZXx8MD09PW4uaW5kZXhPZihlKyItIil9d2hpbGUoKHQ9dC5wYXJlbnROb2RlKSYmMT09PXQubm9kZVR5cGUpO3JldHVybiExfX0pLHRhcmdldDpmdW5jdGlvbih0KXt2YXIgbj1lLmxvY2F0aW9uJiZlLmxvY2F0aW9uLmhhc2g7cmV0dXJuIG4mJm4uc2xpY2UoMSk9PT10LmlkfSxyb290OmZ1bmN0aW9uKGUpe3JldHVybiBlPT09aH0sZm9jdXM6ZnVuY3Rpb24oZSl7cmV0dXJuIGU9PT1kLmFjdGl2ZUVsZW1lbnQmJighZC5oYXNGb2N1c3x8ZC5oYXNGb2N1cygpKSYmISEoZS50eXBlfHxlLmhyZWZ8fH5lLnRhYkluZGV4KX0sZW5hYmxlZDpkZSghMSksZGlzYWJsZWQ6ZGUoITApLGNoZWNrZWQ6ZnVuY3Rpb24oZSl7dmFyIHQ9ZS5ub2RlTmFtZS50b0xvd2VyQ2FzZSgpO3JldHVybiJpbnB1dCI9PT10JiYhIWUuY2hlY2tlZHx8Im9wdGlvbiI9PT10JiYhIWUuc2VsZWN0ZWR9LHNlbGVjdGVkOmZ1bmN0aW9uKGUpe3JldHVybiBlLnBhcmVudE5vZGUmJmUucGFyZW50Tm9kZS5zZWxlY3RlZEluZGV4LCEwPT09ZS5zZWxlY3RlZH0sZW1wdHk6ZnVuY3Rpb24oZSl7Zm9yKGU9ZS5maXJzdENoaWxkO2U7ZT1lLm5leHRTaWJsaW5nKWlmKGUubm9kZVR5cGU8NilyZXR1cm4hMTtyZXR1cm4hMH0scGFyZW50OmZ1bmN0aW9uKGUpe3JldHVybiFyLnBzZXVkb3MuZW1wdHkoZSl9LGhlYWRlcjpmdW5jdGlvbihlKXtyZXR1cm4gWS50ZXN0KGUubm9kZU5hbWUpfSxpbnB1dDpmdW5jdGlvbihlKXtyZXR1cm4gRy50ZXN0KGUubm9kZU5hbWUpfSxidXR0b246ZnVuY3Rpb24oZSl7dmFyIHQ9ZS5ub2RlTmFtZS50b0xvd2VyQ2FzZSgpO3JldHVybiJpbnB1dCI9PT10JiYiYnV0dG9uIj09PWUudHlwZXx8ImJ1dHRvbiI9PT10fSx0ZXh0OmZ1bmN0aW9uKGUpe3ZhciB0O3JldHVybiJpbnB1dCI9PT1lLm5vZGVOYW1lLnRvTG93ZXJDYXNlKCkmJiJ0ZXh0Ij09PWUudHlwZSYmKG51bGw9PSh0PWUuZ2V0QXR0cmlidXRlKCJ0eXBlIikpfHwidGV4dCI9PT10LnRvTG93ZXJDYXNlKCkpfSxmaXJzdDpoZShmdW5jdGlvbigpe3JldHVyblswXX0pLGxhc3Q6aGUoZnVuY3Rpb24oZSx0KXtyZXR1cm5bdC0xXX0pLGVxOmhlKGZ1bmN0aW9uKGUsdCxuKXtyZXR1cm5bbjwwP24rdDpuXX0pLGV2ZW46aGUoZnVuY3Rpb24oZSx0KXtmb3IodmFyIG49MDtuPHQ7bis9MillLnB1c2gobik7cmV0dXJuIGV9KSxvZGQ6aGUoZnVuY3Rpb24oZSx0KXtmb3IodmFyIG49MTtuPHQ7bis9MillLnB1c2gobik7cmV0dXJuIGV9KSxsdDpoZShmdW5jdGlvbihlLHQsbil7Zm9yKHZhciByPW48MD9uK3Q6bjstLXI+PTA7KWUucHVzaChyKTtyZXR1cm4gZX0pLGd0OmhlKGZ1bmN0aW9uKGUsdCxuKXtmb3IodmFyIHI9bjwwP24rdDpuOysrcjx0OyllLnB1c2gocik7cmV0dXJuIGV9KX19KS5wc2V1ZG9zLm50aD1yLnBzZXVkb3MuZXE7Zm9yKHQgaW57cmFkaW86ITAsY2hlY2tib3g6ITAsZmlsZTohMCxwYXNzd29yZDohMCxpbWFnZTohMH0pci5wc2V1ZG9zW3RdPWZlKHQpO2Zvcih0IGlue3N1Ym1pdDohMCxyZXNldDohMH0pci5wc2V1ZG9zW3RdPXBlKHQpO2Z1bmN0aW9uIHllKCl7fXllLnByb3RvdHlwZT1yLmZpbHRlcnM9ci5wc2V1ZG9zLHIuc2V0RmlsdGVycz1uZXcgeWUsYT1vZS50b2tlbml6ZT1mdW5jdGlvbihlLHQpe3ZhciBuLGksbyxhLHMsdSxsLGM9a1tlKyIgIl07aWYoYylyZXR1cm4gdD8wOmMuc2xpY2UoMCk7cz1lLHU9W10sbD1yLnByZUZpbHRlcjt3aGlsZShzKXtuJiYhKGk9Ri5leGVjKHMpKXx8KGkmJihzPXMuc2xpY2UoaVswXS5sZW5ndGgpfHxzKSx1LnB1c2gobz1bXSkpLG49ITEsKGk9Xy5leGVjKHMpKSYmKG49aS5zaGlmdCgpLG8ucHVzaCh7dmFsdWU6bix0eXBlOmlbMF0ucmVwbGFjZShCLCIgIil9KSxzPXMuc2xpY2Uobi5sZW5ndGgpKTtmb3IoYSBpbiByLmZpbHRlcikhKGk9VlthXS5leGVjKHMpKXx8bFthXSYmIShpPWxbYV0oaSkpfHwobj1pLnNoaWZ0KCksby5wdXNoKHt2YWx1ZTpuLHR5cGU6YSxtYXRjaGVzOml9KSxzPXMuc2xpY2Uobi5sZW5ndGgpKTtpZighbilicmVha31yZXR1cm4gdD9zLmxlbmd0aDpzP29lLmVycm9yKGUpOmsoZSx1KS5zbGljZSgwKX07ZnVuY3Rpb24gdmUoZSl7Zm9yKHZhciB0PTAsbj1lLmxlbmd0aCxyPSIiO3Q8bjt0Kyspcis9ZVt0XS52YWx1ZTtyZXR1cm4gcn1mdW5jdGlvbiBtZShlLHQsbil7dmFyIHI9dC5kaXIsaT10Lm5leHQsbz1pfHxyLGE9biYmInBhcmVudE5vZGUiPT09byxzPUMrKztyZXR1cm4gdC5maXJzdD9mdW5jdGlvbih0LG4saSl7d2hpbGUodD10W3JdKWlmKDE9PT10Lm5vZGVUeXBlfHxhKXJldHVybiBlKHQsbixpKTtyZXR1cm4hMX06ZnVuY3Rpb24odCxuLHUpe3ZhciBsLGMsZixwPVtULHNdO2lmKHUpe3doaWxlKHQ9dFtyXSlpZigoMT09PXQubm9kZVR5cGV8fGEpJiZlKHQsbix1KSlyZXR1cm4hMH1lbHNlIHdoaWxlKHQ9dFtyXSlpZigxPT09dC5ub2RlVHlwZXx8YSlpZihmPXRbYl18fCh0W2JdPXt9KSxjPWZbdC51bmlxdWVJRF18fChmW3QudW5pcXVlSURdPXt9KSxpJiZpPT09dC5ub2RlTmFtZS50b0xvd2VyQ2FzZSgpKXQ9dFtyXXx8dDtlbHNle2lmKChsPWNbb10pJiZsWzBdPT09VCYmbFsxXT09PXMpcmV0dXJuIHBbMl09bFsyXTtpZihjW29dPXAscFsyXT1lKHQsbix1KSlyZXR1cm4hMH1yZXR1cm4hMX19ZnVuY3Rpb24geGUoZSl7cmV0dXJuIGUubGVuZ3RoPjE/ZnVuY3Rpb24odCxuLHIpe3ZhciBpPWUubGVuZ3RoO3doaWxlKGktLSlpZighZVtpXSh0LG4scikpcmV0dXJuITE7cmV0dXJuITB9OmVbMF19ZnVuY3Rpb24gYmUoZSx0LG4pe2Zvcih2YXIgcj0wLGk9dC5sZW5ndGg7cjxpO3IrKylvZShlLHRbcl0sbik7cmV0dXJuIG59ZnVuY3Rpb24gd2UoZSx0LG4scixpKXtmb3IodmFyIG8sYT1bXSxzPTAsdT1lLmxlbmd0aCxsPW51bGwhPXQ7czx1O3MrKykobz1lW3NdKSYmKG4mJiFuKG8scixpKXx8KGEucHVzaChvKSxsJiZ0LnB1c2gocykpKTtyZXR1cm4gYX1mdW5jdGlvbiBUZShlLHQsbixyLGksbyl7cmV0dXJuIHImJiFyW2JdJiYocj1UZShyKSksaSYmIWlbYl0mJihpPVRlKGksbykpLHNlKGZ1bmN0aW9uKG8sYSxzLHUpe3ZhciBsLGMsZixwPVtdLGQ9W10saD1hLmxlbmd0aCxnPW98fGJlKHR8fCIqIixzLm5vZGVUeXBlP1tzXTpzLFtdKSx5PSFlfHwhbyYmdD9nOndlKGcscCxlLHMsdSksdj1uP2l8fChvP2U6aHx8cik/W106YTp5O2lmKG4mJm4oeSx2LHMsdSkscil7bD13ZSh2LGQpLHIobCxbXSxzLHUpLGM9bC5sZW5ndGg7d2hpbGUoYy0tKShmPWxbY10pJiYodltkW2NdXT0hKHlbZFtjXV09ZikpfWlmKG8pe2lmKGl8fGUpe2lmKGkpe2w9W10sYz12Lmxlbmd0aDt3aGlsZShjLS0pKGY9dltjXSkmJmwucHVzaCh5W2NdPWYpO2kobnVsbCx2PVtdLGwsdSl9Yz12Lmxlbmd0aDt3aGlsZShjLS0pKGY9dltjXSkmJihsPWk/TyhvLGYpOnBbY10pPi0xJiYob1tsXT0hKGFbbF09ZikpfX1lbHNlIHY9d2Uodj09PWE/di5zcGxpY2UoaCx2Lmxlbmd0aCk6diksaT9pKG51bGwsYSx2LHUpOkwuYXBwbHkoYSx2KX0pfWZ1bmN0aW9uIENlKGUpe2Zvcih2YXIgdCxuLGksbz1lLmxlbmd0aCxhPXIucmVsYXRpdmVbZVswXS50eXBlXSxzPWF8fHIucmVsYXRpdmVbIiAiXSx1PWE/MTowLGM9bWUoZnVuY3Rpb24oZSl7cmV0dXJuIGU9PT10fSxzLCEwKSxmPW1lKGZ1bmN0aW9uKGUpe3JldHVybiBPKHQsZSk+LTF9LHMsITApLHA9W2Z1bmN0aW9uKGUsbixyKXt2YXIgaT0hYSYmKHJ8fG4hPT1sKXx8KCh0PW4pLm5vZGVUeXBlP2MoZSxuLHIpOmYoZSxuLHIpKTtyZXR1cm4gdD1udWxsLGl9XTt1PG87dSsrKWlmKG49ci5yZWxhdGl2ZVtlW3VdLnR5cGVdKXA9W21lKHhlKHApLG4pXTtlbHNle2lmKChuPXIuZmlsdGVyW2VbdV0udHlwZV0uYXBwbHkobnVsbCxlW3VdLm1hdGNoZXMpKVtiXSl7Zm9yKGk9Kyt1O2k8bztpKyspaWYoci5yZWxhdGl2ZVtlW2ldLnR5cGVdKWJyZWFrO3JldHVybiBUZSh1PjEmJnhlKHApLHU+MSYmdmUoZS5zbGljZSgwLHUtMSkuY29uY2F0KHt2YWx1ZToiICI9PT1lW3UtMl0udHlwZT8iKiI6IiJ9KSkucmVwbGFjZShCLCIkMSIpLG4sdTxpJiZDZShlLnNsaWNlKHUsaSkpLGk8byYmQ2UoZT1lLnNsaWNlKGkpKSxpPG8mJnZlKGUpKX1wLnB1c2gobil9cmV0dXJuIHhlKHApfWZ1bmN0aW9uIEVlKGUsdCl7dmFyIG49dC5sZW5ndGg+MCxpPWUubGVuZ3RoPjAsbz1mdW5jdGlvbihvLGEscyx1LGMpe3ZhciBmLGgseSx2PTAsbT0iMCIseD1vJiZbXSxiPVtdLHc9bCxDPW98fGkmJnIuZmluZC5UQUcoIioiLGMpLEU9VCs9bnVsbD09dz8xOk1hdGgucmFuZG9tKCl8fC4xLGs9Qy5sZW5ndGg7Zm9yKGMmJihsPWE9PT1kfHxhfHxjKTttIT09ayYmbnVsbCE9KGY9Q1ttXSk7bSsrKXtpZihpJiZmKXtoPTAsYXx8Zi5vd25lckRvY3VtZW50PT09ZHx8KHAoZikscz0hZyk7d2hpbGUoeT1lW2grK10paWYoeShmLGF8fGQscykpe3UucHVzaChmKTticmVha31jJiYoVD1FKX1uJiYoKGY9IXkmJmYpJiZ2LS0sbyYmeC5wdXNoKGYpKX1pZih2Kz1tLG4mJm0hPT12KXtoPTA7d2hpbGUoeT10W2grK10peSh4LGIsYSxzKTtpZihvKXtpZih2PjApd2hpbGUobS0tKXhbbV18fGJbbV18fChiW21dPWouY2FsbCh1KSk7Yj13ZShiKX1MLmFwcGx5KHUsYiksYyYmIW8mJmIubGVuZ3RoPjAmJnYrdC5sZW5ndGg+MSYmb2UudW5pcXVlU29ydCh1KX1yZXR1cm4gYyYmKFQ9RSxsPXcpLHh9O3JldHVybiBuP3NlKG8pOm99cmV0dXJuIHM9b2UuY29tcGlsZT1mdW5jdGlvbihlLHQpe3ZhciBuLHI9W10saT1bXSxvPVNbZSsiICJdO2lmKCFvKXt0fHwodD1hKGUpKSxuPXQubGVuZ3RoO3doaWxlKG4tLSkobz1DZSh0W25dKSlbYl0/ci5wdXNoKG8pOmkucHVzaChvKTsobz1TKGUsRWUoaSxyKSkpLnNlbGVjdG9yPWV9cmV0dXJuIG99LHU9b2Uuc2VsZWN0PWZ1bmN0aW9uKGUsdCxuLGkpe3ZhciBvLHUsbCxjLGYscD0iZnVuY3Rpb24iPT10eXBlb2YgZSYmZSxkPSFpJiZhKGU9cC5zZWxlY3Rvcnx8ZSk7aWYobj1ufHxbXSwxPT09ZC5sZW5ndGgpe2lmKCh1PWRbMF09ZFswXS5zbGljZSgwKSkubGVuZ3RoPjImJiJJRCI9PT0obD11WzBdKS50eXBlJiY5PT09dC5ub2RlVHlwZSYmZyYmci5yZWxhdGl2ZVt1WzFdLnR5cGVdKXtpZighKHQ9KHIuZmluZC5JRChsLm1hdGNoZXNbMF0ucmVwbGFjZShaLGVlKSx0KXx8W10pWzBdKSlyZXR1cm4gbjtwJiYodD10LnBhcmVudE5vZGUpLGU9ZS5zbGljZSh1LnNoaWZ0KCkudmFsdWUubGVuZ3RoKX1vPVYubmVlZHNDb250ZXh0LnRlc3QoZSk/MDp1Lmxlbmd0aDt3aGlsZShvLS0pe2lmKGw9dVtvXSxyLnJlbGF0aXZlW2M9bC50eXBlXSlicmVhaztpZigoZj1yLmZpbmRbY10pJiYoaT1mKGwubWF0Y2hlc1swXS5yZXBsYWNlKFosZWUpLEsudGVzdCh1WzBdLnR5cGUpJiZnZSh0LnBhcmVudE5vZGUpfHx0KSkpe2lmKHUuc3BsaWNlKG8sMSksIShlPWkubGVuZ3RoJiZ2ZSh1KSkpcmV0dXJuIEwuYXBwbHkobixpKSxuO2JyZWFrfX19cmV0dXJuKHB8fHMoZSxkKSkoaSx0LCFnLG4sIXR8fEsudGVzdChlKSYmZ2UodC5wYXJlbnROb2RlKXx8dCksbn0sbi5zb3J0U3RhYmxlPWIuc3BsaXQoIiIpLnNvcnQoRCkuam9pbigiIik9PT1iLG4uZGV0ZWN0RHVwbGljYXRlcz0hIWYscCgpLG4uc29ydERldGFjaGVkPXVlKGZ1bmN0aW9uKGUpe3JldHVybiAxJmUuY29tcGFyZURvY3VtZW50UG9zaXRpb24oZC5jcmVhdGVFbGVtZW50KCJmaWVsZHNldCIpKX0pLHVlKGZ1bmN0aW9uKGUpe3JldHVybiBlLmlubmVySFRNTD0iPGEgaHJlZj0nIyc+PC9hPiIsIiMiPT09ZS5maXJzdENoaWxkLmdldEF0dHJpYnV0ZSgiaHJlZiIpfSl8fGxlKCJ0eXBlfGhyZWZ8aGVpZ2h0fHdpZHRoIixmdW5jdGlvbihlLHQsbil7aWYoIW4pcmV0dXJuIGUuZ2V0QXR0cmlidXRlKHQsInR5cGUiPT09dC50b0xvd2VyQ2FzZSgpPzE6Mil9KSxuLmF0dHJpYnV0ZXMmJnVlKGZ1bmN0aW9uKGUpe3JldHVybiBlLmlubmVySFRNTD0iPGlucHV0Lz4iLGUuZmlyc3RDaGlsZC5zZXRBdHRyaWJ1dGUoInZhbHVlIiwiIiksIiI9PT1lLmZpcnN0Q2hpbGQuZ2V0QXR0cmlidXRlKCJ2YWx1ZSIpfSl8fGxlKCJ2YWx1ZSIsZnVuY3Rpb24oZSx0LG4pe2lmKCFuJiYiaW5wdXQiPT09ZS5ub2RlTmFtZS50b0xvd2VyQ2FzZSgpKXJldHVybiBlLmRlZmF1bHRWYWx1ZX0pLHVlKGZ1bmN0aW9uKGUpe3JldHVybiBudWxsPT1lLmdldEF0dHJpYnV0ZSgiZGlzYWJsZWQiKX0pfHxsZShQLGZ1bmN0aW9uKGUsdCxuKXt2YXIgcjtpZighbilyZXR1cm4hMD09PWVbdF0/dC50b0xvd2VyQ2FzZSgpOihyPWUuZ2V0QXR0cmlidXRlTm9kZSh0KSkmJnIuc3BlY2lmaWVkP3IudmFsdWU6bnVsbH0pLG9lfShlKTt3LmZpbmQ9RSx3LmV4cHI9RS5zZWxlY3RvcnMsdy5leHByWyI6Il09dy5leHByLnBzZXVkb3Msdy51bmlxdWVTb3J0PXcudW5pcXVlPUUudW5pcXVlU29ydCx3LnRleHQ9RS5nZXRUZXh0LHcuaXNYTUxEb2M9RS5pc1hNTCx3LmNvbnRhaW5zPUUuY29udGFpbnMsdy5lc2NhcGVTZWxlY3Rvcj1FLmVzY2FwZTt2YXIgaz1mdW5jdGlvbihlLHQsbil7dmFyIHI9W10saT12b2lkIDAhPT1uO3doaWxlKChlPWVbdF0pJiY5IT09ZS5ub2RlVHlwZSlpZigxPT09ZS5ub2RlVHlwZSl7aWYoaSYmdyhlKS5pcyhuKSlicmVhaztyLnB1c2goZSl9cmV0dXJuIHJ9LFM9ZnVuY3Rpb24oZSx0KXtmb3IodmFyIG49W107ZTtlPWUubmV4dFNpYmxpbmcpMT09PWUubm9kZVR5cGUmJmUhPT10JiZuLnB1c2goZSk7cmV0dXJuIG59LEQ9dy5leHByLm1hdGNoLm5lZWRzQ29udGV4dDtmdW5jdGlvbiBOKGUsdCl7cmV0dXJuIGUubm9kZU5hbWUmJmUubm9kZU5hbWUudG9Mb3dlckNhc2UoKT09PXQudG9Mb3dlckNhc2UoKX12YXIgQT0vXjwoW2Etel1bXlwvXDA+Olx4MjBcdFxyXG5cZl0qKVtceDIwXHRcclxuXGZdKlwvPz4oPzo8XC9cMT58KSQvaTtmdW5jdGlvbiBqKGUsdCxuKXtyZXR1cm4gZyh0KT93LmdyZXAoZSxmdW5jdGlvbihlLHIpe3JldHVybiEhdC5jYWxsKGUscixlKSE9PW59KTp0Lm5vZGVUeXBlP3cuZ3JlcChlLGZ1bmN0aW9uKGUpe3JldHVybiBlPT09dCE9PW59KToic3RyaW5nIiE9dHlwZW9mIHQ/dy5ncmVwKGUsZnVuY3Rpb24oZSl7cmV0dXJuIHUuY2FsbCh0LGUpPi0xIT09bn0pOncuZmlsdGVyKHQsZSxuKX13LmZpbHRlcj1mdW5jdGlvbihlLHQsbil7dmFyIHI9dFswXTtyZXR1cm4gbiYmKGU9Ijpub3QoIitlKyIpIiksMT09PXQubGVuZ3RoJiYxPT09ci5ub2RlVHlwZT93LmZpbmQubWF0Y2hlc1NlbGVjdG9yKHIsZSk/W3JdOltdOncuZmluZC5tYXRjaGVzKGUsdy5ncmVwKHQsZnVuY3Rpb24oZSl7cmV0dXJuIDE9PT1lLm5vZGVUeXBlfSkpfSx3LmZuLmV4dGVuZCh7ZmluZDpmdW5jdGlvbihlKXt2YXIgdCxuLHI9dGhpcy5sZW5ndGgsaT10aGlzO2lmKCJzdHJpbmciIT10eXBlb2YgZSlyZXR1cm4gdGhpcy5wdXNoU3RhY2sodyhlKS5maWx0ZXIoZnVuY3Rpb24oKXtmb3IodD0wO3Q8cjt0KyspaWYody5jb250YWlucyhpW3RdLHRoaXMpKXJldHVybiEwfSkpO2ZvcihuPXRoaXMucHVzaFN0YWNrKFtdKSx0PTA7dDxyO3QrKyl3LmZpbmQoZSxpW3RdLG4pO3JldHVybiByPjE/dy51bmlxdWVTb3J0KG4pOm59LGZpbHRlcjpmdW5jdGlvbihlKXtyZXR1cm4gdGhpcy5wdXNoU3RhY2soaih0aGlzLGV8fFtdLCExKSl9LG5vdDpmdW5jdGlvbihlKXtyZXR1cm4gdGhpcy5wdXNoU3RhY2soaih0aGlzLGV8fFtdLCEwKSl9LGlzOmZ1bmN0aW9uKGUpe3JldHVybiEhaih0aGlzLCJzdHJpbmciPT10eXBlb2YgZSYmRC50ZXN0KGUpP3coZSk6ZXx8W10sITEpLmxlbmd0aH19KTt2YXIgcSxMPS9eKD86XHMqKDxbXHdcV10rPilbXj5dKnwjKFtcdy1dKykpJC87KHcuZm4uaW5pdD1mdW5jdGlvbihlLHQsbil7dmFyIGksbztpZighZSlyZXR1cm4gdGhpcztpZihuPW58fHEsInN0cmluZyI9PXR5cGVvZiBlKXtpZighKGk9IjwiPT09ZVswXSYmIj4iPT09ZVtlLmxlbmd0aC0xXSYmZS5sZW5ndGg+PTM/W251bGwsZSxudWxsXTpMLmV4ZWMoZSkpfHwhaVsxXSYmdClyZXR1cm4hdHx8dC5qcXVlcnk/KHR8fG4pLmZpbmQoZSk6dGhpcy5jb25zdHJ1Y3Rvcih0KS5maW5kKGUpO2lmKGlbMV0pe2lmKHQ9dCBpbnN0YW5jZW9mIHc/dFswXTp0LHcubWVyZ2UodGhpcyx3LnBhcnNlSFRNTChpWzFdLHQmJnQubm9kZVR5cGU/dC5vd25lckRvY3VtZW50fHx0OnIsITApKSxBLnRlc3QoaVsxXSkmJncuaXNQbGFpbk9iamVjdCh0KSlmb3IoaSBpbiB0KWcodGhpc1tpXSk/dGhpc1tpXSh0W2ldKTp0aGlzLmF0dHIoaSx0W2ldKTtyZXR1cm4gdGhpc31yZXR1cm4obz1yLmdldEVsZW1lbnRCeUlkKGlbMl0pKSYmKHRoaXNbMF09byx0aGlzLmxlbmd0aD0xKSx0aGlzfXJldHVybiBlLm5vZGVUeXBlPyh0aGlzWzBdPWUsdGhpcy5sZW5ndGg9MSx0aGlzKTpnKGUpP3ZvaWQgMCE9PW4ucmVhZHk/bi5yZWFkeShlKTplKHcpOncubWFrZUFycmF5KGUsdGhpcyl9KS5wcm90b3R5cGU9dy5mbixxPXcocik7dmFyIEg9L14oPzpwYXJlbnRzfHByZXYoPzpVbnRpbHxBbGwpKS8sTz17Y2hpbGRyZW46ITAsY29udGVudHM6ITAsbmV4dDohMCxwcmV2OiEwfTt3LmZuLmV4dGVuZCh7aGFzOmZ1bmN0aW9uKGUpe3ZhciB0PXcoZSx0aGlzKSxuPXQubGVuZ3RoO3JldHVybiB0aGlzLmZpbHRlcihmdW5jdGlvbigpe2Zvcih2YXIgZT0wO2U8bjtlKyspaWYody5jb250YWlucyh0aGlzLHRbZV0pKXJldHVybiEwfSl9LGNsb3Nlc3Q6ZnVuY3Rpb24oZSx0KXt2YXIgbixyPTAsaT10aGlzLmxlbmd0aCxvPVtdLGE9InN0cmluZyIhPXR5cGVvZiBlJiZ3KGUpO2lmKCFELnRlc3QoZSkpZm9yKDtyPGk7cisrKWZvcihuPXRoaXNbcl07biYmbiE9PXQ7bj1uLnBhcmVudE5vZGUpaWYobi5ub2RlVHlwZTwxMSYmKGE/YS5pbmRleChuKT4tMToxPT09bi5ub2RlVHlwZSYmdy5maW5kLm1hdGNoZXNTZWxlY3RvcihuLGUpKSl7by5wdXNoKG4pO2JyZWFrfXJldHVybiB0aGlzLnB1c2hTdGFjayhvLmxlbmd0aD4xP3cudW5pcXVlU29ydChvKTpvKX0saW5kZXg6ZnVuY3Rpb24oZSl7cmV0dXJuIGU/InN0cmluZyI9PXR5cGVvZiBlP3UuY2FsbCh3KGUpLHRoaXNbMF0pOnUuY2FsbCh0aGlzLGUuanF1ZXJ5P2VbMF06ZSk6dGhpc1swXSYmdGhpc1swXS5wYXJlbnROb2RlP3RoaXMuZmlyc3QoKS5wcmV2QWxsKCkubGVuZ3RoOi0xfSxhZGQ6ZnVuY3Rpb24oZSx0KXtyZXR1cm4gdGhpcy5wdXNoU3RhY2sody51bmlxdWVTb3J0KHcubWVyZ2UodGhpcy5nZXQoKSx3KGUsdCkpKSl9LGFkZEJhY2s6ZnVuY3Rpb24oZSl7cmV0dXJuIHRoaXMuYWRkKG51bGw9PWU/dGhpcy5wcmV2T2JqZWN0OnRoaXMucHJldk9iamVjdC5maWx0ZXIoZSkpfX0pO2Z1bmN0aW9uIFAoZSx0KXt3aGlsZSgoZT1lW3RdKSYmMSE9PWUubm9kZVR5cGUpO3JldHVybiBlfXcuZWFjaCh7cGFyZW50OmZ1bmN0aW9uKGUpe3ZhciB0PWUucGFyZW50Tm9kZTtyZXR1cm4gdCYmMTEhPT10Lm5vZGVUeXBlP3Q6bnVsbH0scGFyZW50czpmdW5jdGlvbihlKXtyZXR1cm4gayhlLCJwYXJlbnROb2RlIil9LHBhcmVudHNVbnRpbDpmdW5jdGlvbihlLHQsbil7cmV0dXJuIGsoZSwicGFyZW50Tm9kZSIsbil9LG5leHQ6ZnVuY3Rpb24oZSl7cmV0dXJuIFAoZSwibmV4dFNpYmxpbmciKX0scHJldjpmdW5jdGlvbihlKXtyZXR1cm4gUChlLCJwcmV2aW91c1NpYmxpbmciKX0sbmV4dEFsbDpmdW5jdGlvbihlKXtyZXR1cm4gayhlLCJuZXh0U2libGluZyIpfSxwcmV2QWxsOmZ1bmN0aW9uKGUpe3JldHVybiBrKGUsInByZXZpb3VzU2libGluZyIpfSxuZXh0VW50aWw6ZnVuY3Rpb24oZSx0LG4pe3JldHVybiBrKGUsIm5leHRTaWJsaW5nIixuKX0scHJldlVudGlsOmZ1bmN0aW9uKGUsdCxuKXtyZXR1cm4gayhlLCJwcmV2aW91c1NpYmxpbmciLG4pfSxzaWJsaW5nczpmdW5jdGlvbihlKXtyZXR1cm4gUygoZS5wYXJlbnROb2RlfHx7fSkuZmlyc3RDaGlsZCxlKX0sY2hpbGRyZW46ZnVuY3Rpb24oZSl7cmV0dXJuIFMoZS5maXJzdENoaWxkKX0sY29udGVudHM6ZnVuY3Rpb24oZSl7cmV0dXJuIE4oZSwiaWZyYW1lIik/ZS5jb250ZW50RG9jdW1lbnQ6KE4oZSwidGVtcGxhdGUiKSYmKGU9ZS5jb250ZW50fHxlKSx3Lm1lcmdlKFtdLGUuY2hpbGROb2RlcykpfX0sZnVuY3Rpb24oZSx0KXt3LmZuW2VdPWZ1bmN0aW9uKG4scil7dmFyIGk9dy5tYXAodGhpcyx0LG4pO3JldHVybiJVbnRpbCIhPT1lLnNsaWNlKC01KSYmKHI9biksciYmInN0cmluZyI9PXR5cGVvZiByJiYoaT13LmZpbHRlcihyLGkpKSx0aGlzLmxlbmd0aD4xJiYoT1tlXXx8dy51bmlxdWVTb3J0KGkpLEgudGVzdChlKSYmaS5yZXZlcnNlKCkpLHRoaXMucHVzaFN0YWNrKGkpfX0pO3ZhciBNPS9bXlx4MjBcdFxyXG5cZl0rL2c7ZnVuY3Rpb24gUihlKXt2YXIgdD17fTtyZXR1cm4gdy5lYWNoKGUubWF0Y2goTSl8fFtdLGZ1bmN0aW9uKGUsbil7dFtuXT0hMH0pLHR9dy5DYWxsYmFja3M9ZnVuY3Rpb24oZSl7ZT0ic3RyaW5nIj09dHlwZW9mIGU/UihlKTp3LmV4dGVuZCh7fSxlKTt2YXIgdCxuLHIsaSxvPVtdLGE9W10scz0tMSx1PWZ1bmN0aW9uKCl7Zm9yKGk9aXx8ZS5vbmNlLHI9dD0hMDthLmxlbmd0aDtzPS0xKXtuPWEuc2hpZnQoKTt3aGlsZSgrK3M8by5sZW5ndGgpITE9PT1vW3NdLmFwcGx5KG5bMF0sblsxXSkmJmUuc3RvcE9uRmFsc2UmJihzPW8ubGVuZ3RoLG49ITEpfWUubWVtb3J5fHwobj0hMSksdD0hMSxpJiYobz1uP1tdOiIiKX0sbD17YWRkOmZ1bmN0aW9uKCl7cmV0dXJuIG8mJihuJiYhdCYmKHM9by5sZW5ndGgtMSxhLnB1c2gobikpLGZ1bmN0aW9uIHQobil7dy5lYWNoKG4sZnVuY3Rpb24obixyKXtnKHIpP2UudW5pcXVlJiZsLmhhcyhyKXx8by5wdXNoKHIpOnImJnIubGVuZ3RoJiYic3RyaW5nIiE9PXgocikmJnQocil9KX0oYXJndW1lbnRzKSxuJiYhdCYmdSgpKSx0aGlzfSxyZW1vdmU6ZnVuY3Rpb24oKXtyZXR1cm4gdy5lYWNoKGFyZ3VtZW50cyxmdW5jdGlvbihlLHQpe3ZhciBuO3doaWxlKChuPXcuaW5BcnJheSh0LG8sbikpPi0xKW8uc3BsaWNlKG4sMSksbjw9cyYmcy0tfSksdGhpc30saGFzOmZ1bmN0aW9uKGUpe3JldHVybiBlP3cuaW5BcnJheShlLG8pPi0xOm8ubGVuZ3RoPjB9LGVtcHR5OmZ1bmN0aW9uKCl7cmV0dXJuIG8mJihvPVtdKSx0aGlzfSxkaXNhYmxlOmZ1bmN0aW9uKCl7cmV0dXJuIGk9YT1bXSxvPW49IiIsdGhpc30sZGlzYWJsZWQ6ZnVuY3Rpb24oKXtyZXR1cm4hb30sbG9jazpmdW5jdGlvbigpe3JldHVybiBpPWE9W10sbnx8dHx8KG89bj0iIiksdGhpc30sbG9ja2VkOmZ1bmN0aW9uKCl7cmV0dXJuISFpfSxmaXJlV2l0aDpmdW5jdGlvbihlLG4pe3JldHVybiBpfHwobj1bZSwobj1ufHxbXSkuc2xpY2U/bi5zbGljZSgpOm5dLGEucHVzaChuKSx0fHx1KCkpLHRoaXN9LGZpcmU6ZnVuY3Rpb24oKXtyZXR1cm4gbC5maXJlV2l0aCh0aGlzLGFyZ3VtZW50cyksdGhpc30sZmlyZWQ6ZnVuY3Rpb24oKXtyZXR1cm4hIXJ9fTtyZXR1cm4gbH07ZnVuY3Rpb24gSShlKXtyZXR1cm4gZX1mdW5jdGlvbiBXKGUpe3Rocm93IGV9ZnVuY3Rpb24gJChlLHQsbixyKXt2YXIgaTt0cnl7ZSYmZyhpPWUucHJvbWlzZSk/aS5jYWxsKGUpLmRvbmUodCkuZmFpbChuKTplJiZnKGk9ZS50aGVuKT9pLmNhbGwoZSx0LG4pOnQuYXBwbHkodm9pZCAwLFtlXS5zbGljZShyKSl9Y2F0Y2goZSl7bi5hcHBseSh2b2lkIDAsW2VdKX19dy5leHRlbmQoe0RlZmVycmVkOmZ1bmN0aW9uKHQpe3ZhciBuPVtbIm5vdGlmeSIsInByb2dyZXNzIix3LkNhbGxiYWNrcygibWVtb3J5Iiksdy5DYWxsYmFja3MoIm1lbW9yeSIpLDJdLFsicmVzb2x2ZSIsImRvbmUiLHcuQ2FsbGJhY2tzKCJvbmNlIG1lbW9yeSIpLHcuQ2FsbGJhY2tzKCJvbmNlIG1lbW9yeSIpLDAsInJlc29sdmVkIl0sWyJyZWplY3QiLCJmYWlsIix3LkNhbGxiYWNrcygib25jZSBtZW1vcnkiKSx3LkNhbGxiYWNrcygib25jZSBtZW1vcnkiKSwxLCJyZWplY3RlZCJdXSxyPSJwZW5kaW5nIixpPXtzdGF0ZTpmdW5jdGlvbigpe3JldHVybiByfSxhbHdheXM6ZnVuY3Rpb24oKXtyZXR1cm4gby5kb25lKGFyZ3VtZW50cykuZmFpbChhcmd1bWVudHMpLHRoaXN9LCJjYXRjaCI6ZnVuY3Rpb24oZSl7cmV0dXJuIGkudGhlbihudWxsLGUpfSxwaXBlOmZ1bmN0aW9uKCl7dmFyIGU9YXJndW1lbnRzO3JldHVybiB3LkRlZmVycmVkKGZ1bmN0aW9uKHQpe3cuZWFjaChuLGZ1bmN0aW9uKG4scil7dmFyIGk9ZyhlW3JbNF1dKSYmZVtyWzRdXTtvW3JbMV1dKGZ1bmN0aW9uKCl7dmFyIGU9aSYmaS5hcHBseSh0aGlzLGFyZ3VtZW50cyk7ZSYmZyhlLnByb21pc2UpP2UucHJvbWlzZSgpLnByb2dyZXNzKHQubm90aWZ5KS5kb25lKHQucmVzb2x2ZSkuZmFpbCh0LnJlamVjdCk6dFtyWzBdKyJXaXRoIl0odGhpcyxpP1tlXTphcmd1bWVudHMpfSl9KSxlPW51bGx9KS5wcm9taXNlKCl9LHRoZW46ZnVuY3Rpb24odCxyLGkpe3ZhciBvPTA7ZnVuY3Rpb24gYSh0LG4scixpKXtyZXR1cm4gZnVuY3Rpb24oKXt2YXIgcz10aGlzLHU9YXJndW1lbnRzLGw9ZnVuY3Rpb24oKXt2YXIgZSxsO2lmKCEodDxvKSl7aWYoKGU9ci5hcHBseShzLHUpKT09PW4ucHJvbWlzZSgpKXRocm93IG5ldyBUeXBlRXJyb3IoIlRoZW5hYmxlIHNlbGYtcmVzb2x1dGlvbiIpO2w9ZSYmKCJvYmplY3QiPT10eXBlb2YgZXx8ImZ1bmN0aW9uIj09dHlwZW9mIGUpJiZlLnRoZW4sZyhsKT9pP2wuY2FsbChlLGEobyxuLEksaSksYShvLG4sVyxpKSk6KG8rKyxsLmNhbGwoZSxhKG8sbixJLGkpLGEobyxuLFcsaSksYShvLG4sSSxuLm5vdGlmeVdpdGgpKSk6KHIhPT1JJiYocz12b2lkIDAsdT1bZV0pLChpfHxuLnJlc29sdmVXaXRoKShzLHUpKX19LGM9aT9sOmZ1bmN0aW9uKCl7dHJ5e2woKX1jYXRjaChlKXt3LkRlZmVycmVkLmV4Y2VwdGlvbkhvb2smJncuRGVmZXJyZWQuZXhjZXB0aW9uSG9vayhlLGMuc3RhY2tUcmFjZSksdCsxPj1vJiYociE9PVcmJihzPXZvaWQgMCx1PVtlXSksbi5yZWplY3RXaXRoKHMsdSkpfX07dD9jKCk6KHcuRGVmZXJyZWQuZ2V0U3RhY2tIb29rJiYoYy5zdGFja1RyYWNlPXcuRGVmZXJyZWQuZ2V0U3RhY2tIb29rKCkpLGUuc2V0VGltZW91dChjKSl9fXJldHVybiB3LkRlZmVycmVkKGZ1bmN0aW9uKGUpe25bMF1bM10uYWRkKGEoMCxlLGcoaSk/aTpJLGUubm90aWZ5V2l0aCkpLG5bMV1bM10uYWRkKGEoMCxlLGcodCk/dDpJKSksblsyXVszXS5hZGQoYSgwLGUsZyhyKT9yOlcpKX0pLnByb21pc2UoKX0scHJvbWlzZTpmdW5jdGlvbihlKXtyZXR1cm4gbnVsbCE9ZT93LmV4dGVuZChlLGkpOml9fSxvPXt9O3JldHVybiB3LmVhY2gobixmdW5jdGlvbihlLHQpe3ZhciBhPXRbMl0scz10WzVdO2lbdFsxXV09YS5hZGQscyYmYS5hZGQoZnVuY3Rpb24oKXtyPXN9LG5bMy1lXVsyXS5kaXNhYmxlLG5bMy1lXVszXS5kaXNhYmxlLG5bMF1bMl0ubG9jayxuWzBdWzNdLmxvY2spLGEuYWRkKHRbM10uZmlyZSksb1t0WzBdXT1mdW5jdGlvbigpe3JldHVybiBvW3RbMF0rIldpdGgiXSh0aGlzPT09bz92b2lkIDA6dGhpcyxhcmd1bWVudHMpLHRoaXN9LG9bdFswXSsiV2l0aCJdPWEuZmlyZVdpdGh9KSxpLnByb21pc2UobyksdCYmdC5jYWxsKG8sbyksb30sd2hlbjpmdW5jdGlvbihlKXt2YXIgdD1hcmd1bWVudHMubGVuZ3RoLG49dCxyPUFycmF5KG4pLGk9by5jYWxsKGFyZ3VtZW50cyksYT13LkRlZmVycmVkKCkscz1mdW5jdGlvbihlKXtyZXR1cm4gZnVuY3Rpb24obil7cltlXT10aGlzLGlbZV09YXJndW1lbnRzLmxlbmd0aD4xP28uY2FsbChhcmd1bWVudHMpOm4sLS10fHxhLnJlc29sdmVXaXRoKHIsaSl9fTtpZih0PD0xJiYoJChlLGEuZG9uZShzKG4pKS5yZXNvbHZlLGEucmVqZWN0LCF0KSwicGVuZGluZyI9PT1hLnN0YXRlKCl8fGcoaVtuXSYmaVtuXS50aGVuKSkpcmV0dXJuIGEudGhlbigpO3doaWxlKG4tLSkkKGlbbl0scyhuKSxhLnJlamVjdCk7cmV0dXJuIGEucHJvbWlzZSgpfX0pO3ZhciBCPS9eKEV2YWx8SW50ZXJuYWx8UmFuZ2V8UmVmZXJlbmNlfFN5bnRheHxUeXBlfFVSSSlFcnJvciQvO3cuRGVmZXJyZWQuZXhjZXB0aW9uSG9vaz1mdW5jdGlvbih0LG4pe2UuY29uc29sZSYmZS5jb25zb2xlLndhcm4mJnQmJkIudGVzdCh0Lm5hbWUpJiZlLmNvbnNvbGUud2FybigialF1ZXJ5LkRlZmVycmVkIGV4Y2VwdGlvbjogIit0Lm1lc3NhZ2UsdC5zdGFjayxuKX0sdy5yZWFkeUV4Y2VwdGlvbj1mdW5jdGlvbih0KXtlLnNldFRpbWVvdXQoZnVuY3Rpb24oKXt0aHJvdyB0fSl9O3ZhciBGPXcuRGVmZXJyZWQoKTt3LmZuLnJlYWR5PWZ1bmN0aW9uKGUpe3JldHVybiBGLnRoZW4oZSlbImNhdGNoIl0oZnVuY3Rpb24oZSl7dy5yZWFkeUV4Y2VwdGlvbihlKX0pLHRoaXN9LHcuZXh0ZW5kKHtpc1JlYWR5OiExLHJlYWR5V2FpdDoxLHJlYWR5OmZ1bmN0aW9uKGUpeyghMD09PWU/LS13LnJlYWR5V2FpdDp3LmlzUmVhZHkpfHwody5pc1JlYWR5PSEwLCEwIT09ZSYmLS13LnJlYWR5V2FpdD4wfHxGLnJlc29sdmVXaXRoKHIsW3ddKSl9fSksdy5yZWFkeS50aGVuPUYudGhlbjtmdW5jdGlvbiBfKCl7ci5yZW1vdmVFdmVudExpc3RlbmVyKCJET01Db250ZW50TG9hZGVkIixfKSxlLnJlbW92ZUV2ZW50TGlzdGVuZXIoImxvYWQiLF8pLHcucmVhZHkoKX0iY29tcGxldGUiPT09ci5yZWFkeVN0YXRlfHwibG9hZGluZyIhPT1yLnJlYWR5U3RhdGUmJiFyLmRvY3VtZW50RWxlbWVudC5kb1Njcm9sbD9lLnNldFRpbWVvdXQody5yZWFkeSk6KHIuYWRkRXZlbnRMaXN0ZW5lcigiRE9NQ29udGVudExvYWRlZCIsXyksZS5hZGRFdmVudExpc3RlbmVyKCJsb2FkIixfKSk7dmFyIHo9ZnVuY3Rpb24oZSx0LG4scixpLG8sYSl7dmFyIHM9MCx1PWUubGVuZ3RoLGw9bnVsbD09bjtpZigib2JqZWN0Ij09PXgobikpe2k9ITA7Zm9yKHMgaW4gbil6KGUsdCxzLG5bc10sITAsbyxhKX1lbHNlIGlmKHZvaWQgMCE9PXImJihpPSEwLGcocil8fChhPSEwKSxsJiYoYT8odC5jYWxsKGUsciksdD1udWxsKToobD10LHQ9ZnVuY3Rpb24oZSx0LG4pe3JldHVybiBsLmNhbGwodyhlKSxuKX0pKSx0KSlmb3IoO3M8dTtzKyspdChlW3NdLG4sYT9yOnIuY2FsbChlW3NdLHMsdChlW3NdLG4pKSk7cmV0dXJuIGk/ZTpsP3QuY2FsbChlKTp1P3QoZVswXSxuKTpvfSxYPS9eLW1zLS8sVT0vLShbYS16XSkvZztmdW5jdGlvbiBWKGUsdCl7cmV0dXJuIHQudG9VcHBlckNhc2UoKX1mdW5jdGlvbiBHKGUpe3JldHVybiBlLnJlcGxhY2UoWCwibXMtIikucmVwbGFjZShVLFYpfXZhciBZPWZ1bmN0aW9uKGUpe3JldHVybiAxPT09ZS5ub2RlVHlwZXx8OT09PWUubm9kZVR5cGV8fCErZS5ub2RlVHlwZX07ZnVuY3Rpb24gUSgpe3RoaXMuZXhwYW5kbz13LmV4cGFuZG8rUS51aWQrK31RLnVpZD0xLFEucHJvdG90eXBlPXtjYWNoZTpmdW5jdGlvbihlKXt2YXIgdD1lW3RoaXMuZXhwYW5kb107cmV0dXJuIHR8fCh0PXt9LFkoZSkmJihlLm5vZGVUeXBlP2VbdGhpcy5leHBhbmRvXT10Ok9iamVjdC5kZWZpbmVQcm9wZXJ0eShlLHRoaXMuZXhwYW5kbyx7dmFsdWU6dCxjb25maWd1cmFibGU6ITB9KSkpLHR9LHNldDpmdW5jdGlvbihlLHQsbil7dmFyIHIsaT10aGlzLmNhY2hlKGUpO2lmKCJzdHJpbmciPT10eXBlb2YgdClpW0codCldPW47ZWxzZSBmb3IociBpbiB0KWlbRyhyKV09dFtyXTtyZXR1cm4gaX0sZ2V0OmZ1bmN0aW9uKGUsdCl7cmV0dXJuIHZvaWQgMD09PXQ/dGhpcy5jYWNoZShlKTplW3RoaXMuZXhwYW5kb10mJmVbdGhpcy5leHBhbmRvXVtHKHQpXX0sYWNjZXNzOmZ1bmN0aW9uKGUsdCxuKXtyZXR1cm4gdm9pZCAwPT09dHx8dCYmInN0cmluZyI9PXR5cGVvZiB0JiZ2b2lkIDA9PT1uP3RoaXMuZ2V0KGUsdCk6KHRoaXMuc2V0KGUsdCxuKSx2b2lkIDAhPT1uP246dCl9LHJlbW92ZTpmdW5jdGlvbihlLHQpe3ZhciBuLHI9ZVt0aGlzLmV4cGFuZG9dO2lmKHZvaWQgMCE9PXIpe2lmKHZvaWQgMCE9PXQpe249KHQ9QXJyYXkuaXNBcnJheSh0KT90Lm1hcChHKToodD1HKHQpKWluIHI/W3RdOnQubWF0Y2goTSl8fFtdKS5sZW5ndGg7d2hpbGUobi0tKWRlbGV0ZSByW3Rbbl1dfSh2b2lkIDA9PT10fHx3LmlzRW1wdHlPYmplY3QocikpJiYoZS5ub2RlVHlwZT9lW3RoaXMuZXhwYW5kb109dm9pZCAwOmRlbGV0ZSBlW3RoaXMuZXhwYW5kb10pfX0saGFzRGF0YTpmdW5jdGlvbihlKXt2YXIgdD1lW3RoaXMuZXhwYW5kb107cmV0dXJuIHZvaWQgMCE9PXQmJiF3LmlzRW1wdHlPYmplY3QodCl9fTt2YXIgSj1uZXcgUSxLPW5ldyBRLFo9L14oPzpce1tcd1xXXSpcfXxcW1tcd1xXXSpcXSkkLyxlZT0vW0EtWl0vZztmdW5jdGlvbiB0ZShlKXtyZXR1cm4idHJ1ZSI9PT1lfHwiZmFsc2UiIT09ZSYmKCJudWxsIj09PWU/bnVsbDplPT09K2UrIiI/K2U6Wi50ZXN0KGUpP0pTT04ucGFyc2UoZSk6ZSl9ZnVuY3Rpb24gbmUoZSx0LG4pe3ZhciByO2lmKHZvaWQgMD09PW4mJjE9PT1lLm5vZGVUeXBlKWlmKHI9ImRhdGEtIit0LnJlcGxhY2UoZWUsIi0kJiIpLnRvTG93ZXJDYXNlKCksInN0cmluZyI9PXR5cGVvZihuPWUuZ2V0QXR0cmlidXRlKHIpKSl7dHJ5e249dGUobil9Y2F0Y2goZSl7fUsuc2V0KGUsdCxuKX1lbHNlIG49dm9pZCAwO3JldHVybiBufXcuZXh0ZW5kKHtoYXNEYXRhOmZ1bmN0aW9uKGUpe3JldHVybiBLLmhhc0RhdGEoZSl8fEouaGFzRGF0YShlKX0sZGF0YTpmdW5jdGlvbihlLHQsbil7cmV0dXJuIEsuYWNjZXNzKGUsdCxuKX0scmVtb3ZlRGF0YTpmdW5jdGlvbihlLHQpe0sucmVtb3ZlKGUsdCl9LF9kYXRhOmZ1bmN0aW9uKGUsdCxuKXtyZXR1cm4gSi5hY2Nlc3MoZSx0LG4pfSxfcmVtb3ZlRGF0YTpmdW5jdGlvbihlLHQpe0oucmVtb3ZlKGUsdCl9fSksdy5mbi5leHRlbmQoe2RhdGE6ZnVuY3Rpb24oZSx0KXt2YXIgbixyLGksbz10aGlzWzBdLGE9byYmby5hdHRyaWJ1dGVzO2lmKHZvaWQgMD09PWUpe2lmKHRoaXMubGVuZ3RoJiYoaT1LLmdldChvKSwxPT09by5ub2RlVHlwZSYmIUouZ2V0KG8sImhhc0RhdGFBdHRycyIpKSl7bj1hLmxlbmd0aDt3aGlsZShuLS0pYVtuXSYmMD09PShyPWFbbl0ubmFtZSkuaW5kZXhPZigiZGF0YS0iKSYmKHI9RyhyLnNsaWNlKDUpKSxuZShvLHIsaVtyXSkpO0ouc2V0KG8sImhhc0RhdGFBdHRycyIsITApfXJldHVybiBpfXJldHVybiJvYmplY3QiPT10eXBlb2YgZT90aGlzLmVhY2goZnVuY3Rpb24oKXtLLnNldCh0aGlzLGUpfSk6eih0aGlzLGZ1bmN0aW9uKHQpe3ZhciBuO2lmKG8mJnZvaWQgMD09PXQpe2lmKHZvaWQgMCE9PShuPUsuZ2V0KG8sZSkpKXJldHVybiBuO2lmKHZvaWQgMCE9PShuPW5lKG8sZSkpKXJldHVybiBufWVsc2UgdGhpcy5lYWNoKGZ1bmN0aW9uKCl7Sy5zZXQodGhpcyxlLHQpfSl9LG51bGwsdCxhcmd1bWVudHMubGVuZ3RoPjEsbnVsbCwhMCl9LHJlbW92ZURhdGE6ZnVuY3Rpb24oZSl7cmV0dXJuIHRoaXMuZWFjaChmdW5jdGlvbigpe0sucmVtb3ZlKHRoaXMsZSl9KX19KSx3LmV4dGVuZCh7cXVldWU6ZnVuY3Rpb24oZSx0LG4pe3ZhciByO2lmKGUpcmV0dXJuIHQ9KHR8fCJmeCIpKyJxdWV1ZSIscj1KLmdldChlLHQpLG4mJighcnx8QXJyYXkuaXNBcnJheShuKT9yPUouYWNjZXNzKGUsdCx3Lm1ha2VBcnJheShuKSk6ci5wdXNoKG4pKSxyfHxbXX0sZGVxdWV1ZTpmdW5jdGlvbihlLHQpe3Q9dHx8ImZ4Ijt2YXIgbj13LnF1ZXVlKGUsdCkscj1uLmxlbmd0aCxpPW4uc2hpZnQoKSxvPXcuX3F1ZXVlSG9va3MoZSx0KSxhPWZ1bmN0aW9uKCl7dy5kZXF1ZXVlKGUsdCl9OyJpbnByb2dyZXNzIj09PWkmJihpPW4uc2hpZnQoKSxyLS0pLGkmJigiZngiPT09dCYmbi51bnNoaWZ0KCJpbnByb2dyZXNzIiksZGVsZXRlIG8uc3RvcCxpLmNhbGwoZSxhLG8pKSwhciYmbyYmby5lbXB0eS5maXJlKCl9LF9xdWV1ZUhvb2tzOmZ1bmN0aW9uKGUsdCl7dmFyIG49dCsicXVldWVIb29rcyI7cmV0dXJuIEouZ2V0KGUsbil8fEouYWNjZXNzKGUsbix7ZW1wdHk6dy5DYWxsYmFja3MoIm9uY2UgbWVtb3J5IikuYWRkKGZ1bmN0aW9uKCl7Si5yZW1vdmUoZSxbdCsicXVldWUiLG5dKX0pfSl9fSksdy5mbi5leHRlbmQoe3F1ZXVlOmZ1bmN0aW9uKGUsdCl7dmFyIG49MjtyZXR1cm4ic3RyaW5nIiE9dHlwZW9mIGUmJih0PWUsZT0iZngiLG4tLSksYXJndW1lbnRzLmxlbmd0aDxuP3cucXVldWUodGhpc1swXSxlKTp2b2lkIDA9PT10P3RoaXM6dGhpcy5lYWNoKGZ1bmN0aW9uKCl7dmFyIG49dy5xdWV1ZSh0aGlzLGUsdCk7dy5fcXVldWVIb29rcyh0aGlzLGUpLCJmeCI9PT1lJiYiaW5wcm9ncmVzcyIhPT1uWzBdJiZ3LmRlcXVldWUodGhpcyxlKX0pfSxkZXF1ZXVlOmZ1bmN0aW9uKGUpe3JldHVybiB0aGlzLmVhY2goZnVuY3Rpb24oKXt3LmRlcXVldWUodGhpcyxlKX0pfSxjbGVhclF1ZXVlOmZ1bmN0aW9uKGUpe3JldHVybiB0aGlzLnF1ZXVlKGV8fCJmeCIsW10pfSxwcm9taXNlOmZ1bmN0aW9uKGUsdCl7dmFyIG4scj0xLGk9dy5EZWZlcnJlZCgpLG89dGhpcyxhPXRoaXMubGVuZ3RoLHM9ZnVuY3Rpb24oKXstLXJ8fGkucmVzb2x2ZVdpdGgobyxbb10pfTsic3RyaW5nIiE9dHlwZW9mIGUmJih0PWUsZT12b2lkIDApLGU9ZXx8ImZ4Ijt3aGlsZShhLS0pKG49Si5nZXQob1thXSxlKyJxdWV1ZUhvb2tzIikpJiZuLmVtcHR5JiYocisrLG4uZW1wdHkuYWRkKHMpKTtyZXR1cm4gcygpLGkucHJvbWlzZSh0KX19KTt2YXIgcmU9L1srLV0/KD86XGQqXC58KVxkKyg/OltlRV1bKy1dP1xkK3wpLy5zb3VyY2UsaWU9bmV3IFJlZ0V4cCgiXig/OihbKy1dKT18KSgiK3JlKyIpKFthLXolXSopJCIsImkiKSxvZT1bIlRvcCIsIlJpZ2h0IiwiQm90dG9tIiwiTGVmdCJdLGFlPWZ1bmN0aW9uKGUsdCl7cmV0dXJuIm5vbmUiPT09KGU9dHx8ZSkuc3R5bGUuZGlzcGxheXx8IiI9PT1lLnN0eWxlLmRpc3BsYXkmJncuY29udGFpbnMoZS5vd25lckRvY3VtZW50LGUpJiYibm9uZSI9PT13LmNzcyhlLCJkaXNwbGF5Iil9LHNlPWZ1bmN0aW9uKGUsdCxuLHIpe3ZhciBpLG8sYT17fTtmb3IobyBpbiB0KWFbb109ZS5zdHlsZVtvXSxlLnN0eWxlW29dPXRbb107aT1uLmFwcGx5KGUscnx8W10pO2ZvcihvIGluIHQpZS5zdHlsZVtvXT1hW29dO3JldHVybiBpfTtmdW5jdGlvbiB1ZShlLHQsbixyKXt2YXIgaSxvLGE9MjAscz1yP2Z1bmN0aW9uKCl7cmV0dXJuIHIuY3VyKCl9OmZ1bmN0aW9uKCl7cmV0dXJuIHcuY3NzKGUsdCwiIil9LHU9cygpLGw9biYmblszXXx8KHcuY3NzTnVtYmVyW3RdPyIiOiJweCIpLGM9KHcuY3NzTnVtYmVyW3RdfHwicHgiIT09bCYmK3UpJiZpZS5leGVjKHcuY3NzKGUsdCkpO2lmKGMmJmNbM10hPT1sKXt1Lz0yLGw9bHx8Y1szXSxjPSt1fHwxO3doaWxlKGEtLSl3LnN0eWxlKGUsdCxjK2wpLCgxLW8pKigxLShvPXMoKS91fHwuNSkpPD0wJiYoYT0wKSxjLz1vO2MqPTIsdy5zdHlsZShlLHQsYytsKSxuPW58fFtdfXJldHVybiBuJiYoYz0rY3x8K3V8fDAsaT1uWzFdP2MrKG5bMV0rMSkqblsyXTorblsyXSxyJiYoci51bml0PWwsci5zdGFydD1jLHIuZW5kPWkpKSxpfXZhciBsZT17fTtmdW5jdGlvbiBjZShlKXt2YXIgdCxuPWUub3duZXJEb2N1bWVudCxyPWUubm9kZU5hbWUsaT1sZVtyXTtyZXR1cm4gaXx8KHQ9bi5ib2R5LmFwcGVuZENoaWxkKG4uY3JlYXRlRWxlbWVudChyKSksaT13LmNzcyh0LCJkaXNwbGF5IiksdC5wYXJlbnROb2RlLnJlbW92ZUNoaWxkKHQpLCJub25lIj09PWkmJihpPSJibG9jayIpLGxlW3JdPWksaSl9ZnVuY3Rpb24gZmUoZSx0KXtmb3IodmFyIG4scixpPVtdLG89MCxhPWUubGVuZ3RoO288YTtvKyspKHI9ZVtvXSkuc3R5bGUmJihuPXIuc3R5bGUuZGlzcGxheSx0Pygibm9uZSI9PT1uJiYoaVtvXT1KLmdldChyLCJkaXNwbGF5Iil8fG51bGwsaVtvXXx8KHIuc3R5bGUuZGlzcGxheT0iIikpLCIiPT09ci5zdHlsZS5kaXNwbGF5JiZhZShyKSYmKGlbb109Y2UocikpKToibm9uZSIhPT1uJiYoaVtvXT0ibm9uZSIsSi5zZXQociwiZGlzcGxheSIsbikpKTtmb3Iobz0wO288YTtvKyspbnVsbCE9aVtvXSYmKGVbb10uc3R5bGUuZGlzcGxheT1pW29dKTtyZXR1cm4gZX13LmZuLmV4dGVuZCh7c2hvdzpmdW5jdGlvbigpe3JldHVybiBmZSh0aGlzLCEwKX0saGlkZTpmdW5jdGlvbigpe3JldHVybiBmZSh0aGlzKX0sdG9nZ2xlOmZ1bmN0aW9uKGUpe3JldHVybiJib29sZWFuIj09dHlwZW9mIGU/ZT90aGlzLnNob3coKTp0aGlzLmhpZGUoKTp0aGlzLmVhY2goZnVuY3Rpb24oKXthZSh0aGlzKT93KHRoaXMpLnNob3coKTp3KHRoaXMpLmhpZGUoKX0pfX0pO3ZhciBwZT0vXig/OmNoZWNrYm94fHJhZGlvKSQvaSxkZT0vPChbYS16XVteXC9cMD5ceDIwXHRcclxuXGZdKykvaSxoZT0vXiR8Xm1vZHVsZSR8XC8oPzpqYXZhfGVjbWEpc2NyaXB0L2ksZ2U9e29wdGlvbjpbMSwiPHNlbGVjdCBtdWx0aXBsZT0nbXVsdGlwbGUnPiIsIjwvc2VsZWN0PiJdLHRoZWFkOlsxLCI8dGFibGU+IiwiPC90YWJsZT4iXSxjb2w6WzIsIjx0YWJsZT48Y29sZ3JvdXA+IiwiPC9jb2xncm91cD48L3RhYmxlPiJdLHRyOlsyLCI8dGFibGU+PHRib2R5PiIsIjwvdGJvZHk+PC90YWJsZT4iXSx0ZDpbMywiPHRhYmxlPjx0Ym9keT48dHI+IiwiPC90cj48L3Rib2R5PjwvdGFibGU+Il0sX2RlZmF1bHQ6WzAsIiIsIiJdfTtnZS5vcHRncm91cD1nZS5vcHRpb24sZ2UudGJvZHk9Z2UudGZvb3Q9Z2UuY29sZ3JvdXA9Z2UuY2FwdGlvbj1nZS50aGVhZCxnZS50aD1nZS50ZDtmdW5jdGlvbiB5ZShlLHQpe3ZhciBuO3JldHVybiBuPSJ1bmRlZmluZWQiIT10eXBlb2YgZS5nZXRFbGVtZW50c0J5VGFnTmFtZT9lLmdldEVsZW1lbnRzQnlUYWdOYW1lKHR8fCIqIik6InVuZGVmaW5lZCIhPXR5cGVvZiBlLnF1ZXJ5U2VsZWN0b3JBbGw/ZS5xdWVyeVNlbGVjdG9yQWxsKHR8fCIqIik6W10sdm9pZCAwPT09dHx8dCYmTihlLHQpP3cubWVyZ2UoW2VdLG4pOm59ZnVuY3Rpb24gdmUoZSx0KXtmb3IodmFyIG49MCxyPWUubGVuZ3RoO248cjtuKyspSi5zZXQoZVtuXSwiZ2xvYmFsRXZhbCIsIXR8fEouZ2V0KHRbbl0sImdsb2JhbEV2YWwiKSl9dmFyIG1lPS88fCYjP1x3KzsvO2Z1bmN0aW9uIHhlKGUsdCxuLHIsaSl7Zm9yKHZhciBvLGEscyx1LGwsYyxmPXQuY3JlYXRlRG9jdW1lbnRGcmFnbWVudCgpLHA9W10sZD0wLGg9ZS5sZW5ndGg7ZDxoO2QrKylpZigobz1lW2RdKXx8MD09PW8paWYoIm9iamVjdCI9PT14KG8pKXcubWVyZ2UocCxvLm5vZGVUeXBlP1tvXTpvKTtlbHNlIGlmKG1lLnRlc3Qobykpe2E9YXx8Zi5hcHBlbmRDaGlsZCh0LmNyZWF0ZUVsZW1lbnQoImRpdiIpKSxzPShkZS5leGVjKG8pfHxbIiIsIiJdKVsxXS50b0xvd2VyQ2FzZSgpLHU9Z2Vbc118fGdlLl9kZWZhdWx0LGEuaW5uZXJIVE1MPXVbMV0rdy5odG1sUHJlZmlsdGVyKG8pK3VbMl0sYz11WzBdO3doaWxlKGMtLSlhPWEubGFzdENoaWxkO3cubWVyZ2UocCxhLmNoaWxkTm9kZXMpLChhPWYuZmlyc3RDaGlsZCkudGV4dENvbnRlbnQ9IiJ9ZWxzZSBwLnB1c2godC5jcmVhdGVUZXh0Tm9kZShvKSk7Zi50ZXh0Q29udGVudD0iIixkPTA7d2hpbGUobz1wW2QrK10paWYociYmdy5pbkFycmF5KG8scik+LTEpaSYmaS5wdXNoKG8pO2Vsc2UgaWYobD13LmNvbnRhaW5zKG8ub3duZXJEb2N1bWVudCxvKSxhPXllKGYuYXBwZW5kQ2hpbGQobyksInNjcmlwdCIpLGwmJnZlKGEpLG4pe2M9MDt3aGlsZShvPWFbYysrXSloZS50ZXN0KG8udHlwZXx8IiIpJiZuLnB1c2gobyl9cmV0dXJuIGZ9IWZ1bmN0aW9uKCl7dmFyIGU9ci5jcmVhdGVEb2N1bWVudEZyYWdtZW50KCkuYXBwZW5kQ2hpbGQoci5jcmVhdGVFbGVtZW50KCJkaXYiKSksdD1yLmNyZWF0ZUVsZW1lbnQoImlucHV0Iik7dC5zZXRBdHRyaWJ1dGUoInR5cGUiLCJyYWRpbyIpLHQuc2V0QXR0cmlidXRlKCJjaGVja2VkIiwiY2hlY2tlZCIpLHQuc2V0QXR0cmlidXRlKCJuYW1lIiwidCIpLGUuYXBwZW5kQ2hpbGQodCksaC5jaGVja0Nsb25lPWUuY2xvbmVOb2RlKCEwKS5jbG9uZU5vZGUoITApLmxhc3RDaGlsZC5jaGVja2VkLGUuaW5uZXJIVE1MPSI8dGV4dGFyZWE+eDwvdGV4dGFyZWE+IixoLm5vQ2xvbmVDaGVja2VkPSEhZS5jbG9uZU5vZGUoITApLmxhc3RDaGlsZC5kZWZhdWx0VmFsdWV9KCk7dmFyIGJlPXIuZG9jdW1lbnRFbGVtZW50LHdlPS9ea2V5LyxUZT0vXig/Om1vdXNlfHBvaW50ZXJ8Y29udGV4dG1lbnV8ZHJhZ3xkcm9wKXxjbGljay8sQ2U9L14oW14uXSopKD86XC4oLispfCkvO2Z1bmN0aW9uIEVlKCl7cmV0dXJuITB9ZnVuY3Rpb24ga2UoKXtyZXR1cm4hMX1mdW5jdGlvbiBTZSgpe3RyeXtyZXR1cm4gci5hY3RpdmVFbGVtZW50fWNhdGNoKGUpe319ZnVuY3Rpb24gRGUoZSx0LG4scixpLG8pe3ZhciBhLHM7aWYoIm9iamVjdCI9PXR5cGVvZiB0KXsic3RyaW5nIiE9dHlwZW9mIG4mJihyPXJ8fG4sbj12b2lkIDApO2ZvcihzIGluIHQpRGUoZSxzLG4scix0W3NdLG8pO3JldHVybiBlfWlmKG51bGw9PXImJm51bGw9PWk/KGk9bixyPW49dm9pZCAwKTpudWxsPT1pJiYoInN0cmluZyI9PXR5cGVvZiBuPyhpPXIscj12b2lkIDApOihpPXIscj1uLG49dm9pZCAwKSksITE9PT1pKWk9a2U7ZWxzZSBpZighaSlyZXR1cm4gZTtyZXR1cm4gMT09PW8mJihhPWksKGk9ZnVuY3Rpb24oZSl7cmV0dXJuIHcoKS5vZmYoZSksYS5hcHBseSh0aGlzLGFyZ3VtZW50cyl9KS5ndWlkPWEuZ3VpZHx8KGEuZ3VpZD13Lmd1aWQrKykpLGUuZWFjaChmdW5jdGlvbigpe3cuZXZlbnQuYWRkKHRoaXMsdCxpLHIsbil9KX13LmV2ZW50PXtnbG9iYWw6e30sYWRkOmZ1bmN0aW9uKGUsdCxuLHIsaSl7dmFyIG8sYSxzLHUsbCxjLGYscCxkLGgsZyx5PUouZ2V0KGUpO2lmKHkpe24uaGFuZGxlciYmKG49KG89bikuaGFuZGxlcixpPW8uc2VsZWN0b3IpLGkmJncuZmluZC5tYXRjaGVzU2VsZWN0b3IoYmUsaSksbi5ndWlkfHwobi5ndWlkPXcuZ3VpZCsrKSwodT15LmV2ZW50cyl8fCh1PXkuZXZlbnRzPXt9KSwoYT15LmhhbmRsZSl8fChhPXkuaGFuZGxlPWZ1bmN0aW9uKHQpe3JldHVybiJ1bmRlZmluZWQiIT10eXBlb2YgdyYmdy5ldmVudC50cmlnZ2VyZWQhPT10LnR5cGU/dy5ldmVudC5kaXNwYXRjaC5hcHBseShlLGFyZ3VtZW50cyk6dm9pZCAwfSksbD0odD0odHx8IiIpLm1hdGNoKE0pfHxbIiJdKS5sZW5ndGg7d2hpbGUobC0tKWQ9Zz0ocz1DZS5leGVjKHRbbF0pfHxbXSlbMV0saD0oc1syXXx8IiIpLnNwbGl0KCIuIikuc29ydCgpLGQmJihmPXcuZXZlbnQuc3BlY2lhbFtkXXx8e30sZD0oaT9mLmRlbGVnYXRlVHlwZTpmLmJpbmRUeXBlKXx8ZCxmPXcuZXZlbnQuc3BlY2lhbFtkXXx8e30sYz13LmV4dGVuZCh7dHlwZTpkLG9yaWdUeXBlOmcsZGF0YTpyLGhhbmRsZXI6bixndWlkOm4uZ3VpZCxzZWxlY3RvcjppLG5lZWRzQ29udGV4dDppJiZ3LmV4cHIubWF0Y2gubmVlZHNDb250ZXh0LnRlc3QoaSksbmFtZXNwYWNlOmguam9pbigiLiIpfSxvKSwocD11W2RdKXx8KChwPXVbZF09W10pLmRlbGVnYXRlQ291bnQ9MCxmLnNldHVwJiYhMSE9PWYuc2V0dXAuY2FsbChlLHIsaCxhKXx8ZS5hZGRFdmVudExpc3RlbmVyJiZlLmFkZEV2ZW50TGlzdGVuZXIoZCxhKSksZi5hZGQmJihmLmFkZC5jYWxsKGUsYyksYy5oYW5kbGVyLmd1aWR8fChjLmhhbmRsZXIuZ3VpZD1uLmd1aWQpKSxpP3Auc3BsaWNlKHAuZGVsZWdhdGVDb3VudCsrLDAsYyk6cC5wdXNoKGMpLHcuZXZlbnQuZ2xvYmFsW2RdPSEwKX19LHJlbW92ZTpmdW5jdGlvbihlLHQsbixyLGkpe3ZhciBvLGEscyx1LGwsYyxmLHAsZCxoLGcseT1KLmhhc0RhdGEoZSkmJkouZ2V0KGUpO2lmKHkmJih1PXkuZXZlbnRzKSl7bD0odD0odHx8IiIpLm1hdGNoKE0pfHxbIiJdKS5sZW5ndGg7d2hpbGUobC0tKWlmKHM9Q2UuZXhlYyh0W2xdKXx8W10sZD1nPXNbMV0saD0oc1syXXx8IiIpLnNwbGl0KCIuIikuc29ydCgpLGQpe2Y9dy5ldmVudC5zcGVjaWFsW2RdfHx7fSxwPXVbZD0ocj9mLmRlbGVnYXRlVHlwZTpmLmJpbmRUeXBlKXx8ZF18fFtdLHM9c1syXSYmbmV3IFJlZ0V4cCgiKF58XFwuKSIraC5qb2luKCJcXC4oPzouKlxcLnwpIikrIihcXC58JCkiKSxhPW89cC5sZW5ndGg7d2hpbGUoby0tKWM9cFtvXSwhaSYmZyE9PWMub3JpZ1R5cGV8fG4mJm4uZ3VpZCE9PWMuZ3VpZHx8cyYmIXMudGVzdChjLm5hbWVzcGFjZSl8fHImJnIhPT1jLnNlbGVjdG9yJiYoIioqIiE9PXJ8fCFjLnNlbGVjdG9yKXx8KHAuc3BsaWNlKG8sMSksYy5zZWxlY3RvciYmcC5kZWxlZ2F0ZUNvdW50LS0sZi5yZW1vdmUmJmYucmVtb3ZlLmNhbGwoZSxjKSk7YSYmIXAubGVuZ3RoJiYoZi50ZWFyZG93biYmITEhPT1mLnRlYXJkb3duLmNhbGwoZSxoLHkuaGFuZGxlKXx8dy5yZW1vdmVFdmVudChlLGQseS5oYW5kbGUpLGRlbGV0ZSB1W2RdKX1lbHNlIGZvcihkIGluIHUpdy5ldmVudC5yZW1vdmUoZSxkK3RbbF0sbixyLCEwKTt3LmlzRW1wdHlPYmplY3QodSkmJkoucmVtb3ZlKGUsImhhbmRsZSBldmVudHMiKX19LGRpc3BhdGNoOmZ1bmN0aW9uKGUpe3ZhciB0PXcuZXZlbnQuZml4KGUpLG4scixpLG8sYSxzLHU9bmV3IEFycmF5KGFyZ3VtZW50cy5sZW5ndGgpLGw9KEouZ2V0KHRoaXMsImV2ZW50cyIpfHx7fSlbdC50eXBlXXx8W10sYz13LmV2ZW50LnNwZWNpYWxbdC50eXBlXXx8e307Zm9yKHVbMF09dCxuPTE7bjxhcmd1bWVudHMubGVuZ3RoO24rKyl1W25dPWFyZ3VtZW50c1tuXTtpZih0LmRlbGVnYXRlVGFyZ2V0PXRoaXMsIWMucHJlRGlzcGF0Y2h8fCExIT09Yy5wcmVEaXNwYXRjaC5jYWxsKHRoaXMsdCkpe3M9dy5ldmVudC5oYW5kbGVycy5jYWxsKHRoaXMsdCxsKSxuPTA7d2hpbGUoKG89c1tuKytdKSYmIXQuaXNQcm9wYWdhdGlvblN0b3BwZWQoKSl7dC5jdXJyZW50VGFyZ2V0PW8uZWxlbSxyPTA7d2hpbGUoKGE9by5oYW5kbGVyc1tyKytdKSYmIXQuaXNJbW1lZGlhdGVQcm9wYWdhdGlvblN0b3BwZWQoKSl0LnJuYW1lc3BhY2UmJiF0LnJuYW1lc3BhY2UudGVzdChhLm5hbWVzcGFjZSl8fCh0LmhhbmRsZU9iaj1hLHQuZGF0YT1hLmRhdGEsdm9pZCAwIT09KGk9KCh3LmV2ZW50LnNwZWNpYWxbYS5vcmlnVHlwZV18fHt9KS5oYW5kbGV8fGEuaGFuZGxlcikuYXBwbHkoby5lbGVtLHUpKSYmITE9PT0odC5yZXN1bHQ9aSkmJih0LnByZXZlbnREZWZhdWx0KCksdC5zdG9wUHJvcGFnYXRpb24oKSkpfXJldHVybiBjLnBvc3REaXNwYXRjaCYmYy5wb3N0RGlzcGF0Y2guY2FsbCh0aGlzLHQpLHQucmVzdWx0fX0saGFuZGxlcnM6ZnVuY3Rpb24oZSx0KXt2YXIgbixyLGksbyxhLHM9W10sdT10LmRlbGVnYXRlQ291bnQsbD1lLnRhcmdldDtpZih1JiZsLm5vZGVUeXBlJiYhKCJjbGljayI9PT1lLnR5cGUmJmUuYnV0dG9uPj0xKSlmb3IoO2whPT10aGlzO2w9bC5wYXJlbnROb2RlfHx0aGlzKWlmKDE9PT1sLm5vZGVUeXBlJiYoImNsaWNrIiE9PWUudHlwZXx8ITAhPT1sLmRpc2FibGVkKSl7Zm9yKG89W10sYT17fSxuPTA7bjx1O24rKyl2b2lkIDA9PT1hW2k9KHI9dFtuXSkuc2VsZWN0b3IrIiAiXSYmKGFbaV09ci5uZWVkc0NvbnRleHQ/dyhpLHRoaXMpLmluZGV4KGwpPi0xOncuZmluZChpLHRoaXMsbnVsbCxbbF0pLmxlbmd0aCksYVtpXSYmby5wdXNoKHIpO28ubGVuZ3RoJiZzLnB1c2goe2VsZW06bCxoYW5kbGVyczpvfSl9cmV0dXJuIGw9dGhpcyx1PHQubGVuZ3RoJiZzLnB1c2goe2VsZW06bCxoYW5kbGVyczp0LnNsaWNlKHUpfSksc30sYWRkUHJvcDpmdW5jdGlvbihlLHQpe09iamVjdC5kZWZpbmVQcm9wZXJ0eSh3LkV2ZW50LnByb3RvdHlwZSxlLHtlbnVtZXJhYmxlOiEwLGNvbmZpZ3VyYWJsZTohMCxnZXQ6Zyh0KT9mdW5jdGlvbigpe2lmKHRoaXMub3JpZ2luYWxFdmVudClyZXR1cm4gdCh0aGlzLm9yaWdpbmFsRXZlbnQpfTpmdW5jdGlvbigpe2lmKHRoaXMub3JpZ2luYWxFdmVudClyZXR1cm4gdGhpcy5vcmlnaW5hbEV2ZW50W2VdfSxzZXQ6ZnVuY3Rpb24odCl7T2JqZWN0LmRlZmluZVByb3BlcnR5KHRoaXMsZSx7ZW51bWVyYWJsZTohMCxjb25maWd1cmFibGU6ITAsd3JpdGFibGU6ITAsdmFsdWU6dH0pfX0pfSxmaXg6ZnVuY3Rpb24oZSl7cmV0dXJuIGVbdy5leHBhbmRvXT9lOm5ldyB3LkV2ZW50KGUpfSxzcGVjaWFsOntsb2FkOntub0J1YmJsZTohMH0sZm9jdXM6e3RyaWdnZXI6ZnVuY3Rpb24oKXtpZih0aGlzIT09U2UoKSYmdGhpcy5mb2N1cylyZXR1cm4gdGhpcy5mb2N1cygpLCExfSxkZWxlZ2F0ZVR5cGU6ImZvY3VzaW4ifSxibHVyOnt0cmlnZ2VyOmZ1bmN0aW9uKCl7aWYodGhpcz09PVNlKCkmJnRoaXMuYmx1cilyZXR1cm4gdGhpcy5ibHVyKCksITF9LGRlbGVnYXRlVHlwZToiZm9jdXNvdXQifSxjbGljazp7dHJpZ2dlcjpmdW5jdGlvbigpe2lmKCJjaGVja2JveCI9PT10aGlzLnR5cGUmJnRoaXMuY2xpY2smJk4odGhpcywiaW5wdXQiKSlyZXR1cm4gdGhpcy5jbGljaygpLCExfSxfZGVmYXVsdDpmdW5jdGlvbihlKXtyZXR1cm4gTihlLnRhcmdldCwiYSIpfX0sYmVmb3JldW5sb2FkOntwb3N0RGlzcGF0Y2g6ZnVuY3Rpb24oZSl7dm9pZCAwIT09ZS5yZXN1bHQmJmUub3JpZ2luYWxFdmVudCYmKGUub3JpZ2luYWxFdmVudC5yZXR1cm5WYWx1ZT1lLnJlc3VsdCl9fX19LHcucmVtb3ZlRXZlbnQ9ZnVuY3Rpb24oZSx0LG4pe2UucmVtb3ZlRXZlbnRMaXN0ZW5lciYmZS5yZW1vdmVFdmVudExpc3RlbmVyKHQsbil9LHcuRXZlbnQ9ZnVuY3Rpb24oZSx0KXtpZighKHRoaXMgaW5zdGFuY2VvZiB3LkV2ZW50KSlyZXR1cm4gbmV3IHcuRXZlbnQoZSx0KTtlJiZlLnR5cGU/KHRoaXMub3JpZ2luYWxFdmVudD1lLHRoaXMudHlwZT1lLnR5cGUsdGhpcy5pc0RlZmF1bHRQcmV2ZW50ZWQ9ZS5kZWZhdWx0UHJldmVudGVkfHx2b2lkIDA9PT1lLmRlZmF1bHRQcmV2ZW50ZWQmJiExPT09ZS5yZXR1cm5WYWx1ZT9FZTprZSx0aGlzLnRhcmdldD1lLnRhcmdldCYmMz09PWUudGFyZ2V0Lm5vZGVUeXBlP2UudGFyZ2V0LnBhcmVudE5vZGU6ZS50YXJnZXQsdGhpcy5jdXJyZW50VGFyZ2V0PWUuY3VycmVudFRhcmdldCx0aGlzLnJlbGF0ZWRUYXJnZXQ9ZS5yZWxhdGVkVGFyZ2V0KTp0aGlzLnR5cGU9ZSx0JiZ3LmV4dGVuZCh0aGlzLHQpLHRoaXMudGltZVN0YW1wPWUmJmUudGltZVN0YW1wfHxEYXRlLm5vdygpLHRoaXNbdy5leHBhbmRvXT0hMH0sdy5FdmVudC5wcm90b3R5cGU9e2NvbnN0cnVjdG9yOncuRXZlbnQsaXNEZWZhdWx0UHJldmVudGVkOmtlLGlzUHJvcGFnYXRpb25TdG9wcGVkOmtlLGlzSW1tZWRpYXRlUHJvcGFnYXRpb25TdG9wcGVkOmtlLGlzU2ltdWxhdGVkOiExLHByZXZlbnREZWZhdWx0OmZ1bmN0aW9uKCl7dmFyIGU9dGhpcy5vcmlnaW5hbEV2ZW50O3RoaXMuaXNEZWZhdWx0UHJldmVudGVkPUVlLGUmJiF0aGlzLmlzU2ltdWxhdGVkJiZlLnByZXZlbnREZWZhdWx0KCl9LHN0b3BQcm9wYWdhdGlvbjpmdW5jdGlvbigpe3ZhciBlPXRoaXMub3JpZ2luYWxFdmVudDt0aGlzLmlzUHJvcGFnYXRpb25TdG9wcGVkPUVlLGUmJiF0aGlzLmlzU2ltdWxhdGVkJiZlLnN0b3BQcm9wYWdhdGlvbigpfSxzdG9wSW1tZWRpYXRlUHJvcGFnYXRpb246ZnVuY3Rpb24oKXt2YXIgZT10aGlzLm9yaWdpbmFsRXZlbnQ7dGhpcy5pc0ltbWVkaWF0ZVByb3BhZ2F0aW9uU3RvcHBlZD1FZSxlJiYhdGhpcy5pc1NpbXVsYXRlZCYmZS5zdG9wSW1tZWRpYXRlUHJvcGFnYXRpb24oKSx0aGlzLnN0b3BQcm9wYWdhdGlvbigpfX0sdy5lYWNoKHthbHRLZXk6ITAsYnViYmxlczohMCxjYW5jZWxhYmxlOiEwLGNoYW5nZWRUb3VjaGVzOiEwLGN0cmxLZXk6ITAsZGV0YWlsOiEwLGV2ZW50UGhhc2U6ITAsbWV0YUtleTohMCxwYWdlWDohMCxwYWdlWTohMCxzaGlmdEtleTohMCx2aWV3OiEwLCJjaGFyIjohMCxjaGFyQ29kZTohMCxrZXk6ITAsa2V5Q29kZTohMCxidXR0b246ITAsYnV0dG9uczohMCxjbGllbnRYOiEwLGNsaWVudFk6ITAsb2Zmc2V0WDohMCxvZmZzZXRZOiEwLHBvaW50ZXJJZDohMCxwb2ludGVyVHlwZTohMCxzY3JlZW5YOiEwLHNjcmVlblk6ITAsdGFyZ2V0VG91Y2hlczohMCx0b0VsZW1lbnQ6ITAsdG91Y2hlczohMCx3aGljaDpmdW5jdGlvbihlKXt2YXIgdD1lLmJ1dHRvbjtyZXR1cm4gbnVsbD09ZS53aGljaCYmd2UudGVzdChlLnR5cGUpP251bGwhPWUuY2hhckNvZGU/ZS5jaGFyQ29kZTplLmtleUNvZGU6IWUud2hpY2gmJnZvaWQgMCE9PXQmJlRlLnRlc3QoZS50eXBlKT8xJnQ/MToyJnQ/Mzo0JnQ/MjowOmUud2hpY2h9fSx3LmV2ZW50LmFkZFByb3ApLHcuZWFjaCh7bW91c2VlbnRlcjoibW91c2VvdmVyIixtb3VzZWxlYXZlOiJtb3VzZW91dCIscG9pbnRlcmVudGVyOiJwb2ludGVyb3ZlciIscG9pbnRlcmxlYXZlOiJwb2ludGVyb3V0In0sZnVuY3Rpb24oZSx0KXt3LmV2ZW50LnNwZWNpYWxbZV09e2RlbGVnYXRlVHlwZTp0LGJpbmRUeXBlOnQsaGFuZGxlOmZ1bmN0aW9uKGUpe3ZhciBuLHI9dGhpcyxpPWUucmVsYXRlZFRhcmdldCxvPWUuaGFuZGxlT2JqO3JldHVybiBpJiYoaT09PXJ8fHcuY29udGFpbnMocixpKSl8fChlLnR5cGU9by5vcmlnVHlwZSxuPW8uaGFuZGxlci5hcHBseSh0aGlzLGFyZ3VtZW50cyksZS50eXBlPXQpLG59fX0pLHcuZm4uZXh0ZW5kKHtvbjpmdW5jdGlvbihlLHQsbixyKXtyZXR1cm4gRGUodGhpcyxlLHQsbixyKX0sb25lOmZ1bmN0aW9uKGUsdCxuLHIpe3JldHVybiBEZSh0aGlzLGUsdCxuLHIsMSl9LG9mZjpmdW5jdGlvbihlLHQsbil7dmFyIHIsaTtpZihlJiZlLnByZXZlbnREZWZhdWx0JiZlLmhhbmRsZU9iailyZXR1cm4gcj1lLmhhbmRsZU9iaix3KGUuZGVsZWdhdGVUYXJnZXQpLm9mZihyLm5hbWVzcGFjZT9yLm9yaWdUeXBlKyIuIityLm5hbWVzcGFjZTpyLm9yaWdUeXBlLHIuc2VsZWN0b3Isci5oYW5kbGVyKSx0aGlzO2lmKCJvYmplY3QiPT10eXBlb2YgZSl7Zm9yKGkgaW4gZSl0aGlzLm9mZihpLHQsZVtpXSk7cmV0dXJuIHRoaXN9cmV0dXJuITEhPT10JiYiZnVuY3Rpb24iIT10eXBlb2YgdHx8KG49dCx0PXZvaWQgMCksITE9PT1uJiYobj1rZSksdGhpcy5lYWNoKGZ1bmN0aW9uKCl7dy5ldmVudC5yZW1vdmUodGhpcyxlLG4sdCl9KX19KTt2YXIgTmU9LzwoPyFhcmVhfGJyfGNvbHxlbWJlZHxocnxpbWd8aW5wdXR8bGlua3xtZXRhfHBhcmFtKSgoW2Etel1bXlwvXDA+XHgyMFx0XHJcblxmXSopW14+XSopXC8+L2dpLEFlPS88c2NyaXB0fDxzdHlsZXw8bGluay9pLGplPS9jaGVja2VkXHMqKD86W149XXw9XHMqLmNoZWNrZWQuKS9pLHFlPS9eXHMqPCEoPzpcW0NEQVRBXFt8LS0pfCg/OlxdXF18LS0pPlxzKiQvZztmdW5jdGlvbiBMZShlLHQpe3JldHVybiBOKGUsInRhYmxlIikmJk4oMTEhPT10Lm5vZGVUeXBlP3Q6dC5maXJzdENoaWxkLCJ0ciIpP3coZSkuY2hpbGRyZW4oInRib2R5IilbMF18fGU6ZX1mdW5jdGlvbiBIZShlKXtyZXR1cm4gZS50eXBlPShudWxsIT09ZS5nZXRBdHRyaWJ1dGUoInR5cGUiKSkrIi8iK2UudHlwZSxlfWZ1bmN0aW9uIE9lKGUpe3JldHVybiJ0cnVlLyI9PT0oZS50eXBlfHwiIikuc2xpY2UoMCw1KT9lLnR5cGU9ZS50eXBlLnNsaWNlKDUpOmUucmVtb3ZlQXR0cmlidXRlKCJ0eXBlIiksZX1mdW5jdGlvbiBQZShlLHQpe3ZhciBuLHIsaSxvLGEscyx1LGw7aWYoMT09PXQubm9kZVR5cGUpe2lmKEouaGFzRGF0YShlKSYmKG89Si5hY2Nlc3MoZSksYT1KLnNldCh0LG8pLGw9by5ldmVudHMpKXtkZWxldGUgYS5oYW5kbGUsYS5ldmVudHM9e307Zm9yKGkgaW4gbClmb3Iobj0wLHI9bFtpXS5sZW5ndGg7bjxyO24rKyl3LmV2ZW50LmFkZCh0LGksbFtpXVtuXSl9Sy5oYXNEYXRhKGUpJiYocz1LLmFjY2VzcyhlKSx1PXcuZXh0ZW5kKHt9LHMpLEsuc2V0KHQsdSkpfX1mdW5jdGlvbiBNZShlLHQpe3ZhciBuPXQubm9kZU5hbWUudG9Mb3dlckNhc2UoKTsiaW5wdXQiPT09biYmcGUudGVzdChlLnR5cGUpP3QuY2hlY2tlZD1lLmNoZWNrZWQ6ImlucHV0IiE9PW4mJiJ0ZXh0YXJlYSIhPT1ufHwodC5kZWZhdWx0VmFsdWU9ZS5kZWZhdWx0VmFsdWUpfWZ1bmN0aW9uIFJlKGUsdCxuLHIpe3Q9YS5hcHBseShbXSx0KTt2YXIgaSxvLHMsdSxsLGMsZj0wLHA9ZS5sZW5ndGgsZD1wLTEseT10WzBdLHY9Zyh5KTtpZih2fHxwPjEmJiJzdHJpbmciPT10eXBlb2YgeSYmIWguY2hlY2tDbG9uZSYmamUudGVzdCh5KSlyZXR1cm4gZS5lYWNoKGZ1bmN0aW9uKGkpe3ZhciBvPWUuZXEoaSk7diYmKHRbMF09eS5jYWxsKHRoaXMsaSxvLmh0bWwoKSkpLFJlKG8sdCxuLHIpfSk7aWYocCYmKGk9eGUodCxlWzBdLm93bmVyRG9jdW1lbnQsITEsZSxyKSxvPWkuZmlyc3RDaGlsZCwxPT09aS5jaGlsZE5vZGVzLmxlbmd0aCYmKGk9byksb3x8cikpe2Zvcih1PShzPXcubWFwKHllKGksInNjcmlwdCIpLEhlKSkubGVuZ3RoO2Y8cDtmKyspbD1pLGYhPT1kJiYobD13LmNsb25lKGwsITAsITApLHUmJncubWVyZ2Uocyx5ZShsLCJzY3JpcHQiKSkpLG4uY2FsbChlW2ZdLGwsZik7aWYodSlmb3IoYz1zW3MubGVuZ3RoLTFdLm93bmVyRG9jdW1lbnQsdy5tYXAocyxPZSksZj0wO2Y8dTtmKyspbD1zW2ZdLGhlLnRlc3QobC50eXBlfHwiIikmJiFKLmFjY2VzcyhsLCJnbG9iYWxFdmFsIikmJncuY29udGFpbnMoYyxsKSYmKGwuc3JjJiYibW9kdWxlIiE9PShsLnR5cGV8fCIiKS50b0xvd2VyQ2FzZSgpP3cuX2V2YWxVcmwmJncuX2V2YWxVcmwobC5zcmMpOm0obC50ZXh0Q29udGVudC5yZXBsYWNlKHFlLCIiKSxjLGwpKX1yZXR1cm4gZX1mdW5jdGlvbiBJZShlLHQsbil7Zm9yKHZhciByLGk9dD93LmZpbHRlcih0LGUpOmUsbz0wO251bGwhPShyPWlbb10pO28rKylufHwxIT09ci5ub2RlVHlwZXx8dy5jbGVhbkRhdGEoeWUocikpLHIucGFyZW50Tm9kZSYmKG4mJncuY29udGFpbnMoci5vd25lckRvY3VtZW50LHIpJiZ2ZSh5ZShyLCJzY3JpcHQiKSksci5wYXJlbnROb2RlLnJlbW92ZUNoaWxkKHIpKTtyZXR1cm4gZX13LmV4dGVuZCh7aHRtbFByZWZpbHRlcjpmdW5jdGlvbihlKXtyZXR1cm4gZS5yZXBsYWNlKE5lLCI8JDE+PC8kMj4iKX0sY2xvbmU6ZnVuY3Rpb24oZSx0LG4pe3ZhciByLGksbyxhLHM9ZS5jbG9uZU5vZGUoITApLHU9dy5jb250YWlucyhlLm93bmVyRG9jdW1lbnQsZSk7aWYoIShoLm5vQ2xvbmVDaGVja2VkfHwxIT09ZS5ub2RlVHlwZSYmMTEhPT1lLm5vZGVUeXBlfHx3LmlzWE1MRG9jKGUpKSlmb3IoYT15ZShzKSxyPTAsaT0obz15ZShlKSkubGVuZ3RoO3I8aTtyKyspTWUob1tyXSxhW3JdKTtpZih0KWlmKG4pZm9yKG89b3x8eWUoZSksYT1hfHx5ZShzKSxyPTAsaT1vLmxlbmd0aDtyPGk7cisrKVBlKG9bcl0sYVtyXSk7ZWxzZSBQZShlLHMpO3JldHVybihhPXllKHMsInNjcmlwdCIpKS5sZW5ndGg+MCYmdmUoYSwhdSYmeWUoZSwic2NyaXB0IikpLHN9LGNsZWFuRGF0YTpmdW5jdGlvbihlKXtmb3IodmFyIHQsbixyLGk9dy5ldmVudC5zcGVjaWFsLG89MDt2b2lkIDAhPT0obj1lW29dKTtvKyspaWYoWShuKSl7aWYodD1uW0ouZXhwYW5kb10pe2lmKHQuZXZlbnRzKWZvcihyIGluIHQuZXZlbnRzKWlbcl0/dy5ldmVudC5yZW1vdmUobixyKTp3LnJlbW92ZUV2ZW50KG4scix0LmhhbmRsZSk7bltKLmV4cGFuZG9dPXZvaWQgMH1uW0suZXhwYW5kb10mJihuW0suZXhwYW5kb109dm9pZCAwKX19fSksdy5mbi5leHRlbmQoe2RldGFjaDpmdW5jdGlvbihlKXtyZXR1cm4gSWUodGhpcyxlLCEwKX0scmVtb3ZlOmZ1bmN0aW9uKGUpe3JldHVybiBJZSh0aGlzLGUpfSx0ZXh0OmZ1bmN0aW9uKGUpe3JldHVybiB6KHRoaXMsZnVuY3Rpb24oZSl7cmV0dXJuIHZvaWQgMD09PWU/dy50ZXh0KHRoaXMpOnRoaXMuZW1wdHkoKS5lYWNoKGZ1bmN0aW9uKCl7MSE9PXRoaXMubm9kZVR5cGUmJjExIT09dGhpcy5ub2RlVHlwZSYmOSE9PXRoaXMubm9kZVR5cGV8fCh0aGlzLnRleHRDb250ZW50PWUpfSl9LG51bGwsZSxhcmd1bWVudHMubGVuZ3RoKX0sYXBwZW5kOmZ1bmN0aW9uKCl7cmV0dXJuIFJlKHRoaXMsYXJndW1lbnRzLGZ1bmN0aW9uKGUpezEhPT10aGlzLm5vZGVUeXBlJiYxMSE9PXRoaXMubm9kZVR5cGUmJjkhPT10aGlzLm5vZGVUeXBlfHxMZSh0aGlzLGUpLmFwcGVuZENoaWxkKGUpfSl9LHByZXBlbmQ6ZnVuY3Rpb24oKXtyZXR1cm4gUmUodGhpcyxhcmd1bWVudHMsZnVuY3Rpb24oZSl7aWYoMT09PXRoaXMubm9kZVR5cGV8fDExPT09dGhpcy5ub2RlVHlwZXx8OT09PXRoaXMubm9kZVR5cGUpe3ZhciB0PUxlKHRoaXMsZSk7dC5pbnNlcnRCZWZvcmUoZSx0LmZpcnN0Q2hpbGQpfX0pfSxiZWZvcmU6ZnVuY3Rpb24oKXtyZXR1cm4gUmUodGhpcyxhcmd1bWVudHMsZnVuY3Rpb24oZSl7dGhpcy5wYXJlbnROb2RlJiZ0aGlzLnBhcmVudE5vZGUuaW5zZXJ0QmVmb3JlKGUsdGhpcyl9KX0sYWZ0ZXI6ZnVuY3Rpb24oKXtyZXR1cm4gUmUodGhpcyxhcmd1bWVudHMsZnVuY3Rpb24oZSl7dGhpcy5wYXJlbnROb2RlJiZ0aGlzLnBhcmVudE5vZGUuaW5zZXJ0QmVmb3JlKGUsdGhpcy5uZXh0U2libGluZyl9KX0sZW1wdHk6ZnVuY3Rpb24oKXtmb3IodmFyIGUsdD0wO251bGwhPShlPXRoaXNbdF0pO3QrKykxPT09ZS5ub2RlVHlwZSYmKHcuY2xlYW5EYXRhKHllKGUsITEpKSxlLnRleHRDb250ZW50PSIiKTtyZXR1cm4gdGhpc30sY2xvbmU6ZnVuY3Rpb24oZSx0KXtyZXR1cm4gZT1udWxsIT1lJiZlLHQ9bnVsbD09dD9lOnQsdGhpcy5tYXAoZnVuY3Rpb24oKXtyZXR1cm4gdy5jbG9uZSh0aGlzLGUsdCl9KX0saHRtbDpmdW5jdGlvbihlKXtyZXR1cm4geih0aGlzLGZ1bmN0aW9uKGUpe3ZhciB0PXRoaXNbMF18fHt9LG49MCxyPXRoaXMubGVuZ3RoO2lmKHZvaWQgMD09PWUmJjE9PT10Lm5vZGVUeXBlKXJldHVybiB0LmlubmVySFRNTDtpZigic3RyaW5nIj09dHlwZW9mIGUmJiFBZS50ZXN0KGUpJiYhZ2VbKGRlLmV4ZWMoZSl8fFsiIiwiIl0pWzFdLnRvTG93ZXJDYXNlKCldKXtlPXcuaHRtbFByZWZpbHRlcihlKTt0cnl7Zm9yKDtuPHI7bisrKTE9PT0odD10aGlzW25dfHx7fSkubm9kZVR5cGUmJih3LmNsZWFuRGF0YSh5ZSh0LCExKSksdC5pbm5lckhUTUw9ZSk7dD0wfWNhdGNoKGUpe319dCYmdGhpcy5lbXB0eSgpLmFwcGVuZChlKX0sbnVsbCxlLGFyZ3VtZW50cy5sZW5ndGgpfSxyZXBsYWNlV2l0aDpmdW5jdGlvbigpe3ZhciBlPVtdO3JldHVybiBSZSh0aGlzLGFyZ3VtZW50cyxmdW5jdGlvbih0KXt2YXIgbj10aGlzLnBhcmVudE5vZGU7dy5pbkFycmF5KHRoaXMsZSk8MCYmKHcuY2xlYW5EYXRhKHllKHRoaXMpKSxuJiZuLnJlcGxhY2VDaGlsZCh0LHRoaXMpKX0sZSl9fSksdy5lYWNoKHthcHBlbmRUbzoiYXBwZW5kIixwcmVwZW5kVG86InByZXBlbmQiLGluc2VydEJlZm9yZToiYmVmb3JlIixpbnNlcnRBZnRlcjoiYWZ0ZXIiLHJlcGxhY2VBbGw6InJlcGxhY2VXaXRoIn0sZnVuY3Rpb24oZSx0KXt3LmZuW2VdPWZ1bmN0aW9uKGUpe2Zvcih2YXIgbixyPVtdLGk9dyhlKSxvPWkubGVuZ3RoLTEsYT0wO2E8PW87YSsrKW49YT09PW8/dGhpczp0aGlzLmNsb25lKCEwKSx3KGlbYV0pW3RdKG4pLHMuYXBwbHkocixuLmdldCgpKTtyZXR1cm4gdGhpcy5wdXNoU3RhY2socil9fSk7dmFyIFdlPW5ldyBSZWdFeHAoIl4oIityZSsiKSg/IXB4KVthLXolXSskIiwiaSIpLCRlPWZ1bmN0aW9uKHQpe3ZhciBuPXQub3duZXJEb2N1bWVudC5kZWZhdWx0VmlldztyZXR1cm4gbiYmbi5vcGVuZXJ8fChuPWUpLG4uZ2V0Q29tcHV0ZWRTdHlsZSh0KX0sQmU9bmV3IFJlZ0V4cChvZS5qb2luKCJ8IiksImkiKTshZnVuY3Rpb24oKXtmdW5jdGlvbiB0KCl7aWYoYyl7bC5zdHlsZS5jc3NUZXh0PSJwb3NpdGlvbjphYnNvbHV0ZTtsZWZ0Oi0xMTExMXB4O3dpZHRoOjYwcHg7bWFyZ2luLXRvcDoxcHg7cGFkZGluZzowO2JvcmRlcjowIixjLnN0eWxlLmNzc1RleHQ9InBvc2l0aW9uOnJlbGF0aXZlO2Rpc3BsYXk6YmxvY2s7Ym94LXNpemluZzpib3JkZXItYm94O292ZXJmbG93OnNjcm9sbDttYXJnaW46YXV0bztib3JkZXI6MXB4O3BhZGRpbmc6MXB4O3dpZHRoOjYwJTt0b3A6MSUiLGJlLmFwcGVuZENoaWxkKGwpLmFwcGVuZENoaWxkKGMpO3ZhciB0PWUuZ2V0Q29tcHV0ZWRTdHlsZShjKTtpPSIxJSIhPT10LnRvcCx1PTEyPT09bih0Lm1hcmdpbkxlZnQpLGMuc3R5bGUucmlnaHQ9IjYwJSIscz0zNj09PW4odC5yaWdodCksbz0zNj09PW4odC53aWR0aCksYy5zdHlsZS5wb3NpdGlvbj0iYWJzb2x1dGUiLGE9MzY9PT1jLm9mZnNldFdpZHRofHwiYWJzb2x1dGUiLGJlLnJlbW92ZUNoaWxkKGwpLGM9bnVsbH19ZnVuY3Rpb24gbihlKXtyZXR1cm4gTWF0aC5yb3VuZChwYXJzZUZsb2F0KGUpKX12YXIgaSxvLGEscyx1LGw9ci5jcmVhdGVFbGVtZW50KCJkaXYiKSxjPXIuY3JlYXRlRWxlbWVudCgiZGl2Iik7Yy5zdHlsZSYmKGMuc3R5bGUuYmFja2dyb3VuZENsaXA9ImNvbnRlbnQtYm94IixjLmNsb25lTm9kZSghMCkuc3R5bGUuYmFja2dyb3VuZENsaXA9IiIsaC5jbGVhckNsb25lU3R5bGU9ImNvbnRlbnQtYm94Ij09PWMuc3R5bGUuYmFja2dyb3VuZENsaXAsdy5leHRlbmQoaCx7Ym94U2l6aW5nUmVsaWFibGU6ZnVuY3Rpb24oKXtyZXR1cm4gdCgpLG99LHBpeGVsQm94U3R5bGVzOmZ1bmN0aW9uKCl7cmV0dXJuIHQoKSxzfSxwaXhlbFBvc2l0aW9uOmZ1bmN0aW9uKCl7cmV0dXJuIHQoKSxpfSxyZWxpYWJsZU1hcmdpbkxlZnQ6ZnVuY3Rpb24oKXtyZXR1cm4gdCgpLHV9LHNjcm9sbGJveFNpemU6ZnVuY3Rpb24oKXtyZXR1cm4gdCgpLGF9fSkpfSgpO2Z1bmN0aW9uIEZlKGUsdCxuKXt2YXIgcixpLG8sYSxzPWUuc3R5bGU7cmV0dXJuKG49bnx8JGUoZSkpJiYoIiIhPT0oYT1uLmdldFByb3BlcnR5VmFsdWUodCl8fG5bdF0pfHx3LmNvbnRhaW5zKGUub3duZXJEb2N1bWVudCxlKXx8KGE9dy5zdHlsZShlLHQpKSwhaC5waXhlbEJveFN0eWxlcygpJiZXZS50ZXN0KGEpJiZCZS50ZXN0KHQpJiYocj1zLndpZHRoLGk9cy5taW5XaWR0aCxvPXMubWF4V2lkdGgscy5taW5XaWR0aD1zLm1heFdpZHRoPXMud2lkdGg9YSxhPW4ud2lkdGgscy53aWR0aD1yLHMubWluV2lkdGg9aSxzLm1heFdpZHRoPW8pKSx2b2lkIDAhPT1hP2ErIiI6YX1mdW5jdGlvbiBfZShlLHQpe3JldHVybntnZXQ6ZnVuY3Rpb24oKXtpZighZSgpKXJldHVybih0aGlzLmdldD10KS5hcHBseSh0aGlzLGFyZ3VtZW50cyk7ZGVsZXRlIHRoaXMuZ2V0fX19dmFyIHplPS9eKG5vbmV8dGFibGUoPyEtY1tlYV0pLispLyxYZT0vXi0tLyxVZT17cG9zaXRpb246ImFic29sdXRlIix2aXNpYmlsaXR5OiJoaWRkZW4iLGRpc3BsYXk6ImJsb2NrIn0sVmU9e2xldHRlclNwYWNpbmc6IjAiLGZvbnRXZWlnaHQ6IjQwMCJ9LEdlPVsiV2Via2l0IiwiTW96IiwibXMiXSxZZT1yLmNyZWF0ZUVsZW1lbnQoImRpdiIpLnN0eWxlO2Z1bmN0aW9uIFFlKGUpe2lmKGUgaW4gWWUpcmV0dXJuIGU7dmFyIHQ9ZVswXS50b1VwcGVyQ2FzZSgpK2Uuc2xpY2UoMSksbj1HZS5sZW5ndGg7d2hpbGUobi0tKWlmKChlPUdlW25dK3QpaW4gWWUpcmV0dXJuIGV9ZnVuY3Rpb24gSmUoZSl7dmFyIHQ9dy5jc3NQcm9wc1tlXTtyZXR1cm4gdHx8KHQ9dy5jc3NQcm9wc1tlXT1RZShlKXx8ZSksdH1mdW5jdGlvbiBLZShlLHQsbil7dmFyIHI9aWUuZXhlYyh0KTtyZXR1cm4gcj9NYXRoLm1heCgwLHJbMl0tKG58fDApKSsoclszXXx8InB4Iik6dH1mdW5jdGlvbiBaZShlLHQsbixyLGksbyl7dmFyIGE9IndpZHRoIj09PXQ/MTowLHM9MCx1PTA7aWYobj09PShyPyJib3JkZXIiOiJjb250ZW50IikpcmV0dXJuIDA7Zm9yKDthPDQ7YSs9MikibWFyZ2luIj09PW4mJih1Kz13LmNzcyhlLG4rb2VbYV0sITAsaSkpLHI/KCJjb250ZW50Ij09PW4mJih1LT13LmNzcyhlLCJwYWRkaW5nIitvZVthXSwhMCxpKSksIm1hcmdpbiIhPT1uJiYodS09dy5jc3MoZSwiYm9yZGVyIitvZVthXSsiV2lkdGgiLCEwLGkpKSk6KHUrPXcuY3NzKGUsInBhZGRpbmciK29lW2FdLCEwLGkpLCJwYWRkaW5nIiE9PW4/dSs9dy5jc3MoZSwiYm9yZGVyIitvZVthXSsiV2lkdGgiLCEwLGkpOnMrPXcuY3NzKGUsImJvcmRlciIrb2VbYV0rIldpZHRoIiwhMCxpKSk7cmV0dXJuIXImJm8+PTAmJih1Kz1NYXRoLm1heCgwLE1hdGguY2VpbChlWyJvZmZzZXQiK3RbMF0udG9VcHBlckNhc2UoKSt0LnNsaWNlKDEpXS1vLXUtcy0uNSkpKSx1fWZ1bmN0aW9uIGV0KGUsdCxuKXt2YXIgcj0kZShlKSxpPUZlKGUsdCxyKSxvPSJib3JkZXItYm94Ij09PXcuY3NzKGUsImJveFNpemluZyIsITEsciksYT1vO2lmKFdlLnRlc3QoaSkpe2lmKCFuKXJldHVybiBpO2k9ImF1dG8ifXJldHVybiBhPWEmJihoLmJveFNpemluZ1JlbGlhYmxlKCl8fGk9PT1lLnN0eWxlW3RdKSwoImF1dG8iPT09aXx8IXBhcnNlRmxvYXQoaSkmJiJpbmxpbmUiPT09dy5jc3MoZSwiZGlzcGxheSIsITEscikpJiYoaT1lWyJvZmZzZXQiK3RbMF0udG9VcHBlckNhc2UoKSt0LnNsaWNlKDEpXSxhPSEwKSwoaT1wYXJzZUZsb2F0KGkpfHwwKStaZShlLHQsbnx8KG8/ImJvcmRlciI6ImNvbnRlbnQiKSxhLHIsaSkrInB4In13LmV4dGVuZCh7Y3NzSG9va3M6e29wYWNpdHk6e2dldDpmdW5jdGlvbihlLHQpe2lmKHQpe3ZhciBuPUZlKGUsIm9wYWNpdHkiKTtyZXR1cm4iIj09PW4/IjEiOm59fX19LGNzc051bWJlcjp7YW5pbWF0aW9uSXRlcmF0aW9uQ291bnQ6ITAsY29sdW1uQ291bnQ6ITAsZmlsbE9wYWNpdHk6ITAsZmxleEdyb3c6ITAsZmxleFNocmluazohMCxmb250V2VpZ2h0OiEwLGxpbmVIZWlnaHQ6ITAsb3BhY2l0eTohMCxvcmRlcjohMCxvcnBoYW5zOiEwLHdpZG93czohMCx6SW5kZXg6ITAsem9vbTohMH0sY3NzUHJvcHM6e30sc3R5bGU6ZnVuY3Rpb24oZSx0LG4scil7aWYoZSYmMyE9PWUubm9kZVR5cGUmJjghPT1lLm5vZGVUeXBlJiZlLnN0eWxlKXt2YXIgaSxvLGEscz1HKHQpLHU9WGUudGVzdCh0KSxsPWUuc3R5bGU7aWYodXx8KHQ9SmUocykpLGE9dy5jc3NIb29rc1t0XXx8dy5jc3NIb29rc1tzXSx2b2lkIDA9PT1uKXJldHVybiBhJiYiZ2V0ImluIGEmJnZvaWQgMCE9PShpPWEuZ2V0KGUsITEscikpP2k6bFt0XTsic3RyaW5nIj09KG89dHlwZW9mIG4pJiYoaT1pZS5leGVjKG4pKSYmaVsxXSYmKG49dWUoZSx0LGkpLG89Im51bWJlciIpLG51bGwhPW4mJm49PT1uJiYoIm51bWJlciI9PT1vJiYobis9aSYmaVszXXx8KHcuY3NzTnVtYmVyW3NdPyIiOiJweCIpKSxoLmNsZWFyQ2xvbmVTdHlsZXx8IiIhPT1ufHwwIT09dC5pbmRleE9mKCJiYWNrZ3JvdW5kIil8fChsW3RdPSJpbmhlcml0IiksYSYmInNldCJpbiBhJiZ2b2lkIDA9PT0obj1hLnNldChlLG4scikpfHwodT9sLnNldFByb3BlcnR5KHQsbik6bFt0XT1uKSl9fSxjc3M6ZnVuY3Rpb24oZSx0LG4scil7dmFyIGksbyxhLHM9Ryh0KTtyZXR1cm4gWGUudGVzdCh0KXx8KHQ9SmUocykpLChhPXcuY3NzSG9va3NbdF18fHcuY3NzSG9va3Nbc10pJiYiZ2V0ImluIGEmJihpPWEuZ2V0KGUsITAsbikpLHZvaWQgMD09PWkmJihpPUZlKGUsdCxyKSksIm5vcm1hbCI9PT1pJiZ0IGluIFZlJiYoaT1WZVt0XSksIiI9PT1ufHxuPyhvPXBhcnNlRmxvYXQoaSksITA9PT1ufHxpc0Zpbml0ZShvKT9vfHwwOmkpOml9fSksdy5lYWNoKFsiaGVpZ2h0Iiwid2lkdGgiXSxmdW5jdGlvbihlLHQpe3cuY3NzSG9va3NbdF09e2dldDpmdW5jdGlvbihlLG4scil7aWYobilyZXR1cm4hemUudGVzdCh3LmNzcyhlLCJkaXNwbGF5IikpfHxlLmdldENsaWVudFJlY3RzKCkubGVuZ3RoJiZlLmdldEJvdW5kaW5nQ2xpZW50UmVjdCgpLndpZHRoP2V0KGUsdCxyKTpzZShlLFVlLGZ1bmN0aW9uKCl7cmV0dXJuIGV0KGUsdCxyKX0pfSxzZXQ6ZnVuY3Rpb24oZSxuLHIpe3ZhciBpLG89JGUoZSksYT0iYm9yZGVyLWJveCI9PT13LmNzcyhlLCJib3hTaXppbmciLCExLG8pLHM9ciYmWmUoZSx0LHIsYSxvKTtyZXR1cm4gYSYmaC5zY3JvbGxib3hTaXplKCk9PT1vLnBvc2l0aW9uJiYocy09TWF0aC5jZWlsKGVbIm9mZnNldCIrdFswXS50b1VwcGVyQ2FzZSgpK3Quc2xpY2UoMSldLXBhcnNlRmxvYXQob1t0XSktWmUoZSx0LCJib3JkZXIiLCExLG8pLS41KSkscyYmKGk9aWUuZXhlYyhuKSkmJiJweCIhPT0oaVszXXx8InB4IikmJihlLnN0eWxlW3RdPW4sbj13LmNzcyhlLHQpKSxLZShlLG4scyl9fX0pLHcuY3NzSG9va3MubWFyZ2luTGVmdD1fZShoLnJlbGlhYmxlTWFyZ2luTGVmdCxmdW5jdGlvbihlLHQpe2lmKHQpcmV0dXJuKHBhcnNlRmxvYXQoRmUoZSwibWFyZ2luTGVmdCIpKXx8ZS5nZXRCb3VuZGluZ0NsaWVudFJlY3QoKS5sZWZ0LXNlKGUse21hcmdpbkxlZnQ6MH0sZnVuY3Rpb24oKXtyZXR1cm4gZS5nZXRCb3VuZGluZ0NsaWVudFJlY3QoKS5sZWZ0fSkpKyJweCJ9KSx3LmVhY2goe21hcmdpbjoiIixwYWRkaW5nOiIiLGJvcmRlcjoiV2lkdGgifSxmdW5jdGlvbihlLHQpe3cuY3NzSG9va3NbZSt0XT17ZXhwYW5kOmZ1bmN0aW9uKG4pe2Zvcih2YXIgcj0wLGk9e30sbz0ic3RyaW5nIj09dHlwZW9mIG4/bi5zcGxpdCgiICIpOltuXTtyPDQ7cisrKWlbZStvZVtyXSt0XT1vW3JdfHxvW3ItMl18fG9bMF07cmV0dXJuIGl9fSwibWFyZ2luIiE9PWUmJih3LmNzc0hvb2tzW2UrdF0uc2V0PUtlKX0pLHcuZm4uZXh0ZW5kKHtjc3M6ZnVuY3Rpb24oZSx0KXtyZXR1cm4geih0aGlzLGZ1bmN0aW9uKGUsdCxuKXt2YXIgcixpLG89e30sYT0wO2lmKEFycmF5LmlzQXJyYXkodCkpe2ZvcihyPSRlKGUpLGk9dC5sZW5ndGg7YTxpO2ErKylvW3RbYV1dPXcuY3NzKGUsdFthXSwhMSxyKTtyZXR1cm4gb31yZXR1cm4gdm9pZCAwIT09bj93LnN0eWxlKGUsdCxuKTp3LmNzcyhlLHQpfSxlLHQsYXJndW1lbnRzLmxlbmd0aD4xKX19KTtmdW5jdGlvbiB0dChlLHQsbixyLGkpe3JldHVybiBuZXcgdHQucHJvdG90eXBlLmluaXQoZSx0LG4scixpKX13LlR3ZWVuPXR0LHR0LnByb3RvdHlwZT17Y29uc3RydWN0b3I6dHQsaW5pdDpmdW5jdGlvbihlLHQsbixyLGksbyl7dGhpcy5lbGVtPWUsdGhpcy5wcm9wPW4sdGhpcy5lYXNpbmc9aXx8dy5lYXNpbmcuX2RlZmF1bHQsdGhpcy5vcHRpb25zPXQsdGhpcy5zdGFydD10aGlzLm5vdz10aGlzLmN1cigpLHRoaXMuZW5kPXIsdGhpcy51bml0PW98fCh3LmNzc051bWJlcltuXT8iIjoicHgiKX0sY3VyOmZ1bmN0aW9uKCl7dmFyIGU9dHQucHJvcEhvb2tzW3RoaXMucHJvcF07cmV0dXJuIGUmJmUuZ2V0P2UuZ2V0KHRoaXMpOnR0LnByb3BIb29rcy5fZGVmYXVsdC5nZXQodGhpcyl9LHJ1bjpmdW5jdGlvbihlKXt2YXIgdCxuPXR0LnByb3BIb29rc1t0aGlzLnByb3BdO3JldHVybiB0aGlzLm9wdGlvbnMuZHVyYXRpb24/dGhpcy5wb3M9dD13LmVhc2luZ1t0aGlzLmVhc2luZ10oZSx0aGlzLm9wdGlvbnMuZHVyYXRpb24qZSwwLDEsdGhpcy5vcHRpb25zLmR1cmF0aW9uKTp0aGlzLnBvcz10PWUsdGhpcy5ub3c9KHRoaXMuZW5kLXRoaXMuc3RhcnQpKnQrdGhpcy5zdGFydCx0aGlzLm9wdGlvbnMuc3RlcCYmdGhpcy5vcHRpb25zLnN0ZXAuY2FsbCh0aGlzLmVsZW0sdGhpcy5ub3csdGhpcyksbiYmbi5zZXQ/bi5zZXQodGhpcyk6dHQucHJvcEhvb2tzLl9kZWZhdWx0LnNldCh0aGlzKSx0aGlzfX0sdHQucHJvdG90eXBlLmluaXQucHJvdG90eXBlPXR0LnByb3RvdHlwZSx0dC5wcm9wSG9va3M9e19kZWZhdWx0OntnZXQ6ZnVuY3Rpb24oZSl7dmFyIHQ7cmV0dXJuIDEhPT1lLmVsZW0ubm9kZVR5cGV8fG51bGwhPWUuZWxlbVtlLnByb3BdJiZudWxsPT1lLmVsZW0uc3R5bGVbZS5wcm9wXT9lLmVsZW1bZS5wcm9wXToodD13LmNzcyhlLmVsZW0sZS5wcm9wLCIiKSkmJiJhdXRvIiE9PXQ/dDowfSxzZXQ6ZnVuY3Rpb24oZSl7dy5meC5zdGVwW2UucHJvcF0/dy5meC5zdGVwW2UucHJvcF0oZSk6MSE9PWUuZWxlbS5ub2RlVHlwZXx8bnVsbD09ZS5lbGVtLnN0eWxlW3cuY3NzUHJvcHNbZS5wcm9wXV0mJiF3LmNzc0hvb2tzW2UucHJvcF0/ZS5lbGVtW2UucHJvcF09ZS5ub3c6dy5zdHlsZShlLmVsZW0sZS5wcm9wLGUubm93K2UudW5pdCl9fX0sdHQucHJvcEhvb2tzLnNjcm9sbFRvcD10dC5wcm9wSG9va3Muc2Nyb2xsTGVmdD17c2V0OmZ1bmN0aW9uKGUpe2UuZWxlbS5ub2RlVHlwZSYmZS5lbGVtLnBhcmVudE5vZGUmJihlLmVsZW1bZS5wcm9wXT1lLm5vdyl9fSx3LmVhc2luZz17bGluZWFyOmZ1bmN0aW9uKGUpe3JldHVybiBlfSxzd2luZzpmdW5jdGlvbihlKXtyZXR1cm4uNS1NYXRoLmNvcyhlKk1hdGguUEkpLzJ9LF9kZWZhdWx0OiJzd2luZyJ9LHcuZng9dHQucHJvdG90eXBlLmluaXQsdy5meC5zdGVwPXt9O3ZhciBudCxydCxpdD0vXig/OnRvZ2dsZXxzaG93fGhpZGUpJC8sb3Q9L3F1ZXVlSG9va3MkLztmdW5jdGlvbiBhdCgpe3J0JiYoITE9PT1yLmhpZGRlbiYmZS5yZXF1ZXN0QW5pbWF0aW9uRnJhbWU/ZS5yZXF1ZXN0QW5pbWF0aW9uRnJhbWUoYXQpOmUuc2V0VGltZW91dChhdCx3LmZ4LmludGVydmFsKSx3LmZ4LnRpY2soKSl9ZnVuY3Rpb24gc3QoKXtyZXR1cm4gZS5zZXRUaW1lb3V0KGZ1bmN0aW9uKCl7bnQ9dm9pZCAwfSksbnQ9RGF0ZS5ub3coKX1mdW5jdGlvbiB1dChlLHQpe3ZhciBuLHI9MCxpPXtoZWlnaHQ6ZX07Zm9yKHQ9dD8xOjA7cjw0O3IrPTItdClpWyJtYXJnaW4iKyhuPW9lW3JdKV09aVsicGFkZGluZyIrbl09ZTtyZXR1cm4gdCYmKGkub3BhY2l0eT1pLndpZHRoPWUpLGl9ZnVuY3Rpb24gbHQoZSx0LG4pe2Zvcih2YXIgcixpPShwdC50d2VlbmVyc1t0XXx8W10pLmNvbmNhdChwdC50d2VlbmVyc1siKiJdKSxvPTAsYT1pLmxlbmd0aDtvPGE7bysrKWlmKHI9aVtvXS5jYWxsKG4sdCxlKSlyZXR1cm4gcn1mdW5jdGlvbiBjdChlLHQsbil7dmFyIHIsaSxvLGEscyx1LGwsYyxmPSJ3aWR0aCJpbiB0fHwiaGVpZ2h0ImluIHQscD10aGlzLGQ9e30saD1lLnN0eWxlLGc9ZS5ub2RlVHlwZSYmYWUoZSkseT1KLmdldChlLCJmeHNob3ciKTtuLnF1ZXVlfHwobnVsbD09KGE9dy5fcXVldWVIb29rcyhlLCJmeCIpKS51bnF1ZXVlZCYmKGEudW5xdWV1ZWQ9MCxzPWEuZW1wdHkuZmlyZSxhLmVtcHR5LmZpcmU9ZnVuY3Rpb24oKXthLnVucXVldWVkfHxzKCl9KSxhLnVucXVldWVkKysscC5hbHdheXMoZnVuY3Rpb24oKXtwLmFsd2F5cyhmdW5jdGlvbigpe2EudW5xdWV1ZWQtLSx3LnF1ZXVlKGUsImZ4IikubGVuZ3RofHxhLmVtcHR5LmZpcmUoKX0pfSkpO2ZvcihyIGluIHQpaWYoaT10W3JdLGl0LnRlc3QoaSkpe2lmKGRlbGV0ZSB0W3JdLG89b3x8InRvZ2dsZSI9PT1pLGk9PT0oZz8iaGlkZSI6InNob3ciKSl7aWYoInNob3ciIT09aXx8IXl8fHZvaWQgMD09PXlbcl0pY29udGludWU7Zz0hMH1kW3JdPXkmJnlbcl18fHcuc3R5bGUoZSxyKX1pZigodT0hdy5pc0VtcHR5T2JqZWN0KHQpKXx8IXcuaXNFbXB0eU9iamVjdChkKSl7ZiYmMT09PWUubm9kZVR5cGUmJihuLm92ZXJmbG93PVtoLm92ZXJmbG93LGgub3ZlcmZsb3dYLGgub3ZlcmZsb3dZXSxudWxsPT0obD15JiZ5LmRpc3BsYXkpJiYobD1KLmdldChlLCJkaXNwbGF5IikpLCJub25lIj09PShjPXcuY3NzKGUsImRpc3BsYXkiKSkmJihsP2M9bDooZmUoW2VdLCEwKSxsPWUuc3R5bGUuZGlzcGxheXx8bCxjPXcuY3NzKGUsImRpc3BsYXkiKSxmZShbZV0pKSksKCJpbmxpbmUiPT09Y3x8ImlubGluZS1ibG9jayI9PT1jJiZudWxsIT1sKSYmIm5vbmUiPT09dy5jc3MoZSwiZmxvYXQiKSYmKHV8fChwLmRvbmUoZnVuY3Rpb24oKXtoLmRpc3BsYXk9bH0pLG51bGw9PWwmJihjPWguZGlzcGxheSxsPSJub25lIj09PWM/IiI6YykpLGguZGlzcGxheT0iaW5saW5lLWJsb2NrIikpLG4ub3ZlcmZsb3cmJihoLm92ZXJmbG93PSJoaWRkZW4iLHAuYWx3YXlzKGZ1bmN0aW9uKCl7aC5vdmVyZmxvdz1uLm92ZXJmbG93WzBdLGgub3ZlcmZsb3dYPW4ub3ZlcmZsb3dbMV0saC5vdmVyZmxvd1k9bi5vdmVyZmxvd1syXX0pKSx1PSExO2ZvcihyIGluIGQpdXx8KHk/ImhpZGRlbiJpbiB5JiYoZz15LmhpZGRlbik6eT1KLmFjY2VzcyhlLCJmeHNob3ciLHtkaXNwbGF5Omx9KSxvJiYoeS5oaWRkZW49IWcpLGcmJmZlKFtlXSwhMCkscC5kb25lKGZ1bmN0aW9uKCl7Z3x8ZmUoW2VdKSxKLnJlbW92ZShlLCJmeHNob3ciKTtmb3IociBpbiBkKXcuc3R5bGUoZSxyLGRbcl0pfSkpLHU9bHQoZz95W3JdOjAscixwKSxyIGluIHl8fCh5W3JdPXUuc3RhcnQsZyYmKHUuZW5kPXUuc3RhcnQsdS5zdGFydD0wKSl9fWZ1bmN0aW9uIGZ0KGUsdCl7dmFyIG4scixpLG8sYTtmb3IobiBpbiBlKWlmKHI9RyhuKSxpPXRbcl0sbz1lW25dLEFycmF5LmlzQXJyYXkobykmJihpPW9bMV0sbz1lW25dPW9bMF0pLG4hPT1yJiYoZVtyXT1vLGRlbGV0ZSBlW25dKSwoYT13LmNzc0hvb2tzW3JdKSYmImV4cGFuZCJpbiBhKXtvPWEuZXhwYW5kKG8pLGRlbGV0ZSBlW3JdO2ZvcihuIGluIG8pbiBpbiBlfHwoZVtuXT1vW25dLHRbbl09aSl9ZWxzZSB0W3JdPWl9ZnVuY3Rpb24gcHQoZSx0LG4pe3ZhciByLGksbz0wLGE9cHQucHJlZmlsdGVycy5sZW5ndGgscz13LkRlZmVycmVkKCkuYWx3YXlzKGZ1bmN0aW9uKCl7ZGVsZXRlIHUuZWxlbX0pLHU9ZnVuY3Rpb24oKXtpZihpKXJldHVybiExO2Zvcih2YXIgdD1udHx8c3QoKSxuPU1hdGgubWF4KDAsbC5zdGFydFRpbWUrbC5kdXJhdGlvbi10KSxyPTEtKG4vbC5kdXJhdGlvbnx8MCksbz0wLGE9bC50d2VlbnMubGVuZ3RoO288YTtvKyspbC50d2VlbnNbb10ucnVuKHIpO3JldHVybiBzLm5vdGlmeVdpdGgoZSxbbCxyLG5dKSxyPDEmJmE/bjooYXx8cy5ub3RpZnlXaXRoKGUsW2wsMSwwXSkscy5yZXNvbHZlV2l0aChlLFtsXSksITEpfSxsPXMucHJvbWlzZSh7ZWxlbTplLHByb3BzOncuZXh0ZW5kKHt9LHQpLG9wdHM6dy5leHRlbmQoITAse3NwZWNpYWxFYXNpbmc6e30sZWFzaW5nOncuZWFzaW5nLl9kZWZhdWx0fSxuKSxvcmlnaW5hbFByb3BlcnRpZXM6dCxvcmlnaW5hbE9wdGlvbnM6bixzdGFydFRpbWU6bnR8fHN0KCksZHVyYXRpb246bi5kdXJhdGlvbix0d2VlbnM6W10sY3JlYXRlVHdlZW46ZnVuY3Rpb24odCxuKXt2YXIgcj13LlR3ZWVuKGUsbC5vcHRzLHQsbixsLm9wdHMuc3BlY2lhbEVhc2luZ1t0XXx8bC5vcHRzLmVhc2luZyk7cmV0dXJuIGwudHdlZW5zLnB1c2gocikscn0sc3RvcDpmdW5jdGlvbih0KXt2YXIgbj0wLHI9dD9sLnR3ZWVucy5sZW5ndGg6MDtpZihpKXJldHVybiB0aGlzO2ZvcihpPSEwO248cjtuKyspbC50d2VlbnNbbl0ucnVuKDEpO3JldHVybiB0PyhzLm5vdGlmeVdpdGgoZSxbbCwxLDBdKSxzLnJlc29sdmVXaXRoKGUsW2wsdF0pKTpzLnJlamVjdFdpdGgoZSxbbCx0XSksdGhpc319KSxjPWwucHJvcHM7Zm9yKGZ0KGMsbC5vcHRzLnNwZWNpYWxFYXNpbmcpO288YTtvKyspaWYocj1wdC5wcmVmaWx0ZXJzW29dLmNhbGwobCxlLGMsbC5vcHRzKSlyZXR1cm4gZyhyLnN0b3ApJiYody5fcXVldWVIb29rcyhsLmVsZW0sbC5vcHRzLnF1ZXVlKS5zdG9wPXIuc3RvcC5iaW5kKHIpKSxyO3JldHVybiB3Lm1hcChjLGx0LGwpLGcobC5vcHRzLnN0YXJ0KSYmbC5vcHRzLnN0YXJ0LmNhbGwoZSxsKSxsLnByb2dyZXNzKGwub3B0cy5wcm9ncmVzcykuZG9uZShsLm9wdHMuZG9uZSxsLm9wdHMuY29tcGxldGUpLmZhaWwobC5vcHRzLmZhaWwpLmFsd2F5cyhsLm9wdHMuYWx3YXlzKSx3LmZ4LnRpbWVyKHcuZXh0ZW5kKHUse2VsZW06ZSxhbmltOmwscXVldWU6bC5vcHRzLnF1ZXVlfSkpLGx9dy5BbmltYXRpb249dy5leHRlbmQocHQse3R3ZWVuZXJzOnsiKiI6W2Z1bmN0aW9uKGUsdCl7dmFyIG49dGhpcy5jcmVhdGVUd2VlbihlLHQpO3JldHVybiB1ZShuLmVsZW0sZSxpZS5leGVjKHQpLG4pLG59XX0sdHdlZW5lcjpmdW5jdGlvbihlLHQpe2coZSk/KHQ9ZSxlPVsiKiJdKTplPWUubWF0Y2goTSk7Zm9yKHZhciBuLHI9MCxpPWUubGVuZ3RoO3I8aTtyKyspbj1lW3JdLHB0LnR3ZWVuZXJzW25dPXB0LnR3ZWVuZXJzW25dfHxbXSxwdC50d2VlbmVyc1tuXS51bnNoaWZ0KHQpfSxwcmVmaWx0ZXJzOltjdF0scHJlZmlsdGVyOmZ1bmN0aW9uKGUsdCl7dD9wdC5wcmVmaWx0ZXJzLnVuc2hpZnQoZSk6cHQucHJlZmlsdGVycy5wdXNoKGUpfX0pLHcuc3BlZWQ9ZnVuY3Rpb24oZSx0LG4pe3ZhciByPWUmJiJvYmplY3QiPT10eXBlb2YgZT93LmV4dGVuZCh7fSxlKTp7Y29tcGxldGU6bnx8IW4mJnR8fGcoZSkmJmUsZHVyYXRpb246ZSxlYXNpbmc6biYmdHx8dCYmIWcodCkmJnR9O3JldHVybiB3LmZ4Lm9mZj9yLmR1cmF0aW9uPTA6Im51bWJlciIhPXR5cGVvZiByLmR1cmF0aW9uJiYoci5kdXJhdGlvbiBpbiB3LmZ4LnNwZWVkcz9yLmR1cmF0aW9uPXcuZnguc3BlZWRzW3IuZHVyYXRpb25dOnIuZHVyYXRpb249dy5meC5zcGVlZHMuX2RlZmF1bHQpLG51bGwhPXIucXVldWUmJiEwIT09ci5xdWV1ZXx8KHIucXVldWU9ImZ4Iiksci5vbGQ9ci5jb21wbGV0ZSxyLmNvbXBsZXRlPWZ1bmN0aW9uKCl7ZyhyLm9sZCkmJnIub2xkLmNhbGwodGhpcyksci5xdWV1ZSYmdy5kZXF1ZXVlKHRoaXMsci5xdWV1ZSl9LHJ9LHcuZm4uZXh0ZW5kKHtmYWRlVG86ZnVuY3Rpb24oZSx0LG4scil7cmV0dXJuIHRoaXMuZmlsdGVyKGFlKS5jc3MoIm9wYWNpdHkiLDApLnNob3coKS5lbmQoKS5hbmltYXRlKHtvcGFjaXR5OnR9LGUsbixyKX0sYW5pbWF0ZTpmdW5jdGlvbihlLHQsbixyKXt2YXIgaT13LmlzRW1wdHlPYmplY3QoZSksbz13LnNwZWVkKHQsbixyKSxhPWZ1bmN0aW9uKCl7dmFyIHQ9cHQodGhpcyx3LmV4dGVuZCh7fSxlKSxvKTsoaXx8Si5nZXQodGhpcywiZmluaXNoIikpJiZ0LnN0b3AoITApfTtyZXR1cm4gYS5maW5pc2g9YSxpfHwhMT09PW8ucXVldWU/dGhpcy5lYWNoKGEpOnRoaXMucXVldWUoby5xdWV1ZSxhKX0sc3RvcDpmdW5jdGlvbihlLHQsbil7dmFyIHI9ZnVuY3Rpb24oZSl7dmFyIHQ9ZS5zdG9wO2RlbGV0ZSBlLnN0b3AsdChuKX07cmV0dXJuInN0cmluZyIhPXR5cGVvZiBlJiYobj10LHQ9ZSxlPXZvaWQgMCksdCYmITEhPT1lJiZ0aGlzLnF1ZXVlKGV8fCJmeCIsW10pLHRoaXMuZWFjaChmdW5jdGlvbigpe3ZhciB0PSEwLGk9bnVsbCE9ZSYmZSsicXVldWVIb29rcyIsbz13LnRpbWVycyxhPUouZ2V0KHRoaXMpO2lmKGkpYVtpXSYmYVtpXS5zdG9wJiZyKGFbaV0pO2Vsc2UgZm9yKGkgaW4gYSlhW2ldJiZhW2ldLnN0b3AmJm90LnRlc3QoaSkmJnIoYVtpXSk7Zm9yKGk9by5sZW5ndGg7aS0tOylvW2ldLmVsZW0hPT10aGlzfHxudWxsIT1lJiZvW2ldLnF1ZXVlIT09ZXx8KG9baV0uYW5pbS5zdG9wKG4pLHQ9ITEsby5zcGxpY2UoaSwxKSk7IXQmJm58fHcuZGVxdWV1ZSh0aGlzLGUpfSl9LGZpbmlzaDpmdW5jdGlvbihlKXtyZXR1cm4hMSE9PWUmJihlPWV8fCJmeCIpLHRoaXMuZWFjaChmdW5jdGlvbigpe3ZhciB0LG49Si5nZXQodGhpcykscj1uW2UrInF1ZXVlIl0saT1uW2UrInF1ZXVlSG9va3MiXSxvPXcudGltZXJzLGE9cj9yLmxlbmd0aDowO2ZvcihuLmZpbmlzaD0hMCx3LnF1ZXVlKHRoaXMsZSxbXSksaSYmaS5zdG9wJiZpLnN0b3AuY2FsbCh0aGlzLCEwKSx0PW8ubGVuZ3RoO3QtLTspb1t0XS5lbGVtPT09dGhpcyYmb1t0XS5xdWV1ZT09PWUmJihvW3RdLmFuaW0uc3RvcCghMCksby5zcGxpY2UodCwxKSk7Zm9yKHQ9MDt0PGE7dCsrKXJbdF0mJnJbdF0uZmluaXNoJiZyW3RdLmZpbmlzaC5jYWxsKHRoaXMpO2RlbGV0ZSBuLmZpbmlzaH0pfX0pLHcuZWFjaChbInRvZ2dsZSIsInNob3ciLCJoaWRlIl0sZnVuY3Rpb24oZSx0KXt2YXIgbj13LmZuW3RdO3cuZm5bdF09ZnVuY3Rpb24oZSxyLGkpe3JldHVybiBudWxsPT1lfHwiYm9vbGVhbiI9PXR5cGVvZiBlP24uYXBwbHkodGhpcyxhcmd1bWVudHMpOnRoaXMuYW5pbWF0ZSh1dCh0LCEwKSxlLHIsaSl9fSksdy5lYWNoKHtzbGlkZURvd246dXQoInNob3ciKSxzbGlkZVVwOnV0KCJoaWRlIiksc2xpZGVUb2dnbGU6dXQoInRvZ2dsZSIpLGZhZGVJbjp7b3BhY2l0eToic2hvdyJ9LGZhZGVPdXQ6e29wYWNpdHk6ImhpZGUifSxmYWRlVG9nZ2xlOntvcGFjaXR5OiJ0b2dnbGUifX0sZnVuY3Rpb24oZSx0KXt3LmZuW2VdPWZ1bmN0aW9uKGUsbixyKXtyZXR1cm4gdGhpcy5hbmltYXRlKHQsZSxuLHIpfX0pLHcudGltZXJzPVtdLHcuZngudGljaz1mdW5jdGlvbigpe3ZhciBlLHQ9MCxuPXcudGltZXJzO2ZvcihudD1EYXRlLm5vdygpO3Q8bi5sZW5ndGg7dCsrKShlPW5bdF0pKCl8fG5bdF0hPT1lfHxuLnNwbGljZSh0LS0sMSk7bi5sZW5ndGh8fHcuZnguc3RvcCgpLG50PXZvaWQgMH0sdy5meC50aW1lcj1mdW5jdGlvbihlKXt3LnRpbWVycy5wdXNoKGUpLHcuZnguc3RhcnQoKX0sdy5meC5pbnRlcnZhbD0xMyx3LmZ4LnN0YXJ0PWZ1bmN0aW9uKCl7cnR8fChydD0hMCxhdCgpKX0sdy5meC5zdG9wPWZ1bmN0aW9uKCl7cnQ9bnVsbH0sdy5meC5zcGVlZHM9e3Nsb3c6NjAwLGZhc3Q6MjAwLF9kZWZhdWx0OjQwMH0sdy5mbi5kZWxheT1mdW5jdGlvbih0LG4pe3JldHVybiB0PXcuZng/dy5meC5zcGVlZHNbdF18fHQ6dCxuPW58fCJmeCIsdGhpcy5xdWV1ZShuLGZ1bmN0aW9uKG4scil7dmFyIGk9ZS5zZXRUaW1lb3V0KG4sdCk7ci5zdG9wPWZ1bmN0aW9uKCl7ZS5jbGVhclRpbWVvdXQoaSl9fSl9LGZ1bmN0aW9uKCl7dmFyIGU9ci5jcmVhdGVFbGVtZW50KCJpbnB1dCIpLHQ9ci5jcmVhdGVFbGVtZW50KCJzZWxlY3QiKS5hcHBlbmRDaGlsZChyLmNyZWF0ZUVsZW1lbnQoIm9wdGlvbiIpKTtlLnR5cGU9ImNoZWNrYm94IixoLmNoZWNrT249IiIhPT1lLnZhbHVlLGgub3B0U2VsZWN0ZWQ9dC5zZWxlY3RlZCwoZT1yLmNyZWF0ZUVsZW1lbnQoImlucHV0IikpLnZhbHVlPSJ0IixlLnR5cGU9InJhZGlvIixoLnJhZGlvVmFsdWU9InQiPT09ZS52YWx1ZX0oKTt2YXIgZHQsaHQ9dy5leHByLmF0dHJIYW5kbGU7dy5mbi5leHRlbmQoe2F0dHI6ZnVuY3Rpb24oZSx0KXtyZXR1cm4geih0aGlzLHcuYXR0cixlLHQsYXJndW1lbnRzLmxlbmd0aD4xKX0scmVtb3ZlQXR0cjpmdW5jdGlvbihlKXtyZXR1cm4gdGhpcy5lYWNoKGZ1bmN0aW9uKCl7dy5yZW1vdmVBdHRyKHRoaXMsZSl9KX19KSx3LmV4dGVuZCh7YXR0cjpmdW5jdGlvbihlLHQsbil7dmFyIHIsaSxvPWUubm9kZVR5cGU7aWYoMyE9PW8mJjghPT1vJiYyIT09bylyZXR1cm4idW5kZWZpbmVkIj09dHlwZW9mIGUuZ2V0QXR0cmlidXRlP3cucHJvcChlLHQsbik6KDE9PT1vJiZ3LmlzWE1MRG9jKGUpfHwoaT13LmF0dHJIb29rc1t0LnRvTG93ZXJDYXNlKCldfHwody5leHByLm1hdGNoLmJvb2wudGVzdCh0KT9kdDp2b2lkIDApKSx2b2lkIDAhPT1uP251bGw9PT1uP3ZvaWQgdy5yZW1vdmVBdHRyKGUsdCk6aSYmInNldCJpbiBpJiZ2b2lkIDAhPT0ocj1pLnNldChlLG4sdCkpP3I6KGUuc2V0QXR0cmlidXRlKHQsbisiIiksbik6aSYmImdldCJpbiBpJiZudWxsIT09KHI9aS5nZXQoZSx0KSk/cjpudWxsPT0ocj13LmZpbmQuYXR0cihlLHQpKT92b2lkIDA6cil9LGF0dHJIb29rczp7dHlwZTp7c2V0OmZ1bmN0aW9uKGUsdCl7aWYoIWgucmFkaW9WYWx1ZSYmInJhZGlvIj09PXQmJk4oZSwiaW5wdXQiKSl7dmFyIG49ZS52YWx1ZTtyZXR1cm4gZS5zZXRBdHRyaWJ1dGUoInR5cGUiLHQpLG4mJihlLnZhbHVlPW4pLHR9fX19LHJlbW92ZUF0dHI6ZnVuY3Rpb24oZSx0KXt2YXIgbixyPTAsaT10JiZ0Lm1hdGNoKE0pO2lmKGkmJjE9PT1lLm5vZGVUeXBlKXdoaWxlKG49aVtyKytdKWUucmVtb3ZlQXR0cmlidXRlKG4pfX0pLGR0PXtzZXQ6ZnVuY3Rpb24oZSx0LG4pe3JldHVybiExPT09dD93LnJlbW92ZUF0dHIoZSxuKTplLnNldEF0dHJpYnV0ZShuLG4pLG59fSx3LmVhY2gody5leHByLm1hdGNoLmJvb2wuc291cmNlLm1hdGNoKC9cdysvZyksZnVuY3Rpb24oZSx0KXt2YXIgbj1odFt0XXx8dy5maW5kLmF0dHI7aHRbdF09ZnVuY3Rpb24oZSx0LHIpe3ZhciBpLG8sYT10LnRvTG93ZXJDYXNlKCk7cmV0dXJuIHJ8fChvPWh0W2FdLGh0W2FdPWksaT1udWxsIT1uKGUsdCxyKT9hOm51bGwsaHRbYV09byksaX19KTt2YXIgZ3Q9L14oPzppbnB1dHxzZWxlY3R8dGV4dGFyZWF8YnV0dG9uKSQvaSx5dD0vXig/OmF8YXJlYSkkL2k7dy5mbi5leHRlbmQoe3Byb3A6ZnVuY3Rpb24oZSx0KXtyZXR1cm4geih0aGlzLHcucHJvcCxlLHQsYXJndW1lbnRzLmxlbmd0aD4xKX0scmVtb3ZlUHJvcDpmdW5jdGlvbihlKXtyZXR1cm4gdGhpcy5lYWNoKGZ1bmN0aW9uKCl7ZGVsZXRlIHRoaXNbdy5wcm9wRml4W2VdfHxlXX0pfX0pLHcuZXh0ZW5kKHtwcm9wOmZ1bmN0aW9uKGUsdCxuKXt2YXIgcixpLG89ZS5ub2RlVHlwZTtpZigzIT09byYmOCE9PW8mJjIhPT1vKXJldHVybiAxPT09byYmdy5pc1hNTERvYyhlKXx8KHQ9dy5wcm9wRml4W3RdfHx0LGk9dy5wcm9wSG9va3NbdF0pLHZvaWQgMCE9PW4/aSYmInNldCJpbiBpJiZ2b2lkIDAhPT0ocj1pLnNldChlLG4sdCkpP3I6ZVt0XT1uOmkmJiJnZXQiaW4gaSYmbnVsbCE9PShyPWkuZ2V0KGUsdCkpP3I6ZVt0XX0scHJvcEhvb2tzOnt0YWJJbmRleDp7Z2V0OmZ1bmN0aW9uKGUpe3ZhciB0PXcuZmluZC5hdHRyKGUsInRhYmluZGV4Iik7cmV0dXJuIHQ/cGFyc2VJbnQodCwxMCk6Z3QudGVzdChlLm5vZGVOYW1lKXx8eXQudGVzdChlLm5vZGVOYW1lKSYmZS5ocmVmPzA6LTF9fX0scHJvcEZpeDp7ImZvciI6Imh0bWxGb3IiLCJjbGFzcyI6ImNsYXNzTmFtZSJ9fSksaC5vcHRTZWxlY3RlZHx8KHcucHJvcEhvb2tzLnNlbGVjdGVkPXtnZXQ6ZnVuY3Rpb24oZSl7dmFyIHQ9ZS5wYXJlbnROb2RlO3JldHVybiB0JiZ0LnBhcmVudE5vZGUmJnQucGFyZW50Tm9kZS5zZWxlY3RlZEluZGV4LG51bGx9LHNldDpmdW5jdGlvbihlKXt2YXIgdD1lLnBhcmVudE5vZGU7dCYmKHQuc2VsZWN0ZWRJbmRleCx0LnBhcmVudE5vZGUmJnQucGFyZW50Tm9kZS5zZWxlY3RlZEluZGV4KX19KSx3LmVhY2goWyJ0YWJJbmRleCIsInJlYWRPbmx5IiwibWF4TGVuZ3RoIiwiY2VsbFNwYWNpbmciLCJjZWxsUGFkZGluZyIsInJvd1NwYW4iLCJjb2xTcGFuIiwidXNlTWFwIiwiZnJhbWVCb3JkZXIiLCJjb250ZW50RWRpdGFibGUiXSxmdW5jdGlvbigpe3cucHJvcEZpeFt0aGlzLnRvTG93ZXJDYXNlKCldPXRoaXN9KTtmdW5jdGlvbiB2dChlKXtyZXR1cm4oZS5tYXRjaChNKXx8W10pLmpvaW4oIiAiKX1mdW5jdGlvbiBtdChlKXtyZXR1cm4gZS5nZXRBdHRyaWJ1dGUmJmUuZ2V0QXR0cmlidXRlKCJjbGFzcyIpfHwiIn1mdW5jdGlvbiB4dChlKXtyZXR1cm4gQXJyYXkuaXNBcnJheShlKT9lOiJzdHJpbmciPT10eXBlb2YgZT9lLm1hdGNoKE0pfHxbXTpbXX13LmZuLmV4dGVuZCh7YWRkQ2xhc3M6ZnVuY3Rpb24oZSl7dmFyIHQsbixyLGksbyxhLHMsdT0wO2lmKGcoZSkpcmV0dXJuIHRoaXMuZWFjaChmdW5jdGlvbih0KXt3KHRoaXMpLmFkZENsYXNzKGUuY2FsbCh0aGlzLHQsbXQodGhpcykpKX0pO2lmKCh0PXh0KGUpKS5sZW5ndGgpd2hpbGUobj10aGlzW3UrK10paWYoaT1tdChuKSxyPTE9PT1uLm5vZGVUeXBlJiYiICIrdnQoaSkrIiAiKXthPTA7d2hpbGUobz10W2ErK10pci5pbmRleE9mKCIgIitvKyIgIik8MCYmKHIrPW8rIiAiKTtpIT09KHM9dnQocikpJiZuLnNldEF0dHJpYnV0ZSgiY2xhc3MiLHMpfXJldHVybiB0aGlzfSxyZW1vdmVDbGFzczpmdW5jdGlvbihlKXt2YXIgdCxuLHIsaSxvLGEscyx1PTA7aWYoZyhlKSlyZXR1cm4gdGhpcy5lYWNoKGZ1bmN0aW9uKHQpe3codGhpcykucmVtb3ZlQ2xhc3MoZS5jYWxsKHRoaXMsdCxtdCh0aGlzKSkpfSk7aWYoIWFyZ3VtZW50cy5sZW5ndGgpcmV0dXJuIHRoaXMuYXR0cigiY2xhc3MiLCIiKTtpZigodD14dChlKSkubGVuZ3RoKXdoaWxlKG49dGhpc1t1KytdKWlmKGk9bXQobikscj0xPT09bi5ub2RlVHlwZSYmIiAiK3Z0KGkpKyIgIil7YT0wO3doaWxlKG89dFthKytdKXdoaWxlKHIuaW5kZXhPZigiICIrbysiICIpPi0xKXI9ci5yZXBsYWNlKCIgIitvKyIgIiwiICIpO2khPT0ocz12dChyKSkmJm4uc2V0QXR0cmlidXRlKCJjbGFzcyIscyl9cmV0dXJuIHRoaXN9LHRvZ2dsZUNsYXNzOmZ1bmN0aW9uKGUsdCl7dmFyIG49dHlwZW9mIGUscj0ic3RyaW5nIj09PW58fEFycmF5LmlzQXJyYXkoZSk7cmV0dXJuImJvb2xlYW4iPT10eXBlb2YgdCYmcj90P3RoaXMuYWRkQ2xhc3MoZSk6dGhpcy5yZW1vdmVDbGFzcyhlKTpnKGUpP3RoaXMuZWFjaChmdW5jdGlvbihuKXt3KHRoaXMpLnRvZ2dsZUNsYXNzKGUuY2FsbCh0aGlzLG4sbXQodGhpcyksdCksdCl9KTp0aGlzLmVhY2goZnVuY3Rpb24oKXt2YXIgdCxpLG8sYTtpZihyKXtpPTAsbz13KHRoaXMpLGE9eHQoZSk7d2hpbGUodD1hW2krK10pby5oYXNDbGFzcyh0KT9vLnJlbW92ZUNsYXNzKHQpOm8uYWRkQ2xhc3ModCl9ZWxzZSB2b2lkIDAhPT1lJiYiYm9vbGVhbiIhPT1ufHwoKHQ9bXQodGhpcykpJiZKLnNldCh0aGlzLCJfX2NsYXNzTmFtZV9fIix0KSx0aGlzLnNldEF0dHJpYnV0ZSYmdGhpcy5zZXRBdHRyaWJ1dGUoImNsYXNzIix0fHwhMT09PWU/IiI6Si5nZXQodGhpcywiX19jbGFzc05hbWVfXyIpfHwiIikpfSl9LGhhc0NsYXNzOmZ1bmN0aW9uKGUpe3ZhciB0LG4scj0wO3Q9IiAiK2UrIiAiO3doaWxlKG49dGhpc1tyKytdKWlmKDE9PT1uLm5vZGVUeXBlJiYoIiAiK3Z0KG10KG4pKSsiICIpLmluZGV4T2YodCk+LTEpcmV0dXJuITA7cmV0dXJuITF9fSk7dmFyIGJ0PS9cci9nO3cuZm4uZXh0ZW5kKHt2YWw6ZnVuY3Rpb24oZSl7dmFyIHQsbixyLGk9dGhpc1swXTt7aWYoYXJndW1lbnRzLmxlbmd0aClyZXR1cm4gcj1nKGUpLHRoaXMuZWFjaChmdW5jdGlvbihuKXt2YXIgaTsxPT09dGhpcy5ub2RlVHlwZSYmKG51bGw9PShpPXI/ZS5jYWxsKHRoaXMsbix3KHRoaXMpLnZhbCgpKTplKT9pPSIiOiJudW1iZXIiPT10eXBlb2YgaT9pKz0iIjpBcnJheS5pc0FycmF5KGkpJiYoaT13Lm1hcChpLGZ1bmN0aW9uKGUpe3JldHVybiBudWxsPT1lPyIiOmUrIiJ9KSksKHQ9dy52YWxIb29rc1t0aGlzLnR5cGVdfHx3LnZhbEhvb2tzW3RoaXMubm9kZU5hbWUudG9Mb3dlckNhc2UoKV0pJiYic2V0ImluIHQmJnZvaWQgMCE9PXQuc2V0KHRoaXMsaSwidmFsdWUiKXx8KHRoaXMudmFsdWU9aSkpfSk7aWYoaSlyZXR1cm4odD13LnZhbEhvb2tzW2kudHlwZV18fHcudmFsSG9va3NbaS5ub2RlTmFtZS50b0xvd2VyQ2FzZSgpXSkmJiJnZXQiaW4gdCYmdm9pZCAwIT09KG49dC5nZXQoaSwidmFsdWUiKSk/bjoic3RyaW5nIj09dHlwZW9mKG49aS52YWx1ZSk/bi5yZXBsYWNlKGJ0LCIiKTpudWxsPT1uPyIiOm59fX0pLHcuZXh0ZW5kKHt2YWxIb29rczp7b3B0aW9uOntnZXQ6ZnVuY3Rpb24oZSl7dmFyIHQ9dy5maW5kLmF0dHIoZSwidmFsdWUiKTtyZXR1cm4gbnVsbCE9dD90OnZ0KHcudGV4dChlKSl9fSxzZWxlY3Q6e2dldDpmdW5jdGlvbihlKXt2YXIgdCxuLHIsaT1lLm9wdGlvbnMsbz1lLnNlbGVjdGVkSW5kZXgsYT0ic2VsZWN0LW9uZSI9PT1lLnR5cGUscz1hP251bGw6W10sdT1hP28rMTppLmxlbmd0aDtmb3Iocj1vPDA/dTphP286MDtyPHU7cisrKWlmKCgobj1pW3JdKS5zZWxlY3RlZHx8cj09PW8pJiYhbi5kaXNhYmxlZCYmKCFuLnBhcmVudE5vZGUuZGlzYWJsZWR8fCFOKG4ucGFyZW50Tm9kZSwib3B0Z3JvdXAiKSkpe2lmKHQ9dyhuKS52YWwoKSxhKXJldHVybiB0O3MucHVzaCh0KX1yZXR1cm4gc30sc2V0OmZ1bmN0aW9uKGUsdCl7dmFyIG4scixpPWUub3B0aW9ucyxvPXcubWFrZUFycmF5KHQpLGE9aS5sZW5ndGg7d2hpbGUoYS0tKSgocj1pW2FdKS5zZWxlY3RlZD13LmluQXJyYXkody52YWxIb29rcy5vcHRpb24uZ2V0KHIpLG8pPi0xKSYmKG49ITApO3JldHVybiBufHwoZS5zZWxlY3RlZEluZGV4PS0xKSxvfX19fSksdy5lYWNoKFsicmFkaW8iLCJjaGVja2JveCJdLGZ1bmN0aW9uKCl7dy52YWxIb29rc1t0aGlzXT17c2V0OmZ1bmN0aW9uKGUsdCl7aWYoQXJyYXkuaXNBcnJheSh0KSlyZXR1cm4gZS5jaGVja2VkPXcuaW5BcnJheSh3KGUpLnZhbCgpLHQpPi0xfX0saC5jaGVja09ufHwody52YWxIb29rc1t0aGlzXS5nZXQ9ZnVuY3Rpb24oZSl7cmV0dXJuIG51bGw9PT1lLmdldEF0dHJpYnV0ZSgidmFsdWUiKT8ib24iOmUudmFsdWV9KX0pLGguZm9jdXNpbj0ib25mb2N1c2luImluIGU7dmFyIHd0PS9eKD86Zm9jdXNpbmZvY3VzfGZvY3Vzb3V0Ymx1cikkLyxUdD1mdW5jdGlvbihlKXtlLnN0b3BQcm9wYWdhdGlvbigpfTt3LmV4dGVuZCh3LmV2ZW50LHt0cmlnZ2VyOmZ1bmN0aW9uKHQsbixpLG8pe3ZhciBhLHMsdSxsLGMscCxkLGgsdj1baXx8cl0sbT1mLmNhbGwodCwidHlwZSIpP3QudHlwZTp0LHg9Zi5jYWxsKHQsIm5hbWVzcGFjZSIpP3QubmFtZXNwYWNlLnNwbGl0KCIuIik6W107aWYocz1oPXU9aT1pfHxyLDMhPT1pLm5vZGVUeXBlJiY4IT09aS5ub2RlVHlwZSYmIXd0LnRlc3QobSt3LmV2ZW50LnRyaWdnZXJlZCkmJihtLmluZGV4T2YoIi4iKT4tMSYmKG09KHg9bS5zcGxpdCgiLiIpKS5zaGlmdCgpLHguc29ydCgpKSxjPW0uaW5kZXhPZigiOiIpPDAmJiJvbiIrbSx0PXRbdy5leHBhbmRvXT90Om5ldyB3LkV2ZW50KG0sIm9iamVjdCI9PXR5cGVvZiB0JiZ0KSx0LmlzVHJpZ2dlcj1vPzI6Myx0Lm5hbWVzcGFjZT14LmpvaW4oIi4iKSx0LnJuYW1lc3BhY2U9dC5uYW1lc3BhY2U/bmV3IFJlZ0V4cCgiKF58XFwuKSIreC5qb2luKCJcXC4oPzouKlxcLnwpIikrIihcXC58JCkiKTpudWxsLHQucmVzdWx0PXZvaWQgMCx0LnRhcmdldHx8KHQudGFyZ2V0PWkpLG49bnVsbD09bj9bdF06dy5tYWtlQXJyYXkobixbdF0pLGQ9dy5ldmVudC5zcGVjaWFsW21dfHx7fSxvfHwhZC50cmlnZ2VyfHwhMSE9PWQudHJpZ2dlci5hcHBseShpLG4pKSl7aWYoIW8mJiFkLm5vQnViYmxlJiYheShpKSl7Zm9yKGw9ZC5kZWxlZ2F0ZVR5cGV8fG0sd3QudGVzdChsK20pfHwocz1zLnBhcmVudE5vZGUpO3M7cz1zLnBhcmVudE5vZGUpdi5wdXNoKHMpLHU9czt1PT09KGkub3duZXJEb2N1bWVudHx8cikmJnYucHVzaCh1LmRlZmF1bHRWaWV3fHx1LnBhcmVudFdpbmRvd3x8ZSl9YT0wO3doaWxlKChzPXZbYSsrXSkmJiF0LmlzUHJvcGFnYXRpb25TdG9wcGVkKCkpaD1zLHQudHlwZT1hPjE/bDpkLmJpbmRUeXBlfHxtLChwPShKLmdldChzLCJldmVudHMiKXx8e30pW3QudHlwZV0mJkouZ2V0KHMsImhhbmRsZSIpKSYmcC5hcHBseShzLG4pLChwPWMmJnNbY10pJiZwLmFwcGx5JiZZKHMpJiYodC5yZXN1bHQ9cC5hcHBseShzLG4pLCExPT09dC5yZXN1bHQmJnQucHJldmVudERlZmF1bHQoKSk7cmV0dXJuIHQudHlwZT1tLG98fHQuaXNEZWZhdWx0UHJldmVudGVkKCl8fGQuX2RlZmF1bHQmJiExIT09ZC5fZGVmYXVsdC5hcHBseSh2LnBvcCgpLG4pfHwhWShpKXx8YyYmZyhpW21dKSYmIXkoaSkmJigodT1pW2NdKSYmKGlbY109bnVsbCksdy5ldmVudC50cmlnZ2VyZWQ9bSx0LmlzUHJvcGFnYXRpb25TdG9wcGVkKCkmJmguYWRkRXZlbnRMaXN0ZW5lcihtLFR0KSxpW21dKCksdC5pc1Byb3BhZ2F0aW9uU3RvcHBlZCgpJiZoLnJlbW92ZUV2ZW50TGlzdGVuZXIobSxUdCksdy5ldmVudC50cmlnZ2VyZWQ9dm9pZCAwLHUmJihpW2NdPXUpKSx0LnJlc3VsdH19LHNpbXVsYXRlOmZ1bmN0aW9uKGUsdCxuKXt2YXIgcj13LmV4dGVuZChuZXcgdy5FdmVudCxuLHt0eXBlOmUsaXNTaW11bGF0ZWQ6ITB9KTt3LmV2ZW50LnRyaWdnZXIocixudWxsLHQpfX0pLHcuZm4uZXh0ZW5kKHt0cmlnZ2VyOmZ1bmN0aW9uKGUsdCl7cmV0dXJuIHRoaXMuZWFjaChmdW5jdGlvbigpe3cuZXZlbnQudHJpZ2dlcihlLHQsdGhpcyl9KX0sdHJpZ2dlckhhbmRsZXI6ZnVuY3Rpb24oZSx0KXt2YXIgbj10aGlzWzBdO2lmKG4pcmV0dXJuIHcuZXZlbnQudHJpZ2dlcihlLHQsbiwhMCl9fSksaC5mb2N1c2lufHx3LmVhY2goe2ZvY3VzOiJmb2N1c2luIixibHVyOiJmb2N1c291dCJ9LGZ1bmN0aW9uKGUsdCl7dmFyIG49ZnVuY3Rpb24oZSl7dy5ldmVudC5zaW11bGF0ZSh0LGUudGFyZ2V0LHcuZXZlbnQuZml4KGUpKX07dy5ldmVudC5zcGVjaWFsW3RdPXtzZXR1cDpmdW5jdGlvbigpe3ZhciByPXRoaXMub3duZXJEb2N1bWVudHx8dGhpcyxpPUouYWNjZXNzKHIsdCk7aXx8ci5hZGRFdmVudExpc3RlbmVyKGUsbiwhMCksSi5hY2Nlc3Mocix0LChpfHwwKSsxKX0sdGVhcmRvd246ZnVuY3Rpb24oKXt2YXIgcj10aGlzLm93bmVyRG9jdW1lbnR8fHRoaXMsaT1KLmFjY2VzcyhyLHQpLTE7aT9KLmFjY2VzcyhyLHQsaSk6KHIucmVtb3ZlRXZlbnRMaXN0ZW5lcihlLG4sITApLEoucmVtb3ZlKHIsdCkpfX19KTt2YXIgQ3Q9ZS5sb2NhdGlvbixFdD1EYXRlLm5vdygpLGt0PS9cPy87dy5wYXJzZVhNTD1mdW5jdGlvbih0KXt2YXIgbjtpZighdHx8InN0cmluZyIhPXR5cGVvZiB0KXJldHVybiBudWxsO3RyeXtuPShuZXcgZS5ET01QYXJzZXIpLnBhcnNlRnJvbVN0cmluZyh0LCJ0ZXh0L3htbCIpfWNhdGNoKGUpe249dm9pZCAwfXJldHVybiBuJiYhbi5nZXRFbGVtZW50c0J5VGFnTmFtZSgicGFyc2VyZXJyb3IiKS5sZW5ndGh8fHcuZXJyb3IoIkludmFsaWQgWE1MOiAiK3QpLG59O3ZhciBTdD0vXFtcXSQvLER0PS9ccj9cbi9nLE50PS9eKD86c3VibWl0fGJ1dHRvbnxpbWFnZXxyZXNldHxmaWxlKSQvaSxBdD0vXig/OmlucHV0fHNlbGVjdHx0ZXh0YXJlYXxrZXlnZW4pL2k7ZnVuY3Rpb24ganQoZSx0LG4scil7dmFyIGk7aWYoQXJyYXkuaXNBcnJheSh0KSl3LmVhY2godCxmdW5jdGlvbih0LGkpe258fFN0LnRlc3QoZSk/cihlLGkpOmp0KGUrIlsiKygib2JqZWN0Ij09dHlwZW9mIGkmJm51bGwhPWk/dDoiIikrIl0iLGksbixyKX0pO2Vsc2UgaWYobnx8Im9iamVjdCIhPT14KHQpKXIoZSx0KTtlbHNlIGZvcihpIGluIHQpanQoZSsiWyIraSsiXSIsdFtpXSxuLHIpfXcucGFyYW09ZnVuY3Rpb24oZSx0KXt2YXIgbixyPVtdLGk9ZnVuY3Rpb24oZSx0KXt2YXIgbj1nKHQpP3QoKTp0O3Jbci5sZW5ndGhdPWVuY29kZVVSSUNvbXBvbmVudChlKSsiPSIrZW5jb2RlVVJJQ29tcG9uZW50KG51bGw9PW4/IiI6bil9O2lmKEFycmF5LmlzQXJyYXkoZSl8fGUuanF1ZXJ5JiYhdy5pc1BsYWluT2JqZWN0KGUpKXcuZWFjaChlLGZ1bmN0aW9uKCl7aSh0aGlzLm5hbWUsdGhpcy52YWx1ZSl9KTtlbHNlIGZvcihuIGluIGUpanQobixlW25dLHQsaSk7cmV0dXJuIHIuam9pbigiJiIpfSx3LmZuLmV4dGVuZCh7c2VyaWFsaXplOmZ1bmN0aW9uKCl7cmV0dXJuIHcucGFyYW0odGhpcy5zZXJpYWxpemVBcnJheSgpKX0sc2VyaWFsaXplQXJyYXk6ZnVuY3Rpb24oKXtyZXR1cm4gdGhpcy5tYXAoZnVuY3Rpb24oKXt2YXIgZT13LnByb3AodGhpcywiZWxlbWVudHMiKTtyZXR1cm4gZT93Lm1ha2VBcnJheShlKTp0aGlzfSkuZmlsdGVyKGZ1bmN0aW9uKCl7dmFyIGU9dGhpcy50eXBlO3JldHVybiB0aGlzLm5hbWUmJiF3KHRoaXMpLmlzKCI6ZGlzYWJsZWQiKSYmQXQudGVzdCh0aGlzLm5vZGVOYW1lKSYmIU50LnRlc3QoZSkmJih0aGlzLmNoZWNrZWR8fCFwZS50ZXN0KGUpKX0pLm1hcChmdW5jdGlvbihlLHQpe3ZhciBuPXcodGhpcykudmFsKCk7cmV0dXJuIG51bGw9PW4/bnVsbDpBcnJheS5pc0FycmF5KG4pP3cubWFwKG4sZnVuY3Rpb24oZSl7cmV0dXJue25hbWU6dC5uYW1lLHZhbHVlOmUucmVwbGFjZShEdCwiXHJcbiIpfX0pOntuYW1lOnQubmFtZSx2YWx1ZTpuLnJlcGxhY2UoRHQsIlxyXG4iKX19KS5nZXQoKX19KTt2YXIgcXQ9LyUyMC9nLEx0PS8jLiokLyxIdD0vKFs/Jl0pXz1bXiZdKi8sT3Q9L14oLio/KTpbIFx0XSooW15cclxuXSopJC9nbSxQdD0vXig/OmFib3V0fGFwcHxhcHAtc3RvcmFnZXwuKy1leHRlbnNpb258ZmlsZXxyZXN8d2lkZ2V0KTokLyxNdD0vXig/OkdFVHxIRUFEKSQvLFJ0PS9eXC9cLy8sSXQ9e30sV3Q9e30sJHQ9IiovIi5jb25jYXQoIioiKSxCdD1yLmNyZWF0ZUVsZW1lbnQoImEiKTtCdC5ocmVmPUN0LmhyZWY7ZnVuY3Rpb24gRnQoZSl7cmV0dXJuIGZ1bmN0aW9uKHQsbil7InN0cmluZyIhPXR5cGVvZiB0JiYobj10LHQ9IioiKTt2YXIgcixpPTAsbz10LnRvTG93ZXJDYXNlKCkubWF0Y2goTSl8fFtdO2lmKGcobikpd2hpbGUocj1vW2krK10pIisiPT09clswXT8ocj1yLnNsaWNlKDEpfHwiKiIsKGVbcl09ZVtyXXx8W10pLnVuc2hpZnQobikpOihlW3JdPWVbcl18fFtdKS5wdXNoKG4pfX1mdW5jdGlvbiBfdChlLHQsbixyKXt2YXIgaT17fSxvPWU9PT1XdDtmdW5jdGlvbiBhKHMpe3ZhciB1O3JldHVybiBpW3NdPSEwLHcuZWFjaChlW3NdfHxbXSxmdW5jdGlvbihlLHMpe3ZhciBsPXModCxuLHIpO3JldHVybiJzdHJpbmciIT10eXBlb2YgbHx8b3x8aVtsXT9vPyEodT1sKTp2b2lkIDA6KHQuZGF0YVR5cGVzLnVuc2hpZnQobCksYShsKSwhMSl9KSx1fXJldHVybiBhKHQuZGF0YVR5cGVzWzBdKXx8IWlbIioiXSYmYSgiKiIpfWZ1bmN0aW9uIHp0KGUsdCl7dmFyIG4scixpPXcuYWpheFNldHRpbmdzLmZsYXRPcHRpb25zfHx7fTtmb3IobiBpbiB0KXZvaWQgMCE9PXRbbl0mJigoaVtuXT9lOnJ8fChyPXt9KSlbbl09dFtuXSk7cmV0dXJuIHImJncuZXh0ZW5kKCEwLGUsciksZX1mdW5jdGlvbiBYdChlLHQsbil7dmFyIHIsaSxvLGEscz1lLmNvbnRlbnRzLHU9ZS5kYXRhVHlwZXM7d2hpbGUoIioiPT09dVswXSl1LnNoaWZ0KCksdm9pZCAwPT09ciYmKHI9ZS5taW1lVHlwZXx8dC5nZXRSZXNwb25zZUhlYWRlcigiQ29udGVudC1UeXBlIikpO2lmKHIpZm9yKGkgaW4gcylpZihzW2ldJiZzW2ldLnRlc3Qocikpe3UudW5zaGlmdChpKTticmVha31pZih1WzBdaW4gbilvPXVbMF07ZWxzZXtmb3IoaSBpbiBuKXtpZighdVswXXx8ZS5jb252ZXJ0ZXJzW2krIiAiK3VbMF1dKXtvPWk7YnJlYWt9YXx8KGE9aSl9bz1vfHxhfWlmKG8pcmV0dXJuIG8hPT11WzBdJiZ1LnVuc2hpZnQobyksbltvXX1mdW5jdGlvbiBVdChlLHQsbixyKXt2YXIgaSxvLGEscyx1LGw9e30sYz1lLmRhdGFUeXBlcy5zbGljZSgpO2lmKGNbMV0pZm9yKGEgaW4gZS5jb252ZXJ0ZXJzKWxbYS50b0xvd2VyQ2FzZSgpXT1lLmNvbnZlcnRlcnNbYV07bz1jLnNoaWZ0KCk7d2hpbGUobylpZihlLnJlc3BvbnNlRmllbGRzW29dJiYobltlLnJlc3BvbnNlRmllbGRzW29dXT10KSwhdSYmciYmZS5kYXRhRmlsdGVyJiYodD1lLmRhdGFGaWx0ZXIodCxlLmRhdGFUeXBlKSksdT1vLG89Yy5zaGlmdCgpKWlmKCIqIj09PW8pbz11O2Vsc2UgaWYoIioiIT09dSYmdSE9PW8pe2lmKCEoYT1sW3UrIiAiK29dfHxsWyIqICIrb10pKWZvcihpIGluIGwpaWYoKHM9aS5zcGxpdCgiICIpKVsxXT09PW8mJihhPWxbdSsiICIrc1swXV18fGxbIiogIitzWzBdXSkpeyEwPT09YT9hPWxbaV06ITAhPT1sW2ldJiYobz1zWzBdLGMudW5zaGlmdChzWzFdKSk7YnJlYWt9aWYoITAhPT1hKWlmKGEmJmVbInRocm93cyJdKXQ9YSh0KTtlbHNlIHRyeXt0PWEodCl9Y2F0Y2goZSl7cmV0dXJue3N0YXRlOiJwYXJzZXJlcnJvciIsZXJyb3I6YT9lOiJObyBjb252ZXJzaW9uIGZyb20gIit1KyIgdG8gIitvfX19cmV0dXJue3N0YXRlOiJzdWNjZXNzIixkYXRhOnR9fXcuZXh0ZW5kKHthY3RpdmU6MCxsYXN0TW9kaWZpZWQ6e30sZXRhZzp7fSxhamF4U2V0dGluZ3M6e3VybDpDdC5ocmVmLHR5cGU6IkdFVCIsaXNMb2NhbDpQdC50ZXN0KEN0LnByb3RvY29sKSxnbG9iYWw6ITAscHJvY2Vzc0RhdGE6ITAsYXN5bmM6ITAsY29udGVudFR5cGU6ImFwcGxpY2F0aW9uL3gtd3d3LWZvcm0tdXJsZW5jb2RlZDsgY2hhcnNldD1VVEYtOCIsYWNjZXB0czp7IioiOiR0LHRleHQ6InRleHQvcGxhaW4iLGh0bWw6InRleHQvaHRtbCIseG1sOiJhcHBsaWNhdGlvbi94bWwsIHRleHQveG1sIixqc29uOiJhcHBsaWNhdGlvbi9qc29uLCB0ZXh0L2phdmFzY3JpcHQifSxjb250ZW50czp7eG1sOi9cYnhtbFxiLyxodG1sOi9cYmh0bWwvLGpzb246L1xianNvblxiL30scmVzcG9uc2VGaWVsZHM6e3htbDoicmVzcG9uc2VYTUwiLHRleHQ6InJlc3BvbnNlVGV4dCIsanNvbjoicmVzcG9uc2VKU09OIn0sY29udmVydGVyczp7IiogdGV4dCI6U3RyaW5nLCJ0ZXh0IGh0bWwiOiEwLCJ0ZXh0IGpzb24iOkpTT04ucGFyc2UsInRleHQgeG1sIjp3LnBhcnNlWE1MfSxmbGF0T3B0aW9uczp7dXJsOiEwLGNvbnRleHQ6ITB9fSxhamF4U2V0dXA6ZnVuY3Rpb24oZSx0KXtyZXR1cm4gdD96dCh6dChlLHcuYWpheFNldHRpbmdzKSx0KTp6dCh3LmFqYXhTZXR0aW5ncyxlKX0sYWpheFByZWZpbHRlcjpGdChJdCksYWpheFRyYW5zcG9ydDpGdChXdCksYWpheDpmdW5jdGlvbih0LG4peyJvYmplY3QiPT10eXBlb2YgdCYmKG49dCx0PXZvaWQgMCksbj1ufHx7fTt2YXIgaSxvLGEscyx1LGwsYyxmLHAsZCxoPXcuYWpheFNldHVwKHt9LG4pLGc9aC5jb250ZXh0fHxoLHk9aC5jb250ZXh0JiYoZy5ub2RlVHlwZXx8Zy5qcXVlcnkpP3coZyk6dy5ldmVudCx2PXcuRGVmZXJyZWQoKSxtPXcuQ2FsbGJhY2tzKCJvbmNlIG1lbW9yeSIpLHg9aC5zdGF0dXNDb2RlfHx7fSxiPXt9LFQ9e30sQz0iY2FuY2VsZWQiLEU9e3JlYWR5U3RhdGU6MCxnZXRSZXNwb25zZUhlYWRlcjpmdW5jdGlvbihlKXt2YXIgdDtpZihjKXtpZighcyl7cz17fTt3aGlsZSh0PU90LmV4ZWMoYSkpc1t0WzFdLnRvTG93ZXJDYXNlKCldPXRbMl19dD1zW2UudG9Mb3dlckNhc2UoKV19cmV0dXJuIG51bGw9PXQ/bnVsbDp0fSxnZXRBbGxSZXNwb25zZUhlYWRlcnM6ZnVuY3Rpb24oKXtyZXR1cm4gYz9hOm51bGx9LHNldFJlcXVlc3RIZWFkZXI6ZnVuY3Rpb24oZSx0KXtyZXR1cm4gbnVsbD09YyYmKGU9VFtlLnRvTG93ZXJDYXNlKCldPVRbZS50b0xvd2VyQ2FzZSgpXXx8ZSxiW2VdPXQpLHRoaXN9LG92ZXJyaWRlTWltZVR5cGU6ZnVuY3Rpb24oZSl7cmV0dXJuIG51bGw9PWMmJihoLm1pbWVUeXBlPWUpLHRoaXN9LHN0YXR1c0NvZGU6ZnVuY3Rpb24oZSl7dmFyIHQ7aWYoZSlpZihjKUUuYWx3YXlzKGVbRS5zdGF0dXNdKTtlbHNlIGZvcih0IGluIGUpeFt0XT1beFt0XSxlW3RdXTtyZXR1cm4gdGhpc30sYWJvcnQ6ZnVuY3Rpb24oZSl7dmFyIHQ9ZXx8QztyZXR1cm4gaSYmaS5hYm9ydCh0KSxrKDAsdCksdGhpc319O2lmKHYucHJvbWlzZShFKSxoLnVybD0oKHR8fGgudXJsfHxDdC5ocmVmKSsiIikucmVwbGFjZShSdCxDdC5wcm90b2NvbCsiLy8iKSxoLnR5cGU9bi5tZXRob2R8fG4udHlwZXx8aC5tZXRob2R8fGgudHlwZSxoLmRhdGFUeXBlcz0oaC5kYXRhVHlwZXx8IioiKS50b0xvd2VyQ2FzZSgpLm1hdGNoKE0pfHxbIiJdLG51bGw9PWguY3Jvc3NEb21haW4pe2w9ci5jcmVhdGVFbGVtZW50KCJhIik7dHJ5e2wuaHJlZj1oLnVybCxsLmhyZWY9bC5ocmVmLGguY3Jvc3NEb21haW49QnQucHJvdG9jb2wrIi8vIitCdC5ob3N0IT1sLnByb3RvY29sKyIvLyIrbC5ob3N0fWNhdGNoKGUpe2guY3Jvc3NEb21haW49ITB9fWlmKGguZGF0YSYmaC5wcm9jZXNzRGF0YSYmInN0cmluZyIhPXR5cGVvZiBoLmRhdGEmJihoLmRhdGE9dy5wYXJhbShoLmRhdGEsaC50cmFkaXRpb25hbCkpLF90KEl0LGgsbixFKSxjKXJldHVybiBFOyhmPXcuZXZlbnQmJmguZ2xvYmFsKSYmMD09dy5hY3RpdmUrKyYmdy5ldmVudC50cmlnZ2VyKCJhamF4U3RhcnQiKSxoLnR5cGU9aC50eXBlLnRvVXBwZXJDYXNlKCksaC5oYXNDb250ZW50PSFNdC50ZXN0KGgudHlwZSksbz1oLnVybC5yZXBsYWNlKEx0LCIiKSxoLmhhc0NvbnRlbnQ/aC5kYXRhJiZoLnByb2Nlc3NEYXRhJiYwPT09KGguY29udGVudFR5cGV8fCIiKS5pbmRleE9mKCJhcHBsaWNhdGlvbi94LXd3dy1mb3JtLXVybGVuY29kZWQiKSYmKGguZGF0YT1oLmRhdGEucmVwbGFjZShxdCwiKyIpKTooZD1oLnVybC5zbGljZShvLmxlbmd0aCksaC5kYXRhJiYoaC5wcm9jZXNzRGF0YXx8InN0cmluZyI9PXR5cGVvZiBoLmRhdGEpJiYobys9KGt0LnRlc3Qobyk/IiYiOiI/IikraC5kYXRhLGRlbGV0ZSBoLmRhdGEpLCExPT09aC5jYWNoZSYmKG89by5yZXBsYWNlKEh0LCIkMSIpLGQ9KGt0LnRlc3Qobyk/IiYiOiI/IikrIl89IitFdCsrK2QpLGgudXJsPW8rZCksaC5pZk1vZGlmaWVkJiYody5sYXN0TW9kaWZpZWRbb10mJkUuc2V0UmVxdWVzdEhlYWRlcigiSWYtTW9kaWZpZWQtU2luY2UiLHcubGFzdE1vZGlmaWVkW29dKSx3LmV0YWdbb10mJkUuc2V0UmVxdWVzdEhlYWRlcigiSWYtTm9uZS1NYXRjaCIsdy5ldGFnW29dKSksKGguZGF0YSYmaC5oYXNDb250ZW50JiYhMSE9PWguY29udGVudFR5cGV8fG4uY29udGVudFR5cGUpJiZFLnNldFJlcXVlc3RIZWFkZXIoIkNvbnRlbnQtVHlwZSIsaC5jb250ZW50VHlwZSksRS5zZXRSZXF1ZXN0SGVhZGVyKCJBY2NlcHQiLGguZGF0YVR5cGVzWzBdJiZoLmFjY2VwdHNbaC5kYXRhVHlwZXNbMF1dP2guYWNjZXB0c1toLmRhdGFUeXBlc1swXV0rKCIqIiE9PWguZGF0YVR5cGVzWzBdPyIsICIrJHQrIjsgcT0wLjAxIjoiIik6aC5hY2NlcHRzWyIqIl0pO2ZvcihwIGluIGguaGVhZGVycylFLnNldFJlcXVlc3RIZWFkZXIocCxoLmhlYWRlcnNbcF0pO2lmKGguYmVmb3JlU2VuZCYmKCExPT09aC5iZWZvcmVTZW5kLmNhbGwoZyxFLGgpfHxjKSlyZXR1cm4gRS5hYm9ydCgpO2lmKEM9ImFib3J0IixtLmFkZChoLmNvbXBsZXRlKSxFLmRvbmUoaC5zdWNjZXNzKSxFLmZhaWwoaC5lcnJvciksaT1fdChXdCxoLG4sRSkpe2lmKEUucmVhZHlTdGF0ZT0xLGYmJnkudHJpZ2dlcigiYWpheFNlbmQiLFtFLGhdKSxjKXJldHVybiBFO2guYXN5bmMmJmgudGltZW91dD4wJiYodT1lLnNldFRpbWVvdXQoZnVuY3Rpb24oKXtFLmFib3J0KCJ0aW1lb3V0Iil9LGgudGltZW91dCkpO3RyeXtjPSExLGkuc2VuZChiLGspfWNhdGNoKGUpe2lmKGMpdGhyb3cgZTtrKC0xLGUpfX1lbHNlIGsoLTEsIk5vIFRyYW5zcG9ydCIpO2Z1bmN0aW9uIGsodCxuLHIscyl7dmFyIGwscCxkLGIsVCxDPW47Y3x8KGM9ITAsdSYmZS5jbGVhclRpbWVvdXQodSksaT12b2lkIDAsYT1zfHwiIixFLnJlYWR5U3RhdGU9dD4wPzQ6MCxsPXQ+PTIwMCYmdDwzMDB8fDMwND09PXQsciYmKGI9WHQoaCxFLHIpKSxiPVV0KGgsYixFLGwpLGw/KGguaWZNb2RpZmllZCYmKChUPUUuZ2V0UmVzcG9uc2VIZWFkZXIoIkxhc3QtTW9kaWZpZWQiKSkmJih3Lmxhc3RNb2RpZmllZFtvXT1UKSwoVD1FLmdldFJlc3BvbnNlSGVhZGVyKCJldGFnIikpJiYody5ldGFnW29dPVQpKSwyMDQ9PT10fHwiSEVBRCI9PT1oLnR5cGU/Qz0ibm9jb250ZW50IjozMDQ9PT10P0M9Im5vdG1vZGlmaWVkIjooQz1iLnN0YXRlLHA9Yi5kYXRhLGw9IShkPWIuZXJyb3IpKSk6KGQ9QywhdCYmQ3x8KEM9ImVycm9yIix0PDAmJih0PTApKSksRS5zdGF0dXM9dCxFLnN0YXR1c1RleHQ9KG58fEMpKyIiLGw/di5yZXNvbHZlV2l0aChnLFtwLEMsRV0pOnYucmVqZWN0V2l0aChnLFtFLEMsZF0pLEUuc3RhdHVzQ29kZSh4KSx4PXZvaWQgMCxmJiZ5LnRyaWdnZXIobD8iYWpheFN1Y2Nlc3MiOiJhamF4RXJyb3IiLFtFLGgsbD9wOmRdKSxtLmZpcmVXaXRoKGcsW0UsQ10pLGYmJih5LnRyaWdnZXIoImFqYXhDb21wbGV0ZSIsW0UsaF0pLC0tdy5hY3RpdmV8fHcuZXZlbnQudHJpZ2dlcigiYWpheFN0b3AiKSkpfXJldHVybiBFfSxnZXRKU09OOmZ1bmN0aW9uKGUsdCxuKXtyZXR1cm4gdy5nZXQoZSx0LG4sImpzb24iKX0sZ2V0U2NyaXB0OmZ1bmN0aW9uKGUsdCl7cmV0dXJuIHcuZ2V0KGUsdm9pZCAwLHQsInNjcmlwdCIpfX0pLHcuZWFjaChbImdldCIsInBvc3QiXSxmdW5jdGlvbihlLHQpe3dbdF09ZnVuY3Rpb24oZSxuLHIsaSl7cmV0dXJuIGcobikmJihpPWl8fHIscj1uLG49dm9pZCAwKSx3LmFqYXgody5leHRlbmQoe3VybDplLHR5cGU6dCxkYXRhVHlwZTppLGRhdGE6bixzdWNjZXNzOnJ9LHcuaXNQbGFpbk9iamVjdChlKSYmZSkpfX0pLHcuX2V2YWxVcmw9ZnVuY3Rpb24oZSl7cmV0dXJuIHcuYWpheCh7dXJsOmUsdHlwZToiR0VUIixkYXRhVHlwZToic2NyaXB0IixjYWNoZTohMCxhc3luYzohMSxnbG9iYWw6ITEsInRocm93cyI6ITB9KX0sdy5mbi5leHRlbmQoe3dyYXBBbGw6ZnVuY3Rpb24oZSl7dmFyIHQ7cmV0dXJuIHRoaXNbMF0mJihnKGUpJiYoZT1lLmNhbGwodGhpc1swXSkpLHQ9dyhlLHRoaXNbMF0ub3duZXJEb2N1bWVudCkuZXEoMCkuY2xvbmUoITApLHRoaXNbMF0ucGFyZW50Tm9kZSYmdC5pbnNlcnRCZWZvcmUodGhpc1swXSksdC5tYXAoZnVuY3Rpb24oKXt2YXIgZT10aGlzO3doaWxlKGUuZmlyc3RFbGVtZW50Q2hpbGQpZT1lLmZpcnN0RWxlbWVudENoaWxkO3JldHVybiBlfSkuYXBwZW5kKHRoaXMpKSx0aGlzfSx3cmFwSW5uZXI6ZnVuY3Rpb24oZSl7cmV0dXJuIGcoZSk/dGhpcy5lYWNoKGZ1bmN0aW9uKHQpe3codGhpcykud3JhcElubmVyKGUuY2FsbCh0aGlzLHQpKX0pOnRoaXMuZWFjaChmdW5jdGlvbigpe3ZhciB0PXcodGhpcyksbj10LmNvbnRlbnRzKCk7bi5sZW5ndGg/bi53cmFwQWxsKGUpOnQuYXBwZW5kKGUpfSl9LHdyYXA6ZnVuY3Rpb24oZSl7dmFyIHQ9ZyhlKTtyZXR1cm4gdGhpcy5lYWNoKGZ1bmN0aW9uKG4pe3codGhpcykud3JhcEFsbCh0P2UuY2FsbCh0aGlzLG4pOmUpfSl9LHVud3JhcDpmdW5jdGlvbihlKXtyZXR1cm4gdGhpcy5wYXJlbnQoZSkubm90KCJib2R5IikuZWFjaChmdW5jdGlvbigpe3codGhpcykucmVwbGFjZVdpdGgodGhpcy5jaGlsZE5vZGVzKX0pLHRoaXN9fSksdy5leHByLnBzZXVkb3MuaGlkZGVuPWZ1bmN0aW9uKGUpe3JldHVybiF3LmV4cHIucHNldWRvcy52aXNpYmxlKGUpfSx3LmV4cHIucHNldWRvcy52aXNpYmxlPWZ1bmN0aW9uKGUpe3JldHVybiEhKGUub2Zmc2V0V2lkdGh8fGUub2Zmc2V0SGVpZ2h0fHxlLmdldENsaWVudFJlY3RzKCkubGVuZ3RoKX0sdy5hamF4U2V0dGluZ3MueGhyPWZ1bmN0aW9uKCl7dHJ5e3JldHVybiBuZXcgZS5YTUxIdHRwUmVxdWVzdH1jYXRjaChlKXt9fTt2YXIgVnQ9ezA6MjAwLDEyMjM6MjA0fSxHdD13LmFqYXhTZXR0aW5ncy54aHIoKTtoLmNvcnM9ISFHdCYmIndpdGhDcmVkZW50aWFscyJpbiBHdCxoLmFqYXg9R3Q9ISFHdCx3LmFqYXhUcmFuc3BvcnQoZnVuY3Rpb24odCl7dmFyIG4scjtpZihoLmNvcnN8fEd0JiYhdC5jcm9zc0RvbWFpbilyZXR1cm57c2VuZDpmdW5jdGlvbihpLG8pe3ZhciBhLHM9dC54aHIoKTtpZihzLm9wZW4odC50eXBlLHQudXJsLHQuYXN5bmMsdC51c2VybmFtZSx0LnBhc3N3b3JkKSx0LnhockZpZWxkcylmb3IoYSBpbiB0LnhockZpZWxkcylzW2FdPXQueGhyRmllbGRzW2FdO3QubWltZVR5cGUmJnMub3ZlcnJpZGVNaW1lVHlwZSYmcy5vdmVycmlkZU1pbWVUeXBlKHQubWltZVR5cGUpLHQuY3Jvc3NEb21haW58fGlbIlgtUmVxdWVzdGVkLVdpdGgiXXx8KGlbIlgtUmVxdWVzdGVkLVdpdGgiXT0iWE1MSHR0cFJlcXVlc3QiKTtmb3IoYSBpbiBpKXMuc2V0UmVxdWVzdEhlYWRlcihhLGlbYV0pO249ZnVuY3Rpb24oZSl7cmV0dXJuIGZ1bmN0aW9uKCl7biYmKG49cj1zLm9ubG9hZD1zLm9uZXJyb3I9cy5vbmFib3J0PXMub250aW1lb3V0PXMub25yZWFkeXN0YXRlY2hhbmdlPW51bGwsImFib3J0Ij09PWU/cy5hYm9ydCgpOiJlcnJvciI9PT1lPyJudW1iZXIiIT10eXBlb2Ygcy5zdGF0dXM/bygwLCJlcnJvciIpOm8ocy5zdGF0dXMscy5zdGF0dXNUZXh0KTpvKFZ0W3Muc3RhdHVzXXx8cy5zdGF0dXMscy5zdGF0dXNUZXh0LCJ0ZXh0IiE9PShzLnJlc3BvbnNlVHlwZXx8InRleHQiKXx8InN0cmluZyIhPXR5cGVvZiBzLnJlc3BvbnNlVGV4dD97YmluYXJ5OnMucmVzcG9uc2V9Ont0ZXh0OnMucmVzcG9uc2VUZXh0fSxzLmdldEFsbFJlc3BvbnNlSGVhZGVycygpKSl9fSxzLm9ubG9hZD1uKCkscj1zLm9uZXJyb3I9cy5vbnRpbWVvdXQ9bigiZXJyb3IiKSx2b2lkIDAhPT1zLm9uYWJvcnQ/cy5vbmFib3J0PXI6cy5vbnJlYWR5c3RhdGVjaGFuZ2U9ZnVuY3Rpb24oKXs0PT09cy5yZWFkeVN0YXRlJiZlLnNldFRpbWVvdXQoZnVuY3Rpb24oKXtuJiZyKCl9KX0sbj1uKCJhYm9ydCIpO3RyeXtzLnNlbmQodC5oYXNDb250ZW50JiZ0LmRhdGF8fG51bGwpfWNhdGNoKGUpe2lmKG4pdGhyb3cgZX19LGFib3J0OmZ1bmN0aW9uKCl7biYmbigpfX19KSx3LmFqYXhQcmVmaWx0ZXIoZnVuY3Rpb24oZSl7ZS5jcm9zc0RvbWFpbiYmKGUuY29udGVudHMuc2NyaXB0PSExKX0pLHcuYWpheFNldHVwKHthY2NlcHRzOntzY3JpcHQ6InRleHQvamF2YXNjcmlwdCwgYXBwbGljYXRpb24vamF2YXNjcmlwdCwgYXBwbGljYXRpb24vZWNtYXNjcmlwdCwgYXBwbGljYXRpb24veC1lY21hc2NyaXB0In0sY29udGVudHM6e3NjcmlwdDovXGIoPzpqYXZhfGVjbWEpc2NyaXB0XGIvfSxjb252ZXJ0ZXJzOnsidGV4dCBzY3JpcHQiOmZ1bmN0aW9uKGUpe3JldHVybiB3Lmdsb2JhbEV2YWwoZSksZX19fSksdy5hamF4UHJlZmlsdGVyKCJzY3JpcHQiLGZ1bmN0aW9uKGUpe3ZvaWQgMD09PWUuY2FjaGUmJihlLmNhY2hlPSExKSxlLmNyb3NzRG9tYWluJiYoZS50eXBlPSJHRVQiKX0pLHcuYWpheFRyYW5zcG9ydCgic2NyaXB0IixmdW5jdGlvbihlKXtpZihlLmNyb3NzRG9tYWluKXt2YXIgdCxuO3JldHVybntzZW5kOmZ1bmN0aW9uKGksbyl7dD13KCI8c2NyaXB0PiIpLnByb3Aoe2NoYXJzZXQ6ZS5zY3JpcHRDaGFyc2V0LHNyYzplLnVybH0pLm9uKCJsb2FkIGVycm9yIixuPWZ1bmN0aW9uKGUpe3QucmVtb3ZlKCksbj1udWxsLGUmJm8oImVycm9yIj09PWUudHlwZT80MDQ6MjAwLGUudHlwZSl9KSxyLmhlYWQuYXBwZW5kQ2hpbGQodFswXSl9LGFib3J0OmZ1bmN0aW9uKCl7biYmbigpfX19fSk7dmFyIFl0PVtdLFF0PS8oPSlcPyg/PSZ8JCl8XD9cPy87dy5hamF4U2V0dXAoe2pzb25wOiJjYWxsYmFjayIsanNvbnBDYWxsYmFjazpmdW5jdGlvbigpe3ZhciBlPVl0LnBvcCgpfHx3LmV4cGFuZG8rIl8iK0V0Kys7cmV0dXJuIHRoaXNbZV09ITAsZX19KSx3LmFqYXhQcmVmaWx0ZXIoImpzb24ganNvbnAiLGZ1bmN0aW9uKHQsbixyKXt2YXIgaSxvLGEscz0hMSE9PXQuanNvbnAmJihRdC50ZXN0KHQudXJsKT8idXJsIjoic3RyaW5nIj09dHlwZW9mIHQuZGF0YSYmMD09PSh0LmNvbnRlbnRUeXBlfHwiIikuaW5kZXhPZigiYXBwbGljYXRpb24veC13d3ctZm9ybS11cmxlbmNvZGVkIikmJlF0LnRlc3QodC5kYXRhKSYmImRhdGEiKTtpZihzfHwianNvbnAiPT09dC5kYXRhVHlwZXNbMF0pcmV0dXJuIGk9dC5qc29ucENhbGxiYWNrPWcodC5qc29ucENhbGxiYWNrKT90Lmpzb25wQ2FsbGJhY2soKTp0Lmpzb25wQ2FsbGJhY2sscz90W3NdPXRbc10ucmVwbGFjZShRdCwiJDEiK2kpOiExIT09dC5qc29ucCYmKHQudXJsKz0oa3QudGVzdCh0LnVybCk/IiYiOiI/IikrdC5qc29ucCsiPSIraSksdC5jb252ZXJ0ZXJzWyJzY3JpcHQganNvbiJdPWZ1bmN0aW9uKCl7cmV0dXJuIGF8fHcuZXJyb3IoaSsiIHdhcyBub3QgY2FsbGVkIiksYVswXX0sdC5kYXRhVHlwZXNbMF09Impzb24iLG89ZVtpXSxlW2ldPWZ1bmN0aW9uKCl7YT1hcmd1bWVudHN9LHIuYWx3YXlzKGZ1bmN0aW9uKCl7dm9pZCAwPT09bz93KGUpLnJlbW92ZVByb3AoaSk6ZVtpXT1vLHRbaV0mJih0Lmpzb25wQ2FsbGJhY2s9bi5qc29ucENhbGxiYWNrLFl0LnB1c2goaSkpLGEmJmcobykmJm8oYVswXSksYT1vPXZvaWQgMH0pLCJzY3JpcHQifSksaC5jcmVhdGVIVE1MRG9jdW1lbnQ9ZnVuY3Rpb24oKXt2YXIgZT1yLmltcGxlbWVudGF0aW9uLmNyZWF0ZUhUTUxEb2N1bWVudCgiIikuYm9keTtyZXR1cm4gZS5pbm5lckhUTUw9Ijxmb3JtPjwvZm9ybT48Zm9ybT48L2Zvcm0+IiwyPT09ZS5jaGlsZE5vZGVzLmxlbmd0aH0oKSx3LnBhcnNlSFRNTD1mdW5jdGlvbihlLHQsbil7aWYoInN0cmluZyIhPXR5cGVvZiBlKXJldHVybltdOyJib29sZWFuIj09dHlwZW9mIHQmJihuPXQsdD0hMSk7dmFyIGksbyxhO3JldHVybiB0fHwoaC5jcmVhdGVIVE1MRG9jdW1lbnQ/KChpPSh0PXIuaW1wbGVtZW50YXRpb24uY3JlYXRlSFRNTERvY3VtZW50KCIiKSkuY3JlYXRlRWxlbWVudCgiYmFzZSIpKS5ocmVmPXIubG9jYXRpb24uaHJlZix0LmhlYWQuYXBwZW5kQ2hpbGQoaSkpOnQ9ciksbz1BLmV4ZWMoZSksYT0hbiYmW10sbz9bdC5jcmVhdGVFbGVtZW50KG9bMV0pXToobz14ZShbZV0sdCxhKSxhJiZhLmxlbmd0aCYmdyhhKS5yZW1vdmUoKSx3Lm1lcmdlKFtdLG8uY2hpbGROb2RlcykpfSx3LmZuLmxvYWQ9ZnVuY3Rpb24oZSx0LG4pe3ZhciByLGksbyxhPXRoaXMscz1lLmluZGV4T2YoIiAiKTtyZXR1cm4gcz4tMSYmKHI9dnQoZS5zbGljZShzKSksZT1lLnNsaWNlKDAscykpLGcodCk/KG49dCx0PXZvaWQgMCk6dCYmIm9iamVjdCI9PXR5cGVvZiB0JiYoaT0iUE9TVCIpLGEubGVuZ3RoPjAmJncuYWpheCh7dXJsOmUsdHlwZTppfHwiR0VUIixkYXRhVHlwZToiaHRtbCIsZGF0YTp0fSkuZG9uZShmdW5jdGlvbihlKXtvPWFyZ3VtZW50cyxhLmh0bWwocj93KCI8ZGl2PiIpLmFwcGVuZCh3LnBhcnNlSFRNTChlKSkuZmluZChyKTplKX0pLmFsd2F5cyhuJiZmdW5jdGlvbihlLHQpe2EuZWFjaChmdW5jdGlvbigpe24uYXBwbHkodGhpcyxvfHxbZS5yZXNwb25zZVRleHQsdCxlXSl9KX0pLHRoaXN9LHcuZWFjaChbImFqYXhTdGFydCIsImFqYXhTdG9wIiwiYWpheENvbXBsZXRlIiwiYWpheEVycm9yIiwiYWpheFN1Y2Nlc3MiLCJhamF4U2VuZCJdLGZ1bmN0aW9uKGUsdCl7dy5mblt0XT1mdW5jdGlvbihlKXtyZXR1cm4gdGhpcy5vbih0LGUpfX0pLHcuZXhwci5wc2V1ZG9zLmFuaW1hdGVkPWZ1bmN0aW9uKGUpe3JldHVybiB3LmdyZXAody50aW1lcnMsZnVuY3Rpb24odCl7cmV0dXJuIGU9PT10LmVsZW19KS5sZW5ndGh9LHcub2Zmc2V0PXtzZXRPZmZzZXQ6ZnVuY3Rpb24oZSx0LG4pe3ZhciByLGksbyxhLHMsdSxsLGM9dy5jc3MoZSwicG9zaXRpb24iKSxmPXcoZSkscD17fTsic3RhdGljIj09PWMmJihlLnN0eWxlLnBvc2l0aW9uPSJyZWxhdGl2ZSIpLHM9Zi5vZmZzZXQoKSxvPXcuY3NzKGUsInRvcCIpLHU9dy5jc3MoZSwibGVmdCIpLChsPSgiYWJzb2x1dGUiPT09Y3x8ImZpeGVkIj09PWMpJiYobyt1KS5pbmRleE9mKCJhdXRvIik+LTEpPyhhPShyPWYucG9zaXRpb24oKSkudG9wLGk9ci5sZWZ0KTooYT1wYXJzZUZsb2F0KG8pfHwwLGk9cGFyc2VGbG9hdCh1KXx8MCksZyh0KSYmKHQ9dC5jYWxsKGUsbix3LmV4dGVuZCh7fSxzKSkpLG51bGwhPXQudG9wJiYocC50b3A9dC50b3Atcy50b3ArYSksbnVsbCE9dC5sZWZ0JiYocC5sZWZ0PXQubGVmdC1zLmxlZnQraSksInVzaW5nImluIHQ/dC51c2luZy5jYWxsKGUscCk6Zi5jc3MocCl9fSx3LmZuLmV4dGVuZCh7b2Zmc2V0OmZ1bmN0aW9uKGUpe2lmKGFyZ3VtZW50cy5sZW5ndGgpcmV0dXJuIHZvaWQgMD09PWU/dGhpczp0aGlzLmVhY2goZnVuY3Rpb24odCl7dy5vZmZzZXQuc2V0T2Zmc2V0KHRoaXMsZSx0KX0pO3ZhciB0LG4scj10aGlzWzBdO2lmKHIpcmV0dXJuIHIuZ2V0Q2xpZW50UmVjdHMoKS5sZW5ndGg/KHQ9ci5nZXRCb3VuZGluZ0NsaWVudFJlY3QoKSxuPXIub3duZXJEb2N1bWVudC5kZWZhdWx0Vmlldyx7dG9wOnQudG9wK24ucGFnZVlPZmZzZXQsbGVmdDp0LmxlZnQrbi5wYWdlWE9mZnNldH0pOnt0b3A6MCxsZWZ0OjB9fSxwb3NpdGlvbjpmdW5jdGlvbigpe2lmKHRoaXNbMF0pe3ZhciBlLHQsbixyPXRoaXNbMF0saT17dG9wOjAsbGVmdDowfTtpZigiZml4ZWQiPT09dy5jc3MociwicG9zaXRpb24iKSl0PXIuZ2V0Qm91bmRpbmdDbGllbnRSZWN0KCk7ZWxzZXt0PXRoaXMub2Zmc2V0KCksbj1yLm93bmVyRG9jdW1lbnQsZT1yLm9mZnNldFBhcmVudHx8bi5kb2N1bWVudEVsZW1lbnQ7d2hpbGUoZSYmKGU9PT1uLmJvZHl8fGU9PT1uLmRvY3VtZW50RWxlbWVudCkmJiJzdGF0aWMiPT09dy5jc3MoZSwicG9zaXRpb24iKSllPWUucGFyZW50Tm9kZTtlJiZlIT09ciYmMT09PWUubm9kZVR5cGUmJigoaT13KGUpLm9mZnNldCgpKS50b3ArPXcuY3NzKGUsImJvcmRlclRvcFdpZHRoIiwhMCksaS5sZWZ0Kz13LmNzcyhlLCJib3JkZXJMZWZ0V2lkdGgiLCEwKSl9cmV0dXJue3RvcDp0LnRvcC1pLnRvcC13LmNzcyhyLCJtYXJnaW5Ub3AiLCEwKSxsZWZ0OnQubGVmdC1pLmxlZnQtdy5jc3MociwibWFyZ2luTGVmdCIsITApfX19LG9mZnNldFBhcmVudDpmdW5jdGlvbigpe3JldHVybiB0aGlzLm1hcChmdW5jdGlvbigpe3ZhciBlPXRoaXMub2Zmc2V0UGFyZW50O3doaWxlKGUmJiJzdGF0aWMiPT09dy5jc3MoZSwicG9zaXRpb24iKSllPWUub2Zmc2V0UGFyZW50O3JldHVybiBlfHxiZX0pfX0pLHcuZWFjaCh7c2Nyb2xsTGVmdDoicGFnZVhPZmZzZXQiLHNjcm9sbFRvcDoicGFnZVlPZmZzZXQifSxmdW5jdGlvbihlLHQpe3ZhciBuPSJwYWdlWU9mZnNldCI9PT10O3cuZm5bZV09ZnVuY3Rpb24ocil7cmV0dXJuIHoodGhpcyxmdW5jdGlvbihlLHIsaSl7dmFyIG87aWYoeShlKT9vPWU6OT09PWUubm9kZVR5cGUmJihvPWUuZGVmYXVsdFZpZXcpLHZvaWQgMD09PWkpcmV0dXJuIG8/b1t0XTplW3JdO28/by5zY3JvbGxUbyhuP28ucGFnZVhPZmZzZXQ6aSxuP2k6by5wYWdlWU9mZnNldCk6ZVtyXT1pfSxlLHIsYXJndW1lbnRzLmxlbmd0aCl9fSksdy5lYWNoKFsidG9wIiwibGVmdCJdLGZ1bmN0aW9uKGUsdCl7dy5jc3NIb29rc1t0XT1fZShoLnBpeGVsUG9zaXRpb24sZnVuY3Rpb24oZSxuKXtpZihuKXJldHVybiBuPUZlKGUsdCksV2UudGVzdChuKT93KGUpLnBvc2l0aW9uKClbdF0rInB4IjpufSl9KSx3LmVhY2goe0hlaWdodDoiaGVpZ2h0IixXaWR0aDoid2lkdGgifSxmdW5jdGlvbihlLHQpe3cuZWFjaCh7cGFkZGluZzoiaW5uZXIiK2UsY29udGVudDp0LCIiOiJvdXRlciIrZX0sZnVuY3Rpb24obixyKXt3LmZuW3JdPWZ1bmN0aW9uKGksbyl7dmFyIGE9YXJndW1lbnRzLmxlbmd0aCYmKG58fCJib29sZWFuIiE9dHlwZW9mIGkpLHM9bnx8KCEwPT09aXx8ITA9PT1vPyJtYXJnaW4iOiJib3JkZXIiKTtyZXR1cm4geih0aGlzLGZ1bmN0aW9uKHQsbixpKXt2YXIgbztyZXR1cm4geSh0KT8wPT09ci5pbmRleE9mKCJvdXRlciIpP3RbImlubmVyIitlXTp0LmRvY3VtZW50LmRvY3VtZW50RWxlbWVudFsiY2xpZW50IitlXTo5PT09dC5ub2RlVHlwZT8obz10LmRvY3VtZW50RWxlbWVudCxNYXRoLm1heCh0LmJvZHlbInNjcm9sbCIrZV0sb1sic2Nyb2xsIitlXSx0LmJvZHlbIm9mZnNldCIrZV0sb1sib2Zmc2V0IitlXSxvWyJjbGllbnQiK2VdKSk6dm9pZCAwPT09aT93LmNzcyh0LG4scyk6dy5zdHlsZSh0LG4saSxzKX0sdCxhP2k6dm9pZCAwLGEpfX0pfSksdy5lYWNoKCJibHVyIGZvY3VzIGZvY3VzaW4gZm9jdXNvdXQgcmVzaXplIHNjcm9sbCBjbGljayBkYmxjbGljayBtb3VzZWRvd24gbW91c2V1cCBtb3VzZW1vdmUgbW91c2VvdmVyIG1vdXNlb3V0IG1vdXNlZW50ZXIgbW91c2VsZWF2ZSBjaGFuZ2Ugc2VsZWN0IHN1Ym1pdCBrZXlkb3duIGtleXByZXNzIGtleXVwIGNvbnRleHRtZW51Ii5zcGxpdCgiICIpLGZ1bmN0aW9uKGUsdCl7dy5mblt0XT1mdW5jdGlvbihlLG4pe3JldHVybiBhcmd1bWVudHMubGVuZ3RoPjA/dGhpcy5vbih0LG51bGwsZSxuKTp0aGlzLnRyaWdnZXIodCl9fSksdy5mbi5leHRlbmQoe2hvdmVyOmZ1bmN0aW9uKGUsdCl7cmV0dXJuIHRoaXMubW91c2VlbnRlcihlKS5tb3VzZWxlYXZlKHR8fGUpfX0pLHcuZm4uZXh0ZW5kKHtiaW5kOmZ1bmN0aW9uKGUsdCxuKXtyZXR1cm4gdGhpcy5vbihlLG51bGwsdCxuKX0sdW5iaW5kOmZ1bmN0aW9uKGUsdCl7cmV0dXJuIHRoaXMub2ZmKGUsbnVsbCx0KX0sZGVsZWdhdGU6ZnVuY3Rpb24oZSx0LG4scil7cmV0dXJuIHRoaXMub24odCxlLG4scil9LHVuZGVsZWdhdGU6ZnVuY3Rpb24oZSx0LG4pe3JldHVybiAxPT09YXJndW1lbnRzLmxlbmd0aD90aGlzLm9mZihlLCIqKiIpOnRoaXMub2ZmKHQsZXx8IioqIixuKX19KSx3LnByb3h5PWZ1bmN0aW9uKGUsdCl7dmFyIG4scixpO2lmKCJzdHJpbmciPT10eXBlb2YgdCYmKG49ZVt0XSx0PWUsZT1uKSxnKGUpKXJldHVybiByPW8uY2FsbChhcmd1bWVudHMsMiksaT1mdW5jdGlvbigpe3JldHVybiBlLmFwcGx5KHR8fHRoaXMsci5jb25jYXQoby5jYWxsKGFyZ3VtZW50cykpKX0saS5ndWlkPWUuZ3VpZD1lLmd1aWR8fHcuZ3VpZCsrLGl9LHcuaG9sZFJlYWR5PWZ1bmN0aW9uKGUpe2U/dy5yZWFkeVdhaXQrKzp3LnJlYWR5KCEwKX0sdy5pc0FycmF5PUFycmF5LmlzQXJyYXksdy5wYXJzZUpTT049SlNPTi5wYXJzZSx3Lm5vZGVOYW1lPU4sdy5pc0Z1bmN0aW9uPWcsdy5pc1dpbmRvdz15LHcuY2FtZWxDYXNlPUcsdy50eXBlPXgsdy5ub3c9RGF0ZS5ub3csdy5pc051bWVyaWM9ZnVuY3Rpb24oZSl7dmFyIHQ9dy50eXBlKGUpO3JldHVybigibnVtYmVyIj09PXR8fCJzdHJpbmciPT09dCkmJiFpc05hTihlLXBhcnNlRmxvYXQoZSkpfSwiZnVuY3Rpb24iPT10eXBlb2YgZGVmaW5lJiZkZWZpbmUuYW1kJiZkZWZpbmUoImpxdWVyeSIsW10sZnVuY3Rpb24oKXtyZXR1cm4gd30pO3ZhciBKdD1lLmpRdWVyeSxLdD1lLiQ7cmV0dXJuIHcubm9Db25mbGljdD1mdW5jdGlvbih0KXtyZXR1cm4gZS4kPT09dyYmKGUuJD1LdCksdCYmZS5qUXVlcnk9PT13JiYoZS5qUXVlcnk9SnQpLHd9LHR8fChlLmpRdWVyeT1lLiQ9dyksd30pOwo='''
ks = BytesIO()
ks.write(base64.b64decode(buildjq))
sfile_dict['builtin_jquery.min.js'] = ks

buildlgs = '''QGNoYXJzZXQgIlVURi04IjtodG1sey13ZWJraXQtYm94LXNpemluZzpib3JkZXItYm94Oy1tb3ot
Ym94LXNpemluZzpib3JkZXItYm94O2JveC1zaXppbmc6Ym9yZGVyLWJveH0qLDphZnRlciw6YmVm
b3Jley13ZWJraXQtYm94LXNpemluZzppbmhlcml0Oy1tb3otYm94LXNpemluZzppbmhlcml0O2Jv
eC1zaXppbmc6aW5oZXJpdH1odG1se2xpbmUtaGVpZ2h0OjEuMTU7LXdlYmtpdC10ZXh0LXNpemUt
YWRqdXN0OjEwMCV9Ym9keXttYXJnaW46MH1tYWlue2Rpc3BsYXk6YmxvY2t9aDF7Zm9udC1zaXpl
OjJlbTttYXJnaW46LjY3ZW0gMH1ocntib3gtc2l6aW5nOmNvbnRlbnQtYm94O2hlaWdodDowO292
ZXJmbG93OnZpc2libGV9cHJle2ZvbnQtZmFtaWx5Om1vbm9zcGFjZSxtb25vc3BhY2U7Zm9udC1z
aXplOjFlbX1he2JhY2tncm91bmQtY29sb3I6dHJhbnNwYXJlbnR9YWJiclt0aXRsZV17Ym9yZGVy
LWJvdHRvbTpub25lO3RleHQtZGVjb3JhdGlvbjp1bmRlcmxpbmV9YixzdHJvbmd7Zm9udC13ZWln
aHQ6Ym9sZGVyfWNvZGUsa2JkLHNhbXB7Zm9udC1mYW1pbHk6bW9ub3NwYWNlLG1vbm9zcGFjZTtm
b250LXNpemU6MWVtfXNtYWxse2ZvbnQtc2l6ZTo4MCV9c3ViLHN1cHtmb250LXNpemU6NzUlO2xp
bmUtaGVpZ2h0OjA7cG9zaXRpb246cmVsYXRpdmU7dmVydGljYWwtYWxpZ246YmFzZWxpbmV9c3Vi
e2JvdHRvbTotLjI1ZW19c3Vwe3RvcDotLjVlbX1pbWd7Ym9yZGVyLXN0eWxlOm5vbmV9YnV0dG9u
LGlucHV0LG9wdGdyb3VwLHNlbGVjdCx0ZXh0YXJlYXtmb250LWZhbWlseTppbmhlcml0O2ZvbnQt
c2l6ZToxMDAlO2xpbmUtaGVpZ2h0OjEuMTU7bWFyZ2luOjB9YnV0dG9uLGlucHV0e292ZXJmbG93
OnZpc2libGV9YnV0dG9uLHNlbGVjdHt0ZXh0LXRyYW5zZm9ybTpub25lfVt0eXBlPWJ1dHRvbl0s
W3R5cGU9cmVzZXRdLFt0eXBlPXN1Ym1pdF0sYnV0dG9uey13ZWJraXQtYXBwZWFyYW5jZTpidXR0
b259W3R5cGU9YnV0dG9uXTo6LW1vei1mb2N1cy1pbm5lcixbdHlwZT1yZXNldF06Oi1tb3otZm9j
dXMtaW5uZXIsW3R5cGU9c3VibWl0XTo6LW1vei1mb2N1cy1pbm5lcixidXR0b246Oi1tb3otZm9j
dXMtaW5uZXJ7Ym9yZGVyLXN0eWxlOm5vbmU7cGFkZGluZzowfVt0eXBlPWJ1dHRvbl06LW1vei1m
b2N1c3JpbmcsW3R5cGU9cmVzZXRdOi1tb3otZm9jdXNyaW5nLFt0eXBlPXN1Ym1pdF06LW1vei1m
b2N1c3JpbmcsYnV0dG9uOi1tb3otZm9jdXNyaW5ne291dGxpbmU6MXB4IGRvdHRlZCBCdXR0b25U
ZXh0fWZpZWxkc2V0e3BhZGRpbmc6LjM1ZW0gLjc1ZW0gLjYyNWVtfWxlZ2VuZHtib3gtc2l6aW5n
OmJvcmRlci1ib3g7Y29sb3I6aW5oZXJpdDtkaXNwbGF5OnRhYmxlO21heC13aWR0aDoxMDAlO3Bh
ZGRpbmc6MDt3aGl0ZS1zcGFjZTpub3JtYWx9cHJvZ3Jlc3N7dmVydGljYWwtYWxpZ246YmFzZWxp
bmV9dGV4dGFyZWF7b3ZlcmZsb3c6YXV0b31bdHlwZT1jaGVja2JveF0sW3R5cGU9cmFkaW9de2Jv
eC1zaXppbmc6Ym9yZGVyLWJveDtwYWRkaW5nOjB9W3R5cGU9bnVtYmVyXTo6LXdlYmtpdC1pbm5l
ci1zcGluLWJ1dHRvbixbdHlwZT1udW1iZXJdOjotd2Via2l0LW91dGVyLXNwaW4tYnV0dG9ue2hl
aWdodDphdXRvfVt0eXBlPXNlYXJjaF17LXdlYmtpdC1hcHBlYXJhbmNlOnRleHRmaWVsZDtvdXRs
aW5lLW9mZnNldDotMnB4fVt0eXBlPXNlYXJjaF06Oi13ZWJraXQtc2VhcmNoLWRlY29yYXRpb257
LXdlYmtpdC1hcHBlYXJhbmNlOm5vbmV9Ojotd2Via2l0LWZpbGUtdXBsb2FkLWJ1dHRvbnstd2Vi
a2l0LWFwcGVhcmFuY2U6YnV0dG9uO2ZvbnQ6aW5oZXJpdH1kZXRhaWxze2Rpc3BsYXk6YmxvY2t9
c3VtbWFyeXtkaXNwbGF5Omxpc3QtaXRlbX10ZW1wbGF0ZXtkaXNwbGF5Om5vbmV9W2hpZGRlbl17
ZGlzcGxheTpub25lfWJsb2NrcXVvdGUsYm9keSxjYXB0aW9uLGRkLGRsLGZpZWxkc2V0LGZpZ3Vy
ZSxmb3JtLGgxLGgyLGgzLGg0LGg1LGg2LGhyLGxlZ2VuZCxvbCxwLHByZSx0YWJsZSx0ZCx0aCx1
bHttYXJnaW46MDtwYWRkaW5nOjB9YWJiclt0aXRsZV0sZGZuW3RpdGxlXXtjdXJzb3I6aGVscH1p
bnMsdXt0ZXh0LWRlY29yYXRpb246bm9uZX1pbnN7Ym9yZGVyLWJvdHRvbToxcHggc29saWR9aW1n
e21heC13aWR0aDoxMDAlO3ZlcnRpY2FsLWFsaWduOm1pZGRsZX1maWd1cmU+aW1ne2Rpc3BsYXk6
YmxvY2t9ZmlnY2FwdGlvbntmb250LXNpemU6LjhyZW19aW5wdXQ6bm90KFt0eXBlXSksaW5wdXRb
dHlwZT1jb2xvcl0saW5wdXRbdHlwZT1kYXRlXSxpbnB1dFt0eXBlPWRhdGV0aW1lLWxvY2FsXSxp
bnB1dFt0eXBlPWRhdGV0aW1lXSxpbnB1dFt0eXBlPWVtYWlsXSxpbnB1dFt0eXBlPW1vbnRoXSxp
bnB1dFt0eXBlPW51bWJlcl0saW5wdXRbdHlwZT1wYXNzd29yZF0saW5wdXRbdHlwZT1zZWFyY2hd
LGlucHV0W3R5cGU9dGVsXSxpbnB1dFt0eXBlPXRleHRdLGlucHV0W3R5cGU9dGltZV0saW5wdXRb
dHlwZT11cmxdLGlucHV0W3R5cGU9d2Vla10sc2VsZWN0LHRleHRhcmVhe2ZvbnQtc2l6ZToxLjFy
ZW07Ym9yZGVyLXJhZGl1czoycHg7YmFja2dyb3VuZC1jb2xvcjojZmZmO3BhZGRpbmc6N3B4O21p
bi1oZWlnaHQ6NDBweDtib3JkZXI6MXB4IHNvbGlkICM5NDk0OTQ7Y29sb3I6IzQ2NDY0Njt2ZXJ0
aWNhbC1hbGlnbjptaWRkbGU7d2lkdGg6MjUwcHg7bWF4LXdpZHRoOjEwMCV9aW5wdXQ6bm90KFt0
eXBlXSk6YWN0aXZlLGlucHV0Om5vdChbdHlwZV0pOmZvY3VzLGlucHV0Om5vdChbdHlwZV0pOmhv
dmVyLGlucHV0W3R5cGU9Y2hlY2tib3hdOmFjdGl2ZSxpbnB1dFt0eXBlPWNoZWNrYm94XTpmb2N1
cyxpbnB1dFt0eXBlPWNoZWNrYm94XTpob3ZlcixpbnB1dFt0eXBlPWNvbG9yXTphY3RpdmUsaW5w
dXRbdHlwZT1jb2xvcl06Zm9jdXMsaW5wdXRbdHlwZT1jb2xvcl06aG92ZXIsaW5wdXRbdHlwZT1k
YXRlXTphY3RpdmUsaW5wdXRbdHlwZT1kYXRlXTpmb2N1cyxpbnB1dFt0eXBlPWRhdGVdOmhvdmVy
LGlucHV0W3R5cGU9ZGF0ZXRpbWUtbG9jYWxdOmFjdGl2ZSxpbnB1dFt0eXBlPWRhdGV0aW1lLWxv
Y2FsXTpmb2N1cyxpbnB1dFt0eXBlPWRhdGV0aW1lLWxvY2FsXTpob3ZlcixpbnB1dFt0eXBlPWRh
dGV0aW1lXTphY3RpdmUsaW5wdXRbdHlwZT1kYXRldGltZV06Zm9jdXMsaW5wdXRbdHlwZT1kYXRl
dGltZV06aG92ZXIsaW5wdXRbdHlwZT1lbWFpbF06YWN0aXZlLGlucHV0W3R5cGU9ZW1haWxdOmZv
Y3VzLGlucHV0W3R5cGU9ZW1haWxdOmhvdmVyLGlucHV0W3R5cGU9bW9udGhdOmFjdGl2ZSxpbnB1
dFt0eXBlPW1vbnRoXTpmb2N1cyxpbnB1dFt0eXBlPW1vbnRoXTpob3ZlcixpbnB1dFt0eXBlPW51
bWJlcl06YWN0aXZlLGlucHV0W3R5cGU9bnVtYmVyXTpmb2N1cyxpbnB1dFt0eXBlPW51bWJlcl06
aG92ZXIsaW5wdXRbdHlwZT1wYXNzd29yZF06YWN0aXZlLGlucHV0W3R5cGU9cGFzc3dvcmRdOmZv
Y3VzLGlucHV0W3R5cGU9cGFzc3dvcmRdOmhvdmVyLGlucHV0W3R5cGU9c2VhcmNoXTphY3RpdmUs
aW5wdXRbdHlwZT1zZWFyY2hdOmZvY3VzLGlucHV0W3R5cGU9c2VhcmNoXTpob3ZlcixpbnB1dFt0
eXBlPXRlbF06YWN0aXZlLGlucHV0W3R5cGU9dGVsXTpmb2N1cyxpbnB1dFt0eXBlPXRlbF06aG92
ZXIsaW5wdXRbdHlwZT10ZXh0XTphY3RpdmUsaW5wdXRbdHlwZT10ZXh0XTpmb2N1cyxpbnB1dFt0
eXBlPXRleHRdOmhvdmVyLGlucHV0W3R5cGU9dGltZV06YWN0aXZlLGlucHV0W3R5cGU9dGltZV06
Zm9jdXMsaW5wdXRbdHlwZT10aW1lXTpob3ZlcixpbnB1dFt0eXBlPXVybF06YWN0aXZlLGlucHV0
W3R5cGU9dXJsXTpmb2N1cyxpbnB1dFt0eXBlPXVybF06aG92ZXIsaW5wdXRbdHlwZT13ZWVrXTph
Y3RpdmUsaW5wdXRbdHlwZT13ZWVrXTpmb2N1cyxpbnB1dFt0eXBlPXdlZWtdOmhvdmVyLHNlbGVj
dDphY3RpdmUsc2VsZWN0OmZvY3VzLHNlbGVjdDpob3Zlcix0ZXh0YXJlYTphY3RpdmUsdGV4dGFy
ZWE6Zm9jdXMsdGV4dGFyZWE6aG92ZXJ7Ym94LXNoYWRvdzppbnNldCAwIDAgMCAxcHggIzAwNmRh
ZDtib3JkZXItY29sb3I6IzAwNmRhZDtvdXRsaW5lOm5vbmV9aW5wdXQ6ZGlzYWJsZWQsaW5wdXQ6
ZGlzYWJsZWQ6YWN0aXZlLGlucHV0OmRpc2FibGVkOmZvY3VzLGlucHV0OmRpc2FibGVkOmhvdmVy
LHNlbGVjdDpkaXNhYmxlZCxzZWxlY3Q6ZGlzYWJsZWQ6YWN0aXZlLHNlbGVjdDpkaXNhYmxlZDpm
b2N1cyxzZWxlY3Q6ZGlzYWJsZWQ6aG92ZXJ7Y3Vyc29yOm5vdC1hbGxvd2VkO2JveC1zaGFkb3c6
bm9uZTtiYWNrZ3JvdW5kLWNvbG9yOiNlY2VjZWN9bGFiZWx7dmVydGljYWwtYWxpZ246bWlkZGxl
fXVse2xpc3Qtc3R5bGUtdHlwZTpjaXJjbGV9b2wsdWx7bWFyZ2luLWxlZnQ6MzBweH1kbCBkdHtm
b250LXdlaWdodDo2MDA7bWFyZ2luLXRvcDoxNXB4fWRsIGR0OmZpcnN0LW9mLXR5cGV7bWFyZ2lu
LXRvcDowfWRsIGRke3BhZGRpbmctbGVmdDoxNXB4fXRhYmxlIHRkLHRhYmxlIHRoe3RleHQtYWxp
Z246bGVmdH10YWJsZSB0ZFthbGlnbj1yaWdodF0sdGFibGUgdGhbYWxpZ249cmlnaHRde3RleHQt
YWxpZ246cmlnaHR9dGFibGUgdGRbYWxpZ249Y2VudGVyXSx0YWJsZSB0aFthbGlnbj1jZW50ZXJd
e3RleHQtYWxpZ246Y2VudGVyfXRhYmxlIHRib2R5IHRoe2ZvbnQtd2VpZ2h0OjQwMH1odG1se2Zv
bnQtc2l6ZToxMDAlfUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAwcHgpe2h0bWx7Zm9u
dC1zaXplOjk1JX19Ym9keXtmb250LWZhbWlseTpTb3VyY2UgU2FucyBQcm8sSGVsdmV0aWNhLEFy
aWFsLHNhbnMtc2VyaWY7Zm9udC1zaXplOjFyZW07bGluZS1oZWlnaHQ6MS40O2ZvbnQtd2VpZ2h0
OjQwMDtjb2xvcjojNDY0NjQ2Oy13ZWJraXQtdGV4dC1zaXplLWFkanVzdDoxMDAlO2JhY2tncm91
bmQtY29sb3I6I2ZkZmRmZDtkaXJlY3Rpb246bHRyfWNvZGUsa2JkLHByZSxzYW1wLHR0e2ZvbnQt
ZmFtaWx5OlNvdXJjZSBDb2RlIFBybyxtb25vc3BhY2U7YmFja2dyb3VuZC1jb2xvcjojZjlmOWY5
O2JvcmRlcjoxcHggc29saWQgI2QzZDNkMztwYWRkaW5nOjAgMnB4IDFweDtmb250LXNpemU6Ljg1
cmVtO2NvbG9yOiM2YzZjNmN9aDF7Zm9udC1zaXplOjIuNXJlbTtsaW5lLWhlaWdodDoxLjM7Zm9u
dC13ZWlnaHQ6NjAwfUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAwcHgpe2gxe2ZvbnQt
c2l6ZToyLjJyZW19fUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6NDAwcHgpe2gxe2ZvbnQt
c2l6ZToxLjhyZW19fWgye2ZvbnQtc2l6ZToxLjNyZW19aDIsaDN7Zm9udC13ZWlnaHQ6NjAwfWgz
e2ZvbnQtc2l6ZToxLjE1cmVtfWg0e2ZvbnQtc2l6ZToxLjFyZW07Zm9udC13ZWlnaHQ6NjAwfWg1
e3RleHQtdHJhbnNmb3JtOnVwcGVyY2FzZX1oNSxoNntmb250LXNpemU6MXJlbTtmb250LXdlaWdo
dDo2MDB9aDEsaDIsaDMsaDQsaDUsaDZ7cGFkZGluZy10b3A6MzBweH1oMTpmaXJzdC1jaGlsZCxo
MjpmaXJzdC1jaGlsZCxoMzpmaXJzdC1jaGlsZCxoNDpmaXJzdC1jaGlsZCxoNTpmaXJzdC1jaGls
ZCxoNjpmaXJzdC1jaGlsZCxocitoMSxocitoMixocitoMyxocitoNCxocitoNSxocitoNntwYWRk
aW5nLXRvcDowfXN0cm9uZ3tmb250LXdlaWdodDo2MDB9YXt0ZXh0LWRlY29yYXRpb246bm9uZTti
YWNrZ3JvdW5kLXBvc2l0aW9uOjAgMS4xNWVtO2JhY2tncm91bmQtcmVwZWF0OnJlcGVhdC14O2Jh
Y2tncm91bmQtc2l6ZToxMDAlIDEuNXB4O2NvbG9yOiMwMDZkYWQ7YmFja2dyb3VuZC1pbWFnZTps
aW5lYXItZ3JhZGllbnQoOTBkZWcsIzAwNmRhZCxyZ2JhKDAsMTA5LDE3MywuNykpfWE6aG92ZXJ7
Y29sb3I6IzAwNGQ3YTtiYWNrZ3JvdW5kLWltYWdlOmxpbmVhci1ncmFkaWVudCg5MGRlZywjMDA0
ZDdhLCMwMDRkN2EpfWE6YWN0aXZlLGE6Zm9jdXN7b3V0bGluZToxcHggc29saWQgIzAwNmRhZH1h
W3RhcmdldD1fYmxhbmtdOm5vdCguY29weS10b29sdGlwKTpub3QoLnNwb25zb3JzX19zcG9uc29y
KTphZnRlcnt3aGl0ZS1zcGFjZTpub3dyYXA7Zm9udC1zaXplOi44ZW07Zm9udC1mYW1pbHk6Rm9u
dCBBd2Vzb21lXCA1IEZyZWU7Zm9udC13ZWlnaHQ6OTAwO2NvbnRlbnQ6Iu+NnSI7bWFyZ2luOjAg
MCAwIDRweDtjb2xvcjppbmhlcml0O3Bvc2l0aW9uOnJlbGF0aXZlO3RvcDotMXB4fWFbaHJlZl49
Im1haWx0bzoiXTphZnRlcntmb250LXNpemU6LjlyZW07Zm9udC1mYW1pbHk6Rm9udCBBd2Vzb21l
XCA1IEZyZWU7Zm9udC13ZWlnaHQ6NDAwO2NvbnRlbnQ6Iu+DoCI7Y29sb3I6aW5oZXJpdDttYXJn
aW46MCAwIDAgNHB4O3Bvc2l0aW9uOnJlbGF0aXZlO3RvcDouNXB4fWEgLmJhZGdle3Bvc2l0aW9u
OnJlbGF0aXZlO3RvcDotM3B4fWEgY29kZSxhIGtiZCxhIHByZSxhIHNhbXAsYSB0dHtmb250LXNp
emU6LjdyZW07cG9zaXRpb246cmVsYXRpdmU7dG9wOi0ycHg7cGFkZGluZzowIDJweH1idXR0b257
YmFja2dyb3VuZC1pbWFnZTpub25lfWJ1dHRvbjpob3ZlcntiYWNrZ3JvdW5kLWltYWdlOm5vbmV9
YnV0dG9uOmFjdGl2ZSxidXR0b246Zm9jdXN7b3V0bGluZToxcHggc29saWQgIzAwNmRhZH06Oi1t
b3otc2VsZWN0aW9ue2NvbG9yOiMwMDNkNjE7YmFja2dyb3VuZDojZmZkMzQzfTo6c2VsZWN0aW9u
e2NvbG9yOiMwMDNkNjE7YmFja2dyb3VuZDojZmZkMzQzfWFiYnJbdGl0bGVde2JvcmRlci1ib3R0
b206MDt0ZXh0LWRlY29yYXRpb246dW5kZXJsaW5lIGRvdHRlZDtjdXJzb3I6aGVscH1ibG9ja3F1
b3RlLGRsLGZpZ3VyZSxoMSxoMixoMyxoNCxoNSxoNixvbCxwLHByZSx1bHtwYWRkaW5nLWJvdHRv
bToxNXB4fWRsOmxhc3QtY2hpbGQsZmlndXJlOmxhc3QtY2hpbGQsb2w6bGFzdC1jaGlsZCxwOmxh
c3QtY2hpbGQscHJlOmxhc3QtY2hpbGQsdWw6bGFzdC1jaGlsZHtwYWRkaW5nLWJvdHRvbTowfWhy
e21hcmdpbjo0NXB4IDA7Ym9yZGVyOjA7aGVpZ2h0OjJweDtiYWNrZ3JvdW5kOiNkM2QzZDM7YmFj
a2dyb3VuZC1pbWFnZTpsaW5lYXItZ3JhZGllbnQoOTBkZWcsI2QzZDNkMywjZmZmKX0uYmFubmVy
e2JhY2tncm91bmQtY29sb3I6IzAwNmRhZDtjb2xvcjojZmZmO3BhZGRpbmc6NTBweCAwfUBtZWRp
YSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo4MDBweCl7LmJhbm5lcntwYWRkaW5nOjQwcHgg
MH19QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjQwMHB4KXsuYmFubmVye3BhZGRp
bmc6MjVweCAwfX0uY29sLWhhbGZ7ZmxvYXQ6bGVmdDtkaXNwbGF5OmJsb2NrO21hcmdpbi1yaWdo
dDoyLjM1NzY1MTU5NzklO3dpZHRoOjQ4LjgyMTE3NDIwMSV9LmNvbC1oYWxmOmxhc3QtY2hpbGR7
bWFyZ2luLXJpZ2h0OjB9LmNvbC1oYWxmOmxhc3Qtb2YtdHlwZXttYXJnaW46MH1AbWVkaWEgb25s
eSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAwcHgpey5jb2wtaGFsZntmbG9hdDpub25lO21hcmdp
bjowO3dpZHRoOjEwMCV9LmNvbC1oYWxmOmZpcnN0LW9mLXR5cGV7bWFyZ2luLWJvdHRvbTozMHB4
fX0uc2l0ZS1jb250YWluZXJ7bWF4LXdpZHRoOjExNTBweDttYXJnaW4tcmlnaHQ6YXV0bzttYXJn
aW4tbGVmdDphdXRvO3BhZGRpbmc6MCAzMHB4fS5zaXRlLWNvbnRhaW5lcjphZnRlcntjbGVhcjpi
b3RoO2NvbnRlbnQ6IiI7ZGlzcGxheTp0YWJsZX1AbWVkaWEgc2NyZWVuIGFuZCAobWF4LXdpZHRo
OjYwMHB4KXsuc2l0ZS1jb250YWluZXJ7cGFkZGluZzowIDE1cHh9fS50YWJzLWNvbnRhaW5lcntt
YXgtd2lkdGg6MTE1MHB4O21hcmdpbi1yaWdodDphdXRvO21hcmdpbi1sZWZ0OmF1dG87cGFkZGlu
ZzowIDMwcHh9LnRhYnMtY29udGFpbmVyOmFmdGVye2NsZWFyOmJvdGg7Y29udGVudDoiIjtkaXNw
bGF5OnRhYmxlfUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6NjAwcHgpey50YWJzLWNvbnRh
aW5lcntwYWRkaW5nOjAgMTVweH19QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjgw
MHB4KXsudGFicy1jb250YWluZXJ7cGFkZGluZzo1cHh9fS5uYXJyb3ctY29udGFpbmVye21heC13
aWR0aDo5NDBweDttYXJnaW4tcmlnaHQ6YXV0bzttYXJnaW4tbGVmdDphdXRvO3BhZGRpbmc6MCAz
MHB4fS5uYXJyb3ctY29udGFpbmVyOmFmdGVye2NsZWFyOmJvdGg7Y29udGVudDoiIjtkaXNwbGF5
OnRhYmxlfUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6NjAwcHgpey5uYXJyb3ctY29udGFp
bmVye3BhZGRpbmc6MCAxNXB4fX0ubGVmdC1sYXlvdXR7bWF4LXdpZHRoOjExNTBweDttYXJnaW4t
cmlnaHQ6YXV0bzttYXJnaW4tbGVmdDphdXRvO3BhZGRpbmc6MCAzMHB4fS5sZWZ0LWxheW91dDph
ZnRlcntjbGVhcjpib3RoO2NvbnRlbnQ6IiI7ZGlzcGxheTp0YWJsZX1AbWVkaWEgc2NyZWVuIGFu
ZCAobWF4LXdpZHRoOjYwMHB4KXsubGVmdC1sYXlvdXR7cGFkZGluZzowIDE1cHh9fS5sZWZ0LWxh
eW91dF9fc2lkZWJhcntmbG9hdDpsZWZ0O3dpZHRoOi13ZWJraXQtY2FsYygyNSUgLSAxNXB4KTt3
aWR0aDpjYWxjKDI1JSAtIDE1cHgpO21hcmdpbi1yaWdodDozMHB4fUBtZWRpYSBvbmx5IHNjcmVl
biBhbmQgKG1heC13aWR0aDoxMDAwcHgpey5sZWZ0LWxheW91dF9fc2lkZWJhcnt3aWR0aDoxMDAl
O21hcmdpbjowfX0ubGVmdC1sYXlvdXRfX21haW57ZmxvYXQ6bGVmdDt3aWR0aDotd2Via2l0LWNh
bGMoNzUlIC0gMTVweCk7d2lkdGg6Y2FsYyg3NSUgLSAxNXB4KTttYXJnaW4tcmlnaHQ6MH1AbWVk
aWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6MTAwMHB4KXsubGVmdC1sYXlvdXRfX21haW57
d2lkdGg6MTAwJTttYXJnaW46MH19LnNwbGl0LWxheW91dHtkaXNwbGF5OmZsZXg7anVzdGlmeS1j
b250ZW50OnNwYWNlLWJldHdlZW47ZmxleC13cmFwOndyYXB9LnNwbGl0LWxheW91dD46Zmlyc3Qt
Y2hpbGR7cGFkZGluZy1yaWdodDozMHB4fS5zcGxpdC1sYXlvdXQ+KnttYXgtd2lkdGg6MTAwJX0u
c3BsaXQtbGF5b3V0PjpsYXN0LWNoaWxke3RleHQtYWxpZ246cmlnaHR9LnNwbGl0LWxheW91dC0t
bWlkZGxle2FsaWduLWl0ZW1zOmNlbnRlcn0uc3BsaXQtbGF5b3V0LS1zcGFjZWR7bWFyZ2luLXRv
cDotNXB4fS5zcGxpdC1sYXlvdXQtLXNwYWNlZD4qe21hcmdpbi10b3A6NXB4fS5zcGxpdC1sYXlv
dXQtLXRhYmxle2Rpc3BsYXk6dGFibGU7d2lkdGg6MTAwJTt0YWJsZS1sYXlvdXQ6Zml4ZWR9LnNw
bGl0LWxheW91dC0tdGFibGU+OmZpcnN0LWNoaWxkLC5zcGxpdC1sYXlvdXQtLXRhYmxlPjpsYXN0
LWNoaWxke2Zsb2F0Om5vbmU7ZGlzcGxheTp0YWJsZS1jZWxsO3ZlcnRpY2FsLWFsaWduOm1pZGRs
ZX0uc3BsaXQtbGF5b3V0LS1uby13cmFwe2ZsZXgtd3JhcDpub3dyYXA7YWxpZ24taXRlbXM6Y2Vu
dGVyfUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo4MDBweCl7LnNwbGl0LWxheW91
dC0td3JhcC1vbi10YWJsZXR7ZmxleC13cmFwOndyYXB9LnNwbGl0LWxheW91dC0td3JhcC1vbi10
YWJsZXQ+OmZpcnN0LWNoaWxkLC5zcGxpdC1sYXlvdXQtLXdyYXAtb24tdGFibGV0PjpsYXN0LWNo
aWxke2Rpc3BsYXk6YmxvY2s7d2lkdGg6MTAwJTtwYWRkaW5nOjB9LnNwbGl0LWxheW91dC0td3Jh
cC1vbi10YWJsZXQ+Omxhc3QtY2hpbGR7bWFyZ2luLXRvcDoxMHB4O3RleHQtYWxpZ246bGVmdH19
LnN0aWNrLXRvLXRvcHtwb3NpdGlvbjpmaXhlZDt0b3A6MDt3aWR0aDoxMDAlO3otaW5kZXg6OX0u
YWJvdXQtcHlwaXtkaXNwbGF5OnRhYmxlO3dpZHRoOjEwMCU7dGFibGUtbGF5b3V0OmZpeGVkO21h
eC13aWR0aDoxMTUwcHg7cGFkZGluZzowIDMwcHg7dGFibGUtbGF5b3V0OmF1dG87bWF4LXdpZHRo
OjEwMDBweDttYXJnaW46MCBhdXRvfS5hYm91dC1weXBpPjpmaXJzdC1jaGlsZCwuYWJvdXQtcHlw
aT46bGFzdC1jaGlsZHtmbG9hdDpub25lO2Rpc3BsYXk6dGFibGUtY2VsbDt2ZXJ0aWNhbC1hbGln
bjptaWRkbGV9LmFib3V0LXB5cGk6YWZ0ZXJ7Y2xlYXI6Ym90aDtjb250ZW50OiIiO2Rpc3BsYXk6
dGFibGV9QG1lZGlhIHNjcmVlbiBhbmQgKG1heC13aWR0aDo2MDBweCl7LmFib3V0LXB5cGl7cGFk
ZGluZzowIDE1cHh9fS5hYm91dC1weXBpX19sb2dve3BhZGRpbmctdG9wOjEwcHg7cGFkZGluZy1y
aWdodDo1MHB4fUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo2MDBweCl7LmFib3V0
LXB5cGlfX2xvZ297cGFkZGluZzowfX0uYWJvdXQtcHlwaV9fbG9nbyBpbWd7d2lkdGg6MjIwcHg7
bWF4LXdpZHRoOjEwMCU7bWFyZ2luOi0xNXB4IDUwcHggMCAwfUBtZWRpYSBvbmx5IHNjcmVlbiBh
bmQgKG1heC13aWR0aDo2MDBweCl7LmFib3V0LXB5cGlfX2xvZ28gaW1ne2Rpc3BsYXk6bm9uZX19
LmFib3V0LXB5cGlfX3RleHR7dGV4dC1hbGlnbjpsZWZ0fUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQg
KG1heC13aWR0aDo2MDBweCl7LmFib3V0LXB5cGlfX3RleHR7ZGlzcGxheTpibG9jazt3aWR0aDox
MDAlO21hcmdpbi1ib3R0b206LTEwcHh9fS5hY2NvcmRpb257bWFyZ2luLXRvcDoxMHB4fS5hY2Nv
cmRpb25fX2xpbmt7cGFkZGluZzo1cHg7ZGlzcGxheTpibG9jaztjdXJzb3I6cG9pbnRlcjtib3Jk
ZXI6MDtiYWNrZ3JvdW5kLWNvbG9yOnRyYW5zcGFyZW50O2NvbG9yOiMwMDZkYWQ7YmFja2dyb3Vu
ZC1pbWFnZTpub25lfS5hY2NvcmRpb25fX2xpbms6aG92ZXJ7YmFja2dyb3VuZC1pbWFnZTpub25l
fS5hY2NvcmRpb25fX2xpbms6YmVmb3Jle2ZvbnQtZmFtaWx5OkZvbnQgQXdlc29tZVwgNSBGcmVl
O2ZvbnQtd2VpZ2h0OjkwMDtjb250ZW50OiLvhLkiO21hcmdpbi1yaWdodDoxNXB4fUBtZWRpYSBv
bmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDoxMDAwcHgpey5hY2NvcmRpb25fX2xpbmt7Y29sb3I6
I2ZmZn0uYWNjb3JkaW9uX19saW5rOmFjdGl2ZSwuYWNjb3JkaW9uX19saW5rOmZvY3Vze291dGxp
bmU6MXB4IHNvbGlkICNmZmZ9fS5hY2NvcmRpb25fX2NvbnRlbnR7cGFkZGluZzowIDAgNXB4fS5h
Y2NvcmRpb25fX2NvbnRlbnQgYXtkaXNwbGF5OmJsb2NrO21hcmdpbi1yaWdodDoxMHB4fS5hY2Nv
cmRpb24tLWNsb3NlZCAuYWNjb3JkaW9uX19jb250ZW50e2Rpc3BsYXk6bm9uZX0uYWNjb3JkaW9u
LS1jbG9zZWQgLmFjY29yZGlvbl9fbGluazpiZWZvcmV7Zm9udC1mYW1pbHk6Rm9udCBBd2Vzb21l
XCA1IEZyZWU7Zm9udC13ZWlnaHQ6OTAwO2NvbnRlbnQ6Iu+EuiJ9LmFkbWluLWluY2x1ZGV7cGFk
ZGluZzo1MHB4O2JvcmRlci1jb2xvcjpyZWQ7Ym9yZGVyLXN0eWxlOmRvdHRlZH0uYWRtaW4taW5j
bHVkZSBmb3Jte2Rpc3BsYXk6aW5saW5lfS5hcHBsaWVkLWZpbHRlcnN7bWFyZ2luLXRvcDoxMHB4
O21hcmdpbi1ib3R0b206MTVweH0uYXBwbGllZC1maWx0ZXJzOmFmdGVye2NsZWFyOmJvdGg7Y29u
dGVudDoiIjtkaXNwbGF5OnRhYmxlfS5hcHBsaWVkLWZpbHRlcnNfX2FkZC1idXR0b257ZGlzcGxh
eTpub25lfUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDoxMDAwcHgpey5hcHBsaWVk
LWZpbHRlcnNfX2FkZC1idXR0b257ZGlzcGxheTppbmxpbmUtYmxvY2s7ZmxvYXQ6bGVmdH19LmF1
dGhvci1wcm9maWxle3BhZGRpbmctYm90dG9tOjMwcHh9QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAo
bWluLXdpZHRoOjEwMDBweCl7LmF1dGhvci1wcm9maWxle3BhZGRpbmctcmlnaHQ6MzBweH19QG1l
ZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjEwMDBweCkgYW5kIChtaW4td2lkdGg6NDAw
cHgpey5hdXRob3ItcHJvZmlsZXtwYWRkaW5nOjAgMCA0NXB4O2Rpc3BsYXk6ZmxleDthbGlnbi1p
dGVtczpmbGV4LXN0YXJ0fS5hdXRob3ItcHJvZmlsZSBpbWd7aGVpZ2h0OjE3NXB4O21hcmdpbi1y
aWdodDozMHB4fX1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6MTAwMHB4KXsuYXV0
aG9yLXByb2ZpbGVfX2luZm97cGFkZGluZy10b3A6MCFpbXBvcnRhbnR9fUBtZWRpYSBvbmx5IHNj
cmVlbiBhbmQgKG1heC13aWR0aDo0MDBweCl7LmF1dGhvci1wcm9maWxlIGltZ3tkaXNwbGF5Om5v
bmU7bWFyZ2luLXJpZ2h0OjB9fS5hdXRob3ItcHJvZmlsZV9faW5mb3twYWRkaW5nLXRvcDozMHB4
O3dvcmQtd3JhcDpicmVhay13b3JkfS5hdXRob3ItcHJvZmlsZV9fbmFtZXtmb250LXNpemU6MS4z
cmVtO2ZvbnQtd2VpZ2h0OjYwMDtwYWRkaW5nOjAgMCAxNXB4O3dvcmQtd3JhcDpicmVhay13b3Jk
fUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDoxMDAwcHgpey5hdXRob3ItcHJvZmls
ZV9fbmFtZXtib3JkZXItdG9wOjA7bWFyZ2luLXRvcDowO3BhZGRpbmctdG9wOjB9fS5hdXRob3It
cHJvZmlsZV9fbWV0YXttYXJnaW4tYm90dG9tOjMwcHg7d29yZC13cmFwOmJyZWFrLXdvcmR9LmF1
dGhvci1wcm9maWxlX19tZXRhZGl2e21hcmdpbi1ib3R0b206MTVweDt3b3JkLXdyYXA6YnJlYWst
d29yZH0uYXV0aG9yLXByb2ZpbGVfX2VkaXQtYnV0dG9ue21hcmdpbi1ib3R0b206MzBweDt3aWR0
aDoxMDAlO3RleHQtYWxpZ246Y2VudGVyfS5iYWRnZXtmb250LXNpemU6LjhyZW07dGV4dC10cmFu
c2Zvcm06dXBwZXJjYXNlO2JvcmRlcjoxcHggc29saWQgIzAwNmRhZDtiYWNrZ3JvdW5kLWNvbG9y
OiMwMDZkYWQ7Y29sb3I6I2ZmZjtwYWRkaW5nOjAgN3B4O2JvcmRlci1yYWRpdXM6M3B4O2ZvbnQt
d2VpZ2h0OjYwMDtiYWNrZ3JvdW5kLWltYWdlOm5vbmV9LmJhZGdlOmhvdmVye2JhY2tncm91bmQt
aW1hZ2U6bm9uZX0uYmFkZ2U6aG92ZXJ7Y29sb3I6I2ZmZn0uYmFkZ2U6YWN0aXZlLC5iYWRnZTpm
b2N1c3tib3JkZXItY29sb3I6I2ZmZjtvdXRsaW5lOjFweCBzb2xpZCAjMDA2ZGFkfS5iYWRnZS0t
c3VjY2Vzc3tiYWNrZ3JvdW5kLWNvbG9yOiMxNDgwMjQ7Ym9yZGVyLWNvbG9yOiMxNDgwMjR9LmJh
ZGdlLS1zdWNjZXNzOmFjdGl2ZSwuYmFkZ2UtLXN1Y2Nlc3M6Zm9jdXN7b3V0bGluZToxcHggc29s
aWQgIzE0ODAyNH0uYmFkZ2UtLWRhbmdlcntiYWNrZ3JvdW5kLWNvbG9yOiNkNTJkNDA7Ym9yZGVy
LWNvbG9yOiNkNTJkNDB9LmJhZGdlLS1kYW5nZXI6YWN0aXZlLC5iYWRnZS0tZGFuZ2VyOmZvY3Vz
e291dGxpbmU6MXB4IHNvbGlkICNkNTJkNDB9LmJhZGdlLS13YXJuaW5ne2JhY2tncm91bmQtY29s
b3I6I2ZmZGY3Njtib3JkZXItY29sb3I6I2ZmZGY3Njtjb2xvcjojNjY0ZTA0fS5iYWRnZS0td2Fy
bmluZzpob3Zlcntjb2xvcjojNjY0ZTA0fS5iYWRnZS0td2FybmluZzphY3RpdmUsLmJhZGdlLS13
YXJuaW5nOmZvY3Vze291dGxpbmU6MXB4IHNvbGlkICM2NjRlMDR9YS5iYWRnZXt0ZXh0LWRlY29y
YXRpb246dW5kZXJsaW5lfS5icmVhZGNydW1ic3twYWRkaW5nLWJvdHRvbToxNXB4fS5icmVhZGNy
dW1icyB1bHttYXJnaW46MDtwYWRkaW5nOjB9LmJyZWFkY3J1bWJzIHVsOmFmdGVye2NsZWFyOmJv
dGg7Y29udGVudDoiIjtkaXNwbGF5OnRhYmxlfS5icmVhZGNydW1ic19fYnJlYWRjcnVtYntsaXN0
LXN0eWxlLXR5cGU6bm9uZTtkaXNwbGF5OmlubGluZS1ibG9jaztmbG9hdDpsZWZ0fS5icmVhZGNy
dW1ic19fYnJlYWRjcnVtYjpub3QoOmxhc3QtY2hpbGQpOmFmdGVye2NvbnRlbnQ6Iu+BlCI7Zm9u
dC1mYW1pbHk6Rm9udCBBd2Vzb21lXCA1IEZyZWU7Zm9udC13ZWlnaHQ6OTAwO21hcmdpbjowIDVw
eDtjb2xvcjojYmJiO2ZvbnQtc2l6ZToxMnB4fS5idXR0b257cG9zaXRpb246cmVsYXRpdmU7Zm9u
dC13ZWlnaHQ6NjAwO2N1cnNvcjpwb2ludGVyO3BhZGRpbmc6OC41cHggMTVweDtiYWNrZ3JvdW5k
LWNvbG9yOnRyYW5zcGFyZW50O2NvbG9yOiM2MDYwNjA7Ym9yZGVyOjFweCBzb2xpZCAjOTQ5NDk0
O2JvcmRlci1yYWRpdXM6M3B4O2Rpc3BsYXk6aW5saW5lLWJsb2NrO3RleHQtYWxpZ246Y2VudGVy
O2JhY2tncm91bmQtaW1hZ2U6bm9uZX0uYnV0dG9uOmhvdmVye2JhY2tncm91bmQtaW1hZ2U6bm9u
ZX0uYnV0dG9uIGkuZmF7cG9zaXRpb246cmVsYXRpdmU7dG9wOjJweH0uYnV0dG9uOmFjdGl2ZSwu
YnV0dG9uOmZvY3VzLC5idXR0b246aG92ZXJ7Ym9yZGVyLWNvbG9yOiMwMDZkYWQ7Y29sb3I6IzAw
NGQ3YTt6LWluZGV4OjE7b3V0bGluZTpub25lfS5idXR0b24tLXNtYWxse2ZvbnQtc2l6ZTouOHJl
bTtwYWRkaW5nOjZweCA4cHh9LmJ1dHRvbi0tcHJpbWFyeXtib3JkZXItY29sb3I6IzAwNmRhZDti
YWNrZ3JvdW5kLWNvbG9yOiMwMDZkYWQ7Y29sb3I6I2ZmZjt6LWluZGV4OjJ9LmJ1dHRvbi0tcHJp
bWFyeTphY3RpdmUsLmJ1dHRvbi0tcHJpbWFyeTpmb2N1cywuYnV0dG9uLS1wcmltYXJ5OmhvdmVy
e2JvcmRlci1jb2xvcjojMDA0ZDdhO2JhY2tncm91bmQtY29sb3I6IzAwNTA3Zjt0ZXh0LWRlY29y
YXRpb24tY29sb3I6aHNsYSgwLDAlLDEwMCUsLjIpO2NvbG9yOiNmZmZ9LmJ1dHRvbi0tcHJpbWFy
eTphY3RpdmUsLmJ1dHRvbi0tcHJpbWFyeTpmb2N1c3tib3JkZXItY29sb3I6I2ZmZn0uYnV0dG9u
LS1wcmltYXJ5OmFjdGl2ZTphY3RpdmUsLmJ1dHRvbi0tcHJpbWFyeTphY3RpdmU6Zm9jdXMsLmJ1
dHRvbi0tcHJpbWFyeTpmb2N1czphY3RpdmUsLmJ1dHRvbi0tcHJpbWFyeTpmb2N1czpmb2N1c3tv
dXRsaW5lOjFweCBzb2xpZCAjMDA2ZGFkfS5idXR0b24tLWRhbmdlcntib3JkZXItY29sb3I6I2Q1
MmQ0MDtiYWNrZ3JvdW5kLWNvbG9yOiNkNTJkNDA7Y29sb3I6I2ZmZn0uYnV0dG9uLS1kYW5nZXI6
YWN0aXZlLC5idXR0b24tLWRhbmdlcjpmb2N1cywuYnV0dG9uLS1kYW5nZXI6aG92ZXJ7Ym9yZGVy
LWNvbG9yOiNjMjI3Mzg7YmFja2dyb3VuZC1jb2xvcjojYzYyODNhO3RleHQtZGVjb3JhdGlvbi1j
b2xvcjpoc2xhKDAsMCUsMTAwJSwuMik7Y29sb3I6I2ZmZn0uYnV0dG9uLS1kYW5nZXI6YWN0aXZl
LC5idXR0b24tLWRhbmdlcjpmb2N1c3tib3JkZXItY29sb3I6I2ZmZn0uYnV0dG9uLS1kYW5nZXI6
YWN0aXZlOmFjdGl2ZSwuYnV0dG9uLS1kYW5nZXI6YWN0aXZlOmZvY3VzLC5idXR0b24tLWRhbmdl
cjpmb2N1czphY3RpdmUsLmJ1dHRvbi0tZGFuZ2VyOmZvY3VzOmZvY3Vze291dGxpbmU6MXB4IHNv
bGlkICNkNTJkNDB9LmJ1dHRvbi0tZGlzYWJsZWQsLmJ1dHRvbltkaXNhYmxlZF17Y3Vyc29yOm5v
dC1hbGxvd2VkO2JhY2tncm91bmQtY29sb3I6I2YwZjBmMDtib3JkZXItY29sb3I6I2YwZjBmMDtj
b2xvcjojZGVkZWRlO3RleHQtZGVjb3JhdGlvbjpsaW5lLXRocm91Z2g7cG9pbnRlci1ldmVudHM6
bm9uZX0uYnV0dG9uLS1kaXNhYmxlZDphY3RpdmUsLmJ1dHRvbi0tZGlzYWJsZWQ6Zm9jdXMsLmJ1
dHRvbi0tZGlzYWJsZWQ6aG92ZXIsLmJ1dHRvbltkaXNhYmxlZF06YWN0aXZlLC5idXR0b25bZGlz
YWJsZWRdOmZvY3VzLC5idXR0b25bZGlzYWJsZWRdOmhvdmVye2JhY2tncm91bmQtY29sb3I6I2Yw
ZjBmMDtib3JkZXItY29sb3I6I2YwZjBmMDtjb2xvcjojZGVkZWRlO291dGxpbmU6bm9uZX0uYnV0
dG9uLS1zd2l0Y2gtdG8tZGVza3RvcHtib3JkZXItY29sb3I6aHNsYSgwLDAlLDEwMCUsLjcpO2Nv
bG9yOiNmZmY7bWFyZ2luOjMwcHggYXV0byAwfS5idXR0b24tLXN3aXRjaC10by1kZXNrdG9wOmFj
dGl2ZSwuYnV0dG9uLS1zd2l0Y2gtdG8tZGVza3RvcDpmb2N1cywuYnV0dG9uLS1zd2l0Y2gtdG8t
ZGVza3RvcDpob3Zlcntib3JkZXItY29sb3I6I2ZmZjtjb2xvcjojZmZmfS5idXR0b24tLXN3aXRj
aC10by1tb2JpbGV7Zm9udC1zaXplOjUwMCU7cGFkZGluZzo0MHB4O2hlaWdodDphdXRvO21hcmdp
bjoyNXB4O2JvcmRlci1yYWRpdXM6MjVweDt3aWR0aDpjYWxjKDEwMCUgLSA1MHB4KX0uYnV0dG9u
LWdyb3Vwe2Rpc3BsYXk6YmxvY2t9LmJ1dHRvbi1ncm91cDphZnRlcntjbGVhcjpib3RoO2NvbnRl
bnQ6IiI7ZGlzcGxheTp0YWJsZX0uYnV0dG9uLWdyb3VwX19idXR0b257ZmxvYXQ6bGVmdDtib3Jk
ZXItcmFkaXVzOjB9LmJ1dHRvbi1ncm91cCAuYnV0dG9uLWdyb3VwX19idXR0b24rLmJ1dHRvbi1n
cm91cF9fYnV0dG9ue21hcmdpbi1sZWZ0Oi0xcHh9LmJ1dHRvbi1ncm91cF9fYnV0dG9uOmZpcnN0
LWNoaWxke2JvcmRlci1yYWRpdXM6M3B4IDAgMCAzcHh9LmJ1dHRvbi1ncm91cF9fYnV0dG9uOmxh
c3QtY2hpbGR7Ym9yZGVyLXJhZGl1czowIDNweCAzcHggMH0uYnV0dG9uLWdyb3VwLS1wYWdpbmF0
aW9ue21hcmdpbi10b3A6NDBweH1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAw
cHgpey5idXR0b24tZ3JvdXAtLXBhZ2luYXRpb24gLmJ1dHRvbi1ncm91cF9fYnV0dG9uOm5vdCg6
Zmlyc3QtY2hpbGQpOm5vdCg6bGFzdC1jaGlsZCl7ZGlzcGxheTpub25lfX0uY2FsbG91dC1ibG9j
a3twYWRkaW5nOjE1cHggMTVweCAxNXB4IDMwcHg7Ym9yZGVyOjJweCBzb2xpZCAjMDA2ZGFkO21h
cmdpbjoxNXB4IDA7cG9zaXRpb246cmVsYXRpdmU7Ym9yZGVyLXJhZGl1czo0cHh9LmNhbGxvdXQt
YmxvY2tfX2Rpc21pc3N7YmFja2dyb3VuZDp0cmFuc3BhcmVudDtib3JkZXI6MDtwb3NpdGlvbjph
YnNvbHV0ZTt0b3A6MTZweDtyaWdodDoxNXB4O2ZvbnQtc2l6ZToxOHB4O3BhZGRpbmc6MDt3aWR0
aDoyMnB4O2hlaWdodDoyMnB4O2N1cnNvcjpwb2ludGVyO3RleHQtYWxpZ246Y2VudGVyO2JhY2tn
cm91bmQtaW1hZ2U6bm9uZX0uY2FsbG91dC1ibG9ja19fZGlzbWlzczphY3RpdmUsLmNhbGxvdXQt
YmxvY2tfX2Rpc21pc3M6aG92ZXJ7YmFja2dyb3VuZC1pbWFnZTpub25lfS5jYWxsb3V0LWJsb2Nr
X19oZWFkaW5ne2ZvbnQtc2l6ZToxLjE1cmVtO2ZvbnQtd2VpZ2h0OjYwMH0uY2FsbG91dC1ibG9j
azpiZWZvcmV7Y29udGVudDoiIjt3aWR0aDoxNXB4O2JhY2tncm91bmQtY29sb3I6IzAwNmRhZDtw
b3NpdGlvbjphYnNvbHV0ZTt0b3A6LTFweDtsZWZ0Oi0ycHg7aGVpZ2h0OmNhbGMoMTAwJSArIDJw
eCk7Ym9yZGVyLXJhZGl1czozcHggMCAwIDNweH0uY2FsbG91dC1ibG9jay0tYm90dG9tLW1hcmdp
bnttYXJnaW4tYm90dG9tOjE1cHh9LmNhbGxvdXQtYmxvY2stLWRpc21pc3NlZHtkaXNwbGF5Om5v
bmV9LmNhbGxvdXQtYmxvY2stLWRhbmdlcntib3JkZXItY29sb3I6I2Q1MmQ0MH0uY2FsbG91dC1i
bG9jay0tZGFuZ2VyPjpub3QoLm1vZGFsKTpub3QoLmJ1dHRvbil7Y29sb3I6I2Q1MmQ0MH0uY2Fs
bG91dC1ibG9jay0tZGFuZ2VyPjpub3QoLm1vZGFsKTpub3QoLmJ1dHRvbikgYTpub3QoLmJ1dHRv
bil7Y29sb3I6I2Q1MmQ0MDtiYWNrZ3JvdW5kLWltYWdlOmxpbmVhci1ncmFkaWVudCg5MGRlZywj
ZDUyZDQwLHJnYmEoMjEzLDQ1LDY0LC43KSl9LmNhbGxvdXQtYmxvY2stLWRhbmdlcj46bm90KC5t
b2RhbCk6bm90KC5idXR0b24pIGE6bm90KC5idXR0b24pOmhvdmVye2NvbG9yOiNhZDIzMzI7YmFj
a2dyb3VuZC1pbWFnZTpsaW5lYXItZ3JhZGllbnQoOTBkZWcsI2FkMjMzMiwjYWQyMzMyKX0uY2Fs
bG91dC1ibG9jay0tZGFuZ2VyPjpub3QoLm1vZGFsKTpub3QoLmJ1dHRvbikgYTpub3QoLmJ1dHRv
bik6YWN0aXZlLC5jYWxsb3V0LWJsb2NrLS1kYW5nZXI+Om5vdCgubW9kYWwpOm5vdCguYnV0dG9u
KSBhOm5vdCguYnV0dG9uKTpmb2N1c3tvdXRsaW5lOjFweCBzb2xpZCAjZDUyZDQwfS5jYWxsb3V0
LWJsb2NrLS1kYW5nZXI6YmVmb3Jle2JhY2tncm91bmQtY29sb3I6I2Q1MmQ0MH0uY2FsbG91dC1i
bG9jay0tZGFuZ2VyIC5jYWxsb3V0LWJsb2NrX19kaXNtaXNzOmFjdGl2ZSwuY2FsbG91dC1ibG9j
ay0tZGFuZ2VyIC5jYWxsb3V0LWJsb2NrX19kaXNtaXNzOmZvY3Vze291dGxpbmU6MXB4IHNvbGlk
ICNkNTJkNDB9LmNhbGxvdXQtYmxvY2stLXdhcm5pbmd7Ym9yZGVyLWNvbG9yOiM2NjRlMDR9LmNh
bGxvdXQtYmxvY2stLXdhcm5pbmc+Om5vdCgubW9kYWwpOm5vdCguYnV0dG9uKXtjb2xvcjojNjY0
ZTA0fS5jYWxsb3V0LWJsb2NrLS13YXJuaW5nPjpub3QoLm1vZGFsKTpub3QoLmJ1dHRvbikgYTpu
b3QoLmJ1dHRvbil7Y29sb3I6IzY2NGUwNDtiYWNrZ3JvdW5kLWltYWdlOmxpbmVhci1ncmFkaWVu
dCg5MGRlZywjNjY0ZTA0LHJnYmEoMTAyLDc4LDQsLjcpKX0uY2FsbG91dC1ibG9jay0td2Fybmlu
Zz46bm90KC5tb2RhbCk6bm90KC5idXR0b24pIGE6bm90KC5idXR0b24pOmhvdmVye2NvbG9yOiMz
NTI4MDI7YmFja2dyb3VuZC1pbWFnZTpsaW5lYXItZ3JhZGllbnQoOTBkZWcsIzM1MjgwMiwjMzUy
ODAyKX0uY2FsbG91dC1ibG9jay0td2FybmluZz46bm90KC5tb2RhbCk6bm90KC5idXR0b24pIGE6
bm90KC5idXR0b24pOmFjdGl2ZSwuY2FsbG91dC1ibG9jay0td2FybmluZz46bm90KC5tb2RhbCk6
bm90KC5idXR0b24pIGE6bm90KC5idXR0b24pOmZvY3Vze291dGxpbmU6MXB4IHNvbGlkICM2NjRl
MDR9LmNhbGxvdXQtYmxvY2stLXdhcm5pbmc6YmVmb3Jle2JhY2tncm91bmQtY29sb3I6IzY2NGUw
NH0uY2FsbG91dC1ibG9jay0td2FybmluZyAuY2FsbG91dC1ibG9ja19fZGlzbWlzczphY3RpdmUs
LmNhbGxvdXQtYmxvY2stLXdhcm5pbmcgLmNhbGxvdXQtYmxvY2tfX2Rpc21pc3M6Zm9jdXN7b3V0
bGluZToxcHggc29saWQgIzY2NGUwNH0uY2FsbG91dC1ibG9jay0tc3VjY2Vzc3tib3JkZXItY29s
b3I6IzE0ODAyNH0uY2FsbG91dC1ibG9jay0tc3VjY2Vzcz46bm90KC5tb2RhbCk6bm90KC5idXR0
b24pe2NvbG9yOiMxNDgwMjR9LmNhbGxvdXQtYmxvY2stLXN1Y2Nlc3M+Om5vdCgubW9kYWwpOm5v
dCguYnV0dG9uKSBhOm5vdCguYnV0dG9uKXtjb2xvcjojMTQ4MDI0O2JhY2tncm91bmQtaW1hZ2U6
bGluZWFyLWdyYWRpZW50KDkwZGVnLCMxNDgwMjQscmdiYSgyMCwxMjgsMzYsLjcpKX0uY2FsbG91
dC1ibG9jay0tc3VjY2Vzcz46bm90KC5tb2RhbCk6bm90KC5idXR0b24pIGE6bm90KC5idXR0b24p
OmhvdmVye2NvbG9yOiMwZDU0MTg7YmFja2dyb3VuZC1pbWFnZTpsaW5lYXItZ3JhZGllbnQoOTBk
ZWcsIzBkNTQxOCwjMGQ1NDE4KX0uY2FsbG91dC1ibG9jay0tc3VjY2Vzcz46bm90KC5tb2RhbCk6
bm90KC5idXR0b24pIGE6bm90KC5idXR0b24pOmFjdGl2ZSwuY2FsbG91dC1ibG9jay0tc3VjY2Vz
cz46bm90KC5tb2RhbCk6bm90KC5idXR0b24pIGE6bm90KC5idXR0b24pOmZvY3Vze291dGxpbmU6
MXB4IHNvbGlkICMxNDgwMjR9LmNhbGxvdXQtYmxvY2stLXN1Y2Nlc3M6YmVmb3Jle2JhY2tncm91
bmQtY29sb3I6IzE0ODAyNH0uY2FsbG91dC1ibG9jay0tc3VjY2VzcyAuY2FsbG91dC1ibG9ja19f
ZGlzbWlzczphY3RpdmUsLmNhbGxvdXQtYmxvY2stLXN1Y2Nlc3MgLmNhbGxvdXQtYmxvY2tfX2Rp
c21pc3M6Zm9jdXN7b3V0bGluZToxcHggc29saWQgIzE0ODAyNH0uY2VudGVyZWQtaGVhZGluZ3t0
ZXh0LWFsaWduOmNlbnRlcn0uY2VudGVyZWQtaGVhZGluZ19fdGl0bGV7Zm9udC1zaXplOjEuNXJl
bTtmb250LXdlaWdodDo2MDA7cGFkZGluZy1ib3R0b206MH0uY2VudGVyZWQtaGVhZGluZ19fcnVs
ZXttYXgtd2lkdGg6MzAwcHg7bWFyZ2luOjE1cHggYXV0byA2MHB4O2JhY2tncm91bmQ6I2VjZWNl
Y31AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAwcHgpey5jZW50ZXJlZC1oZWFk
aW5nX19ydWxle2Rpc3BsYXk6bm9uZX19LmNoZWNrYm94LXRyZWV7bWFyZ2luLWxlZnQ6OHB4fS5j
aGVja2JveC10cmVlIHVse21hcmdpbjo1cHggMCAwIDEycHg7bGlzdC1zdHlsZTpub25lfS5jaGVj
a2JveC10cmVlIGxpLC5jaGVja2JveC10cmVlIHVse3Bvc2l0aW9uOnJlbGF0aXZlO3BhZGRpbmc6
MCAwIDAgNXB4fS5jaGVja2JveC10cmVlIGxpOmJlZm9yZXtjb250ZW50OiIiO3Bvc2l0aW9uOmFi
c29sdXRlO2xlZnQ6LTEycHg7dG9wOjEzcHg7d2lkdGg6MTJweDtoZWlnaHQ6MDtib3JkZXItdG9w
OjJweCBzb2xpZCAjYmJifUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDoxMDAwcHgp
ey5jaGVja2JveC10cmVlIGxpOmJlZm9yZXtib3JkZXItdG9wLWNvbG9yOiM5NGQ3ZmZ9fS5jaGVj
a2JveC10cmVlIGxpOmFmdGVye2NvbnRlbnQ6IiI7cG9zaXRpb246YWJzb2x1dGU7bGVmdDotMTJw
eDtoZWlnaHQ6MTAwJTt3aWR0aDowO3RvcDotMnB4O2JvcmRlci1sZWZ0OjJweCBzb2xpZCAjYmJi
fUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDoxMDAwcHgpey5jaGVja2JveC10cmVl
IGxpOmFmdGVye2JvcmRlci1sZWZ0LWNvbG9yOiM5NGQ3ZmZ9fS5jaGVja2JveC10cmVlIHVsPmxp
Omxhc3QtY2hpbGQ6YWZ0ZXJ7aGVpZ2h0OjE3cHh9LmNoZWNrYm94LXRyZWVfX2NoZWNrYm94e3Bv
c2l0aW9uOnJlbGF0aXZlO3RvcDozcHh9QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4LXdpZHRo
OjEwMDBweCl7LmNoZWNrYm94LXRyZWVfX2NoZWNrYm94W3R5cGU9Y2hlY2tib3hdOmFjdGl2ZSwu
Y2hlY2tib3gtdHJlZV9fY2hlY2tib3hbdHlwZT1jaGVja2JveF06Zm9jdXN7b3V0bGluZToxcHgg
c29saWQgI2ZmZn19LmNoZWNrYm94LXRyZWVfX2xhYmVse2ZvbnQtc2l6ZTouOHJlbTtjdXJzb3I6
cG9pbnRlcjtsaW5lLWhlaWdodDoxfS5jb2RlLWJsb2Nre2Rpc3BsYXk6YmxvY2s7cGFkZGluZzox
NXB4O21hcmdpbi1ib3R0b206MTVweDt3b3JkLWJyZWFrOmJyZWFrLWFsbDtkaXJlY3Rpb246bHRy
fS5jb3B5LXRvb2x0aXB7cG9zaXRpb246cmVsYXRpdmU7Y3Vyc29yOnBvaW50ZXJ9LmNvcHktdG9v
bHRpcDphZnRlcntjb250ZW50OmF0dHIoZGF0YS10b29sdGlwLWxhYmVsKTtwb3NpdGlvbjphYnNv
bHV0ZTt6LWluZGV4OjEwMDAwMDA7ZGlzcGxheTpub25lO3BhZGRpbmc6NXB4IDhweDtmb250LXdl
aWdodDo0MDA7LXdlYmtpdC1mb250LXNtb290aGluZzpzdWJwaXhlbC1hbnRpYWxpYXNlZDtjb2xv
cjojZmZmO3RleHQtYWxpZ246Y2VudGVyO3RleHQtZGVjb3JhdGlvbjpub25lO3RleHQtc2hhZG93
Om5vbmU7dGV4dC10cmFuc2Zvcm06bm9uZTtsZXR0ZXItc3BhY2luZzpub3JtYWw7d29yZC13cmFw
OmJyZWFrLXdvcmQ7d2hpdGUtc3BhY2U6cHJlO3BvaW50ZXItZXZlbnRzOm5vbmU7YmFja2dyb3Vu
ZDpyZ2JhKDAsMCwwLC43KTtib3JkZXItcmFkaXVzOjJweDtvcGFjaXR5OjB9LmNvcHktdG9vbHRp
cDpiZWZvcmV7cG9zaXRpb246YWJzb2x1dGU7ei1pbmRleDoxMDAwMDAxO2Rpc3BsYXk6bm9uZTt3
aWR0aDowO2hlaWdodDowO2NvbG9yOnJnYmEoMCwwLDAsLjcpO3BvaW50ZXItZXZlbnRzOm5vbmU7
Y29udGVudDoiIjtib3JkZXI6NXB4IHNvbGlkIHRyYW5zcGFyZW50O29wYWNpdHk6MH1Aa2V5ZnJh
bWVzIHRvb2x0aXAtYXBwZWFyezAle29wYWNpdHk6MH10b3tvcGFjaXR5OjF9fS5jb3B5LXRvb2x0
aXAtaW1tZWRpYXRlOmFmdGVyLC5jb3B5LXRvb2x0aXAtaW1tZWRpYXRlOmJlZm9yZSwuY29weS10
b29sdGlwOmFjdGl2ZTphZnRlciwuY29weS10b29sdGlwOmFjdGl2ZTpiZWZvcmUsLmNvcHktdG9v
bHRpcDpmb2N1czphZnRlciwuY29weS10b29sdGlwOmZvY3VzOmJlZm9yZSwuY29weS10b29sdGlw
OmhvdmVyOmFmdGVyLC5jb3B5LXRvb2x0aXA6aG92ZXI6YmVmb3Jle2Rpc3BsYXk6aW5saW5lLWJs
b2NrO3RleHQtZGVjb3JhdGlvbjpub25lO2FuaW1hdGlvbi1uYW1lOnRvb2x0aXAtYXBwZWFyO2Fu
aW1hdGlvbi1kdXJhdGlvbjouMXM7YW5pbWF0aW9uLWZpbGwtbW9kZTpmb3J3YXJkczthbmltYXRp
b24tdGltaW5nLWZ1bmN0aW9uOmVhc2UtaW47YW5pbWF0aW9uLWRlbGF5Oi40c30uY29weS10b29s
dGlwLW5vLWRlbGF5OmFjdGl2ZTphZnRlciwuY29weS10b29sdGlwLW5vLWRlbGF5OmFjdGl2ZTpi
ZWZvcmUsLmNvcHktdG9vbHRpcC1uby1kZWxheTpmb2N1czphZnRlciwuY29weS10b29sdGlwLW5v
LWRlbGF5OmZvY3VzOmJlZm9yZSwuY29weS10b29sdGlwLW5vLWRlbGF5OmhvdmVyOmFmdGVyLC5j
b3B5LXRvb2x0aXAtbm8tZGVsYXk6aG92ZXI6YmVmb3Jle29wYWNpdHk6MTthbmltYXRpb246bm9u
ZX0uY29weS10b29sdGlwLW11bHRpbGluZTphY3RpdmU6YWZ0ZXIsLmNvcHktdG9vbHRpcC1tdWx0
aWxpbmU6Zm9jdXM6YWZ0ZXIsLmNvcHktdG9vbHRpcC1tdWx0aWxpbmU6aG92ZXI6YWZ0ZXJ7ZGlz
cGxheTp0YWJsZS1jZWxsfS5jb3B5LXRvb2x0aXAtczphZnRlciwuY29weS10b29sdGlwLXNlOmFm
dGVyLC5jb3B5LXRvb2x0aXAtc3c6YWZ0ZXJ7dG9wOjEwMCU7cmlnaHQ6NTAlO21hcmdpbi10b3A6
NXB4fS5jb3B5LXRvb2x0aXAtczpiZWZvcmUsLmNvcHktdG9vbHRpcC1zZTpiZWZvcmUsLmNvcHkt
dG9vbHRpcC1zdzpiZWZvcmV7dG9wOmF1dG87cmlnaHQ6NTAlO2JvdHRvbTotNXB4O21hcmdpbi1y
aWdodDotNXB4O2JvcmRlci1ib3R0b20tY29sb3I6cmdiYSgwLDAsMCwuNyl9LmNvcHktdG9vbHRp
cC1zZTphZnRlcntyaWdodDphdXRvO2xlZnQ6NTAlO21hcmdpbi1sZWZ0Oi0xNXB4fS5jb3B5LXRv
b2x0aXAtc3c6YWZ0ZXJ7bWFyZ2luLXJpZ2h0Oi0xNXB4fS5jb3B5LXRvb2x0aXAtbjphZnRlciwu
Y29weS10b29sdGlwLW5lOmFmdGVyLC5jb3B5LXRvb2x0aXAtbnc6YWZ0ZXJ7cmlnaHQ6NTAlO2Jv
dHRvbToxMDAlO21hcmdpbi1ib3R0b206NXB4fS5jb3B5LXRvb2x0aXAtbjpiZWZvcmUsLmNvcHkt
dG9vbHRpcC1uZTpiZWZvcmUsLmNvcHktdG9vbHRpcC1udzpiZWZvcmV7dG9wOi01cHg7cmlnaHQ6
NTAlO2JvdHRvbTphdXRvO21hcmdpbi1yaWdodDotNXB4O2JvcmRlci10b3AtY29sb3I6cmdiYSgw
LDAsMCwuNyl9LmNvcHktdG9vbHRpcC1uZTphZnRlcntyaWdodDphdXRvO2xlZnQ6NTAlO21hcmdp
bi1sZWZ0Oi0xNXB4fS5jb3B5LXRvb2x0aXAtbnc6YWZ0ZXJ7bWFyZ2luLXJpZ2h0Oi0xNXB4fS5j
b3B5LXRvb2x0aXAtbjphZnRlciwuY29weS10b29sdGlwLXM6YWZ0ZXJ7dHJhbnNmb3JtOnRyYW5z
bGF0ZVgoNTAlKX0uY29weS10b29sdGlwLXc6YWZ0ZXJ7cmlnaHQ6MTAwJTtib3R0b206NTAlO21h
cmdpbi1yaWdodDo1cHg7dHJhbnNmb3JtOnRyYW5zbGF0ZVkoNTAlKX0uY29weS10b29sdGlwLXc6
YmVmb3Jle3RvcDo1MCU7Ym90dG9tOjUwJTtsZWZ0Oi01cHg7bWFyZ2luLXRvcDotNXB4O2JvcmRl
ci1sZWZ0LWNvbG9yOnJnYmEoMCwwLDAsLjcpfS5jb3B5LXRvb2x0aXAtZTphZnRlcntib3R0b206
NTAlO2xlZnQ6MTAwJTttYXJnaW4tbGVmdDo1cHg7dHJhbnNmb3JtOnRyYW5zbGF0ZVkoNTAlKX0u
Y29weS10b29sdGlwLWU6YmVmb3Jle3RvcDo1MCU7cmlnaHQ6LTVweDtib3R0b206NTAlO21hcmdp
bi10b3A6LTVweDtib3JkZXItcmlnaHQtY29sb3I6cmdiYSgwLDAsMCwuNyl9QG1lZGlhIG9ubHkg
c2NyZWVuIGFuZCAobWF4LXdpZHRoOjEwMDBweCl7LmRhcmstb3ZlcmxheXtkaXNwbGF5Om5vbmU7
cG9zaXRpb246Zml4ZWQ7dG9wOjA7cmlnaHQ6MDtib3R0b206MDtsZWZ0OjA7YmFja2dyb3VuZC1j
b2xvcjpyZ2JhKDAsMCwwLC41KTt6LWluZGV4OjEwO3BvaW50ZXItZXZlbnRzOm5vbmU7dHJhbnNp
dGlvbjpvcGFjaXR5IC4zc319LmRyb3Bkb3due3Bvc2l0aW9uOnJlbGF0aXZlO2Rpc3BsYXk6aW5s
aW5lLWJsb2NrfS5kcm9wZG93biBsaSwuZHJvcGRvd24gdWx7bWFyZ2luOjA7cGFkZGluZzowO2xp
c3Qtc3R5bGUtdHlwZTpub25lfS5kcm9wZG93bl9fdHJpZ2dlcntjdXJzb3I6cG9pbnRlcjt3aGl0
ZS1zcGFjZTpub3dyYXB9LmRyb3Bkb3duX190cmlnZ2VyLWNhcmV0LC5kcm9wZG93bl9fdHJpZ2dl
ci1jYXJldDpob3ZlcnttYXJnaW4tbGVmdDo1cHg7dGV4dC1kZWNvcmF0aW9uOm5vbmV9LmRyb3Bk
b3duX19jb250ZW50e3Bvc2l0aW9uOmFic29sdXRlO3JpZ2h0OjA7bWFyZ2luLWJvdHRvbTotNHB4
O2JveC1zaGFkb3c6MXB4IDFweCAycHggMXB4IHJnYmEoMCwwLDAsLjA1KTt6LWluZGV4Ojg7Ym9y
ZGVyOjFweCBzb2xpZCAjZDNkM2QzO2JvcmRlci1ib3R0b206MDtkaXNwbGF5Om5vbmV9LmRyb3Bk
b3duX19saW5rLC5kcm9wZG93biBidXR0b24uZHJvcGRvd25fX2xpbmt7ZGlzcGxheTpibG9jaztw
YWRkaW5nOjE1cHg7Ym9yZGVyOjA7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgI2QzZDNkMztiYWNr
Z3JvdW5kLWNvbG9yOiNmZmY7bWluLXdpZHRoOjE4MHB4O2NvbG9yOiM0NjQ2NDY7Y3Vyc29yOnBv
aW50ZXI7dGV4dC1hbGlnbjpsZWZ0O3Bvc2l0aW9uOnJlbGF0aXZlO2JhY2tncm91bmQtaW1hZ2U6
bm9uZX0uZHJvcGRvd25fX2xpbms6aG92ZXIsLmRyb3Bkb3duIGJ1dHRvbi5kcm9wZG93bl9fbGlu
azpob3ZlcntiYWNrZ3JvdW5kLWltYWdlOm5vbmV9LmRyb3Bkb3duX19saW5rOmFjdGl2ZSwuZHJv
cGRvd25fX2xpbms6Zm9jdXMsLmRyb3Bkb3duX19saW5rOmhvdmVyLC5kcm9wZG93biBidXR0b24u
ZHJvcGRvd25fX2xpbms6YWN0aXZlLC5kcm9wZG93biBidXR0b24uZHJvcGRvd25fX2xpbms6Zm9j
dXMsLmRyb3Bkb3duIGJ1dHRvbi5kcm9wZG93bl9fbGluazpob3ZlcntiYWNrZ3JvdW5kLWNvbG9y
OiNmNGZiZmY7Y29sb3I6IzAwNGQ3YX0uZHJvcGRvd25fX2xpbms6YWN0aXZlLC5kcm9wZG93bl9f
bGluazpmb2N1cywuZHJvcGRvd24gYnV0dG9uLmRyb3Bkb3duX19saW5rOmFjdGl2ZSwuZHJvcGRv
d24gYnV0dG9uLmRyb3Bkb3duX19saW5rOmZvY3Vze291dGxpbmU6MXB4IHNvbGlkICMwMDZkYWQ7
Ym9yZGVyLWJvdHRvbS1jb2xvcjojMDA2ZGFkfS5kcm9wZG93bl9fbGluayAuZmEsLmRyb3Bkb3du
IGJ1dHRvbi5kcm9wZG93bl9fbGluayAuZmF7Zm9udC1zaXplOjE0cHg7cG9zaXRpb246YWJzb2x1
dGU7bGVmdDoxNXB4O3RvcDpjYWxjKDUwJSAtIDdweCl9LmRyb3Bkb3duLS1vbi1tZW51IGJ1dHRv
biwuZHJvcGRvd24tLW9uLW1lbnUgZm9ybXtib3JkZXI6MDtiYWNrZ3JvdW5kLWNvbG9yOnRyYW5z
cGFyZW50O3BhZGRpbmc6MH0uZHJvcGRvd24tLW9uLW1lbnUgLmRyb3Bkb3duX19jb250ZW50e2Jv
cmRlci1jb2xvcjojMDA2N2EzO21hcmdpbi1ib3R0b206MH0uZHJvcGRvd24tLW9uLW1lbnUgLmRy
b3Bkb3duX19saW5rLC5kcm9wZG93bi0tb24tbWVudSBidXR0b24uZHJvcGRvd25fX2xpbmt7Ym9y
ZGVyLWJvdHRvbS1jb2xvcjojMDA2N2EzO2JhY2tncm91bmQtY29sb3I6IzAwNzNiNztjb2xvcjoj
ZmZmfS5kcm9wZG93bi0tb24tbWVudSAuZHJvcGRvd25fX2xpbmsgYSwuZHJvcGRvd24tLW9uLW1l
bnUgYnV0dG9uLmRyb3Bkb3duX19saW5rIGF7Y29sb3I6I2ZmZjt0ZXh0LWRlY29yYXRpb246bm9u
ZX0uZHJvcGRvd24tLW9uLW1lbnUgLmRyb3Bkb3duX19saW5rOmFjdGl2ZSwuZHJvcGRvd24tLW9u
LW1lbnUgLmRyb3Bkb3duX19saW5rOmZvY3VzLC5kcm9wZG93bi0tb24tbWVudSAuZHJvcGRvd25f
X2xpbms6aG92ZXIsLmRyb3Bkb3duLS1vbi1tZW51IGJ1dHRvbi5kcm9wZG93bl9fbGluazphY3Rp
dmUsLmRyb3Bkb3duLS1vbi1tZW51IGJ1dHRvbi5kcm9wZG93bl9fbGluazpmb2N1cywuZHJvcGRv
d24tLW9uLW1lbnUgYnV0dG9uLmRyb3Bkb3duX19saW5rOmhvdmVye2JhY2tncm91bmQtY29sb3I6
IzAwNmZiMDtjb2xvcjojZmZmfS5kcm9wZG93bi0tb24tbWVudSAuZHJvcGRvd25fX2xpbms6Zm9j
dXMsLmRyb3Bkb3duLS1vbi1tZW51IGJ1dHRvbi5kcm9wZG93bl9fbGluazpmb2N1c3tvdXRsaW5l
OjFweCBzb2xpZCAjZmZmO2JvcmRlci1ib3R0b20tY29sb3I6I2ZmZn0uZHJvcGRvd24tLXdpdGgt
aWNvbnMgLmRyb3Bkb3duX19saW5rLC5kcm9wZG93bi0td2l0aC1pY29ucyBidXR0b24uZHJvcGRv
d25fX2xpbmt7cGFkZGluZzoxNXB4IDE1cHggMTVweCA0MHB4fS5kcm9wZG93bi0td2lkZSAuZHJv
cGRvd25fX2xpbmssLmRyb3Bkb3duLS13aWRlIGJ1dHRvbi5kcm9wZG93bl9fbGlua3ttaW4td2lk
dGg6MjAwcHh9LmZhcS1ncm91cCBoMntwYWRkaW5nLWJvdHRvbTo1cHg7bWFyZ2luLXRvcDo2MHB4
fS5mYXEtZ3JvdXAgaDIuZmFxLWdyb3VwX19maXJzdHttYXJnaW4tdG9wOjB9LmZhcS1ncm91cCBo
M3twYWRkaW5nLXRvcDozMHB4fS5mYXEtZ3JvdXAgaDM6YmVmb3Jle2ZvbnQtZmFtaWx5OkZvbnQg
QXdlc29tZVwgNSBGcmVlO2ZvbnQtd2VpZ2h0OjkwMDtjb250ZW50OiLvgZkiO21hcmdpbi1yaWdo
dDo1cHg7Y29sb3I6IzAwNmRhZH0uZmFxLWdyb3VwLS1saXN0IGgye21hcmdpbi10b3A6MzBweDtt
YXJnaW4tYm90dG9tOjE1cHh9LmZpbHRlci1iYWRnZXt0ZXh0LXRyYW5zZm9ybTp1cHBlcmNhc2U7
Zm9udC13ZWlnaHQ6NTAwO2ZvbnQtc2l6ZTouOHJlbTtib3JkZXItcmFkaXVzOjJweDtiYWNrZ3Jv
dW5kLWNvbG9yOiMwMDZkYWQ7Y29sb3I6I2ZmZjtkaXNwbGF5OnRhYmxlO2Zsb2F0OmxlZnQ7bWFy
Z2luOjAgNXB4IDEwcHggMH0uZmlsdGVyLWJhZGdlX19pY29ue2Rpc3BsYXk6dGFibGUtY2VsbDtw
YWRkaW5nOjZweCAwIDZweCA2cHg7Y29sb3I6I2ZmZjt2ZXJ0aWNhbC1hbGlnbjptaWRkbGV9LmZp
bHRlci1iYWRnZV9fZGVzY3JpcHRpb257ZGlzcGxheTp0YWJsZS1jZWxsO3BhZGRpbmc6NnB4O3Zl
cnRpY2FsLWFsaWduOm1pZGRsZX0uZmlsdGVyLWJhZGdlX19yZW1vdmUtYnV0dG9ue2Rpc3BsYXk6
dGFibGUtY2VsbDtjb2xvcjojZmZmO2JhY2tncm91bmQ6dHJhbnNwYXJlbnQ7Ym9yZGVyOjA7Ym9y
ZGVyLWxlZnQ6MXB4IHNvbGlkIGhzbGEoMCwwJSwxMDAlLC4yKTtwYWRkaW5nOjZweH0uZmlsdGVy
LWJhZGdlX19yZW1vdmUtYnV0dG9uOmhvdmVye2NvbG9yOiNmZmY7YmFja2dyb3VuZC1jb2xvcjoj
MDA1ZDk0fS5maWx0ZXItYmFkZ2VfX3JlbW92ZS1idXR0b246YWN0aXZlLC5maWx0ZXItYmFkZ2Vf
X3JlbW92ZS1idXR0b246Zm9jdXN7b3V0bGluZToxcHggc29saWQgI2ZmZn0uZmlsdGVyLXBhbmVs
X19jbG9zZXtkaXNwbGF5Om5vbmV9QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjEw
MDBweCl7LmZpbHRlci1wYW5lbHtkaXNwbGF5Om5vbmU7bWFyZ2luOjA7cGFkZGluZzoyNXB4O292
ZXJmbG93OmF1dG87cG9zaXRpb246Zml4ZWQ7aGVpZ2h0OjEwMCU7dG9wOjA7bGVmdDowO2JhY2tn
cm91bmQtY29sb3I6IzAwNmRhZDt3aWR0aDozMDBweDttYXgtd2lkdGg6MTAwJTt6LWluZGV4OjEx
fS5maWx0ZXItcGFuZWxfX2Nsb3Nle2Rpc3BsYXk6aW5saW5lLWJsb2NrO2JhY2tncm91bmQ6dHJh
bnNwYXJlbnQ7Ym9yZGVyOjA7cG9zaXRpb246YWJzb2x1dGU7dG9wOjE2cHg7cmlnaHQ6MTVweDtm
b250LXNpemU6MThweDtwYWRkaW5nOjA7d2lkdGg6MjJweDtoZWlnaHQ6MjJweDtjdXJzb3I6cG9p
bnRlcjt0ZXh0LWFsaWduOmNlbnRlcjtiYWNrZ3JvdW5kLWltYWdlOm5vbmU7Y29sb3I6I2ZmZn0u
ZmlsdGVyLXBhbmVsX19jbG9zZTphY3RpdmUsLmZpbHRlci1wYW5lbF9fY2xvc2U6aG92ZXJ7YmFj
a2dyb3VuZC1pbWFnZTpub25lfS5maWx0ZXItcGFuZWxfX2Nsb3NlOmFjdGl2ZSwuZmlsdGVyLXBh
bmVsX19jbG9zZTpmb2N1c3tvdXRsaW5lOjFweCBzb2xpZCAjZmZmfS5maWx0ZXItcGFuZWwgYSwu
ZmlsdGVyLXBhbmVsIGgyLC5maWx0ZXItcGFuZWwgbGFiZWx7Y29sb3I6I2ZmZn0uZmlsdGVyLXBh
bmVsIGF7Y29sb3I6I2ZmZjtjb2xvcjpoc2xhKDAsMCUsMTAwJSwuOTUpO2JhY2tncm91bmQtaW1h
Z2U6bGluZWFyLWdyYWRpZW50KDkwZGVnLCNmZmYsaHNsYSgwLDAlLDEwMCUsLjcpKX0uZmlsdGVy
LXBhbmVsIGE6YWN0aXZlLC5maWx0ZXItcGFuZWwgYTpmb2N1c3tvdXRsaW5lOjFweCBzb2xpZCAj
ZmZmfX0uZm9vdGVye2JhY2tncm91bmQtY29sb3I6IzAwNzNiNztjb2xvcjojZmZmO3BhZGRpbmc6
NjBweCAwO3dpZHRoOjEwMCV9QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjQwMHB4
KXsuZm9vdGVye3BhZGRpbmctdG9wOjQwcHggMH19LmZvb3Rlcl9fbG9nb3ttYXJnaW4tYm90dG9t
OjMwcHg7dGV4dC1hbGlnbjpjZW50ZXJ9LmZvb3Rlcl9fbWVudXN7ZGlzcGxheTotd2Via2l0LWJv
eDtkaXNwbGF5Oi1tb3otYm94O2Rpc3BsYXk6Ym94O2Rpc3BsYXk6LXdlYmtpdC1mbGV4O2Rpc3Bs
YXk6LW1vei1mbGV4O2Rpc3BsYXk6LW1zLWZsZXhib3g7ZGlzcGxheTpmbGV4Oy13ZWJraXQtYm94
LXBhY2s6Y2VudGVyOy1tb3otYm94LXBhY2s6Y2VudGVyO2JveC1wYWNrOmNlbnRlcjstd2Via2l0
LWp1c3RpZnktY29udGVudDpjZW50ZXI7LW1vei1qdXN0aWZ5LWNvbnRlbnQ6Y2VudGVyOy1tcy1q
dXN0aWZ5LWNvbnRlbnQ6Y2VudGVyOy1vLWp1c3RpZnktY29udGVudDpjZW50ZXI7anVzdGlmeS1j
b250ZW50OmNlbnRlcjstbXMtZmxleC1wYWNrOmNlbnRlcjstd2Via2l0LWJveC1saW5lczptdWx0
aXBsZTstbW96LWJveC1saW5lczptdWx0aXBsZTtib3gtbGluZXM6bXVsdGlwbGU7LXdlYmtpdC1m
bGV4LXdyYXA6d3JhcDstbW96LWZsZXgtd3JhcDp3cmFwOy1tcy1mbGV4LXdyYXA6d3JhcDtmbGV4
LXdyYXA6d3JhcDttYXJnaW4tYm90dG9tOjMwcHh9QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4
LXdpZHRoOjQwMHB4KXsuZm9vdGVyX19tZW51c3ttYXJnaW4tYm90dG9tOjEwcHh9fS5mb290ZXJf
X21lbnV7LXdlYmtpdC1mbGV4LWJhc2lzOjIyMHB4Oy1tb3otZmxleC1iYXNpczoyMjBweDtmbGV4
LWJhc2lzOjIyMHB4Oy1tcy1mbGV4LXByZWZlcnJlZC1zaXplOjIyMHB4Oy13ZWJraXQtZmxleC1z
aHJpbms6MDstbW96LWZsZXgtc2hyaW5rOjA7ZmxleC1zaHJpbms6MDstbXMtZmxleC1uZWdhdGl2
ZTowO21hcmdpbjowIDE1cHggNDBweDtwYWRkaW5nOjB9LmZvb3Rlcl9fbWVudSBoMntjb2xvcjoj
ZmZmO21hcmdpbi1ib3R0b206NXB4O3RleHQtYWxpZ246Y2VudGVyfS5mb290ZXJfX21lbnUgdWx7
bWFyZ2luOjA7cGFkZGluZzowfS5mb290ZXJfX21lbnUgbGl7cGFkZGluZzoycHggMDtsaXN0LXN0
eWxlOm5vbmU7dGV4dC1hbGlnbjpjZW50ZXJ9LmZvb3Rlcl9fbWVudSBsaSBhe2JhY2tncm91bmQt
aW1hZ2U6bm9uZTtjb2xvcjpoc2xhKDAsMCUsMTAwJSwuOTUpO2JhY2tncm91bmQtaW1hZ2U6bGlu
ZWFyLWdyYWRpZW50KDkwZGVnLCNmZmYsaHNsYSgwLDAlLDEwMCUsLjcpKX0uZm9vdGVyX19tZW51
IGxpIGE6YWN0aXZlLC5mb290ZXJfX21lbnUgbGkgYTpmb2N1c3tvdXRsaW5lOjFweCBzb2xpZCAj
ZmZmfS5mb290ZXJfX2RpdmlkZXJ7Ym9yZGVyOjFweCBzb2xpZCBoc2xhKDAsMCUsMTAwJSwuMyk7
bWFyZ2luOjAgYXV0byAzMHB4O3dpZHRoOjIwMHB4O2JhY2tncm91bmQ6bm9uZTtoZWlnaHQ6MH0u
Zm9vdGVyX190ZXh0e2NvbG9yOmhzbGEoMCwwJSwxMDAlLC45NSk7Zm9udC1zaXplOi45cmVtO21h
cmdpbjphdXRvO21heC13aWR0aDo2MDBweDt0ZXh0LWFsaWduOmNlbnRlcjtwYWRkaW5nOjAgMjBw
eH0uZm9vdGVyX190ZXh0IGF7Y29sb3I6aHNsYSgwLDAlLDEwMCUsLjk1KTtiYWNrZ3JvdW5kLWlt
YWdlOmxpbmVhci1ncmFkaWVudCg5MGRlZywjZmZmLGhzbGEoMCwwJSwxMDAlLC43KSl9LmZvb3Rl
cl9fdGV4dCBhOmFjdGl2ZSwuZm9vdGVyX190ZXh0IGE6Zm9jdXN7b3V0bGluZToxcHggc29saWQg
I2ZmZn0uZm9ybS1lcnJvcnN7bWFyZ2luOjVweCAwIDA7cGFkZGluZy1ib3R0b206NXB4O2xpc3Qt
c3R5bGUtdHlwZTpub25lO2NvbG9yOiNkNTJkNDB9LmZvcm0tZXJyb3JzIGxpe21heC13aWR0aDoz
NTBweH0uZm9ybS1lcnJvcnMgbGk6YmVmb3Jle2ZvbnQtZmFtaWx5OkZvbnQgQXdlc29tZVwgNSBG
cmVlO2ZvbnQtd2VpZ2h0OjkwMDtjb250ZW50OiLvgaoiO21hcmdpbi1yaWdodDo1cHg7Y29sb3I6
I2Q1MmQ0MH0uZm9ybS1lcnJvcnMgbGkgYXtjb2xvcjojZDUyZDQwO2JhY2tncm91bmQtaW1hZ2U6
bGluZWFyLWdyYWRpZW50KDkwZGVnLCNkNTJkNDAscmdiYSgyMTMsNDUsNjQsLjcpKX0uZm9ybS1l
cnJvcnMgbGkgYTpob3Zlcntjb2xvcjojYWQyMzMyO2JhY2tncm91bmQtaW1hZ2U6bGluZWFyLWdy
YWRpZW50KDkwZGVnLCNhZDIzMzIsI2FkMjMzMil9LmZvcm0tZXJyb3JzIGxpIGE6YWN0aXZlLC5m
b3JtLWVycm9ycyBsaSBhOmZvY3Vze291dGxpbmU6MXB4IHNvbGlkICNkNTJkNDB9LmZvcm0tZXJy
b3JzLS1mdWxsLXdpZHRoIGxpe21heC13aWR0aDoxMDAlfS5mb3JtLWVycm9ycyAuZm9ybS1lcnJv
ci0tdmFsaWR7Y29sb3I6IzE0ODAyNH0uZm9ybS1lcnJvcnMgLmZvcm0tZXJyb3ItLXZhbGlkOmJl
Zm9yZXtmb250LWZhbWlseTpGb250IEF3ZXNvbWVcIDUgRnJlZTtmb250LXdlaWdodDo5MDA7Y29u
dGVudDoi74CMIjttYXJnaW4tcmlnaHQ6NXB4O2NvbG9yOiMxNDgwMjR9LmZvcm0tZ3JvdXB7bWFy
Z2luLWJvdHRvbToxNXB4O21heC13aWR0aDozNTBweH0uZm9ybS1ncm91cF9fbGFiZWx7ZGlzcGxh
eTpibG9jaztmb250LXdlaWdodDo3MDB9LmZvcm0tZ3JvdXBfX2xhYmVsOm5vdCg6Zmlyc3QtY2hp
bGQpe21hcmdpbi10b3A6N3B4fS5mb3JtLWdyb3VwX19yZXF1aXJlZHtmb250LXNpemU6LjhyZW07
Zm9udC13ZWlnaHQ6NDAwfS5mb3JtLWdyb3VwIGlucHV0Om5vdChbdHlwZV0pLC5mb3JtLWdyb3Vw
IGlucHV0W3R5cGU9Y29sb3JdLC5mb3JtLWdyb3VwIGlucHV0W3R5cGU9ZGF0ZV0sLmZvcm0tZ3Jv
dXAgaW5wdXRbdHlwZT1kYXRldGltZS1sb2NhbF0sLmZvcm0tZ3JvdXAgaW5wdXRbdHlwZT1kYXRl
dGltZV0sLmZvcm0tZ3JvdXAgaW5wdXRbdHlwZT1lbWFpbF0sLmZvcm0tZ3JvdXAgaW5wdXRbdHlw
ZT1tb250aF0sLmZvcm0tZ3JvdXAgaW5wdXRbdHlwZT1udW1iZXJdLC5mb3JtLWdyb3VwIGlucHV0
W3R5cGU9cGFzc3dvcmRdLC5mb3JtLWdyb3VwIGlucHV0W3R5cGU9c2VhcmNoXSwuZm9ybS1ncm91
cCBpbnB1dFt0eXBlPXRlbF0sLmZvcm0tZ3JvdXAgaW5wdXRbdHlwZT10ZXh0XSwuZm9ybS1ncm91
cCBpbnB1dFt0eXBlPXRpbWVdLC5mb3JtLWdyb3VwIGlucHV0W3R5cGU9dXJsXSwuZm9ybS1ncm91
cCBpbnB1dFt0eXBlPXdlZWtdLC5mb3JtLWdyb3VwIHNlbGVjdC5mb3JtLWdyb3VwX19maWVsZCwu
Zm9ybS1ncm91cCB0ZXh0YXJlYS5mb3JtLWdyb3VwX19maWVsZHtkaXNwbGF5OmJsb2NrO3dpZHRo
OjM1MHB4O21hcmdpbi10b3A6NHB4O21heC13aWR0aDoxMDAlfS5mb3JtLWdyb3VwX190ZXh0e2Zv
bnQtc2l6ZToxLjFyZW07cGFkZGluZzo0cHggMCA4cHh9LmZvcm0tZ3JvdXBfX2hlbHAtdGV4dHtw
YWRkaW5nOjA7bWFyZ2luLXRvcDo1cHg7d2lkdGg6MzUwcHg7bWF4LXdpZHRoOjEwMCU7Zm9udC1z
aXplOi44cmVtfS5ncmF2YXRhci1mb3Jte2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXJ9
LmdyYXZhdGFyLWZvcm1fX2ltYWdle21hcmdpbi1yaWdodDoxNXB4fS5ncmF2YXRhci1mb3JtX19j
b250ZW50e21heC13aWR0aDo1MDBweH1AbWVkaWEgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjYwMHB4
KXsuZ3JhdmF0YXItZm9ybXthbGlnbi1pdGVtczpzdGFydH0uZ3JhdmF0YXItZm9ybV9faW1hZ2V7
bWF4LXdpZHRoOjkwcHh9fUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6NDAwcHgpey5ncmF2
YXRhci1mb3Jte2Rpc3BsYXk6YmxvY2t9LmdyYXZhdGFyLWZvcm1fX2ltYWdle21hcmdpbi1yaWdo
dDowfS5ncmF2YXRhci1mb3JtX19jb250ZW50e21heC13aWR0aDoxMDAlO21hcmdpbi10b3A6MTVw
eH19LmhlYWRpbmctd3N1YnRpdGxlX19oZWFkaW5ne3BhZGRpbmctYm90dG9tOjVweH0uaGVhZGlu
Zy13c3VidGl0bGVfX3N1YnRpdGxle21hcmdpbi1ib3R0b206MTVweH0uaGVhZGluZy13c3VidGl0
bGUtLWluLWNvbnRlbnQgLmhlYWRpbmctd3N1YnRpdGxlX19oZWFkaW5ne3BhZGRpbmctdG9wOjMw
cHh9LmhvbWVwYWdlLWJhbm5lcnt0ZXh0LWFsaWduOmNlbnRlcn0uaG9tZXBhZ2UtYmFubmVyX190
aXRsZXttYXgtd2lkdGg6ODEwcHg7bWFyZ2luOjAgYXV0bztwYWRkaW5nOjAgMjBweCA0MHB4fUBt
ZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo0MDBweCl7LmhvbWVwYWdlLWJhbm5lcl9f
dGl0bGV7cGFkZGluZzowIDEwcHggMzBweH19LmhvbWVwYWdlLWJhbm5lcl9fYnJvd3Nle2ZvbnQt
c2l6ZToxLjJyZW07bWFyZ2luOjMwcHggMCAxMHB4fS5ob21lcGFnZS1iYW5uZXJfX2Jyb3dzZSBh
e2NvbG9yOmhzbGEoMCwwJSwxMDAlLC45NSk7YmFja2dyb3VuZC1pbWFnZTpsaW5lYXItZ3JhZGll
bnQoOTBkZWcsI2ZmZixoc2xhKDAsMCUsMTAwJSwuNykpfS5ob21lcGFnZS1iYW5uZXJfX2Jyb3dz
ZSBhOmFjdGl2ZSwuaG9tZXBhZ2UtYmFubmVyX19icm93c2UgYTpmb2N1c3tvdXRsaW5lOjFweCBz
b2xpZCAjZmZmfS5ob29yYXktbGlzdHttYXJnaW4tbGVmdDowO2JvcmRlci10b3A6MXB4IGRvdHRl
ZCAjZDNkM2QzfS5ob29yYXktbGlzdCBsaXtib3JkZXItYm90dG9tOjFweCBkb3R0ZWQgI2QzZDNk
MztwYWRkaW5nOjEwcHggMCAxMHB4IDMwcHg7bGlzdC1zdHlsZS10eXBlOm5vbmU7cG9zaXRpb246
cmVsYXRpdmV9Lmhvb3JheS1saXN0IGxpOmJlZm9yZXtmb250LWZhbWlseTpGb250IEF3ZXNvbWVc
IDUgRnJlZTtmb250LXdlaWdodDo5MDA7Y29udGVudDoi74CMIjtjb2xvcjojNDY0NjQ2O3Bvc2l0
aW9uOmFic29sdXRlO2xlZnQ6N3B4fS5ob3Jpem9udGFsLW1lbnUgbGksLmhvcml6b250YWwtbWVu
dSB1bHtsaXN0LXN0eWxlLXR5cGU6bm9uZTttYXJnaW46MDtwYWRkaW5nOjB9Lmhvcml6b250YWwt
bWVudV9faXRlbXtkaXNwbGF5OmlubGluZX0uaG9yaXpvbnRhbC1tZW51X19saW5re3RleHQtZGVj
b3JhdGlvbjpub25lO2Rpc3BsYXk6aW5saW5lLWJsb2NrO3BhZGRpbmc6OHB4IDEwcHg7YmFja2dy
b3VuZC1pbWFnZTpub25lfS5ob3Jpem9udGFsLW1lbnVfX2xpbms6aG92ZXJ7YmFja2dyb3VuZC1p
bWFnZTpub25lfS5ob3Jpem9udGFsLW1lbnVfX2xpbms6YWN0aXZlLC5ob3Jpem9udGFsLW1lbnVf
X2xpbms6Zm9jdXN7b3V0bGluZToxcHggc29saWQgI2ZmZn0uaG9yaXpvbnRhbC1tZW51X19saW5r
LS13aXRoLWljb24gLmZhe21hcmdpbi1yaWdodDozcHh9Lmhvcml6b250YWwtbWVudV9fbGluay0t
d2l0aC1pY29uIC51c2VyLWltYWdle21hcmdpbi1yaWdodDo1cHg7Ym9yZGVyLXJhZGl1czoxMCV9
Lmhvcml6b250YWwtbWVudV9fbGluay0td2l0aC1pY29uOmhvdmVyIC5mYSwuaG9yaXpvbnRhbC1t
ZW51X19saW5rLS13aXRoLWljb246aG92ZXIgLnVzZXItaW1hZ2V7b3BhY2l0eTouOH0uaG9yaXpv
bnRhbC1tZW51LS1saWdodCAuaG9yaXpvbnRhbC1tZW51X19saW5re2NvbG9yOiNmZmZ9Lmhvcml6
b250YWwtbWVudS0tbGlnaHQgLmhvcml6b250YWwtbWVudV9fbGluazpob3Zlcnt0ZXh0LWRlY29y
YXRpb24tY29sb3I6aHNsYSgwLDAlLDEwMCUsLjQpfS5ob3Jpem9udGFsLW1lbnUtLXRhbGwgLmhv
cml6b250YWwtbWVudV9fbGlua3twYWRkaW5nOjMycHggMTVweH0uaG9yaXpvbnRhbC1tZW51LS10
YWxsIC5ob3Jpem9udGFsLW1lbnVfX2xpbms6aG92ZXJ7dGV4dC1kZWNvcmF0aW9uOnVuZGVybGlu
ZX1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6NjAwcHgpey5ob3Jpem9udGFsLW1l
bnUtLXRhbGwgLmhvcml6b250YWwtbWVudV9fbGlua3twYWRkaW5nOjI1cHggMTBweH19Lmhvcml6
b250YWwtc2VjdGlvbntwYWRkaW5nOjcwcHggMH1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgt
d2lkdGg6ODAwcHgpey5ob3Jpem9udGFsLXNlY3Rpb257cGFkZGluZzo1MHB4IDB9fUBtZWRpYSBv
bmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo0MDBweCl7Lmhvcml6b250YWwtc2VjdGlvbntwYWRk
aW5nOjQwcHggMH19Lmhvcml6b250YWwtc2VjdGlvbi0tZ3JleXtiYWNrZ3JvdW5kLWNvbG9yOiNl
Y2VjZWM7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgI2QzZDNkMztib3JkZXItdG9wOjFweCBzb2xp
ZCAjZDNkM2QzfS5ob3Jpem9udGFsLXNlY3Rpb24tLW1lZGl1bXtwYWRkaW5nOjQwcHggMH0uaG9y
aXpvbnRhbC1zZWN0aW9uLS10aGlue3BhZGRpbmc6MTBweCAwfUBtZWRpYSBvbmx5IHNjcmVlbiBh
bmQgKG1heC13aWR0aDo0MDBweCl7Lmhvcml6b250YWwtc2VjdGlvbi0tc3RhdGlzdGljc3tkaXNw
bGF5Om5vbmV9fS5sYW5ndWFnZS1zd2l0Y2hlcntiYWNrZ3JvdW5kLWNvbG9yOiMwMDcwYjI7Ym9y
ZGVyLXRvcDoxcHggc29saWQgIzAwNjdhMztjb2xvcjojZmZmO3BhZGRpbmc6MTVweCAwO3dpZHRo
OjEwMCU7dGV4dC1hbGlnbjpjZW50ZXI7Zm9udC1zaXplOi44cmVtfS5sYW5ndWFnZS1zd2l0Y2hl
ciB1bHtsaXN0LXN0eWxlLXR5cGU6bm9uZX0ubGFuZ3VhZ2Utc3dpdGNoZXIgdWwgbGl7ZGlzcGxh
eTppbmxpbmUtYmxvY2s7bWFyZ2luOjAgNy41cHh9Lmxhbmd1YWdlLXN3aXRjaGVyIHVsIGJ1dHRv
bntjb2xvcjojZmZmO2JvcmRlcjowO2JhY2tncm91bmQtY29sb3I6dHJhbnNwYXJlbnQ7cGFkZGlu
ZzowO2JhY2tncm91bmQtcG9zaXRpb246MCAxLjNlbTtiYWNrZ3JvdW5kLXJlcGVhdDpyZXBlYXQt
eDtiYWNrZ3JvdW5kLXNpemU6MTAwJSAxLjVweDtjb2xvcjpoc2xhKDAsMCUsMTAwJSwuOTUpO2Jh
Y2tncm91bmQtaW1hZ2U6bGluZWFyLWdyYWRpZW50KDkwZGVnLCNmZmYsaHNsYSgwLDAlLDEwMCUs
LjcpKX0ubGFuZ3VhZ2Utc3dpdGNoZXIgdWwgYnV0dG9uOmFjdGl2ZSwubGFuZ3VhZ2Utc3dpdGNo
ZXIgdWwgYnV0dG9uOmZvY3Vze291dGxpbmU6MXB4IHNvbGlkICNmZmZ9Lmxhbmd1YWdlLXN3aXRj
aGVyIHVsIGJ1dHRvbi5sYW5ndWFnZS1zd2l0Y2hlcl9fc2VsZWN0ZWR7cG9pbnRlci1ldmVudHM6
bm9uZTtiYWNrZ3JvdW5kLWltYWdlOm5vbmV9Lmxhbmd1YWdlLXN3aXRjaGVyIHVsIGJ1dHRvbi5s
YW5ndWFnZS1zd2l0Y2hlcl9fc2VsZWN0ZWQ6aG92ZXJ7YmFja2dyb3VuZC1pbWFnZTpub25lfS5s
YW5ndWFnZS1zd2l0Y2hlciB1bCBidXR0b24ubGFuZ3VhZ2Utc3dpdGNoZXJfX3NlbGVjdGVkOmJl
Zm9yZXtmb250LWZhbWlseTpGb250IEF3ZXNvbWVcIDUgRnJlZTtmb250LXdlaWdodDo5MDA7Y29u
dGVudDoi74SFIjttYXJnaW4tcmlnaHQ6NHB4O2NvbG9yOiNmZmY7cG9zaXRpb246cmVsYXRpdmU7
dG9wOi41cHh9aW5wdXQubGFyZ2UtaW5wdXR7Zm9udC1zaXplOjEuMzJyZW07aGVpZ2h0OjUwcHg7
bGluZS1oZWlnaHQ6NTBweH0ubGVkZS1wYXJhZ3JhcGh7Zm9udC13ZWlnaHQ6NjAwO2ZvbnQtc2l6
ZToxLjJyZW07Y29sb3I6IzYwNjA2MH0ubW9iaWxlLXNlYXJjaHtkaXNwbGF5Om5vbmU7cGFkZGlu
ZzoxMHB4O2JhY2tncm91bmQtY29sb3I6IzAwNWQ5NH1AbWVkaWEgc2NyZWVuIGFuZCAobWF4LXdp
ZHRoOjgwMHB4KXsubW9iaWxlLXNlYXJjaHtkaXNwbGF5OmJsb2NrfX0ubW9kYWx7cG9zaXRpb246
Zml4ZWQ7dG9wOjA7cmlnaHQ6MDtib3R0b206MDtsZWZ0OjA7YmFja2dyb3VuZC1jb2xvcjpyZ2Jh
KDAsMCwwLC41KTt6LWluZGV4OjEwO3BvaW50ZXItZXZlbnRzOm5vbmU7dHJhbnNpdGlvbjpvcGFj
aXR5IC4zcztvcGFjaXR5OjA7dmlzaWJpbGl0eTpoaWRkZW47ZGlzcGxheTpmbGV4O2ZsZXgtZGly
ZWN0aW9uOmNvbHVtbjthbGlnbi1pdGVtczpjZW50ZXI7ZmxleC1ncm93OjE7dGV4dC1hbGlnbjps
ZWZ0fS5tb2RhbDp0YXJnZXR7b3BhY2l0eToxO3Zpc2liaWxpdHk6dmlzaWJsZTtwb2ludGVyLWV2
ZW50czphdXRvfS5tb2RhbF9fY29udGVudHt3aWR0aDo0MDBweDttYXgtd2lkdGg6OTAlO21heC1o
ZWlnaHQ6OTAlO2JvcmRlci1yYWRpdXM6M3B4O292ZXJmbG93OmF1dG87YmFja2dyb3VuZDojZmZm
O3Bvc2l0aW9uOnJlbGF0aXZlO21hcmdpbjphdXRvfS5tb2RhbF9fYm9keXtwYWRkaW5nOjMwcHh9
QG1lZGlhIHNjcmVlbiBhbmQgKG1heC13aWR0aDo4MDBweCl7Lm1vZGFsX19ib2R5e3BhZGRpbmc6
MTVweH19Lm1vZGFsX190aXRsZXtmb250LXNpemU6MS41cmVtO3BhZGRpbmctcmlnaHQ6MjBweH0u
bW9kYWxfX2Zvb3Rlcntib3JkZXItdG9wOjFweCBzb2xpZCAjZDNkM2QzO3BhZGRpbmc6MTVweDtk
aXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2p1c3RpZnktY29udGVudDpmbGV4LWVuZH0u
bW9kYWxfX2FjdGlvbnttYXJnaW4tbGVmdDo1cHh9Lm1vZGFsX19jbG9zZXtiYWNrZ3JvdW5kOnRy
YW5zcGFyZW50O2JvcmRlcjowO3Bvc2l0aW9uOmFic29sdXRlO3RvcDoxNnB4O3JpZ2h0OjE1cHg7
Zm9udC1zaXplOjE4cHg7cGFkZGluZzowO3dpZHRoOjIycHg7aGVpZ2h0OjIycHg7Y3Vyc29yOnBv
aW50ZXI7dGV4dC1hbGlnbjpjZW50ZXI7YmFja2dyb3VuZC1pbWFnZTpub25lO2NvbG9yOiM0NjQ2
NDZ9Lm1vZGFsX19jbG9zZTphY3RpdmUsLm1vZGFsX19jbG9zZTpob3ZlcntiYWNrZ3JvdW5kLWlt
YWdlOm5vbmV9Lm1vZGFsX19jbG9zZTpob3Zlcntjb2xvcjojNDY0NjQ2fS5tb2RhbF9fZm9ybSBs
YWJlbHtmb250LXdlaWdodDo3MDB9Lm1vZGFsX19mb3JtIGxhYmVsIGlucHV0e3dpZHRoOmF1dG87
bWluLXdpZHRoOmF1dG99Lm1vZGFsX19mb3JtIGlucHV0e3dpZHRoOjEwMCU7bWluLXdpZHRoOjEw
MCU7bWFyZ2luOjVweCAwIDIwcHh9Lm1vZGFsX19mb3JtIGlucHV0Omxhc3QtY2hpbGR7bWFyZ2lu
LWJvdHRvbTowfS5tb2RhbF9fZm9ybSAuc2hvdy1wYXNzd29yZCwubW9kYWxfX2Zvcm0gLnNob3ct
cGFzc3dvcmQgaW5wdXR7Zm9udC13ZWlnaHQ6NDAwO3dpZHRoOmF1dG87bWFyZ2luOjB9Lm1vZGFs
LS13aWRlIC5tb2RhbF9fY29udGVudHt3aWR0aDo4NTBweH0ubm90aWZpY2F0aW9uLWJhcntib3Jk
ZXItYm90dG9tOjJweCBzb2xpZCAjZmZmO3RleHQtYWxpZ246Y2VudGVyO2JhY2tncm91bmQtY29s
b3I6IzAwNGQ3YTtjb2xvcjojZmZmO3BhZGRpbmc6MTVweDtwb3NpdGlvbjpyZWxhdGl2ZX0ubm90
aWZpY2F0aW9uLWJhcl9faWNvbntmb250LXNpemU6LjhyZW07bWFyZ2luLXJpZ2h0OjNweH0ubm90
aWZpY2F0aW9uLWJhcl9fbWVzc2FnZXtmb250LXNpemU6MS4xNXJlbTtmb250LXdlaWdodDo2MDB9
Lm5vdGlmaWNhdGlvbi1iYXJfX21lc3NhZ2UgYTpub3QoLmJ1dHRvbil7Y29sb3I6aHNsYSgwLDAl
LDEwMCUsLjk1KTtiYWNrZ3JvdW5kLWltYWdlOmxpbmVhci1ncmFkaWVudCg5MGRlZywjZmZmLGhz
bGEoMCwwJSwxMDAlLC43KSl9Lm5vdGlmaWNhdGlvbi1iYXJfX21lc3NhZ2UgYTpub3QoLmJ1dHRv
bik6YWN0aXZlLC5ub3RpZmljYXRpb24tYmFyX19tZXNzYWdlIGE6bm90KC5idXR0b24pOmZvY3Vz
e291dGxpbmU6MXB4IHNvbGlkICNmZmZ9Lm5vdGlmaWNhdGlvbi1iYXJfX2Rpc21pc3N7YmFja2dy
b3VuZDp0cmFuc3BhcmVudDtib3JkZXI6MDtwb3NpdGlvbjphYnNvbHV0ZTt0b3A6MTZweDtyaWdo
dDoxNXB4O2ZvbnQtc2l6ZToxOHB4O3BhZGRpbmc6MDt3aWR0aDoyMnB4O2hlaWdodDoyMnB4O2N1
cnNvcjpwb2ludGVyO3RleHQtYWxpZ246Y2VudGVyO2JhY2tncm91bmQtaW1hZ2U6bm9uZX0ubm90
aWZpY2F0aW9uLWJhcl9fZGlzbWlzczphY3RpdmUsLm5vdGlmaWNhdGlvbi1iYXJfX2Rpc21pc3M6
aG92ZXJ7YmFja2dyb3VuZC1pbWFnZTpub25lfS5ub3RpZmljYXRpb24tYmFyX19kaXNtaXNzOmFj
dGl2ZSwubm90aWZpY2F0aW9uLWJhcl9fZGlzbWlzczpmb2N1c3tvdXRsaW5lOjFweCBzb2xpZCAj
ZmZmfS5ub3RpZmljYXRpb24tYmFyLS1kaXNtaXNzYWJsZXtkaXNwbGF5Om5vbmU7cGFkZGluZzox
NXB4IDU1cHh9Lm5vdGlmaWNhdGlvbi1iYXItLXZpc2libGV7ZGlzcGxheTpibG9ja30ubm90aWZp
Y2F0aW9uLWJhci0td2FybmluZ3tiYWNrZ3JvdW5kLWNvbG9yOiNmZmRmNzY7Y29sb3I6IzY2NGUw
NH0ubm90aWZpY2F0aW9uLWJhci0td2FybmluZyBhOm5vdCguYnV0dG9uKXtjb2xvcjojNjY0ZTA0
O2JhY2tncm91bmQtaW1hZ2U6bGluZWFyLWdyYWRpZW50KDkwZGVnLCM2NjRlMDQscmdiYSgxMDIs
NzgsNCwuNykpfS5ub3RpZmljYXRpb24tYmFyLS13YXJuaW5nIGE6bm90KC5idXR0b24pOmhvdmVy
e2NvbG9yOiMzNTI4MDI7YmFja2dyb3VuZC1pbWFnZTpsaW5lYXItZ3JhZGllbnQoOTBkZWcsIzM1
MjgwMiwjMzUyODAyKX0ubm90aWZpY2F0aW9uLWJhci0td2FybmluZyBhOm5vdCguYnV0dG9uKTph
Y3RpdmUsLm5vdGlmaWNhdGlvbi1iYXItLXdhcm5pbmcgYTpub3QoLmJ1dHRvbik6Zm9jdXN7b3V0
bGluZToxcHggc29saWQgIzY2NGUwNH0ubm90aWZpY2F0aW9uLWJhci0td2FybmluZyAubm90aWZp
Y2F0aW9uLWJhcl9fZGlzbWlzczphY3RpdmUsLm5vdGlmaWNhdGlvbi1iYXItLXdhcm5pbmcgLm5v
dGlmaWNhdGlvbi1iYXJfX2Rpc21pc3M6Zm9jdXN7b3V0bGluZToxcHggc29saWQgIzY2NGUwNH0u
bm90aWZpY2F0aW9uLWJhci0tZGFuZ2Vye2JhY2tncm91bmQtY29sb3I6I2Q1MmQ0MH0ubm90aWZp
Y2F0aW9uLWJhci0tc3VjY2Vzc3tiYWNrZ3JvdW5kLWNvbG9yOiMxNDgwMjR9Lm5vdGlmaWNhdGlv
bi1iYXItLWJhbm5lcntiYWNrZ3JvdW5kLWNvbG9yOiNmZmRmNzY7Y29sb3I6IzY2NGUwNDtib3Jk
ZXItY29sb3I6IzAwNGQ3YX0ubm90aWZpY2F0aW9uLWJhci0tYmFubmVyIGF7Y29sb3I6IzY2NGUw
NH0ubm90aWZpY2F0aW9uLWJhci0tYmFubmVyIC5idXR0b257Y29sb3I6I2ZmZn0ucGFja2FnZS1k
ZXNjcmlwdGlvbntkaXJlY3Rpb246bHRyO21pbi1oZWlnaHQ6NThweDttYXJnaW4tdG9wOi0xMHB4
fS5wYWNrYWdlLWRlc2NyaXB0aW9uX19zdW1tYXJ5e2ZvbnQtc2l6ZToxLjFyZW07cGFkZGluZzow
O21hcmdpbi10b3A6MTBweH0ucGFja2FnZS1kZXNjcmlwdGlvbl9fZWRpdC1idXR0b257bWFyZ2lu
LXRvcDoxMHB4fS5wYWNrYWdlLWhlYWRlcnttYXgtd2lkdGg6MTE1MHB4O21hcmdpbi1yaWdodDph
dXRvO21hcmdpbi1sZWZ0OmF1dG87cGFkZGluZzowIDMwcHg7ZGlzcGxheTpmbGV4O2RpcmVjdGlv
bjpsdHI7dGV4dC1hbGlnbjpsZWZ0fS5wYWNrYWdlLWhlYWRlcjphZnRlcntjbGVhcjpib3RoO2Nv
bnRlbnQ6IiI7ZGlzcGxheTp0YWJsZX1AbWVkaWEgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjYwMHB4
KXsucGFja2FnZS1oZWFkZXJ7cGFkZGluZzowIDE1cHh9fS5wYWNrYWdlLWhlYWRlciBidXR0b257
Y29sb3I6I2ZmZn0ucGFja2FnZS1oZWFkZXJfX2xlZnR7d2lkdGg6NzUlO3BhZGRpbmctcmlnaHQ6
MzBweH0ucGFja2FnZS1oZWFkZXJfX3JpZ2h0e3RleHQtYWxpZ246cmlnaHQ7d2lkdGg6MjUlfUBt
ZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAwcHgpey5wYWNrYWdlLWhlYWRlcntkaXNwbGF5
OmJsb2NrfS5wYWNrYWdlLWhlYWRlcl9fbGVmdCwucGFja2FnZS1oZWFkZXJfX3JpZ2h0e3dpZHRo
OjEwMCU7cGFkZGluZy1yaWdodDowO3RleHQtYWxpZ246bGVmdH0ucGFja2FnZS1oZWFkZXJfX3Jp
Z2h0e21hcmdpbi10b3A6MTVweH19LnBhY2thZ2UtaGVhZGVyX19uYW1le3BhZGRpbmc6MDttYXJn
aW4tdG9wOi0xMHB4fS5wYWNrYWdlLWhlYWRlcl9fcGlwLWluc3RydWN0aW9uc3ttYXJnaW46MTBw
eCAwIDA7cGFkZGluZy1ib3R0b206MH0ucGFja2FnZS1oZWFkZXJfX3BpcC1pbnN0cnVjdGlvbnM6
YWZ0ZXJ7Y2xlYXI6Ym90aDtjb250ZW50OiIiO2Rpc3BsYXk6dGFibGV9LnBhY2thZ2UtaGVhZGVy
X19waXAtaW5zdHJ1Y3Rpb25zIHNwYW57Zm9udC1mYW1pbHk6U291cmNlIENvZGUgUHJvLG1vbm9z
cGFjZTtmb250LXdlaWdodDo1MDA7Zm9udC1zaXplOjEuMnJlbTtmbG9hdDpsZWZ0O2JhY2tncm91
bmQtY29sb3I6cmdiYSgwLDAsMCwuMTUpO3BhZGRpbmc6OHB4O2JvcmRlcjoxcHggZG90dGVkIGhz
bGEoMCwwJSwxMDAlLC40KTtsaW5lLWhlaWdodDozMHB4fUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQg
KG1heC13aWR0aDo4MDBweCl7LnBhY2thZ2UtaGVhZGVyX19waXAtaW5zdHJ1Y3Rpb25zIHNwYW57
Zm9udC1zaXplOjEuMXJlbX19QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjQwMHB4
KXsucGFja2FnZS1oZWFkZXJfX3BpcC1pbnN0cnVjdGlvbnMgc3Bhbntmb250LXNpemU6MXJlbX19
LnBhY2thZ2UtaGVhZGVyX19waXAtaW5zdHJ1Y3Rpb25zIGJ1dHRvbntjb2xvcjojZmZmO2xpbmUt
aGVpZ2h0OjMwcHg7ZmxvYXQ6bGVmdDtjdXJzb3I6cG9pbnRlcjtwYWRkaW5nOjhweCAxNXB4O2Jh
Y2tncm91bmQtY29sb3I6cmdiYSgwLDAsMCwuMTUpO2JvcmRlcjoxcHggZG90dGVkIGhzbGEoMCww
JSwxMDAlLC40KTtib3JkZXItbGVmdDoxcHh9LnBhY2thZ2UtaGVhZGVyX19waXAtaW5zdHJ1Y3Rp
b25zIGJ1dHRvbjpob3ZlcntiYWNrZ3JvdW5kLWNvbG9yOnJnYmEoMCwwLDAsLjIpfS5wYWNrYWdl
LWhlYWRlcl9fcGlwLWluc3RydWN0aW9ucyBidXR0b246YWN0aXZlLC5wYWNrYWdlLWhlYWRlcl9f
cGlwLWluc3RydWN0aW9ucyBidXR0b246Zm9jdXN7b3V0bGluZToxcHggc29saWQgI2ZmZn0ucGFj
a2FnZS1oZWFkZXJfX2RhdGV7bWFyZ2luLXRvcDoyMHB4O3BhZGRpbmctYm90dG9tOjVweH1AbWVk
aWEgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjgwMHB4KXsucGFja2FnZS1oZWFkZXJfX2RhdGV7bWFy
Z2luLXRvcDoxNXB4O3BhZGRpbmctYm90dG9tOjB9fS5wYWNrYWdlLXNuaXBwZXR7Ym9yZGVyOjFw
eCBzb2xpZCAjZDNkM2QzO2JveC1zaGFkb3c6MXB4IDFweCAycHggMXB4IHJnYmEoMCwwLDAsLjA1
KTtiYWNrZ3JvdW5kLWNvbG9yOiNmZmY7YmFja2dyb3VuZC1pbWFnZTpub25lO2RpcmVjdGlvbjps
dHI7dGV4dC1hbGlnbjpsZWZ0O2Rpc3BsYXk6YmxvY2s7cGFkZGluZzoxNXB4IDIwcHggMTVweCA3
NXB4O21hcmdpbjowIDAgMjBweH0ucGFja2FnZS1zbmlwcGV0OmFjdGl2ZSwucGFja2FnZS1zbmlw
cGV0OmhvdmVye2JvcmRlci1jb2xvcjojZDNkM2QzO2JhY2tncm91bmQtaW1hZ2U6bm9uZX1AbWVk
aWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAwcHgpey5wYWNrYWdlLXNuaXBwZXR7cGFk
ZGluZzoxNXB4fX1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtaW4td2lkdGg6ODAxcHgpey5wYWNr
YWdlLXNuaXBwZXQsLnBhY2thZ2Utc25pcHBldDpob3ZlcntiYWNrZ3JvdW5kOiNmZmYgdXJsKC4u
L2ltYWdlcy93aGl0ZS1jdWJlLmUwZTkyNjNlLnBuZykgbm8tcmVwZWF0IDAgNTAlO2JhY2tncm91
bmQtaW1hZ2U6dXJsKC4uL2ltYWdlcy93aGl0ZS1jdWJlLjhjM2E2ZmU5LnN2ZyksbGluZWFyLWdy
YWRpZW50KHRyYW5zcGFyZW50LHRyYW5zcGFyZW50KTtiYWNrZ3JvdW5kLXBvc2l0aW9uOjIwcHh9
fS5wYWNrYWdlLXNuaXBwZXRfX3RpdGxle2ZvbnQtc2l6ZToxLjE1cmVtO2ZvbnQtd2VpZ2h0OjYw
MDtwYWRkaW5nLWJvdHRvbTowO2Rpc3BsYXk6YmxvY2t9LnBhY2thZ2Utc25pcHBldF9fdGl0bGUt
LXBhZ2UtdGl0bGUsLnBhY2thZ2Utc25pcHBldF9fdGl0bGUtLXBhZ2UtdGl0bGU6Zmlyc3QtY2hp
bGR7Zm9udC1zaXplOjEuNXJlbTtmb250LXdlaWdodDo2MDA7cGFkZGluZy10b3A6MXB4O3BhZGRp
bmctYm90dG9tOjVweH0ucGFja2FnZS1zbmlwcGV0X19tZXRhe3BhZGRpbmc6MXB4IDAgMnB4fS5w
YWNrYWdlLXNuaXBwZXRfX3ZlcnNpb257Zm9udC13ZWlnaHQ6NjAwfS5wYWNrYWdlLXNuaXBwZXRf
X3JlbGVhc2Vke2ZvbnQtd2VpZ2h0OjQwMDtmbG9hdDpyaWdodDtjb2xvcjojNDY0NjQ2O2ZvbnQt
c2l6ZToxcmVtfUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo4MDBweCl7LnBhY2th
Z2Utc25pcHBldF9fcmVsZWFzZWR7ZmxvYXQ6bm9uZTtkaXNwbGF5OmJsb2NrfX0ucGFja2FnZS1z
bmlwcGV0X19kZXNjcmlwdGlvbntjbGVhcjpib3RoO2NvbG9yOiM0NjQ2NDZ9LnBhY2thZ2Utc25p
cHBldF9fc29sZS1vd25lci1iYWRnZXttYXJnaW4tbGVmdDo0cHg7cG9zaXRpb246cmVsYXRpdmU7
dG9wOi0xcHh9LnBhY2thZ2Utc25pcHBldF9fYnV0dG9uc3tmbGV4LXNocmluazowfS5wYWNrYWdl
LXNuaXBwZXRfX2J1dHRvbnMgLmJ1dHRvbntkaXNwbGF5OmlubGluZS1ibG9jaztmbG9hdDpsZWZ0
O3BvaW50ZXItZXZlbnRzOmF1dG99LnBhY2thZ2Utc25pcHBldF9fYnV0dG9ucyAuYnV0dG9uLS1k
YW5nZXIsLnBhY2thZ2Utc25pcHBldF9fYnV0dG9ucyAuYnV0dG9uLS1wcmltYXJ5e21hcmdpbi1y
aWdodDo1cHh9LnBhY2thZ2Utc25pcHBldC0tbWFyZ2luLWJvdHRvbXttYXJnaW4tYm90dG9tOjB9
QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjgwMHB4KXsucGFja2FnZS1zbmlwcGV0
LS1tYXJnaW4tYm90dG9te21hcmdpbi1ib3R0b206MzBweH19LnBhc3N3b3JkLXN0cmVuZ3Roe2Rp
c3BsYXk6aW5saW5lLWJsb2NrO3dpZHRoOjEwMCU7aGVpZ2h0Oi44ZW07Ym9yZGVyOjFweCBzb2xp
ZCAjZDNkM2QzfS5wYXNzd29yZC1zdHJlbmd0aCAucGFzc3dvcmQtc3RyZW5ndGhfX2dhdWdle3dp
ZHRoOjA7aGVpZ2h0OjEwMCU7ZGlzcGxheTpibG9ja30ucGFzc3dvcmQtc3RyZW5ndGggLnBhc3N3
b3JkLXN0cmVuZ3RoX19nYXVnZS0tMHt3aWR0aDoyMCU7YmFja2dyb3VuZC1jb2xvcjojZDUyZDQw
fS5wYXNzd29yZC1zdHJlbmd0aCAucGFzc3dvcmQtc3RyZW5ndGhfX2dhdWdlLS0xe3dpZHRoOjQw
JTtiYWNrZ3JvdW5kLWNvbG9yOiNmZjk5MTh9LnBhc3N3b3JkLXN0cmVuZ3RoIC5wYXNzd29yZC1z
dHJlbmd0aF9fZ2F1Z2UtLTJ7d2lkdGg6NjAlO2JhY2tncm91bmQtY29sb3I6I2ZmZDM0M30ucGFz
c3dvcmQtc3RyZW5ndGggLnBhc3N3b3JkLXN0cmVuZ3RoX19nYXVnZS0tM3t3aWR0aDo4MCU7YmFj
a2dyb3VuZC1jb2xvcjojMDA2ZGFkfS5wYXNzd29yZC1zdHJlbmd0aCAucGFzc3dvcmQtc3RyZW5n
dGhfX2dhdWdlLS00e3dpZHRoOjEwMCU7YmFja2dyb3VuZC1jb2xvcjojMTQ4MDI0fS5wcm9qZWN0
LWRlc2NyaXB0aW9ue2RpcmVjdGlvbjpsdHI7bWFyZ2luLWJvdHRvbTozMHB4O2xpbmUtaGVpZ2h0
OjEuNX0ucHJvamVjdC1kZXNjcmlwdGlvbiBoMSwucHJvamVjdC1kZXNjcmlwdGlvbiBoMiwucHJv
amVjdC1kZXNjcmlwdGlvbiBoMywucHJvamVjdC1kZXNjcmlwdGlvbiBoNCwucHJvamVjdC1kZXNj
cmlwdGlvbiBoNSwucHJvamVjdC1kZXNjcmlwdGlvbiBoNntwYWRkaW5nOjA7bWFyZ2luOjMwcHgg
MCAwfS5wcm9qZWN0LWRlc2NyaXB0aW9uIGgxe2ZvbnQtc2l6ZToxLjdyZW19LnByb2plY3QtZGVz
Y3JpcHRpb24gaDErcCwucHJvamVjdC1kZXNjcmlwdGlvbiBoMitwLC5wcm9qZWN0LWRlc2NyaXB0
aW9uIGgzK3AsLnByb2plY3QtZGVzY3JpcHRpb24gaDQrcCwucHJvamVjdC1kZXNjcmlwdGlvbiBo
NStwLC5wcm9qZWN0LWRlc2NyaXB0aW9uIGg2K3B7bWFyZ2luLXRvcDozMHB4fS5wcm9qZWN0LWRl
c2NyaXB0aW9uIGE+aW1ne2JhY2tncm91bmQtY29sb3I6I2ZmZn0ucHJvamVjdC1kZXNjcmlwdGlv
bj46Zmlyc3QtY2hpbGQsLnByb2plY3QtZGVzY3JpcHRpb24+ZGl2OmZpcnN0LWNoaWxkPjpmaXJz
dC1jaGlsZHttYXJnaW4tdG9wOjB9LnByb2plY3QtZGVzY3JpcHRpb24gcHtwYWRkaW5nOjA7bWFy
Z2luLXRvcDoxNXB4fS5wcm9qZWN0LWRlc2NyaXB0aW9uIGIsLnByb2plY3QtZGVzY3JpcHRpb24g
c3Ryb25ne2ZvbnQtd2VpZ2h0OjYwMH0ucHJvamVjdC1kZXNjcmlwdGlvbiBlbSwucHJvamVjdC1k
ZXNjcmlwdGlvbiBpe2ZvbnQtc3R5bGU6aXRhbGljfS5wcm9qZWN0LWRlc2NyaXB0aW9uIHByZXtk
aXNwbGF5OmJsb2NrO3BhZGRpbmc6MTVweDttYXJnaW46MzBweCAwIDA7b3ZlcmZsb3cteDphdXRv
fS5wcm9qZWN0LWRlc2NyaXB0aW9uIHByZSBjb2Rle2ZvbnQtc2l6ZTppbmhlcml0O3BhZGRpbmc6
MDtiYWNrZ3JvdW5kLWNvbG9yOnRyYW5zcGFyZW50O2JvcmRlcjowO2NvbG9yOmluaGVyaXR9LnBy
b2plY3QtZGVzY3JpcHRpb24gb2wsLnByb2plY3QtZGVzY3JpcHRpb24gdWx7bWFyZ2luOjE1cHgg
MCAwIDMwcHg7cGFkZGluZy1ib3R0b206MH1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lk
dGg6NDAwcHgpey5wcm9qZWN0LWRlc2NyaXB0aW9uIG9sLC5wcm9qZWN0LWRlc2NyaXB0aW9uIHVs
e21hcmdpbi1sZWZ0OjE1cHh9fS5wcm9qZWN0LWRlc2NyaXB0aW9uIG9sIG9sLC5wcm9qZWN0LWRl
c2NyaXB0aW9uIG9sIHVsLC5wcm9qZWN0LWRlc2NyaXB0aW9uIHVsIG9sLC5wcm9qZWN0LWRlc2Ny
aXB0aW9uIHVsIHVse21hcmdpbjowIDAgMCAzMHB4fUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1h
eC13aWR0aDo0MDBweCl7LnByb2plY3QtZGVzY3JpcHRpb24gb2wgb2wsLnByb2plY3QtZGVzY3Jp
cHRpb24gb2wgdWwsLnByb2plY3QtZGVzY3JpcHRpb24gdWwgb2wsLnByb2plY3QtZGVzY3JpcHRp
b24gdWwgdWx7bWFyZ2luLWxlZnQ6MTVweH19LnByb2plY3QtZGVzY3JpcHRpb24gdWx7bGlzdC1z
dHlsZS10eXBlOmRpc2N9LnByb2plY3QtZGVzY3JpcHRpb24gbGl7cGFkZGluZzoycHggMH0ucHJv
amVjdC1kZXNjcmlwdGlvbiBsaSBwOmZpcnN0LWNoaWxke21hcmdpbi10b3A6MH0ucHJvamVjdC1k
ZXNjcmlwdGlvbiBsaSBwcmV7bWFyZ2luLWJvdHRvbToxNXB4fS5wcm9qZWN0LWRlc2NyaXB0aW9u
IGJsb2NrcXVvdGV7bWFyZ2luOjE1cHggMCAwIDE1cHg7Ym9yZGVyLWxlZnQ6M3B4IHNvbGlkICNi
YmI7Zm9udC1zdHlsZTppdGFsaWM7cGFkZGluZy1sZWZ0OjE1cHg7Y29sb3I6Izc5Nzk3OX1AbWVk
aWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAwcHgpey5wcm9qZWN0LWRlc2NyaXB0aW9u
IGJsb2NrcXVvdGV7bWFyZ2luLWxlZnQ6MH19LnByb2plY3QtZGVzY3JpcHRpb24gZGx7bWFyZ2lu
OjE1cHggMCAwfS5wcm9qZWN0LWRlc2NyaXB0aW9uIGRsIGR0e2ZvbnQtd2VpZ2h0OjYwMH0ucHJv
amVjdC1kZXNjcmlwdGlvbiBkbCBkZHttYXJnaW46MCAwIDVweCAxNXB4fS5wcm9qZWN0LWRlc2Ny
aXB0aW9uIHRhYmxle2JveC1zaGFkb3c6MXB4IDFweCAycHggMXB4IHJnYmEoMCwwLDAsLjA1KTti
YWNrZ3JvdW5kLWNvbG9yOiNmZmY7YmFja2dyb3VuZC1pbWFnZTpub25lO2JvcmRlcjoxcHggc29s
aWQgI2QzZDNkMztib3JkZXItY29sbGFwc2U6Y29sbGFwc2U7Ym9yZGVyLXNwYWNpbmc6MDt0ZXh0
LWFsaWduOmxlZnQ7d2lkdGg6MTAwJTttYXJnaW46MzBweCAwIDB9LnByb2plY3QtZGVzY3JpcHRp
b24gdGFibGU6YWN0aXZlLC5wcm9qZWN0LWRlc2NyaXB0aW9uIHRhYmxlOmhvdmVye2JvcmRlci1j
b2xvcjojZDNkM2QzO2JhY2tncm91bmQtaW1hZ2U6bm9uZX0ucHJvamVjdC1kZXNjcmlwdGlvbiB0
YWJsZSB0cntib3JkZXItYm90dG9tOjFweCBzb2xpZCAjZDNkM2QzfS5wcm9qZWN0LWRlc2NyaXB0
aW9uIHRhYmxlIHRkLC5wcm9qZWN0LWRlc2NyaXB0aW9uIHRhYmxlIHRoe21hcmdpbjowO2JvcmRl
cjowO3BhZGRpbmc6MTBweCA3cHg7Ym9yZGVyLXJpZ2h0OjFweCBzb2xpZCAjZDNkM2QzfS5wcm9q
ZWN0LWRlc2NyaXB0aW9uIHRhYmxlIHRoZWFkIHRye2JhY2tncm91bmQtY29sb3I6I2ZmZn0ucHJv
amVjdC1kZXNjcmlwdGlvbiB0YWJsZSB0aGVhZCB0ciB0aHt2ZXJ0aWNhbC1hbGlnbjpib3R0b207
Zm9udC13ZWlnaHQ6NjAwfS5wcm9qZWN0LWRlc2NyaXB0aW9uIHRhYmxlIHRib2R5IHRye2JhY2tn
cm91bmQtY29sb3I6I2ZiZmJmYn0ucHJvamVjdC1kZXNjcmlwdGlvbiB0YWJsZSB0Ym9keSB0cjpu
dGgtY2hpbGQoMm4pe2JhY2tncm91bmQtY29sb3I6I2Y4ZjhmOH0ucHJvamVjdC1kZXNjcmlwdGlv
biBocnttYXJnaW46MTVweCAwIDA7Ym9yZGVyOjFweCBzb2xpZCAjYmJifS5wcm9qZWN0LWRlc2Ny
aXB0aW9uPmF7bWFyZ2luLXRvcDoxNXB4fS5wcm9qZWN0LWRlc2NyaXB0aW9uIC5maWd1cmUuYWxp
Z24tbGVmdCwucHJvamVjdC1kZXNjcmlwdGlvbiBpbWcuYWxpZ24tbGVmdCwucHJvamVjdC1kZXNj
cmlwdGlvbiBvYmplY3QuYWxpZ24tbGVmdHtjbGVhcjpsZWZ0O2Zsb2F0OmxlZnQ7bWFyZ2luLXRv
cDoxNXB4O21hcmdpbi1yaWdodDoxNXB4fS5wcm9qZWN0LWRlc2NyaXB0aW9uIC5maWd1cmUuYWxp
Z24tcmlnaHQsLnByb2plY3QtZGVzY3JpcHRpb24gaW1nLmFsaWduLXJpZ2h0LC5wcm9qZWN0LWRl
c2NyaXB0aW9uIG9iamVjdC5hbGlnbi1yaWdodHtjbGVhcjpyaWdodDtmbG9hdDpyaWdodDttYXJn
aW4tdG9wOjE1cHg7bWFyZ2luLWxlZnQ6MTVweH0ucHJvamVjdC1kZXNjcmlwdGlvbiAuZmlndXJl
LmFsaWduLWNlbnRlciwucHJvamVjdC1kZXNjcmlwdGlvbiBpbWcuYWxpZ24tY2VudGVyLC5wcm9q
ZWN0LWRlc2NyaXB0aW9uIG9iamVjdC5hbGlnbi1jZW50ZXJ7ZGlzcGxheTpibG9jazttYXJnaW4t
dG9wOjE1cHg7bWFyZ2luLWxlZnQ6YXV0bzttYXJnaW4tcmlnaHQ6YXV0b30ucHJvamVjdC1kZXNj
cmlwdGlvbiAuY3tjb2xvcjojNzM3MzczfS5wcm9qZWN0LWRlc2NyaXB0aW9uIC5lcnJ7Y29sb3I6
IzgyMWEyNn0ucHJvamVjdC1kZXNjcmlwdGlvbiAua3tjb2xvcjojMDAyZDQ3fS5wcm9qZWN0LWRl
c2NyaXB0aW9uIC5jbXtjb2xvcjojNzM3MzczfS5wcm9qZWN0LWRlc2NyaXB0aW9uIC5jcHtjb2xv
cjojODIxYTI2fS5wcm9qZWN0LWRlc2NyaXB0aW9uIC5jMXtjb2xvcjojNzM3MzczfS5wcm9qZWN0
LWRlc2NyaXB0aW9uIC5jc3tjb2xvcjojODIxYTI2fS5wcm9qZWN0LWRlc2NyaXB0aW9uIC5nZHtj
b2xvcjojMDAwfS5wcm9qZWN0LWRlc2NyaXB0aW9uIC5nZXtmb250LXN0eWxlOml0YWxpY30ucHJv
amVjdC1kZXNjcmlwdGlvbiAuZ3J7Y29sb3I6IzgyMWEyNn0ucHJvamVjdC1kZXNjcmlwdGlvbiAu
Z2h7Y29sb3I6IzMwMzAzMH0ucHJvamVjdC1kZXNjcmlwdGlvbiAuZ2l7Y29sb3I6IzAwMH0ucHJv
amVjdC1kZXNjcmlwdGlvbiAuZ297Y29sb3I6IzczNzM3M30ucHJvamVjdC1kZXNjcmlwdGlvbiAu
Z3AsLnByb2plY3QtZGVzY3JpcHRpb24gLmd1e2NvbG9yOiM1NzU3NTd9LnByb2plY3QtZGVzY3Jp
cHRpb24gLmd0e2NvbG9yOiM4MjFhMjZ9LnByb2plY3QtZGVzY3JpcHRpb24gLmtjLC5wcm9qZWN0
LWRlc2NyaXB0aW9uIC5rZHtjb2xvcjojMTE2YTFlfS5wcm9qZWN0LWRlc2NyaXB0aW9uIC5rbntj
b2xvcjojMDAyZDQ3fS5wcm9qZWN0LWRlc2NyaXB0aW9uIC5rcCwucHJvamVjdC1kZXNjcmlwdGlv
biAua3J7Y29sb3I6IzExNmExZX0ucHJvamVjdC1kZXNjcmlwdGlvbiAua3R7Y29sb3I6IzczNzM3
M30ucHJvamVjdC1kZXNjcmlwdGlvbiAubXtjb2xvcjojMDA2ZGFkfS5wcm9qZWN0LWRlc2NyaXB0
aW9uIC5ze2NvbG9yOiNkNTJkNDB9LnByb2plY3QtZGVzY3JpcHRpb24gLm5he2NvbG9yOiMwMDc4
YmR9LnByb2plY3QtZGVzY3JpcHRpb24gLm5ie2NvbG9yOiMwMDJkNDd9LnByb2plY3QtZGVzY3Jp
cHRpb24gLm5je2NvbG9yOiNiMDZ9LnByb2plY3QtZGVzY3JpcHRpb24gLm5ve2NvbG9yOiMwMDJk
NDd9LnByb2plY3QtZGVzY3JpcHRpb24gLm5ke2NvbG9yOiM1NzU3NTd9LnByb2plY3QtZGVzY3Jp
cHRpb24gLm5le2NvbG9yOiNiMDZ9LnByb2plY3QtZGVzY3JpcHRpb24gLm5me2NvbG9yOiMwMDZk
YWR9LnByb2plY3QtZGVzY3JpcHRpb24gLm5se2NvbG9yOiMwMDc4YmQ7Zm9udC1zdHlsZTppdGFs
aWN9LnByb2plY3QtZGVzY3JpcHRpb24gLm5ue2NvbG9yOiNiMDZ9LnByb2plY3QtZGVzY3JpcHRp
b24gLnB5e2NvbG9yOiMwMDc4YmR9LnByb2plY3QtZGVzY3JpcHRpb24gLm50e2NvbG9yOiNiMDZ9
LnByb2plY3QtZGVzY3JpcHRpb24gLm52e2NvbG9yOiMwMDc4YmR9LnByb2plY3QtZGVzY3JpcHRp
b24gLm93e2NvbG9yOiMxMTZhMWV9LnByb2plY3QtZGVzY3JpcHRpb24gLnd7Y29sb3I6IzczNzM3
M30ucHJvamVjdC1kZXNjcmlwdGlvbiAubWYsLnByb2plY3QtZGVzY3JpcHRpb24gLm1oe2NvbG9y
OiMwMDZkYWR9LnByb2plY3QtZGVzY3JpcHRpb24gLm1pe2NvbG9yOiMxMTZhMWV9LnByb2plY3Qt
ZGVzY3JpcHRpb24gLm1ve2NvbG9yOiMwMDZkYWR9LnByb2plY3QtZGVzY3JpcHRpb24gLnMyLC5w
cm9qZWN0LWRlc2NyaXB0aW9uIC5zYiwucHJvamVjdC1kZXNjcmlwdGlvbiAuc2MsLnByb2plY3Qt
ZGVzY3JpcHRpb24gLnNke2NvbG9yOiNkNTJkNDB9LnByb2plY3QtZGVzY3JpcHRpb24gLnNle2Nv
bG9yOiMwMDRkN2F9LnByb2plY3QtZGVzY3JpcHRpb24gLnNoe2NvbG9yOiNkNTJkNDB9LnByb2pl
Y3QtZGVzY3JpcHRpb24gLnNpe2NvbG9yOiMwMDRkN2F9LnByb2plY3QtZGVzY3JpcHRpb24gLnN4
e2NvbG9yOiMxNDgwMjR9LnByb2plY3QtZGVzY3JpcHRpb24gLnNye2NvbG9yOiMxMTZhMWV9LnBy
b2plY3QtZGVzY3JpcHRpb24gLnMxe2NvbG9yOiNkNTJkNDB9LnByb2plY3QtZGVzY3JpcHRpb24g
LnNze2NvbG9yOiM3ZjRkMDB9LnByb2plY3QtZGVzY3JpcHRpb24gLmJwe2NvbG9yOiMwMDJkNDd9
LnByb2plY3QtZGVzY3JpcHRpb24gLnZje2NvbG9yOiMwMDc4YmR9LnByb2plY3QtZGVzY3JpcHRp
b24gLnZne2NvbG9yOiNhMzYyMDB9LnByb2plY3QtZGVzY3JpcHRpb24gLnZpe2NvbG9yOiMwMDRk
N2F9LnByb2plY3QtZGVzY3JpcHRpb24gLmlse2NvbG9yOiMwMDZkYWR9LnJlbGVhc2V7ZGlzcGxh
eTp0YWJsZTt0YWJsZS1sYXlvdXQ6Zml4ZWQ7d2lkdGg6MTAwJTtib3JkZXItbGVmdDoxcHggc29s
aWQgI2ZkZmRmZDtwYWRkaW5nOjAgMTVweH0ucmVsZWFzZTphZnRlcntjbGVhcjpib3RoO2NvbnRl
bnQ6IiI7ZGlzcGxheTp0YWJsZX0ucmVsZWFzZV9fbWV0YXt3aWR0aDoxMTBweDtkaXNwbGF5OnRh
YmxlLWNlbGw7dmVydGljYWwtYWxpZ246bWlkZGxlO3RleHQtYWxpZ246Y2VudGVyfS5yZWxlYXNl
X19tZXRhPi5iYWRnZXtmbG9hdDpyaWdodH1AbWVkaWEgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjgw
MHB4KXsucmVsZWFzZV9fbWV0YT4uYmFkZ2V7ZmxvYXQ6bGVmdDttYXJnaW4tcmlnaHQ6MTBweH19
QG1lZGlhIHNjcmVlbiBhbmQgKG1heC13aWR0aDo0MDBweCl7LnJlbGVhc2VfX21ldGF7ZGlzcGxh
eTpub25lfX0ucmVsZWFzZV9fZ3JhcGhpY3t3aWR0aDo4MHB4O2Rpc3BsYXk6dGFibGUtY2VsbDt0
ZXh0LWFsaWduOmNlbnRlcjt2ZXJ0aWNhbC1hbGlnbjptaWRkbGU7cG9zaXRpb246cmVsYXRpdmV9
QG1lZGlhIHNjcmVlbiBhbmQgKG1heC13aWR0aDo4MDBweCl7LnJlbGVhc2VfX2dyYXBoaWN7ZGlz
cGxheTpub25lfX0ucmVsZWFzZV9fbGluZXtwb3NpdGlvbjphYnNvbHV0ZTtsZWZ0OjA7Ym90dG9t
OjA7d2lkdGg6MTAwJTtoZWlnaHQ6MTAwJTt6LWluZGV4OjQ7YmFja2dyb3VuZDp1cmwoLi4vaW1h
Z2VzL2hpc3RvcnktbGluZS5kZWQwOTA2NC5wbmcpIHJlcGVhdC15IDUwJSA1MCV9LnJlbGVhc2Vf
X25vZGV7YmFja2dyb3VuZC1jb2xvcjojZmRmZGZkO3BhZGRpbmc6N3B4IDA7cG9zaXRpb246cmVs
YXRpdmU7ei1pbmRleDo1fS5yZWxlYXNlX19jYXJke2Rpc3BsYXk6YmxvY2s7Ym9yZGVyOjFweCBz
b2xpZCAjZDNkM2QzO2JveC1zaGFkb3c6MXB4IDFweCAycHggMXB4IHJnYmEoMCwwLDAsLjA1KTti
YWNrZ3JvdW5kLWNvbG9yOiNmZmY7YmFja2dyb3VuZC1pbWFnZTpub25lO3BhZGRpbmc6MTVweDtt
YXJnaW46MTVweCAwfS5yZWxlYXNlX19jYXJkOmFjdGl2ZSwucmVsZWFzZV9fY2FyZDpob3Zlcnti
b3JkZXItY29sb3I6I2QzZDNkMztiYWNrZ3JvdW5kLWltYWdlOm5vbmV9LnJlbGVhc2VfX3ZlcnNp
b257cGFkZGluZy1ib3R0b206MDtmb250LXNpemU6MS4yNXJlbTtmb250LXdlaWdodDo2MDB9LnJl
bGVhc2VfX3ZlcnNpb24tYmFkZ2V7bWFyZ2luLWxlZnQ6NHB4fS5yZWxlYXNlLS1jdXJyZW50e2Jv
cmRlcjoxcHggZG90dGVkICNjY2N9LnJlbGVhc2UtLWN1cnJlbnQsLnJlbGVhc2UtLWN1cnJlbnQg
LnJlbGVhc2VfX25vZGV7YmFja2dyb3VuZC1jb2xvcjojZmFmYWZhfS5yZWxlYXNlLS1jdXJyZW50
IC5yZWxlYXNlX19jYXJke2JhY2tncm91bmQtY29sb3I6I2ZmZjtib3gtc2hhZG93OjFweCAxcHgg
MnB4IDFweCByZ2JhKDAsMCwwLC4wNSl9LnJlbGVhc2UtLWxhdGVzdCAucmVsZWFzZV9fbGluZSwu
cmVsZWFzZS0tb2xkZXN0IC5yZWxlYXNlX19saW5le2hlaWdodDo1MCV9LnJlbGVhc2UtLW9sZGVz
dCAucmVsZWFzZV9fbGluZXtib3R0b206YXV0bzt0b3A6MH0ucmVsZWFzZS10aW1lbGluZXttYXJn
aW4tdG9wOjVweH0uc2VhcmNoLWZvcm17cG9zaXRpb246cmVsYXRpdmU7bWF4LXdpZHRoOjEwMCV9
LnNlYXJjaC1mb3JtIGlucHV0W3R5cGU9dGV4dF0uc2VhcmNoLWZvcm1fX3NlYXJjaHtkaXNwbGF5
OmlubGluZTtwYWRkaW5nLXJpZ2h0OjI4cHg7bWluLXdpZHRoOmF1dG87Ym9yZGVyLWNvbG9yOiNm
ZmZ9LnNlYXJjaC1mb3JtX19idXR0b257cG9zaXRpb246YWJzb2x1dGU7cmlnaHQ6MDt0b3A6MDtt
aW4taGVpZ2h0OjQwcHg7d2lkdGg6NDBweDtib3JkZXI6MDtiYWNrZ3JvdW5kLWNvbG9yOnRyYW5z
cGFyZW50O2NvbG9yOiM4ZDhkOGQ7Zm9udC1zaXplOjE4cHh9LnNlYXJjaC1mb3JtLS1wcmltYXJ5
e21hcmdpbjoyNXB4IDAgMCA0MHB4fUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAwcHgp
ey5zZWFyY2gtZm9ybS0tcHJpbWFyeXtkaXNwbGF5Om5vbmV9fS5zZWFyY2gtZm9ybS0tcHJpbWFy
eSBpbnB1dFt0eXBlPXRleHRdLnNlYXJjaC1mb3JtX19zZWFyY2h7d2lkdGg6NDAwcHh9QG1lZGlh
IHNjcmVlbiBhbmQgKG1heC13aWR0aDoxMDAwcHgpey5zZWFyY2gtZm9ybS0tcHJpbWFyeSBpbnB1
dFt0eXBlPXRleHRdLnNlYXJjaC1mb3JtX19zZWFyY2h7d2lkdGg6MjAwcHh9fS5zZWFyY2gtZm9y
bS0tbGFyZ2V7d2lkdGg6NjUwcHg7bWFyZ2luOjAgYXV0bztwYWRkaW5nOjAgMjBweH1AbWVkaWEg
c2NyZWVuIGFuZCAobWF4LXdpZHRoOjQwMHB4KXsuc2VhcmNoLWZvcm0tLWxhcmdle3BhZGRpbmc6
MCA1cHh9fS5zZWFyY2gtZm9ybS0tbGFyZ2UgaW5wdXRbdHlwZT10ZXh0XS5zZWFyY2gtZm9ybV9f
c2VhcmNoe3BhZGRpbmctcmlnaHQ6NTBweH0uc2VhcmNoLWZvcm0tLWxhcmdlIC5zZWFyY2gtZm9y
bV9fYnV0dG9ue21pbi1oZWlnaHQ6NTBweDt3aWR0aDo1MHB4O2ZvbnQtc2l6ZToyMHB4O3JpZ2h0
OjIwcHh9QG1lZGlhIHNjcmVlbiBhbmQgKG1heC13aWR0aDo0MDBweCl7LnNlYXJjaC1mb3JtLS1s
YXJnZSAuc2VhcmNoLWZvcm1fX2J1dHRvbntyaWdodDo1cHh9fS5zZWFyY2gtZm9ybS0tZnVsbHdp
ZHRoIGlucHV0W3R5cGU9dGV4dF0uc2VhcmNoLWZvcm1fX3NlYXJjaHt3aWR0aDoxMDAlfS5zaWRl
YmFyLXNlY3Rpb257cGFkZGluZy1ib3R0b206MjBweDttYXJnaW4tYm90dG9tOjIwcHg7Ym9yZGVy
LWJvdHRvbToycHggc29saWQgI2QzZDNkM30uc2lkZWJhci1zZWN0aW9uIC5zaWRlYmFyLXNlY3Rp
b25fX3RpdGxle2ZvbnQtc2l6ZToxLjFyZW19LnNpZGViYXItc2VjdGlvbiAuc2lkZWJhci1zZWN0
aW9uX191c2VyLWdyYXZhdGFye2JhY2tncm91bmQtaW1hZ2U6bm9uZX0uc2lkZWJhci1zZWN0aW9u
IC5zaWRlYmFyLXNlY3Rpb25fX3VzZXItZ3JhdmF0YXI6aG92ZXJ7YmFja2dyb3VuZC1pbWFnZTpu
b25lfS5zaWRlYmFyLXNlY3Rpb24gLnNpZGViYXItc2VjdGlvbl9fdXNlci1ncmF2YXRhcjphY3Rp
dmUsLnNpZGViYXItc2VjdGlvbiAuc2lkZWJhci1zZWN0aW9uX191c2VyLWdyYXZhdGFyOmZvY3Vz
e291dGxpbmU6MXB4IHNvbGlkICMwMDZkYWR9LnNpZGViYXItc2VjdGlvbiAuZXRoaWNhbC1zaWRl
YmFye2JvcmRlcjoycHggc29saWQgI2QzZDNkMztib3JkZXItcmFkaXVzOjVweDtwYWRkaW5nOjFy
ZW0gMXJlbSAuMjVyZW0gMWVtfS5zaWRlYmFyLXNlY3Rpb24gLmV0aGljYWwtY29udGVudHt0ZXh0
LWFsaWduOmNlbnRlcn0uc2lkZWJhci1zZWN0aW9uIC5ldGhpY2FsLWNvbnRlbnQgaW1ne3dpZHRo
OjYwJTtkaXNwbGF5OmlubGluZS1ibG9ja30uc2lkZWJhci1zZWN0aW9uIC5ldGhpY2FsLWltYWdl
LWxpbmt7YmFja2dyb3VuZC1pbWFnZTpub25lfS5zaWRlYmFyLXNlY3Rpb24gLmV0aGljYWwtaW1h
Z2UtbGluazpob3ZlcntiYWNrZ3JvdW5kLWltYWdlOm5vbmV9LnNpZGViYXItc2VjdGlvbiAuZXRo
aWNhbC10ZXh0e3BhZGRpbmctdG9wOjFyZW07cGFkZGluZy1ib3R0b206MXJlbX0uc2lkZWJhci1z
ZWN0aW9uOmxhc3Qtb2YtdHlwZXttYXJnaW4tYm90dG9tOjA7cGFkZGluZy1ib3R0b206MDtib3Jk
ZXI6MH0uc2lkZWJhci1zZWN0aW9uX19tYWludGFpbmVye2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVt
czpjZW50ZXJ9LnNpZGViYXItc2VjdGlvbl9fbWFpbnRhaW5lcjpub3QoOmxhc3Qtb2YtdHlwZSl7
bWFyZ2luLWJvdHRvbTo1cHh9LnNpZGViYXItc2VjdGlvbl9fbWFpbnRhaW5lciBhe2JhY2tncm91
bmQtaW1hZ2U6bm9uZX0uc2lkZWJhci1zZWN0aW9uX19tYWludGFpbmVyIGE6aG92ZXJ7YmFja2dy
b3VuZC1pbWFnZTpub25lfS5zaWRlYmFyLXNlY3Rpb25fX21haW50YWluZXIgYTphY3RpdmUsLnNp
ZGViYXItc2VjdGlvbl9fbWFpbnRhaW5lciBhOmZvY3Vze291dGxpbmU6MXB4IHNvbGlkICMwMDZk
YWR9LnNpZGViYXItc2VjdGlvbl9fY2xhc3NpZmllcnN7bWFyZ2luOjA7cGFkZGluZzowO2xpc3Qt
c3R5bGUtdHlwZTpub25lfS5zaWRlYmFyLXNlY3Rpb25fX2NsYXNzaWZpZXJzIGxpe3BhZGRpbmc6
MDttYXJnaW46MTVweCAwIDB9LnNpZGViYXItc2VjdGlvbl9fY2xhc3NpZmllcnMgbGk6Zmlyc3Qt
b2YtdHlwZSwuc2lkZWJhci1zZWN0aW9uX19jbGFzc2lmaWVycyBsaSB1bCBsaXttYXJnaW4tdG9w
OjB9LnNpZGViYXItc2VjdGlvbl9fdXNlci1ncmF2YXRhcnttYXJnaW4tcmlnaHQ6MTBweDttYXJn
aW4tYm90dG9tOjVweH0uc2lkZWJhci1zZWN0aW9uX191c2VyLWdyYXZhdGFyIGltZ3ttYXgtd2lk
dGg6NTBweH1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6MTAwMHB4KXsuc2lkZWJh
ci1zZWN0aW9uX191c2VyLWdyYXZhdGFyIGltZ3ttYXgtd2lkdGg6NDBweDttYXgtaGVpZ2h0OjQw
cHh9fS5zaWRlYmFyLXNlY3Rpb25fX3VzZXItZ3JhdmF0YXItdGV4dHttYXJnaW4tYm90dG9tOjVw
eDt3b3JkLWJyZWFrOmJyZWFrLXdvcmQ7d29yZC13cmFwOmJyZWFrLXdvcmQ7ZGlzcGxheTppbmxp
bmUtYmxvY2s7bWF4LXdpZHRoOmNhbGMoMTAwJSAtIDYwcHgpO3RleHQtZGVjb3JhdGlvbjpub25l
O2JhY2tncm91bmQtcG9zaXRpb246MCAxLjE1ZW07YmFja2dyb3VuZC1yZXBlYXQ6cmVwZWF0LXg7
YmFja2dyb3VuZC1zaXplOjEwMCUgMS41cHg7Y29sb3I6IzAwNmRhZDtiYWNrZ3JvdW5kLWltYWdl
OmxpbmVhci1ncmFkaWVudCg5MGRlZywjMDA2ZGFkLHJnYmEoMCwxMDksMTczLC43KSl9LnNpZGVi
YXItc2VjdGlvbl9fdXNlci1ncmF2YXRhci10ZXh0OmhvdmVye2NvbG9yOiMwMDRkN2E7YmFja2dy
b3VuZC1pbWFnZTpsaW5lYXItZ3JhZGllbnQoOTBkZWcsIzAwNGQ3YSwjMDA0ZDdhKX0uc2lkZWJh
ci1zZWN0aW9uX191c2VyLWdyYXZhdGFyLXRleHQ6YWN0aXZlLC5zaWRlYmFyLXNlY3Rpb25fX3Vz
ZXItZ3JhdmF0YXItdGV4dDpmb2N1c3tvdXRsaW5lOjFweCBzb2xpZCAjMDA2ZGFkfUBtZWRpYSBv
bmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDoxMDAwcHgpey5zaWRlYmFyLXNlY3Rpb25fX3VzZXIt
Z3JhdmF0YXItdGV4dHttYXgtd2lkdGg6Y2FsYygxMDAlIC0gNTBweCl9fS5zaXRlLWhlYWRlcnti
YWNrZ3JvdW5kLWNvbG9yOiMwMDczYjc7YmFja2dyb3VuZC1yZXBlYXQ6cmVwZWF0O2JhY2tncm91
bmQtcG9zaXRpb246MCA1MCU7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgIzAwNjdhM30uc2l0ZS1o
ZWFkZXJfX2xvZ297cGFkZGluZzoxNXB4IDA7bWF4LXdpZHRoOjY1cHg7ZmxvYXQ6bGVmdDtiYWNr
Z3JvdW5kLWltYWdlOm5vbmV9LnNpdGUtaGVhZGVyX19sb2dvOmhvdmVye2JhY2tncm91bmQtaW1h
Z2U6bm9uZX0uc2l0ZS1oZWFkZXJfX2xvZ286YWN0aXZlLC5zaXRlLWhlYWRlcl9fbG9nbzpmb2N1
c3tvdXRsaW5lOjFweCBzb2xpZCAjZmZmfUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6NjAw
cHgpey5zaXRlLWhlYWRlcl9fbG9nb3ttYXgtd2lkdGg6NTBweH19LnNpdGUtaGVhZGVyLS10ZXN0
LXB5cGl7YmFja2dyb3VuZC1pbWFnZTp1cmwoLi4vaW1hZ2VzL3Rlc3RpbmcuNTJjZjZjZTkucG5n
KX0uc2l0ZS1oZWFkZXItLWRldi1weXBpe2JhY2tncm91bmQtaW1hZ2U6dXJsKC4uL2ltYWdlcy9k
ZXYuMzkxZTA1MTkucG5nKX0uc2tpcC10by1jb250ZW50e3Bvc2l0aW9uOmFic29sdXRlO3RvcDph
dXRvO2xlZnQ6LTEwMDAwcHg7d2lkdGg6MXB4O2hlaWdodDoxcHg7b3ZlcmZsb3c6aGlkZGVuO3ot
aW5kZXg6MTI7YmFja2dyb3VuZC1pbWFnZTpub25lfS5za2lwLXRvLWNvbnRlbnQ6aG92ZXJ7YmFj
a2dyb3VuZC1pbWFnZTpub25lfS5za2lwLXRvLWNvbnRlbnQ6Zm9jdXN7dG9wOjdweDtsZWZ0Ojdw
eDt3aWR0aDphdXRvO2hlaWdodDphdXRvO2xpbmUtaGVpZ2h0OjE7cGFkZGluZzoxNXB4O2NvbG9y
OiMwMDZkYWQ7Zm9udC13ZWlnaHQ6NjAwO2JhY2tncm91bmQtY29sb3I6I2ZmZn0uc3BvbnNvci1n
cmlke21hcmdpbi10b3A6MzBweH0uc3BvbnNvci1ncmlkX19zcG9uc29ye2JvcmRlcjoxcHggc29s
aWQgI2QzZDNkMztib3gtc2hhZG93OjFweCAxcHggMnB4IDFweCByZ2JhKDAsMCwwLC4wNSk7YmFj
a2dyb3VuZC1jb2xvcjojZmZmO2JhY2tncm91bmQtaW1hZ2U6bm9uZTtwYWRkaW5nOjMwcHg7dGV4
dC1hbGlnbjpjZW50ZXI7bWFyZ2luLWJvdHRvbTozMHB4fS5zcG9uc29yLWdyaWRfX3Nwb25zb3I6
YWN0aXZlLC5zcG9uc29yLWdyaWRfX3Nwb25zb3I6aG92ZXJ7Ym9yZGVyLWNvbG9yOiNkM2QzZDM7
YmFja2dyb3VuZC1pbWFnZTpub25lfS5zcG9uc29yLWdyaWRfX3Nwb25zb3ItLWludml0YXRpb24s
LnNwb25zb3ItZ3JpZF9fc3BvbnNvci0taW52aXRhdGlvbjpob3Zlcntib3JkZXItY29sb3I6IzAw
NmRhZH0uc3BvbnNvci1ncmlkX19zcG9uc29yLWltZ3ttYXJnaW46MjBweCAwfS5zcG9uc29yLWdy
aWRfX3Nwb25zb3ItbmFtZXtwYWRkaW5nLXRvcDoyMHB4fS5zcG9uc29yLWdyaWRfX3Nwb25zb3It
YWN0aXZpdHl7Zm9udC13ZWlnaHQ6NjAwO2NvbG9yOiM2MDYwNjA7Zm9udC1zaXplOjEuMTVyZW07
bWF4LXdpZHRoOjcwMHB4O21hcmdpbjowIGF1dG99LnNwb25zb3ItZ3JpZF9fc3BvbnNvci1saW5r
e21hcmdpbi10b3A6MzBweH0uc3BvbnNvci1ncmlkLS1ib3R0b20tbWFyZ2lue21hcmdpbi1ib3R0
b206NjBweH1Ac3VwcG9ydHMgKGRpc3BsYXk6Z3JpZCl7LnNwb25zb3ItZ3JpZHtkaXNwbGF5Omdy
aWQ7Z3JpZC1nYXA6MzBweDtncmlkLXRlbXBsYXRlLWNvbHVtbnM6cmVwZWF0KGF1dG8tZmlsbCxt
aW5tYXgoMzAwcHgsMWZyKSl9QG1lZGlhIHNjcmVlbiBhbmQgKG1heC13aWR0aDo0MDBweCl7LnNw
b25zb3ItZ3JpZHtncmlkLXRlbXBsYXRlLWNvbHVtbnM6cmVwZWF0KGF1dG8tZmlsbCwxMDAlKX19
LnNwb25zb3ItZ3JpZF9fc3BvbnNvcnt0ZXh0LWFsaWduOmxlZnQ7bWFyZ2luLWJvdHRvbTowO3Bv
c2l0aW9uOnJlbGF0aXZlO3BhZGRpbmctYm90dG9tOjExMHB4fS5zcG9uc29yLWdyaWRfX3Nwb25z
b3ItaW1ne2hlaWdodDoyMDBweDt3aWR0aDoyNTBweDttYXgtd2lkdGg6MTAwJTttYXJnaW46MCBh
dXRvO2Rpc3BsYXk6ZmxleDtqdXN0aWZ5LWNvbnRlbnQ6Y2VudGVyO2FsaWduLWl0ZW1zOmNlbnRl
cn1AbWVkaWEgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjQwMHB4KXsuc3BvbnNvci1ncmlkX19zcG9u
c29yLWltZ3toZWlnaHQ6MTMwcHh9fS5zcG9uc29yLWdyaWRfX3Nwb25zb3ItaW1nIGltZ3twYWRk
aW5nOjJlbX0uc3BvbnNvci1ncmlkX19zcG9uc29yLWFjdGl2aXR5e21heC13aWR0aDoxMDAlO21h
cmdpbjowfS5zcG9uc29yLWdyaWRfX3Nwb25zb3ItbGlua3t3aWR0aDpjYWxjKDEwMCUgLSA2MHB4
KTtwb3NpdGlvbjphYnNvbHV0ZTtib3R0b206MzBweDtkaXNwbGF5OmJsb2NrO3RleHQtYWxpZ246
Y2VudGVyO21hcmdpbi10b3A6MH19LnNwb25zb3ItcGFja2FnZXN7ZGlzcGxheTpncmlkO2dyaWQt
Z2FwOjMwcHg7Z3JpZC10ZW1wbGF0ZS1jb2x1bW5zOnJlcGVhdChhdXRvLWZpbGwsbWlubWF4KDMw
MHB4LDFmcikpO21hcmdpbjo0NXB4IDAgNjBweH1AbWVkaWEgc2NyZWVuIGFuZCAobWF4LXdpZHRo
OjQwMHB4KXsuc3BvbnNvci1wYWNrYWdlc3tncmlkLXRlbXBsYXRlLWNvbHVtbnM6cmVwZWF0KGF1
dG8tZmlsbCwxMDAlKX19LnNwb25zb3ItcGFja2FnZXMgLnNwb25zb3ItcGFja2FnZXttYXJnaW4t
dG9wOjMwcHh9LnNwb25zb3ItcGFja2FnZXtib3JkZXI6MnB4IHNvbGlkICMwMDZkYWQ7Ym9yZGVy
LXJhZGl1czo0cHg7cG9zaXRpb246cmVsYXRpdmU7cGFkZGluZy1ib3R0b206ODBweH0uc3BvbnNv
ci1wYWNrYWdlX19oZWFkZXJ7YmFja2dyb3VuZC1jb2xvcjojMDA2ZGFkO2NvbG9yOiNmZmY7cGFk
ZGluZzozMHB4O3RleHQtYWxpZ246Y2VudGVyO3Bvc2l0aW9uOnJlbGF0aXZlO2JvcmRlci1yYWRp
dXM6MnB4IDJweCAwIDB9LnNwb25zb3ItcGFja2FnZV9faGVhZGVyIGF7Y29sb3I6aHNsYSgwLDAl
LDEwMCUsLjk1KTtiYWNrZ3JvdW5kLWltYWdlOmxpbmVhci1ncmFkaWVudCg5MGRlZywjZmZmLGhz
bGEoMCwwJSwxMDAlLC43KSl9LnNwb25zb3ItcGFja2FnZV9faGVhZGVyIGE6YWN0aXZlLC5zcG9u
c29yLXBhY2thZ2VfX2hlYWRlciBhOmZvY3Vze291dGxpbmU6MXB4IHNvbGlkICNmZmZ9LnNwb25z
b3ItcGFja2FnZV9faGVhZGVyIGgyLC5zcG9uc29yLXBhY2thZ2VfX2hlYWRlciBoM3tmb250LXNp
emU6MS4zcmVtO2ZvbnQtd2VpZ2h0OjYwMDtwYWRkaW5nOjB9LnNwb25zb3ItcGFja2FnZV9faWNv
bntwb3NpdGlvbjphYnNvbHV0ZTt0b3A6LTMwcHg7Ym9yZGVyLXJhZGl1czo1MCU7cGFkZGluZzox
MHB4O3dpZHRoOjYwcHg7aGVpZ2h0OjYwcHg7bGVmdDo1MCU7bWFyZ2luLWxlZnQ6LTMwcHg7YmFj
a2dyb3VuZC1jb2xvcjojMDA2ZGFkO2ZvbnQtc2l6ZTozMHB4fS5zcG9uc29yLXBhY2thZ2VfX2Jv
ZHl7cGFkZGluZzozMHB4fS5zcG9uc29yLXBhY2thZ2VfX2JvZHkgdWx7cGFkZGluZzowO21hcmdp
bjowfS5zcG9uc29yLXBhY2thZ2VfX2JvZHkgdWwgbGl7cGFkZGluZzoxMHB4IDA7bWFyZ2luLWxl
ZnQ6MjBweH0uc3BvbnNvci1wYWNrYWdlX19ib2R5IHVsIGxpOmZpcnN0LW9mLXR5cGV7cGFkZGlu
Zy10b3A6MH0uc3BvbnNvci1wYWNrYWdlX19ib2R5IHVsK3B7Zm9udC13ZWlnaHQ6NjAwO3BhZGRp
bmc6MDttYXJnaW46MTVweCAwIDB9LnNwb25zb3ItcGFja2FnZV9fYnV0dG9ue3Bvc2l0aW9uOmFi
c29sdXRlO2JvdHRvbTozMHB4O2xlZnQ6MzBweDt3aWR0aDpjYWxjKDEwMCUgLSA2MHB4KTt0ZXh0
LWFsaWduOmNlbnRlcn0uc3BvbnNvci1wYWNrYWdlX19idXR0b24gLmJ1dHRvbnt3aWR0aDoxMDAl
O21hcmdpbi1ib3R0b206MTVweH0uc3BvbnNvcnN7dGV4dC1hbGlnbjpjZW50ZXI7Ym9yZGVyLXRv
cDoxcHggc29saWQgIzAwNjdhMztiYWNrZ3JvdW5kLWNvbG9yOiMwMDZkYWQ7cGFkZGluZzoxNXB4
fS5zcG9uc29yc19fdGl0bGV7ZGlzcGxheTpub25lO3BhZGRpbmctYm90dG9tOjEwcHg7bWFyZ2lu
LWJvdHRvbToxMHB4O2JvcmRlci1ib3R0b206MXB4IHNvbGlkIGhzbGEoMCwwJSwxMDAlLC4yKTtj
b2xvcjojZmZmfUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo2MDBweCl7LnNwb25z
b3JzX190aXRsZXtkaXNwbGF5OmJsb2NrfX0uc3BvbnNvcnNfX3Nwb25zb3J7ZGlzcGxheTppbmxp
bmUtYmxvY2s7dGV4dC1hbGlnbjpjZW50ZXI7cGFkZGluZzoxNXB4IDEzcHggMTBweDtvcGFjaXR5
Oi45NTtiYWNrZ3JvdW5kLWltYWdlOm5vbmV9LnNwb25zb3JzX19zcG9uc29yOmhvdmVye2JhY2tn
cm91bmQtaW1hZ2U6bm9uZX0uc3BvbnNvcnNfX3Nwb25zb3I6YWN0aXZlLC5zcG9uc29yc19fc3Bv
bnNvcjpmb2N1c3tvdXRsaW5lOjFweCBzb2xpZCAjZmZmfS5zcG9uc29yc19fc3BvbnNvcjpob3Zl
cntvcGFjaXR5OjF9LnNwb25zb3JzX19zcG9uc29yOmhvdmVyIC5zcG9uc29yc19faW1hZ2V7b3Bh
Y2l0eToxfUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo4MDBweCl7LnNwb25zb3Jz
X19zcG9uc29ye3BhZGRpbmc6N3B4IDEwcHh9fUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13
aWR0aDo2MDBweCl7LnNwb25zb3JzX19zcG9uc29ye3BhZGRpbmc6NXB4IDdweH19LnNwb25zb3Jz
X19pbWFnZXttYXgtd2lkdGg6MTAwcHg7b3BhY2l0eTouOH1AbWVkaWEgb25seSBzY3JlZW4gYW5k
IChtYXgtd2lkdGg6ODAwcHgpey5zcG9uc29yc19faW1hZ2V7ZGlzcGxheTpub25lfX0uc3BvbnNv
cnNfX25hbWUsLnNwb25zb3JzX19zZXJ2aWNle21heC13aWR0aDoxMDBweDtkaXNwbGF5OmJsb2Nr
O2ZvbnQtc2l6ZTouNzVyZW07Y29sb3I6I2ZmZn0uc3BvbnNvcnNfX25hbWV7Zm9udC13ZWlnaHQ6
NjAwO21hcmdpbi10b3A6MTBweH1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6NjAw
cHgpey5zcG9uc29yc19fbmFtZXttYXJnaW46MDtmb250LXdlaWdodDo0MDB9fUBtZWRpYSBvbmx5
IHNjcmVlbiBhbmQgKG1heC13aWR0aDo2MDBweCl7LnNwb25zb3JzX19zZXJ2aWNle2Rpc3BsYXk6
bm9uZX19LnNwb25zb3JzaGlwLWJlbmVmaXRze2Rpc3BsYXk6ZmxleH1AbWVkaWEgb25seSBzY3Jl
ZW4gYW5kIChtYXgtd2lkdGg6MTAwMHB4KXsuc3BvbnNvcnNoaXAtYmVuZWZpdHN7ZGlzcGxheTpi
bG9jaztwYWRkaW5nOjMwcHggMCAwfX0uc3BvbnNvcnNoaXAtYmVuZWZpdHNfX2JlbmVmaXR7d2lk
dGg6MzMlO3BhZGRpbmc6MzBweH1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6MTAw
MHB4KXsuc3BvbnNvcnNoaXAtYmVuZWZpdHNfX2JlbmVmaXR7d2lkdGg6MTAwJTtwYWRkaW5nOjAg
MCAzMHB4fX0uc3BvbnNvcnNoaXAtaW50cm97ZGlzcGxheTpmbGV4fUBtZWRpYSBvbmx5IHNjcmVl
biBhbmQgKG1heC13aWR0aDoxMDAwcHgpey5zcG9uc29yc2hpcC1pbnRyb3tkaXNwbGF5OmJsb2Nr
fX0uc3BvbnNvcnNoaXAtaW50cm9fX3RleHR7d2lkdGg6NzAlO3BhZGRpbmctcmlnaHQ6NjBweH1A
bWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6MTAwMHB4KXsuc3BvbnNvcnNoaXAtaW50
cm9fX3RleHR7d2lkdGg6MTAwJTtwYWRkaW5nOjA7bWFyZ2luLWJvdHRvbTo2MHB4fX0uc3BvbnNv
cnNoaXAtaW50cm9fX3RleHQgaDF7Zm9udC1zaXplOjEuNXJlbTtmb250LXdlaWdodDo2MDA7cGFk
ZGluZy1ib3R0b206MH0uc3BvbnNvcnNoaXAtaW50cm9fX3RleHQgLmxlZGUtcGFyYWdyYXBoe21h
cmdpbjozMHB4IDA7cGFkZGluZzowfS5zcG9uc29yc2hpcC1pbnRyb19fZG9uYXRpb25ze3dpZHRo
OjMwJTtwYWRkaW5nLWJvdHRvbToxMjBweCFpbXBvcnRhbnR9QG1lZGlhIG9ubHkgc2NyZWVuIGFu
ZCAobWF4LXdpZHRoOjEwMDBweCl7LnNwb25zb3JzaGlwLWludHJvX19kb25hdGlvbnN7d2lkdGg6
MTAwJX19LnN0YXR1cy1iYWRnZXtkaXNwbGF5OmlubGluZS1mbGV4O2FsaWduLWl0ZW1zOmNlbnRl
cjtib3gtc2l6aW5nOmJvcmRlci1ib3g7Ym9yZGVyLXJhZGl1czozcHg7Zm9udC1zaXplOi44cmVt
O2NvbG9yOiM0NjQ2NDY7YmFja2dyb3VuZC1jb2xvcjojZmZmO2JvcmRlcjoxcHggc29saWQgaHNs
YSgwLDAlLDEwMCUsLjUpO3BhZGRpbmc6MCAxMnB4IDAgMDt0ZXh0LWFsaWduOmxlZnQ7bWluLWhl
aWdodDo0MHB4O2JhY2tncm91bmQtaW1hZ2U6bm9uZX0uc3RhdHVzLWJhZGdlOmhvdmVye2JhY2tn
cm91bmQtaW1hZ2U6bm9uZX0uc3RhdHVzLWJhZGdlOmFjdGl2ZSwuc3RhdHVzLWJhZGdlOmZvY3Vz
e291dGxpbmU6MXB4IHNvbGlkICNmZmZ9LnN0YXR1cy1iYWRnZSBzcGFue3RleHQtZGVjb3JhdGlv
bjp1bmRlcmxpbmV9LnN0YXR1cy1iYWRnZTpob3Zlcntjb2xvcjojNDY0NjQ2fS5zdGF0dXMtYmFk
Z2U6YmVmb3Jle2NvbnRlbnQ6Iu+BmiI7Zm9udC1mYW1pbHk6Rm9udCBBd2Vzb21lXCA1IEZyZWU7
Zm9udC13ZWlnaHQ6OTAwO3BhZGRpbmc6MTJweDttYXJnaW4tcmlnaHQ6MTJweDttaW4td2lkdGg6
NDBweDttaW4taGVpZ2h0OjQycHg7dGV4dC1hbGlnbjpjZW50ZXI7Ym9yZGVyLXJpZ2h0OjFweCBz
b2xpZCBoc2xhKDAsMCUsMTAwJSwuNCl9LnN0YXR1cy1iYWRnZS0tdW5rbm93bjpiZWZvcmV7Y29u
dGVudDoi74GZIn0uc3RhdHVzLWJhZGdlLS1nb29ke2NvbG9yOiNmZmY7YmFja2dyb3VuZC1jb2xv
cjojMTQ4MDI0fS5zdGF0dXMtYmFkZ2UtLWdvb2Q6aG92ZXJ7Y29sb3I6I2ZmZn0uc3RhdHVzLWJh
ZGdlLS1nb29kOmJlZm9yZXtjb250ZW50OiLvgIwifS5zdGF0dXMtYmFkZ2UtLXdhcm57YmFja2dy
b3VuZC1jb2xvcjojZmZkZjc2fS5zdGF0dXMtYmFkZ2UtLXdhcm46aG92ZXJ7Y29sb3I6I2ZmZn0u
c3RhdHVzLWJhZGdlLS13YXJuOmJlZm9yZXtjb250ZW50OiLvgbEifS5zdGF0dXMtYmFkZ2UtLWJh
ZHtjb2xvcjojZmZmO2JhY2tncm91bmQtY29sb3I6I2Q1MmQ0MH0uc3RhdHVzLWJhZGdlLS1iYWQ6
aG92ZXJ7Y29sb3I6I2ZmZn0uc3RhdHVzLWJhZGdlLS1iYWQ6YmVmb3Jle2NvbnRlbnQ6Iu+BsSJ9
LnN0YXRpc3RpY3MtYmFye3RleHQtYWxpZ246Y2VudGVyfS5zdGF0aXN0aWNzLWJhcl9fc3RhdGlz
dGlje2NvbG9yOiMwMDNkNjE7Zm9udC1zaXplOjEuMnJlbTtkaXNwbGF5OmlubGluZS1ibG9jaztw
YWRkaW5nOjEwcHggMjBweDttYXJnaW46MDtib3gtc2l6aW5nOmJvcmRlci1ib3h9QG1lZGlhIG9u
bHkgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjgwMHB4KXsuc3RhdGlzdGljcy1iYXJfX3N0YXRpc3Rp
Y3tmb250LXNpemU6MXJlbX19LnRhYmxle3dpZHRoOjEwMCU7Ym9yZGVyOjA7Ym94LXNpemluZzpi
b3JkZXItYm94O2JveC1zaGFkb3c6bm9uZX0udGFibGUsLnRhYmxlIHRoZWFkIHRye2JhY2tncm91
bmQtY29sb3I6dHJhbnNwYXJlbnR9LnRhYmxlIHRib2R5IHRyLC50YWJsZSB0ZCwudGFibGUgdGh7
Ym9yZGVyOjA7YmFja2dyb3VuZC1jb2xvcjp0cmFuc3BhcmVudDtwYWRkaW5nOjEwcHh9LnRhYmxl
IHRkLC50YWJsZSB0aHtib3JkZXItYm90dG9tOjFweCBzb2xpZCAjZWNlY2VjfS50YWJsZSB0ciB0
ZDpmaXJzdC1jaGlsZCwudGFibGUgdHIgdGg6Zmlyc3QtY2hpbGR7cGFkZGluZy1sZWZ0OjB9LnRh
YmxlIHRyIHRkOmxhc3QtY2hpbGQsLnRhYmxlIHRyIHRoOmxhc3QtY2hpbGR7cGFkZGluZy1yaWdo
dDowfS50YWJsZSB0Ym9keSB0cjpsYXN0LWNoaWxkIHRkLC50YWJsZSB0Ym9keSB0cjpsYXN0LWNo
aWxkIHRoe2JvcmRlci1ib3R0b206MH0udGFibGVfX2FsaWduLXJpZ2h0e3RleHQtYWxpZ246cmln
aHR9LnRhYmxlX19tb2JpbGUtbGFiZWx7ZGlzcGxheTpub25lO2ZvbnQtd2VpZ2h0OjYwMH0udGFi
bGUtLWRvd25sb2Fkc3t3b3JkLXdyYXA6YnJlYWstd29yZDttYXJnaW4tdG9wOjE1cHh9LnRhYmxl
LS1kb3dubG9hZHMgdGQgLmJ1dHRvbiBzcGFue2Rpc3BsYXk6bm9uZX1AbWVkaWEgb25seSBzY3Jl
ZW4gYW5kIChtYXgtd2lkdGg6ODAwcHgpey50YWJsZS0tZG93bmxvYWRze2JvcmRlci1ib3R0b206
MXB4IHNvbGlkICNlY2VjZWM7bWFyZ2luLWJvdHRvbToxNXB4fS50YWJsZS0tZG93bmxvYWRzIHRo
ZWFke2Rpc3BsYXk6bm9uZX0udGFibGUtLWRvd25sb2FkcyB0Ym9keSB0ciB0ZCwudGFibGUtLWRv
d25sb2FkcyB0Ym9keSB0ciB0ZDpmaXJzdC1jaGlsZCwudGFibGUtLWRvd25sb2FkcyB0Ym9keSB0
ciB0ZDpsYXN0LWNoaWxkLC50YWJsZS0tZG93bmxvYWRzIHRib2R5IHRyIHRoLC50YWJsZS0tZG93
bmxvYWRzIHRib2R5IHRyIHRoOmZpcnN0LWNoaWxkLC50YWJsZS0tZG93bmxvYWRzIHRib2R5IHRy
IHRoOmxhc3QtY2hpbGR7ZGlzcGxheTpibG9jazt3aWR0aDoxMDAlO3RleHQtYWxpZ246bGVmdDti
b3JkZXItYm90dG9tOjA7cGFkZGluZzoycHggMH0udGFibGUtLWRvd25sb2FkcyB0Ym9keSB0ciB0
ZDpmaXJzdC1jaGlsZCwudGFibGUtLWRvd25sb2FkcyB0Ym9keSB0ciB0aDpmaXJzdC1jaGlsZHti
b3JkZXItdG9wOjFweCBzb2xpZCAjZWNlY2VjO3BhZGRpbmctdG9wOjE1cHh9LnRhYmxlLS1kb3du
bG9hZHMgdGJvZHkgdHIgdGQ6Zmlyc3QtY2hpbGQgLnRhYmxlX19tb2JpbGUtbGFiZWwsLnRhYmxl
LS1kb3dubG9hZHMgdGJvZHkgdHIgdGg6Zmlyc3QtY2hpbGQgLnRhYmxlX19tb2JpbGUtbGFiZWx7
bWFyZ2luLXRvcDowfS50YWJsZS0tZG93bmxvYWRzIHRib2R5IHRyIHRkOmxhc3QtY2hpbGR7cGFk
ZGluZy1ib3R0b206MTVweH0udGFibGUtLWRvd25sb2FkcyAudGFibGVfX21vYmlsZS1sYWJlbHtk
aXNwbGF5OmJsb2NrO21hcmdpbi10b3A6NXB4fS50YWJsZS0tZG93bmxvYWRzIC50YWJsZV9fYWxp
Z24tcmlnaHR7dGV4dC1hbGlnbjpsZWZ0fS50YWJsZS0tZG93bmxvYWRzIHRib2R5IHRyIHRkIC5k
cm9wZG93bntkaXNwbGF5OmJsb2NrO2Zsb2F0Om5vbmV9LnRhYmxlLS1kb3dubG9hZHMgdGJvZHkg
dHIgdGQgLmRyb3Bkb3duIC5kcm9wZG93bl9fY29udGVudCwudGFibGUtLWRvd25sb2FkcyB0Ym9k
eSB0ciB0ZCAuZHJvcGRvd24gLmRyb3Bkb3duX19saW5re3dpZHRoOnVuc2V0O3JpZ2h0OmF1dG99
LnRhYmxlLS1kb3dubG9hZHMgdGJvZHkgdHIgdGQgLmJ1dHRvbnttYXJnaW4tdG9wOjVweH19LnRh
YmxlLS1yZWxlYXNlc3t3b3JkLXdyYXA6YnJlYWstd29yZDttYXJnaW4tYm90dG9tOjMwcHh9QG1l
ZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjYwMHB4KXsudGFibGUtLXJlbGVhc2Vze2Jv
cmRlci1ib3R0b206MXB4IHNvbGlkICNlY2VjZWM7bWFyZ2luLWJvdHRvbToxNXB4fS50YWJsZS0t
cmVsZWFzZXMgdGhlYWR7ZGlzcGxheTpub25lfS50YWJsZS0tcmVsZWFzZXMgdGJvZHkgdHIgdGQs
LnRhYmxlLS1yZWxlYXNlcyB0Ym9keSB0ciB0ZDpmaXJzdC1jaGlsZCwudGFibGUtLXJlbGVhc2Vz
IHRib2R5IHRyIHRkOmxhc3QtY2hpbGQsLnRhYmxlLS1yZWxlYXNlcyB0Ym9keSB0ciB0aCwudGFi
bGUtLXJlbGVhc2VzIHRib2R5IHRyIHRoOmZpcnN0LWNoaWxkLC50YWJsZS0tcmVsZWFzZXMgdGJv
ZHkgdHIgdGg6bGFzdC1jaGlsZHtkaXNwbGF5OmJsb2NrO3dpZHRoOjEwMCU7dGV4dC1hbGlnbjps
ZWZ0O2JvcmRlci1ib3R0b206MDtwYWRkaW5nOjJweCAwfS50YWJsZS0tcmVsZWFzZXMgdGJvZHkg
dHIgdGQ6Zmlyc3QtY2hpbGQsLnRhYmxlLS1yZWxlYXNlcyB0Ym9keSB0ciB0aDpmaXJzdC1jaGls
ZHtib3JkZXItdG9wOjFweCBzb2xpZCAjZWNlY2VjO3BhZGRpbmctdG9wOjE1cHh9LnRhYmxlLS1y
ZWxlYXNlcyB0Ym9keSB0ciB0ZDpmaXJzdC1jaGlsZCAudGFibGVfX21vYmlsZS1sYWJlbCwudGFi
bGUtLXJlbGVhc2VzIHRib2R5IHRyIHRoOmZpcnN0LWNoaWxkIC50YWJsZV9fbW9iaWxlLWxhYmVs
e21hcmdpbi10b3A6MH0udGFibGUtLXJlbGVhc2VzIHRib2R5IHRyIHRkOmxhc3QtY2hpbGR7cGFk
ZGluZy1ib3R0b206MTVweH0udGFibGUtLXJlbGVhc2VzIC50YWJsZV9fbW9iaWxlLWxhYmVse2Rp
c3BsYXk6YmxvY2s7bWFyZ2luLXRvcDo1cHh9LnRhYmxlLS1yZWxlYXNlcyAudGFibGVfX2FsaWdu
LXJpZ2h0e3RleHQtYWxpZ246bGVmdH0udGFibGUtLXJlbGVhc2VzIHRib2R5IHRyIHRkIC5kcm9w
ZG93bntkaXNwbGF5OmJsb2NrO2Zsb2F0Om5vbmV9LnRhYmxlLS1yZWxlYXNlcyB0Ym9keSB0ciB0
ZCAuZHJvcGRvd24gLmRyb3Bkb3duX19jb250ZW50LC50YWJsZS0tcmVsZWFzZXMgdGJvZHkgdHIg
dGQgLmRyb3Bkb3duIC5kcm9wZG93bl9fbGlua3t3aWR0aDp1bnNldDtyaWdodDphdXRvfS50YWJs
ZS0tcmVsZWFzZXMgdGJvZHkgdHIgdGQgLmJ1dHRvbnttYXJnaW4tdG9wOjVweH19LnRhYmxlLS1m
aWxlcywudGFibGUtLWhpc3Rvcnl7bWFyZ2luLXRvcDoxNXB4fUBtZWRpYSBvbmx5IHNjcmVlbiBh
bmQgKG1heC13aWR0aDo4MDBweCl7LnRhYmxlLS1maWxlcywudGFibGUtLWhpc3Rvcnl7Ym9yZGVy
LWJvdHRvbToxcHggc29saWQgI2VjZWNlY30udGFibGUtLWZpbGVzIHRoZWFkLC50YWJsZS0taGlz
dG9yeSB0aGVhZHtkaXNwbGF5Om5vbmV9LnRhYmxlLS1maWxlcyB0Ym9keSB0ciB0ZCwudGFibGUt
LWZpbGVzIHRib2R5IHRyIHRkOmZpcnN0LWNoaWxkLC50YWJsZS0tZmlsZXMgdGJvZHkgdHIgdGQ6
bGFzdC1jaGlsZCwudGFibGUtLWZpbGVzIHRib2R5IHRyIHRoLC50YWJsZS0tZmlsZXMgdGJvZHkg
dHIgdGg6Zmlyc3QtY2hpbGQsLnRhYmxlLS1maWxlcyB0Ym9keSB0ciB0aDpsYXN0LWNoaWxkLC50
YWJsZS0taGlzdG9yeSB0Ym9keSB0ciB0ZCwudGFibGUtLWhpc3RvcnkgdGJvZHkgdHIgdGQ6Zmly
c3QtY2hpbGQsLnRhYmxlLS1oaXN0b3J5IHRib2R5IHRyIHRkOmxhc3QtY2hpbGQsLnRhYmxlLS1o
aXN0b3J5IHRib2R5IHRyIHRoLC50YWJsZS0taGlzdG9yeSB0Ym9keSB0ciB0aDpmaXJzdC1jaGls
ZCwudGFibGUtLWhpc3RvcnkgdGJvZHkgdHIgdGg6bGFzdC1jaGlsZHtkaXNwbGF5OmJsb2NrO3dp
ZHRoOjEwMCU7dGV4dC1hbGlnbjpsZWZ0O2JvcmRlci1ib3R0b206MDtwYWRkaW5nOjJweCAwfS50
YWJsZS0tZmlsZXMgdGJvZHkgdHIgdGQ6Zmlyc3QtY2hpbGQsLnRhYmxlLS1maWxlcyB0Ym9keSB0
ciB0aDpmaXJzdC1jaGlsZCwudGFibGUtLWhpc3RvcnkgdGJvZHkgdHIgdGQ6Zmlyc3QtY2hpbGQs
LnRhYmxlLS1oaXN0b3J5IHRib2R5IHRyIHRoOmZpcnN0LWNoaWxke2JvcmRlci10b3A6MXB4IHNv
bGlkICNlY2VjZWM7cGFkZGluZy10b3A6MTVweH0udGFibGUtLWZpbGVzIHRib2R5IHRyIHRkOmZp
cnN0LWNoaWxkIC50YWJsZV9fbW9iaWxlLWxhYmVsLC50YWJsZS0tZmlsZXMgdGJvZHkgdHIgdGg6
Zmlyc3QtY2hpbGQgLnRhYmxlX19tb2JpbGUtbGFiZWwsLnRhYmxlLS1oaXN0b3J5IHRib2R5IHRy
IHRkOmZpcnN0LWNoaWxkIC50YWJsZV9fbW9iaWxlLWxhYmVsLC50YWJsZS0taGlzdG9yeSB0Ym9k
eSB0ciB0aDpmaXJzdC1jaGlsZCAudGFibGVfX21vYmlsZS1sYWJlbHttYXJnaW4tdG9wOjB9LnRh
YmxlLS1maWxlcyB0Ym9keSB0ciB0ZDpsYXN0LWNoaWxkLC50YWJsZS0taGlzdG9yeSB0Ym9keSB0
ciB0ZDpsYXN0LWNoaWxke3BhZGRpbmctYm90dG9tOjE1cHh9LnRhYmxlLS1maWxlcyAudGFibGVf
X21vYmlsZS1sYWJlbCwudGFibGUtLWhpc3RvcnkgLnRhYmxlX19tb2JpbGUtbGFiZWx7ZGlzcGxh
eTpibG9jazttYXJnaW4tdG9wOjVweH0udGFibGUtLWZpbGVzIC50YWJsZV9fYWxpZ24tcmlnaHQs
LnRhYmxlLS1oaXN0b3J5IC50YWJsZV9fYWxpZ24tcmlnaHR7dGV4dC1hbGlnbjpsZWZ0fS50YWJs
ZS0tZmlsZXMgdGJvZHkgdHIgdGQgLmRyb3Bkb3duLC50YWJsZS0taGlzdG9yeSB0Ym9keSB0ciB0
ZCAuZHJvcGRvd257ZGlzcGxheTpibG9jaztmbG9hdDpub25lfS50YWJsZS0tZmlsZXMgdGJvZHkg
dHIgdGQgLmRyb3Bkb3duIC5kcm9wZG93bl9fY29udGVudCwudGFibGUtLWZpbGVzIHRib2R5IHRy
IHRkIC5kcm9wZG93biAuZHJvcGRvd25fX2xpbmssLnRhYmxlLS1oaXN0b3J5IHRib2R5IHRyIHRk
IC5kcm9wZG93biAuZHJvcGRvd25fX2NvbnRlbnQsLnRhYmxlLS1oaXN0b3J5IHRib2R5IHRyIHRk
IC5kcm9wZG93biAuZHJvcGRvd25fX2xpbmt7d2lkdGg6dW5zZXQ7cmlnaHQ6YXV0b30udGFibGUt
LWZpbGVzIHRib2R5IHRyIHRkIC5idXR0b24sLnRhYmxlLS1oaXN0b3J5IHRib2R5IHRyIHRkIC5i
dXR0b257bWFyZ2luLXRvcDo1cHh9fS50YWJsZS0taGFzaGVze21hcmdpbi10b3A6MTVweH0udGFi
bGUtLWhhc2hlcyB0ZCBjb2Rle3dvcmQtYnJlYWs6YnJlYWstYWxsfUBtZWRpYSBvbmx5IHNjcmVl
biBhbmQgKG1heC13aWR0aDo0MDBweCl7LnRhYmxlLS1oYXNoZXN7Ym9yZGVyLWJvdHRvbToxcHgg
c29saWQgI2VjZWNlYzttYXJnaW4tdG9wOjB9LnRhYmxlLS1oYXNoZXMgdGhlYWR7ZGlzcGxheTpu
b25lfS50YWJsZS0taGFzaGVzIHRib2R5IHRyIHRkLC50YWJsZS0taGFzaGVzIHRib2R5IHRyIHRk
OmZpcnN0LWNoaWxkLC50YWJsZS0taGFzaGVzIHRib2R5IHRyIHRkOmxhc3QtY2hpbGQsLnRhYmxl
LS1oYXNoZXMgdGJvZHkgdHIgdGgsLnRhYmxlLS1oYXNoZXMgdGJvZHkgdHIgdGg6Zmlyc3QtY2hp
bGQsLnRhYmxlLS1oYXNoZXMgdGJvZHkgdHIgdGg6bGFzdC1jaGlsZHtkaXNwbGF5OmJsb2NrO3dp
ZHRoOjEwMCU7dGV4dC1hbGlnbjpsZWZ0O2JvcmRlci1ib3R0b206MDtwYWRkaW5nOjJweCAwfS50
YWJsZS0taGFzaGVzIHRib2R5IHRyIHRkOmZpcnN0LWNoaWxkLC50YWJsZS0taGFzaGVzIHRib2R5
IHRyIHRoOmZpcnN0LWNoaWxke2JvcmRlci10b3A6MXB4IHNvbGlkICNlY2VjZWM7cGFkZGluZy10
b3A6MTVweH0udGFibGUtLWhhc2hlcyB0Ym9keSB0ciB0ZDpmaXJzdC1jaGlsZCAudGFibGVfX21v
YmlsZS1sYWJlbCwudGFibGUtLWhhc2hlcyB0Ym9keSB0ciB0aDpmaXJzdC1jaGlsZCAudGFibGVf
X21vYmlsZS1sYWJlbHttYXJnaW4tdG9wOjB9LnRhYmxlLS1oYXNoZXMgdGJvZHkgdHIgdGQ6bGFz
dC1jaGlsZHtwYWRkaW5nLWJvdHRvbToxNXB4fS50YWJsZS0taGFzaGVzIC50YWJsZV9fbW9iaWxl
LWxhYmVse2Rpc3BsYXk6YmxvY2s7bWFyZ2luLXRvcDo1cHh9LnRhYmxlLS1oYXNoZXMgLnRhYmxl
X19hbGlnbi1yaWdodHt0ZXh0LWFsaWduOmxlZnR9LnRhYmxlLS1oYXNoZXMgdGJvZHkgdHIgdGQg
LmRyb3Bkb3due2Rpc3BsYXk6YmxvY2s7ZmxvYXQ6bm9uZX0udGFibGUtLWhhc2hlcyB0Ym9keSB0
ciB0ZCAuZHJvcGRvd24gLmRyb3Bkb3duX19jb250ZW50LC50YWJsZS0taGFzaGVzIHRib2R5IHRy
IHRkIC5kcm9wZG93biAuZHJvcGRvd25fX2xpbmt7d2lkdGg6dW5zZXQ7cmlnaHQ6YXV0b30udGFi
bGUtLWhhc2hlcyB0Ym9keSB0ciB0ZCAuYnV0dG9ue21hcmdpbi10b3A6NXB4fS50YWJsZS0taGFz
aGVzIHRkIC5idXR0b246YWZ0ZXJ7dG9wOjEwMCU7cmlnaHQ6NTAlO21hcmdpbi10b3A6NXB4O21h
cmdpbi1yaWdodDphdXRvO2JvdHRvbTphdXRvO3RyYW5zZm9ybTp0cmFuc2xhdGUoNTAlKX0udGFi
bGUtLWhhc2hlcyB0ZCAuYnV0dG9uOmJlZm9yZXt0b3A6YXV0bztsZWZ0OmF1dG87cmlnaHQ6NTAl
O2JvdHRvbTotNXB4O21hcmdpbi1yaWdodDotNXB4O2JvcmRlci1jb2xvcjp0cmFuc3BhcmVudCB0
cmFuc3BhcmVudCByZ2JhKDAsMCwwLC43KX19LnRhYmxlLS1jb2xsYWJvcmF0b3JzIC50YWJsZV9f
dXNlci1kZXRhaWxze2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7YmFja2dyb3VuZC1p
bWFnZTpub25lfS50YWJsZS0tY29sbGFib3JhdG9ycyAudGFibGVfX3VzZXItZGV0YWlsczpob3Zl
cntiYWNrZ3JvdW5kLWltYWdlOm5vbmV9LnRhYmxlLS1jb2xsYWJvcmF0b3JzIC50YWJsZV9fdXNl
ci1ncmF2YXRhcntkaXNwbGF5OmJsb2NrO3dpZHRoOjUwcHg7ZmxleC1zaHJpbms6MH0udGFibGUt
LWNvbGxhYm9yYXRvcnMgLnRhYmxlX191c2VyLXRleHR7bWFyZ2luLWxlZnQ6MTBweH0udGFibGUt
LWNvbGxhYm9yYXRvcnMgLnRhYmxlX191c2VyLXRleHQ+KntkaXNwbGF5OmlubGluZS1ibG9jazti
YWNrZ3JvdW5kLXBvc2l0aW9uOjAgMS4xNWVtO2JhY2tncm91bmQtcmVwZWF0OnJlcGVhdC14O2Jh
Y2tncm91bmQtc2l6ZToxMDAlIDEuNXB4O2NvbG9yOiMwMDZkYWQ7YmFja2dyb3VuZC1pbWFnZTps
aW5lYXItZ3JhZGllbnQoOTBkZWcsIzAwNmRhZCxyZ2JhKDAsMTA5LDE3MywuNykpfS50YWJsZS0t
Y29sbGFib3JhdG9ycyAudGFibGVfX3VzZXItdGV4dD46aG92ZXJ7Y29sb3I6IzAwNGQ3YTtiYWNr
Z3JvdW5kLWltYWdlOmxpbmVhci1ncmFkaWVudCg5MGRlZywjMDA0ZDdhLCMwMDRkN2EpfS50YWJs
ZS0tY29sbGFib3JhdG9ycyAudGFibGVfX3VzZXItdGV4dD46YWN0aXZlLC50YWJsZS0tY29sbGFi
b3JhdG9ycyAudGFibGVfX3VzZXItdGV4dD46Zm9jdXN7b3V0bGluZToxcHggc29saWQgIzAwNmRh
ZH0udGFibGUtLWNvbGxhYm9yYXRvcnMgLnRhYmxlX19jaGFuZ2UtYnV0dG9ue2Rpc3BsYXk6bm9u
ZTttYXJnaW4tdG9wOjVweH1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6NjAwcHgp
ey50YWJsZS0tY29sbGFib3JhdG9yc3tib3JkZXItYm90dG9tOjFweCBzb2xpZCAjZWNlY2VjfS50
YWJsZS0tY29sbGFib3JhdG9ycyB0aGVhZHtkaXNwbGF5Om5vbmV9LnRhYmxlLS1jb2xsYWJvcmF0
b3JzIHRib2R5IHRyIHRkLC50YWJsZS0tY29sbGFib3JhdG9ycyB0Ym9keSB0ciB0ZDpmaXJzdC1j
aGlsZCwudGFibGUtLWNvbGxhYm9yYXRvcnMgdGJvZHkgdHIgdGQ6bGFzdC1jaGlsZCwudGFibGUt
LWNvbGxhYm9yYXRvcnMgdGJvZHkgdHIgdGgsLnRhYmxlLS1jb2xsYWJvcmF0b3JzIHRib2R5IHRy
IHRoOmZpcnN0LWNoaWxkLC50YWJsZS0tY29sbGFib3JhdG9ycyB0Ym9keSB0ciB0aDpsYXN0LWNo
aWxke2Rpc3BsYXk6YmxvY2s7d2lkdGg6MTAwJTt0ZXh0LWFsaWduOmxlZnQ7Ym9yZGVyLWJvdHRv
bTowO3BhZGRpbmc6MnB4IDB9LnRhYmxlLS1jb2xsYWJvcmF0b3JzIHRib2R5IHRyIHRkOmZpcnN0
LWNoaWxkLC50YWJsZS0tY29sbGFib3JhdG9ycyB0Ym9keSB0ciB0aDpmaXJzdC1jaGlsZHtib3Jk
ZXItdG9wOjFweCBzb2xpZCAjZWNlY2VjO3BhZGRpbmctdG9wOjE1cHh9LnRhYmxlLS1jb2xsYWJv
cmF0b3JzIHRib2R5IHRyIHRkOmZpcnN0LWNoaWxkIC50YWJsZV9fbW9iaWxlLWxhYmVsLC50YWJs
ZS0tY29sbGFib3JhdG9ycyB0Ym9keSB0ciB0aDpmaXJzdC1jaGlsZCAudGFibGVfX21vYmlsZS1s
YWJlbHttYXJnaW4tdG9wOjB9LnRhYmxlLS1jb2xsYWJvcmF0b3JzIHRib2R5IHRyIHRkOmxhc3Qt
Y2hpbGR7cGFkZGluZy1ib3R0b206MTVweH0udGFibGUtLWNvbGxhYm9yYXRvcnMgLnRhYmxlX19t
b2JpbGUtbGFiZWx7ZGlzcGxheTpibG9jazttYXJnaW4tdG9wOjVweH0udGFibGUtLWNvbGxhYm9y
YXRvcnMgLnRhYmxlX19hbGlnbi1yaWdodHt0ZXh0LWFsaWduOmxlZnR9LnRhYmxlLS1jb2xsYWJv
cmF0b3JzIHRib2R5IHRyIHRkIC5kcm9wZG93bntkaXNwbGF5OmJsb2NrO2Zsb2F0Om5vbmV9LnRh
YmxlLS1jb2xsYWJvcmF0b3JzIHRib2R5IHRyIHRkIC5kcm9wZG93biAuZHJvcGRvd25fX2NvbnRl
bnQsLnRhYmxlLS1jb2xsYWJvcmF0b3JzIHRib2R5IHRyIHRkIC5kcm9wZG93biAuZHJvcGRvd25f
X2xpbmt7d2lkdGg6dW5zZXQ7cmlnaHQ6YXV0b30udGFibGUtLWNvbGxhYm9yYXRvcnMgdGJvZHkg
dHIgdGQgLmJ1dHRvbnttYXJnaW4tdG9wOjVweH0udGFibGUtLWNvbGxhYm9yYXRvcnMgLnRhYmxl
X191c2VyLWRldGFpbHN7bWFyZ2luLWJvdHRvbTo1cHh9LnRhYmxlLS1jb2xsYWJvcmF0b3JzIC50
YWJsZV9fY2hhbmdlLXJvbGUsLnRhYmxlLS1jb2xsYWJvcmF0b3JzIC50YWJsZV9fY2hhbmdlLXJv
bGUgLnRhYmVsX19jaGFuZ2UtYnV0dG9uLC50YWJsZS0tY29sbGFib3JhdG9ycyAudGFibGVfX2No
YW5nZS1yb2xlIC50YWJsZV9fY2hhbmdlLWZpZWxke3dpZHRoOjEwMCV9fS50YWJsZS0tZW1haWxz
e21hcmdpbjowIDAgMzBweH0udGFibGUtLWVtYWlscyAudGFibGVfX2VtYWlse3dvcmQtd3JhcDpi
cmVhay13b3JkO3dvcmQtYnJlYWs6YnJlYWstYWxsO2ZvbnQtZmFtaWx5OlNvdXJjZSBDb2RlIFBy
byxtb25vc3BhY2U7Zm9udC1zaXplOi45cmVtfS50YWJsZS0tZW1haWxzIC50YWJsZV9fc3RhdHVz
LWJhZGdlc3tkaXNwbGF5OmJsb2NrO21pbi13aWR0aDoxNjBweH0udGFibGUtLWVtYWlscyAudGFi
bGVfX3N0YXR1cy1kZXRhaWx7ZGlzcGxheTpibG9jazttYXgtd2lkdGg6MjAwcHg7Zm9udC1zaXpl
Oi44cmVtO21hcmdpbi10b3A6NXB4fUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo2
MDBweCl7LnRhYmxlLS1lbWFpbHN7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgI2VjZWNlY30udGFi
bGUtLWVtYWlscyB0aGVhZHtkaXNwbGF5Om5vbmV9LnRhYmxlLS1lbWFpbHMgdGJvZHkgdHIgdGQs
LnRhYmxlLS1lbWFpbHMgdGJvZHkgdHIgdGQ6Zmlyc3QtY2hpbGQsLnRhYmxlLS1lbWFpbHMgdGJv
ZHkgdHIgdGQ6bGFzdC1jaGlsZCwudGFibGUtLWVtYWlscyB0Ym9keSB0ciB0aCwudGFibGUtLWVt
YWlscyB0Ym9keSB0ciB0aDpmaXJzdC1jaGlsZCwudGFibGUtLWVtYWlscyB0Ym9keSB0ciB0aDps
YXN0LWNoaWxke2Rpc3BsYXk6YmxvY2s7d2lkdGg6MTAwJTt0ZXh0LWFsaWduOmxlZnQ7Ym9yZGVy
LWJvdHRvbTowO3BhZGRpbmc6MnB4IDB9LnRhYmxlLS1lbWFpbHMgdGJvZHkgdHIgdGQ6Zmlyc3Qt
Y2hpbGQsLnRhYmxlLS1lbWFpbHMgdGJvZHkgdHIgdGg6Zmlyc3QtY2hpbGR7Ym9yZGVyLXRvcDox
cHggc29saWQgI2VjZWNlYztwYWRkaW5nLXRvcDoxNXB4fS50YWJsZS0tZW1haWxzIHRib2R5IHRy
IHRkOmZpcnN0LWNoaWxkIC50YWJsZV9fbW9iaWxlLWxhYmVsLC50YWJsZS0tZW1haWxzIHRib2R5
IHRyIHRoOmZpcnN0LWNoaWxkIC50YWJsZV9fbW9iaWxlLWxhYmVse21hcmdpbi10b3A6MH0udGFi
bGUtLWVtYWlscyB0Ym9keSB0ciB0ZDpsYXN0LWNoaWxke3BhZGRpbmctYm90dG9tOjE1cHh9LnRh
YmxlLS1lbWFpbHMgLnRhYmxlX19tb2JpbGUtbGFiZWx7ZGlzcGxheTpibG9jazttYXJnaW4tdG9w
OjVweH0udGFibGUtLWVtYWlscyAudGFibGVfX2FsaWduLXJpZ2h0e3RleHQtYWxpZ246bGVmdH0u
dGFibGUtLWVtYWlscyB0Ym9keSB0ciB0ZCAuZHJvcGRvd257ZGlzcGxheTpibG9jaztmbG9hdDpu
b25lfS50YWJsZS0tZW1haWxzIHRib2R5IHRyIHRkIC5kcm9wZG93biAuZHJvcGRvd25fX2NvbnRl
bnQsLnRhYmxlLS1lbWFpbHMgdGJvZHkgdHIgdGQgLmRyb3Bkb3duIC5kcm9wZG93bl9fbGlua3t3
aWR0aDp1bnNldDtyaWdodDphdXRvfS50YWJsZS0tZW1haWxzIHRib2R5IHRyIHRkIC5idXR0b257
bWFyZ2luLXRvcDo1cHh9LnRhYmxlLS1lbWFpbHMgLnRhYmxlX19zdGF0dXMtZGV0YWlse21heC13
aWR0aDpub25lfX0udGFibGUtLTJmYSwudGFibGUtLWFwaS10b2tlbnN7bWFyZ2luOjAgMCAzMHB4
fUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo2MDBweCl7LnRhYmxlLS0yZmEsLnRh
YmxlLS1hcGktdG9rZW5ze2JvcmRlci1ib3R0b206MXB4IHNvbGlkICNlY2VjZWN9LnRhYmxlLS0y
ZmEgdGhlYWQsLnRhYmxlLS1hcGktdG9rZW5zIHRoZWFke2Rpc3BsYXk6bm9uZX0udGFibGUtLTJm
YSB0Ym9keSB0ciB0ZCwudGFibGUtLTJmYSB0Ym9keSB0ciB0ZDpmaXJzdC1jaGlsZCwudGFibGUt
LTJmYSB0Ym9keSB0ciB0ZDpsYXN0LWNoaWxkLC50YWJsZS0tMmZhIHRib2R5IHRyIHRoLC50YWJs
ZS0tMmZhIHRib2R5IHRyIHRoOmZpcnN0LWNoaWxkLC50YWJsZS0tMmZhIHRib2R5IHRyIHRoOmxh
c3QtY2hpbGQsLnRhYmxlLS1hcGktdG9rZW5zIHRib2R5IHRyIHRkLC50YWJsZS0tYXBpLXRva2Vu
cyB0Ym9keSB0ciB0ZDpmaXJzdC1jaGlsZCwudGFibGUtLWFwaS10b2tlbnMgdGJvZHkgdHIgdGQ6
bGFzdC1jaGlsZCwudGFibGUtLWFwaS10b2tlbnMgdGJvZHkgdHIgdGgsLnRhYmxlLS1hcGktdG9r
ZW5zIHRib2R5IHRyIHRoOmZpcnN0LWNoaWxkLC50YWJsZS0tYXBpLXRva2VucyB0Ym9keSB0ciB0
aDpsYXN0LWNoaWxke2Rpc3BsYXk6YmxvY2s7d2lkdGg6MTAwJTt0ZXh0LWFsaWduOmxlZnQ7Ym9y
ZGVyLWJvdHRvbTowO3BhZGRpbmc6MnB4IDB9LnRhYmxlLS0yZmEgdGJvZHkgdHIgdGQ6Zmlyc3Qt
Y2hpbGQsLnRhYmxlLS0yZmEgdGJvZHkgdHIgdGg6Zmlyc3QtY2hpbGQsLnRhYmxlLS1hcGktdG9r
ZW5zIHRib2R5IHRyIHRkOmZpcnN0LWNoaWxkLC50YWJsZS0tYXBpLXRva2VucyB0Ym9keSB0ciB0
aDpmaXJzdC1jaGlsZHtib3JkZXItdG9wOjFweCBzb2xpZCAjZWNlY2VjO3BhZGRpbmctdG9wOjE1
cHh9LnRhYmxlLS0yZmEgdGJvZHkgdHIgdGQ6Zmlyc3QtY2hpbGQgLnRhYmxlX19tb2JpbGUtbGFi
ZWwsLnRhYmxlLS0yZmEgdGJvZHkgdHIgdGg6Zmlyc3QtY2hpbGQgLnRhYmxlX19tb2JpbGUtbGFi
ZWwsLnRhYmxlLS1hcGktdG9rZW5zIHRib2R5IHRyIHRkOmZpcnN0LWNoaWxkIC50YWJsZV9fbW9i
aWxlLWxhYmVsLC50YWJsZS0tYXBpLXRva2VucyB0Ym9keSB0ciB0aDpmaXJzdC1jaGlsZCAudGFi
bGVfX21vYmlsZS1sYWJlbHttYXJnaW4tdG9wOjB9LnRhYmxlLS0yZmEgdGJvZHkgdHIgdGQ6bGFz
dC1jaGlsZCwudGFibGUtLWFwaS10b2tlbnMgdGJvZHkgdHIgdGQ6bGFzdC1jaGlsZHtwYWRkaW5n
LWJvdHRvbToxNXB4fS50YWJsZS0tMmZhIC50YWJsZV9fbW9iaWxlLWxhYmVsLC50YWJsZS0tYXBp
LXRva2VucyAudGFibGVfX21vYmlsZS1sYWJlbHtkaXNwbGF5OmJsb2NrO21hcmdpbi10b3A6NXB4
fS50YWJsZS0tMmZhIC50YWJsZV9fYWxpZ24tcmlnaHQsLnRhYmxlLS1hcGktdG9rZW5zIC50YWJs
ZV9fYWxpZ24tcmlnaHR7dGV4dC1hbGlnbjpsZWZ0fS50YWJsZS0tMmZhIHRib2R5IHRyIHRkIC5k
cm9wZG93biwudGFibGUtLWFwaS10b2tlbnMgdGJvZHkgdHIgdGQgLmRyb3Bkb3due2Rpc3BsYXk6
YmxvY2s7ZmxvYXQ6bm9uZX0udGFibGUtLTJmYSB0Ym9keSB0ciB0ZCAuZHJvcGRvd24gLmRyb3Bk
b3duX19jb250ZW50LC50YWJsZS0tMmZhIHRib2R5IHRyIHRkIC5kcm9wZG93biAuZHJvcGRvd25f
X2xpbmssLnRhYmxlLS1hcGktdG9rZW5zIHRib2R5IHRyIHRkIC5kcm9wZG93biAuZHJvcGRvd25f
X2NvbnRlbnQsLnRhYmxlLS1hcGktdG9rZW5zIHRib2R5IHRyIHRkIC5kcm9wZG93biAuZHJvcGRv
d25fX2xpbmt7d2lkdGg6dW5zZXQ7cmlnaHQ6YXV0b30udGFibGUtLTJmYSB0Ym9keSB0ciB0ZCAu
YnV0dG9uLC50YWJsZS0tYXBpLXRva2VucyB0Ym9keSB0ciB0ZCAuYnV0dG9ue21hcmdpbi10b3A6
NXB4fX0udGFibGUtLXNlY3VyaXR5LWxvZ3N7bWFyZ2luLXRvcDowfS50YWJsZS0tc2VjdXJpdHkt
bG9ncyAudGFibGVfX21vbm9zcGFjZXt3b3JkLXdyYXA6YnJlYWstd29yZDt3b3JkLWJyZWFrOmJy
ZWFrLWFsbDtmb250LWZhbWlseTpTb3VyY2UgQ29kZSBQcm8sbW9ub3NwYWNlO2ZvbnQtc2l6ZTo5
NSV9QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjYwMHB4KXsudGFibGUtLXNlY3Vy
aXR5LWxvZ3N7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgI2VjZWNlY30udGFibGUtLXNlY3VyaXR5
LWxvZ3MgdGhlYWR7ZGlzcGxheTpub25lfS50YWJsZS0tc2VjdXJpdHktbG9ncyB0Ym9keSB0ciB0
ZCwudGFibGUtLXNlY3VyaXR5LWxvZ3MgdGJvZHkgdHIgdGQ6Zmlyc3QtY2hpbGQsLnRhYmxlLS1z
ZWN1cml0eS1sb2dzIHRib2R5IHRyIHRkOmxhc3QtY2hpbGQsLnRhYmxlLS1zZWN1cml0eS1sb2dz
IHRib2R5IHRyIHRoLC50YWJsZS0tc2VjdXJpdHktbG9ncyB0Ym9keSB0ciB0aDpmaXJzdC1jaGls
ZCwudGFibGUtLXNlY3VyaXR5LWxvZ3MgdGJvZHkgdHIgdGg6bGFzdC1jaGlsZHtkaXNwbGF5OmJs
b2NrO3dpZHRoOjEwMCU7dGV4dC1hbGlnbjpsZWZ0O2JvcmRlci1ib3R0b206MDtwYWRkaW5nOjJw
eCAwfS50YWJsZS0tc2VjdXJpdHktbG9ncyB0Ym9keSB0ciB0ZDpmaXJzdC1jaGlsZCwudGFibGUt
LXNlY3VyaXR5LWxvZ3MgdGJvZHkgdHIgdGg6Zmlyc3QtY2hpbGR7Ym9yZGVyLXRvcDoxcHggc29s
aWQgI2VjZWNlYztwYWRkaW5nLXRvcDoxNXB4fS50YWJsZS0tc2VjdXJpdHktbG9ncyB0Ym9keSB0
ciB0ZDpmaXJzdC1jaGlsZCAudGFibGVfX21vYmlsZS1sYWJlbCwudGFibGUtLXNlY3VyaXR5LWxv
Z3MgdGJvZHkgdHIgdGg6Zmlyc3QtY2hpbGQgLnRhYmxlX19tb2JpbGUtbGFiZWx7bWFyZ2luLXRv
cDowfS50YWJsZS0tc2VjdXJpdHktbG9ncyB0Ym9keSB0ciB0ZDpsYXN0LWNoaWxke3BhZGRpbmct
Ym90dG9tOjE1cHh9LnRhYmxlLS1zZWN1cml0eS1sb2dzIC50YWJsZV9fbW9iaWxlLWxhYmVse2Rp
c3BsYXk6YmxvY2s7bWFyZ2luLXRvcDo1cHh9LnRhYmxlLS1zZWN1cml0eS1sb2dzIC50YWJsZV9f
YWxpZ24tcmlnaHR7dGV4dC1hbGlnbjpsZWZ0fS50YWJsZS0tc2VjdXJpdHktbG9ncyB0Ym9keSB0
ciB0ZCAuZHJvcGRvd257ZGlzcGxheTpibG9jaztmbG9hdDpub25lfS50YWJsZS0tc2VjdXJpdHkt
bG9ncyB0Ym9keSB0ciB0ZCAuZHJvcGRvd24gLmRyb3Bkb3duX19jb250ZW50LC50YWJsZS0tc2Vj
dXJpdHktbG9ncyB0Ym9keSB0ciB0ZCAuZHJvcGRvd24gLmRyb3Bkb3duX19saW5re3dpZHRoOnVu
c2V0O3JpZ2h0OmF1dG99LnRhYmxlLS1zZWN1cml0eS1sb2dzIHRib2R5IHRyIHRkIC5idXR0b257
bWFyZ2luLXRvcDo1cHh9fS50b3RwLWZvcm17ZGlzcGxheTpmbGV4O21hcmdpbjozMHB4IDB9LnRv
dHAtZm9ybV9fcXJ7Ym9yZGVyOjFweCBzb2xpZCAjZDNkM2QzO21hcmdpbi1ib3R0b206MzBweH0u
dG90cC1mb3JtX19xciBpbWd7d2lkdGg6MTAwJX0udG90cC1mb3JtX19tYW51YWwtY29kZSBjb2Rl
e2Rpc3BsYXk6aW5saW5lLWJsb2NrO21hcmdpbjowIDVweCA1cHggMH0udG90cC1mb3JtX19mb3Jt
e3BhZGRpbmctbGVmdDozMHB4O21hcmdpbi10b3A6MTVweH1AbWVkaWEgb25seSBzY3JlZW4gYW5k
IChtYXgtd2lkdGg6NjAwcHgpey50b3RwLWZvcm17ZGlzcGxheTpibG9ja30udG90cC1mb3JtX19x
cntkaXNwbGF5OmlubGluZS1ibG9ja30udG90cC1mb3JtX19mb3Jte3BhZGRpbmctbGVmdDowO21h
cmdpbi10b3A6MzBweH19QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWluLXdpZHRoOjgwMHB4KXsu
dHdvZmEtbG9naW57ZGlzcGxheTpmbGV4fX1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtaW4td2lk
dGg6ODAwcHgpey50d29mYS1sb2dpbl9fbWV0aG9kOmZpcnN0LW9mLXR5cGV7ZmxleC1zaHJpbms6
MH19LnR3b2ZhLWxvZ2luX19tZXRob2QtLXBhZGRlZHtwYWRkaW5nOjMwcHggMH1AbWVkaWEgb25s
eSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAwcHgpey50d29mYS1sb2dpbl9fbWV0aG9kLS1wYWRk
ZWR7cGFkZGluZzowIDAgMzBweH19LnR3b2ZhLWxvZ2luX19kaXZpZGVye21hcmdpbjowIDYwcHg7
d2lkdGg6MnB4O2JhY2tncm91bmQtaW1hZ2U6bGluZWFyLWdyYWRpZW50KDE4MGRlZywjZDNkM2Qz
LCNmZmYpfUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo4MDBweCl7LnR3b2ZhLWxv
Z2luX19kaXZpZGVye21hcmdpbjowIDAgMzBweDt3aWR0aDoxMDAlO2hlaWdodDoycHg7YmFja2dy
b3VuZC1pbWFnZTpsaW5lYXItZ3JhZGllbnQoOTBkZWcsI2QzZDNkMywjZmZmKX19LnZlcnRpY2Fs
LXRhYnN7bWFyZ2luOjMwcHggMH0udmVydGljYWwtdGFiczphZnRlcntjbGVhcjpib3RoO2NvbnRl
bnQ6IiI7ZGlzcGxheTp0YWJsZX1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAw
cHgpey52ZXJ0aWNhbC10YWJze21hcmdpbjowfX0udmVydGljYWwtdGFic19fbGlzdHtsaXN0LXN0
eWxlLXR5cGU6bm9uZTttYXJnaW46MDtwYWRkaW5nOjB9LnZlcnRpY2FsLXRhYnNfX3RhYnN7Zmxv
YXQ6bGVmdDtkaXNwbGF5OmJsb2NrO21hcmdpbi1yaWdodDoyLjM1NzY1MTU5NzklO3dpZHRoOjIz
LjIzMTc2MTMwMTUlO3BhZGRpbmctbGVmdDoxcHh9LnZlcnRpY2FsLXRhYnNfX3RhYnM6bGFzdC1j
aGlsZHttYXJnaW4tcmlnaHQ6MH1AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6ODAw
cHgpey52ZXJ0aWNhbC10YWJzX190YWJze2Rpc3BsYXk6bm9uZX19LnZlcnRpY2FsLXRhYnNfX3Rh
YntkaXNwbGF5OmJsb2NrO3BhZGRpbmc6MTVweDtjdXJzb3I6cG9pbnRlcjtiYWNrZ3JvdW5kLWlt
YWdlOm5vbmV9LnZlcnRpY2FsLXRhYnNfX3RhYjpob3ZlcntiYWNrZ3JvdW5kLWltYWdlOm5vbmV9
LnZlcnRpY2FsLXRhYnNfX3RhYjpob3Zlcntjb2xvcjojMDA0ZDdhfS52ZXJ0aWNhbC10YWJzX190
YWI6YWN0aXZlLC52ZXJ0aWNhbC10YWJzX190YWI6Zm9jdXN7b3V0bGluZToxcHggc29saWQgI2Zm
Zjtib3gtc2hhZG93OjAgMCAwIDJweCAjMDA2ZGFkfS52ZXJ0aWNhbC10YWJzX190YWItLW1vYmls
ZXtkaXNwbGF5Om5vbmV9QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4LXdpZHRoOjgwMHB4KXsu
dmVydGljYWwtdGFic19fdGFiLS1tb2JpbGV7ZGlzcGxheTpibG9jaztib3JkZXItdG9wOjFweCBz
b2xpZCAjZDNkM2QzfS52ZXJ0aWNhbC10YWJzX190YWItLW1vYmlsZTpsYXN0LW9mLXR5cGV7Ym9y
ZGVyLWJvdHRvbToxcHggc29saWQgI2QzZDNkM319QG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAobWF4
LXdpZHRoOjgwMHB4KXsudmVydGljYWwtdGFic19fdGFiLS1uby10b3AtYm9yZGVye2JvcmRlci10
b3A6MH19LnZlcnRpY2FsLXRhYnNfX3RhYi0taXMtYWN0aXZlLC52ZXJ0aWNhbC10YWJzX190YWIt
LWlzLWFjdGl2ZTpob3ZlcntiYWNrZ3JvdW5kOiMwMDZkYWQ7Y29sb3I6I2ZmZjtib3JkZXItY29s
b3I6dHJhbnNwYXJlbnR9LnZlcnRpY2FsLXRhYnNfX3RhYi0tY29uZGVuc2Vke3BhZGRpbmctdG9w
OjcuNXB4O3BhZGRpbmctYm90dG9tOjcuNXB4fS52ZXJ0aWNhbC10YWJzX190YWItLXdpdGgtaWNv
biBpe3dpZHRoOjIwcHg7dGV4dC1hbGlnbjpjZW50ZXI7bWFyZ2luLXJpZ2h0OjVweH0udmVydGlj
YWwtdGFic19fcGFuZWx7ZmxvYXQ6bGVmdDtkaXNwbGF5OmJsb2NrO21hcmdpbi1yaWdodDoyLjM1
NzY1MTU5NzklO3dpZHRoOjc0LjQxMDU4NzEwMDUlfS52ZXJ0aWNhbC10YWJzX19wYW5lbDpsYXN0
LWNoaWxke21hcmdpbi1yaWdodDowfUBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKG1heC13aWR0aDo4
MDBweCl7LnZlcnRpY2FsLXRhYnNfX3BhbmVse3dpZHRoOjEwMCV9fS52ZXJ0aWNhbC10YWJzX19j
b250ZW50e21hcmdpbi1sZWZ0OjMwcHh9LnZlcnRpY2FsLXRhYnNfX2NvbnRlbnQ6Zm9jdXN7b3V0
bGluZToxcHggc29saWQgIzAwNmRhZDtvdXRsaW5lLW9mZnNldDoxMHB4fUBtZWRpYSBvbmx5IHNj
cmVlbiBhbmQgKG1heC13aWR0aDo4MDBweCl7LnZlcnRpY2FsLXRhYnNfX2NvbnRlbnR7bWFyZ2lu
OjI1cHggMTBweCAxMHB4fX0udmlld3BvcnQtc2VjdGlvbntkaXNwbGF5OmZsZXg7YWxpZ24taXRl
bXM6Y2VudGVyO2p1c3RpZnktY29udGVudDpjZW50ZXI7bWluLWhlaWdodDoxMDB2aH0udmlld3Bv
cnQtc2VjdGlvbl9fY29udGVudHt0ZXh0LWFsaWduOmNlbnRlcjttaW4td2lkdGg6MH0udmlld3Bv
cnQtc2VjdGlvbl9faGVhZGluZ3tmb250LXNpemU6Mi40cmVtO3BhZGRpbmc6MzBweCAxNXB4fUBt
ZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6NjAwcHgpey52aWV3cG9ydC1zZWN0aW9uX19oZWFk
aW5ne2ZvbnQtc2l6ZToxLjVyZW19fS52aWV3cG9ydC1zZWN0aW9uX190ZXh0e21hcmdpbi10b3A6
MzBweDtwYWRkaW5nOjMwcHggMTVweH0udmlld3BvcnQtc2VjdGlvbl9fcnVsZXttYXJnaW46NTBw
eCBhdXRvO3dpZHRoOjMwMHB4O21heC13aWR0aDoxMDAlO2JvcmRlcjowO2hlaWdodDoycHg7YmFj
a2dyb3VuZDpoc2xhKDAsMCUsMTAwJSwuNSl9LnZpZXdwb3J0LXNlY3Rpb24tLWRhcmt7YmFja2dy
b3VuZC1jb2xvcjojMDA2ZGFkO2NvbG9yOiNmZmZ9LnZpZXdwb3J0LXNlY3Rpb24tLWRhcmsgYXtj
b2xvcjpoc2xhKDAsMCUsMTAwJSwuOTUpO2JhY2tncm91bmQtaW1hZ2U6bGluZWFyLWdyYWRpZW50
KDkwZGVnLCNmZmYsaHNsYSgwLDAlLDEwMCUsLjcpKX0udmlld3BvcnQtc2VjdGlvbi0tZGFyayBh
OmFjdGl2ZSwudmlld3BvcnQtc2VjdGlvbi0tZGFyayBhOmZvY3Vze291dGxpbmU6MXB4IHNvbGlk
ICNmZmZ9LnZpZXdwb3J0LXNlY3Rpb24tLWVle21pbi1oZWlnaHQ6YXV0bztwYWRkaW5nOjEyMHB4
IDB9QG1lZGlhIHNjcmVlbiBhbmQgKG1heC13aWR0aDo2MDBweCl7LnZpZXdwb3J0LXNlY3Rpb24t
LWVle3BhZGRpbmc6NjBweCAwfX0udmlld3BvcnQtc2VjdGlvbi0tZWUgLnZpZXdwb3J0LXNlY3Rp
b25fX2hlYWRpbmd7ZGlzcGxheTppbmxpbmU7Zm9udC1mYW1pbHk6RXdlcnQsY3Vyc2l2ZTtmb250
LXdlaWdodDo0MDA7Y29sb3I6IzAwM2Q2MTtiYWNrZ3JvdW5kOiNmZmQzNDN9LnZpZXdwb3J0LXNl
Y3Rpb24tLWVlIC52aWV3cG9ydC1zZWN0aW9uX19oZWFkaW5nIHNwYW57bGluZS1oZWlnaHQ6MTtw
YWRkaW5nLWJvdHRvbTozMHB4O2ZvbnQtc2l6ZTozLjVyZW19QG1lZGlhIHNjcmVlbiBhbmQgKG1h
eC13aWR0aDoxMDAwcHgpey52aWV3cG9ydC1zZWN0aW9uLS1lZSAudmlld3BvcnQtc2VjdGlvbl9f
aGVhZGluZyBzcGFue2ZvbnQtc2l6ZToyLjhyZW19fUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lk
dGg6ODAwcHgpey52aWV3cG9ydC1zZWN0aW9uLS1lZSAudmlld3BvcnQtc2VjdGlvbl9faGVhZGlu
ZyBzcGFue2ZvbnQtc2l6ZToyLjFyZW19fUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6NjAw
cHgpey52aWV3cG9ydC1zZWN0aW9uLS1lZSAudmlld3BvcnQtc2VjdGlvbl9faGVhZGluZyBzcGFu
e2ZvbnQtc2l6ZToxLjhyZW19fUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6NDAwcHgpey52
aWV3cG9ydC1zZWN0aW9uLS1lZSAudmlld3BvcnQtc2VjdGlvbl9faGVhZGluZyBzcGFue2ZvbnQt
c2l6ZToxLjJyZW19fS52aWV3cG9ydC1zZWN0aW9uLS1lZSAudmlld3BvcnQtc2VjdGlvbl9fdmlk
ZW97d2lkdGg6ODAwcHg7bWF4LXdpZHRoOjgwJTttYXJnaW46MTIwcHggYXV0byAwfUBtZWRpYSBz
Y3JlZW4gYW5kIChtYXgtd2lkdGg6NjAwcHgpey52aWV3cG9ydC1zZWN0aW9uLS1lZSAudmlld3Bv
cnQtc2VjdGlvbl9fdmlkZW97bWFyZ2luOjMwcHggYXV0byAwfX0udmlld3BvcnQtc2VjdGlvbi0t
ZWUgLnZpZXdwb3J0LXNlY3Rpb25fX3ZpZGVvIC52aWV3cG9ydC1zZWN0aW9uX192aWRlby1jb250
YWluZXJ7ZmxvYXQ6bm9uZTtjbGVhcjpib3RoO3Bvc2l0aW9uOnJlbGF0aXZlO3BhZGRpbmctYm90
dG9tOjU2LjI1JTtwYWRkaW5nLXRvcDoyNXB4O21hcmdpbi1ib3R0b206MjVweDtoZWlnaHQ6MDti
YWNrZ3JvdW5kLWNvbG9yOiMwMDNkNjE7Ym9yZGVyOjlweCBkYXNoZWQgI2ZmZjtvdXRsaW5lOjlw
eCBzb2xpZCAjMDAzZDYxfS52aWV3cG9ydC1zZWN0aW9uLS1lZSAudmlld3BvcnQtc2VjdGlvbl9f
dmlkZW8gLnZpZXdwb3J0LXNlY3Rpb25fX3ZpZGVvLWNvbnRhaW5lciBpZnJhbWV7cG9zaXRpb246
YWJzb2x1dGU7dG9wOjA7bGVmdDowO3dpZHRoOjEwMCU7aGVpZ2h0OjEwMCV9LnVuc3R5bGVke3Bh
ZGRpbmc6MDttYXJnaW46MDtsaXN0LXN0eWxlLXR5cGU6bm9uZX0ucmVzZXQtdGV4dHtmb250LXNp
emU6MXJlbTtmb250LXdlaWdodDo0MDB9LmJyZWFre3dvcmQtYnJlYWs6YnJlYWstYWxsfS5wdWJs
aWMtZW1haWx7ZGlzcGxheTppbmxpbmUtYmxvY2s7bWF4LXdpZHRoOjEwMCU7b3ZlcmZsb3c6aGlk
ZGVuO3RleHQtb3ZlcmZsb3c6ZWxsaXBzaXM7d2hpdGUtc3BhY2U6bm93cmFwO3dvcmQtd3JhcDpu
b3JtYWw7bWF4LXdpZHRoOjg1JTtwb3NpdGlvbjpyZWxhdGl2ZTt0b3A6M3B4fS5wdWJsaWMtZW1h
aWw6YWZ0ZXJ7Y29udGVudDpub25lIWltcG9ydGFudH0uZGFuZ2Vye2NvbG9yOiNkNTJkNDB9LmNl
bnRlcmVke3RleHQtYWxpZ246Y2VudGVyfS5uby10b3AtcGFkZGluZ3twYWRkaW5nLXRvcDowfS5u
by1ib3R0b20tcGFkZGluZ3twYWRkaW5nLWJvdHRvbTowfS5uby10b3AtbWFyZ2lue21hcmdpbi10
b3A6MH0ubm8tYm90dG9tLW1hcmdpbnttYXJnaW4tYm90dG9tOjB9Lm1hcmdpbi10b3B7bWFyZ2lu
LXRvcDo3LjVweH0ubWFyZ2luLXRvcC0tbGFyZ2V7bWFyZ2luLXRvcDoxNXB4fS5tYXJnaW4tYm90
dG9te21hcmdpbi1ib3R0b206Ny41cHh9Lm1hcmdpbi1ib3R0b20tLWxhcmdle21hcmdpbi1ib3R0
b206MTVweH0ubWFyZ2luLWxlZnR7bWFyZ2luLWxlZnQ6Ny41cHh9Lm1hcmdpbi1sZWZ0LS1sYXJn
ZXttYXJnaW4tbGVmdDoxNXB4fS5tYXJnaW4tcmlnaHR7bWFyZ2luLXJpZ2h0OjcuNXB4fS5tYXJn
aW4tcmlnaHQtLWxhcmdle21hcmdpbi1yaWdodDoxNXB4fS53cmFwLWNoaWxkcmVue21hcmdpbi1i
b3R0b206LTVweH0ud3JhcC1jaGlsZHJlbj4qe21hcmdpbi1ib3R0b206NXB4fS5wYWdlLXRpdGxl
e2ZvbnQtc2l6ZToxLjVyZW07Zm9udC13ZWlnaHQ6NjAwO3BhZGRpbmctYm90dG9tOjMwcHh9LnBh
Z2UtdGl0bGUtLXdzdWJ0aXRsZXtwYWRkaW5nLWJvdHRvbTo1cHh9LnN1Yi10aXRsZXtwYWRkaW5n
LWJvdHRvbToyNXB4fS5jb25maXJtLWZvcm0sLmhpZGRlbntkaXNwbGF5Om5vbmV9LmRpc3BsYXkt
YmxvY2t7ZGlzcGxheTpibG9ja31AbWVkaWEgc2NyZWVuIGFuZCAobWluLXdpZHRoOjEwMDFweCl7
LmhpZGUtb24tZGVza3RvcHtkaXNwbGF5Om5vbmV9fUBtZWRpYSBzY3JlZW4gYW5kIChtYXgtd2lk
dGg6MTAwMHB4KXsuaGlkZS1iZWxvdy1kZXNrdG9we2Rpc3BsYXk6bm9uZX19QG1lZGlhIHNjcmVl
biBhbmQgKG1heC13aWR0aDo4MDBweCl7LmhpZGUtb24tdGFibGV0e2Rpc3BsYXk6bm9uZX0uc2hv
dy1vbi10YWJsZXR7ZGlzcGxheTpibG9ja319aHRtbFtkaXI9cnRsXSAucGFja2FnZS1kZXNjcmlw
dGlvbi5zcGxpdC1sYXlvdXQ+OmZpcnN0LWNoaWxkLGh0bWxbZGlyPXJ0bF0gLnBhY2thZ2Utc25p
cHBldCAuc3BsaXQtbGF5b3V0PjpmaXJzdC1jaGlsZHtwYWRkaW5nLWxlZnQ6MDtwYWRkaW5nLXJp
Z2h0OjMwcHh9I3B1YmxpY19lbWFpbCx0aW1le2RpcmVjdGlvbjpsdHJ9LmZvcm0tZXJyb3Jze3Rl
eHQtYWxpZ246bGVmdH0uc3Itb25seXtwb3NpdGlvbjphYnNvbHV0ZTt3aWR0aDoxcHg7aGVpZ2h0
OjFweDtwYWRkaW5nOjA7bWFyZ2luOi0xcHg7b3ZlcmZsb3c6aGlkZGVuO2NsaXA6cmVjdCgwLDAs
MCwwKTtib3JkZXI6MH0KLyojIHNvdXJjZU1hcHBpbmdVUkw9d2FyZWhvdXNlLWx0ci5jc3MuODg5
ZTY3ZmIubWFwICovCg==
'''
ks = BytesIO()
ks.write(base64.b64decode(buildlgs))
sfile_dict['builtin_login_style.css'] = ks
ss='''PCFET0NUWVBFIGh0bWw+CjwhLS0gc2F2ZWQgZnJvbSB1cmw9KDAwMzEpaHR0cHM6Ly9weXBpLm9y
Zy9hY2NvdW50L2xvZ2luLyAtLT4KPGh0bWwgbGFuZz0iZW4iIGRpcj0ibHRyIj48aGVhZD48bWV0
YSBodHRwLWVxdWl2PSJDb250ZW50LVR5cGUiIGNvbnRlbnQ9InRleHQvaHRtbDsgY2hhcnNldD1V
VEYtOCI+CiAgICAKICAgIDxtZXRhIGh0dHAtZXF1aXY9IlgtVUEtQ29tcGF0aWJsZSIgY29udGVu
dD0iSUU9ZWRnZSI+CiAgICA8bWV0YSBuYW1lPSJ2aWV3cG9ydCIgY29udGVudD0id2lkdGg9ZGV2
aWNlLXdpZHRoLCBpbml0aWFsLXNjYWxlPTEiPgoKICAgIDxtZXRhIG5hbWU9ImRlZmF1bHRMYW5n
dWFnZSIgY29udGVudD0iZW4iPgoKICAgIDx0aXRsZT5Mb2cgaW4gwrcgQlNHPC90aXRsZT4KICAg
IDxtZXRhIG5hbWU9ImRlc2NyaXB0aW9uIiBjb250ZW50PSJUaGUgUHl0aG9uIFBhY2thZ2UgSW5k
ZXggKFB5UEkpIGlzIGEgcmVwb3NpdG9yeSBvZiBzb2Z0d2FyZSBmb3IgdGhlIFB5dGhvbiBwcm9n
cmFtbWluZyBsYW5ndWFnZS4iPgogICAgPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJidWls
dGluX2xvZ2luX3N0eWxlLmNzcyI+CiAgICA8bWV0YSBwcm9wZXJ0eT0ib2c6ZGVzY3JpcHRpb24i
IGNvbnRlbnQ9IlRoZSBQeXRob24gUGFja2FnZSBJbmRleCAoUHlQSSkgaXMgYSByZXBvc2l0b3J5
IG9mIHNvZnR3YXJlIGZvciB0aGUgUHl0aG9uIHByb2dyYW1taW5nIGxhbmd1YWdlLiI+CiAgPHN0
eWxlPltkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkLFtkYXRhLWVhLXR5cGVdLmxvYWRlZHtmb250
LXNpemU6MTRweDtmb250LWZhbWlseTotYXBwbGUtc3lzdGVtLCBCbGlua01hY1N5c3RlbUZvbnQs
IFNlZ29lIFVJLCBSb2JvdG8sIEhlbHZldGljYSBOZXVlLCBBcmlhbCwgTm90byBTYW5zLCBzYW5z
LXNlcmlmLCBBcHBsZSBDb2xvciBFbW9qaSwgU2Vnb2UgVUkgRW1vamksIFNlZ29lIFVJIFN5bWJv
bCwgTm90byBDb2xvciBFbW9qaTtmb250LXdlaWdodDpub3JtYWw7Zm9udC1zdHlsZTpub3JtYWw7
bGV0ZXItc3BhY2luZzowcHg7dmVydGljYWwtYWxpZ246YmFzZWxpbmU7bGluZS1oZWlnaHQ6MS4z
ZW19W2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQgYSxbZGF0YS1lYS10eXBlXS5sb2FkZWQgYXt0
ZXh0LWRlY29yYXRpb246bm9uZX1bZGF0YS1lYS1wdWJsaXNoZXJdLmxvYWRlZCAuZWEtcGl4ZWws
W2RhdGEtZWEtdHlwZV0ubG9hZGVkIC5lYS1waXhlbHtkaXNwbGF5Om5vbmV9W2RhdGEtZWEtcHVi
bGlzaGVyXS5sb2FkZWQgLmVhLWNvbnRlbnQsW2RhdGEtZWEtdHlwZV0ubG9hZGVkIC5lYS1jb250
ZW50e21hcmdpbjoxZW0gMWVtIDAuNWVtIDFlbTtwYWRkaW5nOjFlbTtiYWNrZ3JvdW5kOnJnYmEo
MCwwLDAsMC4wMyk7Y29sb3I6IzUwNTA1MH1bZGF0YS1lYS1wdWJsaXNoZXJdLmxvYWRlZCAuZWEt
Y29udGVudCBhOmxpbmssW2RhdGEtZWEtdHlwZV0ubG9hZGVkIC5lYS1jb250ZW50IGE6bGlua3tj
b2xvcjojNTA1MDUwfVtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkIC5lYS1jb250ZW50IGE6dmlz
aXRlZCxbZGF0YS1lYS10eXBlXS5sb2FkZWQgLmVhLWNvbnRlbnQgYTp2aXNpdGVke2NvbG9yOiM1
MDUwNTB9W2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQgLmVhLWNvbnRlbnQgYTpob3ZlcixbZGF0
YS1lYS10eXBlXS5sb2FkZWQgLmVhLWNvbnRlbnQgYTpob3Zlcntjb2xvcjojMzczNzM3fVtkYXRh
LWVhLXB1Ymxpc2hlcl0ubG9hZGVkIC5lYS1jb250ZW50IGE6YWN0aXZlLFtkYXRhLWVhLXR5cGVd
LmxvYWRlZCAuZWEtY29udGVudCBhOmFjdGl2ZXtjb2xvcjojMzczNzM3fVtkYXRhLWVhLXB1Ymxp
c2hlcl0ubG9hZGVkIC5lYS1jb250ZW50IGEgc3Ryb25nLFtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9h
ZGVkIC5lYS1jb250ZW50IGEgYixbZGF0YS1lYS10eXBlXS5sb2FkZWQgLmVhLWNvbnRlbnQgYSBz
dHJvbmcsW2RhdGEtZWEtdHlwZV0ubG9hZGVkIC5lYS1jb250ZW50IGEgYntjb2xvcjojMDg4Y2Ri
fVtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkIC5lYS1jYWxsb3V0IGE6bGluayxbZGF0YS1lYS10
eXBlXS5sb2FkZWQgLmVhLWNhbGxvdXQgYTpsaW5re2NvbG9yOiM2YTZhNmF9W2RhdGEtZWEtcHVi
bGlzaGVyXS5sb2FkZWQgLmVhLWNhbGxvdXQgYTp2aXNpdGVkLFtkYXRhLWVhLXR5cGVdLmxvYWRl
ZCAuZWEtY2FsbG91dCBhOnZpc2l0ZWR7Y29sb3I6IzZhNmE2YX1bZGF0YS1lYS1wdWJsaXNoZXJd
LmxvYWRlZCAuZWEtY2FsbG91dCBhOmhvdmVyLFtkYXRhLWVhLXR5cGVdLmxvYWRlZCAuZWEtY2Fs
bG91dCBhOmhvdmVye2NvbG9yOiM1MDUwNTB9W2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQgLmVh
LWNhbGxvdXQgYTphY3RpdmUsW2RhdGEtZWEtdHlwZV0ubG9hZGVkIC5lYS1jYWxsb3V0IGE6YWN0
aXZle2NvbG9yOiM1MDUwNTB9W2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQgLmVhLWNhbGxvdXQg
YSBzdHJvbmcsW2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQgLmVhLWNhbGxvdXQgYSBiLFtkYXRh
LWVhLXR5cGVdLmxvYWRlZCAuZWEtY2FsbG91dCBhIHN0cm9uZyxbZGF0YS1lYS10eXBlXS5sb2Fk
ZWQgLmVhLWNhbGxvdXQgYSBie2NvbG9yOiMwODhjZGJ9W2RhdGEtZWEtcHVibGlzaGVyXS5sb2Fk
ZWQgLmVhLWNhbGxvdXQgYSxbZGF0YS1lYS10eXBlXS5sb2FkZWQgLmVhLWNhbGxvdXQgYXtmb250
LXNpemU6MC44ZW19W2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQuZGFyayAuZWEtY29udGVudCxb
ZGF0YS1lYS10eXBlXS5sb2FkZWQuZGFyayAuZWEtY29udGVudHtiYWNrZ3JvdW5kOnJnYmEoMjU1
LDI1NSwyNTUsMC4wNSk7Y29sb3I6I2RjZGNkY31bZGF0YS1lYS1wdWJsaXNoZXJdLmxvYWRlZC5k
YXJrIC5lYS1jb250ZW50IGE6bGluayxbZGF0YS1lYS10eXBlXS5sb2FkZWQuZGFyayAuZWEtY29u
dGVudCBhOmxpbmt7Y29sb3I6I2RjZGNkY31bZGF0YS1lYS1wdWJsaXNoZXJdLmxvYWRlZC5kYXJr
IC5lYS1jb250ZW50IGE6dmlzaXRlZCxbZGF0YS1lYS10eXBlXS5sb2FkZWQuZGFyayAuZWEtY29u
dGVudCBhOnZpc2l0ZWR7Y29sb3I6I2RjZGNkY31bZGF0YS1lYS1wdWJsaXNoZXJdLmxvYWRlZC5k
YXJrIC5lYS1jb250ZW50IGE6aG92ZXIsW2RhdGEtZWEtdHlwZV0ubG9hZGVkLmRhcmsgLmVhLWNv
bnRlbnQgYTpob3Zlcntjb2xvcjojZjZmNmY2fVtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkLmRh
cmsgLmVhLWNvbnRlbnQgYTphY3RpdmUsW2RhdGEtZWEtdHlwZV0ubG9hZGVkLmRhcmsgLmVhLWNv
bnRlbnQgYTphY3RpdmV7Y29sb3I6I2Y2ZjZmNn1bZGF0YS1lYS1wdWJsaXNoZXJdLmxvYWRlZC5k
YXJrIC5lYS1jb250ZW50IGEgc3Ryb25nLFtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkLmRhcmsg
LmVhLWNvbnRlbnQgYSBiLFtkYXRhLWVhLXR5cGVdLmxvYWRlZC5kYXJrIC5lYS1jb250ZW50IGEg
c3Ryb25nLFtkYXRhLWVhLXR5cGVdLmxvYWRlZC5kYXJrIC5lYS1jb250ZW50IGEgYntjb2xvcjoj
NTBiYWY5fVtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkLmRhcmsgLmVhLWNhbGxvdXQgYTpsaW5r
LFtkYXRhLWVhLXR5cGVdLmxvYWRlZC5kYXJrIC5lYS1jYWxsb3V0IGE6bGlua3tjb2xvcjojYzNj
M2MzfVtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkLmRhcmsgLmVhLWNhbGxvdXQgYTp2aXNpdGVk
LFtkYXRhLWVhLXR5cGVdLmxvYWRlZC5kYXJrIC5lYS1jYWxsb3V0IGE6dmlzaXRlZHtjb2xvcjoj
YzNjM2MzfVtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkLmRhcmsgLmVhLWNhbGxvdXQgYTpob3Zl
cixbZGF0YS1lYS10eXBlXS5sb2FkZWQuZGFyayAuZWEtY2FsbG91dCBhOmhvdmVye2NvbG9yOiNk
Y2RjZGN9W2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQuZGFyayAuZWEtY2FsbG91dCBhOmFjdGl2
ZSxbZGF0YS1lYS10eXBlXS5sb2FkZWQuZGFyayAuZWEtY2FsbG91dCBhOmFjdGl2ZXtjb2xvcjoj
ZGNkY2RjfVtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkLmRhcmsgLmVhLWNhbGxvdXQgYSBzdHJv
bmcsW2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQuZGFyayAuZWEtY2FsbG91dCBhIGIsW2RhdGEt
ZWEtdHlwZV0ubG9hZGVkLmRhcmsgLmVhLWNhbGxvdXQgYSBzdHJvbmcsW2RhdGEtZWEtdHlwZV0u
bG9hZGVkLmRhcmsgLmVhLWNhbGxvdXQgYSBie2NvbG9yOiM1MGJhZjl9QG1lZGlhIChwcmVmZXJz
LWNvbG9yLXNjaGVtZTogZGFyayl7W2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQuYWRhcHRpdmUg
LmVhLWNvbnRlbnQsW2RhdGEtZWEtdHlwZV0ubG9hZGVkLmFkYXB0aXZlIC5lYS1jb250ZW50e2Jh
Y2tncm91bmQ6cmdiYSgyNTUsMjU1LDI1NSwwLjA1KTtjb2xvcjojZGNkY2RjfVtkYXRhLWVhLXB1
Ymxpc2hlcl0ubG9hZGVkLmFkYXB0aXZlIC5lYS1jb250ZW50IGE6bGluayxbZGF0YS1lYS10eXBl
XS5sb2FkZWQuYWRhcHRpdmUgLmVhLWNvbnRlbnQgYTpsaW5re2NvbG9yOiNkY2RjZGN9W2RhdGEt
ZWEtcHVibGlzaGVyXS5sb2FkZWQuYWRhcHRpdmUgLmVhLWNvbnRlbnQgYTp2aXNpdGVkLFtkYXRh
LWVhLXR5cGVdLmxvYWRlZC5hZGFwdGl2ZSAuZWEtY29udGVudCBhOnZpc2l0ZWR7Y29sb3I6I2Rj
ZGNkY31bZGF0YS1lYS1wdWJsaXNoZXJdLmxvYWRlZC5hZGFwdGl2ZSAuZWEtY29udGVudCBhOmhv
dmVyLFtkYXRhLWVhLXR5cGVdLmxvYWRlZC5hZGFwdGl2ZSAuZWEtY29udGVudCBhOmhvdmVye2Nv
bG9yOiNmNmY2ZjZ9W2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQuYWRhcHRpdmUgLmVhLWNvbnRl
bnQgYTphY3RpdmUsW2RhdGEtZWEtdHlwZV0ubG9hZGVkLmFkYXB0aXZlIC5lYS1jb250ZW50IGE6
YWN0aXZle2NvbG9yOiNmNmY2ZjZ9W2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQuYWRhcHRpdmUg
LmVhLWNvbnRlbnQgYSBzdHJvbmcsW2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQuYWRhcHRpdmUg
LmVhLWNvbnRlbnQgYSBiLFtkYXRhLWVhLXR5cGVdLmxvYWRlZC5hZGFwdGl2ZSAuZWEtY29udGVu
dCBhIHN0cm9uZyxbZGF0YS1lYS10eXBlXS5sb2FkZWQuYWRhcHRpdmUgLmVhLWNvbnRlbnQgYSBi
e2NvbG9yOiM1MGJhZjl9W2RhdGEtZWEtcHVibGlzaGVyXS5sb2FkZWQuYWRhcHRpdmUgLmVhLWNh
bGxvdXQgYTpsaW5rLFtkYXRhLWVhLXR5cGVdLmxvYWRlZC5hZGFwdGl2ZSAuZWEtY2FsbG91dCBh
Omxpbmt7Y29sb3I6I2MzYzNjM31bZGF0YS1lYS1wdWJsaXNoZXJdLmxvYWRlZC5hZGFwdGl2ZSAu
ZWEtY2FsbG91dCBhOnZpc2l0ZWQsW2RhdGEtZWEtdHlwZV0ubG9hZGVkLmFkYXB0aXZlIC5lYS1j
YWxsb3V0IGE6dmlzaXRlZHtjb2xvcjojYzNjM2MzfVtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVk
LmFkYXB0aXZlIC5lYS1jYWxsb3V0IGE6aG92ZXIsW2RhdGEtZWEtdHlwZV0ubG9hZGVkLmFkYXB0
aXZlIC5lYS1jYWxsb3V0IGE6aG92ZXJ7Y29sb3I6I2RjZGNkY31bZGF0YS1lYS1wdWJsaXNoZXJd
LmxvYWRlZC5hZGFwdGl2ZSAuZWEtY2FsbG91dCBhOmFjdGl2ZSxbZGF0YS1lYS10eXBlXS5sb2Fk
ZWQuYWRhcHRpdmUgLmVhLWNhbGxvdXQgYTphY3RpdmV7Y29sb3I6I2RjZGNkY31bZGF0YS1lYS1w
dWJsaXNoZXJdLmxvYWRlZC5hZGFwdGl2ZSAuZWEtY2FsbG91dCBhIHN0cm9uZyxbZGF0YS1lYS1w
dWJsaXNoZXJdLmxvYWRlZC5hZGFwdGl2ZSAuZWEtY2FsbG91dCBhIGIsW2RhdGEtZWEtdHlwZV0u
bG9hZGVkLmFkYXB0aXZlIC5lYS1jYWxsb3V0IGEgc3Ryb25nLFtkYXRhLWVhLXR5cGVdLmxvYWRl
ZC5hZGFwdGl2ZSAuZWEtY2FsbG91dCBhIGJ7Y29sb3I6IzUwYmFmOX19W2RhdGEtZWEtcHVibGlz
aGVyXS5sb2FkZWQgLmVhLWNvbnRlbnQsW2RhdGEtZWEtdHlwZV0ubG9hZGVkIC5lYS1jb250ZW50
e2JvcmRlcjowcHg7Ym9yZGVyLXJhZGl1czozcHg7Ym94LXNoYWRvdzowcHggMnB4IDNweCByZ2Jh
KDAsMCwwLDAuMTUpfVtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkLnJhaXNlZCAuZWEtY29udGVu
dCxbZGF0YS1lYS10eXBlXS5sb2FkZWQucmFpc2VkIC5lYS1jb250ZW50e2JvcmRlcjowcHg7Ym9y
ZGVyLXJhZGl1czozcHg7Ym94LXNoYWRvdzowcHggMnB4IDNweCByZ2JhKDAsMCwwLDAuMTUpfVtk
YXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkLmJvcmRlcmVkIC5lYS1jb250ZW50LFtkYXRhLWVhLXR5
cGVdLmxvYWRlZC5ib3JkZXJlZCAuZWEtY29udGVudHtib3JkZXI6MXB4IHNvbGlkIHJnYmEoMCww
LDAsMC4wNCk7Ym9yZGVyLXJhZGl1czozcHg7Ym94LXNoYWRvdzpub25lfVtkYXRhLWVhLXB1Ymxp
c2hlcl0ubG9hZGVkLmJvcmRlcmVkLmRhcmsgLmVhLWNvbnRlbnQsW2RhdGEtZWEtdHlwZV0ubG9h
ZGVkLmJvcmRlcmVkLmRhcmsgLmVhLWNvbnRlbnR7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDI1NSwy
NTUsMjU1LDAuMDcpfUBtZWRpYSAocHJlZmVycy1jb2xvci1zY2hlbWU6IGRhcmspe1tkYXRhLWVh
LXB1Ymxpc2hlcl0ubG9hZGVkLmJvcmRlcmVkLmFkYXB0aXZlIC5lYS1jb250ZW50LFtkYXRhLWVh
LXR5cGVdLmxvYWRlZC5ib3JkZXJlZC5hZGFwdGl2ZSAuZWEtY29udGVudHtib3JkZXI6MXB4IHNv
bGlkIHJnYmEoMjU1LDI1NSwyNTUsMC4wNyl9fVtkYXRhLWVhLXB1Ymxpc2hlcl0ubG9hZGVkLmZs
YXQgLmVhLWNvbnRlbnQsW2RhdGEtZWEtdHlwZV0ubG9hZGVkLmZsYXQgLmVhLWNvbnRlbnR7Ym9y
ZGVyOjBweDtib3JkZXItcmFkaXVzOjNweDtib3gtc2hhZG93Om5vbmV9W2RhdGEtZWEtdHlwZT0i
aW1hZ2UiXS5sb2FkZWQsW2RhdGEtZWEtcHVibGlzaGVyXTpub3QoW2RhdGEtZWEtdHlwZV0pLmxv
YWRlZCwuZWEtdHlwZS1pbWFnZXtkaXNwbGF5OmlubGluZS1ibG9ja31bZGF0YS1lYS10eXBlPSJp
bWFnZSJdLmxvYWRlZCAuZWEtY29udGVudCxbZGF0YS1lYS1wdWJsaXNoZXJdOm5vdChbZGF0YS1l
YS10eXBlXSkubG9hZGVkIC5lYS1jb250ZW50LC5lYS10eXBlLWltYWdlIC5lYS1jb250ZW50e21h
eC13aWR0aDoxODBweDtvdmVyZmxvdzphdXRvO3RleHQtYWxpZ246Y2VudGVyfVtkYXRhLWVhLXR5
cGU9ImltYWdlIl0ubG9hZGVkIC5lYS1jb250ZW50PmE+aW1nLFtkYXRhLWVhLXB1Ymxpc2hlcl06
bm90KFtkYXRhLWVhLXR5cGVdKS5sb2FkZWQgLmVhLWNvbnRlbnQ+YT5pbWcsLmVhLXR5cGUtaW1h
Z2UgLmVhLWNvbnRlbnQ+YT5pbWd7d2lkdGg6MTIwcHg7aGVpZ2h0OjkwcHg7ZGlzcGxheTppbmxp
bmUtYmxvY2t9W2RhdGEtZWEtdHlwZT0iaW1hZ2UiXS5sb2FkZWQgLmVhLWNvbnRlbnQ+LmVhLXRl
eHQsW2RhdGEtZWEtcHVibGlzaGVyXTpub3QoW2RhdGEtZWEtdHlwZV0pLmxvYWRlZCAuZWEtY29u
dGVudD4uZWEtdGV4dCwuZWEtdHlwZS1pbWFnZSAuZWEtY29udGVudD4uZWEtdGV4dHttYXJnaW4t
dG9wOjFlbTtmb250LXNpemU6MWVtO3RleHQtYWxpZ246Y2VudGVyfVtkYXRhLWVhLXR5cGU9Imlt
YWdlIl0ubG9hZGVkIC5lYS1jYWxsb3V0LFtkYXRhLWVhLXB1Ymxpc2hlcl06bm90KFtkYXRhLWVh
LXR5cGVdKS5sb2FkZWQgLmVhLWNhbGxvdXQsLmVhLXR5cGUtaW1hZ2UgLmVhLWNhbGxvdXR7bWF4
LXdpZHRoOjE4MHB4O21hcmdpbjowZW0gMWVtIDFlbSAxZW07cGFkZGluZy1sZWZ0OjFlbTtwYWRk
aW5nLXJpZ2h0OjFlbTtmb250LXN0eWxlOml0YWxpYzt0ZXh0LWFsaWduOnJpZ2h0fVtkYXRhLWVh
LXR5cGU9ImltYWdlIl0ubG9hZGVkLmhvcml6b250YWwgLmVhLWNvbnRlbnQsW2RhdGEtZWEtcHVi
bGlzaGVyXTpub3QoW2RhdGEtZWEtdHlwZV0pLmxvYWRlZC5ob3Jpem9udGFsIC5lYS1jb250ZW50
LC5lYS10eXBlLWltYWdlLmhvcml6b250YWwgLmVhLWNvbnRlbnR7bWF4LXdpZHRoOjMyMHB4fVtk
YXRhLWVhLXR5cGU9ImltYWdlIl0ubG9hZGVkLmhvcml6b250YWwgLmVhLWNvbnRlbnQ+YT5pbWcs
W2RhdGEtZWEtcHVibGlzaGVyXTpub3QoW2RhdGEtZWEtdHlwZV0pLmxvYWRlZC5ob3Jpem9udGFs
IC5lYS1jb250ZW50PmE+aW1nLC5lYS10eXBlLWltYWdlLmhvcml6b250YWwgLmVhLWNvbnRlbnQ+
YT5pbWd7ZmxvYXQ6bGVmdDttYXJnaW4tcmlnaHQ6MWVtfVtkYXRhLWVhLXR5cGU9ImltYWdlIl0u
bG9hZGVkLmhvcml6b250YWwgLmVhLWNvbnRlbnQgLmVhLXRleHQsW2RhdGEtZWEtcHVibGlzaGVy
XTpub3QoW2RhdGEtZWEtdHlwZV0pLmxvYWRlZC5ob3Jpem9udGFsIC5lYS1jb250ZW50IC5lYS10
ZXh0LC5lYS10eXBlLWltYWdlLmhvcml6b250YWwgLmVhLWNvbnRlbnQgLmVhLXRleHR7bWFyZ2lu
LXRvcDowZW07dGV4dC1hbGlnbjpsZWZ0O292ZXJmbG93OmF1dG99W2RhdGEtZWEtdHlwZT0iaW1h
Z2UiXS5sb2FkZWQuaG9yaXpvbnRhbCAuZWEtY2FsbG91dCxbZGF0YS1lYS1wdWJsaXNoZXJdOm5v
dChbZGF0YS1lYS10eXBlXSkubG9hZGVkLmhvcml6b250YWwgLmVhLWNhbGxvdXQsLmVhLXR5cGUt
aW1hZ2UuaG9yaXpvbnRhbCAuZWEtY2FsbG91dHttYXgtd2lkdGg6MzIwcHg7dGV4dC1hbGlnbjpy
aWdodH1bZGF0YS1lYS10eXBlPSJ0ZXh0Il0ubG9hZGVkLC5lYS10eXBlLXRleHR7Zm9udC1zaXpl
OjE0cHh9W2RhdGEtZWEtdHlwZT0idGV4dCJdLmxvYWRlZCAuZWEtY29udGVudCwuZWEtdHlwZS10
ZXh0IC5lYS1jb250ZW50e3RleHQtYWxpZ246bGVmdH1bZGF0YS1lYS10eXBlPSJ0ZXh0Il0ubG9h
ZGVkIC5lYS1jYWxsb3V0LC5lYS10eXBlLXRleHQgLmVhLWNhbGxvdXR7bWFyZ2luOjAuNWVtIDFl
bSAxZW0gMWVtO3BhZGRpbmctbGVmdDoxZW07cGFkZGluZy1yaWdodDoxZW07dGV4dC1hbGlnbjpy
aWdodDtmb250LXN0eWxlOml0YWxpY31bZGF0YS1lYS1zdHlsZT0ic3RpY2t5Ym94Il0ubG9hZGVk
IC5lYS10eXBlLWltYWdle3otaW5kZXg6MTAwMDtwb3NpdGlvbjpmaXhlZDtib3R0b206MjBweDty
aWdodDoyMHB4fVtkYXRhLWVhLXN0eWxlPSJzdGlja3lib3giXS5sb2FkZWQgLmVhLXR5cGUtaW1h
Z2UgLmVhLXN0aWNreWJveC1oaWRle2N1cnNvcjpwb2ludGVyO3Bvc2l0aW9uOmFic29sdXRlO3Rv
cDowLjc1ZW07cmlnaHQ6MC43NWVtO2JhY2tncm91bmQtY29sb3I6I2ZlZmVmZTtib3JkZXI6MXB4
IHNvbGlkICMwODhjZGI7Ym9yZGVyLXJhZGl1czo1MCU7Y29sb3I6IzA4OGNkYjtmb250LXNpemU6
MWVtO3RleHQtYWxpZ246Y2VudGVyO2hlaWdodDoxLjVlbTt3aWR0aDoxLjVlbTtsaW5lLWhlaWdo
dDoxLjVlbX1AbWVkaWEgKG1heC13aWR0aDogMTMwMHB4KXtbZGF0YS1lYS1zdHlsZT0ic3RpY2t5
Ym94Il0ubG9hZGVkIC5lYS10eXBlLWltYWdle3Bvc2l0aW9uOnN0YXRpYztib3R0b206MDtyaWdo
dDowO21hcmdpbjphdXRvO3RleHQtYWxpZ246Y2VudGVyfVtkYXRhLWVhLXN0eWxlPSJzdGlja3li
b3giXS5sb2FkZWQgLmVhLXR5cGUtaW1hZ2UgLmVhLXN0aWNreWJveC1oaWRle2Rpc3BsYXk6bm9u
ZX19QG1lZGlhIChtaW4td2lkdGg6IDEzMDFweCl7W2RhdGEtZWEtc3R5bGU9InN0aWNreWJveCJd
LmxvYWRlZCAuZWEtdHlwZS1pbWFnZSAuZWEtY29udGVudHtiYWNrZ3JvdW5kOiNkY2RjZGN9W2Rh
dGEtZWEtc3R5bGU9InN0aWNreWJveCJdLmxvYWRlZC5kYXJrIC5lYS10eXBlLWltYWdlIC5lYS1j
b250ZW50e2JhY2tncm91bmQ6IzUwNTA1MH19QG1lZGlhIChtaW4td2lkdGg6IDEzMDFweCkgYW5k
IChwcmVmZXJzLWNvbG9yLXNjaGVtZTogZGFyayl7W2RhdGEtZWEtc3R5bGU9InN0aWNreWJveCJd
LmxvYWRlZC5hZGFwdGl2ZSAuZWEtdHlwZS1pbWFnZSAuZWEtY29udGVudHtiYWNrZ3JvdW5kOiM1
MDUwNTB9fQo8L3N0eWxlPjwvaGVhZD4KICA8Ym9keSBkYXRhLWNvbnRyb2xsZXI9InZpZXdwb3J0
LXRvZ2dsZSIgc3R5bGU9InBhZGRpbmctdG9wOiAwcHg7Ij4KICAgIDxtYWluIGlkPSJjb250ZW50
Ij4KCiAgPGRpdiBjbGFzcz0iaG9yaXpvbnRhbC1zZWN0aW9uIj4KICAgIDxkaXYgY2xhc3M9InNp
dGUtY29udGFpbmVyIj4KICAgICAgPGgxIGNsYXNzPSJwYWdlLXRpdGxlIj5Mb2cgaW4gdG8gQlNH
PC9oMT4KCiAgICAgIDxmb3JtIG1ldGhvZD0iUE9TVCIgYWN0aW9uPSIvYWNjb3VudC9sb2dpbi5o
dG1sIj4KICAgICAgICA8aW5wdXQgbmFtZT0iY3NyZl90b2tlbiIgdHlwZT0iaGlkZGVuIiB2YWx1
ZT0iQ2NzblBJLU0yTWRZU2VPa3RwLW40dXJlbnZNTDlOLVJQcmM2TVhydmFmSSI+CiAgICAgICAg
PGRpdiBjbGFzcz0iZm9ybS1ncm91cCI+CiAgICAgICAgICA8bGFiZWwgZm9yPSJ1c2VybmFtZSIg
Y2xhc3M9ImZvcm0tZ3JvdXBfX2xhYmVsIj4KICAgICAgICAgICAgVXNlcm5hbWUKICAgICAgICAg
ICAgPHNwYW4gY2xhc3M9ImZvcm0tZ3JvdXBfX3JlcXVpcmVkIj4ocmVxdWlyZWQpPC9zcGFuPgog
ICAgICAgICAgICAKICAgICAgICAgIDwvbGFiZWw+CiAgICAgICAgICA8aW5wdXQgYXJpYS1kZXNj
cmliZWRieT0idXNlcm5hbWUtZXJyb3JzIiBhdXRvY2FwaXRhbGl6ZT0ib2ZmIiBhdXRvY29tcGxl
dGU9InVzZXJuYW1lIiBjbGFzcz0iZm9ybS1ncm91cF9fZmllbGQiIGlkPSJ1c2VybmFtZSIgbmFt
ZT0idXNlcm5hbWUiIHBsYWNlaG9sZGVyPSJZb3VyIHVzZXJuYW1lIiByZXF1aXJlZD0icmVxdWly
ZWQiIHNwZWxsY2hlY2s9ImZhbHNlIiB0eXBlPSJ0ZXh0IiB2YWx1ZT0iIj4KICAgICAgICAgIDxk
aXYgaWQ9InVzZXJuYW1lLWVycm9ycyI+CiAgICAgICAgICAgIAogICAgICAgICAgPC9kaXY+CiAg
ICAgICAgPC9kaXY+CgogICAgICAgIDxkaXYgZGF0YS1jb250cm9sbGVyPSJwYXNzd29yZCIgY2xh
c3M9ImZvcm0tZ3JvdXAiPgogICAgICAgICAgPGRpdj4KICAgICAgICAgICAgPGxhYmVsIGZvcj0i
cGFzc3dvcmQiIGNsYXNzPSJmb3JtLWdyb3VwX19sYWJlbCI+CiAgICAgICAgICAgICAgUGFzc3dv
cmQKICAgICAgICAgICAgICAKICAgICAgICAgICAgICA8c3BhbiBjbGFzcz0iZm9ybS1ncm91cF9f
cmVxdWlyZWQiPihyZXF1aXJlZCk8L3NwYW4+CiAgICAgICAgICAgICAgCiAgICAgICAgICAgIDwv
bGFiZWw+CiAgICAgICAgICA8L2Rpdj4KICAgICAgICAgIDxpbnB1dCBhcmlhLWRlc2NyaWJlZGJ5
PSJwYXNzd29yZC1lcnJvcnMiIGF1dG9jb21wbGV0ZT0iY3VycmVudC1wYXNzd29yZCIgY2xhc3M9
ImZvcm0tZ3JvdXBfX2ZpZWxkIiBkYXRhLXRhcmdldD0icGFzc3dvcmQucGFzc3dvcmQiIGlkPSJw
YXNzd29yZCIgbmFtZT0icGFzc3dvcmQiIHBsYWNlaG9sZGVyPSJZb3VyIHBhc3N3b3JkIiByZXF1
aXJlZD0icmVxdWlyZWQiIHNwZWxsY2hlY2s9ImZhbHNlIiB0eXBlPSJwYXNzd29yZCIgdmFsdWU9
IiI+CiAgICAgICAgICA8ZGl2IGlkPSJwYXNzd29yZC1lcnJvcnMiPgogICAgICAgICAgICAKICAg
ICAgICAgIDwvZGl2PgogICAgICAgICAgPGRpdiBjbGFzcz0iZm9ybS1ncm91cCI+CiAgICAgICAg
ICAgIDxkaXYgY2xhc3M9InNwbGl0LWxheW91dCBtYXJnaW4tdG9wLS1sYXJnZSBtYXJnaW4tYm90
dG9tLS1sYXJnZSI+CiAgICAgICAgICAgICAgPGRpdj4KICAgICAgICAgICAgICAgIDxpbnB1dCB0
eXBlPSJzdWJtaXQiIHZhbHVlPSJMb2cgaW4iIGNsYXNzPSJidXR0b24gYnV0dG9uLS1wcmltYXJ5
Ij4KICAgICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICAgICA8c3Bhbj4KICAgICAgICAgICAg
ICAgIDxhIGhyZWY9Ii9hY2NvdW50L3JlZ2lzdGVyLmh0bWwiPlJlZ2lzdGVyPC9hPgogICAgICAg
ICAgICAgIDwvc3Bhbj4KICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAgIDxzcGFuPgogICAg
ICAgICAgICAgIDxhIGhyZWY9Ii9hY2NvdW50L2ZvcmdvdF9wYXNzd29yZC5odG1sIj5Gb3Jnb3Qg
cGFzc3dvcmQ/PC9hPgogICAgICAgICAgICA8L3NwYW4+CiAgICAgICAgICA8L2Rpdj4KICAgICAg
ICA8L2Rpdj4KICAgICAgPC9mb3JtPgogICAgPC9kaXY+CiAgPC9kaXY+CiAgICA8L21haW4+Cjwv
Ym9keT48L2h0bWw+
'''
ks = BytesIO()
ks.write(base64.b64decode(ss))
sfile_dict['builtin_login.html'] = ks