GOFED_VERSION = "0.0.7"
GOFED_COMPILED = "1 August 2015"
GOFED_AUTHOR = "Jan Chaloupka <jchaloup@redhat.com>"

def printVersion():
	print "Gofed %s (%s)" % (GOFED_VERSION, GOFED_COMPILED)
	#print "Bug reports at %s" % GOFED_AUTHOR

if __name__ == "__main__":
	printVersion()
