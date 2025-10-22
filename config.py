email = "your-email-on-linkedin@com"
password = "your_password"
apikeyOpenAI = "open_ai_key"
cvName = 'cv.pdf'
LinkedInProfileURL = "https://www.linkedin.com/in/danielfnz/"
Location = "Minas Gerais, Brasil"
salaryCLT = "11000"
salaryPJ = "15000"

# run browser in headless mode, no browser screen will be shown it will work in background.
browser = ["Chrome"]
headless = False

# These settings are for running Linkedin job apply bot.
# location you want to search the jobs - ex : ["Brasil", "Singapore", "New York City Metropolitan Area", "Monroe County"]
# continent locations:["Europe", "Asia", "Australia", "NorthAmerica", "SouthAmerica", "Africa", "Australia"]
location = ["Brasil"]
# keywords related with your job search
keywords = ['angular']
# job experience Level - ex:  ["Internship", "Entry level" , "Associate" , "Mid-Senior level" , "Director" , "Executive"]
experienceLevels = ["Mid-Senior level"]
# job posted date - ex: ["Any Time", "Past Month" , "Past Week" , "Past 24 hours"] - select only one
datePosted = ["Any Time"]
# job type - ex:  ["Full-time", "Part-time" , "Contract" , "Temporary", "Volunteer", "Intership", "Other"]
jobType = ["Full-time", "Part-time", "Contract", "Temporary"]
# remote  - ex: ["On-site" , "Remote" , "Hybrid"]
remote = ["Remote"]
# sort - ex:["Recent"] or ["Relevent"] - select only one
sort = ["Recent"]
# Blacklist companies you dont want to apply - ex: ["Apple","Google"]
blacklistCompanies = ["zup"]
# Blaclist keywords in title - ex:["manager", ".Net"]
blackListTitles = ['PCD', 'hibrido', 'Mulher', 'ZUP']
# Follow companies after sucessfull application True - yes, False - no
followCompanies = False
# If you have multiple CV's you can choose which one you want the bot to use. (1- the first one on the list, 2 - second , etc)
preferredCv = 1
# Do not apply the jobs having these keywords in the job description
blockJobDescription = []
chromeProfilePath = r""
# Testing & Debugging features
displayWarnings = True
