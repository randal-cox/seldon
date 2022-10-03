import subprocess

def call(*command):
  """Just get stdout of a shell command"""
  p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
  return p.stdout.read().decode('utf-8')
