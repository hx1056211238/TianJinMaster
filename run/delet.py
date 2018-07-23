current_cwd = os.getcwd()
print current_cwd
os.chdir("/home/pi/hf_formation/run/ext/")
current_cwd = os.getcwd()
os.system("find -name '*.py' |xargs rm -rf")
print "delet py files"
os.chdir(current_cwd)