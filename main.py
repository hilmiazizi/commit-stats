import requests
import json
import os
from datetime import datetime, timedelta
import time
import os
if os.name == 'nt':
    os.system('cls')
else:
    os.system('clear')


CONFIG_AUTH = 'ghp_xxxxxxxxx'
CONFIG_OWNER = 'hilmiazizi'
CONFIG_REPO = 'commit-stats'
CONFIG_AUTHOR = 'hilmiazizi'
storage = []
file_extension = json.loads(requests.get('https://gist.githubusercontent.com/ppisarczyk/43962d06686722d26d176fad46879d41/raw/211547723b4621a622fc56978d74aa416cbd1729/Programming_Languages_Extensions.json').text)



def HTMLWriter(name,owner,contributor,tanggal,commit,commit_average,content):
	source = open('template.html').readlines()
	result = open('result.html','w').close()
	result = open('result.html','a+')
	for i in source:
		if '#name#' in i:
			i = i.replace("#name#", name)
		elif '#owner#' in i:
			i = i.replace("#owner#", owner)
		elif '#contributor#' in i:
			i = i.replace("#contributor#", contributor)
		elif '#tanggal#' in i:
			i = i.replace("#tanggal#", tanggal)
		elif '#commit#' in i:
			i = i.replace("#commit#", commit)
		elif '#commit_average#' in i:	
			i = i.replace("#commit_average#", commit_average)
		elif '<-- HERE -->' in i:
			i = i.replace("<-- HERE -->", content)

		result.write(i+'\n')
	result.close()
	return True


def GetContributor():
	headers = {
		'Accept': 'application/vnd.github+json',
		'Authorization': 'Bearer '+CONFIG_AUTH,
		'X-GitHub-Api-Version': '2022-11-28',
	}

	response = requests.get('https://api.github.com/repos/'+CONFIG_OWNER+'/'+CONFIG_REPO+'/contributors', headers=headers)
	result = json.loads(response.text)
	return len(result)


def GetOwner(user):
	headers = {
		'Accept': 'application/vnd.github+json',
		'Authorization': 'Bearer '+CONFIG_AUTH,
		'X-GitHub-Api-Version': '2022-11-28',
	}

	response = requests.get('https://api.github.com/users/'+user, headers=headers)
	result = json.loads(response.text)
	return result['name']


def MatchLanguage(file_format):
	global file_extension
	for i in file_extension:
		if 'extensions' in i.keys():
			if file_format in i['extensions']:
				return i['name']
	return False


def NextExtractor(response):
	temp = response.split(',')
	next_page = False
	for i in temp:
		if 'rel="next"' in i:
			next_page = i.split(';')[0][1:-1]

	return next_page


def GetCommitHistory(next_page=False):
	global CONFIG_AUTH,CONFIG_OWNER,CONFIG_REPO, storage

	headers = {
		'Accept': 'application/vnd.github+json',
		'Authorization': 'Bearer '+CONFIG_AUTH,
	}

	params = {
		'author': CONFIG_AUTHOR,
		'until': datetime.now().isoformat(),
		'per_page': 100
	}

	if not next_page:
		response = requests.get('https://api.github.com/repos/'+CONFIG_OWNER+'/'+CONFIG_REPO+'/commits', params=params, headers=headers)
		result = json.loads(response.text)
		for x in result:
			storage.append(x)


		next_page = NextExtractor(response.headers['Link'])
		if next_page:
			GetCommitHistory(next_page)
		else:
			return True
	else:
		response = requests.get(next_page, params=params, headers=headers)
		result = json.loads(response.text)
		for x in result:
			storage.append(x)

		next_page = NextExtractor(response.headers['Link'])
		if next_page:
			GetCommitHistory(next_page)
		else:
			return True
	
def CommitStats(commits):
	headers = {
			'Accept': 'application/vnd.github+json',
			'Authorization': 'Bearer '+CONFIG_AUTH,
		}
	counter = 0

	for line in commits:
		temp = []
		result = json.loads(requests.get('https://api.github.com/repos/'+CONFIG_OWNER+'/'+CONFIG_REPO+'/commits/'+line[0], headers=headers).text)
		for x in result['files']:
			filename = x['filename']
			language = "."+x['filename'].split('.')[-1]
			language = MatchLanguage(language)
			if not language or language == 'reStructuredText':
				continue

			addition = x['additions']
			deletion = x['deletions']
			temp.append([filename, language, addition, deletion])

		commits[counter].append(temp)
		counter+=1

	return commits


contributor_count = GetContributor()
owner_name = GetOwner(CONFIG_OWNER)
user_name = GetOwner(CONFIG_AUTHOR)

print("[+] Fetching All Commit . . .")
GetCommitHistory()
if storage:
	storage.reverse()
	grouped_commit = {}

	for x in storage:
		date_str = x['commit']['committer']['date']
		datetime_obj = datetime.fromisoformat(date_str[:-1] + '+00:00') 
		datetime_obj = datetime_obj.strftime("%d-%m-%Y")
		grouped_commit[datetime_obj] = []

	for x in storage:
		date_str = x['commit']['committer']['date']
		datetime_obj = datetime.fromisoformat(date_str[:-1] + '+00:00') 
		datetime_obj = datetime_obj.strftime("%d-%m-%Y")
		grouped_commit[datetime_obj].append([x['sha'],x['commit']['message']])

	
	#Calculate working days
	date_span = [datetime.strptime(x, '%d-%m-%Y') for x in grouped_commit.keys()]
	early_date = min(date_span)
	latest_date = max(date_span)
	day_passed = (latest_date-early_date).days
	weekdays_count = 0

	for day in range(day_passed+1):
		current_date = early_date + timedelta(days=day)
		if 0 <= current_date.weekday() <= 4:
			weekdays_count += 1

	print('[+]',len(storage),' Commit made in the span of',weekdays_count,'working days!, Extracting commit stats!')

	counter = 0
	for x in grouped_commit.keys():
		counter+=1
		result = CommitStats(grouped_commit[x])
		grouped_commit[x] = result
		print('    ['+str(counter)+'/'+str(len(grouped_commit))+']',x,'Commited to',len(grouped_commit[x]), 'Files')
		
	print('\n\n')
	unique_files = []
	prog_lang = {}
	add_lang = {}
	total_addition = 0
	total_deletion = 0
	for x in grouped_commit.keys():
		for index in grouped_commit[x]:
			for line in index[2]:
				prog_lang[line[1]] = []
				add_lang[line[1]] = [0,0]


	#print(add_lang)
	for x in grouped_commit:
		for index in grouped_commit[x]:
			for line in index[2]:
				if line[1] not in unique_files:
					unique_files.append(line[0])
					prog_lang[line[1]].append(line[1])
				add_lang[line[1]][0]+=line[2]
				add_lang[line[1]][1]+=line[3]


				
	print('- Period:', early_date.strftime("%d-%m-%Y"),'-',latest_date.strftime("%d-%m-%Y"),' ('+str(weekdays_count)+' Working days)')
	print('- Total Commit:',len(storage))
	print('- Commit Average:',round(len(storage)/weekdays_count, 2), ' Commits/day')

	period = str(early_date.strftime("%d-%m-%Y").replace('-','/'))+' - '+str(latest_date.strftime("%d-%m-%Y").replace('-','/'))+' ('+str(weekdays_count)+' Working days)'
	content = ""
	for x in prog_lang.keys():
		temp = '''
		<div class="section-title">
			#1#
		</div>

		<table>
			<tr>
				<td class="highlight"><i class="fas fa-file-code icon"></i>Working on</td>
				<td class="stat">#2# Unique Files</td>
			</tr>
			<tr>
				<td class="highlight"><i class="fas fa-plus icon"></i>Lines Added</td>
				<td class="stat">#3# Lines</td>
			</tr>
			<tr>
				<td class="highlight"><i class="fas fa-minus icon"></i>Lines Deleted</td>
				<td class="stat">#4# Lines</td>
			</tr>
			<tr>
				<td class="highlight"><i class="fas fa-exchange-alt icon"></i>Total Lines Changed</td>
				<td class="stat">#5# Lines</td>
			</tr>
		</table>
		'''

		temp = temp.replace('#1#', x)
		temp = temp.replace('#2#', str(len(prog_lang[x])))
		temp = temp.replace('#3#', str(add_lang[x][0]))
		temp = temp.replace('#4#', str(add_lang[x][1]))
		temp = temp.replace('#5#', str(add_lang[x][1]+add_lang[x][0]))


		print('   -',x)
		print('      - Working on',len(prog_lang[x]), 'Unique Files')
		print('      -',add_lang[x][0], 'Lines added')
		print('      -',add_lang[x][1], 'Lines deleted')
		print('      -',add_lang[x][1]+add_lang[x][0], 'Total lines change')
		content+=temp


	HTMLWriter(user_name,owner_name,str(contributor_count),str(period),str(len(storage)),str(round(len(storage)/weekdays_count, 2)),content)
