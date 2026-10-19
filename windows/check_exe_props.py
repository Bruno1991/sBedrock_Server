import re

with open(r'c:\dev\s_Bedrock_Server\server\runtime\bedrock_server.exe', 'rb') as f:
    content = f.read()

matches = set(re.findall(b'server-authoritative-[a-zA-Z0-9_-]+', content))
for m in sorted(matches):
    print(m.decode('ascii'))

print("--- Player position thresholds ---")
pmatches = set(re.findall(b'player-[a-zA-Z0-9_-]+', content))
for m in sorted(pmatches):
    print(m.decode('ascii'))
