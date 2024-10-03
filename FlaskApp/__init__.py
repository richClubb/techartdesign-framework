from flask import Flask
from flask import render_template
import markdown
from markdown.extensions.toc import TocExtension
from flaskext.markdown import Markdown
from json import load
import os

from os.path import join, isdir

app = Flask(__name__)
Markdown(app)


CONFIG_FILE_PATH = "config.json"
CONTENT_DIR = "/home/web/techartdesign-content/"
IMAGE_DIR = "/home/web/techartdesign-content/static/images"

# -------------------------------------------------------------- #

@app.route('/')
def index():
   json_nav_page_links = load_page_nav()

   activity = recent_activity_all(5, 5)

   home_content_file_path = join(CONTENT_DIR, "home", "home.md")

   try:
      with open(home_content_file_path, 'r') as ff:
         home_content = ff.read()
   except FileNotFoundError:
      pass

   return render_template("index.html", links=json_nav_page_links, home_content=home_content, activity_list=activity)

@app.route('/projects')
def projects():

   json_nav_page_links = load_page_nav()

   recent_activity = recent_activity_projects(10)

   print(recent_activity)

   projects = {}
   error_text = ""

   try:
      projects_dirs = os.listdir(join(CONTENT_DIR, "projects"))
   except FileNotFoundError:
      projects_dirs = None

   projects_overview_file_path = join(CONTENT_DIR, "projects", "overview.md")
   projects_overview_content = ""

   try:
      with open(projects_overview_file_path, 'r') as ff:
         projects_overview_content = ff.read()
   except FileNotFoundError:
      pass

   if projects_dirs is None:
      error_text = "Error retrieving projects"
   elif len(projects_dirs) == 0:
      error_text = "No projects, check back later"
   else:
      for project in projects_dirs:
         try:
            file_path = join(CONTENT_DIR, "projects", project, "project.json")
         except:
            continue

         try:
            with open(file_path, 'r') as ff:
               json_data = load(ff)
               projects[json_data["name"]] = { "topics" : json_data["topics"], "brief" : json_data["brief"], "link" : "/projects/" + project }
         except:
            continue

   return render_template("projects.html", 
                          links=json_nav_page_links, 
                          projects=projects,
                          projects_overview_content=projects_overview_content, 
                          recent_activity_list=recent_activity, 
                          error_text=error_text)

@app.route("/projects/<path>")
def project_page(path):

   json_nav_page_links = load_page_nav()

   # make sure it is easy for the URL to be manually enterered.
   projects_dirs = os.listdir(join(CONTENT_DIR, "projects"))

   if path in projects_dirs:
      project_dir = join(CONTENT_DIR, "projects", path)
      json_file_path = join(project_dir, "project.json")
      with open(json_file_path, 'r') as ff:
         json_file = load(ff)
         content_file_path = join(project_dir, json_file["content"])
         with open(content_file_path, "r") as gg:
            page_content = gg.read()
            return render_template("project_page.html", links=json_nav_page_links, project_text=page_content)
   else:
      return render_template("404.html", links=json_nav_page_links)

@app.route('/blog')
def blog():
   json_nav_page_links = load_page_nav()

   recent_activity = recent_activity_blogs(10)

   blogs = {}
   error_text = ""

   blog_overview_file_path = join(CONTENT_DIR, "blog", "overview.md")
   blog_overview_content = ""

   try:
      with open(blog_overview_file_path, 'r') as ff:
         blog_overview_content = ff.read()
   except FileNotFoundError:
      pass

   try:
      blogs_dirs = os.listdir(join(CONTENT_DIR, "blog"))
   except FileNotFoundError:
      blogs_dirs = None

   if blogs_dirs is None:
      error_text = "Error retrieving blog posts"
   elif len(blogs_dirs) == 0:
      error_text = "No blogs here, come back later"
   else:
      for blog in blogs_dirs:
         print(blog)
         blog_path = join(CONTENT_DIR, "blog", blog, "brief.json")
         try:
            with open(blog_path, 'r') as ff:
               json_data = load(ff)
               blogs[json_data["title"]] = { "title": json_data["title"], "brief" : json_data["brief"], "topics" : json_data["topics"], "link" : "/blog/" + blog }
         except FileNotFoundError:
            continue
         except NotADirectoryError:
            continue

   # return blogs
   return render_template("blog.html", 
                          links=json_nav_page_links, 
                          blogs=blogs,
                          blog_overview_content=blog_overview_content,
                          recent_activity_list=recent_activity, 
                          error_text=error_text)

@app.route("/blog/<path>")
def blog_page(path):

   json_nav_page_links = load_page_nav()

   # make sure it is easy for the URL to be manually enterered.
   blog_dirs = os.listdir(join(CONTENT_DIR, "blog"))

   if path in blog_dirs:
      blog_dir = join(CONTENT_DIR, "blog", path)
      blog_file_path = join(blog_dir, "post.md")
      with open(blog_file_path, "r") as ff:
         page_content = ff.read()
         return render_template("blog_page.html", links=json_nav_page_links, blog_text=page_content)
   else:
      return render_template("404.html", links=json_nav_page_links)

@app.route("/links")
def links():
   ''' Generate the links page '''
   json_nav_page_links = load_page_nav()

   # I'm still trying to extract the TOC from the markdown page for
   # the time being I'm just going to put recent activity.
   activity = recent_activity_all(5, 5)

   links_content_file = join(CONTENT_DIR, "links", "links.md")
   with open(links_content_file, 'r') as ff:
      links_content = ff.read()
      
      return render_template("links.html", links=json_nav_page_links, links_text=links_content, activity_list=activity)


@app.route("/contact")
def contact():
   json_nav_page_links = load_page_nav()

   activity = recent_activity_all(5, 5)

   contact_content_file_path = join(CONTENT_DIR, "contact", "contact.md")
   contact_content = ""

   try:
      with open(contact_content_file_path, 'r') as ff:
         contact_content = ff.read()
   except FileNotFoundError:
      pass

   return render_template("contact.html", 
                          contact_content=contact_content, 
                          links=json_nav_page_links,
                          activity_list=activity)

# -------------------------------------------------------------- #

def load_page_nav():
   json_file_path = join(CONTENT_DIR, "site_nav.json")
   json_file = open(json_file_path, "r")

   json = load(json_file)

   return json

def recent_activity_all(number_blogs=0, number_projects=0):
   """ Returns a sorted list with the title, type and link of both the projects and blogs """

   blog_list = recent_activity_blogs(number_blogs)
   projects_list = recent_activity_projects(number_projects)

   complete_list = []

   for blog in blog_list:
      blog.append("blog")
      complete_list.append(blog)

   for project in projects_list:
      project.append("project")
      complete_list.append(project)

   for i in range(len(complete_list) - 1):
      for j in range(i+1, len(complete_list)):
         if complete_list[i][1] < complete_list[j][1]:
            t = complete_list[i]
            complete_list[i] = complete_list[j]
            complete_list[j] = t

   return(complete_list)

def recent_activity_projects(number=0):
   """ Returns a sorted list with the title and link of the projects """

   try:
      projects_dirs = os.listdir(join(CONTENT_DIR, "projects"))
   except FileNotFoundError:
      projects_dirs = None

   projects_list = []

   if projects_dirs is not None:
      for project in projects_dirs:

         project_json_file_path = join(CONTENT_DIR, "projects", project, "project.json")

         try:
            with open(project_json_file_path, "r") as ff:
               project_json_file = load(ff)
               projects_list.append([ project_json_file["name"], project_json_file["date_modified"], "/projects/" + project ])
         except FileNotFoundError:
            continue
         except NotADirectoryError:
            continue

      for i in range(len(projects_list) - 1):
         for j in range(i+1, len(projects_list)):
            if projects_list[i][1] < projects_list[j][1]:
               t = projects_list[i]
               projects_list[i] = projects_list[j]
               projects_list[j] = t

      if number != 0:
         projects_list = projects_list[0:min(number,len(projects_list))]

   return projects_list

def recent_activity_blogs(number=0):
   """ Returns a sorted list with the title and link of the projects """
   try:
      blog_dirs = os.listdir(join(CONTENT_DIR, "blog"))
   except FileNotFoundError:
      blog_dirs = None
   blog_list = []

   if blog_dirs is not None:

      for blog in blog_dirs:
         blog_json_file_path = join(CONTENT_DIR, "blog", blog, "brief.json")
         try:
            with open(blog_json_file_path, "r") as ff:
               project_json_file = load(ff)
               blog_list.append([ project_json_file["title"], project_json_file["date_modified"], "/blog/" + blog ])
         except FileNotFoundError:
            continue
         except NotADirectoryError:
            continue

      for i in range(len(blog_list) - 1):
         for j in range(i+1, len(blog_list)):
            if blog_list[i][1] < blog_list[j][1]:
               t = blog_list[i]
               blog_list[i] = blog_list[j]
               blog_list[j] = t

      if number != 0:
         blog_list = blog_list[0:min(number, len(blog_list))]

   return blog_list

@app.route('/static/images/<filename>')
def static_images(filename):
   return Flask.send_from_directory(IMAGE_DIR, filename)


if __name__ == "__main__":

   if os.path.isfile(CONFIG_FILE_PATH):
      try:      
         config_file = open(CONFIG_FILE_PATH, 'r')
         config = load(config_file)

         CONTENT_DIR = config["content_dir"]

         app.run(debug = True)
      except:
         print("Error starting application")
   else:
      print("something went wrong")
   
