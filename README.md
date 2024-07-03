
![uploaded image](https://gcdnb.pbrd.co/images/BmJUa3DYpFar.png?o=1)

# Commit Stats

Script to extract commit statistic on single repository either public or private, information include:
- Author Names
- Project Owner
- Contributors count
- Period (first commit - last commit) in working days
- Total Commit
- Commit Average

Each programming language will made it own section that have information like this:
 - Unique files count
 - Lines added
 - Lines deleted
 - Total lines change
 
 All you need to do is only github API, changes main.py and fill this line:
 
	CONFIG_AUTH = 'Github classic token'
	CONFIG_OWNER = 'repository owner username'
	CONFIG_REPO = 'repository name'
	CONFIG_AUTHOR = 'your_username'
Result will be saved on result.html
