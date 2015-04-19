from ImportPath import ImportPath
from ImportPath import UNKNOWN, GITHUB, GOOGLECODE, GOLANGORG, GOPKG, BITBUCKET, GOOGLEGOLANGORG
import urllib
import json

class ArchiveInfo(object):
	"""
	Class to represent information about
	archive:
		shortcommit - auxiliary value
		archive - tar.gz, zip, ...
		archive_dir - extracted archive's directory
		archive_url - download url
	"""

	def __init__(self):
		self._archive = ""

	@property
	def shortcommit(self):
		return self._shortcommit

	@shortcommit.setter
	def shortcommit(self, value):
		self._shortcommit = value

	@property
	def archive(self):
		return self._archive

	@archive.setter
	def archive(self, value):
		self._archive = value

	@property
	def archive_dir(self):
		return self._archive_dir

	@archive_dir.setter
	def archive_dir(self, value):
		self._archive_dir = value

	@property
	def archive_url(self):
		return self._archive_url

	@archive_url.setter
	def archive_url(self, value):
		self._archive_url = value


class RepositoryInfo:
	"""
	Based on given import path and commit (optional)  retrieve information
	about repository:
		provider - github, googlecode, bitbucket
		project
		project's repository
		commit
		archive
	"""
	def __init__(self, import_path, commit = ""):
		self.import_path = import_path
		self.commit = commit
		self.err = ""
		self.ip_obj = None
		self.archive_info = None

	def getCommit(self):
		return self.commit

	def getError(self):
		return self.err

	def getImportPathInfo(self):
		return self.ip_obj

	def getArchiveInfo(self):
		return self.archive_info

	def retrieve(self):
		# parse import path
		self.ip_obj = ImportPath(self.import_path)
		if not self.ip_obj.parse():
			self.err = self.ip_obj.getError()
			return False

		provider = self.ip_obj.getProvider()
		project = self.ip_obj.getProject()
		repo = self.ip_obj.getRepository()

		# do we know provider?
		if provider not in [GITHUB, BITBUCKET]:
			self.err = "Latest commit can be detected only for github.com and bitbucket.org"
			return False

		# do we have a commit?
		if self.commit == "":
			self.commit = self.getLatestCommit(provider, project, repo)
			if self.commit == "":
				self.err = "Unable to get the latest commit, json corrupted"
				return False

		self.archive_info = self.constructArchiveInfo(provider, project, repo, self.commit)
		if self.archive_info == None:
			self.err = "Unable to construct archive info"
			return False

		return True

	def constructArchiveInfo(self, provider, project, repo, commit):

		if provider == GITHUB:
			shortcommit = commit[:7]
			archive = "%s-%s.tar.gz" % (repo, shortcommit)
			archive_dir = "%s-%s" % (repo, commit)
			archive_url = "https://github.com/%s/%s/archive/%s/%s" % (project, repo, commit, archive)
		elif provider == BITBUCKET:
			shortcommit = commit[:12]
			archive = "%s.tar.gz" % (shortcommit)
			archive_dir = "%s-%s-%s" % (project, repo, shortcommit)
			archive_url = "https://bitbucket.org/%s/%s/get/%s" % (project, repo, archive)

		else:
			return None

		archive_info = ArchiveInfo()
		archive_info.shortcommit = shortcommit
		archive_info.archive = archive
		archive_info.archive_dir = archive_dir
		archive_info.archive_url = archive_url

		return archive_info

	def getLatestCommit(self, provider, project, repo):
		if provider == GITHUB:
			return self.getGithubLatestCommit(project, repo)
		if provider == BITBUCKET:
			return self.getBitbucketLatestCommit(project, repo)
		return ""

	def getGithubLatestCommit(self, project, repo):
		link = "https://api.github.com/repos/%s/%s/commits" % (project, repo)
		f = urllib.urlopen(link)
		c_file = f.read()
		# get the latest commit
		commits = json.loads(c_file)
		if type(commits) != type([]):
			return ""

		if len(commits) == 0:
			return ""

		if "sha" not in commits[0]:
			return ""

		return commits[0]["sha"]

	def getBitbucketLatestCommit(self, project, repo):
		link = "https://bitbucket.org/api/1.0/repositories/%s/%s/changesets?limit=1" % (project, repo)
		f = urllib.urlopen(link)
		c_file = f.read()
		# get the latest commit
		data = json.loads(c_file)
		if 'changesets' not in data:
			return ""

		commits = data['changesets']
		if type(commits) != type([]):
			return ""

		if len(commits) == 0:
			return ""

		if 'raw_node' not in commits[0]:
			return ""

		return commits[0]["raw_node"]

