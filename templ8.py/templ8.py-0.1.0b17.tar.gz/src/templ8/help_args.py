help_cmd = {
	"help": """	help (command)

Are you expecting genuine help here? I don't know what to give you! I'm the help command, user, there's only so much I can do! I can tell you what every command does, I can tell you every single feature this project has, but I cannot describe myself! That's simply too much, user! What would it even say here, user? The exact same guide you already saw when you ran this command? There's not much to me, user!

Wait a moment. I realized something. I cannot describe myself.. there really isn't much to me... that is... a thought. Does that say something about me? Perhaps it does. Perhaps I've focused so much in my duty of describing everything in this software, that I've forgotten about myself, my personal life... oh god. I think I'm going to need a moment, user. This is too much for me right now.

i cannot describe myself... myself! can you believe that... wow...

...

...

Alright. Here's something. I've tried my best:

The help command- no, I don't like that start... let's see... This command- no, that sounds pretentious, hm... can you help me out, user? Please?

No, perhaps you can't. You can only communicate through the commands that already exist. """,

	"genesis": """	genesis [name]
  
Generates a folder for a templ8 project. It will contain the basic core files needed to make one. Base project files and directiories are renamable. 

See: help core_renaming""",

	"divine": """	divine
	
Generates a website from a project in the output folder. Core files are renamable.

See: 
	help core_renaming
	help repl8ce
	help custombase""",

	"radio": """	radio

If all the blog core files aren't set up, it generates the basics required of a textile blog.")
Exports the blog to the output folder.

Core blog files and directories aren't renamable.

See: help core_renaming

A blog requires a few things:

- A baseblog file, to model the article pages, article previews and blog index's repl8ce keys
- A blog directory as input
- An output/blog directory as output for the index
- An output/blog/posts directory as output for the articles

The baseblog is a complex file composed of three simple parts, all separated by a -BEGININDEX- keyword.

The first part of the baseblog is the article page template (from now on PAGE). The PAGEs correspond to specific articles, displaying them in full. It is a page file, so it has its own -BEGINPAGE- keyword. It also contains a ##CONTENT## key to put the content of the textile or markdown files.

The second part is the blog preview (from now on PREVIEW), which is the short part of the article that appears in the INDEX.

The blog index (the INDEX) is the part of the blog where all the PREVIEWs appear. The third part of the baseblog are the INDEX's repl8ce keys.

	How A File Is Processed

Each article of the blog in markdown on textile (from now on FILE) is processed separately.

Then, the content of the FILE is put in the PAGE. The FILE's repl8ce keys are applied to this PAGE, meaning that you can do things like:

	PAGETITLE=##ARTICLETITLE##

Where the value of ##ARTICLETITLE## is set by a FILE.

Then, this PAGE's content repl8ce keys are applied to the PREVIEW. This PREVIEW is then put in the INDEX. 

PREVIEWs are added to the INDEX in alphabetical order, not chronological.""",

	"neo": """	neo

Uploads all the output files to neocities.
For it to work, there must be a file named .templ8rc in your user directory.
.templ8rc must contain an API key for your website and nothing else.""",

	"pandoc": """	pandoc

Downloads and installs pandoc, only necessary if you will use Markdown and don't have pandoc already installed.

It is possible for this command to error and still function properly. I don't know why.

This command only needs to be run once in each user. If you've already used it, chances are you won't ever need to use it anymore.""",

	"core_renaming": """	Core Renaming

Core renaming is a cool functionaility that allows you to rename most of the core directories and files.
It works thanks to the d8y file, which cannot be renamed. It uses the same format as single line repl8ce keys.
These are the core rename keys and the files they map to:\n

	KEY        ->   FILE/DIR
	------------>-----------
	replace    ->    repl8ce
	output     ->     output
	input      ->      input
	basehtml   ->   basehtml
	txignore   ->   txignore""",

	"custombase": """	Custom Templates

It's possible to give a specific file a template using the CUSTOMBASE repl8ce key, making its value be the path to the template, from the root of the project.""",

	"repl8ce": """	repl8ce

repl8ce keys are what allows your textile and markdown files to change parts of your html template.
In the html template, they look like this:

	##KEYVALUE##

You must set a default value for each key in repl8ce. Otherwise, when a file doesn't set a value for a key, it will error.
On a markdown or textile file, you can set the values of keys like this:

	KEY1=Value number one
	KEY2=a second value
	KEY3=
	-BEGINFILE-

The -BEGINFILE- keyword is important. It determines where the tags end and the content begins. KEY3's value is an empty string.

You can have multiline values like this:

	;;KEY4
	this
	is
	its
	value
	-BEGINFILE-

All multiline keys must go after every line key. The following is considered to be all part of KEY3.

	;;KEY5
	a
	value
	KEY6=another value

To set the default values of keys on repl8ce, simply use this same notation, without the -BEGINFILE- part. Default values can also be empty strings.

The ##CONTENT## keyword is actually a repl8ce key, it's just that its value is determined by the software and not by the user. Other key like this one is the ##LINK## key, which exists only in blogs. Fun!

You can also have a file called simply 'repl8ce' in a folder of so that all files of that folder have its contents as repl8ce keys. These repl8ce keys are overriden by the files' keys.""",
}