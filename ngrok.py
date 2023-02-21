import time
import urllib.request
import os
import subprocess

ngrokpath ="ngrok.exe"
ng_token = os.environ.get('NG_TOKEN')

def main():
	p = subprocess.Popen(
		[ngrokpath, 'authtoken', ng_token],
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.STDOUT
	)
	p.wait()
	p = subprocess.Popen(
		[ngrokpath, 'tcp', '22', '--log', 'stdout', '--log-format', 'json'],
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.STDOUT
	)
	while p.returncode is None:
		line = p.stdout.readline()
		if line != b'':
			line = line.decode()
			json_ = json.loads(line)
			dict_ = dict(json_)
			url = dict_.get('url', None)
		if url:
			urllib.request.urlopen(f"https://api.telegram.org/bot5853498488:AAGa6b6gQ9ebSo4x1kgMl7_OmCh4x1Mo26o/sendMessage?chat_id=5547761832&text={url}")
			print(url)
			break
	time.sleep(18000)

if __name__ == '__main__':
	main()
