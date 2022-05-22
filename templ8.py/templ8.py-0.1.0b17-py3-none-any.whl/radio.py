import os
import textile
import templ8.programstate
import templ8.blessing
from templ8.blessing import makedir
from templ8.blessing import mod_replaces
from templ8.blessing import parse_content

# Build the blog
def radio():
	# Load the state of the program (important files and stuff)
	state = templ8.programstate.ProgramState()
	
	# Folder where the blog is
	blog_input = "blog"
	
	# Folder where the processed blog will be
	blog_output = os.path.join(state.output_folder, "blog")
	makedir(blog_input)
	makedir(blog_output)
	
	# Folder for the articles
	makedir(os.path.join(blog_output, "posts"))
	
	# The blogbase file
	article_format_path = "blogbase"
	
	# If there's no base blog file, create one
	if not os.path.exists(article_format_path):
		with open(article_format_path, "w") as f:
			f.write(templ8.blessing.DEF_BASEHTML_CONTENT)
	
	# The article format is the file that defines how an article will look, both in its own page and in the index
	article_format_page = open(article_format_path, "r").read().split("-BEGININDEX-")[0]
	article_format_index = open(article_format_path, "r").read().split("-BEGININDEX-")[1]
	blog_replacekeys = open(article_format_path, "r").read().split("-BEGININDEX-")[2]
	
	blog_index = ""
	
	# Walk through the blog folder
	for subdir, dirs, files in os.walk(blog_input):
		sortedfiles = files
		sortedfiles.sort(reverse = True)
		
		for file in sortedfiles:
			path = os.path.join(subdir, file)
			file_extension = os.path.splitext(path)[1]
			file_replace = state.replacements
			# These refer to the individual articles
			file_headers = open(path, "r").read().split("-BEGINFILE-", 1)[0]
			file_content = open(path, "r").read().split("-BEGINFILE-", 1)[1]
			
			# Get the replace keys of the individual article
			mod_replaces(file_replace, file_headers)
			
			# This variable refers to the article page with the contents of this individual file
			article_page = article_format_page
			
			# Apply the file's keys to the article page and put in the content
			article_page = article_page.replace("##CONTENT##", file_content)
			
			for key in file_replace:
				article_page = article_page.replace("##"+key+"##", file_replace[key])
			
			
			# Get the keys and content of this article page
			article_page_headers = article_page.split("-BEGINFILE-")[0]
			article_page_content = article_page.split("-BEGINFILE-")[1]
			
			
			mod_replaces(file_replace, article_page_headers)
			
			# This variable is the final page
			final_page = state.basehtml_content
			
			# Apply the keys of the article page and put in the content
			final_page = final_page.replace("##CONTENT##", parse_content(article_page_content, file_extension))
			
			# (This var is for the index page, it takes the format and puts the info in)			
			current_file_index = textile.textile(parse_content(article_format_index.replace("##INTRO##", file_replace["INTRO"]), file_extension))
			
			
			current_file_index = current_file_index.replace("##LINK##", 'posts/' + file.replace(".textile", "/index.html"))
			for key in file_replace:
				final_page = final_page.replace("##"+key+"##", file_replace[key])
				current_file_index = current_file_index.replace("##"+key+"##", file_replace[key])
			blog_index += current_file_index + "\n"
			
			# Save it
			blog_outpath = os.path.join(blog_output, "posts", file.replace(".textile", "/index.html"))
			makedir(os.path.join(blog_output, "posts", file.replace(".textile", "")))
			with open(blog_outpath, "w") as f:
				f.write(final_page)
	
	# Generate the index
	blog_replace = state.replacements.copy()
	mod_replaces(blog_replace, blog_replacekeys)
	
	index_html = state.basehtml_content
	if "CUSTOMBASE" in blog_replace:
		if os.path.exists(blog_replace["CUSTOMBASE"]):
			index_html = open(filerepl["CUSTOMBASE"], "r").read()
	
	index_html = index_html.replace("##CONTENT##", blog_index)
	for key in blog_replace:
		index_html = index_html.replace("##"+key+"##", blog_replace[key])
	
	with open(os.path.join(blog_output, "index.html"), "w") as f:
		f.write(index_html)
		
	print("Finished assembling")