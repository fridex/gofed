import optparse
from modules.Utils import runCommand
from modules.specParser import SpecInfo
from modules.Repos import getGithubLatestCommit, getBitbucketLatestCommit

def getSpec():
	so, se, rc = runCommand("ls *.spec")
	if rc != 0:
		return ""
	else:
		return so.strip().split(" ")[0]

def getMacros(spec):

	err = ""
	macros = {}
	obj = SpecInfo(spec)
	macros["project"] = obj.getMacro("project")
	macros["repo"] = obj.getMacro("repo")
	macros["provider"] = obj.getMacro("provider")

	if macros["project"] == "":
		err = "Unable to detect project macro"
		return err, {}

	if macros["repo"] == "":
		err = "Unable to detect repo macro"
		return err, {}

	if macros["provider"] == "":
		err = "unable to detect provider macro"
		return err, {}

	macros["ip"] = obj.getMacro("import_path")
	if macros["ip"] == "":
		macros["provider_tld"] = obj.getMacro("provider_tld")

		if macros["provider_tld"] == "":
			err = "Unable to detect provider_tld macro"
			return err, {}

		macros["ip"] = "%s.%s/%s/%s" % (macros["provider"], macros["provider_tld"], macros["project"], macros["repo"])

	return "", macros

def downloadTarball(archive_url):
	so, se, rc = runCommand("wget -nv %s --no-check-certificate" % archive_url)
	if rc != 0:		
		print "%sUnable to download tarball:\n%s%s" % (RED, se, ENDC)
		exit(1)

def updateSpec(spec, commit):
	so, se, rc = runCommand("sed -i -e \"s/%%global commit\([[:space:]]\+\)[[:xdigit:]]\{40\}/%%global commit\\1%s/\" %s" % (commit, spec))
	if rc != 0:
		return False
	else:
		return True

def bumpSpec(spec, commit):
	so, se, rc = runCommand("rpmdev-bumpspec --comment=\"Bump to upstream %s\" %s" % (commit, spec))
	if rc != 0:
		return False
	else:
		return True

if __name__ == "__main__":

	parser = optparse.OptionParser("%prog [-c COMMIT] ")

	parser.add_option(
	    "", "-c", "--commit", dest="commit", default = "",
	    help = "Bump spec file to commit."
	)

	options, args = parser.parse_args()

	# must be on master branch
	so, se, rc = runCommand("git branch | grep '*' | sed 's/*//'")
	if rc != 0:
		print "Not in a git repository"
		exit(1)

	branch = so.split('\n')[0].strip()
	if branch != "master":
		print "Not on branch master"
		exit(1)

	# get spec file
	print "Searching for spec file"
	spec = getSpec()
	if spec == "":
		print "Unable to find spec file"
		exit(1)

	# get macros
	print "Reading macros from %s" % spec
	err, macros = getMacros(spec)
	if err != "":
		print err
		exit(2)

	provider = macros["provider"]
	project = macros["project"]
	repo = macros["repo"]
	# only github so far
	if provider != "github" and provider != "bitbucket":
		print "Only githum.com and bitbucket.org are supported"
		exit(2)

	commit = options.commit
	if commit == "":
		# get latest commit
		print "Getting the latest commit from %s" % macros["ip"]
		if provider == "github":
			commit = getGithubLatestCommit(project, repo)
		else:
			commit = getBitbucketLatestCommit(project, repo)	
		if commit == "":
			print "Unable to get the latest commit"
			exit(3)

	# don't bump if the commit is the as at htel atest

	# download tarball
	print "Download tarball"
	if provider == "github":
		shortcommit = commit[:7]
		archive = "%s-%s.tar.gz" % (repo, shortcommit)
		archive_url = "https://github.com/%s/%s/archive/%s/%s" % (project, repo, commit, archive)
	else:
		shortcommit = commit[:12]
		archive = "%s.tar.gz" % (shortcommit)
		archive_url = "https://bitbucket.org/%s/%s/get/%s" % (project, repo, archive)
	downloadTarball(archive_url)

	# update spec file
	print "Updating spec file"
	if not updateSpec(spec, commit):
		print "Unable to update spec file"
		exit(5)

	# bump spec file
	print "Bumping spec file"
	if not bumpSpec(spec, commit):
		print "Unable to bump spec file"
		exit(6)

